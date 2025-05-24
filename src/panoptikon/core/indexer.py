"""Core Indexing Framework for Panoptikon.

Defines the IndexerServiceInterface, IndexerService, and indexing event types.
Implements service registration and event publication according to project standards.
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
import logging
import os
from pathlib import Path
import time
from typing import Any, Optional

from panoptikon.core.events import EventBase, EventBus
from panoptikon.core.service import ServiceContainer, ServiceInterface, ServiceLifetime
from panoptikon.database.query_builder import QueryBuilder
from panoptikon.database.service import DatabaseService
from panoptikon.indexing.state_manager import (
    IndexingCheckpoint,
    IndexingOperationType,
    IndexingStateManager,
    IndexingStatus,
)

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


class IndexerService(IndexerServiceInterface):
    """Concrete implementation of the IndexerServiceInterface."""

    def __init__(self, event_bus: EventBus, db_service: DatabaseService) -> None:
        """Initialize the indexer service with event bus and database service."""
        self._event_bus = event_bus
        self._db_service = db_service
        self._state_manager = IndexingStateManager(db_service)
        self._current_operation_id: Optional[str] = None
        self._paused = False
        self._last_checkpoint_time = 0.0
        self._checkpoint_interval = 1.0  # Throttle to 1 second

    def initialize(self) -> None:
        """Initialize the indexer service."""
        active_op = self._state_manager.get_active_operation()
        if active_op:
            self._current_operation_id = active_op["checkpoint"].operation_id
            if active_op["status"] == IndexingStatus.PAUSED:
                self._paused = True
                logger.info(f"Found paused operation {self._current_operation_id}")
            elif active_op["status"] == IndexingStatus.IN_PROGRESS:
                logger.info(f"Found interrupted operation {self._current_operation_id}")

    def shutdown(self) -> None:
        """Shutdown the indexer service."""
        if self._current_operation_id:
            try:
                self._state_manager.pause_operation(self._current_operation_id)
            except Exception as e:
                logger.error(f"Failed to pause operation on shutdown: {e}")

    def start_initial_indexing(self, paths: Sequence[str]) -> None:
        """Begin initial indexing of specified paths."""
        try:
            active_op = self._state_manager.get_active_operation()
            if (
                active_op
                and active_op["operation_type"] == IndexingOperationType.INITIAL
            ):
                if self._should_resume_operation(active_op):
                    self._resume_indexing(active_op)
                    return
            total_files = self._estimate_total_files(paths)
            self._current_operation_id = self._state_manager.start_operation(
                IndexingOperationType.INITIAL, total_files=total_files
            )
            self._event_bus.publish(
                IndexingStartedEvent(operation="initial", paths=list(paths))
            )
            self._index_files(paths, total_files)
        except Exception as e:
            if self._current_operation_id:
                self._state_manager.fail_operation(self._current_operation_id, str(e))
            self._event_bus.publish(
                IndexingErrorEvent(
                    error_type=type(e).__name__,
                    message=str(e),
                )
            )
            raise

    def start_incremental_indexing(self, paths: Sequence[str] | None = None) -> None:
        """Begin incremental indexing of specified paths, or all if None."""
        try:
            active_op = self._state_manager.get_active_operation()
            if (
                active_op
                and active_op["operation_type"] == IndexingOperationType.INCREMENTAL
            ):
                if self._should_resume_operation(active_op):
                    self._resume_indexing(active_op)
                    return
            total_files = self._estimate_total_files(paths) if paths else None
            self._current_operation_id = self._state_manager.start_operation(
                IndexingOperationType.INCREMENTAL, total_files=total_files
            )
            self._event_bus.publish(
                IndexingStartedEvent(
                    operation="incremental", paths=list(paths) if paths else None
                )
            )
            self._index_files(paths, total_files)
        except Exception as e:
            if self._current_operation_id:
                self._state_manager.fail_operation(self._current_operation_id, str(e))
            self._event_bus.publish(
                IndexingErrorEvent(
                    error_type=type(e).__name__,
                    message=str(e),
                )
            )
            raise

    def pause_indexing(self) -> None:
        """Pause any ongoing indexing operations."""
        if self._current_operation_id and not self._paused:
            self._paused = True
            self._state_manager.pause_operation(self._current_operation_id)
            self._event_bus.publish(IndexingPausedEvent(reason="User requested"))

    def resume_indexing(self) -> None:
        """Resume previously paused indexing operations."""
        if self._current_operation_id and self._paused:
            checkpoint = self._state_manager.resume_operation(
                self._current_operation_id
            )
            self._paused = False
            self._event_bus.publish(IndexingResumedEvent())
            self._index_files_from_checkpoint(checkpoint)

    def get_indexing_status(self) -> dict[str, Any]:
        """Return the current indexing status."""
        active_op = self._state_manager.get_active_operation()
        if active_op:
            checkpoint = active_op["checkpoint"]
            return {
                "state": active_op["status"].value,
                "operation_id": active_op["operation_id"],
                "operation_type": active_op["operation_type"].value,
                "files_processed": checkpoint.files_processed,
                "total_files": checkpoint.total_files,
                "rate": checkpoint.rate,
                "current_path": checkpoint.current_path,
                "errors": len(checkpoint.errors),
                "started_at": active_op["started_at"],
                "duration": checkpoint.duration,
            }
        # If no active operation, check for last operation (completed/failed)
        last_op = self._state_manager.get_last_operation()
        if last_op and last_op["status"] in [
            IndexingStatus.COMPLETED,
            IndexingStatus.FAILED,
        ]:
            checkpoint = last_op["checkpoint"]
            return {
                "state": last_op["status"].value,
                "operation_id": last_op["operation_id"],
                "operation_type": last_op["operation_type"].value,
                "files_processed": checkpoint.files_processed,
                "total_files": checkpoint.total_files,
                "rate": checkpoint.rate,
                "current_path": checkpoint.current_path,
                "errors": len(checkpoint.errors),
                "started_at": last_op["started_at"],
                "duration": checkpoint.duration,
            }
        else:
            return {
                "state": "idle",
                "operation_id": None,
                "files_processed": 0,
                "total_files": None,
                "rate": None,
                "errors": 0,
            }

    def _maybe_update_checkpoint(
        self, files_processed: int, current_path: str, last_file: str, batch_num: int
    ) -> None:
        """Update checkpoint with throttling to avoid excessive DB writes."""
        now = time.time()
        if now - self._last_checkpoint_time >= self._checkpoint_interval:
            self._state_manager.update_checkpoint(
                self._current_operation_id,
                files_processed=files_processed,
                current_path=current_path,
                last_file=last_file,
                batch_num=batch_num,
            )
            self._last_checkpoint_time = now

    def _estimate_total_files(self, paths: Sequence[str]) -> int:
        """Quick estimation of total files to index."""
        total = 0
        for root in paths:
            for _, _, files in os.walk(root):
                total += len(files)
        return total

    def _should_resume_operation(self, operation: dict[str, Any]) -> bool:
        """Determine if we should resume an operation (could prompt user in future)."""
        age = datetime.now() - operation["started_at"]
        return age.total_seconds() < 86400

    def _resume_indexing(self, operation: dict[str, Any]) -> None:
        """Resume an interrupted indexing operation."""
        checkpoint = operation["checkpoint"]
        self._current_operation_id = checkpoint.operation_id
        self._state_manager.resume_operation(checkpoint.operation_id)
        self._event_bus.publish(IndexingResumedEvent())
        self._index_files_from_checkpoint(checkpoint)

    def _index_files_from_checkpoint(self, checkpoint: IndexingCheckpoint) -> None:
        """Continue indexing from a checkpoint."""
        logger.info(
            f"Resuming from {checkpoint.files_processed} files, "
            f"last: {checkpoint.last_processed_file}"
        )
        self._index_files(None, checkpoint.total_files, resume_from=checkpoint)

    def _index_files(
        self,
        paths: Sequence[str] | None = None,
        total_files: int | None = None,
        resume_from: IndexingCheckpoint | None = None,
    ) -> None:
        """Index files with enhanced checkpoint management."""
        BATCH_SIZE = 1000
        try:
            if resume_from:
                files_processed = resume_from.files_processed
                last_path = resume_from.last_processed_file
                batch_num = resume_from.batch_num
            else:
                files_processed = 0
                last_path = None
                batch_num = 0
            all_files: list[Path] = []
            for root in paths or []:
                for dirpath, dirnames, filenames in os.walk(root):
                    for filename in filenames:
                        file_path = Path(dirpath) / filename
                        all_files.append(file_path)
            if total_files is None:
                total_files = len(all_files)
            if resume_from and last_path:
                try:
                    last_idx = next(
                        i for i, p in enumerate(all_files) if str(p) == last_path
                    )
                    all_files = all_files[last_idx + 1 :]
                    files_processed = last_idx + 1
                except StopIteration:
                    pass
            for i in range(0, len(all_files), BATCH_SIZE):
                if self._paused:
                    break
                batch = all_files[i : i + BATCH_SIZE]
                batch_data = [self._extract_metadata(p) for p in batch]
                sql, _ = QueryBuilder.build_insert("files", batch_data[0])
                self._db_service.execute_many(sql, batch_data)
                files_processed += len(batch)
                batch_num += 1
                last_path = str(batch[-1])
                self._maybe_update_checkpoint(
                    files_processed=files_processed,
                    current_path=str(batch[-1].parent),
                    last_file=last_path,
                    batch_num=batch_num,
                )
                self._event_bus.publish(
                    IndexingProgressEvent(
                        files_processed=files_processed,
                        total_files=total_files,
                        rate=None,
                        estimated_completion=None,
                    )
                )
            if not self._paused and self._current_operation_id:
                self._state_manager.complete_operation(
                    self._current_operation_id, {"files_indexed": files_processed}
                )
                self._event_bus.publish(
                    IndexingCompletedEvent(
                        files_indexed=files_processed,
                        duration_ms=None,
                        operation="initial",
                    )
                )
                self._current_operation_id = None
        except Exception as e:
            logger.error(f"Indexing error: {e}")
            if self._current_operation_id:
                self._state_manager.fail_operation(self._current_operation_id, str(e))
            self._event_bus.publish(
                IndexingErrorEvent(
                    error_type=type(e).__name__,
                    message=str(e),
                )
            )
            raise

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
