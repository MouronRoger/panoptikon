"""Event system for component communication (patched version).

This module provides an event bus that enables components to communicate
through publish/subscribe patterns, supporting both synchronous and
asynchronous event handling.
"""

from abc import ABC, abstractmethod
import asyncio
from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum, auto
import json
import logging
import traceback
from typing import Any, Callable, Generic, Optional, TypeVar, Union
import uuid


class ServiceInterface:
    """Temporary base class for tests."""

    def initialize(self) -> None:
        """Initialize the service."""
        pass

    def shutdown(self) -> None:
        """Perform cleanup when the service is being disposed."""
        pass


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


class EventBase:
    """Base class for all events in the system."""

    def __init__(
        self,
        event_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        source: Optional[str] = None,
    ) -> None:
        """Initialize the event base.

        Args:
            event_id: Unique ID for the event (auto-generated if not provided)
            timestamp: Event creation time (auto-generated if not provided)
            source: Source of the event
        """
        self.event_id = event_id or str(uuid.uuid4())
        self.timestamp = timestamp or datetime.now()
        self.source = source

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


class ErrorEvent(EventBase):
    """Event issued when an error occurs in the system."""

    def __init__(
        self,
        error_type: str,
        message: str,
        event_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        source: Optional[str] = None,
        severity: str = "ERROR",
        traceback: Optional[str] = None,
    ) -> None:
        """Initialize the error event.

        Args:
            error_type: Type of error that occurred
            message: Error message
            event_id: Unique ID for the event
            timestamp: Event creation time
            source: Source of the event
            severity: Error severity level
            traceback: Error traceback information
        """
        super().__init__(event_id, timestamp, source)
        self.error_type = error_type
        self.message = message
        self.severity = severity
        self.traceback = traceback


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
        """
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
                    if not subscriptions:
                        del self._subscriptions[event_type]
                    return True
        return False

    def get_event_history(self) -> list[EventBase]:
        """Get the event history.

        Returns:
            List of all events that have been published, up to the max history size.
        """
        return self._event_history.copy()

    def clear_history(self) -> None:
        """Clear the event history."""
        self._event_history.clear()

    def set_max_history_size(self, size: int) -> None:
        """Set the maximum number of events to keep in history.

        Args:
            size: Maximum number of events to keep in history.

        Raises:
            ValueError: If size is less than 1.
        """
        if size < 1:
            raise ValueError("History size must be at least 1")
        self._max_history_size = size
        if len(self._event_history) > size:
            self._event_history = self._event_history[-size:]

    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set the event loop to use for asynchronous event delivery.

        Args:
            loop: The event loop to use.
        """
        self._event_loop = loop

    def set_record_history(self, record: bool) -> None:
        """Set whether to record events in history.

        Args:
            record: Whether to record events.
        """
        self._record_history = record

    def _get_matching_subscriptions(
        self, event_type: type[EventBase]
    ) -> list[EventSubscription]:
        """Get all subscriptions that match the event type.

        This includes subscriptions to parent classes of the event type.

        Args:
            event_type: Type of event to match.

        Returns:
            List of matching subscriptions.
        """
        result: list[EventSubscription] = []

        # Add direct subscriptions
        if event_type in self._subscriptions:
            result.extend(self._subscriptions[event_type])

        # Add subscriptions to parent classes
        for sub_type, subscriptions in self._subscriptions.items():
            if (
                event_type != sub_type
                and issubclass(event_type, sub_type)
                and not any(s.event_type == sub_type for s in result)
            ):
                result.extend(subscriptions)

        return result

    def _deliver_event(self, event: EventBase, subscription: EventSubscription) -> None:
        """Deliver an event to a subscriber.

        Args:
            event: The event to deliver.
            subscription: The subscription to deliver to.
        """
        try:
            if subscription.delivery_mode == EventDeliveryMode.ASYNCHRONOUS:
                self._deliver_asynchronous(event, subscription.handler)
            else:
                self._deliver_synchronous(event, subscription.handler)
        except Exception as e:
            # Log the error but don't re-raise to avoid breaking the event chain
            logger.error(
                f"Error delivering event {event.event_id} to subscription "
                f"{subscription.subscription_id}: {e}",
                exc_info=True,
            )

    def _deliver_synchronous(self, event: EventBase, handler: Any) -> None:
        """Deliver an event synchronously.

        Args:
            event: The event to deliver.
            handler: The handler to deliver to.
        """
        if isinstance(handler, EventHandler):
            handler.handle(event)
        elif callable(handler):
            handler(event)
        else:
            logger.error(f"Invalid handler type: {type(handler)}")

    def _deliver_asynchronous(self, event: EventBase, handler: Any) -> None:
        """Deliver an event asynchronously.

        Args:
            event: The event to deliver.
            handler: The handler to deliver to.
        """
        if not self._event_loop:
            self._event_loop = asyncio.get_event_loop()

        if isinstance(handler, AsyncEventHandler):
            self._event_loop.create_task(handler.handle(event))
        elif callable(handler) and asyncio.iscoroutinefunction(handler):
            self._event_loop.create_task(handler(event))
        else:
            # Fallback to synchronous delivery
            self._deliver_synchronous(event, handler)
