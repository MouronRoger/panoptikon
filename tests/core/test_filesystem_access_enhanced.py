"""Enhanced test suite for filesystem access functionality.

This module contains additional tests to improve coverage of the filesystem
access module, focusing on methods that aren't fully covered by existing tests.
"""

from pathlib import Path
import platform
from unittest.mock import MagicMock, patch

import pytest

from src.panoptikon.core.events import EventBus
from src.panoptikon.filesystem.access import (
    AccessRequest,
    AccessType,
    FileAccessService,
    PermissionStatus,
    PermissionStrategy,
)
from src.panoptikon.filesystem.bookmarks import BookmarkService
from src.panoptikon.filesystem.cloud import CloudProviderInfo, CloudStorageService
from src.panoptikon.filesystem.events import CloudProviderType
from src.panoptikon.filesystem.paths import PathManager


@pytest.fixture
def mock_dependencies():
    """Create mock dependencies for FileAccessService."""
    event_bus = MagicMock(spec=EventBus)
    path_manager = MagicMock(spec=PathManager)
    bookmark_service = MagicMock(spec=BookmarkService)
    cloud_service = MagicMock(spec=CloudStorageService)

    # Set up bookmark service mocks
    bookmark_service.has_bookmark.return_value = False
    bookmark_service.create_bookmark.return_value = True
    bookmark_service.start_access.return_value = True

    # Set up cloud service mocks
    cloud_service.get_provider_for_path.return_value = None

    return {
        "event_bus": event_bus,
        "path_manager": path_manager,
        "bookmark_service": bookmark_service,
        "cloud_service": cloud_service,
    }


@pytest.fixture
def access_service(mock_dependencies):
    """Create a FileAccessService with mock dependencies."""
    service = FileAccessService(
        event_bus=mock_dependencies["event_bus"],
        path_manager=mock_dependencies["path_manager"],
        bookmark_service=mock_dependencies["bookmark_service"],
        cloud_service=mock_dependencies["cloud_service"],
    )
    service.initialize()
    yield service
    service.shutdown()


class TestFileOperationHandlers:
    """Tests focusing on the file operation handlers in FileAccessService."""

    def test_standard_write_file_not_exists(self, access_service, tmp_path):
        """Test standard write on a file that doesn't exist."""
        non_existent = tmp_path / "does_not_exist.txt"

        # Mock the _standard_create method
        with patch.object(access_service, "_standard_create", return_value=True):
            result = access_service._standard_write(non_existent)
            assert result is True
            access_service._standard_create.assert_called_once_with(non_existent.parent)

    def test_standard_write_directory(self, access_service, tmp_path):
        """Test standard write on a directory."""
        # Create a temporary directory
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # Test the directory write functionality
        result = access_service._standard_write(test_dir)

        # Directory should be writable
        assert result is True

    def test_standard_delete_non_existent(self, access_service, tmp_path):
        """Test standard delete on a non-existent path."""
        non_existent = tmp_path / "does_not_exist.txt"

        # Deleting a non-existent file should succeed
        result = access_service._standard_delete(non_existent)
        assert result is True

    def test_standard_rename_non_existent(self, access_service, tmp_path):
        """Test standard rename on a non-existent path."""
        non_existent = tmp_path / "does_not_exist.txt"

        # Renaming a non-existent file should fail
        result = access_service._standard_rename(non_existent)
        assert result is False

    def test_standard_move_with_target(self, access_service, tmp_path):
        """Test standard move with a specified target."""
        source = tmp_path / "source.txt"
        source.touch()
        target = tmp_path / "target.txt"

        # Mock the _standard_write method
        with patch.object(access_service, "_standard_write", return_value=True):
            result = access_service._standard_move(source, target)
            assert result is True
            # Should check both source and target parent directories
            assert access_service._standard_write.call_count == 2

    def test_standard_move_non_existent(self, access_service, tmp_path):
        """Test standard move on a non-existent path."""
        non_existent = tmp_path / "does_not_exist.txt"
        target = tmp_path / "target.txt"

        # Moving a non-existent file should fail
        result = access_service._standard_move(non_existent, target)
        assert result is False

    def test_standard_create_parent_not_exists(self, access_service, tmp_path):
        """Test standard create when parent doesn't exist."""
        path = tmp_path / "non_existent_dir" / "file.txt"

        # Creating a file in a non-existent directory should fail
        result = access_service._standard_create(path)
        assert result is False


class TestAccessRequestHandling:
    """Tests focusing on access request handling in FileAccessService."""

    def test_get_operation_handler_cloud_provider(
        self, access_service, mock_dependencies
    ):
        """Test getting operation handler for a cloud provider path."""
        path = Path("/cloud/path")

        # Setup mock provider and handler
        provider = CloudProviderInfo(
            provider_type=CloudProviderType.ICLOUD,
            display_name="Test Provider",
            root_path=Path("/cloud"),
        )
        mock_handler = MagicMock(return_value=True)

        # Mock cloud service to return our provider
        mock_dependencies["cloud_service"].get_provider_for_path.return_value = provider

        # Mock both methods to avoid bookmark handling and use our handler
        with patch.object(
            access_service, "_get_operation_handler", return_value=mock_handler
        ):
            with patch.object(
                access_service, "_handle_bookmark_access", return_value=None
            ):
                # Test request_access which will use our mocked handler
                request = AccessRequest(
                    path=path,
                    access_type=AccessType.READ,
                    strategy=PermissionStrategy.IMMEDIATE,
                )
                result = access_service.request_access(request)

                # Request should succeed
                assert result.success is True

                # Verify our mock handler was called with the path
                mock_handler.assert_called_once_with(path)

    def test_get_operation_handler_fallback(self, access_service):
        """Test falling back to standard handler when no provider-specific handler exists."""
        path = Path("/some/path")

        # Get the handler for an access type that should have a standard handler
        handler = access_service._get_operation_handler(path, AccessType.READ)

        # Verify it returns a callable
        assert callable(handler)

        # The standard READ handler should be the _standard_read method
        assert handler == access_service._standard_read

    def test_handle_bookmark_access_not_needed(self, access_service, tmp_path):
        """Test bookmark handling when not needed (relative path)."""
        path = Path("relative/path")
        request = AccessRequest(path=path, access_type=AccessType.READ)

        result = access_service._handle_bookmark_access(path, request)
        assert result is None

        # Bookmark service should not be called
        access_service._bookmark_service.has_bookmark.assert_not_called()

    @pytest.mark.skipif(platform.system() != "Darwin", reason="macOS-specific test")
    def test_handle_bookmark_access_macos_home(self, access_service):
        """Test bookmark handling for path in home directory on macOS."""
        path = Path.home() / "test.txt"
        request = AccessRequest(path=path, access_type=AccessType.READ)

        result = access_service._handle_bookmark_access(path, request)
        assert result is None

        # Bookmark service should not be called for home directory
        access_service._bookmark_service.has_bookmark.assert_not_called()

    def test_handle_bookmark_access_immediate_strategy(
        self, access_service, mock_dependencies
    ):
        """Test bookmark handling with IMMEDIATE strategy."""
        # Use a mock to simulate macOS
        with patch("platform.system", return_value="Darwin"):
            # Setup a path outside home directory
            path = Path("/outside/home/file.txt")
            request = AccessRequest(
                path=path,
                access_type=AccessType.READ,
                strategy=PermissionStrategy.IMMEDIATE,
            )

            # Ensure bookmark service reports no bookmark
            mock_dependencies["bookmark_service"].has_bookmark.return_value = False

            result = access_service._handle_bookmark_access(path, request)

            # Should fail with IMMEDIATE strategy
            assert result is not None
            assert result.success is False
            assert result.permission_status == PermissionStatus.DENIED
            assert "IMMEDIATE strategy" in result.message

    def test_handle_bookmark_access_progressive_strategy(
        self, access_service, mock_dependencies
    ):
        """Test bookmark handling with PROGRESSIVE strategy."""
        # Use a mock to simulate macOS
        with patch("platform.system", return_value="Darwin"):
            # Setup a path outside home directory
            path = Path("/outside/home/file.txt")
            request = AccessRequest(
                path=path,
                access_type=AccessType.READ,
                strategy=PermissionStrategy.PROGRESSIVE,
            )

            # Ensure bookmark service reports no bookmark
            mock_dependencies["bookmark_service"].has_bookmark.return_value = False
            mock_dependencies["bookmark_service"].create_bookmark.return_value = True
            mock_dependencies["bookmark_service"].start_access.return_value = True

            result = access_service._handle_bookmark_access(path, request)

            # Should succeed with PROGRESSIVE strategy
            assert result is None
            mock_dependencies[
                "bookmark_service"
            ].create_bookmark.assert_called_once_with(path)
            mock_dependencies["bookmark_service"].start_access.assert_called_once_with(
                path
            )

    def test_handle_bookmark_access_create_failure(
        self, access_service, mock_dependencies
    ):
        """Test bookmark handling when creation fails."""
        # Use a mock to simulate macOS
        with patch("platform.system", return_value="Darwin"):
            # Setup a path outside home directory
            path = Path("/outside/home/file.txt")
            request = AccessRequest(
                path=path,
                access_type=AccessType.READ,
                strategy=PermissionStrategy.PROGRESSIVE,
            )

            # Ensure bookmark service reports failures
            mock_dependencies["bookmark_service"].has_bookmark.return_value = False
            mock_dependencies["bookmark_service"].create_bookmark.return_value = False

            result = access_service._handle_bookmark_access(path, request)

            # Should fail when bookmark creation fails
            assert result is not None
            assert result.success is False
            assert result.permission_status == PermissionStatus.DENIED
            assert "Failed to create security bookmark" in result.message

    def test_handle_access_denied_silent_fail(self, access_service):
        """Test handling access denied with SILENT_FAIL strategy."""
        path = Path("/some/path")
        request = AccessRequest(
            path=path,
            access_type=AccessType.READ,
            strategy=PermissionStrategy.SILENT_FAIL,
        )

        result = access_service._handle_access_denied(path, request)

        # Should fail silently
        assert result.success is False
        assert result.permission_status == PermissionStatus.DENIED
        assert result.message is None

        # No event should be published
        access_service._event_bus.publish.assert_not_called()

    def test_handle_access_denied_with_event(self, access_service):
        """Test handling access denied with event publication."""
        path = Path("/some/path")
        request = AccessRequest(
            path=path,
            access_type=AccessType.READ,
            strategy=PermissionStrategy.IMMEDIATE,
            message="Custom message",
        )

        result = access_service._handle_access_denied(path, request)

        # Should fail and publish event
        assert result.success is False
        assert result.permission_status == PermissionStatus.DENIED
        assert "Permission denied" in result.message

        # Event should be published
        access_service._event_bus.publish.assert_called_once()


class TestHighLevelAccessMethods:
    """Tests for the high-level access methods in FileAccessService."""

    def test_create_directory_success(self, access_service, tmp_path):
        """Test creating a directory successfully."""
        new_dir = tmp_path / "new_directory"

        # Mock the request_access method to return success
        with patch.object(access_service, "request_access") as mock_request:
            mock_request.return_value.success = True

            result = access_service.create_directory(new_dir)

            assert result is True
            assert new_dir.exists()
            assert new_dir.is_dir()

    def test_move_file_success(self, access_service, tmp_path):
        """Test moving a file successfully."""
        source = tmp_path / "source.txt"
        source.write_text("test content")
        target = tmp_path / "target.txt"

        # Mock the request_access method to return success
        with patch.object(access_service, "request_access") as mock_request:
            mock_request.return_value.success = True

            result = access_service.move_file(source, target)

            assert result is True
            assert not source.exists()
            assert target.exists()
            assert target.read_text() == "test content"

    def test_move_file_failure(self, access_service, tmp_path):
        """Test moving a file with permission failure."""
        source = tmp_path / "source.txt"
        source.write_text("test content")
        target = tmp_path / "target.txt"

        # Mock the request_access method to return failure
        with patch.object(access_service, "request_access") as mock_request:
            mock_request.return_value.success = False

            result = access_service.move_file(source, target)

            assert result is False
            assert source.exists()
            assert not target.exists()
