"""Tests for the main database service."""

from collections.abc import Generator
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from panoptikon.core.config import (  # type: ignore[import-untyped]
    ConfigSection,
    ConfigurationSystem,
)
from panoptikon.core.errors import DatabaseError  # type: ignore[import-untyped]
from panoptikon.core.events import EventBus  # type: ignore[import-untyped]
from panoptikon.database.config import DatabaseConfig  # type: ignore[import-untyped]
from panoptikon.database.service import DatabaseService  # type: ignore[import-untyped]


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
