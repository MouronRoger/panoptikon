"""Tests for enhanced indexing state management."""

from collections.abc import Generator
from pathlib import Path
import time
from typing import Any

import pytest

from panoptikon.core.config import ConfigSource, ConfigurationSystem
from panoptikon.core.errors import IndexingError
from panoptikon.core.events import EventBus
from panoptikon.indexing.state_manager import (
    IndexingCheckpoint,
    IndexingOperationType,
    IndexingStateManager,
    IndexingStatus,
)


@pytest.fixture
def db_service(tmp_path: Path) -> Generator[Any, None, None]:
    """Create a database service with test database, letting service handle config registration."""
    from panoptikon.database.schema import SchemaManager
    from panoptikon.database.service import DatabaseService

    db_path = tmp_path / "test.db"
    event_bus = EventBus()
    config_system = ConfigurationSystem(event_bus)
    service = DatabaseService(config_system)
    service.initialize()
    # Set the database path in the config system after registration
    config_system.set("database", "path", str(db_path), source=ConfigSource.RUNTIME)
    schema_manager = SchemaManager(db_path)
    schema_manager.create_schema()
    yield service
    service.shutdown()


@pytest.fixture
def state_manager(db_service: Any) -> IndexingStateManager:
    """Create state manager with test database."""
    return IndexingStateManager(db_service)


@pytest.fixture(autouse=True)
def clean_indexing_state(state_manager: IndexingStateManager) -> None:
    """Ensure clean indexing state before each test using the public reset method."""
    state_manager.reset()


class TestIndexingStateManager:
    """Test suite for IndexingStateManager."""

    def test_start_operation(self, state_manager: IndexingStateManager) -> None:
        """Test starting a new operation."""
        op_id = state_manager.start_operation(
            IndexingOperationType.INITIAL, total_files=1000
        )
        assert op_id is not None
        assert len(op_id) == 36  # UUID format
        active = state_manager.get_active_operation()
        assert active is not None
        assert active["operation_id"] == op_id
        assert active["status"] == IndexingStatus.IN_PROGRESS

    def test_prevent_concurrent_operations(
        self, state_manager: IndexingStateManager
    ) -> None:
        """Test that concurrent operations are prevented."""
        state_manager.start_operation(IndexingOperationType.INITIAL)
        with pytest.raises(IndexingError, match="already exists"):
            state_manager.start_operation(IndexingOperationType.INCREMENTAL)

    def test_update_checkpoint(self, state_manager: IndexingStateManager) -> None:
        """Test checkpoint updates."""
        op_id = state_manager.start_operation(IndexingOperationType.INITIAL)
        state_manager.update_checkpoint(
            op_id,
            files_processed=500,
            current_path="/test/path",
            last_file="file.txt",
            batch_num=5,
        )
        active = state_manager.get_active_operation()
        checkpoint = active["checkpoint"]
        assert checkpoint.files_processed == 500
        assert checkpoint.current_path == "/test/path"
        assert checkpoint.last_processed_file == "file.txt"
        assert checkpoint.batch_num == 5

    def test_pause_resume_operation(self, state_manager: IndexingStateManager) -> None:
        """Test pause and resume functionality."""
        op_id = state_manager.start_operation(IndexingOperationType.INITIAL)
        state_manager.update_checkpoint(op_id, files_processed=100)
        state_manager.pause_operation(op_id)
        active = state_manager.get_active_operation()
        assert active["status"] == IndexingStatus.PAUSED
        checkpoint = state_manager.resume_operation(op_id)
        assert checkpoint.files_processed == 100
        active = state_manager.get_active_operation()
        assert active["status"] == IndexingStatus.IN_PROGRESS

    def test_complete_operation(self, state_manager: IndexingStateManager) -> None:
        """Test operation completion."""
        op_id = state_manager.start_operation(IndexingOperationType.INITIAL)
        state_manager.update_checkpoint(op_id, files_processed=1000)
        state_manager.complete_operation(op_id, {"final_count": 1000})
        active = state_manager.get_active_operation()
        assert active is None

    def test_fail_operation(self, state_manager: IndexingStateManager) -> None:
        """Test operation failure."""
        op_id = state_manager.start_operation(IndexingOperationType.INITIAL)
        state_manager.fail_operation(op_id, "Test error")
        active = state_manager.get_active_operation()
        assert active is None

    def test_checkpoint_serialization(self) -> None:
        """Test checkpoint JSON serialization."""
        checkpoint = IndexingCheckpoint(
            operation_id="test-123",
            operation_type=IndexingOperationType.INITIAL,
            total_files=1000,
            files_processed=500,
            current_path="/test",
            last_processed_file="file.txt",
            errors=[{"error": "test", "timestamp": 123}],
            rate=50.0,
            started_at=time.time(),
            last_update=time.time(),
        )
        json_str = checkpoint.to_json()
        restored = IndexingCheckpoint.from_json(json_str)
        assert restored.operation_id == checkpoint.operation_id
        assert restored.operation_type == checkpoint.operation_type
        assert restored.files_processed == checkpoint.files_processed
        assert len(restored.errors) == 1

    def test_rate_calculation(self, state_manager: IndexingStateManager) -> None:
        """Test that rate calculation works correctly."""
        op_id = state_manager.start_operation(IndexingOperationType.INITIAL)
        time.sleep(0.1)
        state_manager.update_checkpoint(op_id, files_processed=50)
        active = state_manager.get_active_operation()
        checkpoint = active["checkpoint"]
        assert checkpoint.rate > 0
        assert checkpoint.rate <= 500  # Should be ~500 files/sec given 0.1s delay
        assert checkpoint.duration >= 0.1
