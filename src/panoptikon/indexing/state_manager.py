"""Enhanced indexing state management with checkpoint and recovery support."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
import json
import logging
import time
from typing import Any, Optional
from uuid import uuid4

from panoptikon.core.errors import IndexingError
from panoptikon.database.service import DatabaseService

logger = logging.getLogger(__name__)


class IndexingStatus(str, Enum):
    """Indexing operation status values."""

    IDLE = "idle"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class IndexingOperationType(str, Enum):
    """Types of indexing operations."""

    INITIAL = "initial"
    INCREMENTAL = "incremental"
    RECOVERY = "recovery"


@dataclass
class IndexingCheckpoint:
    """Structured checkpoint data for indexing operations."""

    operation_id: str
    operation_type: IndexingOperationType
    total_files: Optional[int]
    files_processed: int
    current_path: Optional[str]
    last_processed_file: Optional[str]
    errors: list[dict[str, Any]]
    rate: float
    started_at: float
    last_update: float
    batch_num: int = 0
    checkpoint_version: str = "1.0"

    @property
    def duration(self) -> float:
        """Calculate elapsed time in seconds."""
        return self.last_update - self.started_at

    def to_json(self) -> str:
        """Serialize to JSON for storage."""
        data = asdict(self)
        return json.dumps(data)

    @classmethod
    def from_json(cls, data: str) -> IndexingCheckpoint:
        """Deserialize from JSON."""
        obj = json.loads(data)
        obj["operation_type"] = IndexingOperationType(obj["operation_type"])
        return cls(**obj)


class IndexingStateManager:
    """Enhanced state management for indexing operations.

    This implementation uses a single-row design (id=1) in the indexing_state table,
    enforced by a CHECK constraint: id INTEGER PRIMARY KEY CHECK (id = 1).
    This means only one operation can be tracked at a time. A future migration
    could remove this constraint to support operation history.
    """

    def __init__(self, db_service: DatabaseService) -> None:
        """Initialize with database service."""
        self._db_service = db_service
        self._current_operation_id: Optional[str] = None

    def start_operation(
        self,
        operation_type: IndexingOperationType,
        total_files: Optional[int] = None,
    ) -> str:
        """Start a new indexing operation.

        Returns:
            Operation ID (UUID string)

        Raises:
            IndexingError: If another operation is already active
        """
        existing = self.get_active_operation()
        if existing and existing["status"] in [
            IndexingStatus.IN_PROGRESS,
            IndexingStatus.PAUSED,
        ]:
            raise IndexingError(
                f"Cannot start new operation: {existing['status'].value} "
                f"operation {existing['checkpoint'].operation_id} already exists"
            )
        operation_id = str(uuid4())
        self._current_operation_id = operation_id
        checkpoint = IndexingCheckpoint(
            operation_id=operation_id,
            operation_type=operation_type,
            total_files=total_files,
            files_processed=0,
            current_path=None,
            last_processed_file=None,
            errors=[],
            rate=0.0,
            started_at=time.time(),
            last_update=time.time(),
        )
        self._save_state(
            operation_type=operation_type.value,
            status=IndexingStatus.IN_PROGRESS.value,
            checkpoint_data=checkpoint.to_json(),
            started_at=int(checkpoint.started_at),
            updated_at=int(checkpoint.last_update),
        )
        logger.info(f"Started {operation_type.value} operation {operation_id}")
        return operation_id

    def update_checkpoint(
        self,
        operation_id: str,
        files_processed: int,
        current_path: Optional[str] = None,
        last_file: Optional[str] = None,
        error: Optional[dict[str, Any]] = None,
        batch_num: Optional[int] = None,
    ) -> None:
        """Update checkpoint for current operation."""
        if operation_id != self._current_operation_id:
            raise IndexingError(f"Invalid operation ID: {operation_id}")
        state = self._load_state()
        if not state:
            raise IndexingError("No active operation found")
        checkpoint = IndexingCheckpoint.from_json(state["checkpoint_data"])
        checkpoint.files_processed = files_processed
        checkpoint.last_update = time.time()
        if current_path:
            checkpoint.current_path = current_path
        if last_file:
            checkpoint.last_processed_file = last_file
        if error:
            checkpoint.errors.append({**error, "timestamp": time.time()})
        if batch_num is not None:
            checkpoint.batch_num = batch_num
        elapsed = checkpoint.last_update - checkpoint.started_at
        if elapsed > 0:
            checkpoint.rate = files_processed / elapsed
        self._save_state(
            operation_type=state["operation_type"],
            status=state["status"],
            checkpoint_data=checkpoint.to_json(),
            started_at=state["started_at"],
            updated_at=int(checkpoint.last_update),
        )

    def get_active_operation(self) -> Optional[dict[str, Any]]:
        """Get any active (in_progress/paused) operation."""
        state = self._load_state()
        if not state:
            return None
        if state["status"] in ["completed", "failed", "idle"]:
            return None
        checkpoint = IndexingCheckpoint.from_json(state["checkpoint_data"])
        return {
            "operation_id": checkpoint.operation_id,
            "operation_type": checkpoint.operation_type,
            "status": IndexingStatus(state["status"]),
            "checkpoint": checkpoint,
            "started_at": datetime.fromtimestamp(state["started_at"]),
            "updated_at": datetime.fromtimestamp(state["updated_at"]),
        }

    def pause_operation(self, operation_id: str) -> None:
        """Mark operation as paused."""
        if operation_id != self._current_operation_id:
            raise IndexingError(f"Invalid operation ID: {operation_id}")
        state = self._load_state()
        if not state or state["status"] != IndexingStatus.IN_PROGRESS.value:
            raise IndexingError("No active operation to pause")
        self._save_state(
            operation_type=state["operation_type"],
            status=IndexingStatus.PAUSED.value,
            checkpoint_data=state["checkpoint_data"],
            started_at=state["started_at"],
            updated_at=int(time.time()),
        )
        logger.info(f"Paused operation {operation_id}")

    def resume_operation(self, operation_id: str) -> IndexingCheckpoint:
        """Resume a paused operation."""
        state = self._load_state()
        if not state:
            raise IndexingError("No operation to resume")
        checkpoint = IndexingCheckpoint.from_json(state["checkpoint_data"])
        if checkpoint.operation_id != operation_id:
            raise IndexingError(f"Operation ID mismatch: {operation_id}")
        if state["status"] != IndexingStatus.PAUSED.value:
            raise IndexingError(f"Cannot resume operation in {state['status']} state")
        self._current_operation_id = operation_id
        self._save_state(
            operation_type=state["operation_type"],
            status=IndexingStatus.IN_PROGRESS.value,
            checkpoint_data=state["checkpoint_data"],
            started_at=state["started_at"],
            updated_at=int(time.time()),
        )
        logger.info(f"Resumed operation {operation_id}")
        return checkpoint

    def complete_operation(self, operation_id: str, stats: dict[str, Any]) -> None:
        """Mark operation as completed."""
        if operation_id != self._current_operation_id:
            raise IndexingError(f"Invalid operation ID: {operation_id}")
        state = self._load_state()
        if not state:
            raise IndexingError("No active operation to complete")
        checkpoint = IndexingCheckpoint.from_json(state["checkpoint_data"])
        checkpoint.last_update = time.time()
        elapsed = checkpoint.last_update - checkpoint.started_at
        if elapsed > 0:
            checkpoint.rate = checkpoint.files_processed / elapsed
        self._save_state(
            operation_type=state["operation_type"],
            status=IndexingStatus.COMPLETED.value,
            checkpoint_data=checkpoint.to_json(),
            started_at=state["started_at"],
            updated_at=int(time.time()),
            completed_at=int(time.time()),
        )
        self._current_operation_id = None
        logger.info(
            f"Completed operation {operation_id}: "
            f"{checkpoint.files_processed} files in {elapsed:.2f}s "
            f"({checkpoint.rate:.1f} files/s)"
        )

    def fail_operation(self, operation_id: str, error: str) -> None:
        """Mark operation as failed."""
        if operation_id != self._current_operation_id:
            raise IndexingError(f"Invalid operation ID: {operation_id}")
        state = self._load_state()
        if not state:
            raise IndexingError("No active operation to fail")
        checkpoint = IndexingCheckpoint.from_json(state["checkpoint_data"])
        checkpoint.errors.append(
            {"error": error, "timestamp": time.time(), "fatal": True}
        )
        self._save_state(
            operation_type=state["operation_type"],
            status=IndexingStatus.FAILED.value,
            checkpoint_data=checkpoint.to_json(),
            started_at=state["started_at"],
            updated_at=int(time.time()),
        )
        self._current_operation_id = None
        logger.error(f"Failed operation {operation_id}: {error}")

    def clear_completed_operation(self) -> None:
        """Clear completed/failed operations (single-row design)."""
        state = self._load_state()
        if state and state["status"] in [
            IndexingStatus.COMPLETED.value,
            IndexingStatus.FAILED.value,
        ]:
            self._clear_state()

    def reset(self) -> None:
        """Reset all indexing state (for testing/maintenance)."""
        self._clear_state()
        self._current_operation_id = None

    # Private methods matching existing implementation
    def _save_state(self, **kwargs: Any) -> None:
        """Save state using existing single-row design."""
        query = (
            "INSERT INTO indexing_state "
            "(id, operation_type, status, checkpoint_data, started_at, updated_at, completed_at) "
            "VALUES (1, :operation_type, :status, :checkpoint_data, :started_at, :updated_at, :completed_at) "
            "ON CONFLICT(id) DO UPDATE SET "
            "operation_type=excluded.operation_type, status=excluded.status, "
            "checkpoint_data=excluded.checkpoint_data, "
            "started_at=excluded.started_at, updated_at=excluded.updated_at, "
            "completed_at=excluded.completed_at"
        )
        params = {
            "operation_type": kwargs["operation_type"],
            "status": kwargs["status"],
            "checkpoint_data": kwargs["checkpoint_data"],
            "started_at": kwargs["started_at"],
            "updated_at": kwargs["updated_at"],
            "completed_at": kwargs.get("completed_at"),
        }
        try:
            conn = self._db_service.get_connection()
            with conn.transaction():
                conn.execute(query, params)
        except Exception as e:
            logger.error(f"Failed to save indexing state: {e}")
            raise IndexingError(f"Failed to save state: {e}")

    def _load_state(self) -> Optional[dict[str, Any]]:
        """Load state using existing single-row design."""
        query = (
            "SELECT operation_type, status, checkpoint_data, started_at, updated_at, "
            "completed_at FROM indexing_state WHERE id = 1"
        )
        try:
            conn = self._db_service.get_connection()
            with conn.connect() as db:
                row = db.execute(query).fetchone()
                if not row:
                    return None
                return {
                    "operation_type": row[0],
                    "status": row[1],
                    "checkpoint_data": row[2],
                    "started_at": row[3],
                    "updated_at": row[4],
                    "completed_at": row[5],
                }
        except Exception as e:
            logger.error(f"Failed to load indexing state: {e}")
            return None

    def _clear_state(self) -> None:
        """Clear state (existing implementation)."""
        query = "DELETE FROM indexing_state WHERE id = 1"
        try:
            conn = self._db_service.get_connection()
            with conn.transaction():
                conn.execute(query)
        except Exception as e:
            logger.error(f"Failed to clear indexing state: {e}")


# TODO: Future migration to multi-row design
# 1. Add migration to remove CHECK constraint on id
# 2. Change operation_id from checkpoint to primary key
# 3. Add indexes on operation_type, status, started_at
# 4. Update queries to handle multiple rows
# This can be done without breaking existing code by:
# - Keeping single active operation constraint in code
# - Adding history queries as new methods

# TODO: Future migration to multi-row design
# 1. Add migration to remove CHECK constraint on id
# 2. Change operation_id from checkpoint to primary key
# 3. Add indexes on operation_type, status, started_at
# 4. Update queries to handle multiple rows
# This can be done without breaking existing code by:
# - Keeping single active operation constraint in code
# - Adding history queries as new methods
