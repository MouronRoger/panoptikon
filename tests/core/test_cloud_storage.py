"""Tests for the cloud storage provider detection."""

from pathlib import Path
import tempfile
from typing import Optional
import unittest
from unittest.mock import MagicMock, patch

from src.panoptikon.core.events import EventBus
from src.panoptikon.filesystem.cloud import CloudProviderDetector, CloudStorageService
from src.panoptikon.filesystem.events import CloudProviderType
from src.panoptikon.filesystem.paths import PathManager


class TestCloudProviderDetector(unittest.TestCase):
    """Tests for the CloudProviderDetector class."""

    def setUp(self) -> None:
        """Set up test environment."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Set up a mock cloud structure
        self.mock_cloud_root = self.temp_path / "mock_cloud"
        self.mock_cloud_root.mkdir()

        # Create marker files for detection
        dropbox_path = self.mock_cloud_root / "Dropbox"
        dropbox_path.mkdir()
        (dropbox_path / ".dropbox").touch()

        # Create a test file in the mock cloud
        self.test_file = dropbox_path / "test_file.txt"
        with open(self.test_file, "w") as f:
            f.write("Test content")

        # Create the detector to test
        with patch("pathlib.Path.home", return_value=self.temp_path):
            self.detector = CloudProviderDetector()

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.temp_dir.cleanup()

    @patch("platform.system", return_value="Darwin")
    def test_initialize_providers_mac(self, mock_system: MagicMock) -> None:
        """Test provider initialization on macOS."""
        # Create a mock home directory with cloud paths
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create cloud directories and marker files
            dropbox_path = temp_path / "Dropbox"
            dropbox_path.mkdir()
            (dropbox_path / ".dropbox").touch()

            # Initialize detector with mock home
            with patch("pathlib.Path.home", return_value=temp_path):
                detector = CloudProviderDetector()

            # Should have detected Dropbox
            providers = detector.get_all_providers()
            provider_types = [p.provider_type for p in providers]
            self.assertIn(CloudProviderType.DROPBOX, provider_types)

    def test_detect_provider(self) -> None:
        """Test detection of providers for paths."""
        # Create a mock home with Dropbox path
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create Dropbox directory with marker
            dropbox_path = temp_path / "Dropbox"
            dropbox_path.mkdir()
            (dropbox_path / ".dropbox").touch()

            # Create test file in Dropbox
            test_file = dropbox_path / "test_file.txt"
            with open(test_file, "w") as f:
                f.write("Test content")

            # Initialize detector with mock home
            with (
                patch("pathlib.Path.home", return_value=temp_path),
                patch("platform.system", return_value="Darwin"),
            ):
                detector = CloudProviderDetector()

            # Test file should be detected as Dropbox
            provider = detector.detect_provider(test_file)
            self.assertIsNotNone(provider)
            self.assertEqual(CloudProviderType.DROPBOX, provider.provider_type)

            # Path outside should not be detected
            outside_path = temp_path / "outside.txt"
            with open(outside_path, "w") as f:
                f.write("Not in cloud")

            provider = detector.detect_provider(outside_path)
            self.assertIsNone(provider)


class TestCloudStorageService(unittest.TestCase):
    """Tests for the CloudStorageService class."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.event_bus = MagicMock(spec=EventBus)
        self.path_manager = MagicMock(spec=PathManager)

        # Create the service with mocked providers
        with patch(
            "src.panoptikon.filesystem.cloud.CloudProviderDetector"
        ) as mock_detector_cls:
            self.mock_detector = mock_detector_cls.return_value
            self.service = CloudStorageService(self.event_bus, self.path_manager)

    def test_initialize(self) -> None:
        """Test service initialization."""
        # Set up mock providers
        mock_provider = MagicMock()
        mock_provider.provider_type = CloudProviderType.DROPBOX
        mock_provider.root_path = Path("/mock/dropbox")

        self.mock_detector.get_all_providers.return_value = [mock_provider]

        # Initialize should publish events for all providers
        self.service.initialize()

        # Should have published provider events
        self.event_bus.publish.assert_called()

    def test_get_provider_for_path(self) -> None:
        """Test retrieving provider for a path."""
        # Set up mock detection
        test_path = Path("/test/path.txt")
        mock_provider = MagicMock()
        mock_provider.provider_type = CloudProviderType.DROPBOX

        self.mock_detector.detect_provider.return_value = mock_provider

        # Get provider for path
        provider = self.service.get_provider_for_path(test_path)

        # Should match mock provider
        self.assertEqual(mock_provider, provider)
        self.mock_detector.detect_provider.assert_called_once_with(test_path)

        # Second call should use cache
        self.mock_detector.detect_provider.reset_mock()
        provider = self.service.get_provider_for_path(test_path)
        self.assertEqual(mock_provider, provider)
        self.mock_detector.detect_provider.assert_not_called()

    def test_is_cloud_path(self) -> None:
        """Test checking if a path is on cloud storage."""
        # Set up mock detection
        cloud_path = Path("/cloud/path.txt")
        non_cloud_path = Path("/local/path.txt")

        mock_provider = MagicMock()

        # Configure detector to return provider for cloud path only
        def mock_detect_provider(path: Path) -> Optional[MagicMock]:
            return mock_provider if path == cloud_path else None

        self.mock_detector.detect_provider.side_effect = mock_detect_provider

        # Check paths
        self.assertTrue(self.service.is_cloud_path(cloud_path))
        self.assertFalse(self.service.is_cloud_path(non_cloud_path))

    def test_get_provider_type(self) -> None:
        """Test getting provider type for a path."""
        # Set up mock detection
        test_path = Path("/test/path.txt")
        mock_provider = MagicMock()
        mock_provider.provider_type = CloudProviderType.DROPBOX

        self.mock_detector.detect_provider.return_value = mock_provider

        # Get provider type
        provider_type = self.service.get_provider_type(test_path)

        # Should match mock provider type
        self.assertEqual(CloudProviderType.DROPBOX, provider_type)

        # Non-cloud path should return UNKNOWN
        self.mock_detector.detect_provider.return_value = None
        provider_type = self.service.get_provider_type(Path("/non/cloud/path.txt"))
        self.assertEqual(CloudProviderType.UNKNOWN, provider_type)

    def test_refresh_provider_status(self) -> None:
        """Test refreshing provider status."""
        # Set up mock status changes
        self.mock_detector.refresh_provider_status.return_value = [
            (CloudProviderType.DROPBOX, True)
        ]

        # Refresh status
        self.service.refresh_provider_status()

        # Should have queried detector
        self.mock_detector.refresh_provider_status.assert_called_once()
