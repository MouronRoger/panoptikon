"""Consolidated tests for the bookmarks service.

This module provides a comprehensive yet maintainable set of tests for the BookmarkService,
which manages security-scoped bookmarks for macOS applications.
"""

from collections.abc import Generator
from datetime import datetime
from pathlib import Path
import platform
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from src.panoptikon.core.events import EventBus
from src.panoptikon.filesystem.bookmarks import (
    MACOS_APIS_AVAILABLE,
    Bookmark,
    BookmarkService,
)
from src.panoptikon.filesystem.events import BookmarkEvent


class TestBookmarkDataClass:
    """Tests for the Bookmark dataclass."""

    def test_bookmark_creation(self) -> None:
        """Test creating a Bookmark object."""
        path = Path("/test/path")
        bookmark_data = b"dummy bookmark data"
        now = datetime.now()

        bookmark = Bookmark(
            path=path,
            bookmark_data=bookmark_data,
            created_at=now,
            last_accessed=now,
        )

        assert bookmark.path == path
        assert bookmark.bookmark_data == bookmark_data
        assert bookmark.created_at == now
        assert bookmark.last_accessed == now
        assert bookmark.is_valid  # Default is True
        assert bookmark.access_count == 0  # Default is 0


@pytest.fixture
def event_bus() -> MagicMock:
    """Create a mock event bus."""
    return MagicMock(spec=EventBus)


@pytest.fixture
def bookmark_service(event_bus: MagicMock) -> BookmarkService:
    """Create a bookmark service for testing.

    Args:
        event_bus: Mock event bus

    Returns:
        Configured BookmarkService instance
    """
    service = BookmarkService(event_bus)
    return service


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing.

    Returns:
        Path to temporary directory
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def test_file(temp_dir: Path) -> Path:
    """Create a test file for bookmark testing.

    Args:
        temp_dir: Temporary directory

    Returns:
        Path to test file
    """
    test_file = temp_dir / "test_file.txt"
    with open(test_file, "w") as f:
        f.write("Test content for bookmark")
    return test_file


class TestBookmarkServiceBasics:
    """Tests for basic BookmarkService functionality regardless of platform."""

    def test_initialization(self, bookmark_service: BookmarkService) -> None:
        """Test service initialization."""
        # Initially should have no bookmarks
        assert bookmark_service._bookmarks == {}
        assert bookmark_service._active_scopes == {}
        assert bookmark_service._bookmark_storage_path is None

        # Initialize
        with patch.object(Path, "mkdir") as mock_mkdir:
            bookmark_service.initialize()
            # Verify storage dir was created
            mock_mkdir.assert_called_once()

        # Storage path should be set
        assert bookmark_service._bookmark_storage_path is not None
        assert "bookmarks" in str(bookmark_service._bookmark_storage_path)

    def test_shutdown(self, bookmark_service: BookmarkService) -> None:
        """Test service shutdown."""
        # Initialize
        with patch.object(Path, "mkdir"):
            bookmark_service.initialize()

        # Add a mock active scope
        test_path = Path("/test/path")
        bookmark_service._active_scopes[test_path] = 1

        # Shutdown
        with patch.object(bookmark_service, "stop_access") as mock_stop:
            bookmark_service.shutdown()
            # Should stop access to all active bookmarks
            mock_stop.assert_called_once_with(test_path)

        # Bookmarks should be cleared
        assert bookmark_service._bookmarks == {}

    def test_has_bookmark(self, bookmark_service: BookmarkService) -> None:
        """Test has_bookmark method."""
        # Create a test path
        path = Path("/test/path")
        resolved_path = path.resolve()

        # Initially should not have bookmark
        assert bookmark_service.has_bookmark(path) is False

        # Add mock bookmark
        bookmark_service._bookmarks[resolved_path] = MagicMock()

        # Now should have bookmark
        assert bookmark_service.has_bookmark(path) is True

    def test_is_valid(self, bookmark_service: BookmarkService) -> None:
        """Test is_valid method."""
        path = Path("/test/path")
        resolved_path = path.resolve()

        # Add a valid bookmark
        valid_bookmark = MagicMock(spec=Bookmark)
        valid_bookmark.is_valid = True
        bookmark_service._bookmarks[resolved_path] = valid_bookmark

        # Check validity
        assert bookmark_service.is_valid(path) is True

        # Make it invalid
        valid_bookmark.is_valid = False
        assert bookmark_service.is_valid(path) is False

        # Test with non-existent bookmark
        non_existent_path = Path("/non/existent/path")
        assert bookmark_service.is_valid(non_existent_path) is False

    def test_get_bookmarked_paths(self, bookmark_service: BookmarkService) -> None:
        """Test get_bookmarked_paths method."""
        # No bookmarks initially
        assert not bookmark_service.get_bookmarked_paths()

        # Add some bookmarks
        path1 = Path("/test/path1")
        path2 = Path("/test/path2")
        bookmark_service._bookmarks = {
            path1: MagicMock(spec=Bookmark),
            path2: MagicMock(spec=Bookmark),
        }

        # Get paths
        paths = bookmark_service.get_bookmarked_paths()
        assert len(paths) == 2
        assert path1 in paths
        assert path2 in paths


class TestBookmarkStorage:
    """Tests for bookmark storage and loading."""

    def test_path_to_filename(self, bookmark_service: BookmarkService) -> None:
        """Test converting a path to a safe filename."""
        path = Path("/test/path/with:special/chars")
        filename = bookmark_service._path_to_filename(path)

        assert "/" not in filename
        assert ":" not in filename
        assert "_" in filename

    def test_save_and_read_bookmark(
        self, bookmark_service: BookmarkService, temp_dir: Path
    ) -> None:
        """Test saving and reading a bookmark file."""
        bookmark_service._bookmark_storage_path = temp_dir

        path = Path("/test/path")
        bookmark_data = b"test bookmark data"
        now = datetime.now()

        bookmark = Bookmark(
            path=path,
            bookmark_data=bookmark_data,
            created_at=now,
            last_accessed=now,
        )

        # Save the bookmark
        result = bookmark_service._save_bookmark(bookmark)
        assert result is True

        # Verify file was created
        expected_filename = f"{bookmark_service._path_to_filename(path)}.bookmark"
        bookmark_file = temp_dir / expected_filename
        assert bookmark_file.exists()

        # Read the bookmark back
        read_path, read_data, read_time = bookmark_service._read_bookmark_file(
            bookmark_file
        )

        # Verify data
        assert read_path == path
        assert read_data == bookmark_data

        # Timestamps might not match exactly due to floating point conversion
        # Just check they're close (within 1 second)
        assert abs(read_time.timestamp() - now.timestamp()) < 1.0

    def test_remove_bookmark(
        self, bookmark_service: BookmarkService, temp_dir: Path
    ) -> None:
        """Test removing a bookmark."""
        path = Path("/test/path")
        resolved_path = path.resolve()
        bookmark = MagicMock(spec=Bookmark)
        bookmark_service._bookmarks[resolved_path] = bookmark
        bookmark_service._bookmark_storage_path = temp_dir

        # Create a mock bookmark file
        bookmark_file = (
            temp_dir / f"{bookmark_service._path_to_filename(resolved_path)}.bookmark"
        )
        with open(bookmark_file, "wb") as f:
            f.write(b"dummy content")

        # Remove the bookmark
        with patch.object(bookmark_service, "stop_access") as mock_stop_access:
            result = bookmark_service.remove_bookmark(path)

            # Verify result
            assert result is True
            assert resolved_path not in bookmark_service._bookmarks

            # Verify bookmark file is removed
            assert not bookmark_file.exists()

            # If stop_access was called, it would mean the path was in active_scopes
            mock_stop_access.assert_not_called()

    def test_remove_bookmark_with_active_access(
        self, bookmark_service: BookmarkService, temp_dir: Path
    ) -> None:
        """Test removing a bookmark with active access."""
        path = Path("/test/path")
        resolved_path = path.resolve()
        bookmark = MagicMock(spec=Bookmark)
        bookmark_service._bookmarks[resolved_path] = bookmark
        bookmark_service._active_scopes[resolved_path] = 1
        bookmark_service._bookmark_storage_path = temp_dir

        # Remove the bookmark
        with patch.object(bookmark_service, "stop_access") as mock_stop_access:
            result = bookmark_service.remove_bookmark(path)

            # Verify result
            assert result is True
            assert resolved_path not in bookmark_service._bookmarks

            # Verify stop_access was called
            mock_stop_access.assert_called_once_with(path)

    def test_load_bookmarks(
        self, bookmark_service: BookmarkService, temp_dir: Path
    ) -> None:
        """Test loading bookmarks from disk."""
        bookmark_service._bookmark_storage_path = temp_dir

        # Create two paths with different validity
        path1 = Path("/test/path1")
        path2 = Path("/test/path2")
        bookmark_data1 = b"bookmark data 1"
        bookmark_data2 = b"bookmark data 2"

        # Create mock read_bookmark_file method
        def mock_read_bookmark(file_path: Path) -> tuple[Path, bytes, datetime]:
            if "path1" in str(file_path):
                return path1, bookmark_data1, datetime.now()
            else:
                return path2, bookmark_data2, datetime.now()

        # Create mock verify_bookmark method
        def mock_verify_bookmark(path: Path, data: bytes) -> bool:
            return path == path1  # Only path1 is valid

        with (
            patch.object(
                bookmark_service, "_read_bookmark_file", side_effect=mock_read_bookmark
            ),
            patch.object(
                bookmark_service, "_verify_bookmark", side_effect=mock_verify_bookmark
            ),
            patch(
                "pathlib.Path.glob",
                return_value=[temp_dir / "path1.bookmark", temp_dir / "path2.bookmark"],
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            bookmark_service._load_bookmarks()

            # Both bookmarks should be loaded
            assert path1 in bookmark_service._bookmarks
            assert path2 in bookmark_service._bookmarks

            # But only path1 should be valid
            assert bookmark_service._bookmarks[path1].is_valid is True
            assert bookmark_service._bookmarks[path2].is_valid is False


@pytest.mark.skipif(
    platform.system() != "Darwin" or not MACOS_APIS_AVAILABLE,
    reason="Security bookmarks only work on macOS with PyObjC",
)
class TestMacOSBookmarkOperations:
    """Tests for macOS-specific bookmark operations."""

    def test_create_bookmark(
        self, bookmark_service: BookmarkService, test_file: Path, event_bus: MagicMock
    ) -> None:
        """Test creating a bookmark."""
        # Initialize
        with patch.object(Path, "mkdir"):
            bookmark_service.initialize()

        # Mock the macOS APIs for bookmark creation
        mock_bookmark_data = b"mock_bookmark_data"
        mock_url = MagicMock()
        mock_url.bookmarkDataWithOptions_includingResourceValuesForKeys_relativeToURL_error_ = MagicMock(
            return_value=(mock_bookmark_data, None)
        )

        with patch("Foundation.NSURL", spec=True) as mock_nsurl_class:
            mock_nsurl_class.fileURLWithPath_ = MagicMock(return_value=mock_url)

            # Create bookmark
            result = bookmark_service.create_bookmark(test_file)

            # Should succeed
            assert result is True

            # Should store bookmark
            resolved_path = test_file.resolve()
            assert resolved_path in bookmark_service._bookmarks

            # Check bookmark data
            bookmark = bookmark_service._bookmarks[resolved_path]
            assert bookmark.path == resolved_path
            assert bookmark.bookmark_data == mock_bookmark_data
            assert bookmark.is_valid is True

            # Should publish event
            event_bus.publish.assert_called_once()
            event = event_bus.publish.call_args[0][0]
            assert isinstance(event, BookmarkEvent)
            assert event.path == resolved_path
            assert event.created is True

    def test_create_bookmark_error(
        self, bookmark_service: BookmarkService, test_file: Path, event_bus: MagicMock
    ) -> None:
        """Test handling errors during bookmark creation."""
        # Initialize
        with patch.object(Path, "mkdir"):
            bookmark_service.initialize()

        # Mock the macOS APIs for bookmark creation failure
        mock_error = MagicMock()
        mock_error.localizedDescription = MagicMock(return_value="Permission denied")
        mock_url = MagicMock()
        mock_url.bookmarkDataWithOptions_includingResourceValuesForKeys_relativeToURL_error_ = MagicMock(
            return_value=(None, mock_error)
        )

        with patch("Foundation.NSURL", spec=True) as mock_nsurl_class:
            mock_nsurl_class.fileURLWithPath_ = MagicMock(return_value=mock_url)

            # Try to create bookmark
            result = bookmark_service.create_bookmark(test_file)

            # Should fail
            assert result is False

            # Should not store bookmark
            resolved_path = test_file.resolve()
            assert resolved_path not in bookmark_service._bookmarks

            # Should publish error event
            event_bus.publish.assert_called_once()
            event = event_bus.publish.call_args[0][0]
            assert isinstance(event, BookmarkEvent)
            assert event.path == resolved_path
            assert event.created is False
            assert event.valid is False
            assert event.error == "Permission denied"

    def test_start_access(
        self, bookmark_service: BookmarkService, test_file: Path, event_bus: MagicMock
    ) -> None:
        """Test starting access to a bookmarked path."""
        # Initialize
        with patch.object(Path, "mkdir"):
            bookmark_service.initialize()

        # Create a mock bookmark
        resolved_path = test_file.resolve()
        mock_bookmark_data = b"mock_bookmark_data"

        # Add bookmark directly to avoid dependency on create_bookmark
        bookmark_service._bookmarks[resolved_path] = MagicMock(
            path=resolved_path, bookmark_data=mock_bookmark_data, is_valid=True
        )

        # Reset mock to clear creation events
        event_bus.reset_mock()

        # Mock URL resolution for accessing
        mock_url = MagicMock()
        mock_url.startAccessingSecurityScopedResource = MagicMock(return_value=True)
        mock_data = MagicMock()

        with (
            patch("Foundation.NSURL", spec=True) as mock_nsurl_class,
            patch("Foundation.NSData", spec=True) as mock_nsdata_class,
        ):
            mock_nsdata_class.dataWithBytes_length_ = MagicMock(return_value=mock_data)
            method_name = (
                "URLByResolvingBookmarkData_options_relativeToURL_"
                "bookmarkDataIsStale_error_"
            )
            setattr(mock_nsurl_class, method_name, mock_url)

            # Set appropriate values for objc.NULL
            with patch("objc.NULL", None):
                # Start access
                result = bookmark_service.start_access(test_file)

                # Should succeed
                assert result is True

                # Should increment reference count
                assert resolved_path in bookmark_service._active_scopes
                assert bookmark_service._active_scopes[resolved_path] == 1

                # Start access again - should increment count
                result = bookmark_service.start_access(test_file)
                assert result is True
                assert bookmark_service._active_scopes[resolved_path] == 2

    def test_start_access_no_bookmark(
        self, bookmark_service: BookmarkService, test_file: Path
    ) -> None:
        """Test starting access with no bookmark."""
        # Start access without a bookmark
        result = bookmark_service.start_access(test_file)

        # Verify result
        assert result is False
        assert test_file.resolve() not in bookmark_service._active_scopes

    def test_start_access_already_active(
        self, bookmark_service: BookmarkService, test_file: Path
    ) -> None:
        """Test starting access when already active."""
        resolved_path = test_file.resolve()
        bookmark_service._bookmarks[resolved_path] = MagicMock(spec=Bookmark)
        bookmark_service._active_scopes[resolved_path] = 1

        # Start access
        result = bookmark_service.start_access(test_file)

        # Verify result
        assert result is True
        assert bookmark_service._active_scopes[resolved_path] == 2

    def test_stop_access(
        self, bookmark_service: BookmarkService, test_file: Path
    ) -> None:
        """Test stopping access to a bookmarked path."""
        # Initialize
        with patch.object(Path, "mkdir"):
            bookmark_service.initialize()

        # Create mock active scope
        resolved_path = test_file.resolve()
        bookmark_service._active_scopes[resolved_path] = 2

        # Mock URL for stopping access
        mock_url = MagicMock()
        mock_url.stopAccessingSecurityScopedResource = MagicMock()

        with patch("Foundation.NSURL", spec=True) as mock_nsurl_class:
            mock_nsurl_class.fileURLWithPath_ = MagicMock(return_value=mock_url)

            # Stop access once - should decrement count
            bookmark_service.stop_access(test_file)
            assert bookmark_service._active_scopes[resolved_path] == 1

            # Stop access again - should remove from active scopes
            bookmark_service.stop_access(test_file)
            assert resolved_path not in bookmark_service._active_scopes

            # Verify URL method called
            mock_url.stopAccessingSecurityScopedResource.assert_called()

    def test_stop_access_not_active(
        self, bookmark_service: BookmarkService, test_file: Path
    ) -> None:
        """Test stopping access that wasn't active."""
        # Stop access for a path that isn't active
        with patch("Foundation.NSURL") as mock_nsurl_class:
            bookmark_service.stop_access(test_file)

            # Verify no attempt to access the URL class
            mock_nsurl_class.fileURLWithPath_.assert_not_called()

    def test_verify_bookmark(
        self, bookmark_service: BookmarkService, test_file: Path
    ) -> None:
        """Test verifying a bookmark's validity."""
        # Initialize
        with patch.object(Path, "mkdir"):
            bookmark_service.initialize()

        # Mock URL resolution for verification - valid case
        mock_url = MagicMock()
        mock_data = MagicMock()

        with (
            patch("Foundation.NSURL", spec=True) as mock_nsurl_class,
            patch("Foundation.NSData", spec=True) as mock_nsdata_class,
        ):
            mock_nsdata_class.dataWithBytes_length_ = MagicMock(return_value=mock_data)
            method_name = (
                "URLByResolvingBookmarkData_options_relativeToURL_"
                "bookmarkDataIsStale_error_"
            )
            # Valid case
            setattr(
                mock_nsurl_class,
                method_name,
                MagicMock(return_value=(mock_url, False, None)),
            )

            with patch.object(Path, "exists", return_value=True):
                # Verify valid bookmark
                result = bookmark_service._verify_bookmark(test_file, b"valid_data")
                assert result is True

            # Now test the stale case
            setattr(
                mock_nsurl_class,
                method_name,
                MagicMock(return_value=(mock_url, True, None)),
            )

            # Verify stale bookmark
            result = bookmark_service._verify_bookmark(test_file, b"stale_data")
            assert result is False

            # Now test the error case
            mock_error = MagicMock()
            mock_error.localizedDescription = MagicMock(
                return_value="Error description"
            )
            setattr(
                mock_nsurl_class,
                method_name,
                MagicMock(return_value=(None, False, mock_error)),
            )

            # Verify error case
            result = bookmark_service._verify_bookmark(test_file, b"error_data")
            assert result is False
