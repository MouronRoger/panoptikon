"""Shared pytest fixtures for filesystem and core tests."""

from collections.abc import Generator
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from src.panoptikon.core.events import EventBus
from src.panoptikon.filesystem.access import FileAccessService
from src.panoptikon.filesystem.bookmarks import BookmarkService
from src.panoptikon.filesystem.cloud import CloudStorageService
from src.panoptikon.filesystem.paths import PathManager
from src.panoptikon.filesystem.watcher import FileSystemWatchService


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def event_bus() -> EventBus:
    """Create an event bus."""
    bus = EventBus()
    bus.initialize()
    return bus


@pytest.fixture
def mock_event_bus() -> MagicMock:
    """Create a mock event bus."""
    return MagicMock(spec=EventBus)


@pytest.fixture
def event_callback() -> MagicMock:
    """Create a mock event callback."""
    return MagicMock()


@pytest.fixture
def mock_dependencies() -> dict[str, MagicMock]:
    """Create mock dependencies for FileAccessService."""
    event_bus = MagicMock(spec=EventBus)
    path_manager = MagicMock(spec=PathManager)
    bookmark_service = MagicMock(spec=BookmarkService)
    cloud_service = MagicMock(spec=CloudStorageService)
    bookmark_service.has_bookmark.return_value = False
    bookmark_service.create_bookmark.return_value = True
    bookmark_service.start_access.return_value = True
    cloud_service.get_provider_for_path.return_value = None
    return {
        "event_bus": event_bus,
        "path_manager": path_manager,
        "bookmark_service": bookmark_service,
        "cloud_service": cloud_service,
    }


@pytest.fixture
def test_file(temp_dir: Path) -> Path:
    """Create a test file."""
    test_file = temp_dir / "test_file.txt"
    test_file.write_text("Test content")
    return test_file


@pytest.fixture
def path_manager() -> PathManager:
    """Create a path manager."""
    manager = PathManager()
    manager.initialize()
    return manager


@pytest.fixture
def bookmark_service(event_bus: EventBus) -> BookmarkService:
    """Create a bookmark service."""
    service = BookmarkService(event_bus)
    with patch.object(Path, "mkdir"):
        service.initialize()
        if service._bookmark_storage_path:
            service._bookmark_storage_path = Path(tempfile.mkdtemp()) / "bookmarks"
            service._bookmark_storage_path.mkdir(exist_ok=True)
    return service


@pytest.fixture
def cloud_service(
    event_bus: EventBus, path_manager: PathManager
) -> CloudStorageService:
    """Create a cloud storage service."""
    service = CloudStorageService(event_bus, path_manager)
    service.initialize()
    return service


@pytest.fixture
def watch_service(
    mock_event_bus: MagicMock,
) -> Generator[FileSystemWatchService, None, None]:
    """Create a file system watch service."""
    service = FileSystemWatchService(mock_event_bus)
    service.initialize()
    yield service
    service.shutdown()


@pytest.fixture
def access_service(
    mock_dependencies: dict[str, MagicMock],
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
def file_access_service(
    event_bus: EventBus,
    path_manager: PathManager,
    bookmark_service: BookmarkService,
    cloud_service: CloudStorageService,
) -> FileAccessService:
    """Create a file access service with real dependencies."""
    service = FileAccessService(
        event_bus,
        path_manager,
        bookmark_service,
        cloud_service,
    )
    service.initialize()
    return service
