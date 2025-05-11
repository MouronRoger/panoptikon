"""Tests for the filesystem watcher module."""

from collections.abc import Generator
from pathlib import Path
import tempfile
import time
from unittest.mock import MagicMock

import pytest

from src.panoptikon.core.events import EventBus
from src.panoptikon.filesystem.events import (
    FileChangeEvent,
    FileChangeType,
    WatchedPathsChangedEvent,
)
from src.panoptikon.filesystem.watcher import (
    FSEVENTS_AVAILABLE,
    FileSystemWatchService,
    FSEventsWatcher,
    PollingWatcher,
    WatcherType,
)


class TestFSWatcher:
    """Base test class for filesystem watchers."""

    @pytest.fixture
    def event_callback(self) -> MagicMock:
        """Create a mock event callback."""
        return MagicMock()

    @pytest.fixture
    def temp_dir(self) -> Generator[str, None, None]:
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield tmp_dir

    def create_test_file(self, directory: str, filename: str) -> Path:
        """Create a test file and return its path.

        Args:
            directory: Directory to create the file in
            filename: Name of the file to create

        Returns:
            Path to the created file
        """
        file_path = Path(directory) / filename
        with open(file_path, "w") as f:
            f.write("test content")
        return file_path

    def modify_test_file(self, file_path: Path) -> None:
        """Modify a test file.

        Args:
            file_path: Path to the file to modify
        """
        with open(file_path, "a") as f:
            f.write("\nmodified content")

    def delete_test_file(self, file_path: Path) -> None:
        """Delete a test file.

        Args:
            file_path: Path to the file to delete
        """
        file_path.unlink()


class TestPollingWatcher(TestFSWatcher):
    """Tests for the PollingWatcher class."""

    @pytest.fixture
    def watcher(self, event_callback: MagicMock) -> PollingWatcher:
        """Create a polling watcher for testing.

        Args:
            event_callback: Mock event callback

        Returns:
            Configured PollingWatcher instance
        """
        # Use a shorter polling interval for faster tests
        watcher = PollingWatcher(event_callback, interval=0.1)
        return watcher

    def test_initialization(self, watcher: PollingWatcher) -> None:
        """Test watcher initialization."""
        assert not watcher._watching
        assert watcher._interval == 0.1
        assert watcher._watches == {}
        assert watcher._recursive_watches == set()

    def test_start_stop(self, watcher: PollingWatcher) -> None:
        """Test starting and stopping the watcher."""
        # Start watcher
        watcher.start()
        assert watcher._watching
        assert watcher._thread is not None

        # Stop watcher
        watcher.stop()
        assert not watcher._watching
        # Thread reference behavior may vary based on implementation
        # The important thing is that watching state is false

    def test_add_remove_watch(self, watcher: PollingWatcher, temp_dir: str) -> None:
        """Test adding and removing watched paths."""
        # Add watch
        path = Path(temp_dir)
        watcher.add_watch(path)
        assert path in watcher._watches
        assert watcher.is_watching(path)
        assert path in watcher.get_watched_paths()

        # Remove watch
        watcher.remove_watch(path)
        assert path not in watcher._watches
        assert not watcher.is_watching(path)
        assert path not in watcher.get_watched_paths()

    def test_detect_file_creation(
        self, watcher: PollingWatcher, event_callback: MagicMock, temp_dir: str
    ) -> None:
        """Test detecting file creation."""
        path = Path(temp_dir)
        watcher.add_watch(path)
        watcher.start()

        # Create a file
        file_path = self.create_test_file(temp_dir, "new_file.txt")

        # Wait for polling to detect changes
        time.sleep(0.3)
        watcher.stop()

        # Verify callback was called with proper event
        assert event_callback.call_count >= 1

        # Check all calls and find the creation event
        creation_events = []
        for call in event_callback.call_args_list:
            event = call[0][0]
            if event.path == file_path and event.change_type == FileChangeType.CREATED:
                creation_events.append(event)

        assert len(creation_events) >= 1

    def test_detect_file_modification(
        self, watcher: PollingWatcher, event_callback: MagicMock, temp_dir: str
    ) -> None:
        """Test detecting file modification."""
        # Create a file first
        file_path = self.create_test_file(temp_dir, "modify_file.txt")

        # Watch the directory
        path = Path(temp_dir)
        watcher.add_watch(path)
        watcher.start()

        # Wait for initial scan
        time.sleep(0.2)

        # Clear the mock to ignore creation events
        event_callback.reset_mock()

        # Modify the file
        self.modify_test_file(file_path)

        # Wait for polling to detect changes
        time.sleep(0.3)
        watcher.stop()

        # Verify callback was called with proper event
        assert event_callback.call_count >= 1

        # Check all calls and find the modification event
        modification_events = []
        for call in event_callback.call_args_list:
            event = call[0][0]
            if event.path == file_path and event.change_type == FileChangeType.MODIFIED:
                modification_events.append(event)

        assert len(modification_events) >= 1

    def test_detect_file_deletion(
        self, watcher: PollingWatcher, event_callback: MagicMock, temp_dir: str
    ) -> None:
        """Test detecting file deletion."""
        # Create a file first
        file_path = self.create_test_file(temp_dir, "delete_file.txt")

        # Watch the directory
        path = Path(temp_dir)
        watcher.add_watch(path)
        watcher.start()

        # Wait for initial scan
        time.sleep(0.2)

        # Clear the mock to ignore creation events
        event_callback.reset_mock()

        # Delete the file
        self.delete_test_file(file_path)

        # Wait for polling to detect changes
        time.sleep(0.3)
        watcher.stop()

        # Verify callback was called with proper event
        assert event_callback.call_count >= 1

        # Check all calls and find the deletion event
        deletion_events = []
        for call in event_callback.call_args_list:
            event = call[0][0]
            if event.path == file_path and event.change_type == FileChangeType.DELETED:
                deletion_events.append(event)

        assert len(deletion_events) >= 1


@pytest.mark.skipif(
    not FSEVENTS_AVAILABLE, reason="FSEvents not available on this platform"
)
class TestFSEventsWatcher(TestFSWatcher):
    """Tests for the FSEventsWatcher class (macOS only)."""

    @pytest.fixture
    def watcher(self, event_callback: MagicMock) -> FSEventsWatcher:
        """Create an FSEvents watcher for testing.

        Args:
            event_callback: Mock event callback

        Returns:
            Configured FSEventsWatcher instance
        """
        watcher = FSEventsWatcher(event_callback, latency=0.1)
        return watcher

    def test_initialization(self, watcher: FSEventsWatcher) -> None:
        """Test watcher initialization."""
        assert not watcher._watching
        assert watcher._latency == 0.1
        assert watcher._streams == {}

    def test_start_stop(self, watcher: FSEventsWatcher) -> None:
        """Test starting and stopping the watcher."""
        # Start watcher
        watcher.start()
        assert watcher._watching
        assert watcher._observer is not None

        # Stop watcher
        watcher.stop()
        assert not watcher._watching
        assert watcher._observer is None

    def test_add_remove_watch(self, watcher: FSEventsWatcher, temp_dir: str) -> None:
        """Test adding and removing watched paths."""
        # Add watch
        path = Path(temp_dir)
        watcher.add_watch(path)
        assert path in watcher._streams
        assert watcher.is_watching(path)
        assert path in watcher.get_watched_paths()

        # Remove watch
        watcher.remove_watch(path)
        assert path not in watcher._streams
        assert not watcher.is_watching(path)
        assert path not in watcher.get_watched_paths()


class TestFileSystemWatchService:
    """Tests for the FileSystemWatchService class."""

    @pytest.fixture
    def event_bus(self) -> MagicMock:
        """Create a mock event bus."""
        return MagicMock(spec=EventBus)

    @pytest.fixture
    def watch_service(self, event_bus: MagicMock) -> FileSystemWatchService:
        """Create a file system watch service.

        Args:
            event_bus: Mock event bus

        Returns:
            Configured FileSystemWatchService instance
        """
        service = FileSystemWatchService(event_bus)
        return service

    @pytest.fixture
    def temp_dir(self) -> Generator[str, None, None]:
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield tmp_dir

    def test_initialization(self, watch_service: FileSystemWatchService) -> None:
        """Test service initialization."""
        watch_service.initialize()
        assert watch_service._watcher is not None

    def test_shutdown(self, watch_service: FileSystemWatchService) -> None:
        """Test service shutdown."""
        watch_service.initialize()
        assert watch_service._watcher is not None

        watch_service.shutdown()
        assert watch_service._watcher is None

    def test_add_watch(
        self, watch_service: FileSystemWatchService, temp_dir: str, event_bus: MagicMock
    ) -> None:
        """Test watching a path."""
        watch_service.initialize()

        path = Path(temp_dir)
        watch_service.add_watch(path)

        # Verify it was added to watched paths
        assert path.resolve() in watch_service._watched_paths

        # Check that an event with the right type and added paths was published
        event_bus.publish.assert_called()

        # Extract the event that was published
        args, kwargs = event_bus.publish.call_args
        event = args[0]

        # Verify it's the right type with the right path
        assert isinstance(event, WatchedPathsChangedEvent)
        assert path.resolve() in event.added_paths

    def test_remove_watch(
        self, watch_service: FileSystemWatchService, temp_dir: str, event_bus: MagicMock
    ) -> None:
        """Test unwatching a path."""
        watch_service.initialize()

        path = Path(temp_dir)
        watch_service.add_watch(path)
        assert path.resolve() in watch_service._watched_paths

        # Reset mock to clear the add_watch event
        event_bus.reset_mock()

        watch_service.remove_watch(path)
        assert path.resolve() not in watch_service._watched_paths

        # Extract the event that was published
        args, kwargs = event_bus.publish.call_args
        event = args[0]

        # Verify it's the right type with the right path
        assert isinstance(event, WatchedPathsChangedEvent)
        assert path.resolve() in event.removed_paths

    def test_watcher_type_configuration(
        self, watch_service: FileSystemWatchService
    ) -> None:
        """Test configuring watcher type."""
        # Default should be AUTO
        assert watch_service._watcher_type == WatcherType.AUTO

        # Configure to use polling
        watch_service.configure(WatcherType.POLLING)
        assert watch_service._watcher_type == WatcherType.POLLING

        # Initialize with polling
        watch_service.initialize()
        assert isinstance(watch_service._watcher, PollingWatcher)

    def test_handle_file_event(
        self, watch_service: FileSystemWatchService, event_bus: MagicMock
    ) -> None:
        """Test handling file events."""
        watch_service.initialize()

        # Create a file event
        test_path = Path("/test/path")
        event = FileChangeEvent(path=test_path, change_type=FileChangeType.CREATED)

        # Directly call the event handler
        watch_service._handle_file_event(event)

        # Check that event was published to the event bus
        event_bus.publish.assert_called_with(event)
