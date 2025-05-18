"""Main entry point for the Panoptikon application."""

import logging
import sys

from .core.config import ConfigurationSystem
from .core.errors import ErrorManager
from .core.events import EventBus
from .core.lifecycle import ApplicationLifecycle
from .core.service import ServiceContainer
from .core.service_extensions import register_window_manager_hooks


def setup_logging() -> None:
    """Set up basic logging configuration."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def main() -> int:
    """Run the application.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Panoptikon")

    try:
        # Create service container
        container = ServiceContainer()

        # Register core services
        event_bus = EventBus()
        container.register(EventBus, factory=lambda c: event_bus)

        error_manager = ErrorManager(event_bus)
        container.register(ErrorManager, factory=lambda c: error_manager)

        config_system = ConfigurationSystem(event_bus)
        container.register(ConfigurationSystem, factory=lambda c: config_system)

        lifecycle = ApplicationLifecycle(container, event_bus)
        container.register(ApplicationLifecycle, factory=lambda c: lifecycle)

        # Prepare for dual-window support (Stage 7)
        register_window_manager_hooks(container)

        # Validate the dependency graph
        container.validate_dependencies()

        # Get services from container
        lifecycle = container.resolve(ApplicationLifecycle)

        # Start the application
        lifecycle.start()

        # TODO: Run the main application logic here
        logger.info("Application running")

        # Wait for shutdown
        exit_code = lifecycle.wait_for_shutdown()

        return exit_code

    except Exception as e:
        logger.exception("Unhandled exception in main:", exc_info=e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
