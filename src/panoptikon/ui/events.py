from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

from panoptikon.core.events import EventBase

# NOTE: Due to Python 3.9 dataclass limitations, fields without defaults cannot follow
# fields with defaults from the parent class. We use explicit __init__ methods for all
# event classes with required fields and do not use @dataclass for those classes.


@dataclass
class WindowEvent(EventBase):
    """Base class for all window-related events."""

    pass


class SecondaryWindowCreatedEvent(WindowEvent):
    """Event issued when the secondary window is created."""

    position: Tuple[int, int]

    def __init__(
        self,
        position: Tuple[int, int],
        event_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        source: Optional[str] = None,
    ) -> None:
        """Initialize SecondaryWindowCreatedEvent."""
        if event_id is not None and timestamp is not None:
            super().__init__(event_id=event_id, timestamp=timestamp, source=source)
        elif event_id is not None:
            super().__init__(event_id=event_id, source=source)
        elif timestamp is not None:
            super().__init__(timestamp=timestamp, source=source)
        else:
            super().__init__(source=source)
        self.position = position


class SecondaryWindowClosedEvent(WindowEvent):
    """Event issued when the secondary window is closed."""

    def __init__(
        self,
        event_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        source: Optional[str] = None,
    ) -> None:
        """Initialize SecondaryWindowClosedEvent."""
        if event_id is not None and timestamp is not None:
            super().__init__(event_id=event_id, timestamp=timestamp, source=source)
        elif event_id is not None:
            super().__init__(event_id=event_id, source=source)
        elif timestamp is not None:
            super().__init__(timestamp=timestamp, source=source)
        else:
            super().__init__(source=source)


class WindowActivatedEvent(WindowEvent):
    """Event issued when a window is activated."""

    window_type: str  # "main" or "secondary"
    previous_window: str  # "main" or "secondary"

    def __init__(
        self,
        window_type: str,
        previous_window: str,
        event_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        source: Optional[str] = None,
    ) -> None:
        """Initialize WindowActivatedEvent."""
        if event_id is not None and timestamp is not None:
            super().__init__(event_id=event_id, timestamp=timestamp, source=source)
        elif event_id is not None:
            super().__init__(event_id=event_id, source=source)
        elif timestamp is not None:
            super().__init__(timestamp=timestamp, source=source)
        else:
            super().__init__(source=source)
        self.window_type = window_type
        self.previous_window = previous_window


class WindowResourceSuspendedEvent(WindowEvent):
    """Event issued when a window's resources are suspended."""

    window_type: str  # "main" or "secondary"

    def __init__(
        self,
        window_type: str,
        event_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        source: Optional[str] = None,
    ) -> None:
        """Initialize WindowResourceSuspendedEvent."""
        if event_id is not None and timestamp is not None:
            super().__init__(event_id=event_id, timestamp=timestamp, source=source)
        elif event_id is not None:
            super().__init__(event_id=event_id, source=source)
        elif timestamp is not None:
            super().__init__(timestamp=timestamp, source=source)
        else:
            super().__init__(source=source)
        self.window_type = window_type


class WindowResourceResumedEvent(WindowEvent):
    """Event issued when a window's resources are resumed."""

    window_type: str  # "main" or "secondary"

    def __init__(
        self,
        window_type: str,
        event_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        source: Optional[str] = None,
    ) -> None:
        """Initialize WindowResourceResumedEvent."""
        if event_id is not None and timestamp is not None:
            super().__init__(event_id=event_id, timestamp=timestamp, source=source)
        elif event_id is not None:
            super().__init__(event_id=event_id, source=source)
        elif timestamp is not None:
            super().__init__(timestamp=timestamp, source=source)
        else:
            super().__init__(source=source)
        self.window_type = window_type


class WindowDragOperationEvent(WindowEvent):
    """Event issued for drag operations between windows."""

    source_window: str  # "main" or "secondary"
    target_window: str  # "main" or "secondary"
    files: List[str]

    def __init__(
        self,
        source_window: str,
        target_window: str,
        files: List[str],
        event_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        source: Optional[str] = None,
    ) -> None:
        """Initialize WindowDragOperationEvent."""
        if event_id is not None and timestamp is not None:
            super().__init__(event_id=event_id, timestamp=timestamp, source=source)
        elif event_id is not None:
            super().__init__(event_id=event_id, source=source)
        elif timestamp is not None:
            super().__init__(timestamp=timestamp, source=source)
        else:
            super().__init__(source=source)
        self.source_window = source_window
        self.target_window = target_window
        self.files = files
