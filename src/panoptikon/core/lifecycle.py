"""Application lifecycle management.

This module provides the application lifecycle management functionality,
handling startup/shutdown sequences, service initialization ordering,
and resource cleanup.
"""

import atexit
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
import logging
import signal
import sys
import threading
import time
from typing import Any, Callable, Optional
import uuid

from ..core.events import EventBase, EventBus
from ..core.service import ServiceContainer, ServiceInterface

logger = logging.getLogger(__name__)


class ApplicationState(Enum):
    """States of the application lifecycle."""

    CREATED = auto()
    INITIALIZING = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()


@dataclass
class ApplicationStateChangedEvent(EventBase):
    """Event issued when application state changes."""

    old_state: Optional[ApplicationState] = None
    new_state: ApplicationState = ApplicationState.CREATED
    message: Optional[str] = None


@dataclass
class ShutdownRequestEvent(EventBase):
    """Event issued when a shutdown is requested."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    force: bool = False
    timeout: Optional[float] = None
    reason: str = "Normal shutdown"


@dataclass
class ServiceRegistration:
    """Information about a registered startup/shutdown hook."""

    name: str
    priority: int
    handler: Callable[[], None]
    is_async: bool = False
    timeout: Optional[float] = None


class ApplicationLifecycle(ServiceInterface):
    """Manages the application lifecycle.

    Handles startup, shutdown, and state transitions.
    """

    def __init__(
        self, service_container: ServiceContainer, event_bus: EventBus
    ) -> None:
        """Initialize the application lifecycle manager.

        Args:
            service_container: Container for service dependencies.
            event_bus: Event bus for publishing lifecycle events.
        """
        self._service_container = service_container
        self._event_bus = event_bus
        self._state = ApplicationState.CREATED
        self._startup_hooks: list[ServiceRegistration] = []
        self._shutdown_hooks: list[ServiceRegistration] = []
        self._state_lock = threading.RLock()
        self._exit_code = 0

        # Register with atexit to ensure cleanup
        atexit.register(self._atexit_handler)

        # Register signal handlers if not running on Windows
        if sys.platform != "win32":
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)

    def initialize(self) -> None:
        """Initialize the lifecycle manager."""
        # Subscribe to shutdown request events
        self._event_bus.subscribe(
            ShutdownRequestEvent,
            self._handle_shutdown_request,
        )
        logger.debug("ApplicationLifecycle initialized")

    def shutdown(self) -> None:
        """Clean up resources."""
        pass  # Nothing specific to clean up here

    def register_startup_hook(
        self,
        name: str,
        handler: Callable[[], None],
        priority: int = 100,
        is_async: bool = False,
        timeout: Optional[float] = None,
    ) -> None:
        """Register a hook to be called during startup.

        Args:
            name: Unique name for the hook.
            handler: Function to call.
            priority: Priority (higher values run later).
            is_async: Whether the handler is asynchronous.
            timeout: Optional timeout for the handler.
        """
        registration = ServiceRegistration(
            name=name,
            priority=priority,
            handler=handler,
            is_async=is_async,
            timeout=timeout,
        )

        # Insert in priority order (lower numbers first)
        for i, hook in enumerate(self._startup_hooks):
            if hook.priority > priority:
                self._startup_hooks.insert(i, registration)
                return

        # If we get here, add to the end
        self._startup_hooks.append(registration)

        logger.debug(f"Registered startup hook: {name} (priority: {priority})")

    def register_shutdown_hook(
        self,
        name: str,
        handler: Callable[[], None],
        priority: int = 100,
        is_async: bool = False,
        timeout: Optional[float] = None,
    ) -> None:
        """Register a hook to be called during shutdown.

        Args:
            name: Unique name for the hook.
            handler: Function to call.
            priority: Priority (higher values run earlier).
            is_async: Whether the handler is asynchronous.
            timeout: Optional timeout for the handler.
        """
        registration = ServiceRegistration(
            name=name,
            priority=priority,
            handler=handler,
            is_async=is_async,
            timeout=timeout,
        )

        # Insert in priority order (higher numbers first for shutdown)
        for i, hook in enumerate(self._shutdown_hooks):
            if hook.priority < priority:
                self._shutdown_hooks.insert(i, registration)
                return

        # If we get here, add to the end
        self._shutdown_hooks.append(registration)

        logger.debug(f"Registered shutdown hook: {name} (priority: {priority})")

    def start(self) -> None:
        """Start the application.

        Runs all startup hooks and initializes services.

        Raises:
            RuntimeError: If the application is already running.
        """
        with self._state_lock:
            if self._state != ApplicationState.CREATED:
                raise RuntimeError(f"Cannot start application in state: {self._state}")

            self._change_state(ApplicationState.INITIALIZING)

        # Run startup hooks
        self._run_hooks(self._startup_hooks, "startup")

        # Initialize all services
        self._service_container.initialize_all()

        with self._state_lock:
            self._change_state(ApplicationState.RUNNING)

        logger.info("Application started successfully")

    def stop(self, exit_code: int = 0, reason: str = "Normal shutdown") -> None:
        """Stop the application.

        Runs all shutdown hooks and cleans up resources.

        Args:
            exit_code: Exit code to return from the process.
            reason: Reason for shutting down.
        """
        with self._state_lock:
            if self._state in (ApplicationState.STOPPING, ApplicationState.STOPPED):
                return

            if self._state != ApplicationState.RUNNING:
                logger.warning(
                    f"Stopping application in unexpected state: {self._state}"
                )

            self._exit_code = exit_code
            self._change_state(ApplicationState.STOPPING, message=reason)

        # Run shutdown hooks
        self._run_hooks(self._shutdown_hooks, "shutdown")

        # Shut down all services
        self._service_container.shutdown_all()

        with self._state_lock:
            self._change_state(ApplicationState.STOPPED)

        logger.info(f"Application stopped (reason: {reason}, exit code: {exit_code})")

    def get_state(self) -> ApplicationState:
        """Get the current application state.

        Returns:
            Current application state.
        """
        with self._state_lock:
            return self._state

    def wait_for_shutdown(self, timeout: Optional[float] = None) -> int:
        """Wait for the application to shut down.

        Args:
            timeout: Optional timeout in seconds.

        Returns:
            Exit code from the application.

        Raises:
            TimeoutError: If the timeout expires.
        """
        start_time = time.time()

        while True:
            with self._state_lock:
                if self._state == ApplicationState.STOPPED:
                    return self._exit_code

            # Check timeout
            if timeout is not None and time.time() - start_time > timeout:
                raise TimeoutError("Timeout waiting for application to stop")

            # Sleep a bit to avoid busy waiting
            time.sleep(0.1)

    def request_shutdown(
        self,
        reason: str = "Shutdown requested",
        force: bool = False,
        timeout: Optional[float] = None,
    ) -> None:
        """Request a shutdown of the application.

        Args:
            reason: Reason for the shutdown.
            force: Whether to force immediate shutdown.
            timeout: Optional timeout for graceful shutdown.
        """
        # Publish shutdown request event
        self._event_bus.publish(
            ShutdownRequestEvent(
                reason=reason,
                force=force,
                timeout=timeout,
            )
        )

    def _change_state(
        self, new_state: ApplicationState, message: Optional[str] = None
    ) -> None:
        """Change the application state and publish an event.

        Args:
            new_state: The new state.
            message: Optional message about the state change.
        """
        with self._state_lock:
            old_state = self._state
            self._state = new_state

            # Publish state change event
            self._event_bus.publish(
                ApplicationStateChangedEvent(
                    old_state=old_state,
                    new_state=new_state,
                    message=message,
                )
            )

            logger.info(
                f"Application state changed: {old_state.name} -> {new_state.name}"
            )
            if message:
                logger.info(f"State change reason: {message}")

    def _run_hooks(self, hooks: list[ServiceRegistration], hook_type: str) -> None:
        """Run a list of registered hooks.

        Args:
            hooks: Hooks to run.
            hook_type: Type of hooks (for logging).
        """
        for hook in hooks:
            logger.debug(f"Running {hook_type} hook: {hook.name}")

            try:
                hook.handler()
            except Exception as e:
                logger.error(
                    f"Error in {hook_type} hook '{hook.name}': {e}", exc_info=True
                )

    def _handle_shutdown_request(self, event: ShutdownRequestEvent) -> None:
        """Handle a shutdown request event.

        Args:
            event: The shutdown request event.
        """
        logger.info(f"Shutdown requested: {event.reason} (force: {event.force})")
        self.stop(reason=event.reason)

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle signals from the operating system.

        Args:
            signum: Signal number.
            frame: Current stack frame.
        """
        if signum == signal.SIGTERM:
            self.request_shutdown(reason="SIGTERM received")
        elif signum == signal.SIGINT:
            self.request_shutdown(reason="SIGINT received (Ctrl+C)")

    def _atexit_handler(self) -> None:
        """Handle process exit."""
        # Ensure we shut down cleanly
        if self._state != ApplicationState.STOPPED:
            self.stop(reason="Process exiting")
