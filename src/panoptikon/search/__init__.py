"""Search functionality for Panoptikon."""

# py.typed marker for type checking compliance

from .result import ResultSet, SearchResult
from .search_engine import SearchEngine

__all__ = [
    "SearchEngine",
    "SearchResult",
    "ResultSet",
]
