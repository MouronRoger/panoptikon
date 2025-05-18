"""Database management and operations for Panoptikon."""

from pathlib import Path
from typing import Optional

from .config import DatabaseConfig, get_default_config
from .connection import DatabaseConnection, DatabaseConnectionService
from .optimization import QueryOptimizer
from .performance_monitor import QueryPerformanceMonitor
from .pool import (
    ConnectionHealthStatus,
    ConnectionPool,
    PooledConnection,
    PoolManager,
    TransactionIsolationLevel,
    get_pool_manager,
)
from .pool_service import DatabasePoolService
from .query_builder import QueryBuilder
from .schema import DatabaseSchemaService, SchemaManager
from .service import DatabaseService
from .statement_registry import StatementRegistry

__all__ = [
    "ConnectionHealthStatus",
    "ConnectionPool",
    "DatabaseConnection",
    "DatabaseConnectionService",
    "DatabaseConfig",
    "DatabasePoolService",
    "DatabaseSchemaService",
    "DatabaseService",
    "PoolManager",
    "PooledConnection",
    "SchemaManager",
    "TransactionIsolationLevel",
    "get_default_config",
    "get_default_db_path",
    "get_pool_manager",
    "StatementRegistry",
    "QueryBuilder",
    "QueryPerformanceMonitor",
    "QueryOptimizer",
]


def get_default_db_path(data_dir: Optional[Path] = None) -> Path:
    """Get the default path for the database file.

    Args:
        data_dir: Optional data directory. If not provided, uses the
            user's home directory.

    Returns:
        Path to the default database file.
    """
    if data_dir is None:
        home_dir = Path.home()
        data_dir = home_dir / ".panoptikon"

    return data_dir / "panoptikon.db"
