"""Tests for the bookmark service."""

from collections.abc import Generator
from pathlib import Path
import platform
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from src.panoptikon.core.events import EventBus
from src.panoptikon.filesystem.bookmarks import MACOS_APIS_AVAILABLE, BookmarkService
from src.panoptikon.filesystem.events import BookmarkEvent


@pytest.mark.skipif(
    platform.system() != "Darwin" or not MACOS_APIS_AVAILABLE,
    reason="Security bookmarks only work on macOS with PyObjC",
)
class TestBookmarkService:
    """Tests for the BookmarkService class."""

    @pytest.fixture
    def event_bus(self) -> MagicMock:
        """Create a mock event bus."""
        return MagicMock(spec=EventBus)

    @pytest.fixture
    def bookmark_service(self, event_bus: MagicMock) -> BookmarkService:
        """Create a bookmark service.

        Args:
            event_bus: Mock event bus

        Returns:
            Configured BookmarkService instance
        """
        service = BookmarkService(event_bus)
        return service

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Create a temporary directory for testing.

        Returns:
            Path to temporary directory
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    @pytest.fixture
    def test_file(self, temp_dir: Path) -> Path:
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

        with patch("Foundation.NSURL", spec=True) as mock_nsurl_class:
            with patch("Foundation.NSData", spec=True) as mock_nsdata_class:
                mock_nsdata_class.dataWithBytes_length_ = MagicMock(
                    return_value=mock_data
                )
                mock_nsurl_class.URLByResolvingBookmarkData_options_relativeToURL_bookmarkDataIsStale_error_ = mock_url

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

    def test_has_bookmark(
        self, bookmark_service: BookmarkService, test_file: Path
    ) -> None:
        """Test checking if a bookmark exists."""
        # Initialize
        with patch.object(Path, "mkdir"):
            bookmark_service.initialize()

        # Initially should not have bookmark
        assert bookmark_service.has_bookmark(test_file) is False

        # Create mock bookmark
        resolved_path = test_file.resolve()
        bookmark_service._bookmarks[resolved_path] = MagicMock()

        # Now should have bookmark
        assert bookmark_service.has_bookmark(test_file) is True

    def test_remove_bookmark(
        self, bookmark_service: BookmarkService, test_file: Path
    ) -> None:
        """Test removing a bookmark."""
        # Initialize
        with patch.object(Path, "mkdir"):
            bookmark_service.initialize()

        # Create mock bookmark and active scope
        resolved_path = test_file.resolve()
        bookmark_service._bookmarks[resolved_path] = MagicMock()
        bookmark_service._active_scopes[resolved_path] = 1

        # Mock bookmark file
        mock_bookmark_file = MagicMock()
        mock_bookmark_file.exists.return_value = True

        with patch.object(
            bookmark_service, "_path_to_filename", return_value="test_file"
        ):
            with patch.object(Path, "__truediv__", return_value=mock_bookmark_file):
                # Remove bookmark
                result = bookmark_service.remove_bookmark(test_file)

                # Should succeed
                assert result is True

                # Should remove from bookmarks and active scopes
                assert resolved_path not in bookmark_service._bookmarks
                assert resolved_path not in bookmark_service._active_scopes

                # Should remove file
                mock_bookmark_file.unlink.assert_called_once()

                # Try removing non-existent bookmark
                result = bookmark_service.remove_bookmark(test_file)
                assert result is False

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

        with patch("Foundation.NSURL", spec=True) as mock_nsurl_class:
            with patch("Foundation.NSData", spec=True) as mock_nsdata_class:
                mock_nsdata_class.dataWithBytes_length_ = MagicMock(
                    return_value=mock_data
                )
                mock_nsurl_class.URLByResolvingBookmarkData_options_relativeToURL_bookmarkDataIsStale_error_ = MagicMock(
                    return_value=(mock_url, False, None)
                )

                with patch.object(Path, "exists", return_value=True):
                    # Verify valid bookmark
                    result = bookmark_service._verify_bookmark(test_file, b"valid_data")
                    assert result is True

                # Now test the stale case
                mock_nsurl_class.URLByResolvingBookmarkData_options_relativeToURL_bookmarkDataIsStale_error_ = MagicMock(
                    return_value=(mock_url, True, None)
                )

                # Verify stale bookmark
                result = bookmark_service._verify_bookmark(test_file, b"stale_data")
                assert result is False

                # Now test the error case
                mock_error = MagicMock()
                mock_error.localizedDescription = MagicMock(
                    return_value="Error description"
                )
                mock_nsurl_class.URLByResolvingBookmarkData_options_relativeToURL_bookmarkDataIsStale_error_ = MagicMock(
                    return_value=(None, False, mock_error)
                )

                # Verify error case
                result = bookmark_service._verify_bookmark(test_file, b"error_data")
                assert result is False
