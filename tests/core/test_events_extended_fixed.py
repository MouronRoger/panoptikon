"""Extended tests for the event system to improve coverage."""

import asyncio
from dataclasses import dataclass
import json
from unittest.mock import MagicMock, patch

import pytest

from src.panoptikon.core.events import (
    AsyncEventHandler,
    ErrorEvent,
    EventBase,
    EventBus,
    EventDeliveryMode,
    EventHandler,
)


@dataclass
class TestEvent(EventBase):
    """Test event for testing."""

    message: str = "test"
    value: int = 0


class TestErrorEventHandler(EventHandler[ErrorEvent]):
    """Handler for error events."""

    def __init__(self) -> None:
        """Initialize with empty event list."""
        self.error_events: list[ErrorEvent] = []

    def handle(self, event: ErrorEvent) -> None:
        """Store events in a list."""
        self.error_events.append(event)


@pytest.fixture
def event_bus() -> EventBus:
    """Create an event bus for testing."""
    bus = EventBus()
    bus.initialize()
    return bus


def test_event_base_to_dict() -> None:
    """Test the to_dict method of EventBase."""
    event = EventBase()
    event_dict = event.to_dict()

    assert "event_id" in event_dict
    assert "timestamp" in event_dict
    assert "source" in event_dict
    assert event_dict["source"] is None


def test_event_base_to_json() -> None:
    """Test the to_json method of EventBase."""
    event = EventBase(source="test_source")
    event_json = event.to_json()

    # Parse the JSON and check fields
    parsed = json.loads(event_json)
    assert "event_id" in parsed
    assert "timestamp" in parsed
    assert "source" in parsed
    assert parsed["source"] == "test_source"


def test_error_event_validation() -> None:
    """Test validation in ErrorEvent."""
    # Valid error event
    error = ErrorEvent(error_type="TestError", message="Test message")
    assert error.error_type == "TestError"
    assert error.message == "Test message"

    # Invalid error events
    with pytest.raises(ValueError):
        ErrorEvent(error_type="", message="Test message")

    with pytest.raises(ValueError):
        ErrorEvent(error_type="TestError", message="")


def test_error_event_to_dict() -> None:
    """Test the to_dict method of ErrorEvent."""
    error = ErrorEvent(
        error_type="TestError",
        message="Test message",
        severity="WARNING",
        traceback="Traceback info",
    )

    error_dict = error.to_dict()
    assert error_dict["error_type"] == "TestError"
    assert error_dict["message"] == "Test message"
    assert error_dict["severity"] == "WARNING"
    assert error_dict["traceback"] == "Traceback info"

    # Test without traceback - the implementation includes traceback as None
    error_no_trace = ErrorEvent(error_type="TestError", message="Test message")
    error_dict = error_no_trace.to_dict()
    assert "traceback" in error_dict
    assert error_dict["traceback"] is None


def test_event_delivery_modes(event_bus: EventBus) -> None:
    """Test different event delivery modes."""
    sync_events = []
    async_events = []

    def sync_handler(event: TestEvent) -> None:
        sync_events.append(event)

    async def async_handler(event: TestEvent) -> None:
        async_events.append(event)

    # Subscribe with explicit delivery modes
    event_bus.subscribe(
        TestEvent, sync_handler, delivery_mode=EventDeliveryMode.SYNCHRONOUS
    )
    event_bus.subscribe(
        TestEvent, async_handler, delivery_mode=EventDeliveryMode.ASYNCHRONOUS
    )

    # Set event loop
    loop = asyncio.get_event_loop()
    event_bus.set_event_loop(loop)

    # Publish an event
    test_event = TestEvent(message="Delivery test")
    event_bus.publish(test_event)

    # Sync handler should have received it immediately
    assert len(sync_events) == 1
    assert sync_events[0].message == "Delivery test"

    # Run the event loop to process async events
    loop.run_until_complete(asyncio.sleep(0.1))
    assert len(async_events) == 1
    assert async_events[0].message == "Delivery test"


def test_auto_detect_delivery_mode(event_bus: EventBus) -> None:
    """Test auto-detection of delivery mode based on handler type."""
    handler_types = {}

    def sync_function(event: TestEvent) -> None:
        handler_types["sync_function"] = "called"

    async def async_function(event: TestEvent) -> None:
        handler_types["async_function"] = "called"

    class SyncHandler(EventHandler[TestEvent]):
        def handle(self, event: TestEvent) -> None:
            handler_types["sync_handler"] = "called"

    class AsyncHandler(AsyncEventHandler[TestEvent]):
        async def handle(self, event: TestEvent) -> None:
            handler_types["async_handler"] = "called"

    # Subscribe without specifying delivery mode
    event_bus.subscribe(TestEvent, sync_function)
    event_bus.subscribe(TestEvent, async_function)
    event_bus.subscribe(TestEvent, SyncHandler())
    event_bus.subscribe(TestEvent, AsyncHandler())

    # Set event loop
    loop = asyncio.get_event_loop()
    event_bus.set_event_loop(loop)

    # Publish an event
    event_bus.publish(TestEvent())

    # Run the event loop to process async events
    loop.run_until_complete(asyncio.sleep(0.1))

    # All handlers should have been called
    assert handler_types.get("sync_function") == "called"
    assert handler_types.get("async_function") == "called"
    assert handler_types.get("sync_handler") == "called"
    assert handler_types.get("async_handler") == "called"


def test_handler_type_checking() -> None:
    """Test checking of handler types."""
    event_bus = EventBus()
    event_bus.initialize()

    # MagicMock is callable by default
    mock_handler = MagicMock()

    # This should succeed because MagicMock is callable
    event_bus.subscribe(TestEvent, mock_handler)

    # Call the handler directly to verify it would be called
    mock_handler.assert_not_called()
    event_bus.publish(TestEvent())
    mock_handler.assert_called_once()


def test_record_history_setting(event_bus: EventBus) -> None:
    """Test enabling/disabling event history recording."""
    # Disable history recording
    event_bus.set_record_history(False)

    # Publish some events
    test_events = []
    for i in range(5):
        event = TestEvent(message=f"Event {i}")
        test_events.append(event)
        event_bus.publish(event)

    # History should be empty
    assert len(event_bus.get_event_history()) == 0

    # Re-enable history recording
    event_bus.set_record_history(True)

    # Publish more events
    for i in range(5, 10):
        event = TestEvent(message=f"Event {i}")
        test_events.append(event)
        event_bus.publish(event)

    # Only events after re-enabling should be recorded
    history = event_bus.get_event_history()
    assert len(history) == 5
    for i, event in enumerate(history):
        assert event.message == f"Event {i + 5}"


def test_event_source_auto_detection(event_bus: EventBus) -> None:
    """Test automatic detection of event source."""
    # Create an event without a source
    event = TestEvent()
    assert event.source is None

    # Publish the event
    event_bus.publish(event)

    # Source should have been set automatically
    assert event.source is not None
    assert "test_events_extended_fixed.py" in event.source


def test_nested_error_handling(event_bus: EventBus) -> None:
    """Test handling of errors in error handlers."""
    error_handler = TestErrorEventHandler()

    # Subscribe error handler that will fail
    def failing_error_handler(event: ErrorEvent) -> None:
        raise ValueError("Error in error handler")

    event_bus.subscribe(ErrorEvent, failing_error_handler)
    event_bus.subscribe(ErrorEvent, error_handler)

    # Create a handler that fails
    def failing_handler(event: TestEvent) -> None:
        raise RuntimeError("Original error")

    event_bus.subscribe(TestEvent, failing_handler)

    # Publish an event that will trigger both errors
    event_bus.publish(TestEvent())

    # Should have received the original error but not the nested one
    # to prevent infinite recursion
    assert len(error_handler.error_events) == 1
    assert error_handler.error_events[0].error_type == "RuntimeError"
    assert error_handler.error_events[0].message == "Original error"


def test_invalid_history_size(event_bus: EventBus) -> None:
    """Test setting invalid history size."""
    with pytest.raises(ValueError):
        event_bus.set_max_history_size(0)

    with pytest.raises(ValueError):
        event_bus.set_max_history_size(-10)


def test_no_event_loop_error() -> None:
    """Test event loop auto-creation when none is available."""
    event_bus = EventBus()
    event_bus.initialize()

    # Make sure there's no event loop
    event_bus._event_loop = None

    # Subscribe an async handler
    async def async_handler(event: TestEvent) -> None:
        pass

    # Subscribe the handler
    subscription_id = event_bus.subscribe(
        TestEvent, async_handler, delivery_mode=EventDeliveryMode.ASYNCHRONOUS
    )

    # Attempt to publish an event
    # Should create an event loop automatically if needed
    event_bus.publish(TestEvent())
    assert event_bus._event_loop is not None


def test_deliver_to_correct_handler_types() -> None:
    """Test delivery to different handler types."""
    event_bus = EventBus()
    event_bus.initialize()

    # Create various handler types
    sync_handler = MagicMock(spec=EventHandler)
    async_handler = MagicMock(spec=AsyncEventHandler)

    # Mock the internal delivery methods
    with patch.object(event_bus, "_deliver_synchronous") as mock_sync:
        with patch.object(event_bus, "_deliver_asynchronous") as mock_async:
            # Test sync delivery
            subscription = MagicMock()
            subscription.handler = sync_handler
            subscription.delivery_mode = EventDeliveryMode.SYNCHRONOUS

            event_bus._deliver_event(TestEvent(), subscription)
            mock_sync.assert_called_once()
            mock_async.assert_not_called()

            # Reset mocks
            mock_sync.reset_mock()
            mock_async.reset_mock()

            # Test async delivery
            subscription.handler = async_handler
            subscription.delivery_mode = EventDeliveryMode.ASYNCHRONOUS

            event_bus._deliver_event(TestEvent(), subscription)
            mock_sync.assert_not_called()
            mock_async.assert_called_once()
