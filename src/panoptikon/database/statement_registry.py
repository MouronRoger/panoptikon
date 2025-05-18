"""Statement registry for prepared statement management in Panoptikon.

This module provides a centralized registry for prepared statements, parameter binding,
and statement caching for SQLite connections. It is designed to be thread-safe and
integrate with the existing connection pool.
"""

from __future__ import annotations

import sqlite3
from threading import Lock
import time
from typing import Dict, Optional, Tuple, Union


class StatementRegistry:
    """Centralized registry for managing prepared statements and their lifecycle."""

    def __init__(self) -> None:
        """Initialize the statement registry."""
        self._statements: Dict[str, sqlite3.Cursor] = {}
        self._cache_times: Dict[str, float] = {}
        self._lock = Lock()
        self._cache_ttl = 600.0  # seconds

    def prepare(self, conn: sqlite3.Connection, sql: str) -> sqlite3.Cursor:
        """Prepare (or retrieve cached) statement for the given SQL.

        Args:
            conn: SQLite connection.
            sql: SQL statement to prepare.

        Returns:
            Prepared statement cursor.
        """
        with self._lock:
            now = time.time()
            if sql in self._statements:
                self._cache_times[sql] = now
                return self._statements[sql]
            cursor = conn.cursor()
            cursor.execute("SELECT 1")  # Dummy to ensure cursor is valid
            self._statements[sql] = cursor
            self._cache_times[sql] = now
            return cursor

    def cleanup(self) -> None:
        """Cleanup expired statements from the cache."""
        with self._lock:
            now = time.time()
            expired = [
                sql for sql, t in self._cache_times.items() if now - t > self._cache_ttl
            ]
            for sql in expired:
                cursor = self._statements.pop(sql, None)
                if cursor is not None:
                    cursor.close()
                self._cache_times.pop(sql, None)

    def clear(self) -> None:
        """Clear all cached statements."""
        with self._lock:
            for cursor in self._statements.values():
                cursor.close()
            self._statements.clear()
            self._cache_times.clear()

    def bind_and_execute(
        self,
        conn: sqlite3.Connection,
        sql: str,
        parameters: Optional[Union[Tuple[object, ...], Dict[str, object]]] = None,
    ) -> sqlite3.Cursor:
        """Bind parameters and execute a prepared statement.

        Args:
            conn: SQLite connection.
            sql: SQL statement to prepare/execute.
            parameters: Parameters to bind.

        Returns:
            Cursor after execution.
        """
        cursor = self.prepare(conn, sql)
        if parameters is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, parameters)
        return cursor
