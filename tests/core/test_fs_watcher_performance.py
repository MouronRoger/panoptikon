"""Test suite for filesystem watcher performance and specific edge cases.

This module contains tests to improve coverage of filesystem watcher code,
focusing on methods that aren't fully covered by the main test suite.
"""

from pathlib import Path
import time
from unittest.mock import MagicMock, patch

import pytest

from src.panoptikon.filesystem.events import FileChangeEvent, FileChangeType
from src.panoptikon.filesystem.watcher import (
    FileSystemWatchService,
    PollingWatcher,
    WatcherType,
)


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def polling_watcher():
    """Create a polling watcher with a mock callback."""
    callback = MagicMock()
    watcher = PollingWatcher(callback, interval=0.1)
    yield watcher, callback
    watcher.stop()


class TestPollingWatcherPerformance:
    """Tests for polling watcher performance and edge cases."""

    def test_polling_watcher_full_cycle(self, polling_watcher, temp_dir):
        """Test full cycle of adding/checking/removing a watch."""
        watcher, callback = polling_watcher

        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("initial content")

        # Add watch and start
        watcher.add_watch(temp_dir)
        watcher.start()

        # Wait a bit for initial scan
        time.sleep(0.3)

        # Clear any initialization events
        callback.reset_mock()

        # Modify the file
        test_file.write_text("modified content")

        # Wait for polling cycle
        time.sleep(0.3)

        # Check for events (should be at least one MODIFIED event)
        assert callback.call_count > 0
        has_modified = False
        for call in callback.call_args_list:
            event = call[0][0]
            if event.path == test_file and event.change_type == FileChangeType.MODIFIED:
                has_modified = True
        assert has_modified, "No modification event detected"

        # Stop watching
        watcher.stop()

    def test_handle_deleted_path(self, polling_watcher, temp_dir):
        """Test handling of a watched path that gets deleted."""
        watcher, callback = polling_watcher

        # Create a subdirectory with files
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        test_file = subdir / "test.txt"
        test_file.write_text("test content")

        # Start watching the subdirectory
        watcher.add_watch(subdir)
        watcher.start()

        # Wait for initial scan
        time.sleep(0.3)
        callback.reset_mock()

        # Delete the directory
        test_file.unlink()  # Delete the file first
        subdir.rmdir()  # Then the directory

        # Wait for polling cycle
        time.sleep(0.3)

        # Check if deletion events were generated
        assert callback.call_count > 0
        deleted_events = [
            call[0][0]
            for call in callback.call_args_list
            if call[0][0].change_type == FileChangeType.DELETED
        ]
        assert len(deleted_events) > 0, "No deletion events detected"

    def test_scan_directory_permission_error(self, polling_watcher, temp_dir):
        """Test directory scanning with permission errors."""
        watcher, callback = polling_watcher

        # Setup mocks to simulate permission errors during directory scanning
        with patch("pathlib.Path.iterdir") as mock_iterdir:
            mock_iterdir.side_effect = PermissionError("Permission denied")

            # Add watch and trigger scan
            watcher._scan_directory(temp_dir, True)

            # Verify the error was handled
            mock_iterdir.assert_called_once()
            # No exception should be raised

    def test_process_new_and_modified_files(self, polling_watcher):
        """Test processing of new and modified files."""
        watcher, callback = polling_watcher

        # Create test data
        old_state = {
            Path("/test/file1.txt"): 1000.0,
            Path("/test/file2.txt"): 2000.0,
        }

        current_files = {
            Path("/test/file1.txt"): 1000.0,  # Unchanged
            Path("/test/file2.txt"): 2000.1,  # Modified
            Path("/test/file3.txt"): 3000.0,  # New
        }

        # Process the changes
        watcher._process_new_and_modified_files(old_state, current_files)

        # Check events
        assert callback.call_count == 2  # One modified, one created

        events = [call[0][0] for call in callback.call_args_list]
        change_types = {(event.path, event.change_type) for event in events}

        assert (Path("/test/file2.txt"), FileChangeType.MODIFIED) in change_types
        assert (Path("/test/file3.txt"), FileChangeType.CREATED) in change_types

    def test_process_deleted_files(self, polling_watcher):
        """Test processing of deleted files."""
        watcher, callback = polling_watcher

        # Create test data
        old_state = {
            Path("/test/file1.txt"): 1000.0,
            Path("/test/file2.txt"): 2000.0,
            Path("/test/file3.txt"): 3000.0,
        }

        current_files = {
            Path("/test/file1.txt"): 1000.0,  # Still exists
            Path("/test/file3.txt"): 3000.0,  # Still exists
        }

        # Process the deletes
        watcher._process_deleted_files(old_state, current_files)

        # Check events
        assert callback.call_count == 1  # One deleted

        event = callback.call_args[0][0]
        assert event.path == Path("/test/file2.txt")
        assert event.change_type == FileChangeType.DELETED


class TestFileSystemWatchServiceCoverage:
    """Tests to improve coverage of the FileSystemWatchService class."""

    def test_service_configuration(self):
        """Test service configuration changes and watcher switching."""
        event_bus = MagicMock()
        service = FileSystemWatchService(event_bus)

        # Initialize with default (AUTO) configuration
        service.initialize()
        assert service._watcher is not None
        original_watcher = service._watcher

        # Change to explicit POLLING type
        service.configure(WatcherType.POLLING)

        # Verify watcher was changed
        assert service._watcher is not None
        assert service._watcher is not original_watcher
        assert service._watcher_type == WatcherType.POLLING

        # Clean up
        service.shutdown()

    def test_watching_operations(self, temp_dir):
        """Test start/stop watching operations."""
        event_bus = MagicMock()
        service = FileSystemWatchService(event_bus)
        service.initialize()

        # Add a watch
        test_path = temp_dir / "test"
        test_path.mkdir()
        service.add_watch(test_path)

        # Test start/stop watching
        with patch.object(service._watcher, "start") as mock_start:
            service.start_watching()
            mock_start.assert_called_once()

        with patch.object(service._watcher, "stop") as mock_stop:
            service.stop_watching()
            mock_stop.assert_called_once()

        # Clean up
        service.shutdown()

    def test_handle_file_event(self):
        """Test the _handle_file_event method."""
        event_bus = MagicMock()
        service = FileSystemWatchService(event_bus)

        # Create a test event
        event = FileChangeEvent(
            path=Path("/test/file.txt"), change_type=FileChangeType.MODIFIED
        )

        # Call the method
        service._handle_file_event(event)

        # Verify event was published
        event_bus.publish.assert_called_once()
        published_event = event_bus.publish.call_args[0][0]
        assert published_event.path == event.path
        assert published_event.change_type == event.change_type
