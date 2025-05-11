"""Tests for filesystem events."""

from pathlib import Path
import unittest

from src.panoptikon.filesystem.events import (
    BookmarkEvent,
    CloudProviderType,
    CloudStorageEvent,
    DirectoryLimitEvent,
    FileChangeEvent,
    FileChangeType,
    FilePermissionEvent,
    FileSystemErrorEvent,
    FileSystemEvent,
    PermissionStatus,
    WatchedPathsChangedEvent,
)


class TestFileSystemEvent(unittest.TestCase):
    """Tests for the FileSystemEvent base class."""

    def test_initialization(self) -> None:
        """Test event initialization."""
        path = Path("/test/path")
        event = FileSystemEvent(path)

        # Verify attributes
        self.assertEqual(event.path, path)

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        path = Path("/test/path")
        event = FileSystemEvent(path)

        # Convert to dict
        result = event.to_dict()

        # Verify result
        self.assertIn("event_type", result)
        self.assertEqual(result["event_type"], "FileSystemEvent")
        self.assertIn("path", result)
        self.assertEqual(result["path"], str(path))


class TestFileChangeEvent(unittest.TestCase):
    """Tests for the FileChangeEvent class."""

    def test_initialization(self) -> None:
        """Test event initialization."""
        path = Path("/test/path")
        change_type = FileChangeType.MODIFIED
        event = FileChangeEvent(path, change_type)

        # Verify attributes
        self.assertEqual(event.path, path)
        self.assertEqual(event.change_type, change_type)
        self.assertIsNone(event.old_path)

        # With old path (rename)
        old_path = Path("/test/old_path")
        rename_event = FileChangeEvent(path, FileChangeType.RENAMED, old_path)
        self.assertEqual(rename_event.old_path, old_path)

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        path = Path("/test/path")
        old_path = Path("/test/old_path")
        change_type = FileChangeType.RENAMED
        event = FileChangeEvent(path, change_type, old_path)

        # Convert to dict
        result = event.to_dict()

        # Verify result
        self.assertEqual(result["event_type"], "FileChangeEvent")
        self.assertEqual(result["path"], str(path))
        self.assertEqual(result["change_type"], "RENAMED")
        self.assertEqual(result["old_path"], str(old_path))


class TestFilePermissionEvent(unittest.TestCase):
    """Tests for the FilePermissionEvent class."""

    def test_initialization(self) -> None:
        """Test event initialization."""
        path = Path("/test/path")
        status = PermissionStatus.GRANTED
        event = FilePermissionEvent(path, status)

        # Verify attributes
        self.assertEqual(event.path, path)
        self.assertEqual(event.status, status)
        self.assertIsNone(event.message)

        # With message
        message = "Permission granted by user"
        event_with_message = FilePermissionEvent(path, status, message)
        self.assertEqual(event_with_message.message, message)

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        path = Path("/test/path")
        status = PermissionStatus.DENIED
        message = "Access denied by system"
        event = FilePermissionEvent(path, status, message)

        # Convert to dict
        result = event.to_dict()

        # Verify result
        self.assertEqual(result["event_type"], "FilePermissionEvent")
        self.assertEqual(result["path"], str(path))
        self.assertEqual(result["status"], "DENIED")
        self.assertEqual(result["message"], message)

        # Without message
        event_no_message = FilePermissionEvent(path, status)
        result_no_message = event_no_message.to_dict()
        self.assertNotIn("message", result_no_message)


class TestCloudStorageEvent(unittest.TestCase):
    """Tests for the CloudStorageEvent class."""

    def test_initialization(self) -> None:
        """Test event initialization."""
        path = Path("/test/cloud/path")
        provider = CloudProviderType.DROPBOX
        online = True
        event = CloudStorageEvent(path, provider, online)

        # Verify attributes
        self.assertEqual(event.path, path)
        self.assertEqual(event.provider, provider)
        self.assertEqual(event.online, online)
        self.assertIsNone(event.sync_status)

        # With sync status
        sync_status = "Syncing 5 files"
        event_with_status = CloudStorageEvent(path, provider, online, sync_status)
        self.assertEqual(event_with_status.sync_status, sync_status)

        # Offline
        offline_event = CloudStorageEvent(path, provider, False)
        self.assertFalse(offline_event.online)

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        path = Path("/test/cloud/path")
        provider = CloudProviderType.ICLOUD
        online = True
        sync_status = "Up to date"
        event = CloudStorageEvent(path, provider, online, sync_status)

        # Convert to dict
        result = event.to_dict()

        # Verify result
        self.assertEqual(result["event_type"], "CloudStorageEvent")
        self.assertEqual(result["path"], str(path))
        self.assertEqual(result["provider"], "ICLOUD")
        self.assertEqual(result["online"], online)
        self.assertEqual(result["sync_status"], sync_status)

        # Without sync status
        event_no_status = CloudStorageEvent(path, provider, online)
        result_no_status = event_no_status.to_dict()
        self.assertNotIn("sync_status", result_no_status)


class TestFileSystemErrorEvent(unittest.TestCase):
    """Tests for the FileSystemErrorEvent class."""

    def test_initialization(self) -> None:
        """Test event initialization."""
        path = Path("/test/error/path")
        error_type = "PermissionError"
        message = "Permission denied"
        event = FileSystemErrorEvent(path, error_type, message)

        # Verify attributes
        self.assertEqual(event.path, path)
        self.assertEqual(event.error_type, error_type)
        self.assertEqual(event.message, message)
        self.assertIsNone(event.error_code)

        # With error code
        error_code = 13  # EACCES
        event_with_code = FileSystemErrorEvent(path, error_type, message, error_code)
        self.assertEqual(event_with_code.error_code, error_code)

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        path = Path("/test/error/path")
        error_type = "IOError"
        message = "Disk full"
        error_code = 28  # ENOSPC
        event = FileSystemErrorEvent(path, error_type, message, error_code)

        # Convert to dict
        result = event.to_dict()

        # Verify result
        self.assertEqual(result["event_type"], "FileSystemErrorEvent")
        self.assertEqual(result["path"], str(path))
        self.assertEqual(result["error_type"], error_type)
        self.assertEqual(result["message"], message)
        self.assertEqual(result["error_code"], error_code)

        # Without error code
        event_no_code = FileSystemErrorEvent(path, error_type, message)
        result_no_code = event_no_code.to_dict()
        self.assertNotIn("error_code", result_no_code)


class TestDirectoryLimitEvent(unittest.TestCase):
    """Tests for the DirectoryLimitEvent class."""

    def test_initialization(self) -> None:
        """Test event initialization."""
        path = Path("/test/dir")
        file_count = 10000
        total_size = 1024 * 1024 * 100  # 100 MB
        event = DirectoryLimitEvent(path, file_count, total_size)

        # Verify attributes
        self.assertEqual(event.path, path)
        self.assertEqual(event.file_count, file_count)
        self.assertEqual(event.total_size, total_size)
        self.assertFalse(event.limit_reached)

        # With limit reached
        limit_event = DirectoryLimitEvent(path, file_count, total_size, True)
        self.assertTrue(limit_event.limit_reached)

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        path = Path("/test/dir")
        file_count = 5000
        total_size = 1024 * 1024 * 50  # 50 MB
        event = DirectoryLimitEvent(path, file_count, total_size, True)

        # Convert to dict
        result = event.to_dict()

        # Verify result
        self.assertEqual(result["event_type"], "DirectoryLimitEvent")
        self.assertEqual(result["path"], str(path))
        self.assertEqual(result["file_count"], file_count)
        self.assertEqual(result["total_size"], total_size)
        self.assertEqual(result["limit_reached"], True)


class TestBookmarkEvent(unittest.TestCase):
    """Tests for the BookmarkEvent class."""

    def test_initialization(self) -> None:
        """Test event initialization."""
        path = Path("/test/bookmark/path")
        event = BookmarkEvent(path)

        # Verify default attributes
        self.assertEqual(event.path, path)
        self.assertFalse(event.created)
        self.assertTrue(event.valid)
        self.assertIsNone(event.error)

        # Created bookmark
        created_event = BookmarkEvent(path, created=True)
        self.assertTrue(created_event.created)

        # Invalid bookmark
        invalid_event = BookmarkEvent(path, valid=False)
        self.assertFalse(invalid_event.valid)

        # Error bookmark
        error_message = "Failed to create bookmark"
        error_event = BookmarkEvent(path, valid=False, error=error_message)
        self.assertEqual(error_event.error, error_message)

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        path = Path("/test/bookmark/path")
        error_message = "Failed to resolve bookmark"
        event = BookmarkEvent(path, created=True, valid=False, error=error_message)

        # Convert to dict
        result = event.to_dict()

        # Verify result
        self.assertEqual(result["event_type"], "BookmarkEvent")
        self.assertEqual(result["path"], str(path))
        self.assertEqual(result["created"], True)
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"], error_message)

        # Without error
        event_no_error = BookmarkEvent(path, created=True)
        result_no_error = event_no_error.to_dict()
        self.assertNotIn("error", result_no_error)


class TestWatchedPathsChangedEvent(unittest.TestCase):
    """Tests for the WatchedPathsChangedEvent class."""

    def test_initialization(self) -> None:
        """Test event initialization."""
        # Default initialization
        event = WatchedPathsChangedEvent()
        self.assertEqual(event.added_paths, set())
        self.assertEqual(event.removed_paths, set())

        # With added paths
        added_paths = {Path("/test/path1"), Path("/test/path2")}
        add_event = WatchedPathsChangedEvent(added_paths=added_paths)
        self.assertEqual(add_event.added_paths, added_paths)
        self.assertEqual(add_event.removed_paths, set())

        # With removed paths
        removed_paths = {Path("/test/path3")}
        remove_event = WatchedPathsChangedEvent(removed_paths=removed_paths)
        self.assertEqual(remove_event.added_paths, set())
        self.assertEqual(remove_event.removed_paths, removed_paths)

        # With both
        both_event = WatchedPathsChangedEvent(added_paths, removed_paths)
        self.assertEqual(both_event.added_paths, added_paths)
        self.assertEqual(both_event.removed_paths, removed_paths)

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        added_paths = {Path("/test/add1"), Path("/test/add2")}
        removed_paths = {Path("/test/remove1")}
        event = WatchedPathsChangedEvent(added_paths, removed_paths)

        # Convert to dict
        result = event.to_dict()

        # Verify result
        self.assertEqual(result["event_type"], "WatchedPathsChangedEvent")
        self.assertEqual(set(result["added_paths"]), {str(p) for p in added_paths})
        self.assertEqual(set(result["removed_paths"]), {str(p) for p in removed_paths})


if __name__ == "__main__":
    unittest.main()
