"""Search engine implementation.

This module implements the core search functionality for Panoptikon.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set


class SearchResult:
    """Represents a single search result."""

    def __init__(
        self,
        path: Path,
        score: float = 1.0,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """Initialize a search result.

        Args:
            path: Path to the file or directory
            score: Relevance score (higher is better)
            metadata: Additional metadata about the result
        """
        self.path = path
        self.score = score
        self.metadata = metadata or {}

    def __str__(self) -> str:
        """Return string representation of the search result.

        Returns:
            String representation of the result
        """
        return f"{self.path} (score: {self.score:.2f})"


class SearchEngine:
    """Core search engine implementation.

    This class handles search queries and returns relevant results from the index.
    """

    def __init__(self) -> None:
        """Initialize the search engine."""
        self.index: Dict[str, Set[Path]] = {}

    def search(
        self,
        query: str,
        max_results: int = 100,
        case_sensitive: bool = False
    ) -> List[SearchResult]:
        """Search for files matching the query.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            case_sensitive: Whether to use case-sensitive matching

        Returns:
            List of search results ordered by relevance
        """
        if not query:
            return []

        if not case_sensitive:
            query = query.lower()

        # Simple implementation that matches file paths containing the query
        results = []
        for keyword, paths in self.index.items():
            keyword_to_match = keyword if case_sensitive else keyword.lower()
            if query in keyword_to_match:
                for path in paths:
                    results.append(SearchResult(path))

        # Sort and limit results
        sorted_results = sorted(
            results,
            key=lambda result: result.score,
            reverse=True
        )
        return sorted_results[:max_results]

    def add_to_index(self, path: Path) -> None:
        """Add a file to the search index.

        Args:
            path: Path to the file to index
        """
        # Index by filename
        filename = path.name
        if filename not in self.index:
            self.index[filename] = set()
        self.index[filename].add(path)

        # Index by parent directories
        for part in path.parts:
            if part not in self.index:
                self.index[part] = set()
            self.index[part].add(path) 