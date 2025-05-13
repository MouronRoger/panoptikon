"""Tests for the database pool service implementation."""

from collections.abc import Generator
from pathlib import Path
import sqlite3
from unittest.mock import MagicMock, patch

import pytest

from panoptikon.core.config import ConfigurationSystem
from panoptikon.core.errors import DatabaseError
from panoptikon.database.config import DatabaseConfig
from panoptikon.database.pool import ConnectionPool, TransactionIsolationLevel
from panoptikon.database.pool_service import DatabasePoolService


@pytest.fixture
def config_system() -> ConfigurationSystem:
    """Create a mock configuration system for testing.

    Returns:
        A mock configuration system.
    """
    mock_config = MagicMock(spec=ConfigurationSystem)

    # Setup the database configuration - use MagicMock with spec to avoid frozen issues
    mock_db_config = MagicMock(spec=DatabaseConfig)
    mock_db_config.path = Path("test.db")
    mock_db_config.timeout = 1.0
    mock_db_config.max_connections = 5
    mock_db_config.min_connections = 1
    mock_db_config.create_if_missing = True

    # Make get_as_model return the database config
    mock_config.get_as_model.return_value = mock_db_config

    return mock_config


@pytest.fixture
def pool_service(
    config_system: ConfigurationSystem,
) -> Generator[DatabasePoolService, None, None]:
    """Create a database pool service for testing.

    Args:
        config_system: Mock configuration system.

    Yields:
        A database pool service for testing.
    """
    # Create a mock pool
    mock_pool = MagicMock(spec=ConnectionPool)

    # Patch the get_pool_manager and SchemaManager to avoid actual initialization
    with (
        patch(
            "panoptikon.database.pool_service.get_pool_manager"
        ) as mock_get_pool_manager,
        patch("panoptikon.database.schema.SchemaManager") as mock_schema_manager_cls,
    ):
        # Configure the mock schema manager
        mock_schema_manager = mock_schema_manager_cls.return_value
        mock_schema_manager.database_exists.return_value = True
        mock_schema_manager.validate_schema.return_value = True

        # Configure the mock pool manager
        mock_pool_manager = MagicMock()
        mock_pool_manager.get_pool.return_value = mock_pool
        mock_get_pool_manager.return_value = mock_pool_manager

        # Create the service
        service = DatabasePoolService(config_system)

        # Initialize it
        service.initialize()

        yield service


def test_pool_service_initialization(config_system: ConfigurationSystem) -> None:
    """Test pool service initialization.

    Args:
        config_system: Mock configuration system.
    """
    # Create the mocks
    with (
        patch(
            "panoptikon.database.pool_service.get_pool_manager"
        ) as mock_get_pool_manager,
        patch("panoptikon.database.schema.SchemaManager") as mock_schema_manager_cls,
    ):
        # Configure the mock schema manager
        mock_schema_manager = mock_schema_manager_cls.return_value
        mock_schema_manager.database_exists.return_value = True
        mock_schema_manager.validate_schema.return_value = True

        # Configure the mock pool manager
        mock_pool_manager = MagicMock()
        mock_get_pool_manager.return_value = mock_pool_manager

        # Create and initialize the service
        service = DatabasePoolService(config_system)
        service.initialize()

        # Check that the pool was created
        assert service._initialized

        # Check that the schema manager was checked
        mock_schema_manager.database_exists.assert_called_once()
        mock_schema_manager.validate_schema.assert_called_once()

        # Check that the pool manager was used to get a pool
        mock_pool_manager.get_pool.assert_called_once()


def test_pool_service_create_database_if_missing(
    config_system: ConfigurationSystem,
) -> None:
    """Test database creation when missing.

    Args:
        config_system: Mock configuration system.
    """
    # Create the mocks
    with (
        patch("panoptikon.database.pool_service.get_pool_manager"),
        patch("panoptikon.database.schema.SchemaManager") as mock_schema_manager_cls,
    ):
        # Configure the mock schema manager
        mock_schema_manager = mock_schema_manager_cls.return_value
        mock_schema_manager.database_exists.return_value = False

        # Create and initialize the service
        service = DatabasePoolService(config_system)
        service.initialize()

        # Check that the schema was created
        mock_schema_manager.create_schema.assert_called_once()


def test_pool_service_recreate_schema_if_invalid(
    config_system: ConfigurationSystem,
) -> None:
    """Test schema recreation when invalid.

    Args:
        config_system: Mock configuration system.
    """
    # Create the mocks
    with (
        patch("panoptikon.database.pool_service.get_pool_manager"),
        patch("panoptikon.database.schema.SchemaManager") as mock_schema_manager_cls,
    ):
        # Configure the mock schema manager
        mock_schema_manager = mock_schema_manager_cls.return_value
        mock_schema_manager.database_exists.return_value = True
        mock_schema_manager.validate_schema.return_value = False

        # Create and initialize the service
        service = DatabasePoolService(config_system)
        service.initialize()

        # Check that the schema was recreated
        mock_schema_manager.create_schema.assert_called_once()


def test_pool_service_fail_if_missing_and_not_create(
    config_system: ConfigurationSystem,
) -> None:
    """Test failure when database is missing and create_if_missing is False.

    Args:
        config_system: Mock configuration system.
    """
    # Modify the mock config to not create if missing
    mock_db_config = config_system.get_as_model.return_value
    mock_db_config.create_if_missing = False

    # Create the mocks
    with (
        patch("panoptikon.database.pool_service.get_pool_manager"),
        patch("panoptikon.database.schema.SchemaManager") as mock_schema_manager_cls,
    ):
        # Configure the mock schema manager
        mock_schema_manager = mock_schema_manager_cls.return_value
        mock_schema_manager.database_exists.return_value = False

        # Create the service
        service = DatabasePoolService(config_system)

        # Initializing should raise an error
        with pytest.raises(DatabaseError, match="Database does not exist"):
            service.initialize()

        # Check that schema was not created
        mock_schema_manager.create_schema.assert_not_called()


def test_pool_service_execute(pool_service: DatabasePoolService) -> None:
    """Test execute method.

    Args:
        pool_service: Database pool service fixture.
    """
    # Setup the mock pool
    mock_pool = pool_service.get_pool()
    mock_cursor = MagicMock(spec=sqlite3.Cursor)
    mock_pool.execute.return_value = mock_cursor

    # Execute a query
    result = pool_service.execute("SELECT * FROM test")

    # Check that the pool's execute method was called
    mock_pool.execute.assert_called_once_with("SELECT * FROM test", None)
    assert result is mock_cursor


def test_pool_service_execute_many(pool_service: DatabasePoolService) -> None:
    """Test execute_many method.

    Args:
        pool_service: Database pool service fixture.
    """
    # Setup the mock pool
    mock_pool = pool_service.get_pool()
    mock_cursor = MagicMock(spec=sqlite3.Cursor)
    mock_pool.execute_many.return_value = mock_cursor

    # Execute a query with multiple parameters
    params = [(1, "test"), (2, "test2")]
    result = pool_service.execute_many("INSERT INTO test VALUES (?, ?)", params)

    # Check that the pool's execute_many method was called
    mock_pool.execute_many.assert_called_once_with(
        "INSERT INTO test VALUES (?, ?)", params
    )
    assert result is mock_cursor


def test_pool_service_transaction(pool_service: DatabasePoolService) -> None:
    """Test transaction method.

    Args:
        pool_service: Database pool service fixture.
    """
    # Setup the mock pool
    mock_pool = pool_service.get_pool()
    mock_conn = MagicMock(spec=sqlite3.Connection)

    # Mock the transaction context manager
    mock_pool.transaction.return_value.__enter__.return_value = mock_conn

    # Use the transaction context manager
    with pool_service.transaction(TransactionIsolationLevel.EXCLUSIVE) as conn:
        # Check that we got the mock connection
        assert conn is mock_conn

    # Check that the pool's transaction method was called with the right isolation level
    mock_pool.transaction.assert_called_once_with(TransactionIsolationLevel.EXCLUSIVE)


def test_pool_service_savepoint(pool_service: DatabasePoolService) -> None:
    """Test savepoint method.

    Args:
        pool_service: Database pool service fixture.
    """
    # Setup the mock pool
    mock_pool = pool_service.get_pool()
    mock_conn = MagicMock(spec=sqlite3.Connection)

    # Mock the savepoint context manager
    mock_pool.savepoint.return_value.__enter__.return_value = mock_conn

    # Use the savepoint context manager
    with pool_service.savepoint("test_savepoint") as conn:
        # Check that we got the mock connection
        assert conn is mock_conn

    # Check that the pool's savepoint method was called with the right name
    mock_pool.savepoint.assert_called_once_with("test_savepoint")


def test_pool_service_get_connection(pool_service: DatabasePoolService) -> None:
    """Test get_connection method.

    Args:
        pool_service: Database pool service fixture.
    """
    # Setup the mock pool
    mock_pool = pool_service.get_pool()
    mock_conn = MagicMock(spec=sqlite3.Connection)

    # Mock the get_connection context manager
    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    # Use the get_connection context manager
    with pool_service.get_connection(timeout=10.0) as conn:
        # Check that we got the mock connection
        assert conn is mock_conn

    # Check that the pool's get_connection method was called with the right timeout
    mock_pool.get_connection.assert_called_once_with(10.0)


def test_pool_service_get_stats(pool_service: DatabasePoolService) -> None:
    """Test get_stats method.

    Args:
        pool_service: Database pool service fixture.
    """
    # Setup the mock pool
    mock_pool = pool_service.get_pool()
    mock_stats = {
        "idle_connections": 2,
        "active_connections": 1,
        "total_created": 5,
        "total_closed": 2,
    }
    mock_pool.get_stats.return_value = mock_stats

    # Get the stats
    stats = pool_service.get_stats()

    # Check that the pool's get_stats method was called
    mock_pool.get_stats.assert_called_once()
    assert stats is mock_stats


def test_pool_service_shutdown(pool_service: DatabasePoolService) -> None:
    """Test shutdown method.

    Args:
        pool_service: Database pool service fixture.
    """
    # Shutdown the service
    pool_service.shutdown()

    # Check that the service is no longer initialized
    assert not pool_service._initialized
