"""Performance monitoring utilities for Panoptikon database layer.

Provides query execution timing, EXPLAIN QUERY PLAN analysis, index usage tracking,
slow query identification, and query frequency analysis.
"""

from __future__ import annotations

import sqlite3
import time
from typing import Dict, List, Optional, Tuple, Union


class QueryPerformanceMonitor:
    """Monitors and analyzes query performance for SQLite connections."""

    def __init__(self) -> None:
        """Initialize the performance monitor."""
        self.query_times: List[Tuple[str, float]] = []
        self.slow_queries: List[Tuple[str, float]] = []
        self.query_counts: Dict[str, int] = {}
        self.slow_threshold: float = 0.1  # seconds

    def time_query(
        self,
        conn: sqlite3.Connection,
        sql: str,
        parameters: Optional[Union[tuple[object, ...], dict[str, object]]] = None,
    ) -> Tuple[sqlite3.Cursor, float]:
        """Execute a query and record its execution time.

        Args:
            conn: SQLite connection.
            sql: SQL query to execute.
            parameters: Parameters for the query.

        Returns:
            Tuple of (cursor, elapsed_time_seconds).
        """
        start = time.perf_counter()
        cursor = (
            conn.execute(sql) if parameters is None else conn.execute(sql, parameters)
        )
        elapsed = time.perf_counter() - start
        self.query_times.append((sql, elapsed))
        self.query_counts[sql] = self.query_counts.get(sql, 0) + 1
        if elapsed > self.slow_threshold:
            self.slow_queries.append((sql, elapsed))
        return cursor, elapsed

    def explain_query_plan(
        self,
        conn: sqlite3.Connection,
        sql: str,
        parameters: Optional[Union[tuple[object, ...], dict[str, object]]] = None,
    ) -> List[Tuple[object, ...]]:
        """Run EXPLAIN QUERY PLAN and return the analysis.

        Args:
            conn: SQLite connection.
            sql: SQL query to analyze.
            parameters: Parameters for the query.

        Returns:
            List of tuples with EXPLAIN QUERY PLAN output.
        """
        explain_sql = f"EXPLAIN QUERY PLAN {sql}"
        cursor = (
            conn.execute(explain_sql)
            if parameters is None
            else conn.execute(explain_sql, parameters)
        )
        return cursor.fetchall()

    def get_slow_queries(self) -> List[Tuple[str, float]]:
        """Get a list of slow queries exceeding the threshold."""
        return self.slow_queries.copy()

    def get_query_frequencies(self) -> Dict[str, int]:
        """Get a mapping of query strings to execution counts."""
        return self.query_counts.copy()
