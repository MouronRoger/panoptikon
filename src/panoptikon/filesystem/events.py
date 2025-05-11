"""Events related to filesystem operations and monitoring.

This module defines events that are emitted during filesystem operations
and monitoring activities.
"""

from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, Optional, Set

from ..core.events import EventBase


class FileChangeType(Enum):
    """Type of file change that occurred."""

    CREATED = auto()
    MODIFIED = auto()
    DELETED = auto()
    RENAMED = auto()
    ATTRIBUTE_MODIFIED = auto()
    UNKNOWN = auto()


class PermissionStatus(Enum):
    """Status of a permission request."""

    GRANTED = auto()
    DENIED = auto()
    PENDING = auto()


class CloudProviderType(Enum):
    """Types of cloud storage providers."""

    ICLOUD = auto()
    DROPBOX = auto()
    ONEDRIVE = auto()
    GOOGLE_DRIVE = auto()
    BOX = auto()
    UNKNOWN = auto()


class FileSystemEvent(EventBase):
    """Base event for all filesystem-related events."""

    def __init__(self, path: Path) -> None:
        """Initialize a filesystem event.

        Args:
            path: Path that this event relates to.
        """
        super().__init__()
        self.path = path

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation.

        Returns:
            Dictionary representation of the event.
        """
        result = super().to_dict()
        result.update({"path": str(self.path)})
        return result


class FileChangeEvent(FileSystemEvent):
    """Event emitted when a file changes."""

    def __init__(
        self, path: Path, change_type: FileChangeType, old_path: Optional[Path] = None
    ) -> None:
        """Initialize a file change event.

        Args:
            path: Path that changed.
            change_type: Type of change that occurred.
            old_path: Previous path (for renames).
        """
        super().__init__(path)
        self.change_type = change_type
        self.old_path = old_path

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation.

        Returns:
            Dictionary representation of the event.
        """
        result = super().to_dict()
        result.update({"change_type": self.change_type.name})
        if self.old_path:
            result["old_path"] = str(self.old_path)
        return result


class FilePermissionEvent(FileSystemEvent):
    """Event emitted when file permissions change."""

    def __init__(
        self, path: Path, status: PermissionStatus, message: Optional[str] = None
    ) -> None:
        """Initialize a file permission event.

        Args:
            path: Path that had a permission change.
            status: New permission status.
            message: Optional status message.
        """
        super().__init__(path)
        self.status = status
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation.

        Returns:
            Dictionary representation of the event.
        """
        result = super().to_dict()
        result.update({"status": self.status.name})
        if self.message:
            result["message"] = self.message
        return result


class CloudStorageEvent(FileSystemEvent):
    """Event emitted for cloud storage related operations."""

    def __init__(
        self,
        path: Path,
        provider: CloudProviderType,
        online: bool = True,
        sync_status: Optional[str] = None,
    ) -> None:
        """Initialize a cloud storage event.

        Args:
            path: Path related to cloud storage.
            provider: Cloud provider type.
            online: Whether the provider is online.
            sync_status: Sync status message if available.
        """
        super().__init__(path)
        self.provider = provider
        self.online = online
        self.sync_status = sync_status

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation.

        Returns:
            Dictionary representation of the event.
        """
        result = super().to_dict()
        result.update(
            {
                "provider": self.provider.name,
                "online": self.online,
            }
        )
        if self.sync_status:
            result["sync_status"] = self.sync_status
        return result


class FileSystemErrorEvent(FileSystemEvent):
    """Event emitted when a filesystem error occurs."""

    def __init__(
        self,
        path: Path,
        error_type: str,
        message: str,
        error_code: Optional[int] = None,
    ) -> None:
        """Initialize a filesystem error event.

        Args:
            path: Path where error occurred.
            error_type: Type of error.
            message: Error message.
            error_code: Optional error code.
        """
        super().__init__(path)
        self.error_type = error_type
        self.message = message
        self.error_code = error_code

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation.

        Returns:
            Dictionary representation of the event.
        """
        result = super().to_dict()
        result.update(
            {
                "error_type": self.error_type,
                "message": self.message,
            }
        )
        if self.error_code is not None:
            result["error_code"] = self.error_code
        return result


class DirectoryLimitEvent(FileSystemEvent):
    """Event emitted when a directory size or file count limit is hit."""

    def __init__(
        self, path: Path, file_count: int, total_size: int, limit_reached: bool = False
    ) -> None:
        """Initialize a directory limit event.

        Args:
            path: Directory path.
            file_count: Number of files.
            total_size: Total size in bytes.
            limit_reached: Whether a limit was reached.
        """
        super().__init__(path)
        self.file_count = file_count
        self.total_size = total_size
        self.limit_reached = limit_reached

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation.

        Returns:
            Dictionary representation of the event.
        """
        result = super().to_dict()
        result.update(
            {
                "file_count": self.file_count,
                "total_size": self.total_size,
                "limit_reached": self.limit_reached,
            }
        )
        return result


class BookmarkEvent(FileSystemEvent):
    """Event emitted for bookmark-related operations."""

    def __init__(
        self,
        path: Path,
        created: bool = False,
        valid: bool = True,
        error: Optional[str] = None,
    ) -> None:
        """Initialize a bookmark event.

        Args:
            path: Bookmarked path.
            created: Whether a bookmark was created.
            valid: Whether the bookmark is valid.
            error: Optional error message.
        """
        super().__init__(path)
        self.created = created
        self.valid = valid
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation.

        Returns:
            Dictionary representation of the event.
        """
        result = super().to_dict()
        result.update(
            {
                "created": self.created,
                "valid": self.valid,
            }
        )
        if self.error:
            result["error"] = self.error
        return result


class WatchedPathsChangedEvent(EventBase):
    """Event emitted when the set of watched paths changes."""

    def __init__(
        self,
        added_paths: Optional[Set[Path]] = None,
        removed_paths: Optional[Set[Path]] = None,
    ) -> None:
        """Initialize a watched paths changed event.

        Args:
            added_paths: Set of paths added to watch.
            removed_paths: Set of paths removed from watch.
        """
        super().__init__()
        self.added_paths = added_paths or set()
        self.removed_paths = removed_paths or set()

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation.

        Returns:
            Dictionary representation of the event.
        """
        result = super().to_dict()
        result.update(
            {
                "added_paths": [str(p) for p in self.added_paths],
                "removed_paths": [str(p) for p in self.removed_paths],
            }
        )
        return result
