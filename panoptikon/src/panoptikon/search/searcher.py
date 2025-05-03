"""Search functionality for Panoptikon.

This module provides the core search capabilities for finding files in the index.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Union


@dataclass
class SearchParams:
    """Parameters for file search operations.

    Attributes:
        query: The search query string.
        case_sensitive: Whether the search should be case-sensitive.
        extensions: Optional list of file extensions to filter by.
        min_size: Optional minimum file size in bytes.
        max_size: Optional maximum file size in bytes.
        modified_after: Optional Unix timestamp for files modified after this time.
        modified_before: Optional Unix timestamp for files modified before this time.
        paths: Optional list of directory paths to search within.
        exclude_paths: Optional list of directory paths to exclude from search.
        limit: Maximum number of results to return.
        offset: Number of results to skip (for pagination).
    """

    query: str
    case_sensitive: bool = False
    extensions: Optional[List[str]] = None
    min_size: Optional[int] = None
    max_size: Optional[int] = None
    modified_after: Optional[float] = None
    modified_before: Optional[float] = None
    paths: Optional[List[str]] = None
    exclude_paths: Optional[List[str]] = None
    limit: int = 1000
    offset: int = 0


def search(params: SearchParams) -> List[Dict[str, Union[str, int, float]]]:
    """Search for files based on the provided parameters.

    Args:
        params: Search parameters.

    Returns:
        List of file information dictionaries matching the search criteria.
    """
    from panoptikon.db import file_store
    
    # Parse the query to extract any special search syntax
    parsed_query = _parse_query(params.query)
    
    # Get results from the database
    results = file_store.search_files(
        query=parsed_query["query"],
        case_sensitive=params.case_sensitive,
        extensions=params.extensions,
        min_size=params.min_size,
        max_size=params.max_size,
        modified_after=params.modified_after,
        modified_before=params.modified_before,
        paths=params.paths,
        exclude_paths=params.exclude_paths,
        limit=params.limit,
        offset=params.offset
    )
    
    return results


def _parse_query(query: str) -> Dict[str, str]:
    """Parse the search query to extract any special search syntax.

    Args:
        query: The raw search query string.

    Returns:
        A dictionary with the parsed query components.
    """
    # Simple implementation for now - will be expanded with advanced syntax
    return {
        "query": query,
        "type": "simple"
    } 