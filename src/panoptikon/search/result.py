"""Result classes and interfaces for Panoptikon search engine."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
import threading
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
        max_cache_pages: int = 10,
    ) -> None:
        """Initialize result set with search parameters.

        Args:
            search_engine: Reference to search engine.
            query_pattern: Original query pattern.
            total_count: Total number of results.
            page_loader: Function to load a page of results.
            max_cache_pages: Maximum number of pages to cache in memory.
        """
        self._search_engine = search_engine
        self._query_pattern = query_pattern
        self._total_count = total_count
        self._page_loader = page_loader
        self._max_cache_pages = max_cache_pages
        self._page_cache: OrderedDict[tuple[int, int], list[SearchResult]] = (
            OrderedDict()
        )
        self._cache_lock = threading.Lock()
        self._stale: bool = False

    def get_page(self, page_number: int, page_size: int = 100) -> list[SearchResult]:
        """Get specific page of results. Raises ResultSetPageError on failure.

        Args:
            page_number: Zero-based page number.
            page_size: Number of results per page.

        Returns:
            List of SearchResult objects.

        Raises:
            ResultSetPageError: If page loading fails.
        """
        key = (page_number, page_size)
        with self._cache_lock:
            if self._stale:
                raise ResultSetStaleError(
                    "ResultSet is stale due to underlying data change."
                )
            if key in self._page_cache:
                self._page_cache.move_to_end(key)
                return self._page_cache[key]
            try:
                page = self._page_loader(page_number, page_size)
            except Exception as exc:
                raise ResultSetPageError(f"Failed to load page {key}: {exc}") from exc
            self._page_cache[key] = page
            if len(self._page_cache) > self._max_cache_pages:
                self._page_cache.popitem(last=False)
            return page

    def get_page_partial(
        self, page_number: int, page_size: int = 100
    ) -> tuple[list[SearchResult], Exception | None]:
        """Get a page of results, returning partial results and error if any.

        Args:
            page_number: Zero-based page number.
            page_size: Number of results per page.

        Returns:
            Tuple of (results, error). If error is None, results are complete.
        """
        try:
            results = self.get_page(page_number, page_size)
            return results, None
        except Exception as exc:
            # Try to return whatever is in cache
            key = (page_number, page_size)
            with self._cache_lock:
                partial = self._page_cache.get(key, [])
            return partial, exc

    def get_total_count(self) -> int:
        """Get total number of results."""
        return self._total_count

    def group_by(
        self, key_function: Callable[[SearchResult], Any]
    ) -> dict[Any, list[SearchResult]]:
        """Group results using the provided key function. Loads all pages as needed.

        Args:
            key_function: Function that returns grouping key.

        Returns:
            Dict mapping keys to lists of results.
        """
        all_results: list[SearchResult] = []
        page_size = 100
        for page_number in range((self._total_count + page_size - 1) // page_size):
            try:
                all_results.extend(self.get_page(page_number, page_size))
            except ResultSetPageError:
                continue  # Skip failed pages
        groups: dict[Any, list[SearchResult]] = {}
        for result in all_results:
            key = key_function(result)
            groups.setdefault(key, []).append(result)
        return groups

    def invalidate_cache(self) -> None:
        """Clear the page cache for this result set."""
        with self._cache_lock:
            self._page_cache.clear()

    def mark_stale(self) -> None:
        """Mark this result set as stale (e.g., if underlying data changes)."""
        with self._cache_lock:
            self._stale = True
            self._page_cache.clear()


class ResultSetPageError(Exception):
    """Raised when a page of results cannot be loaded."""


class ResultSetStaleError(Exception):
    """Raised when a ResultSet is stale due to underlying data change."""
