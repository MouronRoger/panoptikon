"""Filesystem operations and monitoring for Panoptikon.

This module provides core filesystem functionality:
- FSEvents-based file monitoring with polling fallback
- Permission-aware file operations
- Cloud storage provider detection
- Security-scoped bookmark handling
- Path normalization and filtering
"""

from .bookmarks import Bookmark, BookmarkService
from .events import (
    BookmarkEvent,
    CloudProviderType,
    CloudStorageEvent,
    DirectoryLimitEvent,
    FileChangeEvent,
    FileChangeType,
    FilePermissionEvent,
    FileSystemErrorEvent,
    PermissionStatus,
    WatchedPathsChangedEvent,
)
from .paths import PathManager, PathMatchType, PathRule, PathRuleSet
from .watcher import (
    FileSystemWatchService,
    FSEventsWatcher,
    PollingWatcher,
    WatcherType,
)

__all__ = [
    # Event types
    "FileChangeType",
    "PermissionStatus",
    "CloudProviderType",
    # Events
    "FileChangeEvent",
    "FilePermissionEvent",
    "CloudStorageEvent",
    "FileSystemErrorEvent",
    "DirectoryLimitEvent",
    "BookmarkEvent",
    "WatchedPathsChangedEvent",
    # Path management
    "PathManager",
    "PathMatchType",
    "PathRule",
    "PathRuleSet",
    # File system watching
    "FileSystemWatchService",
    "FSEventsWatcher",
    "PollingWatcher",
    "WatcherType",
    # Bookmarks
    "Bookmark",
    "BookmarkService",
]
