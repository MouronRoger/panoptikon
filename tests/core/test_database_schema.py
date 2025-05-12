"""Tests for the database schema implementation."""

from collections.abc import Generator
from pathlib import Path
import sqlite3
import tempfile

import pytest

from panoptikon.core.errors import DatabaseError
from panoptikon.database.schema import CURRENT_SCHEMA_VERSION, SchemaManager


@pytest.fixture
def temp_db_path() -> Generator[Path, None, None]:
    """Create a temporary database path for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        yield db_path


def test_schema_manager_init(temp_db_path: Path) -> None:
    """Test that SchemaManager initializes correctly."""
    schema_manager = SchemaManager(temp_db_path)
    assert schema_manager.db_path == temp_db_path
    assert not schema_manager.database_exists()


def test_database_exists(temp_db_path: Path) -> None:
    """Test that database_exists works correctly."""
    schema_manager = SchemaManager(temp_db_path)
    assert not schema_manager.database_exists()

    # Create an empty file
    with open(temp_db_path, "w") as f:
        f.write("")

    assert schema_manager.database_exists()


def test_create_schema(temp_db_path: Path) -> None:
    """Test that the schema is created correctly."""
    schema_manager = SchemaManager(temp_db_path)
    schema_manager.create_schema()

    # Verify that the database file exists
    assert temp_db_path.exists()
    assert temp_db_path.is_file()

    # Connect to the database and check that tables exist
    conn = sqlite3.connect(str(temp_db_path))

    # Enable foreign keys for the testing connection
    conn.execute("PRAGMA foreign_keys = ON")

    cursor = conn.cursor()

    # Check that schema version is set correctly
    cursor.execute("SELECT version FROM schema_version WHERE id = 1")
    version = cursor.fetchone()[0]
    assert version == CURRENT_SCHEMA_VERSION

    # Check that all tables exist
    tables = [
        "schema_version",
        "files",
        "directories",
        "file_types",
        "tabs",
        "indexing_log",
        "permission_bookmarks",
    ]
    for table in tables:
        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
        )
        assert cursor.fetchone() is not None, f"Table {table} does not exist"

    # Check that all indexes exist
    indexes = [
        "idx_files_name",
        "idx_files_ext",
        "idx_files_path",
        "idx_files_parent",
        "idx_files_type",
        "idx_files_cloud",
        "idx_files_indexed",
        "idx_directories_path",
        "idx_file_types_ext",
        "idx_tabs_position",
    ]
    for index in indexes:
        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='index' AND name='{index}'"
        )
        assert cursor.fetchone() is not None, f"Index {index} does not exist"

    # Check that foreign keys are enabled
    cursor.execute("PRAGMA foreign_keys")
    assert cursor.fetchone()[0] == 1

    conn.close()


def test_create_schema_directory_error(temp_db_path: Path) -> None:
    """Test that an error is raised if the directory cannot be created."""
    # Using a file as a directory should fail
    with open(temp_db_path, "w") as f:
        f.write("")

    db_path = temp_db_path / "test.db"
    schema_manager = SchemaManager(db_path)

    with pytest.raises(DatabaseError):
        schema_manager.create_schema()


def test_validate_schema(temp_db_path: Path) -> None:
    """Test that schema validation works correctly."""
    schema_manager = SchemaManager(temp_db_path)

    # Schema doesn't exist yet
    assert not schema_manager.validate_schema()

    # Create schema
    schema_manager.create_schema()

    # Schema should be valid
    assert schema_manager.validate_schema()

    # Corrupt the schema by dropping a table
    conn = sqlite3.connect(str(temp_db_path))
    conn.execute("DROP TABLE files")
    conn.commit()
    conn.close()

    # Schema should be invalid
    assert not schema_manager.validate_schema()


def test_validate_schema_version(temp_db_path: Path) -> None:
    """Test schema validation with different versions."""
    schema_manager = SchemaManager(temp_db_path)
    schema_manager.create_schema()

    # Change the schema version to an incompatible one
    conn = sqlite3.connect(str(temp_db_path))
    conn.execute("UPDATE schema_version SET version = '0.9.0' WHERE id = 1")
    conn.commit()
    conn.close()

    # Schema should be invalid due to version mismatch
    assert not schema_manager.validate_schema()


def test_get_schema_version(temp_db_path: Path) -> None:
    """Test getting the schema version."""
    schema_manager = SchemaManager(temp_db_path)

    # Database doesn't exist yet
    with pytest.raises(DatabaseError):
        schema_manager.get_schema_version()

    # Create schema
    schema_manager.create_schema()

    # Version should be correct
    assert schema_manager.get_schema_version() == CURRENT_SCHEMA_VERSION

    # Change the version
    conn = sqlite3.connect(str(temp_db_path))
    conn.execute("UPDATE schema_version SET version = '2.0.0' WHERE id = 1")
    conn.commit()
    conn.close()

    # Should return the new version
    assert schema_manager.get_schema_version() == "2.0.0"


def test_validate_schema_error(temp_db_path: Path) -> None:
    """Test error handling in validate_schema."""
    schema_manager = SchemaManager(temp_db_path)
    schema_manager.create_schema()

    # Corrupt the database file
    with open(temp_db_path, "w") as f:
        f.write("This is not a valid SQLite database")

    # Should raise a DatabaseError
    with pytest.raises(DatabaseError):
        schema_manager.validate_schema()


def test_check_version_compatibility() -> None:
    """Test version compatibility checking."""
    schema_manager = SchemaManager(Path("dummy.db"))

    # Current version should be compatible
    assert schema_manager._check_version_compatibility(CURRENT_SCHEMA_VERSION)

    # Different version should not be compatible
    assert not schema_manager._check_version_compatibility("0.9.0")
    assert not schema_manager._check_version_compatibility("2.0.0")
