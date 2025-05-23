"""Core Indexing Framework for Panoptikon.

Defines the IndexerServiceInterface, IndexerService, and indexing event types.
Implements service registration and event publication according to project standards.
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
import json
import logging
import os
from pathlib import Path
from typing import Any

from panoptikon.core.events import EventBase, EventBus
from panoptikon.core.service import ServiceContainer, ServiceInterface, ServiceLifetime
from panoptikon.database.query_builder import QueryBuilder
from panoptikon.database.service import DatabaseService

logger = logging.getLogger(__name__)


class IndexerServiceInterface(ServiceInterface):
    """Base interface for indexing services."""

    @abstractmethod
    def start_initial_indexing(self, paths: Sequence[str]) -> None:
        """Begin initial indexing of specified paths."""
        raise NotImplementedError

    @abstractmethod
    def start_incremental_indexing(self, paths: Sequence[str] | None = None) -> None:
        """Begin incremental indexing of specified paths, or all if None."""
        raise NotImplementedError

    @abstractmethod
    def pause_indexing(self) -> None:
        """Pause any ongoing indexing operations."""
        raise NotImplementedError

    @abstractmethod
    def resume_indexing(self) -> None:
        """Resume previously paused indexing operations."""
        raise NotImplementedError

    @abstractmethod
    def get_indexing_status(self) -> dict[str, Any]:
        """Return the current indexing status."""
        raise NotImplementedError


@dataclass
class IndexingStartedEvent(EventBase):
    """Event triggered when indexing begins."""

    operation: str = "initial"  # 'initial' or 'incremental'
    paths: list[str] | None = None


@dataclass
class IndexingProgressEvent(EventBase):
    """Event triggered periodically during indexing."""

    files_processed: int = 0
    total_files: int | None = None
    rate: float | None = None  # files per second
    estimated_completion: datetime | None = None


@dataclass
class IndexingCompletedEvent(EventBase):
    """Event triggered when indexing completes."""

    files_indexed: int = 0
    duration_ms: int | None = None
    operation: str = "initial"


@dataclass
class IndexingPausedEvent(EventBase):
    """Event triggered when indexing is paused."""

    reason: str | None = None


@dataclass
class IndexingResumedEvent(EventBase):
    """Event triggered when indexing is resumed."""

    pass


@dataclass
class IndexingErrorEvent(EventBase):
    """Event triggered when errors occur during indexing."""

    error_type: str = ""
    message: str = ""
    traceback: str | None = None


class IndexingStateManager:
    """Manages persistence and recovery of indexing state (Stage 6.1)."""

    def __init__(self, db_service: DatabaseService) -> None:
        """Initialize with a DatabaseService instance."""
        self._db_service = db_service

    def save_state(
        self,
        operation_type: str,
        status: str,
        checkpoint_data: dict[str, Any],
        started_at: int,
        updated_at: int,
        completed_at: int | None = None,
    ) -> None:
        """Save or update the current indexing state atomically."""
        data_json = json.dumps(checkpoint_data)
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
            "operation_type": operation_type,
            "status": status,
            "checkpoint_data": data_json,
            "started_at": started_at,
            "updated_at": updated_at,
            "completed_at": completed_at,
        }
        try:
            conn = self._db_service.get_connection()
            with conn.transaction():
                conn.execute(query, params)
        except Exception as e:
            logger.error(f"Failed to save indexing state: {e}")

    def load_state(self) -> dict[str, Any] | None:
        """Load the current indexing state, or None if not present."""
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
                checkpoint_data = json.loads(row[2]) if row[2] else {}
                return {
                    "operation_type": row[0],
                    "status": row[1],
                    "checkpoint_data": checkpoint_data,
                    "started_at": row[3],
                    "updated_at": row[4],
                    "completed_at": row[5],
                }
        except Exception as e:
            logger.error(f"Failed to load indexing state: {e}")
            return None

    def clear_state(self) -> None:
        """Clear the indexing state (after successful completion)."""
        query = "DELETE FROM indexing_state WHERE id = 1"
        try:
            conn = self._db_service.get_connection()
            with conn.transaction():
                conn.execute(query)
        except Exception as e:
            logger.error(f"Failed to clear indexing state: {e}")


class IndexerService(IndexerServiceInterface):
    """Concrete implementation of the IndexerServiceInterface."""

    def __init__(self, event_bus: EventBus, db_service: DatabaseService) -> None:
        """Initialize the indexer service with event bus and database service."""
        self._event_bus = event_bus
        self._status: dict[str, Any] = {
            "state": "idle",
            "files_processed": 0,
            "total_files": None,
            "rate": None,
            "estimated_completion": None,
        }
        self._paused = False
        self._state_manager = IndexingStateManager(db_service)

    def initialize(self) -> None:
        """Initialize the indexer service."""
        state = self._state_manager.load_state()
        if state:
            self._status = state["checkpoint_data"]
            self._status["state"] = state["status"]
            if state["status"] == "paused":
                self._paused = True
            if state["status"] == "indexing":
                self._event_bus.publish(
                    IndexingStartedEvent(
                        operation=state["operation_type"], paths=state["paths"]
                    )
                )

    def shutdown(self) -> None:
        """Shutdown the indexer service."""
        self._state_manager.clear_state()

    def start_initial_indexing(self, paths: Sequence[str]) -> None:
        """Begin initial indexing of specified paths."""
        self._status["state"] = "indexing"
        self._event_bus.publish(
            IndexingStartedEvent(operation="initial", paths=list(paths))
        )
        self._index_files(paths)

    def start_incremental_indexing(self, paths: Sequence[str] | None = None) -> None:
        """Begin incremental indexing of specified paths, or all if None."""
        self._status["state"] = "indexing"
        self._event_bus.publish(
            IndexingStartedEvent(
                operation="incremental", paths=list(paths) if paths else None
            )
        )
        self._index_files(paths)

    def pause_indexing(self) -> None:
        """Pause any ongoing indexing operations."""
        self._paused = True
        self._status["state"] = "paused"
        self._event_bus.publish(IndexingPausedEvent(reason="Paused by user"))
        self._state_manager.save_state(
            "incremental",
            self._status["state"],
            self._status,
            int(datetime.now().timestamp()),
            int(datetime.now().timestamp()),
        )

    def resume_indexing(self) -> None:
        """Resume previously paused indexing operations."""
        if self._paused:
            self._paused = False
            self._status["state"] = "indexing"
            self._event_bus.publish(IndexingResumedEvent())
            self._state_manager.save_state(
                "incremental",
                self._status["state"],
                self._status,
                int(datetime.now().timestamp()),
                int(datetime.now().timestamp()),
            )

    def get_indexing_status(self) -> dict[str, Any]:
        """Return the current indexing status."""
        return self._status.copy()

    def _index_files(self, paths: Sequence[str] | None = None) -> None:
        """Index files under specified paths, batching and checkpointing as per Stage 6.1."""
        BATCH_SIZE = 1000
        try:
            # Determine starting point from checkpoint if resuming
            state = self._state_manager.load_state()
            if state and state["status"] == "indexing":
                checkpoint = state["checkpoint_data"]
                files_processed = checkpoint.get("files_processed", 0)
                last_path = checkpoint.get("last_path")
                batch_num = checkpoint.get("batch_num", 0)
                resume = True
            else:
                files_processed = 0
                last_path = None
                batch_num = 0
                resume = False

            # Prepare list of all files to index
            all_files: list[Path] = []
            for root in paths or []:
                for dirpath, dirnames, filenames in os.walk(root):
                    for filename in filenames:
                        file_path = Path(dirpath) / filename
                        all_files.append(file_path)
            total_files = len(all_files)

            # If resuming, skip files up to last_path
            if resume and last_path:
                try:
                    last_idx = next(
                        i for i, p in enumerate(all_files) if str(p) == last_path
                    )
                    all_files = all_files[last_idx + 1 :]
                    files_processed = last_idx + 1
                except StopIteration:
                    pass  # If last_path not found, start from beginning

            # Batch and insert
            for i in range(0, len(all_files), BATCH_SIZE):
                batch = all_files[i : i + BATCH_SIZE]
                batch_data = [self._extract_metadata(p) for p in batch]
                sql, _ = QueryBuilder.build_insert("files", batch_data[0])
                # Use execute_many for batch insert
                self._db_service.execute_many(sql, batch_data)
                files_processed += len(batch)
                batch_num += 1
                last_path = str(batch[-1])
                # Checkpoint after each batch
                checkpoint_data = {
                    "files_processed": files_processed,
                    "last_path": last_path,
                    "batch_num": batch_num,
                }
                now = int(datetime.now().timestamp())
                self._state_manager.save_state(
                    operation_type="initial",
                    status="indexing",
                    checkpoint_data=checkpoint_data,
                    started_at=now if not resume else state["started_at"],
                    updated_at=now,
                )
                # Publish progress event
                self._event_bus.publish(
                    IndexingProgressEvent(
                        files_processed=files_processed,
                        total_files=total_files,
                        rate=None,  # Can be calculated if needed
                        estimated_completion=None,
                    )
                )
            # On completion
            duration = None  # Can be calculated if needed
            self._state_manager.clear_state()
            self._event_bus.publish(
                IndexingCompletedEvent(
                    files_indexed=files_processed,
                    duration_ms=duration,
                    operation="initial",
                )
            )
        except Exception as e:
            logger.error(f"Indexing error: {e}")
            # Publish error event and checkpoint
            self._event_bus.publish(
                IndexingErrorEvent(
                    error_type=type(e).__name__,
                    message=str(e),
                )
            )
            # Save checkpoint with error status
            now = int(datetime.now().timestamp())
            self._state_manager.save_state(
                operation_type="initial",
                status="error",
                checkpoint_data={
                    "files_processed": files_processed,
                    "last_path": last_path,
                    "batch_num": batch_num,
                },
                started_at=now if not resume else state["started_at"],
                updated_at=now,
            )

    def _extract_metadata(self, path: Path) -> dict[str, Any]:
        """Extract file metadata for indexing."""
        try:
            stat = path.stat()
            return {
                "name": path.name,
                "name_lower": path.name.lower(),
                "extension": path.suffix.lstrip(".").lower(),
                "path": str(path),
                "parent_path": str(path.parent),
                "size": stat.st_size,
                "folder_size": None,  # Only for directories, can be filled later
                "date_created": int(stat.st_ctime),
                "date_modified": int(stat.st_mtime),
                "file_type": "file" if path.is_file() else "directory",
                "is_directory": 1 if path.is_dir() else 0,
                "cloud_provider": None,  # Can be filled with cloud detection later
                "cloud_status": 0,  # 0=local, 1=downloaded, 2=cloud-only
                "indexed_at": int(datetime.now().timestamp()),
            }
        except Exception as e:
            logger.warning(f"Failed to extract metadata for {path}: {e}")
            return {
                "name": path.name,
                "name_lower": path.name.lower(),
                "extension": path.suffix.lstrip(".").lower(),
                "path": str(path),
                "parent_path": str(path.parent),
                "size": None,
                "folder_size": None,
                "date_created": None,
                "date_modified": None,
                "file_type": None,
                "is_directory": None,
                "cloud_provider": None,
                "cloud_status": None,
                "indexed_at": int(datetime.now().timestamp()),
            }


def register_indexer_service(
    container: ServiceContainer, event_bus: EventBus, db_service: DatabaseService
) -> None:
    """Register the IndexerService with the service container.

    Note: ServiceContainer requires a concrete class as the key when using a factory.
    Consumers should resolve the service using IndexerServiceInterface for type safety.
    """

    def factory(_: ServiceContainer) -> IndexerService:
        return IndexerService(event_bus, db_service)

    # Register using the concrete implementation as the key
    container.register(
        service_type=IndexerService,  # must be concrete for factory registration
        factory=factory,
        lifetime=ServiceLifetime.SINGLETON,
    )
    # Consumers should use container.resolve(IndexerServiceInterface) for type safety
