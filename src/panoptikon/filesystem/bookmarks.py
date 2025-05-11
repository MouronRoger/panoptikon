"""Security-scoped bookmarks for macOS.

This module provides utilities for creating, storing, and using security-scoped
bookmarks, which allow sandboxed applications to retain access to user-selected
files and directories between launches.
"""

from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
import platform
from typing import Optional

from ..core.events import EventBus
from ..core.service import ServiceInterface
from .events import BookmarkEvent

logger = logging.getLogger(__name__)

# Check if we're on macOS and can use the macOS-specific APIs
try:
    if platform.system() == "Darwin":
        import Foundation  # type: ignore
        import objc  # type: ignore

        MACOS_APIS_AVAILABLE = True
    else:
        MACOS_APIS_AVAILABLE = False
except ImportError:
    MACOS_APIS_AVAILABLE = False


@dataclass
class Bookmark:
    """Represents a security-scoped bookmark to a file or directory."""

    path: Path
    bookmark_data: bytes
    created_at: datetime
    last_accessed: datetime
    is_valid: bool = True
    access_count: int = 0


class BookmarkService(ServiceInterface):
    """Service for managing security-scoped bookmarks."""

    def __init__(self, event_bus: EventBus) -> None:
        """Initialize the bookmark service.

        Args:
            event_bus: Event bus to publish events to.
        """
        self._event_bus = event_bus
        self._bookmarks: dict[Path, Bookmark] = {}
        self._active_scopes: dict[Path, int] = {}  # Path -> reference count
        self._bookmark_storage_path: Optional[Path] = None

    def initialize(self) -> None:
        """Initialize the service."""
        if not MACOS_APIS_AVAILABLE:
            logger.warning("Security-scoped bookmarks not available on this platform")
            return

        # Set up storage directory for bookmarks
        app_data_dir = Path.home() / "Library" / "Application Support" / "Panoptikon"
        self._bookmark_storage_path = app_data_dir / "bookmarks"
        self._bookmark_storage_path.mkdir(parents=True, exist_ok=True)

        # Load any existing bookmarks
        self._load_bookmarks()
        logger.debug("BookmarkService initialized")

    def shutdown(self) -> None:
        """Shut down the service."""
        # Stop access to all active bookmarks
        for path in list(self._active_scopes.keys()):
            self.stop_access(path)
        self._bookmarks.clear()
        logger.debug("BookmarkService shut down")

    def create_bookmark(self, path: Path) -> bool:
        """Create a new security-scoped bookmark.

        Args:
            path: Path to create a bookmark for.

        Returns:
            True if bookmark was created successfully, False otherwise.
        """
        if not MACOS_APIS_AVAILABLE:
            logger.warning("Security-scoped bookmarks not available on this platform")
            return False

        if path in self._bookmarks:
            logger.debug(f"Bookmark already exists for {path}")
            return True

        try:
            path = path.resolve()
            url = Foundation.NSURL.fileURLWithPath_(str(path))
            bookmark_data, error = (
                url.bookmarkDataWithOptions_includingResourceValuesForKeys_relativeToURL_error_(
                    Foundation.NSURLBookmarkCreationWithSecurityScope,
                    None,
                    None,
                    None,
                )
            )

            if error:
                error_info = error.localizedDescription()
                logger.error(f"Failed to create bookmark for {path}: {error_info}")
                self._event_bus.publish(
                    BookmarkEvent(
                        path=path, created=False, valid=False, error=str(error_info)
                    )
                )
                return False

            # Store the bookmark
            now = datetime.now()
            bookmark = Bookmark(
                path=path,
                bookmark_data=bytes(bookmark_data),
                created_at=now,
                last_accessed=now,
            )
            self._bookmarks[path] = bookmark

            # Save to disk
            self._save_bookmark(bookmark)

            # Publish event
            self._event_bus.publish(BookmarkEvent(path=path, created=True))
            logger.debug(f"Created bookmark for {path}")
            return True
        except Exception as e:
            logger.error(f"Error creating bookmark for {path}: {e}")
            self._event_bus.publish(
                BookmarkEvent(path=path, created=False, valid=False, error=str(e))
            )
            return False

    def start_access(self, path: Path) -> bool:
        """Start accessing a bookmarked path.

        Args:
            path: Path to access.

        Returns:
            True if access was started successfully, False otherwise.
        """
        if not MACOS_APIS_AVAILABLE:
            # Non-macOS platforms don't need security-scoped access
            return True

        path = path.resolve()
        if path not in self._bookmarks:
            logger.error(f"No bookmark exists for {path}")
            return False

        # If already accessing, just increment reference count
        if path in self._active_scopes:
            self._active_scopes[path] += 1
            return True

        bookmark = self._bookmarks[path]
        try:
            url = Foundation.NSURL.URLByResolvingBookmarkData_options_relativeToURL_bookmarkDataIsStale_error_(
                Foundation.NSData.dataWithBytes_length_(
                    bookmark.bookmark_data,
                    len(bookmark.bookmark_data),
                ),
                Foundation.NSURLBookmarkResolutionWithSecurityScope,
                None,
                objc.NULL,
                None,
            )

            if not url:
                logger.error(f"Failed to resolve bookmark for {path}")
                bookmark.is_valid = False
                self._event_bus.publish(
                    BookmarkEvent(
                        path=path, valid=False, error="Failed to resolve bookmark"
                    )
                )
                return False

            # Start accessing
            success = url.startAccessingSecurityScopedResource()
            if not success:
                logger.error(f"Failed to start accessing {path}")
                self._event_bus.publish(
                    BookmarkEvent(
                        path=path, valid=False, error="Failed to start accessing"
                    )
                )
                return False

            # Update bookmark
            bookmark.last_accessed = datetime.now()
            bookmark.access_count += 1
            self._active_scopes[path] = 1

            logger.debug(f"Started accessing {path}")
            return True
        except Exception as e:
            logger.error(f"Error starting access to {path}: {e}")
            bookmark.is_valid = False
            self._event_bus.publish(BookmarkEvent(path=path, valid=False, error=str(e)))
            return False

    def stop_access(self, path: Path) -> None:
        """Stop accessing a bookmarked path.

        Args:
            path: Path to stop accessing.
        """
        if not MACOS_APIS_AVAILABLE:
            return

        path = path.resolve()
        if path not in self._active_scopes:
            logger.debug(f"Not currently accessing {path}")
            return

        # Decrement reference count
        self._active_scopes[path] -= 1
        if self._active_scopes[path] > 0:
            # Still being accessed elsewhere
            return

        # Stop accessing
        try:
            url = Foundation.NSURL.fileURLWithPath_(str(path))
            url.stopAccessingSecurityScopedResource()
            del self._active_scopes[path]
            logger.debug(f"Stopped accessing {path}")
        except Exception as e:
            logger.error(f"Error stopping access to {path}: {e}")
        finally:
            # Even if stopping access fails, remove from active scopes
            self._active_scopes.pop(path, None)

    def has_bookmark(self, path: Path) -> bool:
        """Check if a bookmark exists for a path.

        Args:
            path: Path to check.

        Returns:
            True if a bookmark exists, False otherwise.
        """
        return path.resolve() in self._bookmarks

    def is_valid(self, path: Path) -> bool:
        """Check if a bookmark is valid.

        Args:
            path: Path to check.

        Returns:
            True if the bookmark is valid, False otherwise.
        """
        path = path.resolve()
        if path not in self._bookmarks:
            return False
        return self._bookmarks[path].is_valid

    def get_bookmarked_paths(self) -> set[Path]:
        """Get all paths with bookmarks.

        Returns:
            Set of paths with bookmarks.
        """
        return set(self._bookmarks.keys())

    def remove_bookmark(self, path: Path) -> bool:
        """Remove a bookmark.

        Args:
            path: Path to remove bookmark for.

        Returns:
            True if the bookmark was removed, False otherwise.
        """
        path = path.resolve()
        if path not in self._bookmarks:
            return False

        # Stop access if active
        if path in self._active_scopes:
            self.stop_access(path)

        # Remove bookmark
        self._bookmarks.pop(path)

        # Remove from disk
        if self._bookmark_storage_path:
            bookmark_file = (
                self._bookmark_storage_path / f"{self._path_to_filename(path)}.bookmark"
            )
            if bookmark_file.exists():
                bookmark_file.unlink()

        logger.debug(f"Removed bookmark for {path}")
        return True

    def _load_bookmarks(self) -> None:
        """Load bookmarks from disk."""
        if not self._bookmark_storage_path or not self._bookmark_storage_path.exists():
            return

        for bookmark_file in self._bookmark_storage_path.glob("*.bookmark"):
            try:
                path, bookmark_data, created_at = self._read_bookmark_file(
                    bookmark_file
                )
                if path and bookmark_data:
                    # Verify the bookmark is still valid
                    is_valid = self._verify_bookmark(path, bookmark_data)

                    # Create bookmark object
                    bookmark = Bookmark(
                        path=path,
                        bookmark_data=bookmark_data,
                        created_at=created_at,
                        last_accessed=created_at,
                        is_valid=is_valid,
                    )
                    self._bookmarks[path] = bookmark

                    logger.debug(f"Loaded bookmark for {path} (valid: {is_valid})")
            except Exception as e:
                logger.error(f"Error loading bookmark from {bookmark_file}: {e}")

    def _save_bookmark(self, bookmark: Bookmark) -> bool:
        """Save a bookmark to disk.

        Args:
            bookmark: Bookmark to save.

        Returns:
            True if saved successfully, False otherwise.
        """
        if not self._bookmark_storage_path:
            return False

        try:
            bookmark_file = (
                self._bookmark_storage_path
                / f"{self._path_to_filename(bookmark.path)}.bookmark"
            )
            with open(bookmark_file, "wb") as f:
                # Write path
                path_str = str(bookmark.path)
                path_bytes = path_str.encode("utf-8")
                f.write(len(path_bytes).to_bytes(4, byteorder="little"))
                f.write(path_bytes)

                # Write created timestamp
                timestamp = int(bookmark.created_at.timestamp())
                f.write(timestamp.to_bytes(8, byteorder="little"))

                # Write bookmark data
                f.write(len(bookmark.bookmark_data).to_bytes(4, byteorder="little"))
                f.write(bookmark.bookmark_data)

            return True
        except Exception as e:
            logger.error(f"Error saving bookmark for {bookmark.path}: {e}")
            return False

    def _read_bookmark_file(
        self, bookmark_file: Path
    ) -> tuple[Optional[Path], Optional[bytes], datetime]:
        """Read a bookmark file.

        Args:
            bookmark_file: Path to bookmark file.

        Returns:
            Tuple of (path, bookmark_data, created_at).
        """
        try:
            with open(bookmark_file, "rb") as f:
                # Read path
                path_len = int.from_bytes(f.read(4), byteorder="little")
                path_bytes = f.read(path_len)
                path_str = path_bytes.decode("utf-8")
                path = Path(path_str)

                # Read created timestamp
                timestamp = int.from_bytes(f.read(8), byteorder="little")
                created_at = datetime.fromtimestamp(timestamp)

                # Read bookmark data
                data_len = int.from_bytes(f.read(4), byteorder="little")
                bookmark_data = f.read(data_len)

                return path, bookmark_data, created_at
        except Exception as e:
            logger.error(f"Error reading bookmark file {bookmark_file}: {e}")
            return None, None, datetime.now()

    def _verify_bookmark(self, path: Path, bookmark_data: bytes) -> bool:
        """Verify a bookmark is still valid.

        Args:
            path: Path the bookmark is for.
            bookmark_data: Bookmark data.

        Returns:
            True if the bookmark is valid, False otherwise.
        """
        if not MACOS_APIS_AVAILABLE:
            return False

        try:
            url, is_stale, error = (
                Foundation.NSURL.URLByResolvingBookmarkData_options_relativeToURL_bookmarkDataIsStale_error_(
                    Foundation.NSData.dataWithBytes_length_(
                        bookmark_data, len(bookmark_data)
                    ),
                    Foundation.NSURLBookmarkResolutionWithSecurityScope,
                    None,
                    None,
                    None,
                )
            )

            if error or not url:
                logger.error(
                    f"Error resolving bookmark for {path}: "
                    f"{error.localizedDescription() if error else 'Unknown error'}"
                )
                return False

            # Check if bookmark is stale
            if is_stale:
                logger.warning(f"Bookmark for {path} is stale")
                return False

            # Check if the path still exists
            if not path.exists():
                logger.warning(f"Bookmarked path {path} no longer exists")
                return False

            return True
        except Exception as e:
            logger.error(f"Error verifying bookmark for {path}: {e}")
            return False

    @staticmethod
    def _path_to_filename(path: Path) -> str:
        """Convert a path to a safe filename.

        Args:
            path: Path to convert.

        Returns:
            Safe filename.
        """
        # Replace unsafe characters
        filename = str(path).replace("/", "_").replace(":", "_")
        return filename
