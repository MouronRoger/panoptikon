"""Result classes and interfaces for Panoptikon search engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol


class SearchResult(Protocol):
    """Individual search result representing a file match."""

    @property
    def name(self) -> str:
        """Get the filename."""
        ...

    @property
    def path(self) -> str:
        """Get the full path."""
        ...

    @property
    def metadata(self) -> dict[str, Any]:
        """Get file metadata."""
        ...

    def annotate(self, key: str, value: Any) -> None:
        """Add annotation to result."""
        ...


@dataclass
class SearchResultImpl:
    """Concrete implementation of SearchResult."""

    name: str
    path: str
    metadata: dict[str, Any] = field(default_factory=dict)
    _annotations: dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    def annotate(self, key: str, value: Any) -> None:
        """Add annotation to result."""
        self._annotations[key] = value

    @property
    def annotations(self) -> dict[str, Any]:
        """Get all annotations for this result."""
        return self._annotations.copy()


class ResultSet(Protocol):
    """Collection of search results with virtual paging."""

    def __init__(
        self,
        search_engine: Any,
        query_pattern: Any,
        total_count: int,
    ) -> None:
        """Initialize result set with search parameters."""
        ...

    def get_page(self, page_number: int, page_size: int = 100) -> list[SearchResult]:
        """Get specific page of results."""
        ...

    def get_total_count(self) -> int:
        """Get total number of results."""
        ...

    def group_by(
        self, key_function: Callable[[SearchResult], Any]
    ) -> dict[Any, list[SearchResult]]:
        """Group results using the provided key function."""
        ...


class ResultSetImpl:
    """Concrete implementation of ResultSet with virtual paging and grouping."""

    def __init__(
        self,
        search_engine: Any,
        query_pattern: Any,
        total_count: int,
        page_loader: Callable[[int, int], list[SearchResult]],
    ) -> None:
        """Initialize result set with search parameters.

        Args:
            search_engine: Reference to search engine.
            query_pattern: Original query pattern.
            total_count: Total number of results.
            page_loader: Function to load a page of results.
        """
        self._search_engine = search_engine
        self._query_pattern = query_pattern
        self._total_count = total_count
        self._page_loader = page_loader
        self._page_cache: dict[tuple[int, int], list[SearchResult]] = {}

    def get_page(self, page_number: int, page_size: int = 100) -> list[SearchResult]:
        """Get specific page of results."""
        key = (page_number, page_size)
        if key not in self._page_cache:
            self._page_cache[key] = self._page_loader(page_number, page_size)
        return self._page_cache[key]

    def get_total_count(self) -> int:
        """Get total number of results."""
        return self._total_count

    def group_by(
        self, key_function: Callable[[SearchResult], Any]
    ) -> dict[Any, list[SearchResult]]:
        """Group results using the provided key function."""
        all_results: list[SearchResult] = []
        page_size = 100
        for page_number in range((self._total_count + page_size - 1) // page_size):
            all_results.extend(self.get_page(page_number, page_size))
        groups: dict[Any, list[SearchResult]] = {}
        for result in all_results:
            key = key_function(result)
            groups.setdefault(key, []).append(result)
        return groups
