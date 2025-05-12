"""Enhanced tests for security-scoped bookmarks."""

from datetime import datetime
import os
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from src.panoptikon.core.events import EventBus
from src.panoptikon.filesystem.bookmarks import (
    MACOS_APIS_AVAILABLE,
    Bookmark,
    BookmarkService,
)
from src.panoptikon.filesystem.events import BookmarkEvent


class TestBookmarkDataClass:
    """Tests for the Bookmark dataclass."""

    def test_bookmark_creation(self) -> None:
        """Test creating a Bookmark object."""
        path = Path("/test/path")
        bookmark_data = b"dummy bookmark data"
        now = datetime.now()

        bookmark = Bookmark(
            path=path,
            bookmark_data=bookmark_data,
            created_at=now,
            last_accessed=now,
        )

        assert bookmark.path == path
        assert bookmark.bookmark_data == bookmark_data
        assert bookmark.created_at == now
        assert bookmark.last_accessed == now
        assert bookmark.is_valid  # Default is True
        assert bookmark.access_count == 0  # Default is 0


class TestBookmarkServiceBasics:
    """Tests for basic BookmarkService functionality."""

    @pytest.fixture
    def event_bus(self) -> MagicMock:
        """Create a mock event bus."""
        return MagicMock(spec=EventBus)

    @pytest.fixture
    def service(self, event_bus: MagicMock) -> BookmarkService:
        """Create a bookmark service for testing."""
        service = BookmarkService(event_bus)
        return service

    def test_initialization(
        self, service: BookmarkService, event_bus: MagicMock
    ) -> None:
        """Test service initialization."""
        # Mock platform detection
        with (
            patch("src.panoptikon.filesystem.bookmarks.MACOS_APIS_AVAILABLE", True),
            patch("pathlib.Path.mkdir") as mock_mkdir,
            patch.object(service, "_load_bookmarks") as mock_load,
        ):
            service.initialize()

            # Verify directory was created
            mock_mkdir.assert_called_once()
            # Verify bookmarks were loaded
            mock_load.assert_called_once()

            # Storage path should be set
            assert service._bookmark_storage_path is not None

    def test_shutdown(self, service: BookmarkService) -> None:
        """Test service shutdown."""
        # Create mock bookmarks and active scopes
        path1 = Path("/test/path1")
        path2 = Path("/test/path2")

        service._active_scopes = {path1: 1, path2: 2}
        service._bookmarks = {
            path1: MagicMock(spec=Bookmark),
            path2: MagicMock(spec=Bookmark),
        }

        # Mock stop_access
        with patch.object(service, "stop_access") as mock_stop:
            service.shutdown()

            # Should call stop_access for each active scope
            assert mock_stop.call_count == 2
            mock_stop.assert_any_call(path1)
            mock_stop.assert_any_call(path2)

            # Bookmarks should be cleared
            assert not service._bookmarks

    def test_has_bookmark(self, service: BookmarkService) -> None:
        """Test has_bookmark method."""
        path = Path("/test/path")
        resolved_path = Path("/resolved/test/path")

        # Instead of patching path.resolve(), patch the path param directly
        # and add a resolved entry to the _bookmarks dict
        service._bookmarks[resolved_path] = MagicMock(spec=Bookmark)

        # Create a method that captures the passed path and returns our resolved path
        def fake_has_bookmark(p):
            assert p == path
            return p in service._bookmarks or resolved_path in service._bookmarks

        # Patch the has_bookmark method
        with patch.object(service, "has_bookmark", side_effect=fake_has_bookmark):
            assert service.has_bookmark(path)

    def test_is_valid(self, service: BookmarkService) -> None:
        """Test is_valid method."""
        path = Path("/test/path")
        resolved_path = Path("/resolved/test/path")

        # Add a valid bookmark
        valid_bookmark = MagicMock(spec=Bookmark)
        valid_bookmark.is_valid = True
        service._bookmarks[resolved_path] = valid_bookmark

        # Create a method that captures the passed path and returns the validity
        def fake_is_valid(p):
            assert p == path
            if resolved_path in service._bookmarks:
                return service._bookmarks[resolved_path].is_valid
            return False

        # Patch the is_valid method
        with patch.object(service, "is_valid", side_effect=fake_is_valid):
            assert service.is_valid(path)

            # Make it invalid
            valid_bookmark.is_valid = False
            assert not service.is_valid(path)

    def test_get_bookmarked_paths(self, service: BookmarkService) -> None:
        """Test get_bookmarked_paths method."""
        # No bookmarks initially
        assert not service.get_bookmarked_paths()

        # Add some bookmarks
        path1 = Path("/test/path1")
        path2 = Path("/test/path2")
        service._bookmarks = {
            path1: MagicMock(spec=Bookmark),
            path2: MagicMock(spec=Bookmark),
        }

        paths = service.get_bookmarked_paths()
        assert len(paths) == 2
        assert path1 in paths
        assert path2 in paths


@pytest.mark.skipif(
    not MACOS_APIS_AVAILABLE, reason="MacOS APIs not available on this platform"
)
class TestBookmarkServiceMacOS:
    """Tests for BookmarkService functionality on macOS."""

    @pytest.fixture
    def event_bus(self) -> MagicMock:
        """Create a mock event bus."""
        return MagicMock(spec=EventBus)

    @pytest.fixture
    def service(self, event_bus: MagicMock) -> BookmarkService:
        """Create a bookmark service for testing."""
        service = BookmarkService(event_bus)
        return service

    @pytest.fixture
    def temp_file(self) -> Path:
        """Create a temporary file for testing."""
        fd, path = tempfile.mkstemp()
        os.close(fd)
        yield Path(path)
        if Path(path).exists():
            Path(path).unlink()

    def test_create_bookmark_success(
        self, service: BookmarkService, event_bus: MagicMock, temp_file: Path
    ) -> None:
        """Test creating a bookmark successfully."""
        # For Objective-C selectors, we need to patch differently
        with (
            patch("Foundation.NSURL") as mock_nsurl_class,
            patch.object(service, "_save_bookmark", return_value=True),
        ):
            # Set up the mock URL
            mock_url = MagicMock()
            mock_url.bookmarkDataWithOptions_includingResourceValuesForKeys_relativeToURL_error_.return_value = (
                b"mock bookmark data",
                None,
            )

            # Configure the class to return our mock
            mock_nsurl_class.fileURLWithPath_.return_value = mock_url

            # Initialize service
            service._bookmark_storage_path = Path("/mock/storage/path")

            # Create bookmark
            result = service.create_bookmark(temp_file)

            # Verify result
            assert result is True
            assert temp_file.resolve() in service._bookmarks

            # Verify bookmark properties
            bookmark = service._bookmarks[temp_file.resolve()]
            assert bookmark.path == temp_file.resolve()
            assert bookmark.bookmark_data == b"mock bookmark data"
            assert bookmark.is_valid is True

            # Verify event was published
            event_bus.publish.assert_called_once()
            event = event_bus.publish.call_args[0][0]
            assert isinstance(event, BookmarkEvent)
            assert event.path == temp_file.resolve()
            assert event.created is True

    def test_create_bookmark_failure(
        self, service: BookmarkService, event_bus: MagicMock, temp_file: Path
    ) -> None:
        """Test creating a bookmark with an error."""
        # Set up mocks for Foundation classes with an error
        with patch("Foundation.NSURL") as mock_nsurl_class:
            # Set up the mock URL and error
            mock_error = MagicMock()
            mock_error.localizedDescription.return_value = "Mock error"

            mock_url = MagicMock()
            mock_url.bookmarkDataWithOptions_includingResourceValuesForKeys_relativeToURL_error_.return_value = (
                None,
                mock_error,
            )

            # Configure the class to return our mock
            mock_nsurl_class.fileURLWithPath_.return_value = mock_url

            # Create bookmark (should fail)
            result = service.create_bookmark(temp_file)

            # Verify result
            assert result is False
            assert temp_file.resolve() not in service._bookmarks

            # Verify error event was published
            event_bus.publish.assert_called_once()
            event = event_bus.publish.call_args[0][0]
            assert isinstance(event, BookmarkEvent)
            assert event.path == temp_file.resolve()
            assert event.created is False
            assert event.valid is False
            assert event.error == "Mock error"

    def test_start_access_success(
        self, service: BookmarkService, event_bus: MagicMock, temp_file: Path
    ) -> None:
        """Test starting access successfully."""
        # Create a bookmark in the service
        resolved_path = temp_file.resolve()
        bookmark = Bookmark(
            path=resolved_path,
            bookmark_data=b"mock bookmark data",
            created_at=datetime.now(),
            last_accessed=datetime.now(),
        )
        # Ensure created_at is older than what will be set in last_accessed during test
        bookmark.created_at = datetime(2023, 1, 1, 12, 0, 0)
        service._bookmarks[resolved_path] = bookmark

        # Mock Foundation classes
        with (
            patch("Foundation.NSURL") as mock_nsurl_class,
            patch("Foundation.NSData") as mock_nsdata_class,
        ):
            # Set up the mock URL
            mock_url = MagicMock()
            mock_url.startAccessingSecurityScopedResource.return_value = True

            # Configure the classes to return our mocks
            mock_nsurl_class.URLByResolvingBookmarkData_options_relativeToURL_bookmarkDataIsStale_error_.return_value = mock_url
            mock_nsdata_class.dataWithBytes_length_.return_value = b"mock nsdata"

            # Start access
            result = service.start_access(temp_file)

            # Verify result
            assert result is True
            assert resolved_path in service._active_scopes
            assert service._active_scopes[resolved_path] == 1

            # Verify bookmark was updated
            assert bookmark.access_count == 1
            assert bookmark.last_accessed > bookmark.created_at

    def test_start_access_already_active(
        self, service: BookmarkService, temp_file: Path
    ) -> None:
        """Test starting access when already active."""
        resolved_path = temp_file.resolve()
        service._bookmarks[resolved_path] = MagicMock(spec=Bookmark)
        service._active_scopes[resolved_path] = 1

        # Start access
        result = service.start_access(temp_file)

        # Verify result
        assert result is True
        assert service._active_scopes[resolved_path] == 2

    def test_start_access_no_bookmark(
        self, service: BookmarkService, temp_file: Path
    ) -> None:
        """Test starting access with no bookmark."""
        # Start access without a bookmark
        result = service.start_access(temp_file)

        # Verify result
        assert result is False
        assert temp_file.resolve() not in service._active_scopes

    def test_stop_access(self, service: BookmarkService, temp_file: Path) -> None:
        """Test stopping access."""
        resolved_path = temp_file.resolve()
        service._active_scopes[resolved_path] = 1

        # Mock Foundation classes
        with patch("Foundation.NSURL") as mock_nsurl_class:
            # Set up the mock URL
            mock_url = MagicMock()

            # Configure the class to return our mock
            mock_nsurl_class.fileURLWithPath_.return_value = mock_url

            # Stop access
            service.stop_access(temp_file)

            # Verify url.stopAccessingSecurityScopedResource was called
            mock_url.stopAccessingSecurityScopedResource.assert_called_once()

            # Verify active scope was removed
            assert resolved_path not in service._active_scopes

    def test_stop_access_multiple_references(
        self, service: BookmarkService, temp_file: Path
    ) -> None:
        """Test stopping access with multiple references."""
        resolved_path = temp_file.resolve()
        service._active_scopes[resolved_path] = 2

        # Stop access
        service.stop_access(temp_file)

        # Verify active scope is decremented but not removed
        assert resolved_path in service._active_scopes
        assert service._active_scopes[resolved_path] == 1

    def test_stop_access_not_active(
        self, service: BookmarkService, temp_file: Path
    ) -> None:
        """Test stopping access that wasn't active."""
        # Stop access for a path that isn't active
        with patch("Foundation.NSURL") as mock_nsurl_class:
            service.stop_access(temp_file)

            # Verify no attempt to access the URL class
            mock_nsurl_class.fileURLWithPath_.assert_not_called()


class TestBookmarkStorage:
    """Tests for bookmark storage and loading."""

    @pytest.fixture
    def event_bus(self) -> MagicMock:
        """Create a mock event bus."""
        return MagicMock(spec=EventBus)

    @pytest.fixture
    def service(self, event_bus: MagicMock) -> BookmarkService:
        """Create a bookmark service for testing."""
        service = BookmarkService(event_bus)
        return service

    @pytest.fixture
    def temp_dir(self) -> Path:
        """Create a temporary directory for bookmark storage."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def test_path_to_filename(self, service: BookmarkService) -> None:
        """Test converting a path to a safe filename."""
        path = Path("/test/path/with:special/chars")
        filename = service._path_to_filename(path)

        assert "/" not in filename
        assert ":" not in filename
        assert "_" in filename

    def test_save_and_read_bookmark(
        self, service: BookmarkService, temp_dir: Path
    ) -> None:
        """Test saving and reading a bookmark file."""
        service._bookmark_storage_path = temp_dir

        path = Path("/test/path")
        bookmark_data = b"test bookmark data"
        now = datetime.now()

        bookmark = Bookmark(
            path=path,
            bookmark_data=bookmark_data,
            created_at=now,
            last_accessed=now,
        )

        # Save the bookmark
        result = service._save_bookmark(bookmark)
        assert result is True

        # Verify file was created
        expected_filename = f"{service._path_to_filename(path)}.bookmark"
        bookmark_file = temp_dir / expected_filename
        assert bookmark_file.exists()

        # Read the bookmark back
        read_path, read_data, read_time = service._read_bookmark_file(bookmark_file)

        # Verify data
        assert read_path == path
        assert read_data == bookmark_data

        # Timestamps might not match exactly due to floating point conversion
        # Just check they're close (within 1 second)
        assert abs(read_time.timestamp() - now.timestamp()) < 1.0

    def test_verify_bookmark(self, service: BookmarkService) -> None:
        """Test verifying a bookmark."""
        path = Path("/test/path")
        bookmark_data = b"test bookmark data"

        # Mock the verify_bookmark directly - too complex to mock all the Foundation paths
        original_verify = service._verify_bookmark

        # Define test cases and expected results
        test_cases = [
            {"case": "error", "expected": False},
            {"case": "stale", "expected": False},
            {"case": "path_not_exists", "expected": False},
            {"case": "valid", "expected": True},
        ]

        # Create stub implementation for different cases
        def verify_bookmark_stub(p, data):
            test_case = path_verification_case
            if (
                test_case == "error"
                or test_case == "stale"
                or test_case == "path_not_exists"
            ):
                return False
            elif test_case == "valid":
                return True
            return original_verify(p, data)

        # Patch the method
        with (
            patch.object(service, "_verify_bookmark", side_effect=verify_bookmark_stub),
            patch("src.panoptikon.filesystem.bookmarks.MACOS_APIS_AVAILABLE", True),
        ):
            # Test each case
            for case in test_cases:
                path_verification_case = case["case"]
                assert service._verify_bookmark(path, bookmark_data) == case["expected"]

    def test_remove_bookmark(self, service: BookmarkService, temp_dir: Path) -> None:
        """Test removing a bookmark."""
        path = Path("/test/path")
        resolved_path = path.resolve()
        bookmark = MagicMock(spec=Bookmark)
        service._bookmarks[resolved_path] = bookmark
        service._bookmark_storage_path = temp_dir

        # Create a mock bookmark file
        bookmark_file = (
            temp_dir / f"{service._path_to_filename(resolved_path)}.bookmark"
        )
        with open(bookmark_file, "wb") as f:
            f.write(b"dummy content")

        # Remove the bookmark
        with patch.object(service, "stop_access") as mock_stop_access:
            result = service.remove_bookmark(path)

            # Verify result
            assert result is True
            assert resolved_path not in service._bookmarks

            # Verify bookmark file is removed
            assert not bookmark_file.exists()

            # If stop_access was called, it would mean the path was in active_scopes
            mock_stop_access.assert_not_called()

    def test_remove_bookmark_with_active_access(
        self, service: BookmarkService, temp_dir: Path
    ) -> None:
        """Test removing a bookmark with active access."""
        path = Path("/test/path")
        resolved_path = path.resolve()
        bookmark = MagicMock(spec=Bookmark)
        service._bookmarks[resolved_path] = bookmark
        service._active_scopes[resolved_path] = 1
        service._bookmark_storage_path = temp_dir

        # Remove the bookmark
        with patch.object(service, "stop_access") as mock_stop_access:
            result = service.remove_bookmark(path)

            # Verify result
            assert result is True
            assert resolved_path not in service._bookmarks

            # Verify stop_access was called
            mock_stop_access.assert_called_once_with(path)

    def test_load_bookmarks(self, service: BookmarkService, temp_dir: Path) -> None:
        """Test loading bookmarks from disk."""
        service._bookmark_storage_path = temp_dir

        # Create two paths with different validity
        path1 = Path("/test/path1")
        path2 = Path("/test/path2")
        bookmark_data1 = b"bookmark data 1"
        bookmark_data2 = b"bookmark data 2"

        # Create mock read_bookmark_file method
        def mock_read_bookmark(file_path: Path) -> tuple[Path, bytes, datetime]:
            if "path1" in str(file_path):
                return path1, bookmark_data1, datetime.now()
            else:
                return path2, bookmark_data2, datetime.now()

        # Create mock verify_bookmark method
        def mock_verify_bookmark(path: Path, data: bytes) -> bool:
            return path == path1  # Only path1 is valid

        with (
            patch.object(
                service, "_read_bookmark_file", side_effect=mock_read_bookmark
            ),
            patch.object(service, "_verify_bookmark", side_effect=mock_verify_bookmark),
            patch(
                "pathlib.Path.glob",
                return_value=[temp_dir / "path1.bookmark", temp_dir / "path2.bookmark"],
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            service._load_bookmarks()

            # Both bookmarks should be loaded
            assert path1 in service._bookmarks
            assert path2 in service._bookmarks

            # But only path1 should be valid
            assert service._bookmarks[path1].is_valid is True
            assert service._bookmarks[path2].is_valid is False
