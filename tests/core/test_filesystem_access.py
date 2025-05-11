"""Tests for the filesystem access module."""

from pathlib import Path
import platform
import tempfile
import unittest
from unittest.mock import MagicMock

import pytest

from src.panoptikon.core.events import EventBus
from src.panoptikon.filesystem.access import (
    AccessRequest,
    AccessType,
    FileAccessService,
    PermissionStrategy,
)
from src.panoptikon.filesystem.bookmarks import BookmarkService
from src.panoptikon.filesystem.cloud import CloudStorageService
from src.panoptikon.filesystem.paths import PathManager


class TestFileAccessService(unittest.TestCase):
    """Tests for the FileAccessService class."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.event_bus = MagicMock(spec=EventBus)
        self.path_manager = MagicMock(spec=PathManager)
        self.bookmark_service = MagicMock(spec=BookmarkService)
        self.cloud_service = MagicMock(spec=CloudStorageService)

        # Set up temp files for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.test_file = self.temp_path / "test_file.txt"
        with open(self.test_file, "w") as f:
            f.write("Test content")

        self.service = FileAccessService(
            self.event_bus,
            self.path_manager,
            self.bookmark_service,
            self.cloud_service,
        )

        # Initialize handlers
        self.service.initialize()

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.temp_dir.cleanup()
        self.service.shutdown()

    def test_can_read_existing_file(self) -> None:
        """Test reading an existing file."""
        # Test file should be readable
        self.assertTrue(self.service.can_read(self.test_file))

    def test_can_write_existing_file(self) -> None:
        """Test writing to an existing file."""
        # Test file should be writable
        self.assertTrue(self.service.can_write(self.test_file))

    def test_read_file_contents(self) -> None:
        """Test reading file contents."""
        # Read the test file
        contents = self.service.read_file(self.test_file)
        self.assertIsNotNone(contents)
        self.assertEqual(b"Test content", contents)

    def test_write_file_contents(self) -> None:
        """Test writing file contents."""
        # Write to the test file
        result = self.service.write_file(self.test_file, b"New content")
        self.assertTrue(result)

        # Verify the content was written
        with open(self.test_file, "rb") as f:
            contents = f.read()
        self.assertEqual(b"New content", contents)

    def test_create_directory(self) -> None:
        """Test creating a directory."""
        # Create a new directory
        new_dir = self.temp_path / "new_dir"
        result = self.service.create_directory(new_dir)
        self.assertTrue(result)
        self.assertTrue(new_dir.exists())
        self.assertTrue(new_dir.is_dir())

    def test_delete_file(self) -> None:
        """Test deleting a file."""
        # Create a file to delete
        temp_file = self.temp_path / "to_delete.txt"
        with open(temp_file, "w") as f:
            f.write("Delete me")

        # Delete the file
        result = self.service.delete_file(temp_file)
        self.assertTrue(result)
        self.assertFalse(temp_file.exists())

    def test_move_file(self) -> None:
        """Test moving a file."""
        # Create a file to move
        source_file = self.temp_path / "to_move.txt"
        target_file = self.temp_path / "moved.txt"
        with open(source_file, "w") as f:
            f.write("Move me")

        # Move the file
        result = self.service.move_file(source_file, target_file)
        self.assertTrue(result)
        self.assertFalse(source_file.exists())
        self.assertTrue(target_file.exists())

        # Verify content
        with open(target_file) as f:
            content = f.read()
        self.assertEqual("Move me", content)

    @pytest.mark.skipif(
        platform.system() != "Darwin", reason="Security bookmarks only work on macOS"
    )
    def test_bookmark_integration(self) -> None:
        """Test integration with BookmarkService."""
        # Mock bookmark service behavior
        self.bookmark_service.has_bookmark.return_value = False
        self.bookmark_service.create_bookmark.return_value = True
        self.bookmark_service.start_access.return_value = True

        # Test with a path outside home (requires bookmark on macOS)
        test_path = Path("/tmp/test.txt")
        resolved_path = test_path.resolve()  # Handle /private/tmp on macOS

        # Request access
        request = AccessRequest(
            path=test_path,
            access_type=AccessType.READ,
            strategy=PermissionStrategy.PROGRESSIVE,
        )
        result = self.service.request_access(request)

        # Should try to create a bookmark
        self.bookmark_service.create_bookmark.assert_called_once_with(resolved_path)
        self.bookmark_service.start_access.assert_called_once_with(resolved_path)
        self.assertTrue(result.success)

    def test_cloud_integration(self) -> None:
        """Test integration with CloudStorageService."""
        # Mock provider detection
        self.cloud_service.get_provider_for_path.return_value = None

        # Get resolved path for test comparison
        resolved_test_file = self.test_file.resolve()

        # Request access to a path
        request = AccessRequest(
            path=self.test_file,
            access_type=AccessType.READ,
            strategy=PermissionStrategy.IMMEDIATE,
        )
        result = self.service.request_access(request)

        # Should check for cloud provider
        self.cloud_service.get_provider_for_path.assert_called_once_with(
            resolved_test_file
        )
        self.assertTrue(result.success)
