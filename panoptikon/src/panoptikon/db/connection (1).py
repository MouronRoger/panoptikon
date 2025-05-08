"""Database connection management for Panoptikon."""

import logging
import os
import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple, Union

import sqlalchemy as sa
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DatabaseError, OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker

from panoptikon.db.schema import create_tables

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages database connections and connection lifecycle.

    This class provides connection pooling, error recovery, and
    ensures proper database initialization.
    """

    def __init__(
        self,
        db_path: Union[str, Path],
        pool_size: int = 5,
        max_overflow: int = 10,
        timeout: int = 30,
        echo: bool = False,
    ):
        """Initialize the connection manager.

        Args:
            db_path: Path to the SQLite database file
            pool_size: Size of the connection pool
            max_overflow: Maximum number of connections to allow beyond pool_size
            timeout: Seconds to wait before timing out on connection pool get
            echo: Whether to echo SQL statements (for debugging)
        """
        self.db_path = str(db_path)
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.timeout = timeout
        self.echo = echo
        
        self._engine = None
        self._sessionmaker = None
        self._lock = threading.RLock()
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the database and connection pool.

        This method creates the database file if it doesn't exist,
        initializes the schema, and sets up the connection pool.
        """
        with self._lock:
            if self._initialized:
                return
                
            # Ensure the database directory exists
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            
            # Create engine
            self._engine = self._create_engine()
            
            # Create session factory
            self._sessionmaker = sessionmaker(bind=self._engine)
            
            # Initialize database schema
            try:
                create_tables(self._engine)
                logger.info(f"Database initialized at {self.db_path}")
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize database: {e}")
                raise

    def _create_engine(self) -> Engine:
        """Create a SQLAlchemy engine with appropriate settings.

        Returns:
            Configured SQLAlchemy engine
        """
        # SQLite-specific connection settings
        connect_args = {
            "check_same_thread": False,  # Allow access from multiple threads
            "timeout": self.timeout,  # Connection timeout in seconds
        }
        
        # Create engine with connection pooling
        return sa.create_engine(
            f"sqlite:///{self.db_path}",
            echo=self.echo,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.timeout,
            pool_recycle=3600,  # Recycle connections after 1 hour
            connect_args=connect_args,
        )

    @property
    def engine(self) -> Engine:
        """Get the SQLAlchemy engine.

        Initializes the database if not already initialized.

        Returns:
            SQLAlchemy engine
        """
        if not self._initialized:
            self.initialize()
        return self._engine

    @contextmanager
    def get_session(self) -> Iterator[sa.orm.Session]:
        """Get a database session with automatic cleanup.

        This context manager creates a new session and ensures
        it is properly closed when the context exits.

        Yields:
            SQLAlchemy session

        Raises:
            DatabaseError: If database access fails
        """
        if not self._initialized:
            self.initialize()
            
        session = self._sessionmaker()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    @contextmanager
    def get_connection(self) -> Iterator[sa.engine.Connection]:
        """Get a raw database connection with automatic cleanup.

        This context manager creates a new connection and ensures
        it is properly closed when the context exits.

        Yields:
            SQLAlchemy connection

        Raises:
            DatabaseError: If connection fails
        """
        if not self._initialized:
            self.initialize()
            
        connection = self._engine.connect()
        try:
            yield connection
        finally:
            connection.close()

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute a raw SQL query and return the results.

        Args:
            query: SQL query string
            params: Optional parameters for the query

        Returns:
            List of dictionaries containing the query results

        Raises:
            DatabaseError: If query execution fails
        """
        params = params or {}
        
        with self.get_connection() as conn:
            try:
                result = conn.execute(sa.text(query), **params)
                return [dict(row) for row in result.fetchall()]
            except Exception as e:
                logger.error(f"Query execution error: {e}")
                raise

    def check_connection(self) -> bool:
        """Test if the database connection is working.

        Returns:
            True if connection is working, False otherwise
        """
        try:
            with self.get_connection() as conn:
                conn.execute(sa.text("SELECT 1")).fetchone()
            return True
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False

    def close(self) -> None:
        """Close all connections and dispose of the engine.

        This should be called when the application is shutting down.
        """
        with self._lock:
            if self._engine:
                self._engine.dispose()
                logger.info("Database connections closed")
            self._initialized = False

    def vacuum(self) -> bool:
        """Vacuum the SQLite database to optimize storage.

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                conn.execute(sa.text("VACUUM"))
            logger.info("Database vacuum completed successfully")
            return True
        except Exception as e:
            logger.error(f"Database vacuum failed: {e}")
            return False

    def backup(self, backup_path: Union[str, Path]) -> bool:
        """Create a backup of the database.

        Args:
            backup_path: Path where the backup should be saved

        Returns:
            True if successful, False otherwise
        """
        backup_path = str(backup_path)
        
        # Ensure backup directory exists
        backup_dir = os.path.dirname(backup_path)
        if backup_dir:
            os.makedirs(backup_dir, exist_ok=True)
        
        try:
            # Use SQLite's backup API for an atomic backup
            source = sqlite3.connect(self.db_path)
            dest = sqlite3.connect(backup_path)
            
            source.backup(dest)
            
            source.close()
            dest.close()
            
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False


# Global connection manager instance
_connection_manager = None
_connection_lock = threading.RLock()


def get_connection_manager(
    db_path: Optional[Union[str, Path]] = None,
    pool_size: int = 5,
    max_overflow: int = 10,
    timeout: int = 30,
    echo: bool = False,
) -> ConnectionManager:
    """Get or create the global connection manager instance.

    This function follows the singleton pattern to ensure
    only one connection manager exists per process.

    Args:
        db_path: Path to the SQLite database file (required on first call)
        pool_size: Size of the connection pool
        max_overflow: Maximum number of connections to allow beyond pool_size
        timeout: Seconds to wait before timing out on connection pool get
        echo: Whether to echo SQL statements (for debugging)

    Returns:
        ConnectionManager instance

    Raises:
        ValueError: If db_path is not provided on first call
    """
    global _connection_manager
    
    with _connection_lock:
        if _connection_manager is None:
            if db_path is None:
                raise ValueError(
                    "Database path must be provided on first call to get_connection_manager"
                )
            
            _connection_manager = ConnectionManager(
                db_path=db_path,
                pool_size=pool_size,
                max_overflow=max_overflow,
                timeout=timeout,
                echo=echo,
            )
            _connection_manager.initialize()
        
        return _connection_manager


def close_connections() -> None:
    """Close all database connections.

    This should be called when the application is shutting down.
    """
    global _connection_manager
    
    with _connection_lock:
        if _connection_manager is not None:
            _connection_manager.close()
            _connection_manager = None


def get_engine() -> Engine:
    """Get the SQLAlchemy engine from the global connection manager.

    Returns:
        SQLAlchemy engine

    Raises:
        RuntimeError: If the connection manager is not initialized
    """
    if _connection_manager is None:
        raise RuntimeError(
            "Connection manager not initialized. Call get_connection_manager first."
        )
    
    return _connection_manager.engine


@contextmanager
def session_scope() -> Iterator[sa.orm.Session]:
    """Get a database session with automatic cleanup.

    This is a convenience wrapper around ConnectionManager.get_session().

    Yields:
        SQLAlchemy session

    Raises:
        RuntimeError: If the connection manager is not initialized
    """
    if _connection_manager is None:
        raise RuntimeError(
            "Connection manager not initialized. Call get_connection_manager first."
        )
    
    with _connection_manager.get_session() as session:
        yield session 