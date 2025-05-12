"""Event system for component communication.

This module provides an event bus that enables components to communicate
through publish/subscribe patterns, supporting both synchronous and
asynchronous event handling.
"""

import asyncio
import json
import logging
import traceback
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Generic, Optional, TypeVar, Union

from ..core.service import ServiceInterface

logger = logging.getLogger(__name__)

T = TypeVar("T")
EventPayload = TypeVar("EventPayload")


class EventDeliveryMode(Enum):
    """Defines how events are delivered to subscribers."""

    SYNCHRONOUS = auto()
    ASYNCHRONOUS = auto()


class EventPriority(Enum):
    """Priority levels for event delivery."""

    LOW = 0
    NORMAL = 50
    HIGH = 100
    CRITICAL = 200


@dataclass
class EventBase:
    """Core event payload shared by every event type."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation.

        Returns:
            Dictionary representation of the event.
        """
        if is_dataclass(self):
            return asdict(self)

        # Fallback for non-dataclass events
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
        }

    def to_json(self) -> str:
        """Convert event to JSON string.

        Returns:
            JSON string representation of the event.
        """
        data = self.to_dict()
        # Convert timestamp to string
        if "timestamp" in data and isinstance(data["timestamp"], datetime):
            data["timestamp"] = data["timestamp"].isoformat()

        return json.dumps(data, default=str)


@dataclass
class ErrorEvent(EventBase):
    """Event issued when an error occurs in the system."""

    error_type: str = ""
    message: str = ""
    severity: str = "ERROR"
    traceback: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate required fields after initialization.

        Raises:
            ValueError: If error_type or message is empty.
        """
        if not self.error_type:
            raise ValueError("error_type is required")
        if not self.message:
            raise ValueError("message is required")

    def to_dict(self) -> dict[str, Any]:
        """Convert error event to dictionary representation.

        Returns:
            Dictionary representation of the error event.
        """
        # Build upon parent's to_dict method
        result = super().to_dict()
        # Add error-specific fields
        result.update(
            {
                "error_type": self.error_type,
                "message": self.message,
                "severity": self.severity,
            }
        )
        if self.traceback:
            result["traceback"] = self.traceback
        return result


class EventHandler(Generic[EventPayload], ABC):
    """Base class for event handlers."""

    @abstractmethod
    def handle(self, event: EventPayload) -> None:
        """Handle the event.

        Args:
            event: The event to handle.
        """
        pass


class AsyncEventHandler(Generic[EventPayload], ABC):
    """Base class for asynchronous event handlers."""

    @abstractmethod
    async def handle(self, event: EventPayload) -> None:
        """Handle the event asynchronously.

        Args:
            event: The event to handle.
        """
        pass


class EventSubscription:
    """Represents a subscription to an event type."""

    def __init__(
        self,
        event_type: type[EventBase],
        handler: Union[
            EventHandler[Any],
            AsyncEventHandler[Any],
            Callable[[Any], None],
            Callable[[Any], asyncio.Future[None]],
        ],
        priority: EventPriority = EventPriority.NORMAL,
        delivery_mode: EventDeliveryMode = EventDeliveryMode.SYNCHRONOUS,
    ) -> None:
        """Initialize a new event subscription.

        Args:
            event_type: Type of event to subscribe to.
            handler: Handler function or object to call when event occurs.
            priority: Priority of this subscription.
            delivery_mode: How events should be delivered to this subscriber.
        """
        self.event_type = event_type
        self.handler = handler
        self.priority = priority
        self.delivery_mode = delivery_mode
        self.subscription_id = str(uuid.uuid4())


class EventBus(ServiceInterface):
    """Central event bus for publish/subscribe communication between components."""

    def __init__(self) -> None:
        """Initialize a new event bus."""
        self._subscriptions: dict[type[EventBase], list[EventSubscription]] = {}
        self._event_history: list[EventBase] = []
        self._max_history_size = 1000
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._record_history = True

    def initialize(self) -> None:
        """Initialize the event bus.

        Required by ServiceInterface.
        """
        self._event_loop = (
            asyncio.get_event_loop() if not self._event_loop else self._event_loop
        )
        logger.debug("EventBus initialized")

    def shutdown(self) -> None:
        """Shutdown the event bus.

        Required by ServiceInterface.
        """
        self._subscriptions.clear()
        self._event_history.clear()
        logger.debug("EventBus shut down")

    def publish(self, event: EventBase) -> None:
        """Publish an event to all subscribers.

        Args:
            event: The event to publish.
        """
        if not event.source:
            # Try to get the caller as source
            frame = traceback.extract_stack()[-2]
            event.source = f"{frame.filename}:{frame.lineno}"

        # Record event in history
        if self._record_history:
            self._event_history.append(event)
            # Trim history if needed
            if len(self._event_history) > self._max_history_size:
                self._event_history = self._event_history[-self._max_history_size :]

        # Find all matching subscriptions
        subscriptions = self._get_matching_subscriptions(type(event))

        # Sort by priority
        subscriptions.sort(key=lambda s: s.priority.value, reverse=True)

        # Deliver to each subscriber
        for subscription in subscriptions:
            self._deliver_event(event, subscription)

    def subscribe(
        self,
        event_type: type[EventBase],
        handler: Union[
            EventHandler[T],
            AsyncEventHandler[T],
            Callable[[T], None],
            Callable[[T], asyncio.Future[None]],
        ],
        priority: EventPriority = EventPriority.NORMAL,
        delivery_mode: Optional[EventDeliveryMode] = None,
    ) -> str:
        """Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to.
            handler: Handler function or object to call when event occurs.
            priority: Priority of this subscription.
            delivery_mode: How events should be delivered to this subscriber.
                If None, will use ASYNCHRONOUS for coroutine functions and
                SYNCHRONOUS for regular functions.

        Returns:
            Subscription ID that can be used to unsubscribe.

        Raises:
            TypeError: If handler type is invalid.
        """
        # Validate handler type
        if not (
            callable(handler) or isinstance(handler, (EventHandler, AsyncEventHandler))
        ):
            raise TypeError(
                f"Handler must be callable or EventHandler/AsyncEventHandler, got: {type(handler)}"
            )

        # Determine delivery mode if not specified
        if delivery_mode is None:
            if isinstance(handler, AsyncEventHandler) or (
                callable(handler) and asyncio.iscoroutinefunction(handler)
            ):
                delivery_mode = EventDeliveryMode.ASYNCHRONOUS
            else:
                delivery_mode = EventDeliveryMode.SYNCHRONOUS

        # Create subscription
        subscription = EventSubscription(
            event_type=event_type,
            handler=handler,
            priority=priority,
            delivery_mode=delivery_mode,
        )

        # Add to subscriptions
        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = []
        self._subscriptions[event_type].append(subscription)

        return subscription.subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from an event.

        Args:
            subscription_id: ID of the subscription to remove.

        Returns:
            True if subscription was found and removed, False otherwise.
        """
        for event_type, subscriptions in self._subscriptions.items():
            for i, subscription in enumerate(subscriptions):
                if subscription.subscription_id == subscription_id:
                    subscriptions.pop(i)
                    # Remove empty subscription lists
                    if not subscriptions:
                        del self._subscriptions[event_type]
                    return True
        return False

    def get_event_history(self) -> list[EventBase]:
        """Get the event history.

        Returns:
            List of recorded events.
        """
        return self._event_history.copy()

    def clear_history(self) -> None:
        """Clear the event history."""
        self._event_history.clear()

    def set_max_history_size(self, size: int) -> None:
        """Set the maximum number of events to keep in history.

        Args:
            size: Maximum number of events to keep.

        Raises:
            ValueError: If size is not positive.
        """
        if size <= 0:
            raise ValueError("History size must be positive")
        self._max_history_size = size
        # Trim history if needed
        if len(self._event_history) > self._max_history_size:
            self._event_history = self._event_history[-self._max_history_size :]

    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set the event loop to use for asynchronous event delivery.

        Args:
            loop: The event loop to use.
        """
        self._event_loop = loop

    def set_record_history(self, record: bool) -> None:
        """Enable or disable event history recording.

        Args:
            record: Whether to record events in history.
        """
        self._record_history = record

    def _get_matching_subscriptions(
        self, event_type: type[EventBase]
    ) -> list[EventSubscription]:
        """Get all subscriptions matching the given event type.

        Args:
            event_type: Type of event to match.

        Returns:
            List of matching subscriptions.
        """
        result: list[EventSubscription] = []

        # Check direct subscriptions
        if event_type in self._subscriptions:
            result.extend(self._subscriptions[event_type])

        # Check subscriptions to parent classes
        for subscribed_type, subscriptions in self._subscriptions.items():
            if subscribed_type != event_type and issubclass(
                event_type, subscribed_type
            ):
                result.extend(subscriptions)

        return result

    def _deliver_event(self, event: EventBase, subscription: EventSubscription) -> None:
        """Deliver an event to a subscriber.

        Args:
            event: The event to deliver.
            subscription: The subscription to deliver to.
        """
        handler = subscription.handler

        try:
            if subscription.delivery_mode == EventDeliveryMode.SYNCHRONOUS:
                self._deliver_synchronous(event, handler)
            else:
                if not self._event_loop:
                    # Auto-create event loop if needed
                    self._event_loop = asyncio.get_event_loop()
                self._deliver_asynchronous(event, handler)
        except Exception as e:
            logger.error(
                f"Error delivering event {type(event).__name__} to handler: {e}",
                exc_info=True,
            )
            # Publish error event
            error_event = ErrorEvent(
                error_type=type(e).__name__,
                message=str(e),
                traceback=traceback.format_exc(),
                source=f"EventBus._deliver_event for {type(event).__name__}",
            )
            # Avoid infinite recursion by checking event type
            if not isinstance(event, ErrorEvent):
                self.publish(error_event)

    def _deliver_synchronous(self, event: EventBase, handler: Any) -> None:
        """Deliver an event synchronously.

        Args:
            event: The event to deliver.
            handler: The handler to deliver to.

        Raises:
            TypeError: If handler is not callable or EventHandler.
        """
        if isinstance(handler, EventHandler):
            # Check if handle method exists and is callable
            if not hasattr(handler, "handle") or not callable(handler.handle):
                raise TypeError("EventHandler missing callable handle method")
            handler.handle(event)
        elif callable(handler):
            handler(event)
        else:
            raise TypeError(f"Invalid handler type: {type(handler)}")

    def _deliver_asynchronous(self, event: EventBase, handler: Any) -> None:
        """Deliver an event asynchronously.

        Args:
            event: The event to deliver.
            handler: The handler to deliver to.

        Raises:
            RuntimeError: If event loop is not available.
            TypeError: If handler is not callable or AsyncEventHandler.
        """
        if not self._event_loop:
            raise RuntimeError("No event loop available for asynchronous delivery")

        if isinstance(handler, AsyncEventHandler):
            # Check if handle method exists and is callable
            if not hasattr(handler, "handle") or not callable(handler.handle):
                raise TypeError("AsyncEventHandler missing callable handle method")
            asyncio.run_coroutine_threadsafe(handler.handle(event), self._event_loop)
        elif callable(handler) and asyncio.iscoroutinefunction(handler):
            asyncio.run_coroutine_threadsafe(handler(event), self._event_loop)
        elif callable(handler):
            # Run regular function in executor
            self._event_loop.run_in_executor(None, handler, event)
        else:
            raise TypeError(f"Invalid handler type: {type(handler)}")
