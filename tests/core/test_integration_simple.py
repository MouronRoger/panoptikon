"""Simple test for core service container and event bus.

This script tests only the service container and event bus core infrastructure
without requiring external dependencies.
"""

import logging
from typing import Any, Optional

from panoptikon.core.service import ServiceContainer, ServiceInterface, ServiceLifetime
from tests import events_patched

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_integration_simple")


# Define a test event
class TestEvent(events_patched.EventBase):
    """Test event for demonstration purposes."""

    def __init__(self, message: str, data: Optional[dict[str, Any]] = None, **kwargs: Any) -> None:
        """Initialize the test event.

        Args:
            message: The test message
            data: Optional data dictionary
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(**kwargs)
        self.message = message
        self.data = data


# Define a test service
class TestService(ServiceInterface):
    """Test service that publishes and subscribes to events."""

    def __init__(self, event_bus: events_patched.EventBus) -> None:
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


def test_simple_core_infrastructure() -> None:
    """Test the simple core infrastructure integration."""
    logger.info("Starting Simple Core Infrastructure Test")

    # Create and set up the service container
    container = ServiceContainer()

    # Register core services
    logger.info("Registering services")
    container.register(
        service_type=events_patched.EventBus,
        implementation_type=events_patched.EventBus,
        lifetime=ServiceLifetime.SINGLETON
    )
    container.register(
        service_type=TestService,
        implementation_type=TestService,
        lifetime=ServiceLifetime.SINGLETON
    )

    # Validate dependencies
    logger.info("Validating service dependencies")
    container.validate_dependencies()

    # Initialize services
    logger.info("Initializing services")
    container.initialize_all()

    # Test event publication and subscription
    logger.info("Testing event system")
    test_service = container.resolve(TestService)
    test_service.publish_test_event("Hello from simple test!")

    # Check if event was received
    if test_service.received_events:
        logger.info(
            f"✅ Event system working! Received events: {len(test_service.received_events)}"
        )
        assert len(test_service.received_events) > 0
    else:
        logger.error("❌ Event system not working! No events received.")
        assert False, "No events received"

    # Clean shutdown
    logger.info("Shutting down services")
    container.shutdown_all()

    logger.info("Simple Core Infrastructure Test Completed")


if __name__ == "__main__":
    test_simple_core_infrastructure() 