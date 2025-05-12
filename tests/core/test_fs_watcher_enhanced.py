"""Enhanced tests for the filesystem watcher module."""

from collections.abc import Generator
from pathlib import Path
import tempfile
import time
from unittest.mock import MagicMock, patch

import pytest

from src.panoptikon.core.events import EventBus
from src.panoptikon.filesystem.events import FileChangeType
from src.panoptikon.filesystem.watcher import (
    FSEVENTS_AVAILABLE,
    FileSystemWatchService,
    FSEventsWatcher,
    PollingWatcher,
    WatcherType,
)


class TestEventCoalescing:
    """Tests for event coalescing behavior."""

    @pytest.fixture
    def event_callback(self) -> MagicMock:
        """Create a mock event callback."""
        return MagicMock()

    @pytest.fixture
    def temp_dir(self) -> Generator[str, None, None]:
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield tmp_dir

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
        assert event_callback.call_count < 6

        # Verify that at least one creation event was received
        creation_events = []
        for call in event_callback.call_args_list:
            event = call[0][0]
            if event.path == file_path and event.change_type == FileChangeType.CREATED:
                creation_events.append(event)

        assert len(creation_events) >= 1

    def test_polling_watcher_event_coalescing(
        self, event_callback: MagicMock, temp_dir: str
    ) -> None:
        """Test event coalescing in Polling watcher."""
        # Create a watcher with appropriate interval for testing
        watcher = PollingWatcher(event_callback, interval=0.2)
        watcher.start()

        path = Path(temp_dir)
        watcher.add_watch(path)

        # Create a file
        file_path = Path(temp_dir) / "coalesce_test.txt"
        with open(file_path, "w") as f:
            f.write("initial content")

        # Wait for first poll to complete
        time.sleep(0.3)

        # Reset the callback to ignore creation events
        event_callback.reset_mock()

        # Perform multiple modifications during a single polling interval
        for i in range(5):
            with open(file_path, "a") as f:
                f.write(f"\nmodification {i}")

        # Wait for next poll to complete
        time.sleep(0.3)
        watcher.stop()

        # Verify that we received only one modification event (coalesced)
        assert event_callback.call_count >= 1

        modification_events = []
        for call in event_callback.call_args_list:
            event = call[0][0]
            if event.path == file_path and event.change_type == FileChangeType.MODIFIED:
                modification_events.append(event)

        # There should be exactly one modification event
        assert len(modification_events) == 1


class TestFileOperations:
    """Tests for different file operations."""

    @pytest.fixture
    def event_callback(self) -> MagicMock:
        """Create a mock event callback."""
        return MagicMock()

    @pytest.fixture
    def temp_dir(self) -> Generator[str, None, None]:
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield tmp_dir

    def test_polling_watcher_complex_operations(
        self, event_callback: MagicMock, temp_dir: str
    ) -> None:
        """Test complex file operations with polling watcher."""
        watcher = PollingWatcher(event_callback, interval=0.1)
        watcher.start()

        path = Path(temp_dir)
        watcher.add_watch(path)

        # Create a subdirectory
        subdir = path / "subdir"
        subdir.mkdir()

        # Wait for creation event
        time.sleep(0.2)
        event_callback.reset_mock()

        # Create a file in the subdirectory
        file_path = subdir / "test_file.txt"
        with open(file_path, "w") as f:
            f.write("test content")

        # Wait for creation event
        time.sleep(0.2)
        event_callback.reset_mock()

        # Rename the file
        new_file_path = subdir / "renamed_file.txt"
        file_path.rename(new_file_path)

        # Wait for events to be processed
        time.sleep(0.2)
        watcher.stop()

        # Verify we got deletion and creation events (rename is detected as delete+create)
        delete_events = []
        create_events = []
        for call in event_callback.call_args_list:
            event = call[0][0]
            if event.change_type == FileChangeType.DELETED and event.path == file_path:
                delete_events.append(event)
            elif (
                event.change_type == FileChangeType.CREATED
                and event.path == new_file_path
            ):
                create_events.append(event)

        assert len(delete_events) == 1
        assert len(create_events) == 1

    @pytest.mark.skipif(
        not FSEVENTS_AVAILABLE, reason="FSEvents not available on this platform"
    )
    def test_fsevents_rename_operations(
        self, event_callback: MagicMock, temp_dir: str
    ) -> None:
        """Test file rename operations with FSEvents watcher."""
        watcher = FSEventsWatcher(event_callback, latency=0.1)
        watcher.start()

        path = Path(temp_dir)
        watcher.add_watch(path)

        # Create a file
        file_path = path / "original.txt"
        with open(file_path, "w") as f:
            f.write("test content")

        # Wait for creation event
        time.sleep(0.2)
        event_callback.reset_mock()

        # Rename the file
        new_file_path = path / "renamed.txt"
        file_path.rename(new_file_path)

        # Wait for rename events to be processed
        time.sleep(0.2)
        watcher.stop()

        # Check if any rename events were emitted
        # FSEvents will either emit RENAMED, or a combination of DELETED and CREATED
        rename_events = []
        delete_events = []
        create_events = []

        for call in event_callback.call_args_list:
            event = call[0][0]
            if event.change_type == FileChangeType.RENAMED:
                rename_events.append(event)
            elif (
                event.change_type == FileChangeType.DELETED and event.path == file_path
            ):
                delete_events.append(event)
            elif (
                event.change_type == FileChangeType.CREATED
                and event.path == new_file_path
            ):
                create_events.append(event)

        # We should have either rename events or delete+create events
        assert len(rename_events) > 0 or (
            len(delete_events) > 0 and len(create_events) > 0
        )


class TestErrorHandling:
    """Tests for error handling in filesystem watchers."""

    @pytest.fixture
    def event_callback(self) -> MagicMock:
        """Create a mock event callback."""
        return MagicMock()

    @pytest.fixture
    def temp_dir(self) -> Generator[str, None, None]:
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield tmp_dir

    def test_polling_watch_nonexistent_path(self, event_callback: MagicMock) -> None:
        """Test watching a nonexistent path with polling watcher."""
        watcher = PollingWatcher(event_callback, interval=0.1)

        # Try to watch a nonexistent path
        nonexistent_path = Path("/path/that/does/not/exist")
        watcher.add_watch(nonexistent_path)

        # Verify the path wasn't added
        assert not watcher.is_watching(nonexistent_path)
        assert nonexistent_path not in watcher.get_watched_paths()

    @pytest.mark.skipif(
        not FSEVENTS_AVAILABLE, reason="FSEvents not available on this platform"
    )
    def test_fsevents_watch_nonexistent_path(self, event_callback: MagicMock) -> None:
        """Test watching a nonexistent path with FSEvents watcher."""
        watcher = FSEventsWatcher(event_callback, latency=0.1)

        # Try to watch a nonexistent path
        nonexistent_path = Path("/path/that/does/not/exist")
        watcher.add_watch(nonexistent_path)

        # Verify the path wasn't added
        assert not watcher.is_watching(nonexistent_path)
        assert nonexistent_path not in watcher.get_watched_paths()

    def test_polling_watch_deleted_path(
        self, event_callback: MagicMock, temp_dir: str
    ) -> None:
        """Test behavior when a watched path is deleted."""
        watcher = PollingWatcher(event_callback, interval=0.1)
        watcher.start()

        path = Path(temp_dir)
        subdir = path / "dir_to_delete"
        subdir.mkdir()

        # Create a file in the subdirectory
        file_path = subdir / "test_file.txt"
        with open(file_path, "w") as f:
            f.write("test content")

        # Watch the subdirectory
        watcher.add_watch(subdir)

        # Wait for initial scan
        time.sleep(0.2)
        event_callback.reset_mock()

        # Delete the entire directory
        file_path.unlink()  # Delete the file first
        subdir.rmdir()  # Then delete the directory

        # Wait for deletion events
        time.sleep(0.2)
        watcher.stop()

        # Verify deletion events were emitted
        deletion_events = []
        for call in event_callback.call_args_list:
            event = call[0][0]
            if event.change_type == FileChangeType.DELETED:
                deletion_events.append(event)

        # We should have at least one deletion event (for the directory)
        # Note: Some implementations might not emit separate events for each file
        assert len(deletion_events) >= 1


class TestWatcherConfigurationAndRecursion:
    """Tests for watcher configuration and recursive watching."""

    @pytest.fixture
    def event_bus(self) -> MagicMock:
        """Create a mock event bus."""
        return MagicMock(spec=EventBus)

    def test_service_watcher_type_switching(self, event_bus: MagicMock) -> None:
        """Test switching between watcher types."""
        service = FileSystemWatchService(event_bus)
        service.initialize()

        # Default should be AUTO, which results in either FSEvents or Polling
        if FSEVENTS_AVAILABLE:
            assert isinstance(service._watcher, FSEventsWatcher)
        else:
            assert isinstance(service._watcher, PollingWatcher)

        # Switch to explicitly request polling
        service.configure(WatcherType.POLLING)
        assert isinstance(service._watcher, PollingWatcher)

        # If FSEvents is available, switch to that
        if FSEVENTS_AVAILABLE:
            service.configure(WatcherType.FSEVENTS)
            assert isinstance(service._watcher, FSEventsWatcher)

        # Cleanup
        service.shutdown()

    def test_recursive_watching(self, event_bus: MagicMock) -> None:
        """Test recursive directory watching."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            service = FileSystemWatchService(event_bus)
            service.initialize()

            # Create a directory structure
            path = Path(tmp_dir)
            subdir1 = path / "subdir1"
            subdir1.mkdir()
            subdir2 = subdir1 / "subdir2"
            subdir2.mkdir()

            # Add watch with recursion
            service.add_watch(path, recursive=True)

            # Verify path is in recursive watches
            assert path.resolve() in service._recursive_watches

            # Clean up
            service.shutdown()

    def test_non_recursive_watching(self, event_bus: MagicMock) -> None:
        """Test non-recursive directory watching."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            service = FileSystemWatchService(event_bus)
            service.initialize()

            # Create a directory structure
            path = Path(tmp_dir)
            subdir1 = path / "subdir1"
            subdir1.mkdir()

            # Add watch without recursion
            service.add_watch(path, recursive=False)

            # Verify path is not in recursive watches
            assert path.resolve() not in service._recursive_watches

            # Clean up
            service.shutdown()


class TestFSWatcherIntegration:
    """Integration tests for filesystem watchers."""

    @pytest.fixture
    def event_bus(self) -> MagicMock:
        """Create a mock event bus."""
        return MagicMock(spec=EventBus)

    def test_service_watches_during_type_switch(self, event_bus: MagicMock) -> None:
        """Test that watched paths remain after switching watcher type."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            service = FileSystemWatchService(event_bus)
            service.initialize()

            # Add some watches
            path1 = Path(tmp_dir)
            path2 = path1 / "subdir"
            path2.mkdir()

            service.add_watch(path1)
            service.add_watch(path2)

            # Switch watcher type
            if FSEVENTS_AVAILABLE:
                # If using FSEvents, switch to polling
                service.configure(WatcherType.POLLING)
            else:
                # If using polling, switch to another instance of polling
                service.configure(WatcherType.POLLING)

            # Verify watches are preserved
            assert service.is_watching(path1)
            assert service.is_watching(path2)

            # Clean up
            service.shutdown()

    @pytest.mark.skipif(
        not FSEVENTS_AVAILABLE, reason="FSEvents not available on this platform"
    )
    def test_fsevents_fallback_on_error(self, event_bus: MagicMock) -> None:
        """Test fallback to polling if FSEvents fails."""
        with patch(
            "src.panoptikon.filesystem.watcher.FSEventsWatcher",
            side_effect=Exception("Simulated error"),
        ):
            service = FileSystemWatchService(event_bus)
            service.configure(WatcherType.FSEVENTS)
            service.initialize()

            # Should fallback to PollingWatcher
            assert isinstance(service._watcher, PollingWatcher)

            # Clean up
            service.shutdown()

    def test_large_directory_watching(self, event_bus: MagicMock) -> None:
        """Test watching a directory with many files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            service = FileSystemWatchService(event_bus)
            service.initialize()

            # Create a large number of files
            path = Path(tmp_dir)
            file_count = 100  # Not too large to keep the test fast

            for i in range(file_count):
                with open(path / f"file_{i}.txt", "w") as f:
                    f.write(f"Content for file {i}")

            # Add watch
            service.add_watch(path)

            # Verify service starts correctly
            service.start_watching()
            time.sleep(0.5)  # Give it time to process

            # Stop and clean up
            service.stop_watching()
            service.shutdown()

            # Should have no errors
            assert service._watcher is None
