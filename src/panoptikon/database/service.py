"""Database service for Panoptikon.

This module provides the main database service that integrates schema,
connection, and configuration management.
"""

import logging
import sqlite3
from typing import Any, Optional, Union, cast

from ..core.config import ConfigurationSystem
from ..core.errors import DatabaseError
from ..core.service import ServiceInterface
from .config import DatabaseConfig
from .connection import DatabaseConnection
from .optimization import QueryOptimizer
from .performance_monitor import QueryPerformanceMonitor
from .schema import SchemaManager
from .statement_registry import StatementRegistry

logger = logging.getLogger(__name__)


class DatabaseService(ServiceInterface):
    """Main service for database operations.

    This service combines schema management, connection handling,
    and configuration to provide a complete database solution.
    """

    def __init__(self, config_system: ConfigurationSystem) -> None:
        """Initialize the database service.

        Args:
            config_system: The configuration system to use.
        """
        self.config_system = config_system
        self._config: Optional[DatabaseConfig] = None
        self._connection: Optional[DatabaseConnection] = None
        self._schema_manager: Optional[SchemaManager] = None
        self._initialized = False
        self.statement_registry = StatementRegistry()
        self.performance_monitor = QueryPerformanceMonitor()
        self.optimizer = QueryOptimizer()

    def initialize(self) -> None:
        """Initialize the database service.

        This method loads configuration, creates the database if needed,
        and initializes connections.

        Raises:
            DatabaseError: If there's an error initializing the service.
        """
        if self._initialized:
            return

        try:
            # Register database configuration section
            from .config import get_default_config

            self.config_system.register_section(
                "database", DatabaseConfig, get_default_config()
            )

            # Get configuration - we can safely cast this since we just registered the schema
            config_model = self.config_system.get_as_model("database")
            self._config = cast(DatabaseConfig, config_model)

            # Create schema manager
            self._schema_manager = SchemaManager(self._config.path)

            # Create database if it doesn't exist
            if not self._schema_manager.database_exists():
                if self._config.create_if_missing:
                    logger.info("Database does not exist, creating...")
                    self._schema_manager.create_schema()
                else:
                    raise DatabaseError(
                        f"Database does not exist at {self._config.path} "
                        "and create_if_missing is False"
                    )

            # Validate schema
            if not self._schema_manager.validate_schema():
                logger.warning("Database schema validation failed, recreating schema")
                self._schema_manager.create_schema()

            # Create connection
            self._connection = DatabaseConnection(
                self._config.path, self._config.timeout
            )

            # Set pragmas
            with self._connection.connect() as conn:
                conn.execute(f"PRAGMA synchronous={self._config.pragma_synchronous}")
                conn.execute(f"PRAGMA journal_mode={self._config.pragma_journal_mode}")
                conn.execute(f"PRAGMA temp_store={self._config.pragma_temp_store}")
                conn.execute(f"PRAGMA cache_size={self._config.pragma_cache_size}")
                conn.execute("PRAGMA foreign_keys=ON")

            self._initialized = True
            logger.info(
                f"Database service initialized with database at {self._config.path}"
            )

        except Exception as e:
            raise DatabaseError(f"Failed to initialize database service: {e}")

    def shutdown(self) -> None:
        """Shutdown the database service.

        Closes all connections and performs cleanup.
        """
        if self._connection:
            self._connection.close()

        self._initialized = False
        logger.debug("Database service shut down")

    def get_connection(self) -> DatabaseConnection:
        """Get the database connection.

        Returns:
            The database connection.

        Raises:
            DatabaseError: If the service is not initialized.
        """
        if not self._initialized or not self._connection:
            raise DatabaseError("Database service not initialized")
        return self._connection

    def execute(
        self,
        query: str,
        parameters: Optional[Union[tuple[Any, ...], dict[str, Any]]] = None,
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
        connection = self.get_connection()
        return connection.execute(
            query,
            parameters,
            use_registry=use_registry,
            monitor=monitor,
            optimize=optimize,
            index_hint=index_hint,
            cache_result=cache_result,
        )

    def execute_many(
        self,
        query: str,
        parameters: list[Union[tuple[Any, ...], dict[str, Any]]],
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
        connection = self.get_connection()
        return connection.execute_many(
            query,
            parameters,
            optimize=optimize,
            batch=batch,
        )

    @property
    def schema_manager(self) -> SchemaManager:
        """Get the schema manager.

        Returns:
            The schema manager.

        Raises:
            DatabaseError: If the service is not initialized.
        """
        if not self._initialized or not self._schema_manager:
            raise DatabaseError("Database service not initialized")
        return self._schema_manager

    @property
    def config(self) -> DatabaseConfig:
        """Get the database configuration.

        Returns:
            The database configuration.

        Raises:
            DatabaseError: If the service is not initialized.
        """
        if not self._initialized or not self._config:
            raise DatabaseError("Database service not initialized")
        return self._config
