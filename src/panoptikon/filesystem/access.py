"""Permission-aware file system operations.

This module provides a layer of abstraction over file system operations:
- Permission-aware file operations
- Progressive permission acquisition
- File operation delegation with provider detection
- Permission state visualization
"""

from dataclasses import dataclass
from enum import Enum, auto
import os
from pathlib import Path
import platform
import shutil
import stat
from typing import Callable, Dict, Optional, Set, Tuple, TypeVar, cast

from ..core.events import EventBus
from ..core.service import ServiceInterface
from .bookmarks import BookmarkService
from .cloud import CloudProviderInfo, CloudStorageService
from .events import FilePermissionEvent, PermissionStatus
from .paths import PathManager


class AccessType(Enum):
    """Types of file system access."""

    READ = auto()
    WRITE = auto()
    EXECUTE = auto()
    DELETE = auto()
    RENAME = auto()
    MOVE = auto()
    CREATE = auto()
    METADATA = auto()


class PermissionStrategy(Enum):
    """Strategies for acquiring permissions."""

    IMMEDIATE = auto()  # Try operation immediately, fail fast
    PROGRESSIVE = auto()  # Try operation, acquire permissions if needed, then retry
    USER_PROMPT = auto()  # Ask user for permission before trying operation
    SILENT_FAIL = auto()  # Try operation, fail silently if permission denied


@dataclass
class AccessRequest:
    """Request for file system access."""

    path: Path
    access_type: AccessType
    strategy: PermissionStrategy = PermissionStrategy.IMMEDIATE
    message: Optional[str] = None


@dataclass
class AccessResult:
    """Result of a file system access attempt."""

    success: bool
    path: Path
    access_type: AccessType
    message: Optional[str] = None
    error: Optional[Exception] = None
    permission_status: PermissionStatus = PermissionStatus.GRANTED


T = TypeVar("T")


class FileAccessService(ServiceInterface):
    """Service for permission-aware file system operations."""

    def __init__(
        self,
        event_bus: EventBus,
        path_manager: PathManager,
        bookmark_service: BookmarkService,
        cloud_service: CloudStorageService,
    ) -> None:
        """Initialize the file access service.

        Args:
            event_bus: Event bus for publishing events.
            path_manager: Path manager for path operations.
            bookmark_service: Bookmark service for handling security bookmarks.
            cloud_service: Cloud service for detecting cloud providers.
        """
        self._event_bus = event_bus
        self._path_manager = path_manager
        self._bookmark_service = bookmark_service
        self._cloud_service = cloud_service

        # Cache of paths known to be accessible
        self._accessible_paths: Dict[str, Set[AccessType]] = {}

        # Mapping of operation types to handler functions based on provider
        self._provider_operations: Dict[
            Tuple[Optional[CloudProviderInfo], AccessType], Callable
        ] = {}

    def initialize(self) -> None:
        """Initialize the service."""
        # Register default operation handlers for each provider type
        self._register_default_handlers()

    def shutdown(self) -> None:
        """Shut down the service."""
        self._accessible_paths.clear()
        self._provider_operations.clear()

    def _register_default_handlers(self) -> None:
        """Register default file operation handlers for different providers."""
        # Standard file operations apply to all provider types
        self._register_standard_operations(None)

        # Provider-specific operations would be registered here
        # For example, different implementations for cloud providers

    def _register_standard_operations(
        self, provider_info: Optional[CloudProviderInfo]
    ) -> None:
        """Register standard file operations for a provider.

        Args:
            provider_info: Provider information or None for standard operations.
        """
        # Read operations
        self._provider_operations[
            cast(
                Tuple[Optional[CloudProviderInfo], AccessType],
                (provider_info, AccessType.READ),
            )
        ] = self._standard_read

        # Write operations
        self._provider_operations[
            cast(
                Tuple[Optional[CloudProviderInfo], AccessType],
                (provider_info, AccessType.WRITE),
            )
        ] = self._standard_write

        # Delete operations
        self._provider_operations[
            cast(
                Tuple[Optional[CloudProviderInfo], AccessType],
                (provider_info, AccessType.DELETE),
            )
        ] = self._standard_delete

        # Rename operations
        self._provider_operations[
            cast(
                Tuple[Optional[CloudProviderInfo], AccessType],
                (provider_info, AccessType.RENAME),
            )
        ] = self._standard_rename

        # Move operations
        self._provider_operations[
            cast(
                Tuple[Optional[CloudProviderInfo], AccessType],
                (provider_info, AccessType.MOVE),
            )
        ] = self._standard_move

        # Create operations
        self._provider_operations[
            cast(
                Tuple[Optional[CloudProviderInfo], AccessType],
                (provider_info, AccessType.CREATE),
            )
        ] = self._standard_create

        # Metadata operations
        self._provider_operations[
            cast(
                Tuple[Optional[CloudProviderInfo], AccessType],
                (provider_info, AccessType.METADATA),
            )
        ] = self._standard_metadata

    def _standard_read(self, path: Path) -> bool:
        """Standard read operation.

        Args:
            path: Path to read.

        Returns:
            True if successful, False otherwise.
        """
        try:
            if path.is_file():
                # Test file readability by reading a bit of data
                with open(path, "rb") as f:
                    f.read(1)
            elif path.is_dir():
                # Test directory readability by listing contents
                next(path.iterdir(), None)
            return True
        except (PermissionError, OSError):
            return False

    def _standard_write(self, path: Path) -> bool:
        """Standard write operation.

        Args:
            path: Path to write to.

        Returns:
            True if successful, False otherwise.
        """
        if not path.exists():
            # If path doesn't exist, check if parent is writable
            return self._standard_create(path.parent)

        try:
            # Test file writability by checking mode
            if path.is_file():
                mode = path.stat().st_mode
                return bool(mode & stat.S_IWUSR)
            elif path.is_dir():
                # Create a temporary file to test directory writability
                temp_file = path / f".tempwrite_{os.getpid()}"
                try:
                    temp_file.touch()
                    temp_file.unlink()
                    return True
                except (PermissionError, OSError):
                    return False
            return False
        except (PermissionError, OSError):
            return False

    def _standard_delete(self, path: Path) -> bool:
        """Standard delete operation.

        Args:
            path: Path to delete.

        Returns:
            True if successful, False otherwise.
        """
        if not path.exists():
            return True  # Nothing to delete

        try:
            # Check if parent directory is writable
            parent = path.parent
            return self._standard_write(parent)
        except (PermissionError, OSError):
            return False

    def _standard_rename(self, path: Path, new_path: Optional[Path] = None) -> bool:
        """Standard rename operation.

        Args:
            path: Path to rename.
            new_path: New path after rename (for testing).

        Returns:
            True if successful, False otherwise.
        """
        if not path.exists():
            return False

        # Need write access to parent directory
        try:
            return self._standard_write(path.parent)
        except (PermissionError, OSError):
            return False

    def _standard_move(self, path: Path, target: Optional[Path] = None) -> bool:
        """Standard move operation.

        Args:
            path: Path to move.
            target: Target path (for testing).

        Returns:
            True if successful, False otherwise.
        """
        if not path.exists():
            return False

        if target is None:
            # Without a specific target, this is just a theoretical check
            return self._standard_rename(path)

        # Need write access to source and target parent directories
        try:
            return self._standard_write(path.parent) and self._standard_write(
                target.parent
            )
        except (PermissionError, OSError):
            return False

    def _standard_create(self, path: Path) -> bool:
        """Standard create operation.

        Args:
            path: Path to create.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Check if parent directory exists and is writable
            parent = path.parent
            if not parent.exists():
                return False

            # Try to create a temporary file to test writability
            temp_file = parent / f".tempcreate_{os.getpid()}"
            try:
                temp_file.touch()
                temp_file.unlink()
                return True
            except (PermissionError, OSError):
                return False
        except (PermissionError, OSError):
            return False

    def _standard_metadata(self, path: Path) -> bool:
        """Standard metadata operation.

        Args:
            path: Path to get metadata for.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Try to access metadata
            path.stat()
            return True
        except (PermissionError, OSError):
            return False

    def _get_operation_handler(
        self, path: Path, access_type: AccessType
    ) -> Callable[[Path], bool]:
        """Get the appropriate operation handler for a path.

        Args:
            path: Path to operate on.
            access_type: Type of access needed.

        Returns:
            Function that implements the operation.
        """
        # Get cloud provider for path, if any
        provider = self._cloud_service.get_provider_for_path(path)

        # Look for provider-specific handler
        key = (provider, access_type)

        if key in self._provider_operations:
            return self._provider_operations[key]

        # Fall back to standard handler if no provider-specific one
        fallback_key = (None, access_type)

        if fallback_key in self._provider_operations:
            return self._provider_operations[fallback_key]

        # If no handler found, return a function that always fails
        return lambda _: False

    def _handle_bookmark_access(
        self, path: Path, request: AccessRequest
    ) -> Optional[AccessResult]:
        """Handle security bookmark access requirements.

        Args:
            path: Resolved path.
            request: Original access request.

        Returns:
            AccessResult if bookmark handling determines the result,
            None if normal access handling should proceed.
        """
        # Check if path requires a security bookmark (on macOS, outside user's home)
        if (
            not path.is_absolute()
            or str(path).startswith(str(Path.home()))
            or platform.system() != "Darwin"
        ):
            return None

        # Path requires a bookmark, check if we have one
        if self._bookmark_service.has_bookmark(path):
            # Start accessing the bookmark
            if self._bookmark_service.start_access(path):
                return None  # Continue with normal access handling

        # Need to create a bookmark based on strategy
        if request.strategy == PermissionStrategy.IMMEDIATE:
            return AccessResult(
                success=False,
                path=path,
                access_type=request.access_type,
                message="Security bookmark required but using IMMEDIATE strategy",
                permission_status=PermissionStatus.DENIED,
            )
        elif request.strategy in (
            PermissionStrategy.PROGRESSIVE,
            PermissionStrategy.USER_PROMPT,
        ):
            # Try to create bookmark
            bookmark_result = self._bookmark_service.create_bookmark(path)
            if not bookmark_result:
                return AccessResult(
                    success=False,
                    path=path,
                    access_type=request.access_type,
                    message="Failed to create security bookmark",
                    permission_status=PermissionStatus.DENIED,
                )
            # Start accessing the bookmark
            if not self._bookmark_service.start_access(path):
                return AccessResult(
                    success=False,
                    path=path,
                    access_type=request.access_type,
                    message="Failed to access security bookmark",
                    permission_status=PermissionStatus.DENIED,
                )
            return None  # Bookmark created, continue with normal access
        else:  # SILENT_FAIL
            return AccessResult(
                success=False,
                path=path,
                access_type=request.access_type,
                permission_status=PermissionStatus.DENIED,
            )

    def request_access(self, request: AccessRequest) -> AccessResult:
        """Request access to a file system resource.

        Args:
            request: Access request details.

        Returns:
            Result of the access request.
        """
        path = request.path.resolve()

        # Check if we already know this path is accessible
        path_str = str(path)
        if (
            path_str in self._accessible_paths
            and request.access_type in self._accessible_paths[path_str]
        ):
            return AccessResult(
                success=True,
                path=path,
                access_type=request.access_type,
                permission_status=PermissionStatus.GRANTED,
            )

        # Handle security bookmark requirements if needed
        bookmark_result = self._handle_bookmark_access(path, request)
        if bookmark_result is not None:
            return bookmark_result

        # Get and run the appropriate operation handler
        handler = self._get_operation_handler(path, request.access_type)

        try:
            result = handler(path)

            if result:
                # Cache successful access
                if path_str not in self._accessible_paths:
                    self._accessible_paths[path_str] = set()
                self._accessible_paths[path_str].add(request.access_type)

                # Publish event
                self._publish_permission_event(
                    path, PermissionStatus.GRANTED, request.message
                )

                return AccessResult(
                    success=True,
                    path=path,
                    access_type=request.access_type,
                    permission_status=PermissionStatus.GRANTED,
                )
            else:
                # Handle unsuccessful access based on strategy
                return self._handle_access_denied(path, request)
        except Exception as e:
            # Handle exceptions
            return AccessResult(
                success=False,
                path=path,
                access_type=request.access_type,
                message=str(e),
                error=e,
                permission_status=PermissionStatus.DENIED,
            )

    def _handle_access_denied(self, path: Path, request: AccessRequest) -> AccessResult:
        """Handle the case where access is denied.

        Args:
            path: Path that access was denied for.
            request: Original access request.

        Returns:
            AccessResult with appropriate data based on the strategy.
        """
        if request.strategy == PermissionStrategy.SILENT_FAIL:
            return AccessResult(
                success=False,
                path=path,
                access_type=request.access_type,
                permission_status=PermissionStatus.DENIED,
            )
        else:
            # For other strategies, publish an event and return failed result
            self._publish_permission_event(
                path, PermissionStatus.DENIED, request.message
            )

            return AccessResult(
                success=False,
                path=path,
                access_type=request.access_type,
                message=f"Permission denied for {request.access_type.name} on {path}",
                permission_status=PermissionStatus.DENIED,
            )

    def _publish_permission_event(
        self, path: Path, status: PermissionStatus, message: Optional[str] = None
    ) -> None:
        """Publish a permission event.

        Args:
            path: Path that the permission applies to.
            status: Permission status.
            message: Optional message.
        """
        event = FilePermissionEvent(path=path, status=status, message=message)
        self._event_bus.publish(event)

    def can_read(
        self, path: Path, strategy: PermissionStrategy = PermissionStrategy.IMMEDIATE
    ) -> bool:
        """Check if a path can be read.

        Args:
            path: Path to check.
            strategy: Permission strategy to use.

        Returns:
            True if path can be read, False otherwise.
        """
        request = AccessRequest(
            path=path, access_type=AccessType.READ, strategy=strategy
        )
        result = self.request_access(request)
        return result.success

    def can_write(
        self, path: Path, strategy: PermissionStrategy = PermissionStrategy.IMMEDIATE
    ) -> bool:
        """Check if a path can be written to.

        Args:
            path: Path to check.
            strategy: Permission strategy to use.

        Returns:
            True if path can be written to, False otherwise.
        """
        request = AccessRequest(
            path=path, access_type=AccessType.WRITE, strategy=strategy
        )
        result = self.request_access(request)
        return result.success

    def can_delete(
        self, path: Path, strategy: PermissionStrategy = PermissionStrategy.IMMEDIATE
    ) -> bool:
        """Check if a path can be deleted.

        Args:
            path: Path to check.
            strategy: Permission strategy to use.

        Returns:
            True if path can be deleted, False otherwise.
        """
        request = AccessRequest(
            path=path, access_type=AccessType.DELETE, strategy=strategy
        )
        result = self.request_access(request)
        return result.success

    def can_create(
        self, path: Path, strategy: PermissionStrategy = PermissionStrategy.IMMEDIATE
    ) -> bool:
        """Check if a file or directory can be created at a path.

        Args:
            path: Path to check.
            strategy: Permission strategy to use.

        Returns:
            True if a file/directory can be created, False otherwise.
        """
        request = AccessRequest(
            path=path, access_type=AccessType.CREATE, strategy=strategy
        )
        result = self.request_access(request)
        return result.success

    def read_file(
        self, path: Path, strategy: PermissionStrategy = PermissionStrategy.PROGRESSIVE
    ) -> Optional[bytes]:
        """Read the contents of a file with permission handling.

        Args:
            path: Path to read.
            strategy: Permission strategy to use.

        Returns:
            File contents as bytes, or None if reading failed.
        """
        request = AccessRequest(
            path=path, access_type=AccessType.READ, strategy=strategy
        )
        result = self.request_access(request)

        if not result.success:
            return None

        try:
            with open(path, "rb") as f:
                return f.read()
        except Exception:
            return None

    def write_file(
        self,
        path: Path,
        data: bytes,
        strategy: PermissionStrategy = PermissionStrategy.PROGRESSIVE,
    ) -> bool:
        """Write data to a file with permission handling.

        Args:
            path: Path to write to.
            data: Data to write.
            strategy: Permission strategy to use.

        Returns:
            True if write was successful, False otherwise.
        """
        request = AccessRequest(
            path=path, access_type=AccessType.WRITE, strategy=strategy
        )
        result = self.request_access(request)

        if not result.success:
            return False

        try:
            with open(path, "wb") as f:
                f.write(data)
            return True
        except Exception:
            return False

    def delete_file(
        self, path: Path, strategy: PermissionStrategy = PermissionStrategy.PROGRESSIVE
    ) -> bool:
        """Delete a file with permission handling.

        Args:
            path: Path to delete.
            strategy: Permission strategy to use.

        Returns:
            True if delete was successful, False otherwise.
        """
        request = AccessRequest(
            path=path, access_type=AccessType.DELETE, strategy=strategy
        )
        result = self.request_access(request)

        if not result.success:
            return False

        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
            return True
        except Exception:
            return False

    def create_directory(
        self, path: Path, strategy: PermissionStrategy = PermissionStrategy.PROGRESSIVE
    ) -> bool:
        """Create a directory with permission handling.

        Args:
            path: Path to create.
            strategy: Permission strategy to use.

        Returns:
            True if directory creation was successful, False otherwise.
        """
        request = AccessRequest(
            path=path, access_type=AccessType.CREATE, strategy=strategy
        )
        result = self.request_access(request)

        if not result.success:
            return False

        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False

    def move_file(
        self,
        source: Path,
        target: Path,
        strategy: PermissionStrategy = PermissionStrategy.PROGRESSIVE,
    ) -> bool:
        """Move a file with permission handling.

        Args:
            source: Source path.
            target: Target path.
            strategy: Permission strategy to use.

        Returns:
            True if move was successful, False otherwise.
        """
        # Check source permission
        source_request = AccessRequest(
            path=source, access_type=AccessType.MOVE, strategy=strategy
        )
        source_result = self.request_access(source_request)

        if not source_result.success:
            return False

        # Check target permission (create permission)
        target_request = AccessRequest(
            path=target, access_type=AccessType.CREATE, strategy=strategy
        )
        target_result = self.request_access(target_request)

        if not target_result.success:
            return False

        try:
            # Handle directory moves with shutil, file moves with pathlib
            if source.is_dir():
                if target.exists() and target.is_dir():
                    shutil.rmtree(target)
                shutil.move(str(source), str(target))
            else:
                if target.exists():
                    target.unlink()
                source.rename(target)
            return True
        except Exception:
            return False
