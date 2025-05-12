"""Filesystem watching and monitoring.

This module provides abstractions for watching filesystem changes using
FSEvents (on macOS) with a fallback polling-based mechanism.
"""

import logging
import threading
from abc import ABC, abstractmethod
from enum import Enum, auto
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

from ..core.events import EventBus
from ..core.service import ServiceInterface
from .events import FileChangeEvent, FileChangeType, WatchedPathsChangedEvent

# Try to import FSEvents, fall back to polling if not available
try:
    from fsevents import Observer, Stream  # type: ignore

    FSEVENTS_AVAILABLE = True
except ImportError:
    FSEVENTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class WatcherType(Enum):
    """Type of filesystem watcher to use."""

    AUTO = auto()  # Choose best available
    FSEVENTS = auto()  # Use FSEvents (macOS only)
    POLLING = auto()  # Use polling (cross-platform)


class FSWatcher(ABC):
    """Abstract base class for filesystem watchers."""

    @abstractmethod
    def start(self) -> None:
        """Start watching for filesystem changes."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop watching for filesystem changes."""
        pass

    @abstractmethod
    def add_watch(self, path: Path, recursive: bool = True) -> None:
        """Add a path to the watch list.

        Args:
            path: The path to watch.
            recursive: Whether to watch subdirectories recursively.
        """
        pass

    @abstractmethod
    def remove_watch(self, path: Path) -> None:
        """Remove a path from the watch list.

        Args:
            path: The path to stop watching.
        """
        pass

    @abstractmethod
    def is_watching(self, path: Path) -> bool:
        """Check if a path is being watched.

        Args:
            path: The path to check.

        Returns:
            True if the path is being watched, False otherwise.
        """
        pass

    @abstractmethod
    def get_watched_paths(self) -> Set[Path]:
        """Get the set of paths currently being watched.

        Returns:
            Set of paths being watched.
        """
        pass


class FSEventsWatcher(FSWatcher):
    """Filesystem watcher using FSEvents (macOS only)."""

    def __init__(
        self, event_callback: Callable[[FileChangeEvent], None], latency: float = 0.1
    ) -> None:
        """Initialize FSEvents watcher.

        Args:
            event_callback: Callback to call when changes are detected.
            latency: Time to wait before processing events in seconds.

        Raises:
            ImportError: If FSEvents is not available.
        """
        if not FSEVENTS_AVAILABLE:
            raise ImportError("FSEvents not available on this platform")

        self._event_callback = event_callback
        self._latency = latency
        self._observer: Optional[Observer] = None
        self._streams: Dict[Path, Stream] = {}
        self._watching = False

    def start(self) -> None:
        """Start watching for filesystem changes."""
        if self._watching:
            return

        self._observer = Observer()
        self._observer.start()
        self._watching = True

        # Start any existing streams
        for path, stream in self._streams.items():
            self._observer.schedule(stream)

        logger.debug("FSEvents watcher started")

    def stop(self) -> None:
        """Stop watching for filesystem changes."""
        if not self._watching or not self._observer:
            return

        self._observer.stop()
        self._observer.join()
        self._observer = None
        self._watching = False
        logger.debug("FSEvents watcher stopped")

    def add_watch(self, path: Path, recursive: bool = True) -> None:
        """Add a path to the watch list.

        Args:
            path: The path to watch.
            recursive: Whether to watch subdirectories recursively.
        """
        if not path.exists():
            logger.warning(f"Attempted to watch non-existent path: {path}")
            return

        path_str = str(path)
        if path in self._streams:
            logger.debug(f"Path already being watched: {path}")
            return

        def _handle_event(
            event_path: str, mask: int, cookie: Optional[int] = None
        ) -> None:
            event_type = FileChangeType.UNKNOWN
            # Convert FSEvents flags to our change types
            if mask & 0x00000100:  # kFSEventStreamEventFlagItemCreated
                event_type = FileChangeType.CREATED
            elif mask & 0x00001000:  # kFSEventStreamEventFlagItemRemoved
                event_type = FileChangeType.DELETED
            elif mask & 0x00000200:  # kFSEventStreamEventFlagItemModified
                event_type = FileChangeType.MODIFIED
            elif mask & 0x00000800:  # kFSEventStreamEventFlagItemRenamed
                event_type = FileChangeType.RENAMED
            elif mask & 0x00000400:  # kFSEventStreamEventFlagItemChangeOwner
                event_type = FileChangeType.ATTRIBUTE_MODIFIED

            event = FileChangeEvent(
                path=Path(event_path),
                change_type=event_type,
            )
            self._event_callback(event)

        stream = Stream(_handle_event, path_str, file_events=True)
        self._streams[path] = stream

        # If already watching, schedule the new stream
        if self._watching and self._observer:
            self._observer.schedule(stream)

        logger.debug(f"Added watch for path: {path}")

    def remove_watch(self, path: Path) -> None:
        """Remove a path from the watch list.

        Args:
            path: The path to stop watching.
        """
        if path not in self._streams:
            logger.debug(f"Path not being watched: {path}")
            return

        stream = self._streams.pop(path)
        if self._watching and self._observer:
            self._observer.unschedule(stream)

        logger.debug(f"Removed watch for path: {path}")

    def is_watching(self, path: Path) -> bool:
        """Check if a path is being watched.

        Args:
            path: The path to check.

        Returns:
            True if the path is being watched, False otherwise.
        """
        return path in self._streams

    def get_watched_paths(self) -> Set[Path]:
        """Get the set of paths currently being watched.

        Returns:
            Set of paths being watched.
        """
        return set(self._streams.keys())


class PollingWatcher(FSWatcher):
    """Filesystem watcher using polling (cross-platform fallback)."""

    def __init__(
        self, event_callback: Callable[[FileChangeEvent], None], interval: float = 1.0
    ) -> None:
        """Initialize polling watcher.

        Args:
            event_callback: Callback to call when changes are detected.
            interval: Polling interval in seconds.
        """
        self._event_callback = event_callback
        self._interval = interval
        self._watches: Dict[Path, Dict[Path, float]] = (
            {}
        )  # Path -> {file_path -> mtime}
        self._recursive_watches: Set[Path] = set()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._watching = False

    def start(self) -> None:
        """Start watching for filesystem changes."""
        if self._watching:
            return

        # Initialize state for existing watches
        for path in list(self._watches.keys()):
            self._refresh_watch_state(path)

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._watch_thread, daemon=True)
        self._thread.start()
        self._watching = True
        logger.debug("Polling watcher started")

    def stop(self) -> None:
        """Stop watching for filesystem changes."""
        if not self._watching:
            return

        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        self._watching = False
        logger.debug("Polling watcher stopped")

    def add_watch(self, path: Path, recursive: bool = True) -> None:
        """Add a path to the watch list.

        Args:
            path: The path to watch.
            recursive: Whether to watch subdirectories recursively.
        """
        if not path.exists():
            logger.warning(f"Attempted to watch non-existent path: {path}")
            return

        if path in self._watches:
            logger.debug(f"Path already being watched: {path}")
            if recursive:
                self._recursive_watches.add(path)
            return

        self._watches[path] = {}
        if recursive:
            self._recursive_watches.add(path)

        # Initialize state
        self._refresh_watch_state(path)
        logger.debug(f"Added watch for path: {path}")

    def remove_watch(self, path: Path) -> None:
        """Remove a path from the watch list.

        Args:
            path: The path to stop watching.
        """
        if path not in self._watches:
            logger.debug(f"Path not being watched: {path}")
            return

        self._watches.pop(path)
        self._recursive_watches.discard(path)
        logger.debug(f"Removed watch for path: {path}")

    def is_watching(self, path: Path) -> bool:
        """Check if a path is being watched.

        Args:
            path: The path to check.

        Returns:
            True if the path is being watched, False otherwise.
        """
        return path in self._watches

    def get_watched_paths(self) -> Set[Path]:
        """Get the set of paths currently being watched.

        Returns:
            Set of paths being watched.
        """
        return set(self._watches.keys())

    def _refresh_watch_state(self, watch_path: Path) -> None:
        """Refresh the watched files state for a directory.

        Args:
            watch_path: The directory to refresh.
        """
        files: Dict[Path, float] = {}

        try:
            if watch_path.is_file():
                mtime = watch_path.stat().st_mtime
                files[watch_path] = mtime
            else:
                # Start with the directory itself
                files[watch_path] = watch_path.stat().st_mtime

                # Add all files in the directory
                for item_path in self._scan_directory(
                    watch_path, self._recursive_watches.issuperset([watch_path])
                ):
                    try:
                        mtime = item_path.stat().st_mtime
                        files[item_path] = mtime
                    except (PermissionError, FileNotFoundError):
                        # Skip files we can't access
                        pass

            self._watches[watch_path] = files
        except (PermissionError, FileNotFoundError) as e:
            logger.warning(f"Error refreshing watch state for {watch_path}: {e}")

    def _scan_directory(self, directory: Path, recursive: bool) -> List[Path]:
        """Scan a directory for files.

        Args:
            directory: The directory to scan.
            recursive: Whether to scan subdirectories.

        Returns:
            List of file paths found.
        """
        result: List[Path] = []

        try:
            for item in directory.iterdir():
                result.append(item)
                if recursive and item.is_dir():
                    result.extend(self._scan_directory(item, recursive))
        except (PermissionError, FileNotFoundError) as e:
            logger.warning(f"Error scanning directory {directory}: {e}")

        return result

    def _watch_thread(self) -> None:
        """Thread function for polling file changes."""
        while not self._stop_event.is_set():
            for watch_path in list(self._watches.keys()):
                try:
                    self._check_for_changes(watch_path)
                except Exception as e:
                    logger.error(f"Error checking for changes in {watch_path}: {e}")

            # Sleep for the polling interval
            self._stop_event.wait(self._interval)

    def _check_for_changes(self, watch_path: Path) -> None:
        """Check for changes in a watched directory.

        Args:
            watch_path: The directory to check.
        """
        if not watch_path.exists():
            self._handle_deleted_path(watch_path)
            return

        old_state = self._watches[watch_path]
        current_files = self._get_current_state(watch_path)

        # Process created and modified files
        self._process_new_and_modified_files(old_state, current_files)

        # Process deleted files
        self._process_deleted_files(old_state, current_files)

        # Update state
        self._watches[watch_path] = current_files

    def _handle_deleted_path(self, watch_path: Path) -> None:
        """Handle a watched path that no longer exists.

        Args:
            watch_path: The path that was deleted.
        """
        # Path was deleted, report all files as deleted
        for file_path in self._watches[watch_path]:
            event = FileChangeEvent(
                path=file_path,
                change_type=FileChangeType.DELETED,
            )
            self._event_callback(event)
        self._watches[watch_path] = {}

    def _get_current_state(self, watch_path: Path) -> Dict[Path, float]:
        """Get the current state of files in a directory.

        Args:
            watch_path: The directory to check.

        Returns:
            Dictionary mapping file paths to modification times.
        """
        current_files: Dict[Path, float] = {}

        # Scan current state
        if watch_path.is_file():
            try:
                mtime = watch_path.stat().st_mtime
                current_files[watch_path] = mtime
            except (PermissionError, FileNotFoundError):
                pass
        else:
            recursive = self._recursive_watches.issuperset([watch_path])
            for item_path in self._scan_directory(watch_path, recursive):
                try:
                    mtime = item_path.stat().st_mtime
                    current_files[item_path] = mtime
                except (PermissionError, FileNotFoundError):
                    # Skip files we can't access
                    pass

        return current_files

    def _process_new_and_modified_files(
        self, old_state: Dict[Path, float], current_files: Dict[Path, float]
    ) -> None:
        """Process created and modified files.

        Args:
            old_state: Previous file state.
            current_files: Current file state.
        """
        for file_path, mtime in current_files.items():
            if file_path not in old_state:
                self._emit_file_event(file_path, FileChangeType.CREATED)
            elif abs(mtime - old_state[file_path]) > 0.000001:
                self._emit_file_event(file_path, FileChangeType.MODIFIED)

    def _process_deleted_files(
        self, old_state: Dict[Path, float], current_files: Dict[Path, float]
    ) -> None:
        """Process deleted files.

        Args:
            old_state: Previous file state.
            current_files: Current file state.
        """
        for file_path in old_state:
            if file_path not in current_files:
                self._emit_file_event(file_path, FileChangeType.DELETED)

    def _emit_file_event(self, file_path: Path, change_type: FileChangeType) -> None:
        """Emit a file change event.

        Args:
            file_path: Path of the changed file.
            change_type: Type of change.
        """
        event = FileChangeEvent(
            path=file_path,
            change_type=change_type,
        )
        self._event_callback(event)


class FileSystemWatchService(ServiceInterface):
    """Service for watching filesystem changes."""

    def __init__(self, event_bus: EventBus) -> None:
        """Initialize the filesystem watch service.

        Args:
            event_bus: Event bus to publish events to.
        """
        self._event_bus = event_bus
        self._watcher: Optional[FSWatcher] = None
        self._watcher_type = WatcherType.AUTO
        self._watched_paths: Set[Path] = set()
        self._recursive_watches: Set[Path] = set()

    def initialize(self) -> None:
        """Initialize the service."""
        self._create_watcher()
        logger.debug("FileSystemWatchService initialized")

    def shutdown(self) -> None:
        """Shut down the service."""
        if self._watcher:
            self._watcher.stop()
            self._watcher = None
        logger.debug("FileSystemWatchService shut down")

    def configure(self, watcher_type: WatcherType = WatcherType.AUTO) -> None:
        """Configure the watch service.

        Args:
            watcher_type: Type of watcher to use.
        """
        if watcher_type != self._watcher_type:
            old_watcher = self._watcher
            self._watcher_type = watcher_type

            # Create new watcher
            self._create_watcher()

            # Transfer watched paths
            if old_watcher and self._watcher:
                watched = old_watcher.get_watched_paths()
                for path in watched:
                    recursive = path in self._recursive_watches
                    self._watcher.add_watch(path, recursive)

                # Stop old watcher
                old_watcher.stop()

    def start_watching(self) -> None:
        """Start watching for changes."""
        if self._watcher:
            self._watcher.start()

    def stop_watching(self) -> None:
        """Stop watching for changes."""
        if self._watcher:
            self._watcher.stop()

    def add_watch(self, path: Path, recursive: bool = True) -> None:
        """Add a path to watch.

        Args:
            path: Path to watch.
            recursive: Whether to watch recursively.
        """
        path = path.resolve()
        self._watched_paths.add(path)
        if recursive:
            self._recursive_watches.add(path)

        if self._watcher:
            self._watcher.add_watch(path, recursive)

        # Notify about the new watch
        self._event_bus.publish(WatchedPathsChangedEvent(added_paths={path}))

    def remove_watch(self, path: Path) -> None:
        """Remove a path from watches.

        Args:
            path: Path to stop watching.
        """
        path = path.resolve()
        self._watched_paths.discard(path)
        self._recursive_watches.discard(path)

        if self._watcher:
            self._watcher.remove_watch(path)

        # Notify about the removed watch
        self._event_bus.publish(WatchedPathsChangedEvent(removed_paths={path}))

    def is_watching(self, path: Path) -> bool:
        """Check if a path is being watched.

        Args:
            path: Path to check.

        Returns:
            True if the path is being watched.
        """
        if not self._watcher:
            return False
        return self._watcher.is_watching(path.resolve())

    def get_watched_paths(self) -> Set[Path]:
        """Get all watched paths.

        Returns:
            Set of watched paths.
        """
        if not self._watcher:
            return set()
        return self._watcher.get_watched_paths()

    def _create_watcher(self) -> None:
        """Create the appropriate watcher based on configuration."""
        # Select watcher type
        watcher_type = self._watcher_type
        if watcher_type == WatcherType.AUTO:
            if FSEVENTS_AVAILABLE:
                watcher_type = WatcherType.FSEVENTS
            else:
                watcher_type = WatcherType.POLLING

        # Create the watcher
        try:
            if watcher_type == WatcherType.FSEVENTS and FSEVENTS_AVAILABLE:
                self._watcher = FSEventsWatcher(self._handle_file_event)
                logger.info("Using FSEvents file system watcher")
            else:
                self._watcher = PollingWatcher(self._handle_file_event)
                logger.info("Using polling file system watcher")
        except Exception as e:
            logger.error(f"Failed to create watcher: {e}")
            # Fall back to polling
            self._watcher = PollingWatcher(self._handle_file_event)
            logger.info("Falling back to polling file system watcher")

    def _handle_file_event(self, event: FileChangeEvent) -> None:
        """Handle file change events from the watcher.

        Args:
            event: The file change event.
        """
        # Publish the event to the event bus
        self._event_bus.publish(event)
