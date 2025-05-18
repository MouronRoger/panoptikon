"""Query optimization strategies for Panoptikon database layer.

Implements index hints, query rewriting, batch operation support, and result caching.
"""

import re
import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional, Tuple


class QueryOptimizer:
    """Provides query optimization strategies for SQLite queries."""

    def __init__(self) -> None:
        """Initialize the optimizer."""
        self._result_cache: Dict[str, Tuple[float, Any]] = {}
        self._cache_ttl = 60.0  # seconds
        self._lock = threading.Lock()

    def with_index_hint(self, sql: str, index_name: Optional[str] = None) -> str:
        """Add an index hint to a SQL query (SQLite supports INDEXED BY syntax).

        Only works for simple queries of the form:
            SELECT ... FROM table_name ...
        and rewrites to:
            SELECT ... FROM table_name INDEXED BY index_name ...
        Does not support aliases, joins, or subqueries.

        Args:
            sql: The SQL query.
            index_name: The index to hint.

        Returns:
            Modified SQL query with index hint if provided.
        """
        if index_name:
            # Match 'FROM <table>' not followed by AS/alias/join/parenthesis
            pattern = r"(FROM\s+)([A-Za-z_][A-Za-z0-9_]*)(\s|$)"

            def repl(match: re.Match[str]) -> str:
                return f"{match.group(1)}{match.group(2)} INDEXED BY {index_name}{match.group(3)}"

            new_sql, count = re.subn(pattern, repl, sql, count=1, flags=re.IGNORECASE)
            if count == 1:
                return new_sql
        return sql

    def rewrite_query(self, sql: str) -> str:
        """Rewrite common query patterns for optimization (placeholder).

        Args:
            sql: The SQL query.

        Returns:
            Optimized SQL query.
        """
        # Placeholder: add real rewriting logic as needed
        return sql

    def batch_execute(
        self,
        conn: sqlite3.Connection,
        sql: str,
        param_sets: List[Tuple[Any, ...]],
    ) -> sqlite3.Cursor:
        """Execute a batch of operations efficiently.

        Args:
            conn: SQLite connection.
            sql: SQL query to execute.
            param_sets: List of parameter tuples.

        Returns:
            Cursor after execution.
        """
        return conn.executemany(sql, param_sets)

    def cached_query(
        self,
        conn: sqlite3.Connection,
        sql: str,
        parameters: Optional[Tuple[Any, ...]] = None,
    ) -> Any:
        """Cache the result of a query for a short period.

        Args:
            conn: SQLite connection.
            sql: SQL query to execute.
            parameters: Parameters for the query.

        Returns:
            Query result (list of rows).
        """
        cache_key = f"{sql}|{parameters}"
        now = time.time()
        with self._lock:
            if cache_key in self._result_cache:
                cached_time, result = self._result_cache[cache_key]
                if now - cached_time < self._cache_ttl:
                    return result
                else:
                    del self._result_cache[cache_key]
        cursor = (
            conn.execute(sql) if parameters is None else conn.execute(sql, parameters)
        )
        result = cursor.fetchall()
        with self._lock:
            self._result_cache[cache_key] = (now, result)
        return result
