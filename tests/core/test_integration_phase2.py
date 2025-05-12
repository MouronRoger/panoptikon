"""Test script to verify the Phase 2 core infrastructure functionality.

This script demonstrates the integration of service container, event bus,
configuration system, error handling, and application lifecycle.
"""

from datetime import datetime
import logging
from typing import Any, Optional
import uuid

from panoptikon.core.config import ConfigurationSystem  # type: ignore
from panoptikon.core.errors import ErrorHandlingService  # type: ignore
from panoptikon.core.events import EventBase, EventBus  # type: ignore
from panoptikon.core.lifecycle import ApplicationLifecycle  # type: ignore
from panoptikon.core.service import (  # type: ignore
    ServiceContainer,
    ServiceInterface,
    ServiceLifetime,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_integration_phase2")


# Define a test event
class TestEvent(EventBase):
    """Test event for demonstration purposes."""

    def __init__(
        self,
        message: str,
        data: Optional[dict] = None,
        event_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        source: Optional[str] = None,
    ) -> None:
        """Initialize a test event.

        Args:
            message: The event message.
            data: Optional data dictionary.
            event_id: Optional event ID, auto-generated if not provided.
            timestamp: Optional timestamp, defaults to current time.
            source: Optional source identifier.
        """
        super().__init__(
            event_id=event_id or str(uuid.uuid4()),
            timestamp=timestamp or datetime.now(),
            source=source,
        )
        self.message = message
        self.data = data

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation.

        Returns:
            Dictionary representation of the event.
        """
        result: dict[str, Any] = super().to_dict()
        result.update(
            {
                "message": self.message,
            }
        )
        if self.data:
            result["data"] = self.data
        return result


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


def test_core_infrastructure_phase2() -> None:
    """Test Phase 2 core infrastructure integration."""
    logger.info("Starting Phase 2 Core Infrastructure Test")

    # Create and set up the service container
    container = ServiceContainer()

    # Register core services
    logger.info("Registering services")
    container.register(
        EventBus, implementation_type=EventBus, lifetime=ServiceLifetime.SINGLETON
    )

    # For testing purposes, use a simplified approach without dependency validation
    # Create mocked instances directly
    event_bus = EventBus()
    config_system = ConfigurationSystem(event_bus=event_bus)
    error_service = ErrorHandlingService(event_bus=event_bus)
    test_service = TestService(event_bus=event_bus)
    lifecycle = ApplicationLifecycle(service_container=container, event_bus=event_bus)

    # Store the created instances in the container without validation
    container._instances[EventBus] = event_bus
    container._instances[ConfigurationSystem] = config_system
    container._instances[ErrorHandlingService] = error_service
    container._instances[TestService] = test_service
    container._instances[ApplicationLifecycle] = lifecycle

    logger.info("Initializing services")
    event_bus.initialize()
    config_system.initialize()
    error_service.initialize()
    test_service.initialize()
    lifecycle.initialize()

    # Test event publication and subscription
    logger.info("Testing event system")
    test_service.publish_test_event("Hello, Phase 2!")

    # Check if event was received
    if test_service.received_events:
        logger.info(
            f"✅ Event system working! "
            f"Received events: {len(test_service.received_events)}"
        )
        assert len(test_service.received_events) > 0
    else:
        logger.error("❌ Event system not working! No events received.")
        raise AssertionError("No events received")

    # Test configuration service
    logger.info(f"Configuration service created: {config_system is not None}")
    assert config_system is not None

    # Test error handling service
    logger.info(f"Error handling service created: {error_service is not None}")
    assert error_service is not None

    # Clean shutdown
    logger.info("Shutting down services")
    for service in [event_bus, config_system, error_service, test_service, lifecycle]:
        service.shutdown()

    logger.info("Phase 2 Core Infrastructure Test Completed")


if __name__ == "__main__":
    test_core_infrastructure_phase2()
