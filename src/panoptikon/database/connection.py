"""Database connection management.

This module provides utilities for managing SQLite database connections,
including connection pooling, thread safety, and proper cleanup.
"""

from collections.abc import Generator
from contextlib import contextmanager
import logging
from pathlib import Path
import sqlite3
import threading
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.errors import DatabaseError
from ..core.service import ServiceInterface

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Wrapper for SQLite database connection with thread safety.

    Provides a simple interface for connecting to a SQLite database
    with consistent configuration.
    """

    def __init__(self, db_path: Path, timeout: float = 5.0) -> None:
        """Initialize the database connection.

        Args:
            db_path: Path to the SQLite database file.
            timeout: Connection timeout in seconds.

        Raises:
            DatabaseError: If the database path is invalid.
        """
        self.db_path = db_path
        self.timeout = timeout
        self._local = threading.local()

    @contextmanager
    def connect(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection.

        This context manager ensures proper cleanup of the connection.

        Yields:
            A SQLite database connection.

        Raises:
            DatabaseError: If there's an error connecting to the database.
        """
        if not hasattr(self._local, "connection") or self._local.connection is None:
            try:
                # Create a new connection
                self._local.connection = sqlite3.connect(
                    str(self.db_path),
                    timeout=self.timeout,
                    isolation_level=None,  # Use explicit transaction control
                    detect_types=sqlite3.PARSE_DECLTYPES,
                )
                self._local.connection.execute("PRAGMA foreign_keys = ON")
                self._local.connection.execute("PRAGMA journal_mode = WAL")

                # Enable detailed error messages
                sqlite3.enable_callback_tracebacks(True)

                # Use row factory for better row access
                self._local.connection.row_factory = sqlite3.Row

                logger.debug(f"Opened new database connection to {self.db_path}")
            except sqlite3.Error as e:
                raise DatabaseError(f"Error connecting to database: {e}")

        try:
            yield self._local.connection
        except sqlite3.Error as e:
            # Rollback any pending transaction on error
            self._local.connection.rollback()
            raise DatabaseError(f"Database error: {e}")

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Begin a transaction and commit or rollback as needed.

        This context manager wraps a database connection with transaction
        handling, ensuring proper commit or rollback on exit.

        Yields:
            A SQLite database connection within a transaction.

        Raises:
            DatabaseError: If there's an error with the transaction.
        """
        with self.connect() as conn:
            try:
                conn.execute("BEGIN")
                yield conn
                conn.execute("COMMIT")
                logger.debug("Transaction committed")
            except Exception as e:
                conn.execute("ROLLBACK")
                logger.debug(f"Transaction rolled back: {e}")
                raise

    def close(self) -> None:
        """Close the connection.

        Closes the connection for the current thread if it exists.
        """
        if hasattr(self._local, "connection") and self._local.connection is not None:
            try:
                self._local.connection.close()
                logger.debug("Database connection closed")
            except sqlite3.Error as e:
                logger.error(f"Error closing database connection: {e}")
            finally:
                self._local.connection = None

    def execute(
        self,
        query: str,
        parameters: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None,
    ) -> sqlite3.Cursor:
        """Execute a SQL query with parameters.

        Args:
            query: The SQL query to execute.
            parameters: Optional parameters for the query.

        Returns:
            A SQLite cursor with the query results.

        Raises:
            DatabaseError: If there's an error executing the query.
        """
        with self.connect() as conn:
            try:
                if parameters is None:
                    return conn.execute(query)
                return conn.execute(query, parameters)
            except sqlite3.Error as e:
                raise DatabaseError(f"Error executing query: {e}, Query: {query}")

    def execute_many(
        self, query: str, parameters: List[Union[Tuple[Any, ...], Dict[str, Any]]]
    ) -> sqlite3.Cursor:
        """Execute a SQL query with multiple parameter sets.

        Args:
            query: The SQL query to execute.
            parameters: List of parameter sets for the query.

        Returns:
            A SQLite cursor with the query results.

        Raises:
            DatabaseError: If there's an error executing the query.
        """
        with self.connect() as conn:
            try:
                return conn.executemany(query, parameters)
            except sqlite3.Error as e:
                raise DatabaseError(f"Error executing batch query: {e}, Query: {query}")


class DatabaseConnectionService(ServiceInterface):
    """Service for managing database connections.

    This service integrates with the service container and provides
    thread-safe database connections.
    """

    def __init__(self, db_path: Path) -> None:
        """Initialize the database connection service.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.connection = DatabaseConnection(db_path)
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the database connection service.

        Raises:
            DatabaseError: If there's an error initializing the service.
        """
        if self._initialized:
            return

        # Test connection to make sure database is accessible
        try:
            with self.connection.connect() as conn:
                conn.execute("SELECT 1")
            self._initialized = True
            logger.info(
                f"Database connection service initialized with database at {self.db_path}"
            )
        except Exception as e:
            raise DatabaseError(
                f"Failed to initialize database connection service: {e}"
            )

    def shutdown(self) -> None:
        """Shutdown the database connection service.

        Closes all connections.
        """
        self.connection.close()
        self._initialized = False
        logger.debug("Database connection service shut down")

    def get_connection(self) -> DatabaseConnection:
        """Get the database connection.

        Returns:
            The database connection.
        """
        return self.connection
