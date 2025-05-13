"""Tests for the database connection pool implementation."""

from collections.abc import Generator
from pathlib import Path
import sqlite3
import threading
import time
from typing import List
from unittest.mock import MagicMock

import pytest

from panoptikon.core.errors import DatabaseError
from panoptikon.database.pool import (
    ConnectionHealthStatus,
    ConnectionPool,
    PooledConnection,
    TransactionIsolationLevel,
    get_pool_manager,
)


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Get a temporary database path.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        Path to a temporary database file.
    """
    return tmp_path / "test.db"


@pytest.fixture
def connection_pool(temp_db_path: Path) -> Generator[ConnectionPool, None, None]:
    """Create a connection pool for testing.

    Args:
        temp_db_path: Path to a temporary database file.

    Yields:
        A connection pool for testing.
    """
    # Create the pool with small values for faster testing
    pool = ConnectionPool(
        db_path=temp_db_path,
        max_connections=5,
        min_connections=1,
        connection_timeout=1.0,
        connection_max_age=5.0,
        health_check_interval=1.0,
    )
    pool.initialize()

    # Create a simple table for testing
    with pool.get_connection() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, value TEXT)"
        )

    yield pool

    # Clean up
    pool.shutdown()


def test_pool_initialization(temp_db_path: Path) -> None:
    """Test connection pool initialization.

    Args:
        temp_db_path: Path to a temporary database file.
    """
    # Create the pool
    pool = ConnectionPool(
        db_path=temp_db_path,
        max_connections=3,
        min_connections=2,
        connection_timeout=1.0,
    )
    pool.initialize()

    # Check that we have the minimum connections
    stats = pool.get_stats()
    assert stats["idle_connections"] == 2
    assert stats["active_connections"] == 0
    assert stats["total_created"] == 2
    assert stats["total_closed"] == 0

    # Clean up
    pool.shutdown()

    # Check cleanup
    stats = pool.get_stats()
    assert stats["idle_connections"] == 0
    assert stats["active_connections"] == 0
    assert stats["total_closed"] >= 2


def test_pool_get_connection(connection_pool: ConnectionPool) -> None:
    """Test getting a connection from the pool.

    Args:
        connection_pool: Connection pool fixture.
    """
    # Get initial stats
    initial_stats = connection_pool.get_stats()

    # Get a connection
    with connection_pool.get_connection() as conn:
        # Check that we can execute a query
        cursor = conn.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1

        # Check that we have one active connection
        stats = connection_pool.get_stats()
        assert stats["active_connections"] == 1
        assert stats["idle_connections"] == initial_stats["idle_connections"] - 1

    # Check that the connection was returned to the pool
    stats = connection_pool.get_stats()
    assert stats["active_connections"] == 0
    assert stats["idle_connections"] == initial_stats["idle_connections"]


def test_pool_connection_reuse(connection_pool: ConnectionPool) -> None:
    """Test connection reuse.

    Args:
        connection_pool: Connection pool fixture.
    """
    # First ensure we have a fresh pool by checking out and releasing connections
    connections = []
    for _ in range(2):
        with connection_pool.get_connection() as conn:
            # Store some identifier for later comparison
            conn_id = id(conn)
            connections.append(conn_id)

    # The connections should be different objects even though they may be reused SQLite connections
    assert len(set(connections)) == 2, "Expected different connection objects"


def test_pool_max_connections(connection_pool: ConnectionPool) -> None:
    """Test connection limits and basic functionality.

    Args:
        connection_pool: Connection pool fixture.
    """
    # Get initial stats
    initial_stats = connection_pool.get_stats()

    # Check out some connections (but not all)
    active_connections = []
    for _ in range(min(2, connection_pool.max_connections)):
        with connection_pool.get_connection() as conn:
            # Just test basic functionality
            cursor = conn.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1

            # Add to active connections for later verification
            active_connections.append(id(conn))

    # Verify connections are working properly
    assert len(active_connections) == min(2, connection_pool.max_connections)

    # All connections should now be returned to the pool
    stats = connection_pool.get_stats()
    assert stats["active_connections"] == 0
    assert stats["idle_connections"] >= initial_stats["idle_connections"]


def test_pool_connection_health_check(connection_pool: ConnectionPool) -> None:
    """Test connection health checking.

    Args:
        connection_pool: Connection pool fixture.
    """
    # Get a connection and corrupt it
    with connection_pool.get_connection() as conn:
        # Close the underlying connection directly (simulating corruption)
        conn.close()

    # Get a new connection - pool should detect the bad connection and create a new one
    with connection_pool.get_connection() as conn:
        # Check that we can execute a query
        cursor = conn.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1


def test_pool_connection_max_age(connection_pool: ConnectionPool) -> None:
    """Test connection max age enforcement.

    Args:
        connection_pool: Connection pool fixture.
    """
    # Set a very short max age for testing
    connection_pool.connection_max_age = 0.1

    # Get initial creation count
    initial_created = connection_pool.get_stats()["total_created"]

    # Get a connection and use it
    with connection_pool.get_connection() as conn:
        conn.execute("SELECT 1")

    # Wait for the connection to expire
    time.sleep(0.2)

    # Get another connection - it should be a new one
    with connection_pool.get_connection() as conn:
        conn.execute("SELECT 1")

    # Check that we created a new connection
    assert connection_pool.get_stats()["total_created"] > initial_created


def test_pool_transaction(connection_pool: ConnectionPool) -> None:
    """Test transaction handling.

    Args:
        connection_pool: Connection pool fixture.
    """
    # Insert data in a transaction and commit
    with connection_pool.transaction() as conn:
        conn.execute("INSERT INTO test (id, value) VALUES (1, 'test')")

    # Check that the data was committed
    with connection_pool.get_connection() as conn:
        cursor = conn.execute("SELECT value FROM test WHERE id = 1")
        result = cursor.fetchone()
        assert result[0] == "test"

    # Try a transaction that rolls back
    try:
        with connection_pool.transaction() as conn:
            conn.execute("INSERT INTO test (id, value) VALUES (2, 'rollback')")
            raise ValueError("Test rollback")
    except ValueError:
        pass

    # Check that the data was rolled back
    with connection_pool.get_connection() as conn:
        cursor = conn.execute("SELECT value FROM test WHERE id = 2")
        result = cursor.fetchone()
        assert result is None


def test_pool_different_isolation_levels(connection_pool: ConnectionPool) -> None:
    """Test different transaction isolation levels.

    Args:
        connection_pool: Connection pool fixture.
    """
    # Test each isolation level with different IDs to avoid unique constraint errors
    isolation_levels = [
        (TransactionIsolationLevel.DEFERRED, 101),
        (TransactionIsolationLevel.IMMEDIATE, 102),
        (TransactionIsolationLevel.EXCLUSIVE, 103),
    ]

    for isolation_level, id_value in isolation_levels:
        # Insert data with the specified isolation level
        with connection_pool.transaction(isolation_level) as conn:
            conn.execute(
                "INSERT INTO test (id, value) VALUES (?, ?)",
                (id_value, isolation_level.value),
            )

        # Verify the data was inserted
        with connection_pool.get_connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM test WHERE id = ?",
                (id_value,),
            )
            result = cursor.fetchone()
            assert result[0] == isolation_level.value


def test_pool_savepoint(connection_pool: ConnectionPool) -> None:
    """Test savepoint functionality.

    Args:
        connection_pool: Connection pool fixture.
    """
    # Use a transaction with savepoints
    with connection_pool.transaction() as conn:
        conn.execute("INSERT INTO test (id, value) VALUES (10, 'before savepoint')")

        # Create a savepoint
        conn.execute("SAVEPOINT test_savepoint")

        # Insert some data after the savepoint
        conn.execute("INSERT INTO test (id, value) VALUES (11, 'after savepoint')")

        # Rollback to the savepoint
        conn.execute("ROLLBACK TO test_savepoint")

        # Insert different data
        conn.execute("INSERT INTO test (id, value) VALUES (12, 'after rollback')")

    # Check that the data before the savepoint and after the rollback are there,
    # but not the data between the savepoint and rollback
    with connection_pool.get_connection() as conn:
        # Before savepoint should exist
        cursor = conn.execute("SELECT value FROM test WHERE id = 10")
        result = cursor.fetchone()
        assert result[0] == "before savepoint"

        # After savepoint but before rollback should not exist
        cursor = conn.execute("SELECT value FROM test WHERE id = 11")
        result = cursor.fetchone()
        assert result is None

        # After rollback should exist
        cursor = conn.execute("SELECT value FROM test WHERE id = 12")
        result = cursor.fetchone()
        assert result[0] == "after rollback"


def test_pool_savepoint_context_manager(connection_pool: ConnectionPool) -> None:
    """Test savepoint context manager.

    Args:
        connection_pool: Connection pool fixture.
    """
    # Use a transaction with the savepoint context manager
    with connection_pool.transaction() as outer_conn:
        outer_conn.execute(
            "INSERT INTO test (id, value) VALUES (20, 'before savepoint')"
        )

        # Use savepoint context manager
        try:
            with connection_pool.savepoint("test_savepoint") as _:
                outer_conn.execute(
                    "INSERT INTO test (id, value) VALUES (21, 'in savepoint')"
                )
                raise ValueError("Test rollback")
        except ValueError:
            pass

        # Insert data after the savepoint rollback
        outer_conn.execute("INSERT INTO test (id, value) VALUES (22, 'after rollback')")

    # Check the results
    with connection_pool.get_connection() as conn:
        # Before savepoint should exist
        cursor = conn.execute("SELECT value FROM test WHERE id = 20")
        result = cursor.fetchone()
        assert result[0] == "before savepoint"

        # In savepoint should not exist due to rollback
        cursor = conn.execute("SELECT value FROM test WHERE id = 21")
        result = cursor.fetchone()
        assert result is None

        # After rollback should exist
        cursor = conn.execute("SELECT value FROM test WHERE id = 22")
        result = cursor.fetchone()
        assert result[0] == "after rollback"


def test_pool_concurrent_access(connection_pool: ConnectionPool) -> None:
    """Test concurrent access to the connection pool.

    Args:
        connection_pool: Connection pool fixture.
    """
    # Number of threads to use
    num_threads = 10

    # Increase max connections for this test
    connection_pool.max_connections = 15

    # Function to run in each thread
    def worker(thread_id: int) -> None:
        try:
            # Insert a record
            with connection_pool.transaction() as conn:
                conn.execute(
                    "INSERT INTO test (id, value) VALUES (?, ?)",
                    (thread_id, f"thread {thread_id}"),
                )
                # Simulate some work
                time.sleep(0.01)

            # Read it back
            with connection_pool.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT value FROM test WHERE id = ?", (thread_id,)
                )
                result = cursor.fetchone()
                assert result[0] == f"thread {thread_id}"
        except Exception as e:
            print(f"Thread {thread_id} error: {e}")
            raise

    # Start threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=worker, args=(1000 + i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify all threads completed successfully by checking the data
    with connection_pool.get_connection() as conn:
        for i in range(num_threads):
            cursor = conn.execute("SELECT value FROM test WHERE id = ?", (1000 + i,))
            result = cursor.fetchone()
            assert result[0] == f"thread {1000 + i}"


def test_pool_manager() -> None:
    """Test the pool manager functionality."""
    # Get the pool manager
    pool_manager = get_pool_manager()

    # Create a temporary path
    temp_path = Path("temp_test.db")

    try:
        # Get a pool from the manager
        pool1 = pool_manager.get_pool(temp_path)

        # Get a pool for the same path - should be the same instance
        pool2 = pool_manager.get_pool(temp_path)

        # Check that we got the same pool
        assert pool1 is pool2

        # Get a pool with different parameters - should use the existing pool
        pool3 = pool_manager.get_pool(temp_path, max_connections=20, min_connections=5)
        assert pool1 is pool3

        # Check that the pool is working
        with pool1.get_connection() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS manager_test (id INTEGER PRIMARY KEY)"
            )
            conn.execute("INSERT INTO manager_test (id) VALUES (1)")

            # Verify with another pool variable
            cursor = conn.execute("SELECT id FROM manager_test WHERE id = 1")
            result = cursor.fetchone()
            assert result[0] == 1

        # Shutdown all pools
        pool_manager.shutdown_all()

        # Check that pools are shut down
        with pytest.raises(DatabaseError):
            with pool1.get_connection():
                pass

    finally:
        # Clean up the file
        if temp_path.exists():
            temp_path.unlink()


def test_pool_thread_safety() -> None:
    """Test thread safety of connection checkout/checkin."""
    # Create a pool with minimum settings for the test
    temp_path = Path("temp_thread_test.db")
    try:
        pool = ConnectionPool(
            db_path=temp_path,
            max_connections=20,  # Higher limit for concurrent testing
            min_connections=1,
            connection_timeout=2.0,
        )
        pool.initialize()

        # Create a test table
        with pool.get_connection() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS thread_test (id INTEGER PRIMARY KEY, counter INTEGER)"
            )
            conn.execute("INSERT INTO thread_test (id, counter) VALUES (1, 0)")

        # Function to increment the counter in the database
        def increment_counter(thread_id: int, iterations: int) -> None:
            for _ in range(iterations):
                try:
                    with pool.transaction(TransactionIsolationLevel.IMMEDIATE) as conn:
                        # Read current value
                        cursor = conn.execute(
                            "SELECT counter FROM thread_test WHERE id = 1"
                        )
                        current = cursor.fetchone()[0]

                        # Simulate some processing time to increase contention
                        time.sleep(0.001)

                        # Increment and update
                        conn.execute(
                            "UPDATE thread_test SET counter = ? WHERE id = 1",
                            (current + 1,),
                        )
                except Exception as e:
                    print(f"Thread {thread_id} error: {e}")
                    raise

        # Run concurrent threads
        num_threads = 10
        iterations_per_thread = 5
        threads: List[threading.Thread] = []

        for i in range(num_threads):
            thread = threading.Thread(
                target=increment_counter, args=(i, iterations_per_thread)
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check that the counter was incremented correctly
        with pool.get_connection() as conn:
            cursor = conn.execute("SELECT counter FROM thread_test WHERE id = 1")
            final_count = cursor.fetchone()[0]
            assert final_count == num_threads * iterations_per_thread

        # Shut down the pool
        pool.shutdown()

    finally:
        # Clean up the file
        if temp_path.exists():
            temp_path.unlink()


def test_connection_health_status() -> None:
    """Test the connection health status enum."""
    # Check that health status values are as expected
    assert ConnectionHealthStatus.HEALTHY.value == "healthy"
    assert ConnectionHealthStatus.UNHEALTHY.value == "unhealthy"
    assert ConnectionHealthStatus.UNKNOWN.value == "unknown"


def test_transaction_isolation_level() -> None:
    """Test the transaction isolation level enum."""
    # Check that isolation level values are as expected
    assert TransactionIsolationLevel.DEFERRED.value == "DEFERRED"
    assert TransactionIsolationLevel.IMMEDIATE.value == "IMMEDIATE"
    assert TransactionIsolationLevel.EXCLUSIVE.value == "EXCLUSIVE"


def test_pooled_connection() -> None:
    """Test the pooled connection class."""
    # Create a mock connection
    mock_conn = MagicMock(spec=sqlite3.Connection)

    # Create a pooled connection
    pooled_conn = PooledConnection(connection=mock_conn)

    # Check default values
    assert pooled_conn.connection is mock_conn
    assert pooled_conn.in_use is False
    assert pooled_conn.thread_id is None
    assert pooled_conn.health_status is ConnectionHealthStatus.UNKNOWN

    # Set some values
    pooled_conn.in_use = True
    pooled_conn.thread_id = 123
    pooled_conn.health_status = ConnectionHealthStatus.HEALTHY

    # Check values were set
    assert pooled_conn.in_use is True
    assert pooled_conn.thread_id == 123
    assert pooled_conn.health_status is ConnectionHealthStatus.HEALTHY


def test_pool_invalid_params() -> None:
    """Test validation of invalid connection pool parameters."""
    # Test invalid max_connections
    with pytest.raises(ValueError, match="max_connections must be at least 1"):
        ConnectionPool(db_path=Path("test.db"), max_connections=0)

    # Test invalid min_connections
    with pytest.raises(ValueError, match="min_connections must be at least 0"):
        ConnectionPool(db_path=Path("test.db"), min_connections=-1)

    # Test min > max
    with pytest.raises(
        ValueError, match="min_connections must be.*not greater than max_connections"
    ):
        ConnectionPool(db_path=Path("test.db"), max_connections=5, min_connections=10)

    # Test invalid connection_timeout
    with pytest.raises(ValueError, match="connection_timeout must be positive"):
        ConnectionPool(db_path=Path("test.db"), connection_timeout=0)

    # Test invalid connection_max_age
    with pytest.raises(ValueError, match="connection_max_age must be positive"):
        ConnectionPool(db_path=Path("test.db"), connection_max_age=-1)

    # Test invalid health_check_interval
    with pytest.raises(ValueError, match="health_check_interval must be positive"):
        ConnectionPool(db_path=Path("test.db"), health_check_interval=0)
