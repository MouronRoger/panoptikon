"""Sorting system for Panoptikon search results (Stage 5.4).

Implements flexible, high-performance sorting for search results, supporting
multi-key, direction, custom comparators, and folder size handling.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import functools
from typing import Any, Callable, TypeVar

from panoptikon.search.result import SearchResult

T = TypeVar("T", bound=SearchResult)


class SortCriteria(ABC):
    """Abstract base class for sort criteria."""

    @abstractmethod
    def apply_to_query(self, query: Any, direction: str = "asc") -> Any:
        """Apply sort to database query.

        Args:
            query: Database query to modify.
            direction: 'asc' or 'desc'.

        Returns:
            Modified query with sort applied.
        """
        pass

    @abstractmethod
    def compare(self, result1: SearchResult, result2: SearchResult) -> int:
        """Compare two results for client-side sorting.

        Args:
            result1: First SearchResult.
            result2: Second SearchResult.

        Returns:
            -1, 0, or 1 (less, equal, greater).
        """
        pass


class AttributeSortCriteria(SortCriteria):
    """Sort criteria for a specific SearchResult attribute."""

    def __init__(self, attribute: str) -> None:
        """Initialize AttributeSortCriteria with the attribute name."""
        self.attribute = attribute

    def apply_to_query(self, query: Any, direction: str = "asc") -> Any:
        """Apply sort to database query (placeholder)."""
        return query  # To be implemented in integration

    def compare(self, result1: SearchResult, result2: SearchResult) -> int:
        """Compare two results by the specified attribute."""
        v1 = getattr(result1, self.attribute, None)
        v2 = getattr(result2, self.attribute, None)
        if v1 is None and v2 is None:
            return 0
        if v1 is None:
            return -1
        if v2 is None:
            return 1
        return int((v1 > v2) - (v1 < v2))


class CustomSortCriteria(SortCriteria):
    """Sort criteria using a custom comparison function."""

    def __init__(self, compare_fn: Callable[[SearchResult, SearchResult], int]) -> None:
        """Initialize CustomSortCriteria with a comparison function."""
        self.compare_fn = compare_fn

    def apply_to_query(self, query: Any, direction: str = "asc") -> Any:
        """Cannot push custom sort to DB; must be client-side."""
        return query

    def compare(self, result1: SearchResult, result2: SearchResult) -> int:
        """Compare two results using the custom function."""
        return self.compare_fn(result1, result2)


class FolderSizeSortCriteria(SortCriteria):
    """Sort criteria for folder size, handling missing or pending values."""

    def __init__(self) -> None:
        """Initialize FolderSizeSortCriteria."""
        pass

    def apply_to_query(self, query: Any, direction: str = "asc") -> Any:
        """Apply sort to database query (placeholder)."""
        return query  # To be implemented in integration

    def compare(self, result1: SearchResult, result2: SearchResult) -> int:
        """Compare two results by folder size, handling None as smallest."""
        size1 = result1.metadata.get("folder_size")
        size2 = result2.metadata.get("folder_size")
        if size1 is None and size2 is None:
            return 0
        if size1 is None:
            return -1
        if size2 is None:
            return 1
        return int((size1 > size2) - (size1 < size2))


class SortingEngine:
    """Engine for applying sorts to result sets."""

    def apply_sort(
        self,
        result_set: list[SearchResult],
        criteria: SortCriteria | list[SortCriteria],
        direction: str = "asc",
    ) -> list[SearchResult]:
        """Apply sort criteria to result set.

        Args:
            result_set: ResultSet to sort.
            criteria: SortCriteria or list of criteria.
            direction: 'asc' or 'desc'.

        Returns:
            Sorted list of SearchResult.
        """
        if not result_set:
            return list(result_set)
        criteria_list = [criteria] if isinstance(criteria, SortCriteria) else criteria
        # If any criteria is a CustomSortCriteria, use cmp_to_key with compare
        if any(isinstance(crit, CustomSortCriteria) for crit in criteria_list):

            def cmp(a: SearchResult, b: SearchResult) -> int:
                for crit in criteria_list:
                    res = crit.compare(a, b)
                    if res != 0:
                        return res
                return 0

            reverse = direction == "desc"
            return sorted(result_set, key=functools.cmp_to_key(cmp), reverse=reverse)
        reverse = direction == "desc"
        return sorted(
            result_set,
            key=lambda x: SortKey(x, criteria_list, direction),
            reverse=reverse,
        )

    def create_sort_criteria(
        self,
        attribute: str,
        custom_fn: Callable[[SearchResult, SearchResult], int] | None = None,
    ) -> SortCriteria:
        """Create sort criteria for specified attribute or custom function.

        Args:
            attribute: Attribute to sort by.
            custom_fn: Optional custom comparison function.

        Returns:
            SortCriteria instance.
        """
        if custom_fn is not None:
            return CustomSortCriteria(custom_fn)
        return AttributeSortCriteria(attribute)


class SortKey:
    """Helper for multi-key sorting using SortCriteria."""

    def __init__(
        self, result: SearchResult, criteria: list[SortCriteria], direction: str
    ) -> None:
        """Initialize SortKey with result, criteria, and direction."""
        self.result = result
        self.criteria = criteria
        self.direction = direction
        self.values = [self._get_value(crit) for crit in criteria]

    def _get_value(self, crit: SortCriteria) -> Any:
        """Get a comparable value for the given sort criteria."""
        if isinstance(crit, AttributeSortCriteria):
            v = getattr(self.result, crit.attribute, None)
        elif isinstance(crit, FolderSizeSortCriteria):
            v = self.result.metadata.get("folder_size")
        else:
            v = None
        if v is None:
            # For ascending, None sorts first; for descending, last
            return float("-inf") if self.direction == "asc" else float("inf")
        return v

    def __lt__(self, other: object) -> bool:
        """Return True if self < other for sorting purposes."""
        if not isinstance(other, SortKey):
            return NotImplemented
        for v1, v2 in zip(self.values, other.values):
            if v1 != v2:
                return bool(v1 < v2)
        return False

    def __eq__(self, other: object) -> bool:
        """Return True if self == other for sorting purposes."""
        if not isinstance(other, SortKey):
            return NotImplemented
        return self.values == other.values
