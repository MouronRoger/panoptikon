"""Tests for the database pool service implementation."""

from collections.abc import Generator
from pathlib import Path
import sqlite3
import threading
import time
from typing import List
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
    # Patch the connection returned by get_connection()
    mock_conn = MagicMock(spec=sqlite3.Connection)
    with patch.object(pool_service.get_pool(), "get_connection") as mock_get_conn:
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        mock_conn.execute.return_value = mock_cursor
        # Execute a query
        result = pool_service.execute("SELECT * FROM test")
        # Check that the connection's execute method was called
        mock_conn.execute.assert_called_once_with("SELECT * FROM test")
        assert result is mock_cursor


def test_pool_service_execute_many(pool_service: DatabasePoolService) -> None:
    """Test execute_many method.

    Args:
        pool_service: Database pool service fixture.
    """
    # Patch the connection returned by get_connection()
    mock_conn = MagicMock(spec=sqlite3.Connection)
    with patch.object(pool_service.get_pool(), "get_connection") as mock_get_conn:
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        mock_conn.executemany.return_value = mock_cursor
        # Execute a query with multiple parameters
        params = [(1, "test"), (2, "test2")]
        result = pool_service.execute_many("INSERT INTO test VALUES (?, ?)", params)
        # Check that the connection's executemany method was called
        mock_conn.executemany.assert_called_once_with(
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


@pytest.fixture
def real_pool_service(tmp_path: Path) -> Generator[DatabasePoolService, None, None]:
    """Create a real DatabasePoolService with a real SQLite file for integration tests."""
    db_path = tmp_path / "integration_test.db"
    config = MagicMock(spec=DatabaseConfig)
    config.path = db_path
    config.timeout = 1.0
    config.max_connections = 20
    config.min_connections = 1
    config.create_if_missing = True
    config.connection_max_age = 10.0
    config.health_check_interval = 1.0
    config.pragma_synchronous = 1
    config.pragma_journal_mode = "WAL"
    config.pragma_temp_store = 2
    config.pragma_cache_size = 2000
    config.connection_max_age = 10.0
    config.health_check_interval = 1.0

    config_system = MagicMock(spec=ConfigurationSystem)
    config_system.get_as_model.return_value = config

    service = DatabasePoolService(config_system)
    service.initialize()
    # Create a test table
    with service.get_connection() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, value TEXT)"
        )
    yield service
    service.shutdown()


@pytest.mark.parametrize("num_threads", [10, 50, 100])
def test_pool_service_concurrent_access_integration(
    real_pool_service: DatabasePoolService, num_threads: int
) -> None:
    """Integration: Test concurrent access to DatabasePoolService with real SQLite file.

    Under high concurrency, SQLite's single-writer limitation means not all threads
    will succeed. This test asserts that a reasonable number of threads succeed.
    """
    errors: List[Exception] = []
    successes = 0
    lock = threading.Lock()

    def worker(thread_id: int) -> None:
        nonlocal successes
        try:
            with real_pool_service.transaction() as conn:
                conn.execute(
                    "INSERT INTO test (id, value) VALUES (?, ?)",
                    (thread_id, f"thread {thread_id}"),
                )
                time.sleep(0.005)
            with real_pool_service.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT value FROM test WHERE id = ?", (thread_id,)
                )
                result = cursor.fetchone()
                if result and result[0] == f"thread {thread_id}":
                    with lock:
                        successes += 1
                else:
                    raise Exception("Read after write failed")
        except Exception as e:
            errors.append(e)

    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=worker, args=(10000 + i,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    assert successes >= num_threads // 2, (
        f"Expected at least 50% success, got {successes}/{num_threads}"
    )
    for e in errors:
        msg = str(e)
        assert (
            "locked" in msg
            or "busy" in msg
            or "cannot rollback" in msg
            or isinstance(e, DatabaseError)
        )


def test_pool_service_writer_contention_integration(
    real_pool_service: DatabasePoolService,
) -> None:
    """Integration: Test writer contention with many threads using DatabasePoolService.

    Many threads attempt to write at once. Some will fail due to SQLite's single-writer limitation.
    """
    num_threads = 30
    errors: List[Exception] = []
    successes = 0
    lock = threading.Lock()

    def writer(thread_id: int) -> None:
        nonlocal successes
        try:
            with real_pool_service.transaction(
                TransactionIsolationLevel.IMMEDIATE
            ) as conn:
                conn.execute(
                    "INSERT INTO test (id, value) VALUES (?, ?)",
                    (20000 + thread_id, f"writer {thread_id}"),
                )
                time.sleep(0.01)
            with lock:
                successes += 1
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=writer, args=(i,)) for i in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert successes > 0
    for e in errors:
        msg = str(e)
        assert (
            "locked" in msg
            or "busy" in msg
            or "cannot rollback" in msg
            or isinstance(e, DatabaseError)
        )


def test_pool_service_stress_leak_prevention_integration(
    real_pool_service: DatabasePoolService,
) -> None:
    """Integration: Stress test for leak/deadlock prevention with DatabasePoolService.

    Many threads, many iterations. All connections should be returned to the pool.
    """
    num_threads = 20
    iterations = 10
    errors: List[Exception] = []

    def worker(thread_id: int) -> None:
        for j in range(iterations):
            try:
                with real_pool_service.transaction() as conn:
                    conn.execute(
                        "INSERT INTO test (id, value) VALUES (?, ?)",
                        (30000 + thread_id * 1000 + j, f"stress {thread_id}-{j}"),
                    )
                with real_pool_service.get_connection() as conn:
                    cursor = conn.execute(
                        "SELECT value FROM test WHERE id = ?",
                        (30000 + thread_id * 1000 + j,),
                    )
                    result = cursor.fetchone()
                    assert result[0] == f"stress {thread_id}-{j}"
            except Exception as e:
                errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    stats = real_pool_service.get_stats()
    assert stats["active_connections"] == 0
    assert stats["idle_connections"] >= 1
    for e in errors:
        msg = str(e)
        assert "deadlock" not in msg.lower()


def test_pool_execute_with_statement_registry(
    real_pool_service: DatabasePoolService,
) -> None:
    """Test execute with StatementRegistry enabled in pool service."""
    real_pool_service.execute(
        "CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, value TEXT)"
    )
    real_pool_service.execute(
        "INSERT INTO test (id, value) VALUES (?, ?)", (1, "foo"), use_registry=True
    )
    cursor = real_pool_service.execute(
        "SELECT value FROM test WHERE id = ?", (1,), use_registry=True
    )
    assert cursor.fetchone()[0] == "foo"


def test_pool_execute_with_performance_monitor(
    real_pool_service: DatabasePoolService,
) -> None:
    """Test execute with performance monitoring enabled in pool service."""
    real_pool_service.execute(
        "CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, value TEXT)"
    )
    real_pool_service.execute(
        "INSERT INTO test (id, value) VALUES (?, ?)", (1, "bar"), monitor=True
    )
    cursor = real_pool_service.execute(
        "SELECT value FROM test WHERE id = ?", (1,), monitor=True
    )
    assert cursor.fetchone()[0] == "bar"
    assert real_pool_service.performance_monitor.query_times


def test_pool_execute_with_optimizer_index_hint(
    real_pool_service: DatabasePoolService,
) -> None:
    """Test execute with optimizer index hint in pool service."""
    real_pool_service.execute(
        "CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, value TEXT)"
    )
    real_pool_service.execute(
        "CREATE INDEX IF NOT EXISTS idx_test_value ON test(value)"
    )
    real_pool_service.execute(
        "INSERT INTO test (id, value) VALUES (?, ?)", (1, "baz"), optimize=True
    )
    cursor = real_pool_service.execute(
        "SELECT value FROM test WHERE id = ?",
        (1,),
        optimize=True,
        index_hint="idx_test_value",
    )
    assert cursor.fetchone()[0] == "baz"


def test_pool_execute_with_result_cache(real_pool_service: DatabasePoolService) -> None:
    """Test execute with result caching enabled in pool service."""
    real_pool_service.execute(
        "CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, value TEXT)"
    )
    real_pool_service.execute(
        "INSERT INTO test (id, value) VALUES (?, ?)", (1, "cacheme")
    )
    cursor = real_pool_service.execute(
        "SELECT value FROM test WHERE id = ?", (1,), cache_result=True
    )
    assert cursor.fetchone()[0] == "cacheme"
    cursor2 = real_pool_service.execute(
        "SELECT value FROM test WHERE id = ?", (1,), cache_result=True
    )
    assert cursor2.fetchone()[0] == "cacheme"


def test_pool_execute_many_with_batch(real_pool_service: DatabasePoolService) -> None:
    """Test execute_many with batch optimization enabled in pool service."""
    real_pool_service.execute(
        "CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, value TEXT)"
    )
    data = [(1, "a"), (2, "b"), (3, "c")]
    real_pool_service.execute_many(
        "INSERT INTO test (id, value) VALUES (?, ?)", data, optimize=True, batch=True
    )
    cursor = real_pool_service.execute("SELECT COUNT(*) FROM test")
    assert cursor.fetchone()[0] == 3
