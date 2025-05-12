"""Consolidated integration tests for core infrastructure (service container, event bus, config, error handling, lifecycle). Covers both minimal and full integration paths, parameterized for event bus implementation."""

from datetime import datetime
import logging
from typing import Any, Optional
import uuid

import pytest

from panoptikon.core.config import ConfigurationSystem  # type: ignore
from panoptikon.core.errors import ErrorHandlingService  # type: ignore
from panoptikon.core.events import EventBase, EventBus  # type: ignore
from panoptikon.core.lifecycle import ApplicationLifecycle  # type: ignore
from panoptikon.core.service import ServiceContainer, ServiceInterface, ServiceLifetime
import tests.events_patched as events_patched

logger = logging.getLogger("test_integration")


@pytest.mark.parametrize(
    "event_bus_cls, event_base_cls, test_name",
    [
        (EventBus, EventBase, "core"),
        (events_patched.EventBus, events_patched.EventBase, "patched"),
    ],
)
def test_core_integration(
    event_bus_cls: type, event_base_cls: type, test_name: str
) -> None:
    """Test core infrastructure integration for both main and patched event bus implementations."""
    logger.info(f"Starting Core Integration Test [{test_name}]")

    class TestEvent(event_base_cls):
        """Test event for demonstration purposes."""

        def __init__(
            self,
            message: str,
            data: Optional[dict[str, Any]] = None,
            event_id: Optional[str] = None,
            timestamp: Optional[datetime] = None,
            source: Optional[str] = None,
        ) -> None:
            super().__init__(
                event_id=event_id or str(uuid.uuid4()),
                timestamp=timestamp or datetime.now(),
                source=source,
            )
            self.message = message
            self.data = data

        def to_dict(self) -> dict[str, Any]:
            result: dict[str, Any] = super().to_dict()
            result["message"] = self.message
            if self.data:
                result["data"] = self.data
            return result

    class TestService(ServiceInterface):
        """Test service that publishes and subscribes to events."""

        def __init__(self, event_bus: Any) -> None:
            self.event_bus = event_bus
            self.received_events: list[TestEvent] = []

        def initialize(self) -> None:
            logger.info("TestService initializing")
            self.event_bus.subscribe(TestEvent, self.handle_test_event)

        def shutdown(self) -> None:
            logger.info("TestService shutting down")

        def publish_test_event(self, message: str) -> None:
            event = TestEvent(message=message, source="TestService")
            logger.info(f"Publishing event: {message}")
            self.event_bus.publish(event)

        def handle_test_event(self, event: TestEvent) -> None:
            logger.info(f"Received event: {event.message}")
            self.received_events.append(event)

    # Create and set up the service container
    container = ServiceContainer()
    container.register(
        event_bus_cls,
        implementation_type=event_bus_cls,
        lifetime=ServiceLifetime.SINGLETON,
    )

    # For minimal test, only event bus and test service
    event_bus = event_bus_cls()
    test_service = TestService(event_bus=event_bus)
    container._instances[event_bus_cls] = event_bus
    container._instances[TestService] = test_service

    # Initialize and test minimal path
    event_bus.initialize()
    test_service.initialize()
    test_service.publish_test_event(f"Hello from {test_name} minimal!")
    assert test_service.received_events, (
        f"No events received in {test_name} minimal path"
    )
    test_service.shutdown()
    event_bus.shutdown()

    # For full integration, add config, error, lifecycle
    config_system = ConfigurationSystem(event_bus=event_bus)
    error_service = ErrorHandlingService(event_bus=event_bus)
    lifecycle = ApplicationLifecycle(service_container=container, event_bus=event_bus)
    container._instances[ConfigurationSystem] = config_system
    container._instances[ErrorHandlingService] = error_service
    container._instances[ApplicationLifecycle] = lifecycle

    # Initialize all
    event_bus.initialize()
    config_system.initialize()
    error_service.initialize()
    test_service.initialize()
    lifecycle.initialize()

    # Test event publication and subscription
    test_service.publish_test_event(f"Hello from {test_name} full!")
    assert test_service.received_events, f"No events received in {test_name} full path"
    assert config_system is not None
    assert error_service is not None

    # Clean shutdown
    for service in [event_bus, config_system, error_service, test_service, lifecycle]:
        service.shutdown()

    logger.info(f"Core Integration Test [{test_name}] Completed")
