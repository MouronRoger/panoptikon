"""Database operations for Panoptikon.

This module is responsible for:
1. Managing the file index database
2. Handling database connections and transactions
3. Providing an interface for file indexing and searching
4. Optimizing database operations for performance

The database layer is designed to be fast and efficient, with a focus on
search performance.
"""

from panoptikon.db.file_store import save_file_info, search_files

__all__ = ["save_file_info", "search_files"]
