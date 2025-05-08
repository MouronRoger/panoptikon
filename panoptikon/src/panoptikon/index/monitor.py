"""File system monitoring for detecting real-time changes."""

import logging
import os
import queue
import threading
import time
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Union

try:
    from watchdog.events import (
        FileSystemEvent,
        FileSystemEventHandler,
        FileCreatedEvent,
        FileDeletedEvent,
        FileModifiedEvent,
        DirCreatedEvent,
        DirDeletedEvent,
    )
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

logger = logging.getLogger(__name__)


class FileEventType(Enum):
    """Types of file system events that can be monitored."""

    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


class FileEvent:
    """Represents a file system event."""

    def __init__(
        self,
        event_type: FileEventType,
        path: str,
        is_directory: bool = False,
        dest_path: Optional[str] = None,
    ):
        """Initialize a new file event.

        Args:
            event_type: Type of the event (created, modified, deleted, moved)
            path: Path where the event occurred
            is_directory: Whether the event target is a directory
            dest_path: Destination path for moved events
        """
        self.event_type = event_type
        self.path = path
        self.is_directory = is_directory
        self.dest_path = dest_path
        self.timestamp = time.time()

    def __str__(self) -> str:
        """Get string representation of the event.

        Returns:
            String representation
        """
        base_str = (
            f"{self.event_type.value.capitalize()} "
            f"{'directory' if self.is_directory else 'file'}: {self.path}"
        )
        if self.event_type == FileEventType.MOVED and self.dest_path:
            base_str += f" -> {self.dest_path}"
        return base_str


class DirectoryMonitor:
    """Monitors directories for file system changes.

    This class provides functionality to watch directories for changes
    and report them via callbacks or an event queue.
    """

    def __init__(
        self,
        callback: Optional[Callable[[FileEvent], None]] = None,
        recursive: bool = True,
        use_polling: bool = False,
        polling_interval: float = 1.0,
    ):
        """Initialize the directory monitor.

        Args:
            callback: Optional callback function that receives file events
            recursive: Whether to monitor subdirectories recursively
            use_polling: Force polling instead of native APIs
            polling_interval: Interval for polling in seconds
        """
        if not WATCHDOG_AVAILABLE:
            raise ImportError(
                "The watchdog package is required for directory monitoring. "
                "Install it with: pip install watchdog"
            )

        self.callback = callback
        self.recursive = recursive
        self.use_polling = use_polling
        self.polling_interval = polling_interval

        self._observer = None
        self._event_queue: queue.Queue = queue.Queue()
        self._watched_paths: Set[str] = set()
        self._stop_event = threading.Event()
        self._lock = threading.RLock()

    def _create_observer(self) -> Observer:
        """Create and configure a file system observer.

        Returns:
            Configured watchdog Observer
        """
        if self.use_polling:
            # Use polling observer for compatibility
            from watchdog.observers.polling import PollingObserver
            
            observer = PollingObserver(timeout=self.polling_interval)
        else:
            # Use the most efficient observer for the platform
            observer = Observer()

        return observer

    def start_monitoring(self, paths: List[Union[str, Path]]) -> None:
        """Start monitoring the specified directories.

        Args:
            paths: List of directory paths to monitor

        Raises:
            ValueError: If no paths are provided or a path doesn't exist
            RuntimeError: If monitoring is already active
        """
        if not paths:
            raise ValueError("At least one path must be provided for monitoring")

        with self._lock:
            if self._observer is not None and self._observer.is_alive():
                raise RuntimeError("Monitoring is already active")

            # Create a new observer
            self._observer = self._create_observer()
            
            # Create event handler
            event_handler = self._create_event_handler()
            
            # Schedule monitoring for each path
            for path in paths:
                path_str = str(path)
                path_obj = Path(path_str)
                
                if not path_obj.exists():
                    raise ValueError(f"Path does not exist: {path_str}")
                
                if not path_obj.is_dir():
                    raise ValueError(f"Path is not a directory: {path_str}")
                
                self._observer.schedule(
                    event_handler, path_str, recursive=self.recursive
                )
                self._watched_paths.add(path_str)
            
            # Start the observer
            self._observer.start()
            
            logger.info(
                f"Started monitoring {len(paths)} "
                f"director{'ies' if len(paths) > 1 else 'y'}"
            )

    def stop_monitoring(self) -> None:
        """Stop all directory monitoring."""
        with self._lock:
            if self._observer is not None and self._observer.is_alive():
                self._observer.stop()
                self._observer.join()
                self._observer = None
                self._watched_paths.clear()
                logger.info("Stopped directory monitoring")

    def _create_event_handler(self) -> FileSystemEventHandler:
        """Create an event handler for file system events.

        Returns:
            FileSystemEventHandler implementation
        """
        monitor = self

        class PanoptikonEventHandler(FileSystemEventHandler):
            """Custom event handler for Panoptikon file monitoring."""

            def dispatch(self, event: FileSystemEvent) -> None:
                """Process file system events.

                Args:
                    event: Watchdog file system event
                """
                # Convert watchdog event to our FileEvent
                file_event = None
                
                if isinstance(event, FileCreatedEvent):
                    file_event = FileEvent(
                        FileEventType.CREATED,
                        event.src_path,
                        isinstance(event, DirCreatedEvent),
                    )
                elif isinstance(event, FileModifiedEvent):
                    file_event = FileEvent(
                        FileEventType.MODIFIED,
                        event.src_path,
                        False,  # watchdog doesn't have DirModifiedEvent
                    )
                elif isinstance(event, FileDeletedEvent):
                    file_event = FileEvent(
                        FileEventType.DELETED,
                        event.src_path,
                        isinstance(event, DirDeletedEvent),
                    )
                elif hasattr(event, "dest_path"):
                    # This is a move event
                    file_event = FileEvent(
                        FileEventType.MOVED,
                        event.src_path,
                        event.is_directory,
                        getattr(event, "dest_path", None),
                    )
                
                if file_event:
                    # Add to queue
                    monitor._event_queue.put(file_event)
                    
                    # Call callback if provided
                    if monitor.callback:
                        try:
                            monitor.callback(file_event)
                        except Exception as e:
                            logger.error(
                                f"Error in file event callback: {e}"
                            )

        return PanoptikonEventHandler()

    def get_events(self, timeout: Optional[float] = None) -> List[FileEvent]:
        """Get pending file events from the queue.

        Args:
            timeout: Maximum time to wait for events in seconds (None to return immediately)

        Returns:
            List of FileEvent objects
        """
        events = []
        start_time = time.time()
        
        try:
            # Get at least one event
            try:
                event = self._event_queue.get(timeout=timeout)
                events.append(event)
                self._event_queue.task_done()
            except queue.Empty:
                # No events available
                return events
            
            # Get any additional events without waiting
            remaining_timeout = (
                None if timeout is None else timeout - (time.time() - start_time)
            )
            while remaining_timeout is None or remaining_timeout > 0:
                try:
                    event = self._event_queue.get(
                        timeout=0 if timeout is None else remaining_timeout
                    )
                    events.append(event)
                    self._event_queue.task_done()
                except queue.Empty:
                    break
                
                if timeout is not None:
                    remaining_timeout = timeout - (time.time() - start_time)
        
        except Exception as e:
            logger.error(f"Error getting file events: {e}")
        
        return events

    def is_active(self) -> bool:
        """Check if monitoring is currently active.

        Returns:
            True if monitoring is active, False otherwise
        """
        with self._lock:
            return self._observer is not None and self._observer.is_alive()

    def get_watched_paths(self) -> List[str]:
        """Get the list of currently monitored paths.

        Returns:
            List of path strings
        """
        with self._lock:
            return list(self._watched_paths)

    def __enter__(self) -> "DirectoryMonitor":
        """Context manager enter method.

        Returns:
            Self reference
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit method.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        self.stop_monitoring()


def monitor_directories(
    paths: List[Union[str, Path]],
    callback: Callable[[FileEvent], None],
    recursive: bool = True,
) -> DirectoryMonitor:
    """Start monitoring directories for changes.

    This is a convenience function that creates a DirectoryMonitor
    and immediately starts monitoring the specified directories.

    Args:
        paths: List of directory paths to monitor
        callback: Callback function that receives file events
        recursive: Whether to monitor subdirectories recursively

    Returns:
        DirectoryMonitor instance (call stop_monitoring() when done)

    Raises:
        ValueError: If no paths are provided or a path doesn't exist
        ImportError: If watchdog package is not installed
    """
    monitor = DirectoryMonitor(callback=callback, recursive=recursive)
    monitor.start_monitoring(paths)
    return monitor 