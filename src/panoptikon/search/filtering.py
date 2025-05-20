"""Filtering system for Panoptikon search results (Stage 5.5).

Implements modular, high-performance filtering for search results, supporting
file type, extension, date, size, path, and composite filter logic (AND/OR/NOT).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime
from typing import Any, List, Optional

from panoptikon.search.result import SearchResult


class FilterCriteria(ABC):
    """Abstract base class for filter criteria."""

    @abstractmethod
    def apply_to_query(self, query: Any) -> Any:
        """Apply filter to database query (e.g., add WHERE clause).

        Args:
            query: Database query to modify.

        Returns:
            Modified query with filter applied.
        """
        pass

    @abstractmethod
    def matches(self, result: SearchResult) -> bool:
        """Check if result matches filter (client-side).

        Args:
            result: SearchResult to check.

        Returns:
            True if result matches, False otherwise.
        """
        pass


class FileTypeFilter(FilterCriteria):
    """Filter by file type (e.g., 'file', 'directory')."""

    def __init__(self, file_type: str) -> None:
        self.file_type = file_type

    def apply_to_query(self, query: Any) -> Any:
        # Example: query = query.where(file_type=...)
        # Placeholder: actual integration with query builder needed
        return query

    def matches(self, result: SearchResult) -> bool:
        return result.metadata.get("file_type") == self.file_type


class ExtensionFilter(FilterCriteria):
    """Filter by file extension (e.g., 'txt', 'pdf')."""

    def __init__(self, extension: str) -> None:
        self.extension = extension.lower()

    def apply_to_query(self, query: Any) -> Any:
        return query

    def matches(self, result: SearchResult) -> bool:
        return result.metadata.get("extension", "").lower() == self.extension


class DateRangeFilter(FilterCriteria):
    """Filter by created/modified date range."""

    def __init__(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        field: str = "date_modified",
    ) -> None:
        self.start = start
        self.end = end
        self.field = field

    def apply_to_query(self, query: Any) -> Any:
        return query

    def matches(self, result: SearchResult) -> bool:
        value = result.metadata.get(self.field)
        if value is None:
            return False
        try:
            dt = (
                value
                if isinstance(value, datetime)
                else datetime.fromisoformat(str(value))
            )
        except Exception:
            return False
        if self.start and dt < self.start:
            return False
        if self.end and dt > self.end:
            return False
        return True


class SizeRangeFilter(FilterCriteria):
    """Filter by file size range (bytes)."""

    def __init__(
        self, min_size: Optional[int] = None, max_size: Optional[int] = None
    ) -> None:
        self.min_size = min_size
        self.max_size = max_size

    def apply_to_query(self, query: Any) -> Any:
        return query

    def matches(self, result: SearchResult) -> bool:
        size = result.metadata.get("size")
        if size is None:
            return False
        if self.min_size is not None and size < self.min_size:
            return False
        if self.max_size is not None and size > self.max_size:
            return False
        return True


class PathFilter(FilterCriteria):
    """Filter by path substring or prefix."""

    def __init__(self, substring: str) -> None:
        self.substring = substring

    def apply_to_query(self, query: Any) -> Any:
        return query

    def matches(self, result: SearchResult) -> bool:
        return self.substring in result.path


class CompositeFilter(FilterCriteria):
    """Composite filter for AND/OR/NOT logic."""

    def __init__(
        self,
        filters: Sequence[FilterCriteria],
        operator: str = "AND",
    ) -> None:
        self.filters = list(filters)
        self.operator = operator.upper()
        if self.operator not in {"AND", "OR", "NOT"}:
            raise ValueError(f"Invalid operator: {self.operator}")

    def apply_to_query(self, query: Any) -> Any:
        # Placeholder: actual DB integration needed
        return query

    def matches(self, result: SearchResult) -> bool:
        if self.operator == "AND":
            return all(f.matches(result) for f in self.filters)
        if self.operator == "OR":
            return any(f.matches(result) for f in self.filters)
        if self.operator == "NOT":
            return bool(not any(f.matches(result) for f in self.filters))
        return False


class FilterEngine:
    """Engine for applying filters to result sets."""

    def apply_filter(
        self,
        result_set: List[SearchResult],
        criteria: FilterCriteria,
    ) -> List[SearchResult]:
        """Apply filter criteria to result set.

        Args:
            result_set: List of SearchResult to filter.
            criteria: FilterCriteria or composite filter.

        Returns:
            Filtered list of SearchResult.
        """
        return [r for r in result_set if criteria.matches(r)]

    def create_filter(self, filter_type: str, **params: Any) -> FilterCriteria:
        """Create filter of specified type.

        Args:
            filter_type: Type of filter to create.
            params: Filter-specific parameters.

        Returns:
            FilterCriteria instance.
        """
        filter_type = filter_type.lower()
        if filter_type == "filetype":
            return FileTypeFilter(params["file_type"])
        if filter_type == "extension":
            return ExtensionFilter(params["extension"])
        if filter_type == "daterange":
            return DateRangeFilter(
                start=params.get("start"),
                end=params.get("end"),
                field=params.get("field", "date_modified"),
            )
        if filter_type == "sizerange":
            return SizeRangeFilter(
                min_size=params.get("min_size"),
                max_size=params.get("max_size"),
            )
        if filter_type == "path":
            return PathFilter(params["substring"])
        raise ValueError(f"Unknown filter type: {filter_type}")

    def combine_filters(
        self, filters: Sequence[FilterCriteria], operator: str = "AND"
    ) -> CompositeFilter:
        """Combine multiple filters.

        Args:
            filters: List of filters to combine.
            operator: "AND", "OR", or "NOT".

        Returns:
            CompositeFilter instance.
        """
        return CompositeFilter(filters, operator=operator)
