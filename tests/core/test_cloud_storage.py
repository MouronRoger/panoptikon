"""Advanced tests for cloud storage module.

These tests focus on improving coverage for the cloud storage detection and
handling functionality.
"""

import platform
import tempfile
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

from panoptikon.filesystem.cloud import (
    CloudProviderDetector,
    CloudProviderInfo,
    CloudStorageService,
)
from panoptikon.filesystem.events import CloudProviderType, CloudStorageEvent


class TestCloudProviderDetectorAdvanced:
    """Advanced tests for CloudProviderDetector."""

    def test_initialize_providers_non_existent_paths(self) -> None:
        """Test initializing providers when paths don't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            detector = CloudProviderDetector()
            # All paths should be considered non-existent, so no providers should be added
            assert not detector._providers
            assert not detector._provider_roots

    def test_check_provider_online_exceptions(self) -> None:
        """Test check_provider_online handles exceptions gracefully."""
        detector = CloudProviderDetector()

        # Test case: Path exists but raises PermissionError when trying to list contents
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.is_dir", return_value=True):
                with patch(
                    "pathlib.Path.iterdir",
                    side_effect=PermissionError("Permission denied"),
                ):
                    assert not detector._check_provider_online(Path("/fake/path"))

        # Test case: Path exists but raises OSError
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.is_dir", return_value=True):
                with patch("pathlib.Path.iterdir", side_effect=OSError("I/O error")):
                    assert not detector._check_provider_online(Path("/fake/path"))

        # Test case: Path is not a directory
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.is_dir", return_value=False):
                assert not detector._check_provider_online(Path("/fake/path"))

    def test_detect_provider_path_variants(self) -> None:
        """Test provider detection with various path formats."""
        detector = CloudProviderDetector()

        # Mock a provider
        test_root = Path("/test/cloud/root")
        detector._providers[CloudProviderType.ICLOUD] = CloudProviderInfo(
            provider_type=CloudProviderType.ICLOUD,
            display_name="Test Cloud",
            root_path=test_root,
        )
        detector._provider_roots.add(test_root)

        # Test direct path match
        assert detector.detect_provider(test_root) is not None

        # Test subpath match
        assert detector.detect_provider(test_root / "subdir") is not None

        # Test with different path formats (resolved paths)
        with patch("pathlib.Path.resolve", return_value=test_root):
            assert detector.detect_provider(Path("/some/other/format")) is not None

    @pytest.mark.skipif(platform.system() != "Darwin", reason="macOS specific test")
    def test_detect_provider_macos_private_prefix(self) -> None:
        """Test macOS specific detection with /private prefix."""
        detector = CloudProviderDetector()

        # Create a provider with a non-private path
        test_root = Path("/tmp/cloud/root")
        detector._providers[CloudProviderType.DROPBOX] = CloudProviderInfo(
            provider_type=CloudProviderType.DROPBOX,
            display_name="Test Cloud",
            root_path=test_root,
        )
        detector._provider_roots.add(test_root)

        # Test with /private prefix
        with patch("platform.system", return_value="Darwin"):
            # Should match a path with /private prefix
            assert (
                detector.detect_provider(Path("/private/tmp/cloud/root/file.txt"))
                is not None
            )

            # Create a provider with a /private path
            private_root = Path("/private/var/cloud/root")
            detector._providers[CloudProviderType.ICLOUD] = CloudProviderInfo(
                provider_type=CloudProviderType.ICLOUD,
                display_name="Private Cloud",
                root_path=private_root,
            )
            detector._provider_roots.add(private_root)

            # Should match a path without /private prefix
            assert (
                detector.detect_provider(Path("/var/cloud/root/file.txt")) is not None
            )

    def test_refresh_provider_status(self) -> None:
        """Test refreshing provider status."""
        detector = CloudProviderDetector()

        # Add test providers
        provider1 = CloudProviderInfo(
            provider_type=CloudProviderType.ICLOUD,
            display_name="Test Cloud 1",
            root_path=Path("/test/cloud/1"),
            online=True,
        )
        provider2 = CloudProviderInfo(
            provider_type=CloudProviderType.DROPBOX,
            display_name="Test Cloud 2",
            root_path=Path("/test/cloud/2"),
            online=True,
        )

        detector._providers[CloudProviderType.ICLOUD] = provider1
        detector._providers[CloudProviderType.DROPBOX] = provider2

        # Mock check_provider_online to return False for provider1 and True for provider2
        original_check = detector._check_provider_online

        def mock_check(path: Path) -> bool:
            if path == Path("/test/cloud/1"):
                return False
            return True

        # Use monkeypatch to avoid type checking issues
        detector._check_provider_online = mock_check  # type-checking bypass for test

        # Refresh status
        status_changes = detector.refresh_provider_status()

        # Provider1 should have changed status
        assert len(status_changes) == 1
        assert status_changes[0] == (CloudProviderType.ICLOUD, False)
        assert not detector._providers[CloudProviderType.ICLOUD].online
        assert detector._providers[CloudProviderType.DROPBOX].online

        # Restore original method
        detector._check_provider_online = original_check

    def test_initialize_providers_mac_real_paths(self) -> None:
        """Test provider initialization using a real temporary home on macOS."""
        # Create a temporary home directory structure that mimics cloud layouts.
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Simulate a Dropbox folder with its marker file.
            dropbox_path = temp_path / "Dropbox"
            dropbox_path.mkdir()
            (dropbox_path / ".dropbox").touch()

            # Patch environment so the detector thinks this is the current home and
            # we are running on macOS.
            with (
                patch("pathlib.Path.home", return_value=temp_path),
                patch("platform.system", return_value="Darwin"),
            ):
                detector = CloudProviderDetector()

            providers = detector.get_all_providers()
            provider_types = {p.provider_type for p in providers}
            assert CloudProviderType.DROPBOX in provider_types

    def test_detect_provider_real_paths(self) -> None:
        """Ensure detect_provider works with real on-disk structures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create Dropbox folder and marker.
            dropbox_path = temp_path / "Dropbox"
            dropbox_path.mkdir()
            (dropbox_path / ".dropbox").touch()

            # Create a test file inside the Dropbox folder.
            test_file = dropbox_path / "test_file.txt"
            test_file.write_text("Test content")

            with (
                patch("pathlib.Path.home", return_value=temp_path),
                patch("platform.system", return_value="Darwin"),
            ):
                detector = CloudProviderDetector()

                provider = detector.detect_provider(test_file)
                assert provider is not None
                assert provider.provider_type == CloudProviderType.DROPBOX

                # A path outside any known provider should not be detected.
                outside_path = temp_path / "outside.txt"
                outside_path.write_text("Not in cloud")
                assert detector.detect_provider(outside_path) is None


class TestCloudStorageServiceAdvanced:
    """Advanced tests for CloudStorageService."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.event_bus = MagicMock()
        self.path_manager = MagicMock()
        self.service = CloudStorageService(self.event_bus, self.path_manager)

    def test_initialize_publishes_events(self) -> None:
        """Test that initialize publishes events for all providers."""
        # Mock detector to return some providers
        mock_detector = MagicMock()
        providers = [
            CloudProviderInfo(
                provider_type=CloudProviderType.ICLOUD,
                display_name="Test Cloud 1",
                root_path=Path("/test/cloud/1"),
                online=True,
            ),
            CloudProviderInfo(
                provider_type=CloudProviderType.DROPBOX,
                display_name="Test Cloud 2",
                root_path=Path("/test/cloud/2"),
                online=False,
            ),
        ]
        mock_detector.get_all_providers.return_value = providers
        self.service._detector = mock_detector

        # Initialize service
        self.service.initialize()

        # Verify events were published
        assert self.event_bus.publish.call_count == 2

        # Check the events
        events = [call[0][0] for call in self.event_bus.publish.call_args_list]

        # First event should be for ICLOUD
        assert isinstance(events[0], CloudStorageEvent)
        assert events[0].provider == CloudProviderType.ICLOUD
        assert events[0].online is True

        # Second event should be for DROPBOX
        assert isinstance(events[1], CloudStorageEvent)
        assert events[1].provider == CloudProviderType.DROPBOX
        assert events[0].online is True

    def test_get_provider_for_path_caching(self) -> None:
        """Test that get_provider_for_path caches results."""
        # Set up detector mock
        mock_detector = MagicMock()
        provider = CloudProviderInfo(
            provider_type=CloudProviderType.ICLOUD,
            display_name="Test Cloud",
            root_path=Path("/test/cloud"),
            online=True,
        )
        mock_detector.detect_provider.return_value = provider
        self.service._detector = mock_detector

        # Call get_provider_for_path twice with same path
        path = Path("/test/cloud/file.txt").resolve()
        result1 = self.service.get_provider_for_path(path)
        result2 = self.service.get_provider_for_path(path)

        # Verify results and that detector was called only once
        assert result1 is provider
        assert result2 is provider
        mock_detector.detect_provider.assert_called_once()

    def test_get_provider_for_path_cache_limit(self) -> None:
        """Test that the provider path cache is limited in size."""
        # Set up detector mock
        mock_detector = MagicMock()
        provider = CloudProviderInfo(
            provider_type=CloudProviderType.ICLOUD,
            display_name="Test Cloud",
            root_path=Path("/test/cloud"),
            online=True,
        )
        mock_detector.detect_provider.return_value = provider
        self.service._detector = mock_detector

        # Set a small cache size for testing
        self.service._max_cache_size = 3

        # Call get_provider_for_path with different paths
        for i in range(5):
            path = Path(f"/test/cloud/file{i}.txt").resolve()
            self.service.get_provider_for_path(path)

        # Cache should have been cleared at least once
        # Cache should now have <= max_cache_size entries
        assert len(self.service._path_provider_cache) <= self.service._max_cache_size

    def test_is_cloud_path(self) -> None:
        """Test is_cloud_path method."""
        # Set up detector mock
        mock_detector = MagicMock()
        provider = CloudProviderInfo(
            provider_type=CloudProviderType.ICLOUD,
            display_name="Test Cloud",
            root_path=Path("/test/cloud"),
            online=True,
        )

        # Mock to return provider for one path and None for another
        def mock_detect(path: Path) -> Optional[CloudProviderInfo]:
            if "/test/cloud" in str(path):
                return provider
            return None

        mock_detector.detect_provider.side_effect = mock_detect
        self.service._detector = mock_detector

        # Test cloud path
        assert self.service.is_cloud_path(Path("/test/cloud/file.txt"))

        # Test non-cloud path
        assert not self.service.is_cloud_path(Path("/regular/path/file.txt"))

    def test_get_provider_type(self) -> None:
        """Test get_provider_type method."""
        # Set up detector mock
        mock_detector = MagicMock()
        provider = CloudProviderInfo(
            provider_type=CloudProviderType.ICLOUD,
            display_name="Test Cloud",
            root_path=Path("/test/cloud"),
            online=True,
        )

        # Mock to return provider for one path and None for another
        def mock_detect(path: Path) -> Optional[CloudProviderInfo]:
            if "/test/cloud" in str(path):
                return provider
            return None

        mock_detector.detect_provider.side_effect = mock_detect
        self.service._detector = mock_detector

        # Test cloud path
        assert (
            self.service.get_provider_type(Path("/test/cloud/file.txt"))
            == CloudProviderType.ICLOUD
        )

        # Test non-cloud path
        assert (
            self.service.get_provider_type(Path("/regular/path/file.txt"))
            == CloudProviderType.UNKNOWN
        )

    def test_is_provider_online(self) -> None:
        """Test is_provider_online method."""
        # Set up mock providers
        mock_detector = MagicMock()
        providers = [
            CloudProviderInfo(
                provider_type=CloudProviderType.ICLOUD,
                display_name="Test Cloud 1",
                root_path=Path("/test/cloud/1"),
                online=True,
            ),
            CloudProviderInfo(
                provider_type=CloudProviderType.DROPBOX,
                display_name="Test Cloud 2",
                root_path=Path("/test/cloud/2"),
                online=False,
            ),
        ]
        mock_detector.get_all_providers.return_value = providers
        self.service._detector = mock_detector

        # Test online provider
        assert self.service.is_provider_online(CloudProviderType.ICLOUD)

        # Test offline provider
        assert not self.service.is_provider_online(CloudProviderType.DROPBOX)

        # Test unknown provider
        assert not self.service.is_provider_online(CloudProviderType.UNKNOWN)

    def test_refresh_provider_status_publishes_events(self) -> None:
        """Test that refresh_provider_status publishes events for status changes."""
        # Set up detector mock
        mock_detector = MagicMock()
        providers = [
            CloudProviderInfo(
                provider_type=CloudProviderType.ICLOUD,
                display_name="Test Cloud 1",
                root_path=Path("/test/cloud/1"),
                online=True,
            ),
            CloudProviderInfo(
                provider_type=CloudProviderType.DROPBOX,
                display_name="Test Cloud 2",
                root_path=Path("/test/cloud/2"),
                online=False,
            ),
        ]
        mock_detector.get_all_providers.return_value = providers

        # Mock status changes - only ICLOUD changed status
        mock_detector.refresh_provider_status.return_value = [
            (CloudProviderType.ICLOUD, False)
        ]

        self.service._detector = mock_detector

        # Reset event bus mock
        self.event_bus.reset_mock()

        # Refresh status
        self.service.refresh_provider_status()

        # Verify event was published only for the changed provider
        self.event_bus.publish.assert_called_once()

        # Check the event
        event = self.event_bus.publish.call_args[0][0]
        assert isinstance(event, CloudStorageEvent)
        assert event.provider == CloudProviderType.ICLOUD

    def test_get_all_providers(self) -> None:
        """Test get_all_providers method."""
        # Set up detector mock
        mock_detector = MagicMock()
        providers = [
            CloudProviderInfo(
                provider_type=CloudProviderType.ICLOUD,
                display_name="Test Cloud 1",
                root_path=Path("/test/cloud/1"),
                online=True,
            ),
            CloudProviderInfo(
                provider_type=CloudProviderType.DROPBOX,
                display_name="Test Cloud 2",
                root_path=Path("/test/cloud/2"),
                online=False,
            ),
        ]
        mock_detector.get_all_providers.return_value = providers
        self.service._detector = mock_detector

        # Get all providers
        result = self.service.get_all_providers()

        # Verify result
        assert result == providers
        mock_detector.get_all_providers.assert_called_once()
