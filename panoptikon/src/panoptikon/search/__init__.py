"""Search functionality for Panoptikon.

This module is responsible for:
1. Processing search queries
2. Efficiently searching the file index
3. Filtering and ranking search results
4. Supporting advanced search syntax

The search system is designed to provide instantaneous results even with
large file indices.
"""

from panoptikon.search.searcher import search, SearchParams

__all__ = ["search", "SearchParams"]
