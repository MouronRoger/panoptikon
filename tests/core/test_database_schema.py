"""Tests for the database schema implementation."""

from collections.abc import Generator
from pathlib import Path
import sqlite3
import tempfile
import time

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
        "idx_files_folder_size",
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

    # Check that the files table has the folder_size column
    cursor.execute("PRAGMA table_info(files)")
    columns = [row[1] for row in cursor.fetchall()]
    assert "folder_size" in columns, "folder_size column missing in files table"

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


def test_migrate_to_latest_adds_folder_size(temp_db_path: Path) -> None:
    """Test that migrate_to_latest upgrades a 1.0.0 database to 1.1.0 and adds folder_size column and index."""
    schema_manager = SchemaManager(temp_db_path)
    # Create schema as 1.0.0 (simulate old schema)
    conn = sqlite3.connect(str(temp_db_path))
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE files (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            name_lower TEXT NOT NULL,
            extension TEXT,
            path TEXT NOT NULL,
            parent_path TEXT NOT NULL,
            size INTEGER,
            date_created INTEGER,
            date_modified INTEGER,
            file_type TEXT,
            is_directory INTEGER NOT NULL,
            cloud_provider TEXT,
            cloud_status INTEGER,
            indexed_at INTEGER NOT NULL
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE schema_version (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version TEXT NOT NULL,
            updated_at INTEGER NOT NULL
        );
        """
    )
    cursor.execute(
        "INSERT INTO schema_version (id, version, updated_at) VALUES (1, '1.0.0', 0);"
    )
    conn.commit()
    conn.close()
    # Run migration
    schema_manager.migrate_to_latest()
    # Check schema version
    conn = sqlite3.connect(str(temp_db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM schema_version WHERE id = 1")
    version = cursor.fetchone()[0]
    assert version == "1.1.0"
    # Check folder_size column
    cursor.execute("PRAGMA table_info(files)")
    columns = [row[1] for row in cursor.fetchall()]
    assert "folder_size" in columns
    # Check index
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_files_folder_size'"
    )
    assert cursor.fetchone() is not None
    conn.close()


def test_migrate_to_latest_idempotent(temp_db_path: Path) -> None:
    """Test that running migrate_to_latest twice is safe (idempotent)."""
    schema_manager = SchemaManager(temp_db_path)
    # Create schema as 1.0.0
    conn = sqlite3.connect(str(temp_db_path))
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE files (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            name_lower TEXT NOT NULL,
            extension TEXT,
            path TEXT NOT NULL,
            parent_path TEXT NOT NULL,
            size INTEGER,
            date_created INTEGER,
            date_modified INTEGER,
            file_type TEXT,
            is_directory INTEGER NOT NULL,
            cloud_provider TEXT,
            cloud_status INTEGER,
            indexed_at INTEGER NOT NULL
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE schema_version (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version TEXT NOT NULL,
            updated_at INTEGER NOT NULL
        );
        """
    )
    cursor.execute(
        "INSERT INTO schema_version (id, version, updated_at) VALUES (1, '1.0.0', 0);"
    )
    conn.commit()
    conn.close()
    # Run migration twice
    schema_manager.migrate_to_latest()
    schema_manager.migrate_to_latest()
    # Check schema version and column
    conn = sqlite3.connect(str(temp_db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM schema_version WHERE id = 1")
    version = cursor.fetchone()[0]
    assert version == "1.1.0"
    cursor.execute("PRAGMA table_info(files)")
    columns = [row[1] for row in cursor.fetchall()]
    assert "folder_size" in columns
    conn.close()


def test_migrate_to_latest_noop_on_1_1_0(temp_db_path: Path) -> None:
    """Test that migrate_to_latest does nothing if already at 1.1.0."""
    schema_manager = SchemaManager(temp_db_path)
    schema_manager.create_schema()
    # Should not raise or change anything
    schema_manager.migrate_to_latest()
    # Check schema version
    conn = sqlite3.connect(str(temp_db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM schema_version WHERE id = 1")
    version = cursor.fetchone()[0]
    assert version == "1.1.0"
    conn.close()


def test_set_and_get_schema_version(temp_db_path: Path) -> None:
    """Test setting and getting the schema version."""
    schema_manager = SchemaManager(temp_db_path)
    schema_manager.create_schema()
    schema_manager.set_schema_version("2.3.4")
    assert schema_manager.get_schema_version() == "2.3.4"


def test_compare_schema_version(temp_db_path: Path) -> None:
    """Test compare_schema_version for less than, equal, and greater than cases."""
    schema_manager = SchemaManager(temp_db_path)
    schema_manager.create_schema()
    schema_manager.set_schema_version("1.2.3")
    assert schema_manager.compare_schema_version("1.2.4") == -1
    assert schema_manager.compare_schema_version("1.2.3") == 0
    assert schema_manager.compare_schema_version("1.2.2") == 1


def test_find_migrations_sequential(temp_db_path: Path) -> None:
    """Test that the registry returns the correct sequence for 1.0.0 to 1.1.0."""
    schema_manager = SchemaManager(temp_db_path)
    migrations = schema_manager._find_migrations("1.0.0", "1.1.0")
    assert len(migrations) == 1
    assert migrations[0]["from_version"] == "1.0.0"
    assert migrations[0]["to_version"] == "1.1.0"


def test_find_migrations_no_path(temp_db_path: Path) -> None:
    """Test that an error is raised if no migration path exists."""
    schema_manager = SchemaManager(temp_db_path)
    with pytest.raises(DatabaseError, match="No migration path"):
        schema_manager._find_migrations("1.1.0", "2.0.0")


def test_registry_extensible(temp_db_path: Path) -> None:
    """Simulate adding a second migration and test correct ordering."""
    SchemaManager.MIGRATIONS = []  # Reset registry for test isolation
    schema_manager = SchemaManager(temp_db_path)
    # Re-add default migration
    SchemaManager.MIGRATIONS.append(
        {
            "from_version": "1.0.0",
            "to_version": "1.1.0",
            "up": schema_manager._migrate_1_0_0_to_1_1_0_with_backup,
        }
    )

    # Add a fake migration 1.1.0 -> 1.2.0
    def fake_migration(conn):
        pass

    schema_manager.MIGRATIONS.append(
        {
            "from_version": "1.1.0",
            "to_version": "1.2.0",
            "up": fake_migration,
        }
    )
    migrations = schema_manager._find_migrations("1.0.0", "1.2.0")
    assert len(migrations) == 2
    assert migrations[0]["from_version"] == "1.0.0"
    assert migrations[1]["from_version"] == "1.1.0"


def test_backup_database_creates_file(tmp_path: Path) -> None:
    """Test that _backup_database creates a backup file when the DB exists."""
    db_path = tmp_path / "test.db"
    db_path.write_bytes(b"testdata")
    schema_manager = SchemaManager(db_path)
    backup_path = schema_manager._backup_database()
    assert backup_path is not None
    assert backup_path.exists()
    assert backup_path.read_bytes() == b"testdata"


def test_backup_database_skips_if_missing(tmp_path: Path, caplog) -> None:
    """Test that _backup_database returns None and logs a warning if the DB does not exist."""
    db_path = tmp_path / "missing.db"
    schema_manager = SchemaManager(db_path)
    with caplog.at_level("WARNING"):
        backup_path = schema_manager._backup_database()
    assert backup_path is None
    assert any("skipping backup" in m for m in caplog.messages)


def test_restore_database_restores_file(tmp_path: Path) -> None:
    """Test that _restore_database restores the DB from backup."""
    db_path = tmp_path / "test.db"
    backup_path = tmp_path / "test.db.bak"
    db_path.write_bytes(b"original")
    backup_path.write_bytes(b"backupdata")
    schema_manager = SchemaManager(db_path)
    schema_manager._restore_database(backup_path)
    assert db_path.read_bytes() == b"backupdata"


def test_migration_executor_success(tmp_path: Path) -> None:
    """Test that a successful migration is committed and version is updated."""
    SchemaManager.MIGRATIONS = []  # Reset registry for test isolation
    db_path = tmp_path / "test.db"
    schema_manager = SchemaManager(db_path)
    schema_manager.create_schema()
    # Re-add default migration
    SchemaManager.MIGRATIONS.append(
        {
            "from_version": "1.0.0",
            "to_version": "1.1.0",
            "up": schema_manager._migrate_1_0_0_to_1_1_0_with_backup,
        }
    )

    # Add a fake migration 1.1.0 -> 1.2.0
    def add_table(conn):
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test_atomic (id INTEGER PRIMARY KEY)")
        cursor.execute(
            "UPDATE schema_version SET version = ?, updated_at = ? WHERE id = 1",
            ("1.2.0", int(time.time())),
        )
        conn.commit()

    schema_manager.MIGRATIONS.append(
        {
            "from_version": "1.1.0",
            "to_version": "1.2.0",
            "up": add_table,
        }
    )
    schema_manager.set_schema_version("1.1.0")
    schema_manager.migrate_to_latest()
    # Check that the table exists and version is updated
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM schema_version WHERE id = 1")
    assert cursor.fetchone()[0] == "1.2.0"
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='test_atomic'"
    )
    assert cursor.fetchone() is not None
    conn.close()


def test_migration_executor_failure_and_rollback(tmp_path: Path) -> None:
    """Test that a migration failure rolls back and restores from backup."""
    SchemaManager.MIGRATIONS = []  # Reset registry for test isolation
    db_path = tmp_path / "test.db"
    schema_manager = SchemaManager(db_path)
    schema_manager.create_schema()
    # Re-add default migration
    SchemaManager.MIGRATIONS.append(
        {
            "from_version": "1.0.0",
            "to_version": "1.1.0",
            "up": schema_manager._migrate_1_0_0_to_1_1_0_with_backup,
        }
    )

    # Add a fake migration 1.2.0 -> 1.3.0 that fails
    def fail_migration(conn):
        raise RuntimeError("Simulated migration failure")

    schema_manager.MIGRATIONS.append(
        {
            "from_version": "1.2.0",
            "to_version": "1.3.0",
            "up": fail_migration,
        }
    )
    schema_manager.set_schema_version("1.2.0")
    # Write a marker to the DB file to check for restore
    db_path.write_bytes(b"originaldb")
    try:
        schema_manager.migrate_to_latest()
    except Exception as e:
        assert "Simulated migration failure" in str(e)
    # The DB file should be restored to the original marker
    assert db_path.read_bytes() == b"originaldb"
    # Version should not be updated
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM schema_version WHERE id = 1")
    assert cursor.fetchone()[0] == "1.2.0"
    conn.close()
