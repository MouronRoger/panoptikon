"""Cloud storage provider detection and handling.

This module provides functionality to detect and interact with cloud storage providers:
- Cloud provider identification (iCloud, Dropbox, OneDrive, Google Drive, Box)
- Provider-agnostic detection mechanisms
- Offline status detection and handling
"""

from pathlib import Path
import platform
from typing import Optional

from pydantic import BaseModel, Field

from ..core.events import EventBus
from ..core.service import ServiceInterface
from .events import CloudProviderType, CloudStorageEvent
from .paths import PathManager


class CloudProviderInfo(BaseModel):
    """Information about a cloud storage provider."""

    provider_type: CloudProviderType
    display_name: str
    root_path: Path
    marker_files: list[str] = Field(default_factory=list)
    marker_folders: list[str] = Field(default_factory=list)
    regex_patterns: list[str] = Field(default_factory=list)
    online: bool = True
    sync_status: Optional[str] = None


class CloudProviderDetector:
    """Detect cloud storage providers and their status."""

    def __init__(self) -> None:
        """Initialize the cloud provider detector."""
        self._providers: dict[CloudProviderType, CloudProviderInfo] = {}
        self._provider_roots: set[Path] = set()
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize known cloud providers based on the current platform."""
        system = platform.system()

        if system == "Darwin":  # macOS
            home = Path.home()
            # iCloud Drive
            icloud_path = home / "Library" / "Mobile Documents" / "com~apple~CloudDocs"
            if icloud_path.exists():
                self._add_provider(
                    CloudProviderType.ICLOUD,
                    "iCloud Drive",
                    icloud_path,
                    marker_files=[".icloud"],
                    marker_folders=["com~apple~CloudDocs"],
                )

            # Dropbox
            dropbox_path = home / "Dropbox"
            if dropbox_path.exists():
                self._add_provider(
                    CloudProviderType.DROPBOX,
                    "Dropbox",
                    dropbox_path,
                    marker_files=[".dropbox"],
                    marker_folders=[".dropbox.cache"],
                )

            # OneDrive
            onedrive_path = home / "OneDrive"
            if onedrive_path.exists():
                self._add_provider(
                    CloudProviderType.ONEDRIVE,
                    "OneDrive",
                    onedrive_path,
                    marker_files=[".onedriveconfig"],
                    regex_patterns=[r"\.~lock\..*#$"],
                )

            # Google Drive
            gdrive_path = home / "Google Drive"
            gdrive_new_path = home / "GoogleDrive"
            gdrive_backup_path = home / "Google Drive File Stream"

            if gdrive_path.exists():
                self._add_provider(
                    CloudProviderType.GOOGLE_DRIVE,
                    "Google Drive",
                    gdrive_path,
                    marker_folders=[".tmp.drivedownload"],
                )
            elif gdrive_new_path.exists():
                self._add_provider(
                    CloudProviderType.GOOGLE_DRIVE,
                    "Google Drive",
                    gdrive_new_path,
                    marker_folders=[".tmp.drivedownload"],
                )
            elif gdrive_backup_path.exists():
                self._add_provider(
                    CloudProviderType.GOOGLE_DRIVE,
                    "Google Drive",
                    gdrive_backup_path,
                    marker_folders=[".tmp.drivedownload"],
                )

            # Box
            box_path = home / "Box"
            box_sync_path = home / "Box Sync"

            if box_path.exists():
                self._add_provider(
                    CloudProviderType.BOX,
                    "Box",
                    box_path,
                    marker_files=[".boxsyncconfig"],
                )
            elif box_sync_path.exists():
                self._add_provider(
                    CloudProviderType.BOX,
                    "Box",
                    box_sync_path,
                    marker_files=[".boxsyncconfig"],
                )

        # Similar implementation for Windows and Linux would go here
        # with appropriate paths and detection methods

    def _add_provider(
        self,
        provider_type: CloudProviderType,
        display_name: str,
        root_path: Path,
        marker_files: Optional[list[str]] = None,
        marker_folders: Optional[list[str]] = None,
        regex_patterns: Optional[list[str]] = None,
    ) -> None:
        """Add a cloud provider to the known providers list.

        Args:
            provider_type: Type of cloud provider.
            display_name: Human-readable name.
            root_path: Root path of the provider.
            marker_files: Files that identify this provider.
            marker_folders: Folders that identify this provider.
            regex_patterns: Regex patterns that identify this provider.
        """
        self._providers[provider_type] = CloudProviderInfo(
            provider_type=provider_type,
            display_name=display_name,
            root_path=root_path,
            marker_files=marker_files or [],
            marker_folders=marker_folders or [],
            regex_patterns=regex_patterns or [],
            online=self._check_provider_online(root_path),
        )
        self._provider_roots.add(root_path)

    def _check_provider_online(self, path: Path) -> bool:
        """Check if a cloud provider appears to be online.

        Args:
            path: Root path of the provider.

        Returns:
            True if provider appears online, False otherwise.
        """
        # Basic check: can we access the directory and are there files?
        try:
            # Check if directory is accessible
            if not path.exists() or not path.is_dir():
                return False

            # Check if we can list contents
            next(path.iterdir(), None)
            return True
        except (PermissionError, OSError):
            return False

    def detect_provider(self, path: Path) -> Optional[CloudProviderInfo]:
        """Detect the cloud provider for a given path.

        Args:
            path: Path to check.

        Returns:
            CloudProviderInfo if a provider is detected, None otherwise.
        """
        path = path.resolve()

        # For all providers, normalize paths for comparison
        for provider in self._providers.values():
            # Try different ways to match the path
            provider_root = provider.root_path.resolve()

            # Direct equality check
            if path == provider_root:
                return provider

            # Check if path starts with provider root
            path_str = str(path)
            root_str = str(provider_root)
            if path_str.startswith(root_str + "/"):
                return provider

            # On macOS, check for /private prefix difference
            if platform.system() == "Darwin":
                if path_str.startswith("/private"):
                    # Remove /private prefix for comparison
                    non_private_path = path_str.replace("/private", "", 1)
                    non_private_root = root_str.replace("/private", "", 1)
                    if non_private_path.startswith(non_private_root):
                        return provider
                else:
                    # Add /private prefix for comparison
                    private_path = "/private" + path_str
                    private_root = "/private" + root_str
                    if private_path.startswith(private_root):
                        return provider

        return None

    def get_all_providers(self) -> list[CloudProviderInfo]:
        """Get information about all detected cloud providers.

        Returns:
            List of cloud provider information.
        """
        return list(self._providers.values())

    def refresh_provider_status(self) -> list[tuple[CloudProviderType, bool]]:
        """Refresh the online status of all providers.

        Returns:
            List of provider types and their online status.
        """
        result = []

        for provider_type, provider in self._providers.items():
            previous_status = provider.online
            current_status = self._check_provider_online(provider.root_path)

            if previous_status != current_status:
                provider.online = current_status
                result.append((provider_type, current_status))

        return result


class CloudStorageService(ServiceInterface):
    """Service for managing cloud storage detection and status."""

    def __init__(self, event_bus: EventBus, path_manager: PathManager) -> None:
        """Initialize the cloud storage service.

        Args:
            event_bus: Event bus for publishing events.
            path_manager: Path manager for path operations.
        """
        self._event_bus = event_bus
        self._path_manager = path_manager
        self._detector = CloudProviderDetector()
        self._path_provider_cache: dict[str, Optional[CloudProviderInfo]] = {}
        self._max_cache_size = 1000

    def initialize(self) -> None:
        """Initialize the service."""
        # Publish initial events for detected providers
        for provider in self._detector.get_all_providers():
            self._publish_cloud_event(provider)

    def shutdown(self) -> None:
        """Shut down the service."""
        self._path_provider_cache.clear()

    def get_provider_for_path(self, path: Path) -> Optional[CloudProviderInfo]:
        """Get the cloud provider for a path, if any.

        Args:
            path: Path to check.

        Returns:
            CloudProviderInfo if path is in cloud storage, None otherwise.
        """
        path_str = str(path.resolve())

        # Check cache first
        if path_str in self._path_provider_cache:
            return self._path_provider_cache[path_str]

        # Detect provider and cache result
        provider = self._detector.detect_provider(path)

        # Manage cache size
        if len(self._path_provider_cache) >= self._max_cache_size:
            # Simple approach: clear the whole cache when it gets too big
            self._path_provider_cache.clear()

        self._path_provider_cache[path_str] = provider
        return provider

    def is_cloud_path(self, path: Path) -> bool:
        """Check if a path is on cloud storage.

        Args:
            path: Path to check.

        Returns:
            True if path is on cloud storage, False otherwise.
        """
        return self.get_provider_for_path(path) is not None

    def get_provider_type(self, path: Path) -> CloudProviderType:
        """Get the cloud provider type for a path.

        Args:
            path: Path to check.

        Returns:
            Cloud provider type, or UNKNOWN if not on cloud storage.
        """
        provider = self.get_provider_for_path(path)
        if provider is None:
            return CloudProviderType.UNKNOWN
        return provider.provider_type

    def is_provider_online(self, provider_type: CloudProviderType) -> bool:
        """Check if a cloud provider is online.

        Args:
            provider_type: Provider to check.

        Returns:
            True if provider is online, False otherwise.
        """
        providers = self._detector.get_all_providers()
        for provider in providers:
            if provider.provider_type == provider_type:
                return provider.online
        return False

    def refresh_provider_status(self) -> None:
        """Refresh the status of all cloud providers and publish events for changes."""
        status_changes = self._detector.refresh_provider_status()

        for provider_type, _online in status_changes:
            # Find the provider from the detector
            for provider in self._detector.get_all_providers():
                if provider.provider_type == provider_type:
                    self._publish_cloud_event(provider)
                    break

    def get_all_providers(self) -> list[CloudProviderInfo]:
        """Get information about all detected cloud providers.

        Returns:
            List of provider information.
        """
        return self._detector.get_all_providers()

    def _publish_cloud_event(self, provider: CloudProviderInfo) -> None:
        """Publish a cloud storage event.

        Args:
            provider: Provider information.
        """
        event = CloudStorageEvent(
            path=provider.root_path,
            provider=provider.provider_type,
            online=provider.online,
            sync_status=provider.sync_status,
        )
        self._event_bus.publish(event)
