"""Tests for the database connection implementation."""

from collections.abc import Generator
from pathlib import Path
import sqlite3
import tempfile
import threading
import time

import pytest

from panoptikon.core.errors import DatabaseError
from panoptikon.database.connection import DatabaseConnection


@pytest.fixture
def temp_db_path() -> Generator[Path, None, None]:
    """Create a temporary database path for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        # Create an empty database
        conn = sqlite3.connect(str(db_path))
        conn.close()
        yield db_path


def test_connection_init(temp_db_path: Path) -> None:
    """Test that DatabaseConnection initializes correctly."""
    connection = DatabaseConnection(temp_db_path)
    assert connection.db_path == temp_db_path
    assert connection.timeout == 5.0  # Default timeout


def test_connect(temp_db_path: Path) -> None:
    """Test that connect method returns a valid connection."""
    connection = DatabaseConnection(temp_db_path)

    with connection.connect() as conn:
        assert isinstance(conn, sqlite3.Connection)
        # Test that the connection works
        cursor = conn.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1


def test_transaction(temp_db_path: Path) -> None:
    """Test transaction handling."""
    connection = DatabaseConnection(temp_db_path)

    # Create a test table
    with connection.connect() as conn:
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")

    # Test successful transaction
    with connection.transaction() as conn:
        conn.execute("INSERT INTO test (id, value) VALUES (1, 'test1')")
        conn.execute("INSERT INTO test (id, value) VALUES (2, 'test2')")

    # Verify data was committed
    with connection.connect() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM test")
        assert cursor.fetchone()[0] == 2

    # Test transaction rollback on exception
    try:
        with connection.transaction() as conn:
            conn.execute("INSERT INTO test (id, value) VALUES (3, 'test3')")
            # This should cause an error (duplicate primary key)
            conn.execute("INSERT INTO test (id, value) VALUES (1, 'duplicate')")
    except DatabaseError:
        pass  # Expected exception

    # Verify transaction was rolled back
    with connection.connect() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM test")
        assert cursor.fetchone()[0] == 2  # Still only 2 rows


def test_close(temp_db_path: Path) -> None:
    """Test closing the connection."""
    connection = DatabaseConnection(temp_db_path)

    # Open a connection
    with connection.connect() as conn:
        # Verify it's open
        conn.execute("SELECT 1")

    # Close it
    connection.close()

    # Open a new one
    with connection.connect() as conn:
        # Should work fine
        conn.execute("SELECT 1")


def test_execute(temp_db_path: Path) -> None:
    """Test the execute method."""
    connection = DatabaseConnection(temp_db_path)

    # Create a test table
    connection.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")

    # Insert with parameters
    connection.execute("INSERT INTO test (id, value) VALUES (?, ?)", (1, "test1"))

    # Insert with named parameters
    connection.execute(
        "INSERT INTO test (id, value) VALUES (:id, :value)", {"id": 2, "value": "test2"}
    )

    # Query with parameters
    cursor = connection.execute("SELECT value FROM test WHERE id = ?", (2,))
    assert cursor.fetchone()[0] == "test2"

    # Test error handling
    with pytest.raises(DatabaseError):
        connection.execute("INSERT INTO nonexistent_table VALUES (1)")


def test_execute_many(temp_db_path: Path) -> None:
    """Test the execute_many method."""
    connection = DatabaseConnection(temp_db_path)

    # Create a test table
    connection.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")

    # Insert multiple rows
    data = [(1, "test1"), (2, "test2"), (3, "test3")]
    connection.execute_many("INSERT INTO test (id, value) VALUES (?, ?)", data)

    # Verify data was inserted
    cursor = connection.execute("SELECT COUNT(*) FROM test")
    assert cursor.fetchone()[0] == 3

    # Test error handling
    with pytest.raises(DatabaseError):
        connection.execute_many(
            "INSERT INTO nonexistent_table VALUES (?)", [(1,), (2,)]
        )


def test_thread_safety() -> None:
    """Test thread safety of the connection."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        connection = DatabaseConnection(db_path)

        # Create a test table
        with connection.connect() as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")

        def worker(worker_id: int) -> None:
            """Worker function for threads."""
            # Each thread inserts 10 rows
            for i in range(10):
                connection.execute(
                    "INSERT INTO test (id, value) VALUES (?, ?)",
                    (worker_id * 100 + i, f"worker{worker_id}-{i}"),
                )
                time.sleep(
                    0.01
                )  # Small delay to increase chance of thread interactions

        # Create and start 5 threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify each thread's data was inserted correctly
        with connection.connect() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM test")
            assert cursor.fetchone()[0] == 50  # 5 threads × 10 rows

            for i in range(5):
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM test WHERE id >= ? AND id < ?",
                    (i * 100, (i + 1) * 100),
                )
                assert cursor.fetchone()[0] == 10  # Each thread inserted 10 rows
