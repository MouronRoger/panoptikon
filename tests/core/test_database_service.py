"""Tests for the main database service."""

from collections.abc import Generator
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from panoptikon.core.config import ConfigSection, ConfigurationSystem
from panoptikon.core.errors import DatabaseError
from panoptikon.core.events import EventBus
from panoptikon.database.config import DatabaseConfig
from panoptikon.database.query_builder import QueryBuilder
from panoptikon.database.service import DatabaseService


@pytest.fixture
def event_bus() -> EventBus:
    """Create a mock event bus for testing."""
    return MagicMock(spec=EventBus)


@pytest.fixture
def config_system(event_bus: EventBus) -> ConfigurationSystem:
    """Create a config system for testing."""
    return ConfigurationSystem(event_bus)


@pytest.fixture
def temp_db_path() -> Generator[Path, None, None]:
    """Create a temporary database path for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        yield db_path


def test_database_service_init(config_system: ConfigurationSystem) -> None:
    """Test that DatabaseService initializes correctly."""
    service = DatabaseService(config_system)
    assert service.config_system == config_system
    assert not service._initialized


def test_database_service_initialize(
    config_system: ConfigurationSystem, temp_db_path: Path
) -> None:
    """Test initializing the database service."""

    # Mock config to use our temp path
    def get_as_model_mock(section: str) -> ConfigSection:
        if section == "database":
            return DatabaseConfig(
                path=temp_db_path,
                timeout=5.0,
                pragma_synchronous=1,
                pragma_journal_mode="WAL",
                pragma_temp_store=2,
                pragma_cache_size=2000,
                create_if_missing=True,
            )
        raise KeyError(f"Section {section} not registered")

    config_system.get_as_model = MagicMock(side_effect=get_as_model_mock)

    # Create service and initialize
    service = DatabaseService(config_system)
    service.initialize()

    # Verify it's initialized
    assert service._initialized
    assert service._connection is not None
    assert service._schema_manager is not None
    assert service._config is not None
    assert service._config.path == temp_db_path

    # Verify database exists and schema was created
    assert temp_db_path.exists()

    # Test that we can execute queries
    cursor = service.execute("SELECT version FROM schema_version WHERE id = 1")
    result = cursor.fetchone()
    assert result is not None


def test_database_service_shutdown(
    config_system: ConfigurationSystem, temp_db_path: Path
) -> None:
    """Test shutting down the database service."""

    # Mock config
    def get_as_model_mock(section: str) -> ConfigSection:
        if section == "database":
            return DatabaseConfig(
                path=temp_db_path,
                timeout=5.0,
                pragma_synchronous=1,
                pragma_journal_mode="WAL",
                pragma_temp_store=2,
                pragma_cache_size=2000,
                create_if_missing=True,
            )
        raise KeyError(f"Section {section} not registered")

    config_system.get_as_model = MagicMock(side_effect=get_as_model_mock)

    # Create service and initialize
    service = DatabaseService(config_system)
    service.initialize()

    # Verify it's initialized
    assert service._initialized

    # Mock the connection close method using patch.object
    assert service._connection is not None
    with patch.object(service._connection, "close", autospec=True) as mock_close:
        # Shutdown
        service.shutdown()
        # Verify shutdown
        assert not service._initialized
        mock_close.assert_called_once()


def test_database_service_get_connection(
    config_system: ConfigurationSystem, temp_db_path: Path
) -> None:
    """Test getting the database connection."""

    # Mock config
    def get_as_model_mock(section: str) -> ConfigSection:
        if section == "database":
            return DatabaseConfig(
                path=temp_db_path,
                timeout=5.0,
                pragma_synchronous=1,
                pragma_journal_mode="WAL",
                pragma_temp_store=2,
                pragma_cache_size=2000,
                create_if_missing=True,
            )
        raise KeyError(f"Section {section} not registered")

    config_system.get_as_model = MagicMock(side_effect=get_as_model_mock)

    # Create service
    service = DatabaseService(config_system)

    # Should raise error if not initialized
    with pytest.raises(DatabaseError):
        service.get_connection()

    # Initialize and try again
    service.initialize()
    connection = service.get_connection()

    # Should return a valid connection
    assert connection is not None
    assert connection is service._connection


def test_database_service_execute(
    config_system: ConfigurationSystem, temp_db_path: Path
) -> None:
    """Test executing a query through the service."""

    # Mock config
    def get_as_model_mock(section: str) -> ConfigSection:
        if section == "database":
            return DatabaseConfig(
                path=temp_db_path,
                timeout=5.0,
                pragma_synchronous=1,
                pragma_journal_mode="WAL",
                pragma_temp_store=2,
                pragma_cache_size=2000,
                create_if_missing=True,
            )
        raise KeyError(f"Section {section} not registered")

    config_system.get_as_model = MagicMock(side_effect=get_as_model_mock)

    # Create service and initialize
    service = DatabaseService(config_system)
    service.initialize()

    # Create a test table
    service.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")

    # Insert data
    service.execute("INSERT INTO test (id, value) VALUES (?, ?)", (1, "test"))

    # Query data
    cursor = service.execute("SELECT value FROM test WHERE id = ?", (1,))
    result = cursor.fetchone()
    assert result is not None
    assert result[0] == "test"


def test_database_service_execute_many(
    config_system: ConfigurationSystem, temp_db_path: Path
) -> None:
    """Test executing a batch query through the service."""

    # Mock config
    def get_as_model_mock(section: str) -> ConfigSection:
        if section == "database":
            return DatabaseConfig(
                path=temp_db_path,
                timeout=5.0,
                pragma_synchronous=1,
                pragma_journal_mode="WAL",
                pragma_temp_store=2,
                pragma_cache_size=2000,
                create_if_missing=True,
            )
        raise KeyError(f"Section {section} not registered")

    config_system.get_as_model = MagicMock(side_effect=get_as_model_mock)

    # Create service and initialize
    service = DatabaseService(config_system)
    service.initialize()

    # Create a test table
    service.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")

    # Insert batch data
    data = [(1, "test1"), (2, "test2"), (3, "test3")]
    from typing import Any, Union, cast

    # Cast to correct type for mypy
    service.execute_many(
        "INSERT INTO test (id, value) VALUES (?, ?)",
        cast(list[Union[tuple[Any, ...], dict[str, Any]]], data),
    )

    # Verify data
    cursor = service.execute("SELECT COUNT(*) FROM test")
    assert cursor.fetchone()[0] == 3

    cursor = service.execute("SELECT value FROM test WHERE id = ?", (2,))
    assert cursor.fetchone()[0] == "test2"


def test_database_service_properties(
    config_system: ConfigurationSystem, temp_db_path: Path
) -> None:
    """Test the service properties."""

    # Mock config
    def get_as_model_mock(section: str) -> ConfigSection:
        if section == "database":
            return DatabaseConfig(
                path=temp_db_path,
                timeout=5.0,
                pragma_synchronous=1,
                pragma_journal_mode="WAL",
                pragma_temp_store=2,
                pragma_cache_size=2000,
                create_if_missing=True,
            )
        raise KeyError(f"Section {section} not registered")

    config_system.get_as_model = MagicMock(side_effect=get_as_model_mock)

    # Create service
    service = DatabaseService(config_system)

    # Should raise error if not initialized
    with pytest.raises(DatabaseError):
        _ = service.schema_manager

    with pytest.raises(DatabaseError):
        _ = service.config

    # Initialize and try again
    service.initialize()

    # Should return valid objects
    assert service.schema_manager is not None
    assert service.schema_manager is service._schema_manager

    assert service.config is not None
    assert service.config is service._config


def test_execute_with_statement_registry(
    config_system: ConfigurationSystem, temp_db_path: Path
) -> None:
    """Test execute with StatementRegistry enabled."""

    def get_as_model_mock(section: str) -> ConfigSection:
        if section == "database":
            return DatabaseConfig(
                path=temp_db_path,
                timeout=5.0,
                pragma_synchronous=1,
                pragma_journal_mode="WAL",
                pragma_temp_store=2,
                pragma_cache_size=2000,
                create_if_missing=True,
            )
        raise KeyError(f"Section {section} not registered")

    config_system.get_as_model = MagicMock(side_effect=get_as_model_mock)
    service = DatabaseService(config_system)
    service.initialize()
    service.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
    service.execute(
        "INSERT INTO test (id, value) VALUES (?, ?)", (1, "foo"), use_registry=True
    )
    cursor = service.execute(
        "SELECT value FROM test WHERE id = ?", (1,), use_registry=True
    )
    assert cursor.fetchone()[0] == "foo"


def test_execute_with_performance_monitor(
    config_system: ConfigurationSystem, temp_db_path: Path
) -> None:
    """Test execute with performance monitoring enabled."""

    def get_as_model_mock(section: str) -> ConfigSection:
        if section == "database":
            return DatabaseConfig(
                path=temp_db_path,
                timeout=5.0,
                pragma_synchronous=1,
                pragma_journal_mode="WAL",
                pragma_temp_store=2,
                pragma_cache_size=2000,
                create_if_missing=True,
            )
        raise KeyError(f"Section {section} not registered")

    config_system.get_as_model = MagicMock(side_effect=get_as_model_mock)
    service = DatabaseService(config_system)
    service.initialize()
    service.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
    service.execute(
        "INSERT INTO test (id, value) VALUES (?, ?)", (1, "bar"), monitor=True
    )
    cursor = service.execute("SELECT value FROM test WHERE id = ?", (1,), monitor=True)
    assert cursor.fetchone()[0] == "bar"
    # Check that timing was recorded
    assert service.get_connection().performance_monitor.query_times


def test_execute_with_optimizer_index_hint(
    config_system: ConfigurationSystem, temp_db_path: Path
) -> None:
    """Test execute with optimizer index hint."""

    def get_as_model_mock(section: str) -> ConfigSection:
        if section == "database":
            return DatabaseConfig(
                path=temp_db_path,
                timeout=5.0,
                pragma_synchronous=1,
                pragma_journal_mode="WAL",
                pragma_temp_store=2,
                pragma_cache_size=2000,
                create_if_missing=True,
            )
        raise KeyError(f"Section {section} not registered")

    config_system.get_as_model = MagicMock(side_effect=get_as_model_mock)
    service = DatabaseService(config_system)
    service.initialize()
    service.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
    service.execute("CREATE INDEX idx_test_value ON test(value)")
    service.execute(
        "INSERT INTO test (id, value) VALUES (?, ?)", (1, "baz"), optimize=True
    )
    cursor = service.execute(
        "SELECT value FROM test WHERE id = ?",
        (1,),
        optimize=True,
        index_hint="idx_test_value",
    )
    assert cursor.fetchone()[0] == "baz"


def test_execute_with_result_cache(
    config_system: ConfigurationSystem, temp_db_path: Path
) -> None:
    """Test execute with result caching enabled."""

    def get_as_model_mock(section: str) -> ConfigSection:
        if section == "database":
            return DatabaseConfig(
                path=temp_db_path,
                timeout=5.0,
                pragma_synchronous=1,
                pragma_journal_mode="WAL",
                pragma_temp_store=2,
                pragma_cache_size=2000,
                create_if_missing=True,
            )
        raise KeyError(f"Section {section} not registered")

    config_system.get_as_model = MagicMock(side_effect=get_as_model_mock)
    service = DatabaseService(config_system)
    service.initialize()
    service.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
    service.execute("INSERT INTO test (id, value) VALUES (?, ?)", (1, "cacheme"))
    # First query (not cached)
    cursor = service.execute(
        "SELECT value FROM test WHERE id = ?", (1,), cache_result=True
    )
    assert cursor.fetchone()[0] == "cacheme"
    # Second query (should hit cache, fallback to cursor)
    cursor2 = service.execute(
        "SELECT value FROM test WHERE id = ?", (1,), cache_result=True
    )
    assert cursor2.fetchone()[0] == "cacheme"


def test_execute_many_with_batch(
    config_system: ConfigurationSystem, temp_db_path: Path
) -> None:
    """Test execute_many with batch optimization enabled."""

    def get_as_model_mock(section: str) -> ConfigSection:
        if section == "database":
            return DatabaseConfig(
                path=temp_db_path,
                timeout=5.0,
                pragma_synchronous=1,
                pragma_journal_mode="WAL",
                pragma_temp_store=2,
                pragma_cache_size=2000,
                create_if_missing=True,
            )
        raise KeyError(f"Section {section} not registered")

    config_system.get_as_model = MagicMock(side_effect=get_as_model_mock)
    service = DatabaseService(config_system)
    service.initialize()
    service.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
    data = [(1, "a"), (2, "b"), (3, "c")]
    service.execute_many(
        "INSERT INTO test (id, value) VALUES (?, ?)", data, optimize=True, batch=True
    )
    cursor = service.execute("SELECT COUNT(*) FROM test")
    assert cursor.fetchone()[0] == 3


def test_query_builder_safe_identifier_valid() -> None:
    assert QueryBuilder.safe_identifier("foo") == '"foo"'
    assert QueryBuilder.safe_identifier("foo_bar123") == '"foo_bar123"'


def test_query_builder_safe_identifier_invalid() -> None:
    import pytest

    with pytest.raises(ValueError):
        QueryBuilder.safe_identifier("foo-bar")
    with pytest.raises(ValueError):
        QueryBuilder.safe_identifier("123abc")
    with pytest.raises(ValueError):
        QueryBuilder.safe_identifier("foo bar")


def test_query_builder_build_where_clause() -> None:
    clause, params = QueryBuilder.build_where_clause({"id": 1, "name": "x"})
    assert clause == '"id" = :id AND "name" = :name'
    assert params == {"id": 1, "name": "x"}
    clause, params = QueryBuilder.build_where_clause({}, param_style="?{name}")
    assert clause == ""
    assert params == {}


def test_query_builder_build_insert() -> None:
    sql, params = QueryBuilder.build_insert("test", {"id": 1, "val": "a"})
    assert sql.startswith('INSERT INTO "test" (')
    assert params == {"id": 1, "val": "a"}
    sql, params = QueryBuilder.build_insert("t", {})
    assert ") VALUES ()" in sql
    assert params == {}


def test_query_builder_build_update() -> None:
    sql, params = QueryBuilder.build_update("test", {"val": "b"}, {"id": 2})
    assert sql.startswith('UPDATE "test" SET "val" = :val WHERE "id" = :id')
    assert params == {"val": "b", "id": 2}
    sql, params = QueryBuilder.build_update("t", {}, {})
    assert "SET " in sql and "WHERE " in sql
    assert params == {}


def test_statement_registry_prepare_and_bind(tmp_path) -> None:
    import sqlite3

    from panoptikon.database.statement_registry import StatementRegistry

    db_path = tmp_path / "test_stmt.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)")
    reg = StatementRegistry()
    # Prepare and bind
    cursor = reg.prepare(conn, "SELECT 1")
    assert cursor is not None
    cursor2 = reg.prepare(conn, "SELECT 1")
    assert cursor2 is cursor  # Should be cached
    # Bind and execute
    conn.execute("INSERT INTO t (id, v) VALUES (?, ?)", (1, "a"))
    cursor = reg.bind_and_execute(conn, "SELECT v FROM t WHERE id = ?", (1,))
    assert cursor.fetchone()[0] == "a"


def test_statement_registry_cleanup_and_clear(tmp_path) -> None:
    import sqlite3
    import time

    from panoptikon.database.statement_registry import StatementRegistry

    db_path = tmp_path / "test_stmt2.db"
    conn = sqlite3.connect(db_path)
    reg = StatementRegistry()
    reg._cache_ttl = 0.01  # Short TTL for test
    reg.prepare(conn, "SELECT 1")
    assert "SELECT 1" in reg._statements
    time.sleep(0.02)
    reg.cleanup()
    assert "SELECT 1" not in reg._statements
    reg.prepare(conn, "SELECT 2")
    reg.clear()
    assert not reg._statements and not reg._cache_times
