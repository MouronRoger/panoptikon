"""Tests for the event system."""

import asyncio
from dataclasses import dataclass
from typing import List, Optional

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

    def __post_init__(self) -> None:
        """Post initialization hook."""
        pass  # No need to call super() since EventBase doesn't have __post_init__


class TestEventHandler(EventHandler[TestEvent]):
    """Test event handler for synchronous events."""

    events: List[TestEvent]

    def setup(self) -> None:
        """Initialize with empty event list."""
        self.events = []

    def handle(self, event: EventBase) -> None:
        """Store event in list."""
        if not hasattr(self, "events"):
            self.setup()
        self.events.append(event)  # type: ignore


class TestAsyncEventHandler(AsyncEventHandler[TestEvent]):
    """Test event handler for asynchronous events."""

    events: List[TestEvent]

    def setup(self) -> None:
        """Initialize with empty event list."""
        self.events = []

    async def handle(self, event: TestEvent) -> None:
        """Store event in list asynchronously."""
        if not hasattr(self, "events"):
            self.setup()
        self.events.append(event)


class ErrorEventHandler(EventHandler[ErrorEvent]):
    """Handler for error events."""

    error_events: List[ErrorEvent]

    def setup(self) -> None:
        """Initialize with empty error list."""
        self.error_events = []

    def handle(self, event: ErrorEvent) -> None:
        """Store error event in list."""
        if not hasattr(self, "error_events"):
            self.setup()
        self.error_events.append(event)


@pytest.fixture
def event_bus() -> EventBus:
    """Create an event bus for testing."""
    bus = EventBus()
    bus.initialize()
    return bus


@pytest.fixture
def sync_handler() -> TestEventHandler:
    """Create a synchronous event handler."""
    return TestEventHandler()


@pytest.fixture
def async_handler() -> TestAsyncEventHandler:
    """Create an asynchronous event handler."""
    return TestAsyncEventHandler()


@pytest.fixture
def error_handler() -> ErrorEventHandler:
    """Create an error event handler."""
    return ErrorEventHandler()


def test_event_bus_initialization(event_bus: EventBus) -> None:
    """Test event bus initialization."""
    # Verify that event_bus is properly initialized
    assert event_bus is not None
    assert isinstance(event_bus, EventBus)
    
    # Check initial state
    assert event_bus.get_event_history() == []


def test_simple_publish_subscribe(event_bus: EventBus, sync_handler: TestEventHandler) -> None:
    """Test basic publish-subscribe functionality."""
    # Subscribe to test events
    event_bus.subscribe(TestEvent, sync_handler)
    
    # Publish a test event
    test_event = TestEvent(message="Hello, world!", value=42)
    event_bus.publish(test_event)
    
    # Verify handler received event
    assert len(sync_handler.events) == 1
    assert sync_handler.events[0] is test_event
    assert sync_handler.events[0].message == "Hello, world!"  # type: ignore
    assert sync_handler.events[0].value == 42  # type: ignore
    
    # Verify event history
    history = event_bus.get_event_history()
    assert len(history) == 1
    assert history[0] is test_event


def test_multiple_handlers(event_bus: EventBus) -> None:
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
        assert handler.events[0].message == "Multi-handler test"  # type: ignore


def test_event_history_management(event_bus: EventBus) -> None:
    """Test event history management."""
    # Publish several events
    events = [TestEvent(message=f"Event {i}", value=i) for i in range(5)]
    for event in events:
        event_bus.publish(event)
    
    # Check history
    history = event_bus.get_event_history()
    assert len(history) == 5
    
    # Verify history contains all events in order
    for i, event in enumerate(history):
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
    assert history[0].message == "Limited 2"
    assert history[1].message == "Limited 3"
    assert history[2].message == "Limited 4"


def test_unsubscribe(event_bus: EventBus, sync_handler: TestEventHandler) -> None:
    """Test unsubscribing from events."""
    # Subscribe to test events
    subscription_id = event_bus.subscribe(TestEvent, sync_handler)
    
    # Publish an event
    event_bus.publish(TestEvent(message="Before unsubscribe"))
    assert len(sync_handler.events) == 1
    
    # Unsubscribe
    result = event_bus.unsubscribe(subscription_id)
    assert result is True
    
    # Publish another event
    event_bus.publish(TestEvent(message="After unsubscribe"))
    
    # Verify handler didn't receive the second event
    assert len(sync_handler.events) == 1
    assert sync_handler.events[0].message == "Before unsubscribe"
    
    # Try to unsubscribe with invalid ID
    result = event_bus.unsubscribe("invalid-id")
    assert result is False


def test_priority_ordering(event_bus: EventBus) -> None:
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
    event_bus.subscribe(TestEvent, normal_priority_handler, priority=EventPriority.NORMAL)
    event_bus.subscribe(TestEvent, high_priority_handler, priority=EventPriority.HIGH)
    event_bus.subscribe(TestEvent, critical_priority_handler, priority=EventPriority.CRITICAL)
    
    # Publish an event
    event_bus.publish(TestEvent())
    
    # Verify handlers were called in order of decreasing priority
    assert call_order == ["critical", "high", "normal", "low"]


def test_error_handling(event_bus: EventBus, error_handler: ErrorEventHandler) -> None:
    """Test error handling during event processing."""
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


@pytest.mark.asyncio
async def test_async_handlers(event_bus: EventBus, async_handler: TestAsyncEventHandler) -> None:
    """Test asynchronous event handlers."""
    # Set up an event loop for testing
    loop = asyncio.get_event_loop()
    event_bus.set_event_loop(loop)
    
    # Subscribe async handler
    event_bus.subscribe(
        TestEvent, 
        async_handler,
        delivery_mode=EventDeliveryMode.ASYNCHRONOUS
    )
    
    # Create an async function handler
    async_events = []
    
    async def async_function_handler(event: TestEvent) -> None:
        async_events.append(event)
    
    # Subscribe async function
    event_bus.subscribe(
        TestEvent, 
        async_function_handler,
        delivery_mode=EventDeliveryMode.ASYNCHRONOUS
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


def test_callable_handlers(event_bus: EventBus) -> None:
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


def test_inheritance_subscription(event_bus: EventBus) -> None:
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
    special_event = SpecializedEvent(message="Inheritance test", special_data="important")
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