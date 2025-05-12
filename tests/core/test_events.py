"""Consolidated tests for the event system.

This module combines all tests for the event system into a single, well-organized module
with proper test hierarchy and organization.
"""

import asyncio
from dataclasses import dataclass
import json
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from src.panoptikon.core.events import (
    AsyncEventHandler,
    ErrorEvent,
    EventBase,
    EventBus,
    EventDeliveryMode,
    EventHandler,
    EventPriority,
)


@dataclass
class TestEvent(EventBase):
    """Test event for testing."""

    message: str = "test"
    value: int = 0


class TestEventHandler(EventHandler[TestEvent]):
    """Test event handler for synchronous events."""

    def __init__(self) -> None:
        """Initialize with empty event list."""
        self.events: list[TestEvent] = []

    def handle(self, event: EventBase) -> None:
        """Store event in list."""
        self.events.append(cast(TestEvent, event))


class TestAsyncEventHandler(AsyncEventHandler[TestEvent]):
    """Test event handler for asynchronous events."""

    def __init__(self) -> None:
        """Initialize with empty event list."""
        self.events: list[TestEvent] = []

    async def handle(self, event: TestEvent) -> None:
        """Store event in list asynchronously."""
        self.events.append(event)


class TestErrorEventHandler(EventHandler[ErrorEvent]):
    """Handler for error events."""

    def __init__(self) -> None:
        """Initialize with empty error list."""
        self.error_events: list[ErrorEvent] = []

    def handle(self, event: ErrorEvent) -> None:
        """Store error event in list."""
        self.error_events.append(event)


@pytest.fixture
def event_bus() -> EventBus:
    """Create an event bus for testing."""
    bus = EventBus()
    bus.initialize()
    return bus


class TestEventBase:
    """Tests for the EventBase class."""

    def test_to_dict(self) -> None:
        """Test the to_dict method of EventBase."""
        event = EventBase()
        event_dict = event.to_dict()

        assert "event_id" in event_dict
        assert "timestamp" in event_dict
        assert "source" in event_dict
        assert event_dict["source"] is None

    def test_to_json(self) -> None:
        """Test the to_json method of EventBase."""
        event = EventBase(source="test_source")
        event_json = event.to_json()

        # Parse the JSON and check fields
        parsed = json.loads(event_json)
        assert "event_id" in parsed
        assert "timestamp" in parsed
        assert "source" in parsed
        assert parsed["source"] == "test_source"


class TestErrorEvent:
    """Tests for the ErrorEvent class."""

    def test_validation(self) -> None:
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

    def test_to_dict(self) -> None:
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

        # Test without traceback
        error_no_trace = ErrorEvent(error_type="TestError", message="Test message")
        error_dict = error_no_trace.to_dict()
        assert "traceback" in error_dict
        assert error_dict["traceback"] is None


class TestEventBusBasics:
    """Basic tests for the EventBus class."""

    def test_initialization(self, event_bus: EventBus) -> None:
        """Test event bus initialization."""
        # Verify that event_bus is properly initialized
        assert event_bus is not None
        assert isinstance(event_bus, EventBus)

        # Check initial state
        assert event_bus.get_event_history() == []

    def test_simple_publish_subscribe(self, event_bus: EventBus) -> None:
        """Test basic publish-subscribe functionality."""
        # Create a handler
        handler = TestEventHandler()

        # Subscribe to test events
        event_bus.subscribe(TestEvent, handler)

        # Publish a test event
        test_event = TestEvent(message="Hello, world!", value=42)
        event_bus.publish(test_event)

        # Verify handler received event
        assert len(handler.events) == 1
        assert handler.events[0] is test_event
        assert handler.events[0].message == "Hello, world!"
        assert handler.events[0].value == 42

        # Verify event history
        history = event_bus.get_event_history()
        assert len(history) == 1
        assert history[0] is test_event

    def test_multiple_handlers(self, event_bus: EventBus) -> None:
        """Test multiple handlers for the same event type."""
        # Create multiple handlers
        handler1 = TestEventHandler()
        handler2 = TestEventHandler()
        handler3 = TestEventHandler()

        # Subscribe all handlers
        event_bus.subscribe(TestEvent, handler1)
        event_bus.subscribe(TestEvent, handler2)
        event_bus.subscribe(TestEvent, handler3)

        # Publish a test event
        test_event = TestEvent(message="Multi-handler test")
        event_bus.publish(test_event)

        # Verify all handlers received the event
        assert len(handler1.events) == 1
        assert len(handler2.events) == 1
        assert len(handler3.events) == 1

        # Verify event details
        for handler in [handler1, handler2, handler3]:
            assert handler.events[0].message == "Multi-handler test"

    def test_unsubscribe(self, event_bus: EventBus) -> None:
        """Test unsubscribing from events."""
        # Create a handler
        handler = TestEventHandler()

        # Subscribe to test events
        subscription_id = event_bus.subscribe(TestEvent, handler)

        # Publish an event
        event_bus.publish(TestEvent(message="Before unsubscribe"))
        assert len(handler.events) == 1

        # Unsubscribe
        result = event_bus.unsubscribe(subscription_id)
        assert result is True

        # Publish another event
        event_bus.publish(TestEvent(message="After unsubscribe"))

        # Verify handler didn't receive the second event
        assert len(handler.events) == 1
        assert handler.events[0].message == "Before unsubscribe"

        # Try to unsubscribe with invalid ID
        result = event_bus.unsubscribe("invalid-id")
        assert result is False


class TestEventHistoryManagement:
    """Tests for event history management in EventBus."""

    def test_event_history_management(self, event_bus: EventBus) -> None:
        """Test event history management."""
        # Publish several events
        events = [TestEvent(message=f"Event {i}", value=i) for i in range(5)]
        for event in events:
            event_bus.publish(event)

        # Check history
        history = event_bus.get_event_history()
        assert len(history) == 5

        # Verify history contains all events in order
        for i, event_base in enumerate(history):
            event = cast(TestEvent, event_base)
            assert event.message == f"Event {i}"
            assert event.value == i

        # Test history clearing
        event_bus.clear_history()
        assert len(event_bus.get_event_history()) == 0

        # Test history size limit
        event_bus.set_max_history_size(3)

        # Publish more events than the limit
        for i in range(5):
            event_bus.publish(TestEvent(message=f"Limited {i}", value=i))

        # Check that only the most recent events are kept
        history = event_bus.get_event_history()
        assert len(history) == 3
        assert cast(TestEvent, history[0]).message == "Limited 2"
        assert cast(TestEvent, history[1]).message == "Limited 3"
        assert cast(TestEvent, history[2]).message == "Limited 4"

    def test_record_history_setting(self, event_bus: EventBus) -> None:
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
        for i, event_base in enumerate(history):
            event = cast(TestEvent, event_base)
            assert event.message == f"Event {i + 5}"

    def test_invalid_history_size(self, event_bus: EventBus) -> None:
        """Test setting invalid history size."""
        with pytest.raises(ValueError):
            event_bus.set_max_history_size(0)

        with pytest.raises(ValueError):
            event_bus.set_max_history_size(-10)


class TestEventDelivery:
    """Tests for event delivery mechanisms in EventBus."""

    def test_priority_ordering(self, event_bus: EventBus) -> None:
        """Test that handlers are called in priority order."""
        # Track the order of handler calls
        call_order = []

        # Define handler functions with different priorities
        def low_priority_handler(event: TestEvent) -> None:
            call_order.append("low")

        def normal_priority_handler(event: TestEvent) -> None:
            call_order.append("normal")

        def high_priority_handler(event: TestEvent) -> None:
            call_order.append("high")

        def critical_priority_handler(event: TestEvent) -> None:
            call_order.append("critical")

        # Subscribe handlers with different priorities
        event_bus.subscribe(TestEvent, low_priority_handler, priority=EventPriority.LOW)
        event_bus.subscribe(
            TestEvent, normal_priority_handler, priority=EventPriority.NORMAL
        )
        event_bus.subscribe(
            TestEvent, high_priority_handler, priority=EventPriority.HIGH
        )
        event_bus.subscribe(
            TestEvent, critical_priority_handler, priority=EventPriority.CRITICAL
        )

        # Publish an event
        event_bus.publish(TestEvent())

        # Verify handlers were called in order of decreasing priority
        assert call_order == ["critical", "high", "normal", "low"]

    def test_error_handling(self, event_bus: EventBus) -> None:
        """Test error handling during event processing."""
        # Create an error handler
        error_handler = TestErrorEventHandler()

        # Subscribe to error events
        event_bus.subscribe(ErrorEvent, error_handler)

        # Create a handler that will raise an exception
        def failing_handler(event: TestEvent) -> None:
            raise ValueError("Test error")

        # Subscribe the failing handler
        event_bus.subscribe(TestEvent, failing_handler)

        # Publish an event
        event_bus.publish(TestEvent())

        # Verify error event was published
        assert len(error_handler.error_events) == 1
        error_event = error_handler.error_events[0]
        assert error_event.error_type == "ValueError"
        assert error_event.message == "Test error"
        assert error_event.source is not None
        assert "EventBus._deliver_event" in error_event.source

    def test_nested_error_handling(self, event_bus: EventBus) -> None:
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

    def test_event_delivery_modes(self, event_bus: EventBus) -> None:
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
        # Type casting for async handlers
        event_bus.subscribe(
            TestEvent,
            cast(Any, async_handler),
            delivery_mode=EventDeliveryMode.ASYNCHRONOUS,
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

    def test_auto_detect_delivery_mode(self, event_bus: EventBus) -> None:
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
        # Type casting for async handlers
        event_bus.subscribe(TestEvent, cast(Any, async_function))
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


class TestAsyncEventHandling:
    """Tests for asynchronous event handling."""

    @pytest.mark.asyncio
    async def test_async_handlers(self, event_bus: EventBus) -> None:
        """Test asynchronous event handlers."""
        # Create an async handler
        async_handler = TestAsyncEventHandler()

        # Set up an event loop for testing
        loop = asyncio.get_event_loop()
        event_bus.set_event_loop(loop)

        # Subscribe async handler
        event_bus.subscribe(
            TestEvent,
            async_handler,
            delivery_mode=EventDeliveryMode.ASYNCHRONOUS,
        )

        # Create an async function handler
        async_events = []

        async def async_function_handler(event: TestEvent) -> None:
            async_events.append(event)

        # Subscribe async function
        event_bus.subscribe(
            TestEvent,
            cast(Any, async_function_handler),
            delivery_mode=EventDeliveryMode.ASYNCHRONOUS,
        )

        # Publish an event
        test_event = TestEvent(message="Async test", value=100)
        event_bus.publish(test_event)

        # Need to wait for async handlers to complete
        await asyncio.sleep(0.1)

        # Verify both handlers received the event
        assert len(async_handler.events) == 1
        assert async_handler.events[0] is test_event

        assert len(async_events) == 1
        assert async_events[0] is test_event

    def test_no_event_loop_error(self) -> None:
        """Test event loop auto-creation when none is available."""
        event_bus = EventBus()
        event_bus.initialize()

        # Make sure there's no event loop
        event_bus._event_loop = None

        # Subscribe an async handler
        async def async_handler(event: TestEvent) -> None:
            pass

        # Subscribe the handler
        event_bus.subscribe(
            TestEvent,
            cast(Any, async_handler),
            delivery_mode=EventDeliveryMode.ASYNCHRONOUS,
        )

        # Attempt to publish an event
        # Should create an event loop automatically if needed
        event_bus.publish(TestEvent())
        assert event_bus._event_loop is not None


class TestHandlerTypes:
    """Tests for various handler types."""

    def test_callable_handlers(self, event_bus: EventBus) -> None:
        """Test using callable functions as handlers."""
        # Create some handler functions
        function_events = []

        def function_handler(event: TestEvent) -> None:
            function_events.append(event)

        lambda_events = []

        def lambda_replacement_handler(event: TestEvent) -> None:
            lambda_events.append(event)

        # Subscribe functions
        event_bus.subscribe(TestEvent, function_handler)
        event_bus.subscribe(TestEvent, lambda_replacement_handler)

        # Publish an event
        test_event = TestEvent(message="Function test")
        event_bus.publish(test_event)

        # Verify both functions received the event
        assert len(function_events) == 1
        assert function_events[0] is test_event

        assert len(lambda_events) == 1
        assert lambda_events[0] is test_event

    def test_invalid_handler_types(self, event_bus: EventBus) -> None:
        """Test handling of invalid handler types."""
        # Try to use an invalid handler type
        invalid_handler = "not a callable or handler"

        with pytest.raises(TypeError):
            event_bus.subscribe(TestEvent, invalid_handler)  # type: ignore

    def test_handler_type_checking(self) -> None:
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

    def test_deliver_to_correct_handler_types(self) -> None:
        """Test delivery to different handler types."""
        event_bus = EventBus()
        event_bus.initialize()

        # Create various handler types
        sync_handler = MagicMock(spec=EventHandler)
        async_handler = MagicMock(spec=AsyncEventHandler)

        # Mock the internal delivery methods
        with (
            patch.object(event_bus, "_deliver_synchronous") as mock_sync,
            patch.object(event_bus, "_deliver_asynchronous") as mock_async,
        ):
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


class TestEventInheritance:
    """Tests for event inheritance and polymorphism."""

    def test_inheritance_subscription(self, event_bus: EventBus) -> None:
        """Test subscribing to parent class events."""

        # Create a subclass of TestEvent
        @dataclass
        class SpecializedEvent(TestEvent):
            special_data: str = "special"

        # Create handlers
        base_events = []
        specialized_events = []

        def base_handler(event: EventBase) -> None:
            base_events.append(event)

        def specialized_handler(event: SpecializedEvent) -> None:
            specialized_events.append(event)

        # Subscribe to different levels
        event_bus.subscribe(EventBase, base_handler)  # Parent class
        event_bus.subscribe(SpecializedEvent, specialized_handler)  # Specific class

        # Publish a specialized event
        special_event = SpecializedEvent(
            message="Inheritance test", special_data="important"
        )
        event_bus.publish(special_event)

        # Base handler should receive it (polymorphism)
        assert len(base_events) == 1

        # Specialized handler should receive it
        assert len(specialized_events) == 1
        assert specialized_events[0] is special_event
        assert specialized_events[0].special_data == "important"

        # Publish a regular test event
        regular_event = TestEvent(message="Regular event")
        event_bus.publish(regular_event)

        # Base handler should receive both events
        assert len(base_events) == 2

        # Specialized handler should only receive the specialized event
        assert len(specialized_events) == 1

    def test_event_source_auto_detection(self, event_bus: EventBus) -> None:
        """Test automatic detection of event source."""
        # Create an event without a source
        event = TestEvent()
        assert event.source is None

        # Publish the event
        event_bus.publish(event)

        # Source should have been set automatically
        assert event.source is not None
        assert "test_events.py" in event.source
