"""Integration tests for IndexerService with enhanced state management."""

from collections.abc import Generator
from pathlib import Path
import time
from typing import Any
from unittest.mock import Mock, patch

import pytest

from panoptikon.core.config import ConfigurationSystem
from panoptikon.core.events import EventBus
from panoptikon.core.indexer import IndexerService
from panoptikon.database.service import DatabaseService
from panoptikon.indexing.state_manager import (  # type: ignore[import-untyped]
    IndexingOperationType,
)


@pytest.fixture
def event_bus() -> Mock:
    """Create a mock event bus."""
    return Mock(spec=EventBus)


@pytest.fixture
def db_service(tmp_path: Path) -> Generator[DatabaseService, None, None]:
    """Create a database service with test database."""
    db_path = tmp_path / "test.db"
    event_bus = EventBus()
    config_system = ConfigurationSystem(event_bus, config_dir=tmp_path)
    service = DatabaseService(config_system)
    # Patch get_default_config to use the test db path
    import panoptikon.database.config as db_config_mod

    orig_get_default_config = db_config_mod.get_default_config

    def test_get_default_config() -> dict[str, object]:
        config = orig_get_default_config()
        config["path"] = db_path
        config["create_if_missing"] = True
        return config

    db_config_mod.get_default_config = test_get_default_config
    try:
        service.initialize()
        yield service
    finally:
        db_config_mod.get_default_config = orig_get_default_config
        service.shutdown()


@pytest.fixture
def indexer_service(
    event_bus: Mock, db_service: DatabaseService
) -> Generator[IndexerService, None, None]:
    """Create an indexer service instance."""
    service = IndexerService(event_bus, db_service)
    service.initialize()
    yield service
    service.shutdown()


@pytest.fixture
def test_files(tmp_path: Path) -> Path:
    """Create test files for indexing."""
    test_dir = tmp_path / "test_files"
    test_dir.mkdir()
    for i in range(10):
        (test_dir / f"file_{i}.txt").write_text(f"Content {i}")
    sub_dir = test_dir / "subdir"
    sub_dir.mkdir()
    for i in range(5):
        (sub_dir / f"subfile_{i}.txt").write_text(f"Sub content {i}")
    return test_dir


class TestIndexerIntegration:
    """Test IndexerService integration with enhanced state management."""

    def test_initial_indexing_with_state(
        self, indexer_service: IndexerService, test_files: Path, event_bus: Mock
    ) -> None:
        """Test initial indexing creates proper state."""
        indexer_service.start_initial_indexing([str(test_files)])
        assert event_bus.publish.called
        start_event = event_bus.publish.call_args_list[0][0][0]
        assert start_event.__class__.__name__ == "IndexingStartedEvent"
        status = indexer_service.get_indexing_status()
        assert status["state"] == "completed"
        assert status["files_processed"] == 15

    def test_pause_resume_indexing(
        self, indexer_service: IndexerService, test_files: Path, event_bus: Mock
    ) -> None:
        """Test pause and resume functionality."""
        original_index = indexer_service._index_files
        pause_after = 5

        def mock_index(*args: Any, **kwargs: Any) -> None:
            for _ in range(pause_after):
                if indexer_service._paused:
                    break
                time.sleep(0.01)
            if indexer_service._paused:
                return
            original_index(*args, **kwargs)

        with patch.object(indexer_service, "_index_files", mock_index):
            import threading

            thread = threading.Thread(
                target=indexer_service.start_initial_indexing, args=([str(test_files)],)
            )
            thread.start()
            time.sleep(0.05)
            indexer_service.pause_indexing()
            thread.join(timeout=1)
            status = indexer_service.get_indexing_status()
            assert status["state"] == "paused"
            indexer_service.resume_indexing()
            status = indexer_service.get_indexing_status()
            assert status["state"] in ["in_progress", "completed"]

    def test_operation_recovery_on_init(
        self, db_service: DatabaseService, event_bus: Mock, test_files: Path
    ) -> None:
        """Test that interrupted operations are detected on init."""
        service1 = IndexerService(event_bus, db_service)
        service1.initialize()
        op_id = service1._state_manager.start_operation(
            IndexingOperationType.INITIAL, total_files=100
        )
        service1._current_operation_id = op_id
        service2 = IndexerService(event_bus, db_service)
        service2.initialize()
        assert service2._current_operation_id == op_id

    def test_checkpoint_throttling(
        self, indexer_service: IndexerService, test_files: Path
    ) -> None:
        """Test that checkpoints are throttled."""
        checkpoint_calls: list[float] = []
        original_update = indexer_service._state_manager.update_checkpoint

        def track_checkpoint(*args: Any, **kwargs: Any) -> None:
            checkpoint_calls.append(time.time())
            return original_update(*args, **kwargs)

        with patch.object(
            indexer_service._state_manager, "update_checkpoint", track_checkpoint
        ):
            indexer_service.start_initial_indexing([str(test_files)])
            if len(checkpoint_calls) > 1:
                for i in range(1, len(checkpoint_calls)):
                    time_diff = checkpoint_calls[i] - checkpoint_calls[i - 1]
                    assert time_diff >= 0.9

    def test_error_handling_updates_state(
        self, indexer_service: IndexerService, event_bus: Mock
    ) -> None:
        """Test that errors properly update operation state."""

        def mock_error(*args: Any, **kwargs: Any) -> None:
            raise ValueError("Test error")

        with patch.object(indexer_service, "_index_files", mock_error):
            with pytest.raises(ValueError):
                indexer_service.start_initial_indexing(["/fake/path"])
            status = indexer_service.get_indexing_status()
            assert status["state"] == "failed"
            error_events = [
                call[0][0]
                for call in event_bus.publish.call_args_list
                if call[0][0].__class__.__name__ == "IndexingErrorEvent"
            ]
            assert len(error_events) == 1
