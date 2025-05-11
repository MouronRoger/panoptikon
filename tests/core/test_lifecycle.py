"""Tests for the application lifecycle management."""

import threading

import pytest

from src.panoptikon.core.events import EventBus
from src.panoptikon.core.lifecycle import (
    ApplicationLifecycle,
    ApplicationState,
    ApplicationStateChangedEvent,
)
from src.panoptikon.core.service import ServiceContainer, ServiceInterface


@pytest.fixture
def event_bus() -> EventBus:
    """Create an event bus for testing."""
    return EventBus()


@pytest.fixture
def service_container() -> ServiceContainer:
    """Create a service container for testing."""
    return ServiceContainer()


@pytest.fixture
def lifecycle(service_container: ServiceContainer, event_bus: EventBus) -> ApplicationLifecycle:
    """Create an application lifecycle manager for testing."""
    lifecycle = ApplicationLifecycle(service_container, event_bus)
    lifecycle.initialize()
    return lifecycle


def test_lifecycle_initialization(lifecycle: ApplicationLifecycle) -> None:
    """Test lifecycle manager initialization."""
    assert lifecycle.get_state() == ApplicationState.CREATED
    assert lifecycle._startup_hooks == []
    assert lifecycle._shutdown_hooks == []
    assert lifecycle._exit_code == 0


def test_startup_hook_registration(lifecycle: ApplicationLifecycle) -> None:
    """Test startup hook registration and ordering."""
    called: list[str] = []

    def hook1() -> None:
        called.append("hook1")

    def hook2() -> None:
        called.append("hook2")

    def hook3() -> None:
        called.append("hook3")

    # Register hooks with different priorities
    lifecycle.register_startup_hook("hook2", hook2, priority=200)
    lifecycle.register_startup_hook("hook1", hook1, priority=100)
    lifecycle.register_startup_hook("hook3", hook3, priority=300)

    # Start the application
    lifecycle.start()

    # Check hook execution order
    assert called == ["hook1", "hook2", "hook3"]
    assert lifecycle.get_state() == ApplicationState.RUNNING


def test_shutdown_hook_registration(lifecycle: ApplicationLifecycle) -> None:
    """Test shutdown hook registration and ordering."""
    called: list[str] = []

    def hook1() -> None:
        called.append("hook1")

    def hook2() -> None:
        called.append("hook2")

    def hook3() -> None:
        called.append("hook3")

    # Register hooks with different priorities
    lifecycle.register_shutdown_hook("hook2", hook2, priority=200)
    lifecycle.register_shutdown_hook("hook1", hook1, priority=100)
    lifecycle.register_shutdown_hook("hook3", hook3, priority=300)

    # Start and stop the application
    lifecycle.start()
    lifecycle.stop()

    # Check hook execution order (higher priority first for shutdown)
    assert called == ["hook3", "hook2", "hook1"]
    assert lifecycle.get_state() == ApplicationState.STOPPED


def test_state_transitions(lifecycle: ApplicationLifecycle, event_bus: EventBus) -> None:
    """Test application state transitions."""
    state_changes: list[ApplicationStateChangedEvent] = []

    def state_change_handler(event: ApplicationStateChangedEvent) -> None:
        state_changes.append(event)

    # Subscribe to state change events
    event_bus.subscribe(ApplicationStateChangedEvent, state_change_handler)

    # Start the application
    lifecycle.start()
    assert lifecycle.get_state() == ApplicationState.RUNNING

    # Stop the application
    lifecycle.stop()
    assert lifecycle.get_state() == ApplicationState.STOPPED

    # Check state transitions
    assert len(state_changes) == 4
    assert state_changes[0].old_state == ApplicationState.CREATED
    assert state_changes[0].new_state == ApplicationState.INITIALIZING
    assert state_changes[1].old_state == ApplicationState.INITIALIZING
    assert state_changes[1].new_state == ApplicationState.RUNNING
    assert state_changes[2].old_state == ApplicationState.RUNNING
    assert state_changes[2].new_state == ApplicationState.STOPPING
    assert state_changes[3].old_state == ApplicationState.STOPPING
    assert state_changes[3].new_state == ApplicationState.STOPPED


def test_shutdown_request(lifecycle: ApplicationLifecycle) -> None:
    """Test shutdown request handling."""
    lifecycle.start()
    assert lifecycle.get_state() == ApplicationState.RUNNING

    # Request shutdown
    lifecycle.request_shutdown(reason="Test shutdown")

    # Wait for shutdown to complete
    exit_code = lifecycle.wait_for_shutdown(timeout=1.0)
    assert exit_code == 0
    assert lifecycle.get_state() == ApplicationState.STOPPED


def test_wait_for_shutdown_timeout(lifecycle: ApplicationLifecycle) -> None:
    """Test wait_for_shutdown timeout."""
    lifecycle.start()

    # Wait for shutdown with a short timeout
    with pytest.raises(TimeoutError):
        lifecycle.wait_for_shutdown(timeout=0.1)


def test_hook_error_handling(lifecycle: ApplicationLifecycle) -> None:
    """Test error handling in hooks."""
    called: list[str] = []

    def good_hook() -> None:
        called.append("good")

    def bad_hook() -> None:
        called.append("bad")
        raise ValueError("Test error")

    # Register hooks
    lifecycle.register_startup_hook("good", good_hook)
    lifecycle.register_startup_hook("bad", bad_hook)

    # Start the application - should continue despite error
    lifecycle.start()

    # Check that both hooks were called
    assert called == ["good", "bad"]
    assert lifecycle.get_state() == ApplicationState.RUNNING


def test_invalid_state_transitions(lifecycle: ApplicationLifecycle) -> None:
    """Test invalid state transitions."""
    # Try to start twice
    lifecycle.start()
    with pytest.raises(RuntimeError):
        lifecycle.start()

    # Stop multiple times should be fine
    lifecycle.stop()
    lifecycle.stop()  # Should not raise
    assert lifecycle.get_state() == ApplicationState.STOPPED


def test_service_initialization(lifecycle: ApplicationLifecycle, service_container: ServiceContainer) -> None:
    """Test service initialization during startup."""
    initialized = threading.Event()
    shutdown = threading.Event()

    class TestService(ServiceInterface):
        def initialize(self) -> None:
            initialized.set()

        def shutdown(self) -> None:
            shutdown.set()

    # Register service
    service = TestService()
    service_container.register(TestService, factory=lambda _: service)

    # Start the application
    lifecycle.start()
    assert initialized.wait(timeout=1.0)

    # Stop the application
    lifecycle.stop()
    assert shutdown.wait(timeout=1.0) 