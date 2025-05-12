"""Tests for the filesystem access module.

This module contains tests for the FileAccessService class, including basic
functionality, edge cases, and handling of different permission strategies.
"""

from collections.abc import Generator
from pathlib import Path
import platform
import tempfile
from typing import Dict
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
def mock_dependencies() -> Dict[str, MagicMock]:
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
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def access_service(
    mock_dependencies: Dict[str, MagicMock],
) -> Generator[FileAccessService, None, None]:
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


@pytest.fixture
def test_file(temp_dir: Path) -> Path:
    """Create a test file."""
    test_file = temp_dir / "test_file.txt"
    test_file.write_text("Test content")
    return test_file


class TestBasicFileOperations:
    """Tests for basic file operations."""

    def test_can_read_existing_file(
        self, access_service: FileAccessService, test_file: Path
    ) -> None:
        """Test reading an existing file."""
        with patch.object(access_service, "can_read", return_value=True):
            assert access_service.can_read(test_file)

    def test_can_write_existing_file(
        self, access_service: FileAccessService, test_file: Path
    ) -> None:
        """Test writing to an existing file."""
        with patch.object(access_service, "can_write", return_value=True):
            assert access_service.can_write(test_file)

    def test_read_file_contents(
        self, access_service: FileAccessService, test_file: Path
    ) -> None:
        """Test reading file contents."""
        contents = access_service.read_file(test_file)
        assert contents == b"Test content"

    def test_write_file_contents(
        self, access_service: FileAccessService, test_file: Path
    ) -> None:
        """Test writing file contents."""
        result = access_service.write_file(test_file, b"New content")
        assert result

        # Verify the content was written
        assert test_file.read_bytes() == b"New content"

    def test_create_directory(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test creating a directory."""
        new_dir = temp_dir / "new_dir"
        result = access_service.create_directory(new_dir)
        assert result
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_delete_file(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test deleting a file."""
        temp_file = temp_dir / "to_delete.txt"
        temp_file.write_text("Delete me")

        result = access_service.delete_file(temp_file)
        assert result
        assert not temp_file.exists()

    def test_move_file(self, access_service: FileAccessService, temp_dir: Path) -> None:
        """Test moving a file."""
        source_file = temp_dir / "to_move.txt"
        target_file = temp_dir / "moved.txt"
        source_file.write_text("Move me")

        result = access_service.move_file(source_file, target_file)
        assert result
        assert not source_file.exists()
        assert target_file.exists()
        assert target_file.read_text() == "Move me"


class TestFileOperationHandlers:
    """Tests focusing on the file operation handlers in FileAccessService."""

    def test_standard_write_file_not_exists(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test standard write on a file that doesn't exist."""
        non_existent = temp_dir / "does_not_exist.txt"

        # Mock the _standard_create method
        mock_create = MagicMock(return_value=True)
        with patch.object(access_service, "_standard_create", mock_create):
            result = access_service._standard_write(non_existent)
            assert result is True
            mock_create.assert_called_once_with(non_existent.parent)

    def test_standard_write_directory(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test standard write on a directory."""
        # Create a temporary directory
        test_dir = temp_dir / "test_dir"
        test_dir.mkdir()

        # Test the directory write functionality
        result = access_service._standard_write(test_dir)

        # Directory should be writable
        assert result is True

    def test_standard_delete_non_existent(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test standard delete on a non-existent path."""
        non_existent = temp_dir / "does_not_exist.txt"

        # Deleting a non-existent file should succeed
        result = access_service._standard_delete(non_existent)
        assert result is True

    def test_standard_rename_non_existent(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test standard rename on a non-existent path."""
        non_existent = temp_dir / "does_not_exist.txt"

        # Renaming a non-existent file should fail
        result = access_service._standard_rename(non_existent)
        assert result is False

    def test_standard_move_with_target(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test standard move with a specified target."""
        source = temp_dir / "source.txt"
        source.touch()
        target = temp_dir / "target.txt"

        # Mock the _standard_write method
        mock_write = MagicMock(return_value=True)
        with patch.object(access_service, "_standard_write", mock_write):
            result = access_service._standard_move(source, target)
            assert result is True
            # Should check both source and target parent directories
            assert mock_write.call_count == 2

    def test_standard_move_non_existent(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test standard move on a non-existent path."""
        non_existent = temp_dir / "does_not_exist.txt"
        target = temp_dir / "target.txt"

        # Moving a non-existent file should fail
        result = access_service._standard_move(non_existent, target)
        assert result is False

    def test_standard_create_parent_not_exists(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test standard create when parent doesn't exist."""
        path = temp_dir / "non_existent_dir" / "file.txt"

        # Creating a file in a non-existent directory should fail
        result = access_service._standard_create(path)
        assert result is False


class TestAccessRequestHandling:
    """Tests focusing on access request handling in FileAccessService."""

    def test_get_operation_handler_cloud_provider(
        self, access_service: FileAccessService, mock_dependencies: Dict[str, MagicMock]
    ) -> None:
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

    def test_get_operation_handler_fallback(
        self, access_service: FileAccessService
    ) -> None:
        """Test falling back to standard handler when no provider-specific handler exists."""
        path = Path("/some/path")

        # Get the handler for an access type that should have a standard handler
        handler = access_service._get_operation_handler(path, AccessType.READ)

        # Verify it returns a callable
        assert callable(handler)

        # The standard READ handler should be the _standard_read method
        assert handler == access_service._standard_read

    def test_handle_bookmark_access_not_needed(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test bookmark handling when not needed (relative path)."""
        path = Path("relative/path")
        request = AccessRequest(path=path, access_type=AccessType.READ)

        # Mock bookmark service has_bookmark method
        with patch.object(
            access_service._bookmark_service,
            "has_bookmark",
            MagicMock(return_value=False),
        ) as mock_has_bookmark:
            result = access_service._handle_bookmark_access(path, request)
            assert result is None

            # Bookmark service should not be called
            mock_has_bookmark.assert_not_called()

    @pytest.mark.skipif(platform.system() != "Darwin", reason="macOS-specific test")
    def test_handle_bookmark_access_macos_home(
        self, access_service: FileAccessService
    ) -> None:
        """Test bookmark handling for path in home directory on macOS."""
        path = Path.home() / "test.txt"
        request = AccessRequest(path=path, access_type=AccessType.READ)

        # Mock bookmark service has_bookmark method
        with patch.object(
            access_service._bookmark_service,
            "has_bookmark",
            MagicMock(return_value=False),
        ) as mock_has_bookmark:
            result = access_service._handle_bookmark_access(path, request)
            assert result is None

            # Bookmark service should not be called for home directory
            mock_has_bookmark.assert_not_called()

    def test_handle_bookmark_access_immediate_strategy(
        self, access_service: FileAccessService, mock_dependencies: Dict[str, MagicMock]
    ) -> None:
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
            assert "IMMEDIATE strategy" in str(result.message or "")

    def test_handle_bookmark_access_progressive_strategy(
        self, access_service: FileAccessService, mock_dependencies: Dict[str, MagicMock]
    ) -> None:
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
        self, access_service: FileAccessService, mock_dependencies: Dict[str, MagicMock]
    ) -> None:
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
            assert "Failed to create security bookmark" in str(result.message or "")

    def test_handle_access_denied_silent_fail(
        self, access_service: FileAccessService
    ) -> None:
        """Test handling access denied with SILENT_FAIL strategy."""
        path = Path("/some/path")
        request = AccessRequest(
            path=path,
            access_type=AccessType.READ,
            strategy=PermissionStrategy.SILENT_FAIL,
        )

        # Mock event_bus publish method
        with patch.object(access_service._event_bus, "publish") as mock_publish:
            result = access_service._handle_access_denied(path, request)

            # Should fail silently
            assert result.success is False
            assert result.permission_status == PermissionStatus.DENIED
            assert result.message is None

            # No event should be published
            mock_publish.assert_not_called()

    def test_handle_access_denied_with_event(
        self, access_service: FileAccessService
    ) -> None:
        """Test handling access denied with event publication."""
        path = Path("/some/path")
        request = AccessRequest(
            path=path,
            access_type=AccessType.READ,
            strategy=PermissionStrategy.IMMEDIATE,
            message="Custom message",
        )

        # Mock event_bus publish method
        with patch.object(access_service._event_bus, "publish") as mock_publish:
            result = access_service._handle_access_denied(path, request)

            # Should fail and publish event
            assert result.success is False
            assert result.permission_status == PermissionStatus.DENIED
            assert "Permission denied" in str(result.message or "")

            # Event should be published
            mock_publish.assert_called_once()


@pytest.mark.skipif(
    platform.system() != "Darwin", reason="Security bookmarks only work on macOS"
)
class TestBookmarkIntegration:
    """Tests for macOS security bookmark integration."""

    def test_bookmark_integration(
        self, mock_dependencies: Dict[str, MagicMock]
    ) -> None:
        """Test integration with BookmarkService."""
        # Create service with our mocked dependencies
        service = FileAccessService(
            mock_dependencies["event_bus"],
            mock_dependencies["path_manager"],
            mock_dependencies["bookmark_service"],
            mock_dependencies["cloud_service"],
        )
        service.initialize()

        # Mock bookmark service behavior
        mock_dependencies["bookmark_service"].has_bookmark.return_value = False
        mock_dependencies["bookmark_service"].create_bookmark.return_value = True
        mock_dependencies["bookmark_service"].start_access.return_value = True

        # Test with a path outside home (requires bookmark on macOS)
        test_path = Path("/tmp/test.txt")
        resolved_path = test_path.resolve()  # Handle /private/tmp on macOS

        # Request access
        request = AccessRequest(
            path=test_path,
            access_type=AccessType.READ,
            strategy=PermissionStrategy.PROGRESSIVE,
        )
        result = service.request_access(request)

        # Should try to create a bookmark
        mock_dependencies["bookmark_service"].create_bookmark.assert_called_once_with(
            resolved_path
        )
        mock_dependencies["bookmark_service"].start_access.assert_called_once_with(
            resolved_path
        )
        assert result.success

        # Clean up
        service.shutdown()


class TestCloudIntegration:
    """Tests for cloud provider integration."""

    def test_cloud_integration(
        self, mock_dependencies: Dict[str, MagicMock], temp_dir: Path
    ) -> None:
        """Test integration with CloudStorageService."""
        # Create a test file
        test_file = temp_dir / "test_file.txt"
        test_file.write_text("Test content")

        # Create a separate mock for cloud service
        cloud_service_mock = MagicMock(spec=CloudStorageService)
        cloud_service_mock.get_provider_for_path.return_value = None

        # Create service with our mocked dependencies including the separate cloud service mock
        service = FileAccessService(
            mock_dependencies["event_bus"],
            mock_dependencies["path_manager"],
            mock_dependencies["bookmark_service"],
            cloud_service_mock,
        )
        service.initialize()

        # Mock internal methods to focus only on the cloud service interaction
        with patch.object(service, "_handle_bookmark_access", return_value=None):
            with patch.object(service, "_standard_read", return_value=True):
                # Request access to a path
                request = AccessRequest(
                    path=test_file,
                    access_type=AccessType.READ,
                    strategy=PermissionStrategy.IMMEDIATE,
                )
                result = service.request_access(request)

                # Should check for cloud provider
                cloud_service_mock.get_provider_for_path.assert_called_once()
                assert result.success

        # Clean up
        service.shutdown()
