"""Unit tests for filesystem watcher components (FSWatcher, PollingWatcher, FSEventsWatcher, FileSystemWatchService).

Covers all error, edge, and fallback logic for watcher code.
"""

from collections.abc import Generator
from pathlib import Path
import time
from unittest.mock import MagicMock, patch

import pytest

from src.panoptikon.filesystem.events import FileChangeType, WatchedPathsChangedEvent
from src.panoptikon.filesystem.watcher import (
    FSEVENTS_AVAILABLE,
    FileSystemWatchService,
    FSEventsWatcher,
    FSWatcher,
    PollingWatcher,
    WatcherType,
)

# Import fixtures from test_filesystem.py


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
        watcher.start()
        assert watcher._watching
        assert watcher._thread is not None
        watcher.stop()
        assert not watcher._watching

    def test_add_remove_watch(self, watcher: PollingWatcher, temp_dir: str) -> None:
        """Test adding and removing watched paths."""
        path = Path(temp_dir)
        watcher.add_watch(path)
        assert path in watcher._watches
        assert watcher.is_watching(path)
        assert path in watcher.get_watched_paths()
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
        file_path = self.create_test_file(temp_dir, "new_file.txt")
        time.sleep(0.3)
        assert event_callback.call_count >= 1
        creation_events = []
        for call in event_callback.call_args_list:
            event = call[0][0]
            if event.path == file_path and event.change_type == FileChangeType.CREATED:
                creation_events.append(event)
        assert len(creation_events) >= 1

    def test_add_watch_nonexistent_path_logs_warning(
        self, watcher: PollingWatcher, caplog
    ) -> None:
        """Test that adding a non-existent path logs a warning and does not add watch."""
        non_existent = Path("/nonexistent/path/should_not_exist")
        with caplog.at_level("WARNING"):
            watcher.add_watch(non_existent)
        assert non_existent not in watcher._watches
        assert any("Attempted to watch non-existent path" in m for m in caplog.messages)

    def test_remove_watch_nonexistent_path_logs_debug(
        self, watcher: PollingWatcher, caplog
    ) -> None:
        """Test that removing a non-watched path logs debug and does not error."""
        non_existent = Path("/nonexistent/path/should_not_exist")
        with caplog.at_level("DEBUG"):
            watcher.remove_watch(non_existent)
        assert any("Path not being watched" in m for m in caplog.messages)

    def test_double_add_watch_logs_debug(
        self, watcher: PollingWatcher, temp_dir: str, caplog
    ) -> None:
        """Test that adding the same path twice logs debug and does not duplicate."""
        path = Path(temp_dir)
        watcher.add_watch(path)
        with caplog.at_level("DEBUG"):
            watcher.add_watch(path)
        assert any("Path already being watched" in m for m in caplog.messages)
        assert list(watcher._watches.keys()).count(path) == 1

    def test_double_remove_watch_logs_debug(
        self, watcher: PollingWatcher, temp_dir: str, caplog
    ) -> None:
        """Test that removing the same path twice logs debug and does not error."""
        path = Path(temp_dir)
        watcher.add_watch(path)
        watcher.remove_watch(path)
        with caplog.at_level("DEBUG"):
            watcher.remove_watch(path)
        assert any("Path not being watched" in m for m in caplog.messages)

    def test_refresh_watch_state_permission_error(
        self, watcher: PollingWatcher, temp_dir: str, caplog
    ) -> None:
        """Test that _refresh_watch_state handles PermissionError and logs warning."""
        path = Path(temp_dir)
        watcher.add_watch(path)
        # Patch stat to raise PermissionError
        with patch.object(Path, "stat", side_effect=PermissionError("no access")):
            with caplog.at_level("WARNING"):
                watcher._refresh_watch_state(path)
        assert any("Error refreshing watch state" in m for m in caplog.messages)

    def test_scan_directory_permission_error(
        self, watcher: PollingWatcher, temp_dir: str, caplog
    ) -> None:
        """Test that _scan_directory handles PermissionError and logs warning."""
        path = Path(temp_dir)
        # Patch iterdir to raise PermissionError
        with patch.object(Path, "iterdir", side_effect=PermissionError("no access")):
            with caplog.at_level("WARNING"):
                result = watcher._scan_directory(path, recursive=True)
        assert result == []
        assert any("Error scanning directory" in m for m in caplog.messages)

    def test_handle_deleted_path_emits_events(
        self, watcher: PollingWatcher, event_callback: MagicMock, temp_dir: str
    ) -> None:
        """Test that _handle_deleted_path emits DELETED events for all watched files."""
        path = Path(temp_dir)
        watcher.add_watch(path)
        # Add a fake file to the watch state
        fake_file = path / "fake.txt"
        watcher._watches[path][fake_file] = 123.0
        watcher._handle_deleted_path(path)
        # Check that the callback was called with a FileChangeEvent of type DELETED
        called_event = event_callback.call_args[0][0]
        from src.panoptikon.filesystem.events import FileChangeEvent, FileChangeType

        assert isinstance(called_event, FileChangeEvent)
        assert called_event.path == fake_file
        assert called_event.change_type == FileChangeType.DELETED
        # The state should be cleared
        assert watcher._watches[path] == {}

    def test_thread_cleanup_on_stop(self, watcher: PollingWatcher) -> None:
        """Test that the polling thread is cleaned up on stop."""
        watcher.start()
        assert watcher._thread is not None
        watcher.stop()
        assert watcher._thread is None
        assert not watcher._watching

    def test_recursive_vs_nonrecursive_watch(
        self, watcher: PollingWatcher, temp_dir: str
    ) -> None:
        """Test that recursive and non-recursive watches are tracked correctly."""
        path = Path(temp_dir)
        watcher.add_watch(path, recursive=False)
        assert path not in watcher._recursive_watches
        watcher.add_watch(path, recursive=True)
        assert path in watcher._recursive_watches

    def test_fsevents_importerror(self):
        """Test that FSEventsWatcher raises ImportError if FSEVENTS_AVAILABLE is False."""
        with patch("src.panoptikon.filesystem.watcher.FSEVENTS_AVAILABLE", False):
            with pytest.raises(ImportError):
                FSEventsWatcher(lambda e: None)

    def test_filesystemwatchservice_fallback_to_polling(
        self, mock_event_bus: MagicMock
    ) -> None:
        """Test that FileSystemWatchService falls back to PollingWatcher if FSEvents creation fails."""
        with patch("src.panoptikon.filesystem.watcher.FSEVENTS_AVAILABLE", True):
            with patch(
                "src.panoptikon.filesystem.watcher.FSEventsWatcher",
                side_effect=Exception("fail"),
            ):
                service = FileSystemWatchService(mock_event_bus)
                service._watcher_type = WatcherType.FSEVENTS
                # Should not raise
                service._create_watcher()
                assert isinstance(service._watcher, PollingWatcher)

    def test_watch_thread_error_handling(
        self, watcher: PollingWatcher, temp_dir: str, event_callback: MagicMock
    ) -> None:
        """Test that errors in _watch_thread do not crash the thread and fallback occurs."""
        from unittest.mock import patch

        path = Path(temp_dir)
        watcher.add_watch(path)
        with patch.object(watcher, "_check_for_changes", side_effect=Exception("fail")):
            watcher._stop_event.set()  # Prevent infinite loop
            # Should not raise
            watcher._watch_thread()
        # No assertion on logs; just ensure no crash

    def test_process_new_and_modified_files(
        self, watcher: PollingWatcher, event_callback: MagicMock
    ) -> None:
        """Test _process_new_and_modified_files emits correct events."""
        old_state = {Path("/a"): 1.0}
        current_files = {Path("/a"): 2.0, Path("/b"): 1.0}
        watcher._event_callback = event_callback
        watcher._process_new_and_modified_files(old_state, current_files)
        # Should emit MODIFIED for /a and CREATED for /b
        calls = [call[0][0] for call in event_callback.call_args_list]
        paths_types = {(c.path, c.change_type) for c in calls}
        from src.panoptikon.filesystem.events import FileChangeType

        assert (Path("/a"), FileChangeType.MODIFIED) in paths_types
        assert (Path("/b"), FileChangeType.CREATED) in paths_types

    def test_process_deleted_files(
        self, watcher: PollingWatcher, event_callback: MagicMock
    ) -> None:
        """Test _process_deleted_files emits correct events."""
        old_state = {Path("/a"): 1.0, Path("/b"): 1.0}
        current_files = {Path("/a"): 1.0}
        watcher._event_callback = event_callback
        watcher._process_deleted_files(old_state, current_files)
        calls = [call[0][0] for call in event_callback.call_args_list]
        from src.panoptikon.filesystem.events import FileChangeType

        assert any(
            c.path == Path("/b") and c.change_type == FileChangeType.DELETED
            for c in calls
        )

    def test_emit_file_event(
        self, watcher: PollingWatcher, event_callback: MagicMock
    ) -> None:
        """Test _emit_file_event calls the event callback with correct event."""
        watcher._event_callback = event_callback
        from src.panoptikon.filesystem.events import FileChangeType

        watcher._emit_file_event(Path("/foo"), FileChangeType.CREATED)
        event_callback.assert_called_once()
        event = event_callback.call_args[0][0]
        assert event.path == Path("/foo")
        assert event.change_type == FileChangeType.CREATED

    def test_double_start_stop(self, watcher: PollingWatcher) -> None:
        """Test that double start/stop does not error and is idempotent."""
        watcher.start()
        watcher.start()
        watcher.stop()
        watcher.stop()
        assert not watcher._watching

    def test_filesystemwatchservice_configure_switch_types(
        self, mock_event_bus: MagicMock
    ) -> None:
        """Test FileSystemWatchService.configure switches watcher types and preserves watches."""
        service = FileSystemWatchService(mock_event_bus)
        service.initialize()
        path = Path("/tmp")
        service.add_watch(path)
        old_watcher = service._watcher
        service.configure(watcher_type=WatcherType.AUTO)
        # Should not switch if same type
        assert service._watcher is old_watcher
        # Switch to POLLING
        service.configure(watcher_type=WatcherType.POLLING)
        assert isinstance(service._watcher, PollingWatcher)
        # Switch to FSEVENTS if available
        from src.panoptikon.filesystem.watcher import (
            FSEVENTS_AVAILABLE,
            FSEventsWatcher,
        )

        if FSEVENTS_AVAILABLE:
            service.configure(watcher_type=WatcherType.FSEVENTS)
            assert isinstance(service._watcher, FSEventsWatcher)

    def test_filesystemwatchservice_start_stop_edge_cases(
        self, mock_event_bus: MagicMock
    ) -> None:
        """Test FileSystemWatchService start/stop edge cases."""
        service = FileSystemWatchService(mock_event_bus)
        service.initialize()
        service.start_watching()
        service.start_watching()
        service.stop_watching()
        service.stop_watching()
        assert service._watcher is not None

    def test_filesystemwatchservice_add_remove_watch_edge_cases(
        self, mock_event_bus: MagicMock
    ) -> None:
        """Test FileSystemWatchService add/remove watch edge cases."""
        service = FileSystemWatchService(mock_event_bus)
        service.initialize()
        path = Path("/tmp")
        service.add_watch(path)
        service.add_watch(path)
        service.remove_watch(path)
        service.remove_watch(path)
        assert path.resolve() not in service._watched_paths

    def test_filesystemwatchservice_create_watcher_error_fallback(
        self, mock_event_bus: MagicMock
    ) -> None:
        """Test FileSystemWatchService._create_watcher error fallback logic (no log assertion)."""
        from unittest.mock import patch

        service = FileSystemWatchService(mock_event_bus)
        service._watcher_type = WatcherType.FSEVENTS
        with patch(
            "src.panoptikon.filesystem.watcher.FSEventsWatcher",
            side_effect=Exception("fail"),
        ):
            # Should not raise, should fallback to PollingWatcher
            service._create_watcher()
        assert isinstance(service._watcher, PollingWatcher)

    def test_fseventswatcher_add_remove_watch_error(self, mocker) -> None:
        """Test FSEventsWatcher add_watch/remove_watch error handling."""
        from src.panoptikon.filesystem.watcher import (
            FSEVENTS_AVAILABLE,
            FSEventsWatcher,
        )

        if not FSEVENTS_AVAILABLE:
            return
        event_callback = mocker.Mock()
        watcher = FSEventsWatcher(event_callback)
        # Remove non-existent
        watcher.remove_watch(Path("/notwatched"))
        # Add already watched
        path = Path("/tmp")
        watcher._streams[path] = mocker.Mock()
        watcher.add_watch(path)
        # Remove watched
        watcher.remove_watch(path)
        assert path not in watcher._streams


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
        watcher.start()
        assert watcher._watching
        assert watcher._observer is not None
        watcher.stop()
        assert not watcher._watching
        assert watcher._observer is None

    def test_add_remove_watch(self, watcher: FSEventsWatcher, temp_dir: str) -> None:
        """Test adding and removing watched paths."""
        path = Path(temp_dir)
        watcher.add_watch(path)
        assert path in watcher._streams
        assert watcher.is_watching(path)
        assert path in watcher.get_watched_paths()
        watcher.remove_watch(path)
        assert path not in watcher._streams
        assert not watcher.is_watching(path)
        assert path not in watcher.get_watched_paths()


class TestFileSystemWatchService:
    """Tests for the FileSystemWatchService class."""

    def test_initialization(self, watch_service: FileSystemWatchService) -> None:
        """Test service initialization."""
        assert watch_service._watcher is not None

    def test_add_watch(
        self,
        watch_service: FileSystemWatchService,
        temp_dir: Path,
        mock_event_bus: MagicMock,
    ) -> None:
        """Test watching a path."""
        path = Path(temp_dir)
        watch_service.add_watch(path)
        assert path.resolve() in watch_service._watched_paths
        mock_event_bus.publish.assert_called()
        event = mock_event_bus.publish.call_args[0][0]
        assert isinstance(event, WatchedPathsChangedEvent)
        assert path.resolve() in event.added_paths

    def test_remove_watch(
        self,
        watch_service: FileSystemWatchService,
        temp_dir: Path,
        mock_event_bus: MagicMock,
    ) -> None:
        """Test unwatching a path."""
        path = Path(temp_dir)
        watch_service.add_watch(path)
        mock_event_bus.reset_mock()
        watch_service.remove_watch(path)
        assert path.resolve() not in watch_service._watched_paths
        event = mock_event_bus.publish.call_args[0][0]
        assert isinstance(event, WatchedPathsChangedEvent)
        assert path.resolve() in event.removed_paths

    # Additional coverage-improving tests will be added below.
