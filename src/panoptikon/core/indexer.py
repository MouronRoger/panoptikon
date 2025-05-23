"""Core Indexing Framework for Panoptikon.

Defines the IndexerServiceInterface, IndexerService, and indexing event types.
Implements service registration and event publication according to project standards.
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from panoptikon.core.events import EventBase, EventBus
from panoptikon.core.service import ServiceContainer, ServiceInterface, ServiceLifetime


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

    def __init__(self, event_bus: EventBus) -> None:
        """Initialize the indexer service with event bus."""
        self._event_bus = event_bus
        self._status: dict[str, Any] = {
            "state": "idle",
            "files_processed": 0,
            "total_files": None,
            "rate": None,
            "estimated_completion": None,
        }
        self._paused = False

    def initialize(self) -> None:
        """Initialize the indexer service."""
        pass

    def shutdown(self) -> None:
        """Shutdown the indexer service."""
        pass

    def start_initial_indexing(self, paths: Sequence[str]) -> None:
        """Begin initial indexing of specified paths."""
        self._status["state"] = "indexing"
        self._event_bus.publish(
            IndexingStartedEvent(operation="initial", paths=list(paths))
        )
        # TODO: Implement actual indexing logic

    def start_incremental_indexing(self, paths: Sequence[str] | None = None) -> None:
        """Begin incremental indexing of specified paths, or all if None."""
        self._status["state"] = "indexing"
        self._event_bus.publish(
            IndexingStartedEvent(
                operation="incremental", paths=list(paths) if paths else None
            )
        )
        # TODO: Implement actual incremental indexing logic

    def pause_indexing(self) -> None:
        """Pause any ongoing indexing operations."""
        self._paused = True
        self._status["state"] = "paused"
        self._event_bus.publish(IndexingPausedEvent(reason="Paused by user"))

    def resume_indexing(self) -> None:
        """Resume previously paused indexing operations."""
        if self._paused:
            self._paused = False
            self._status["state"] = "indexing"
            self._event_bus.publish(IndexingResumedEvent())

    def get_indexing_status(self) -> dict[str, Any]:
        """Return the current indexing status."""
        return self._status.copy()


def register_indexer_service(container: ServiceContainer, event_bus: EventBus) -> None:
    """Register the IndexerService with the service container.

    Note: ServiceContainer requires a concrete class as the key when using a factory.
    Consumers should resolve the service using IndexerServiceInterface for type safety.
    """

    def factory(_: ServiceContainer) -> IndexerService:
        return IndexerService(event_bus)

    # Register using the concrete implementation as the key
    container.register(
        service_type=IndexerService,  # must be concrete for factory registration
        factory=factory,
        lifetime=ServiceLifetime.SINGLETON,
    )
    # Consumers should use container.resolve(IndexerServiceInterface) for type safety
