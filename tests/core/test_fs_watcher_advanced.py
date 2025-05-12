"""Advanced tests for filesystem watcher module.

These tests focus on improving coverage for the filesystem watcher module
by covering edge cases and error conditions.
"""

from pathlib import Path
import time
from typing import Dict, Set
from unittest.mock import MagicMock, patch

import pytest

from panoptikon.filesystem.events import (
    FileChangeEvent,
    FileChangeType,
    WatchedPathsChangedEvent,
)
from panoptikon.filesystem.watcher import (
    FSEVENTS_AVAILABLE,
    FileSystemWatchService,
    FSEventsWatcher,
    FSWatcher,
    PollingWatcher,
    WatcherType,
)


class TestFSWatcherAbstract:
    """Test the abstract base class FSWatcher."""

    def test_abstract_methods(self) -> None:
        """Test that FSWatcher is an abstract class."""
        with pytest.raises(TypeError):
            FSWatcher()  # type: ignore


class TestFSEventsWatcherAdvanced:
    """Advanced tests for FSEventsWatcher."""

    @pytest.mark.skipif(not FSEVENTS_AVAILABLE, reason="FSEvents not available")
    def test_handle_event_flags(self, tmp_path: Path) -> None:
        """Test FSEventsWatcher event flag handling."""
        callback = MagicMock()
        watcher = FSEventsWatcher(callback)

        # Mock the stream creation and directly call the event handler
        with patch("fsevents.Stream") as mock_stream:
            # Add a watch to get a stream object created
            watcher.add_watch(tmp_path)

            # Get the event handler function from the last call
            stream_constructor = mock_stream.call_args[0][0]

            # Test created event
            stream_constructor(str(tmp_path / "file.txt"), 0x00000100)
            callback.assert_called_with(
                FileChangeEvent(
                    path=Path(str(tmp_path / "file.txt")),
                    change_type=FileChangeType.CREATED,
                )
            )
            callback.reset_mock()

            # Test deleted event
            stream_constructor(str(tmp_path / "file.txt"), 0x00001000)
            callback.assert_called_with(
                FileChangeEvent(
                    path=Path(str(tmp_path / "file.txt")),
                    change_type=FileChangeType.DELETED,
                )
            )
            callback.reset_mock()

            # Test modified event
            stream_constructor(str(tmp_path / "file.txt"), 0x00000200)
            callback.assert_called_with(
                FileChangeEvent(
                    path=Path(str(tmp_path / "file.txt")),
                    change_type=FileChangeType.MODIFIED,
                )
            )
            callback.reset_mock()

            # Test renamed event
            stream_constructor(str(tmp_path / "file.txt"), 0x00000800)
            callback.assert_called_with(
                FileChangeEvent(
                    path=Path(str(tmp_path / "file.txt")),
                    change_type=FileChangeType.RENAMED,
                )
            )
            callback.reset_mock()

            # Test attribute modified event
            stream_constructor(str(tmp_path / "file.txt"), 0x00000400)
            callback.assert_called_with(
                FileChangeEvent(
                    path=Path(str(tmp_path / "file.txt")),
                    change_type=FileChangeType.ATTRIBUTE_MODIFIED,
                )
            )
            callback.reset_mock()

            # Test unknown event
            stream_constructor(str(tmp_path / "file.txt"), 0x00010000)
            callback.assert_called_with(
                FileChangeEvent(
                    path=Path(str(tmp_path / "file.txt")),
                    change_type=FileChangeType.UNKNOWN,
                )
            )


class TestPollingWatcherAdvanced:
    """Advanced tests for PollingWatcher."""

    def test_complex_directory_structure(self, tmp_path: Path) -> None:
        """Test watching a complex directory structure."""
        callback = MagicMock()
        watcher = PollingWatcher(callback, interval=0.1)

        # Create a complex directory structure
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir1" / "subdir1").mkdir()
        (tmp_path / "dir1" / "subdir1" / "file1.txt").write_text("content")
        (tmp_path / "dir1" / "file2.txt").write_text("content")
        (tmp_path / "file3.txt").write_text("content")

        # Add watch and do polling cycle
        watcher.add_watch(tmp_path, recursive=True)

        # Verify initial state
        assert len(watcher._watches[tmp_path]) >= 5  # Directory, 2 subdirs, 2 files

        # Modify a file
        (tmp_path / "dir1" / "subdir1" / "file1.txt").write_text("new content")

        # Directly call check for changes
        watcher._check_for_changes(tmp_path)

        # Verify the event was generated
        assert callback.call_count >= 1

        # Find the modified file event
        file_modified = False
        for call in callback.call_args_list:
            event = call[0][0]
            if (
                event.path == (tmp_path / "dir1" / "subdir1" / "file1.txt")
                and event.change_type == FileChangeType.MODIFIED
            ):
                file_modified = True
                break

        assert file_modified

    def test_watch_thread_exception_handling(self, tmp_path: Path) -> None:
        """Test that exceptions in the watch thread are handled."""
        callback = MagicMock()
        watcher = PollingWatcher(callback, interval=0.1)

        # Add watch
        watcher.add_watch(tmp_path)

        # Mock check_for_changes to raise an exception
        with patch.object(
            watcher, "_check_for_changes", side_effect=Exception("Test error")
        ):
            # Start watching
            watcher.start()

            # Let the thread run for a short time
            time.sleep(0.2)

            # Stop watching
            watcher.stop()

        # The test passes if no exception was raised from the thread


class TestFileSystemWatchServiceAdvanced:
    """Advanced tests for FileSystemWatchService."""

    def test_fallback_watcher_creation(self) -> None:
        """Test that service falls back to polling watcher if FSEvents fails."""
        event_bus = MagicMock()
        service = FileSystemWatchService(event_bus)

        # Mock FSEventsWatcher to raise an exception
        with patch(
            "panoptikon.filesystem.watcher.FSEventsWatcher",
            side_effect=Exception("Test error"),
        ):
            with patch("panoptikon.filesystem.watcher.FSEVENTS_AVAILABLE", True):
                # Force recreation of watcher
                service._create_watcher()

                # Verify we fell back to PollingWatcher
                assert isinstance(service._watcher, PollingWatcher)

    def test_switching_watcher_types(self, tmp_path: Path) -> None:
        """Test switching between watcher types."""
        # Create the directories first
        if not tmp_path.exists():
            tmp_path.mkdir(parents=True)

        event_bus = MagicMock()
        service = FileSystemWatchService(event_bus)
        service.initialize()

        # Mock the watcher's add_watch method to avoid path existence checks
        with patch.object(PollingWatcher, "add_watch") as mock_add_watch:
            # Add a watch
            service.add_watch(tmp_path)

            # Get original watcher
            original_watcher = service._watcher

            # Configure to use different watcher type
            service.configure(WatcherType.POLLING)

            # Verify watcher was changed
            assert service._watcher is not original_watcher
            assert isinstance(service._watcher, PollingWatcher)

            # Verify add_watch was called for the new watcher
            mock_add_watch.assert_called_with(tmp_path.resolve(), True)

    def test_multiple_watches_and_removal(self, tmp_path: Path) -> None:
        """Test adding and removing multiple watches."""
        # Create directory structure
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir(parents=True, exist_ok=True)
        dir2.mkdir(parents=True, exist_ok=True)

        event_bus = MagicMock()
        service = FileSystemWatchService(event_bus)
        service.initialize()

        # Mock the watcher methods to avoid path existence checks
        with (
            patch.object(PollingWatcher, "add_watch") as mock_add_watch,
            patch.object(PollingWatcher, "is_watching") as mock_is_watching,
            patch.object(PollingWatcher, "remove_watch") as mock_remove_watch,
        ):
            # Setup the mock to return True for is_watching
            mock_is_watching.return_value = True

            # Add watches
            service.add_watch(dir1)
            service.add_watch(dir2)

            # Verify watches were added
            assert mock_add_watch.call_count == 2

            # Check event published
            event_bus.publish.assert_called()

            # Find WatchedPathsChangedEvent calls
            events = [
                call[0][0]
                for call in event_bus.publish.call_args_list
                if isinstance(call[0][0], WatchedPathsChangedEvent)
            ]
            assert len(events) == 2

            # Reset mock
            event_bus.reset_mock()

            # Remove a watch
            service.remove_watch(dir1)

            # Verify remove_watch was called
            mock_remove_watch.assert_called_once_with(dir1.resolve())

            # Check event published
            event_bus.publish.assert_called_once()
            assert isinstance(
                event_bus.publish.call_args[0][0], WatchedPathsChangedEvent
            )
            event = event_bus.publish.call_args[0][0]
            assert dir1.resolve() in event.removed_paths

    def test_get_watched_paths(self, tmp_path: Path) -> None:
        """Test getting all watched paths."""
        event_bus = MagicMock()
        service = FileSystemWatchService(event_bus)

        # No watcher should return empty set
        service._watcher = None
        assert service.get_watched_paths() == set()

        # Create watcher and add watches
        service._create_watcher()

        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir(parents=True, exist_ok=True)
        dir2.mkdir(parents=True, exist_ok=True)

        # Mock the watcher to return specific watched paths
        mock_watcher = MagicMock()
        mock_watcher.get_watched_paths.return_value = {dir1.resolve(), dir2.resolve()}
        service._watcher = mock_watcher

        # Get watched paths
        watched = service.get_watched_paths()

        # Verify
        assert len(watched) == 2
        assert dir1.resolve() in watched
        assert dir2.resolve() in watched


class MockFSWatcher(FSWatcher):
    """Mock implementation of FSWatcher for testing."""

    def __init__(self) -> None:
        """Initialize the mock watcher."""
        self.started = False
        self.watches: Dict[Path, bool] = {}  # Path -> recursive

    def start(self) -> None:
        """Start watching for filesystem changes."""
        self.started = True

    def stop(self) -> None:
        """Stop watching for filesystem changes."""
        self.started = False

    def add_watch(self, path: Path, recursive: bool = True) -> None:
        """Add a path to the watch list."""
        self.watches[path.resolve()] = recursive

    def remove_watch(self, path: Path) -> None:
        """Remove a path from the watch list."""
        if path.resolve() in self.watches:
            del self.watches[path.resolve()]

    def is_watching(self, path: Path) -> bool:
        """Check if a path is being watched."""
        return path.resolve() in self.watches

    def get_watched_paths(self) -> Set[Path]:
        """Get the set of paths currently being watched."""
        return set(self.watches.keys())


class TestFileSystemWatchServiceWithMockWatcher:
    """Test FileSystemWatchService with a controllable mock watcher."""

    def test_service_with_custom_watcher(self, tmp_path: Path) -> None:
        """Test service using a custom watcher implementation."""
        event_bus = MagicMock()
        service = FileSystemWatchService(event_bus)

        # Replace watcher with our mock
        mock_watcher = MockFSWatcher()
        service._watcher = mock_watcher

        # Test operations
        service.start_watching()
        assert mock_watcher.started

        service.add_watch(tmp_path)
        assert tmp_path.resolve() in mock_watcher.watches

        assert service.is_watching(tmp_path)

        service.remove_watch(tmp_path)
        assert tmp_path.resolve() not in mock_watcher.watches

        service.stop_watching()
        assert not mock_watcher.started
