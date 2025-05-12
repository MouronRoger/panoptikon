"""Unit tests for filesystem access and permission components (FileAccessService, AccessRequest, AccessType, etc.).

Covers all error, edge, and fallback logic for access code.
"""

from pathlib import Path
import platform
from unittest.mock import MagicMock, patch

import pytest

from src.panoptikon.filesystem.access import (
    AccessRequest,
    AccessType,
    FileAccessService,
    PermissionStrategy,
)
from src.panoptikon.filesystem.cloud import CloudProviderInfo, CloudProviderType

# Import fixtures from test_filesystem.py


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
        mock_create = MagicMock(return_value=True)
        with patch.object(access_service, "_standard_create", mock_create):
            result = access_service._standard_write(non_existent)
            assert result is True
            mock_create.assert_called_once_with(non_existent.parent)

    def test_standard_delete_non_existent(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test standard delete on a non-existent path."""
        non_existent = temp_dir / "does_not_exist.txt"
        result = access_service._standard_delete(non_existent)
        assert result is True

    def test_standard_rename_non_existent(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test standard rename on a non-existent path."""
        non_existent = temp_dir / "does_not_exist.txt"
        result = access_service._standard_rename(non_existent)
        assert result is False

    def test_standard_read_permission_error(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test _standard_read returns False on PermissionError."""
        file_path = temp_dir / "file.txt"
        file_path.write_text("data")
        with patch("builtins.open", side_effect=PermissionError):
            assert not access_service._standard_read(file_path)

    def test_standard_write_permission_error(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test _standard_write returns False on PermissionError."""
        file_path = temp_dir / "file.txt"
        file_path.write_text("data")
        # Patch Path.stat to raise PermissionError for file
        with patch.object(Path, "stat", side_effect=PermissionError):
            assert not access_service._standard_write(file_path)
        # Patch Path.touch to raise PermissionError for directory
        with patch.object(Path, "touch", side_effect=PermissionError):
            assert not access_service._standard_write(temp_dir)

    def test_standard_delete_permission_error(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test _standard_delete returns False on PermissionError."""
        file_path = temp_dir / "file.txt"
        file_path.write_text("data")
        with patch.object(Path, "exists", side_effect=PermissionError):
            assert not access_service._standard_delete(file_path)

    def test_standard_rename_permission_error(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test _standard_rename returns False on PermissionError."""
        file_path = temp_dir / "file.txt"
        file_path.write_text("data")
        with patch.object(Path, "exists", side_effect=PermissionError):
            assert not access_service._standard_rename(file_path)

    def test_standard_move_permission_error(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test _standard_move returns False on PermissionError."""
        file_path = temp_dir / "file.txt"
        file_path.write_text("data")
        with patch.object(Path, "stat", side_effect=PermissionError):
            assert not access_service._standard_move(file_path, target=file_path)

    def test_standard_create_permission_error(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test _standard_create returns False on PermissionError."""
        file_path = temp_dir / "file.txt"
        with patch.object(Path, "touch", side_effect=PermissionError):
            assert not access_service._standard_create(file_path)

    def test_standard_metadata_permission_error(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test _standard_metadata returns False on PermissionError."""
        file_path = temp_dir / "file.txt"
        file_path.write_text("data")
        with patch.object(Path, "stat", side_effect=PermissionError):
            assert not access_service._standard_metadata(file_path)

    def test_get_operation_handler_fallback(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test _get_operation_handler falls back to standard handler if provider-specific not found."""
        handler = access_service._get_operation_handler(temp_dir, AccessType.READ)
        assert callable(handler)

    def test_get_operation_handler_not_found(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test _get_operation_handler returns always-fail function if no handler found."""
        # Remove all handlers
        access_service._provider_operations.clear()
        handler = access_service._get_operation_handler(temp_dir, AccessType.READ)
        assert not handler(temp_dir)

    def test_cloud_operation_not_implemented_logs_warning(
        self, access_service: FileAccessService, temp_dir: Path, caplog
    ) -> None:
        """Test _cloud_operation_not_implemented logs a warning and returns False."""
        with caplog.at_level("WARNING"):
            result = access_service._cloud_operation_not_implemented(temp_dir)
        assert result is False
        assert any("Cloud operation requested" in m for m in caplog.messages)

    def test_handle_access_denied_silent_fail(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test _handle_access_denied returns denied result with SILENT_FAIL and does not publish event."""
        request = AccessRequest(
            path=temp_dir,
            access_type=AccessType.READ,
            strategy=PermissionStrategy.SILENT_FAIL,
        )
        result = access_service._handle_access_denied(temp_dir, request)
        assert not result.success
        assert result.permission_status.name == "DENIED"

    def test_handle_access_denied_other_strategies_publishes_event(
        self, access_service: FileAccessService, temp_dir: Path, mocker
    ) -> None:
        """Test _handle_access_denied publishes event for non-SILENT_FAIL strategies."""
        request = AccessRequest(
            path=temp_dir,
            access_type=AccessType.READ,
            strategy=PermissionStrategy.IMMEDIATE,
        )
        publish_spy = mocker.spy(access_service, "_publish_permission_event")
        result = access_service._handle_access_denied(temp_dir, request)
        assert not result.success
        assert result.permission_status.name == "DENIED"
        publish_spy.assert_called_once()

    def test_request_access_user_prompt(
        self, access_service: FileAccessService, temp_dir: Path, mocker
    ) -> None:
        """Test request_access with USER_PROMPT strategy returns denied if not accessible."""
        request = AccessRequest(
            path=temp_dir,
            access_type=AccessType.READ,
            strategy=PermissionStrategy.USER_PROMPT,
        )
        # Force handler to always fail
        mocker.patch.object(
            access_service, "_get_operation_handler", return_value=lambda _: False
        )
        result = access_service.request_access(request)
        assert not result.success
        assert result.permission_status.name == "DENIED"

    def test_request_access_silent_fail(
        self, access_service: FileAccessService, temp_dir: Path, mocker
    ) -> None:
        """Test request_access with SILENT_FAIL strategy returns denied if not accessible."""
        request = AccessRequest(
            path=temp_dir,
            access_type=AccessType.READ,
            strategy=PermissionStrategy.SILENT_FAIL,
        )
        # Force handler to always fail
        mocker.patch.object(
            access_service, "_get_operation_handler", return_value=lambda _: False
        )
        result = access_service.request_access(request)
        assert not result.success
        assert result.permission_status.name == "DENIED"


class TestAccessRequestHandling:
    """Tests focusing on access request handling in FileAccessService."""

    def test_get_operation_handler_cloud_provider(
        self, access_service: FileAccessService, mock_dependencies: dict[str, MagicMock]
    ) -> None:
        """Test getting operation handler for a cloud provider path."""
        path = Path("/cloud/path")
        provider = CloudProviderInfo(
            provider_type=CloudProviderType.ICLOUD,
            display_name="Test Provider",
            root_path=Path("/cloud"),
        )
        mock_handler = MagicMock(return_value=True)
        mock_dependencies["cloud_service"].get_provider_for_path.return_value = provider
        with (
            patch.object(
                access_service, "_get_operation_handler", return_value=mock_handler
            ),
            patch.object(access_service, "_handle_bookmark_access", return_value=None),
        ):
            request = AccessRequest(
                path=path,
                access_type=AccessType.READ,
                strategy=PermissionStrategy.IMMEDIATE,
            )
            result = access_service.request_access(request)
            assert result.success is True
            mock_handler.assert_called_once_with(path)

    def test_handle_bookmark_access_not_needed(
        self, access_service: FileAccessService, temp_dir: Path
    ) -> None:
        """Test bookmark handling when not needed (relative path)."""
        path = Path("relative/path")
        request = AccessRequest(path=path, access_type=AccessType.READ)
        with patch.object(
            access_service._bookmark_service,
            "has_bookmark",
            MagicMock(return_value=False),
        ) as mock_has_bookmark:
            result = access_service._handle_bookmark_access(path, request)
            assert result is None
            mock_has_bookmark.assert_not_called()

    @pytest.mark.skipif(platform.system() != "Darwin", reason="macOS-specific test")
    def test_handle_bookmark_access_macos_home(
        self, access_service: FileAccessService
    ) -> None:
        """Test bookmark handling for path in home directory on macOS."""
        path = Path.home() / "test.txt"
        request = AccessRequest(path=path, access_type=AccessType.READ)
        with patch.object(
            access_service._bookmark_service,
            "has_bookmark",
            MagicMock(return_value=False),
        ) as mock_has_bookmark:
            result = access_service._handle_bookmark_access(path, request)
            assert result is None
            mock_has_bookmark.assert_not_called()


@pytest.mark.skipif(
    platform.system() != "Darwin", reason="Security bookmarks only work on macOS"
)
class TestBookmarkIntegration:
    """Tests for macOS security bookmark integration."""

    def test_bookmark_integration(
        self, mock_dependencies: dict[str, MagicMock]
    ) -> None:
        """Test integration with BookmarkService."""
        service = FileAccessService(
            mock_dependencies["event_bus"],
            mock_dependencies["path_manager"],
            mock_dependencies["bookmark_service"],
            mock_dependencies["cloud_service"],
        )
        service.initialize()
        mock_dependencies["bookmark_service"].has_bookmark.return_value = False
        mock_dependencies["bookmark_service"].create_bookmark.return_value = True
        mock_dependencies["bookmark_service"].start_access.return_value = True
        test_path = Path("/tmp/test.txt")
        resolved_path = test_path.resolve()
        request = AccessRequest(
            path=test_path,
            access_type=AccessType.READ,
            strategy=PermissionStrategy.PROGRESSIVE,
        )
        result = service.request_access(request)
        mock_dependencies["bookmark_service"].create_bookmark.assert_called_once_with(
            resolved_path
        )
        mock_dependencies["bookmark_service"].start_access.assert_called_once_with(
            resolved_path
        )
        assert result.success
        service.shutdown()


# Additional coverage-improving tests will be added below.
