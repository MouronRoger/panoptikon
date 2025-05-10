"""Test script to verify the Phase 2 core infrastructure functionality.

This script demonstrates the integration of service container, event bus,
configuration system, error handling, and application lifecycle.
"""

from dataclasses import dataclass
import logging
from typing import Optional

from panoptikon.core.config import ConfigService
from panoptikon.core.errors import ErrorHandlingService
from panoptikon.core.events import EventBase, EventBus
from panoptikon.core.lifecycle import ApplicationLifecycle
from panoptikon.core.service import ServiceContainer, ServiceInterface, ServiceLifetime

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_phase2")


# Define a test event
@dataclass
class TestEvent(EventBase):
    """Test event for demonstration purposes."""

    message: str
    data: Optional[dict] = None


# Define a test service
class TestService(ServiceInterface):
    """Test service that publishes and subscribes to events."""

    def __init__(self, event_bus: EventBus) -> None:
        """Initialize with dependencies.

        Args:
            event_bus: The event bus for publishing/subscribing to events.
        """
        self.event_bus = event_bus
        self.received_events: list[TestEvent] = []

    def initialize(self) -> None:
        """Initialize the service and subscribe to events."""
        logger.info("TestService initializing")
        self.event_bus.subscribe(TestEvent, self.handle_test_event)

    def shutdown(self) -> None:
        """Clean up resources."""
        logger.info("TestService shutting down")

    def publish_test_event(self, message: str) -> None:
        """Publish a test event.

        Args:
            message: The message to include in the event.
        """
        event = TestEvent(message=message, source="TestService")
        logger.info(f"Publishing event: {message}")
        self.event_bus.publish(event)

    def handle_test_event(self, event: TestEvent) -> None:
        """Handle incoming test events.

        Args:
            event: The event to handle.
        """
        logger.info(f"Received event: {event.message}")
        self.received_events.append(event)


def main() -> None:
    """Main test function."""
    logger.info("Starting Phase 2 Core Infrastructure Test")

    # Create and set up the service container
    container = ServiceContainer()

    # Register core services
    logger.info("Registering services")
    container.register(EventBus, lifetime=ServiceLifetime.SINGLETON)
    container.register(ConfigService, lifetime=ServiceLifetime.SINGLETON)
    container.register(ErrorHandlingService, lifetime=ServiceLifetime.SINGLETON)
    container.register(TestService, lifetime=ServiceLifetime.SINGLETON)
    container.register(ApplicationLifecycle, lifetime=ServiceLifetime.SINGLETON)

    # Validate dependencies
    logger.info("Validating service dependencies")
    container.validate_dependencies()

    # Initialize services
    logger.info("Initializing services")
    container.initialize_all()

    # Resolve application lifecycle
    container.resolve(ApplicationLifecycle)
    logger.info("Application lifecycle service resolved")

    # Test event publication and subscription
    logger.info("Testing event system")
    test_service = container.resolve(TestService)
    test_service.publish_test_event("Hello, Phase 2!")

    # Check if event was received
    if test_service.received_events:
        logger.info(
            f"✅ Event system working! Received events: {len(test_service.received_events)}"
        )
    else:
        logger.error("❌ Event system not working! No events received.")

    # Test configuration service
    config_service = container.resolve(ConfigService)
    logger.info(f"Configuration service resolved: {config_service is not None}")

    # Test error handling service
    error_service = container.resolve(ErrorHandlingService)
    logger.info(f"Error handling service resolved: {error_service is not None}")

    # Clean shutdown
    logger.info("Shutting down services")
    container.shutdown_all()

    logger.info("Phase 2 Core Infrastructure Test Completed")


if __name__ == "__main__":
    main()
