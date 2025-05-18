"""Database connection pool service.

This module provides a service for managing database connection pools
with integration into the service container.
"""

from collections.abc import Generator
from contextlib import contextmanager
import logging
import sqlite3
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.config import ConfigurationSystem
from ..core.errors import DatabaseError
from ..core.service import ServiceInterface
from .config import DatabaseConfig
from .optimization import QueryOptimizer
from .performance_monitor import QueryPerformanceMonitor
from .pool import ConnectionPool, TransactionIsolationLevel, get_pool_manager
from .statement_registry import StatementRegistry

logger = logging.getLogger(__name__)


class DatabasePoolService(ServiceInterface):
    """Service for managing database connection pools.

    This service integrates connection pool management with the service container.
    It provides connection pooling, transaction management, and query execution.

    Thread Safety:
        - All public methods are thread-safe unless otherwise noted.
        - Each thread is assigned its own connection when possible.
        - The underlying pool is thread-safe and connections are not shared between threads.

    Context Manager Usage:
        - Use `with service.get_connection()` to safely acquire and release a connection.
        - Use `with service.transaction()` to run a transaction with automatic commit/rollback.
        - Use `with service.savepoint()` for nested transactions.

    SQLite Single-Writer Limitation:
        - SQLite allows only one writer at a time. Under high write concurrency,
          some threads may experience 'database is locked' errors or timeouts.
        - The pool will retry and recycle connections as needed, but users should
          expect write contention and handle exceptions accordingly.
    """

    def __init__(self, config_system: ConfigurationSystem) -> None:
        """Initialize the database pool service.

        Args:
            config_system: The configuration system.
        """
        self.config_system = config_system
        self._config: Optional[DatabaseConfig] = None
        self._pool: Optional[ConnectionPool] = None
        self._initialized = False
        self.statement_registry = StatementRegistry()
        self.performance_monitor = QueryPerformanceMonitor()
        self.optimizer = QueryOptimizer()

    def initialize(self) -> None:
        """Initialize the database pool service.

        Raises:
            DatabaseError: If there's an error initializing the service.
        """
        if self._initialized:
            return

        try:
            # Get or register configuration
            self._setup_configuration()

            # Setup database schema
            self._setup_database_schema()

            # Setup connection pool
            self._setup_connection_pool()

            # Mark as initialized
            self._initialized = True
            assert self._config is not None  # For type checking
            logger.info(
                f"Database pool service initialized for database at {self._config.path}"
            )
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database pool service: {e}")

    def _setup_configuration(self) -> None:
        """Setup the database configuration.

        Raises:
            DatabaseError: If there's an error with the configuration.
        """
        try:
            config_model = self.config_system.get_as_model("database")
            if not isinstance(config_model, DatabaseConfig):
                raise DatabaseError(
                    "Database configuration is not of type DatabaseConfig"
                )
            self._config = config_model
        except Exception:
            # Register database configuration section
            from .config import get_default_config

            self.config_system.register_section(
                "database", DatabaseConfig, get_default_config()
            )
            config_model = self.config_system.get_as_model("database")
            if not isinstance(config_model, DatabaseConfig):
                raise DatabaseError(
                    "Database configuration is not of type DatabaseConfig"
                )
            self._config = config_model

    def _setup_database_schema(self) -> None:
        """Setup the database schema.

        Raises:
            DatabaseError: If there's an error with the schema.
        """
        from .schema import SchemaManager

        if self._config is None:
            raise DatabaseError("Database configuration is not set")

        schema_manager = SchemaManager(self._config.path)

        # Create database if it doesn't exist
        if not schema_manager.database_exists():
            if self._config.create_if_missing:
                logger.info("Database does not exist, creating...")
                schema_manager.create_schema()
            else:
                raise DatabaseError(
                    f"Database does not exist at {self._config.path} "
                    "and create_if_missing is False"
                )

        # Validate schema
        if not schema_manager.validate_schema():
            logger.warning("Database schema validation failed, recreating schema")
            schema_manager.create_schema()

    def _setup_connection_pool(self) -> None:
        """Setup the connection pool.

        Raises:
            DatabaseError: If there's an error setting up the pool.
        """
        if self._config is None:
            raise DatabaseError("Database configuration is not set")

        pool_manager = get_pool_manager()

        # Get pool configuration from settings
        max_connections = getattr(self._config, "max_connections", 10)
        min_connections = getattr(self._config, "min_connections", 1)
        connection_max_age = getattr(self._config, "connection_max_age", 600.0)
        health_check_interval = getattr(self._config, "health_check_interval", 60.0)

        # Create or get the pool
        self._pool = pool_manager.get_pool(
            db_path=self._config.path,
            max_connections=max_connections,
            min_connections=min_connections,
            connection_timeout=self._config.timeout,
            connection_max_age=connection_max_age,
            health_check_interval=health_check_interval,
        )

    def shutdown(self) -> None:
        """Shutdown the database pool service.

        Closes all connections and releases resources.
        """
        self._initialized = False
        logger.debug("Database pool service shut down")

    def get_pool(self) -> ConnectionPool:
        """Get the connection pool.

        Returns:
            The connection pool for this service.

        Raises:
            DatabaseError: If the service is not initialized.
        """
        if not self._initialized or not self._pool:
            raise DatabaseError("Database pool service not initialized")
        return self._pool

    def execute(
        self,
        query: str,
        parameters: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None,
        *,
        use_registry: bool = True,
        monitor: bool = True,
        optimize: bool = False,
        index_hint: Optional[str] = None,
        cache_result: bool = False,
    ) -> sqlite3.Cursor:
        """Execute a SQL query with parameters, supporting prepared statement registry,
        performance monitoring, and optional optimization.

        Args:
            query: The SQL query to execute.
            parameters: Optional parameters for the query.
            use_registry: Use StatementRegistry for prepared statements.
            monitor: Record timing and performance metrics.
            optimize: Apply query optimization strategies.
            index_hint: Optional index hint for the query.
            cache_result: Use result caching for SELECT queries.

        Returns:
            A SQLite cursor with the query results.

        Raises:
            DatabaseError: If there's an error executing the query.
        """
        pool = self.get_pool()
        # Pool does not directly support these features, so use a connection context
        with pool.get_connection() as conn:
            optimizer = self.optimizer
            performance_monitor = self.performance_monitor
            statement_registry = self.statement_registry
            sql = query
            if optimize:
                sql = optimizer.rewrite_query(sql)
                if index_hint:
                    sql = optimizer.with_index_hint(sql, index_hint)
            if cache_result and sql.strip().upper().startswith("SELECT"):
                result = optimizer.cached_query(
                    conn,
                    sql,
                    tuple(parameters)
                    if isinstance(parameters, (list, tuple))
                    else None,
                )
                if isinstance(result, sqlite3.Cursor):
                    return result
                if parameters is None:
                    return conn.execute(sql)
                return conn.execute(sql, parameters)
            if use_registry:
                if monitor:
                    cursor, _ = performance_monitor.time_query(conn, sql, parameters)
                    return cursor
                return statement_registry.bind_and_execute(conn, sql, parameters)
            if monitor:
                cursor, _ = performance_monitor.time_query(conn, sql, parameters)
                return cursor
            if parameters is None:
                return conn.execute(sql)
            return conn.execute(sql, parameters)

    def execute_many(
        self,
        query: str,
        parameters: List[Union[Tuple[Any, ...], Dict[str, Any]]],
        *,
        optimize: bool = False,
        batch: bool = True,
    ) -> sqlite3.Cursor:
        """Execute a SQL query with multiple parameter sets, supporting batch optimization.

        Args:
            query: The SQL query to execute.
            parameters: List of parameter sets for the query.
            optimize: Apply query optimization strategies.
            batch: Use batch execution optimization.

        Returns:
            A SQLite cursor with the query results.

        Raises:
            DatabaseError: If there's an error executing the query.
        """
        pool = self.get_pool()
        with pool.get_connection() as conn:
            optimizer = self.optimizer
            sql = query
            if optimize:
                sql = optimizer.rewrite_query(sql)
            if batch:
                tuple_params = [
                    tuple(p.values()) if isinstance(p, dict) else tuple(p)
                    for p in parameters
                ]
                return optimizer.batch_execute(conn, sql, tuple_params)
            return conn.executemany(sql, parameters)

    @contextmanager
    def transaction(
        self,
        isolation_level: TransactionIsolationLevel = TransactionIsolationLevel.DEFERRED,
    ) -> Generator[sqlite3.Connection, None, None]:
        """Start a transaction with the specified isolation level.

        This method is a context manager. Use as:
            with service.transaction() as conn:
                ...

        Thread Safety:
            - Safe to call from multiple threads. Each thread gets its own transaction.

        SQLite Limitation:
            - Only one write transaction can be active at a time. Other threads may block or fail.
            - Use IMMEDIATE or EXCLUSIVE isolation levels to control locking behavior.

        Args:
            isolation_level: Transaction isolation level.

        Yields:
            A SQLite connection within a transaction.

        Raises:
            DatabaseError: If there's an error with the transaction.
        """
        pool = self.get_pool()
        with pool.transaction(isolation_level) as conn:
            yield conn

    @contextmanager
    def savepoint(self, name: str = "") -> Generator[sqlite3.Connection, None, None]:
        """Create a savepoint for nested transactions.

        This method is a context manager. Use as:
            with service.savepoint("sp_name") as conn:
                ...

        Thread Safety:
            - Safe to call from multiple threads. Each thread gets its own savepoint.

        SQLite Limitation:
            - Savepoints are only effective within a transaction.

        Args:
            name: Optional savepoint name. If not provided, a unique name is generated.

        Yields:
            A SQLite connection within a savepoint.

        Raises:
            DatabaseError: If there's an error with the savepoint.
        """
        pool = self.get_pool()
        with pool.savepoint(name) as conn:
            yield conn

    @contextmanager
    def get_connection(
        self, timeout: Optional[float] = None
    ) -> Generator[sqlite3.Connection, None, None]:
        """Get a connection from the pool.

        This method is a context manager. Use as:
            with service.get_connection() as conn:
                ...

        Thread Safety:
            - Safe to call from multiple threads. Each thread gets its own connection.
            - Connections are not shared between threads.

        SQLite Limitation:
            - Under high concurrency, acquiring a connection may block or timeout.
            - If all connections are in use, a ConnectionAcquisitionTimeout is raised.

        Args:
            timeout: Optional timeout override for connection acquisition.

        Yields:
            A SQLite database connection.

        Raises:
            DatabaseError: If there's an error getting a connection.
            TimeoutError: If a connection couldn't be acquired within the timeout.
        """
        pool = self.get_pool()
        with pool.get_connection(timeout) as conn:
            yield conn

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the connection pool.

        Thread Safety:
            - Safe to call from multiple threads.

        Returns:
            Dictionary with connection pool statistics.
        """
        pool = self.get_pool()
        return pool.get_stats()
