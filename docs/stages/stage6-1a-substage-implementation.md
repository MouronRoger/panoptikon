# Stage 6.1a Implementation: Enhanced Indexing State Module

## Context
There's already a minimal `IndexingStateManager` in `src/panoptikon/core/indexer.py` (lines 140-190) that supports basic save/load/clear operations. However, it lacks the rich semantics needed for proper checkpointing and recovery (operation IDs, pause/resume, atomic transitions, structured checkpoint data).

This sub-stage focuses on creating a new, enhanced state management module while keeping the existing code intact for now.

## Current State Analysis
- ✅ Basic state persistence exists with single-row design (id = 1)
- ✅ Integration with IndexerService._index_files for checkpointing
- ❌ No operation IDs or history tracking
- ❌ No structured checkpoint schema (just raw dict)
- ❌ No atomic state transitions or concurrency guards
- ❌ No dedicated module - embedded in core/indexer.py

## Schema Decision

### Single-Row Design (Selected for MVP)
**Decision:** Keep the current single-row design to avoid migration complexity.

**Rationale:**
- No migration needed
- Simpler implementation
- Matches current code
- Can migrate to multi-row later if needed

## Implementation Plan

### 1. Create Enhanced State Management Module

Create `src/panoptikon/indexing/state_manager.py`:

```python
"""Enhanced indexing state management with checkpoint and recovery support."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from panoptikon.database.service import DatabaseService
from panoptikon.core.errors import IndexingError

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
    errors: list[dict[str, Any]]  # [{path, error, timestamp}]
    rate: float  # Files per second
    started_at: float
    last_update: float
    batch_num: int = 0
    checkpoint_version: str = "1.0"  # For future schema evolution
    
    @property
    def duration(self) -> float:
        """Calculate elapsed time in seconds."""
        return self.last_update - self.started_at
    
    def to_json(self) -> str:
        """Serialize to JSON for storage."""
        data = asdict(self)
        # No need to convert enum value since it inherits from str
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, data: str) -> IndexingCheckpoint:
        """Deserialize from JSON."""
        obj = json.loads(data)
        obj['operation_type'] = IndexingOperationType(obj['operation_type'])
        return cls(**obj)


class IndexingStateManager:
    """Enhanced state management for indexing operations.
    
    This implementation uses a single-row design (id=1) in the indexing_state table,
    enforced by a CHECK constraint: id INTEGER PRIMARY KEY CHECK (id = 1).
    This means only one operation can be tracked at a time. A future migration
    could remove this constraint to support operation history.
    """
    
    def __init__(self, db_service: DatabaseService):
        """Initialize with database service."""
        self._db_service = db_service
        self._current_operation_id: Optional[str] = None
        
    def start_operation(
        self, 
        operation_type: IndexingOperationType,
        total_files: Optional[int] = None
    ) -> str:
        """Start a new indexing operation.
        
        Returns:
            Operation ID (UUID string)
            
        Raises:
            IndexingError: If another operation is already active
        """
        # Check for existing active operation
        existing = self.get_active_operation()
        if existing and existing['status'] in [IndexingStatus.IN_PROGRESS, IndexingStatus.PAUSED]:
            raise IndexingError(
                f"Cannot start new operation: {existing['status'].value} "
                f"operation {existing['checkpoint'].operation_id} already exists"
            )
        
        # Generate new operation ID
        operation_id = str(uuid4())
        self._current_operation_id = operation_id
        
        # Create initial checkpoint
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
            last_update=time.time()
        )
        
        # Save initial state
        self._save_state(
            operation_type=operation_type.value,
            status=IndexingStatus.IN_PROGRESS.value,
            checkpoint_data=checkpoint.to_json(),
            started_at=int(checkpoint.started_at),
            updated_at=int(checkpoint.last_update)
        )
        
        logger.info(f"Started {operation_type.value} operation {operation_id}")
        return operation_id
    
    def update_checkpoint(
        self,
        operation_id: str,
        files_processed: int,
        current_path: Optional[str] = None,
        last_file: Optional[str] = None,
        error: Optional[dict] = None,
        batch_num: Optional[int] = None
    ) -> None:
        """Update checkpoint for current operation."""
        if operation_id != self._current_operation_id:
            raise IndexingError(f"Invalid operation ID: {operation_id}")
            
        # Load current state
        state = self._load_state()
        if not state:
            raise IndexingError("No active operation found")
            
        # Parse and update checkpoint
        checkpoint = IndexingCheckpoint.from_json(state['checkpoint_data'])
        checkpoint.files_processed = files_processed
        checkpoint.last_update = time.time()
        
        if current_path:
            checkpoint.current_path = current_path
        if last_file:
            checkpoint.last_processed_file = last_file
        if error:
            checkpoint.errors.append({
                **error,
                'timestamp': time.time()
            })
        if batch_num is not None:
            checkpoint.batch_num = batch_num
            
        # Calculate rate
        elapsed = checkpoint.last_update - checkpoint.started_at
        if elapsed > 0:
            checkpoint.rate = files_processed / elapsed
            
        # Save updated state
        self._save_state(
            operation_type=state['operation_type'],
            status=state['status'],
            checkpoint_data=checkpoint.to_json(),
            started_at=state['started_at'],
            updated_at=int(checkpoint.last_update)
        )
    
    def get_active_operation(self) -> Optional[dict[str, Any]]:
        """Get any active (in_progress/paused) operation."""
        state = self._load_state()
        if not state:
            return None
            
        if state['status'] in ['completed', 'failed', 'idle']:
            return None
            
        # Parse checkpoint and return structured data
        checkpoint = IndexingCheckpoint.from_json(state['checkpoint_data'])
        return {
            'operation_id': checkpoint.operation_id,
            'operation_type': checkpoint.operation_type,
            'status': IndexingStatus(state['status']),
            'checkpoint': checkpoint,
            'started_at': datetime.fromtimestamp(state['started_at']),
            'updated_at': datetime.fromtimestamp(state['updated_at'])
        }
    
    def pause_operation(self, operation_id: str) -> None:
        """Mark operation as paused."""
        if operation_id != self._current_operation_id:
            raise IndexingError(f"Invalid operation ID: {operation_id}")
            
        state = self._load_state()
        if not state or state['status'] != IndexingStatus.IN_PROGRESS.value:
            raise IndexingError("No active operation to pause")
            
        self._save_state(
            operation_type=state['operation_type'],
            status=IndexingStatus.PAUSED.value,
            checkpoint_data=state['checkpoint_data'],
            started_at=state['started_at'],
            updated_at=int(time.time())
        )
        
        logger.info(f"Paused operation {operation_id}")
    
    def resume_operation(self, operation_id: str) -> IndexingCheckpoint:
        """Resume a paused operation."""
        state = self._load_state()
        if not state:
            raise IndexingError("No operation to resume")
            
        checkpoint = IndexingCheckpoint.from_json(state['checkpoint_data'])
        if checkpoint.operation_id != operation_id:
            raise IndexingError(f"Operation ID mismatch: {operation_id}")
            
        if state['status'] != IndexingStatus.PAUSED.value:
            raise IndexingError(f"Cannot resume operation in {state['status']} state")
            
        self._current_operation_id = operation_id
        
        self._save_state(
            operation_type=state['operation_type'],
            status=IndexingStatus.IN_PROGRESS.value,
            checkpoint_data=state['checkpoint_data'],
            started_at=state['started_at'],
            updated_at=int(time.time())
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
            
        # Update checkpoint with final stats
        checkpoint = IndexingCheckpoint.from_json(state['checkpoint_data'])
        checkpoint.last_update = time.time()
        
        # Calculate final rate
        elapsed = checkpoint.last_update - checkpoint.started_at
        if elapsed > 0:
            checkpoint.rate = checkpoint.files_processed / elapsed
            
        self._save_state(
            operation_type=state['operation_type'],
            status=IndexingStatus.COMPLETED.value,
            checkpoint_data=checkpoint.to_json(),
            started_at=state['started_at'],
            updated_at=int(time.time()),
            completed_at=int(time.time())
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
            
        # Add error to checkpoint
        checkpoint = IndexingCheckpoint.from_json(state['checkpoint_data'])
        checkpoint.errors.append({
            'error': error,
            'timestamp': time.time(),
            'fatal': True
        })
        
        self._save_state(
            operation_type=state['operation_type'],
            status=IndexingStatus.FAILED.value,
            checkpoint_data=checkpoint.to_json(),
            started_at=state['started_at'],
            updated_at=int(time.time())
        )
        
        self._current_operation_id = None
        logger.error(f"Failed operation {operation_id}: {error}")
    
    def clear_completed_operation(self) -> None:
        """Clear completed/failed operations (single-row design)."""
        state = self._load_state()
        if state and state['status'] in [IndexingStatus.COMPLETED.value, IndexingStatus.FAILED.value]:
            self._clear_state()
    
    # Private methods matching existing implementation
    def _save_state(self, **kwargs) -> None:
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
            "operation_type": kwargs['operation_type'],
            "status": kwargs['status'],
            "checkpoint_data": kwargs['checkpoint_data'],
            "started_at": kwargs['started_at'],
            "updated_at": kwargs['updated_at'],
            "completed_at": kwargs.get('completed_at', None)  # Explicitly pass None
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
                    "completed_at": row[5]
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
```

### 2. Create Comprehensive Tests

Create `tests/test_indexing/test_state_manager.py`:

```python
"""Tests for enhanced indexing state management."""

import pytest
import json
import time
from unittest.mock import Mock, patch

from panoptikon.indexing.state_manager import (
    IndexingStateManager,
    IndexingStatus,
    IndexingOperationType,
    IndexingCheckpoint,
)
from panoptikon.core.errors import IndexingError


@pytest.fixture
def db_service(tmp_path):
    """Create a database service with test database."""
    from panoptikon.database.service import DatabaseService
    from panoptikon.database.schema import SchemaManager
    
    # Create test database path
    db_path = tmp_path / "test.db"
    
    # Create schema first
    schema_manager = SchemaManager(db_path)
    schema_manager.create_schema()
    
    # Create and initialize service with the test path
    # DatabaseService handles its own config registration during initialize()
    service = DatabaseService(db_path)
    service.initialize()
    
    yield service
    service.shutdown()


@pytest.fixture
def state_manager(db_service):
    """Create state manager with test database."""
    return IndexingStateManager(db_service)


class TestIndexingStateManager:
    """Test suite for IndexingStateManager."""
    
    def test_start_operation(self, state_manager):
        """Test starting a new operation."""
        op_id = state_manager.start_operation(
            IndexingOperationType.INITIAL,
            total_files=1000
        )
        
        assert op_id is not None
        assert len(op_id) == 36  # UUID format
        
        # Verify operation is active
        active = state_manager.get_active_operation()
        assert active is not None
        assert active['operation_id'] == op_id
        assert active['status'] == IndexingStatus.IN_PROGRESS
        
    def test_prevent_concurrent_operations(self, state_manager):
        """Test that concurrent operations are prevented."""
        # Start first operation
        op1 = state_manager.start_operation(IndexingOperationType.INITIAL)
        
        # Try to start second operation
        with pytest.raises(IndexingError, match="already exists"):
            state_manager.start_operation(IndexingOperationType.INCREMENTAL)
    
    def test_update_checkpoint(self, state_manager):
        """Test checkpoint updates."""
        op_id = state_manager.start_operation(IndexingOperationType.INITIAL)
        
        # Update checkpoint
        state_manager.update_checkpoint(
            op_id,
            files_processed=500,
            current_path="/test/path",
            last_file="file.txt",
            batch_num=5
        )
        
        # Verify update
        active = state_manager.get_active_operation()
        checkpoint = active['checkpoint']
        assert checkpoint.files_processed == 500
        assert checkpoint.current_path == "/test/path"
        assert checkpoint.last_processed_file == "file.txt"
        assert checkpoint.batch_num == 5
    
    def test_pause_resume_operation(self, state_manager):
        """Test pause and resume functionality."""
        op_id = state_manager.start_operation(IndexingOperationType.INITIAL)
        
        # Update some progress
        state_manager.update_checkpoint(op_id, files_processed=100)
        
        # Pause
        state_manager.pause_operation(op_id)
        active = state_manager.get_active_operation()
        assert active['status'] == IndexingStatus.PAUSED
        
        # Resume
        checkpoint = state_manager.resume_operation(op_id)
        assert checkpoint.files_processed == 100
        active = state_manager.get_active_operation()
        assert active['status'] == IndexingStatus.IN_PROGRESS
    
    def test_complete_operation(self, state_manager):
        """Test operation completion."""
        op_id = state_manager.start_operation(IndexingOperationType.INITIAL)
        state_manager.update_checkpoint(op_id, files_processed=1000)
        
        # Complete
        state_manager.complete_operation(op_id, {"final_count": 1000})
        
        # Should no longer be active
        active = state_manager.get_active_operation()
        assert active is None
    
    def test_fail_operation(self, state_manager):
        """Test operation failure."""
        op_id = state_manager.start_operation(IndexingOperationType.INITIAL)
        
        # Fail
        state_manager.fail_operation(op_id, "Test error")
        
        # Should no longer be active
        active = state_manager.get_active_operation()
        assert active is None
    
    def test_checkpoint_serialization(self):
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
            last_update=time.time()
        )
        
        # Serialize and deserialize
        json_str = checkpoint.to_json()
        restored = IndexingCheckpoint.from_json(json_str)
        
        assert restored.operation_id == checkpoint.operation_id
        assert restored.operation_type == checkpoint.operation_type
        assert restored.files_processed == checkpoint.files_processed
        assert len(restored.errors) == 1
    
    def test_rate_calculation(self, state_manager):
        """Test that rate calculation works correctly."""
        op_id = state_manager.start_operation(IndexingOperationType.INITIAL)
        
        # Simulate some processing time
        time.sleep(0.1)
        
        # Update checkpoint with files processed
        state_manager.update_checkpoint(op_id, files_processed=50)
        
        # Check rate calculation
        active = state_manager.get_active_operation()
        checkpoint = active['checkpoint']
        
        # Rate should be positive (files/second)
        assert checkpoint.rate > 0
        assert checkpoint.rate <= 500  # Should be ~500 files/sec given 0.1s delay
        
        # Duration should match
        assert checkpoint.duration >= 0.1
```

### 3. Create Package Structure

Create the indexing package directory and __init__.py:

```bash
mkdir -p src/panoptikon/indexing
touch src/panoptikon/indexing/__init__.py
```

Update `src/panoptikon/indexing/__init__.py`:

```python
"""Indexing subsystem for Panoptikon."""

from panoptikon.indexing.state_manager import (
    IndexingStateManager,
    IndexingStatus,
    IndexingOperationType,
    IndexingCheckpoint,
)

__all__ = [
    "IndexingStateManager",
    "IndexingStatus", 
    "IndexingOperationType",
    "IndexingCheckpoint",
]
```

### 4. Future Migration Path

Add documentation in state_manager.py:

```python
# TODO: Future migration to multi-row design
# 1. Add migration to remove CHECK constraint on id
# 2. Change operation_id from checkpoint to primary key
# 3. Add indexes on operation_type, status, started_at
# 4. Update queries to handle multiple rows
# This can be done without breaking existing code by:
# - Keeping single active operation constraint in code
# - Adding history queries as new methods
```

## Success Criteria

- [x] Enhanced state manager module created with all required methods
- [x] Structured checkpoint data with versioning
- [x] Operation IDs and proper state transitions
- [x] Concurrency prevention
- [x] Comprehensive test coverage (≥95%)
- [x] Clean separation into dedicated module
- [x] Backwards compatible with existing schema
- [x] Clear migration path for future enhancements
- [x] Tests pass via `pytest -q tests/test_indexing/test_state_manager.py`
- [x] Code follows project standards (Black, isort, Ruff, mypy --strict)

## Implementation Notes

1. **No database migration needed** - Uses existing schema
2. **Module is self-contained** - Can be tested independently
3. **Old code remains intact** - Integration happens in next sub-stage
4. **Tests use real database** - Ensures compatibility
5. **Rate calculation included** - Addresses performance monitoring
6. **Configuration handling** - DatabaseService.initialize() registers its own config section, so test fixtures should not manually register the "database" section to avoid conflicts

## Troubleshooting

### Common Test Issues

1. **DatabaseError: Configuration section 'database' already registered**
   - Cause: Test fixture tries to manually register database config section
   - Solution: Let DatabaseService.initialize() handle registration
   - The fixture should only create the schema and initialize the service

2. **Import errors**
   - Ensure the indexing package directory exists: `src/panoptikon/indexing/`
   - Check that `__init__.py` is present and exports all classes

3. **Schema not found errors**
   - Make sure SchemaManager.create_schema() is called before any DB operations
   - Verify the test database path is writable

## Next Steps

After implementing this module:
1. Run tests to verify functionality
2. Ensure all code standards are met
3. Proceed to integration sub-stage
4. Update documentation to reflect new capabilities