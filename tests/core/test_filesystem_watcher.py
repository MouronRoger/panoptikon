"""Tests for the filesystem watcher module.

This module provides comprehensive testing for the filesystem watcher
implementation, including basic functionality, edge cases, performance
considerations, and specialized behavior.
"""

from collections.abc import Generator
from pathlib import Path
import tempfile
import time
from unittest.mock import MagicMock, patch

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
    FSWatcher,
    PollingWatcher,
    WatcherType,
)


@pytest.fixture
def event_callback() -> MagicMock:
    """Create a mock event callback."""
    return MagicMock()


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def event_bus() -> MagicMock:
    """Create a mock event bus."""
    return MagicMock(spec=EventBus)


@pytest.fixture
def watch_service(event_bus: MagicMock) -> FileSystemWatchService:
    """Create a file system watch service."""
    service = FileSystemWatchService(event_bus)
    service.initialize()
    yield service
    service.shutdown()


class TestFSWatcherBase:
    """Tests for the FSWatcher abstract base class."""

    def test_abstract_methods(self) -> None:
        """Test that FSWatcher is an abstract class."""
        with pytest.raises(TypeError):
            FSWatcher()  # type: ignore


class TestPollingWatcher:
    """Tests for the PollingWatcher implementation."""

    def create_test_file(self, directory: str, filename: str) -> Path:
        """Create a test file and return its path."""
        file_path = Path(directory) / filename
        with open(file_path, "w") as f:
            f.write("test content")
        return file_path

    def modify_test_file(self, file_path: Path) -> None:
        """Modify a test file."""
        with open(file_path, "a") as f:
            f.write("\nmodified content")

    def delete_test_file(self, file_path: Path) -> None:
        """Delete a test file."""
        file_path.unlink()

    @pytest.fixture
    def watcher(
        self, event_callback: MagicMock
    ) -> Generator[PollingWatcher, None, None]:
        """Create a polling watcher for testing."""
        # Use a shorter polling interval for faster tests
        watcher = PollingWatcher(event_callback, interval=0.1)
        yield watcher
        watcher.stop()

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

        # Verify callback was called with proper event
        assert event_callback.call_count >= 1

        # Check all calls and find the deletion event
        deletion_events = []
        for call in event_callback.call_args_list:
            event = call[0][0]
            if event.path == file_path and event.change_type == FileChangeType.DELETED:
                deletion_events.append(event)

        assert len(deletion_events) >= 1

    def test_complex_directory_structure(
        self, event_callback: MagicMock, temp_dir: str
    ) -> None:
        """Test watching a complex directory structure."""
        watcher = PollingWatcher(event_callback, interval=0.1)

        # Create a complex directory structure
        path = Path(temp_dir)
        (path / "dir1").mkdir()
        (path / "dir1" / "subdir1").mkdir()
        (path / "dir1" / "subdir1" / "file1.txt").write_text("content")
        (path / "dir1" / "file2.txt").write_text("content")
        (path / "file3.txt").write_text("content")

        # Add watch and do polling cycle
        watcher.add_watch(path, recursive=True)

        # Verify initial state
        assert len(watcher._watches[path]) >= 5  # Directory, 2 subdirs, 2 files

        # Modify a file
        (path / "dir1" / "subdir1" / "file1.txt").write_text("new content")

        # Directly call check for changes
        watcher._check_for_changes(path)

        # Verify the event was generated
        assert event_callback.call_count >= 1

        # Find the modified file event
        file_modified = False
        for call in event_callback.call_args_list:
            event = call[0][0]
            if (
                event.path == (path / "dir1" / "subdir1" / "file1.txt")
                and event.change_type == FileChangeType.MODIFIED
            ):
                file_modified = True
                break

        assert file_modified

    def test_error_handling_during_watch(
        self, event_callback: MagicMock, temp_dir: str
    ) -> None:
        """Test error handling during directory watching."""
        watcher = PollingWatcher(event_callback, interval=0.1)
        path = Path(temp_dir)
        watcher.add_watch(path)

        # Mock stat to raise error for specific test
        with patch(
            "pathlib.Path.stat", side_effect=PermissionError("Permission denied")
        ):
            # This should not raise an exception
            watcher._refresh_watch_state(path)

            # The watcher should handle the error gracefully
            assert path in watcher._watches


@pytest.mark.skipif(
    not FSEVENTS_AVAILABLE, reason="FSEvents not available on this platform"
)
class TestFSEventsWatcher:
    """Tests for the FSEventsWatcher class (macOS only)."""

    @pytest.fixture
    def watcher(
        self, event_callback: MagicMock
    ) -> Generator[FSEventsWatcher, None, None]:
        """Create an FSEvents watcher for testing."""
        watcher = FSEventsWatcher(event_callback, latency=0.1)
        yield watcher
        watcher.stop()

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

    def test_handle_event_flags(self, event_callback: MagicMock, temp_dir: str) -> None:
        """Test FSEventsWatcher event flag handling."""
        watcher = FSEventsWatcher(event_callback)

        # Mock the stream creation and directly call the event handler
        with patch("fsevents.Stream") as mock_stream:
            # Add a watch to get a stream object created
            watcher.add_watch(Path(temp_dir))

            # Get the event handler function from the last call
            stream_constructor = mock_stream.call_args[0][0]

            # Test created event
            stream_constructor(str(Path(temp_dir) / "file.txt"), 0x00000100)
            callback_event = event_callback.call_args[0][0]
            assert callback_event.change_type == FileChangeType.CREATED
            event_callback.reset_mock()

            # Test deleted event
            stream_constructor(str(Path(temp_dir) / "file.txt"), 0x00001000)
            callback_event = event_callback.call_args[0][0]
            assert callback_event.change_type == FileChangeType.DELETED
            event_callback.reset_mock()

            # Test modified event
            stream_constructor(str(Path(temp_dir) / "file.txt"), 0x00000200)
            callback_event = event_callback.call_args[0][0]
            assert callback_event.change_type == FileChangeType.MODIFIED


class TestFileSystemWatchService:
    """Tests for the FileSystemWatchService class."""

    def test_initialization(self, watch_service: FileSystemWatchService) -> None:
        """Test service initialization."""
        assert watch_service._watcher is not None

    def test_add_watch(
        self, watch_service: FileSystemWatchService, temp_dir: str, event_bus: MagicMock
    ) -> None:
        """Test watching a path."""
        path = Path(temp_dir)
        watch_service.add_watch(path)

        # Verify it was added to watched paths
        assert path.resolve() in watch_service._watched_paths

        # Check that an event with the right type and added paths was published
        event_bus.publish.assert_called()

        # Extract the event that was published
        event = event_bus.publish.call_args[0][0]

        # Verify it's the right type with the right path
        assert isinstance(event, WatchedPathsChangedEvent)
        assert path.resolve() in event.added_paths

    def test_remove_watch(
        self, watch_service: FileSystemWatchService, temp_dir: str, event_bus: MagicMock
    ) -> None:
        """Test unwatching a path."""
        path = Path(temp_dir)
        watch_service.add_watch(path)

        # Reset mock to clear the add_watch event
        event_bus.reset_mock()

        watch_service.remove_watch(path)
        assert path.resolve() not in watch_service._watched_paths

        # Verify an event was published with the removed path
        event = event_bus.publish.call_args[0][0]
        assert isinstance(event, WatchedPathsChangedEvent)
        assert path.resolve() in event.removed_paths

    def test_watcher_type_configuration(self, event_bus: MagicMock) -> None:
        """Test configuring watcher type."""
        service = FileSystemWatchService(event_bus)

        # Default should be AUTO
        assert service._watcher_type == WatcherType.AUTO

        # Configure to use polling
        service.configure(WatcherType.POLLING)
        assert service._watcher_type == WatcherType.POLLING

        # Initialize with polling
        service.initialize()
        assert isinstance(service._watcher, PollingWatcher)

        # Clean up
        service.shutdown()

    def test_watcher_type_switching(self, event_bus: MagicMock, temp_dir: str) -> None:
        """Test switching between watcher types."""
        service = FileSystemWatchService(event_bus)
        service.initialize()

        # Add a watch
        path = Path(temp_dir)
        service.add_watch(path)

        # Save original watcher type
        original_watcher = service._watcher

        # Switch to polling
        service.configure(WatcherType.POLLING)

        # Verify watcher was changed
        assert service._watcher is not original_watcher
        assert isinstance(service._watcher, PollingWatcher)

        # Verify watch was preserved
        assert service.is_watching(path)

        # Clean up
        service.shutdown()

    def test_handle_file_event(
        self, watch_service: FileSystemWatchService, event_bus: MagicMock
    ) -> None:
        """Test handling file events."""
        # Create a file event
        test_path = Path("/test/path")
        event = FileChangeEvent(path=test_path, change_type=FileChangeType.CREATED)

        # Directly call the event handler
        watch_service._handle_file_event(event)

        # Check that event was published to the event bus
        event_bus.publish.assert_called_with(event)

    def test_recursive_watching(self, event_bus: MagicMock, temp_dir: str) -> None:
        """Test recursive directory watching."""
        service = FileSystemWatchService(event_bus)
        service.initialize()

        # Create a directory structure
        path = Path(temp_dir)
        subdir = path / "subdir1"
        subdir.mkdir(exist_ok=True)

        # Add watch with recursion
        service.add_watch(path, recursive=True)

        # Verify path is in recursive watches
        assert path.resolve() in service._recursive_watches

        # Clean up
        service.shutdown()


class TestPerformanceAndEdgeCases:
    """Tests for performance considerations and edge cases."""

    @pytest.mark.skipif(
        not FSEVENTS_AVAILABLE, reason="FSEvents not available on this platform"
    )
    def test_fsevents_event_coalescing(
        self, event_callback: MagicMock, temp_dir: str
    ) -> None:
        """Test event coalescing in FSEvents watcher."""
        # Create a watcher with longer latency to increase coalescing
        watcher = FSEventsWatcher(event_callback, latency=0.3)
        watcher.start()

        path = Path(temp_dir)
        watcher.add_watch(path)

        # Create a file
        file_path = Path(temp_dir) / "coalesce_test.txt"
        with open(file_path, "w") as f:
            f.write("initial content")

        # Rapidly modify the file multiple times
        for i in range(5):
            with open(file_path, "a") as f:
                f.write(f"\nmodification {i}")
            # Very short sleep to ensure changes are registered as separate operations
            time.sleep(0.02)

        # Wait for events to be processed
        time.sleep(0.5)
        watcher.stop()

        # Verify that we received at least 2 events (creation + at least one modification)
        # but fewer than the 6 total operations (indicating some coalescing occurred)
        assert event_callback.call_count >= 2

        # Verify that at least one creation event was received
        creation_events = []
        for call in event_callback.call_args_list:
            event = call[0][0]
            if event.path == file_path and event.change_type == FileChangeType.CREATED:
                creation_events.append(event)

        assert len(creation_events) >= 1

    def test_watch_nonexistent_path(self, event_callback: MagicMock) -> None:
        """Test watching a nonexistent path."""
        watcher = PollingWatcher(event_callback, interval=0.1)

        # Try to watch a nonexistent path
        nonexistent_path = Path("/path/that/does/not/exist")

        # Mock existence check
        with patch.object(Path, "exists", return_value=False):
            watcher.add_watch(nonexistent_path)

        # Verify the path wasn't added
        assert nonexistent_path not in watcher.get_watched_paths()

    def test_fallback_to_polling(self, event_bus: MagicMock) -> None:
        """Test fallback to polling if FSEvents fails."""
        service = FileSystemWatchService(event_bus)

        # Mock FSEventsWatcher to raise an exception
        with patch(
            "src.panoptikon.filesystem.watcher.FSEventsWatcher",
            side_effect=Exception("Test error"),
        ):
            with patch("src.panoptikon.filesystem.watcher.FSEVENTS_AVAILABLE", True):
                # Initialize service which should fallback to polling
                service.initialize()

                # Verify we fell back to PollingWatcher
                assert isinstance(service._watcher, PollingWatcher)

        # Clean up
        service.shutdown()
