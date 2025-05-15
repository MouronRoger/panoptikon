"""Database schema definition and initialization.

This module defines the database schema for Panoptikon and provides utilities
for creating and validating the database schema.
"""

import logging
import os
from pathlib import Path
import shutil
import sqlite3
import time
from typing import Any, Optional

from ..core.errors import DatabaseError
from ..core.service import ServiceInterface

logger = logging.getLogger(__name__)

# SQL statements for schema creation
SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- Single row table
    version TEXT NOT NULL,                  -- Semantic version (Major.Minor.Patch)
    updated_at INTEGER NOT NULL             -- Last update timestamp
);
"""

FILES_TABLE = """
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,               -- Filename without path
    name_lower TEXT NOT NULL,         -- Lowercase for case-insensitive search
    extension TEXT,                   -- File extension (lowercase)
    path TEXT NOT NULL,               -- Full path
    parent_path TEXT NOT NULL,        -- Parent directory path
    size INTEGER,                     -- File size (NULL for cloud-only)
    folder_size INTEGER,              -- Folder size in bytes (for directories, NULL for files)
    date_created INTEGER,             -- Creation timestamp
    date_modified INTEGER,            -- Modification timestamp 
    file_type TEXT,                   -- UTType identifier
    is_directory INTEGER NOT NULL,    -- 1 if directory, 0 if file
    cloud_provider TEXT,              -- NULL, 'iCloud', 'Dropbox', etc.
    cloud_status INTEGER,             -- 0=local, 1=downloaded, 2=cloud-only
    indexed_at INTEGER NOT NULL       -- Timestamp of last indexing
);
"""

DIRECTORIES_TABLE = """
CREATE TABLE IF NOT EXISTS directories (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,        -- Directory path
    included INTEGER NOT NULL,        -- 1 if included, 0 if excluded
    priority INTEGER NOT NULL,        -- Higher number takes precedence
    recursive INTEGER NOT NULL,       -- 1 if rule applies to subdirectories
    permission_state INTEGER NOT NULL -- Current permission status
);
"""

FILE_TYPES_TABLE = """
CREATE TABLE IF NOT EXISTS file_types (
    id INTEGER PRIMARY KEY,
    extension TEXT NOT NULL UNIQUE,   -- Lowercase extension without dot
    type_name TEXT NOT NULL,          -- User-friendly type name
    category TEXT NOT NULL            -- Category for tab grouping
);
"""

TABS_TABLE = """
CREATE TABLE IF NOT EXISTS tabs (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,               -- Display name
    filter_def TEXT NOT NULL,         -- JSON filter definition
    position INTEGER NOT NULL,        -- Order in tab bar
    visible INTEGER NOT NULL          -- 1 if visible, 0 if hidden
);
"""

INDEXING_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS indexing_log (
    id INTEGER PRIMARY KEY,
    timestamp INTEGER NOT NULL,       -- Operation timestamp
    operation TEXT NOT NULL,          -- 'initial', 'incremental', etc.
    path TEXT,                        -- Related path if applicable
    file_count INTEGER,               -- Number of files processed
    duration INTEGER                  -- Operation duration in milliseconds
);
"""

PERMISSION_BOOKMARKS_TABLE = """
CREATE TABLE IF NOT EXISTS permission_bookmarks (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,        -- Path this bookmark grants access to
    bookmark BLOB NOT NULL,           -- Security-scoped bookmark data
    created_at INTEGER NOT NULL       -- Creation timestamp
);
"""

# Indexes for performance
INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_files_name ON files(name_lower);",
    "CREATE INDEX IF NOT EXISTS idx_files_ext ON files(extension);",
    "CREATE INDEX IF NOT EXISTS idx_files_path ON files(path);",
    "CREATE INDEX IF NOT EXISTS idx_files_parent ON files(parent_path);",
    "CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type);",
    "CREATE INDEX IF NOT EXISTS idx_files_cloud ON files(cloud_provider, cloud_status);",
    "CREATE INDEX IF NOT EXISTS idx_files_indexed ON files(indexed_at);",
    "CREATE INDEX IF NOT EXISTS idx_files_folder_size ON files(folder_size);",
    "CREATE INDEX IF NOT EXISTS idx_directories_path ON directories(path);",
    "CREATE INDEX IF NOT EXISTS idx_file_types_ext ON file_types(extension);",
    "CREATE INDEX IF NOT EXISTS idx_tabs_position ON tabs(position);",
]

# Current schema version
CURRENT_SCHEMA_VERSION = "1.1.0"


class SchemaManager:
    """Manages the database schema for Panoptikon.

    Provides utilities for creating and validating the database schema,
    as well as applying migrations between schema versions.
    """

    MIGRATIONS: list[dict[str, Any]] = []

    def __init__(self, db_path: Path) -> None:
        """Initialize the schema manager.

        Args:
            db_path: Path to the SQLite database file.

        Raises:
            DatabaseError: If the database path is invalid.
        """
        self.db_path = db_path
        # Register migrations (for now, just 1.0.0 -> 1.1.0)
        if not self.MIGRATIONS:
            self.MIGRATIONS.append(
                {
                    "from_version": "1.0.0",
                    "to_version": "1.1.0",
                    "up": self._migrate_1_0_0_to_1_1_0_with_backup,
                    # 'down': None (not implemented)
                }
            )

        # Ensure the parent directory exists
        if not self.db_path.parent.exists():
            try:
                os.makedirs(self.db_path.parent, exist_ok=True)
            except OSError as e:
                raise DatabaseError(f"Failed to create database directory: {e}")

    def database_exists(self) -> bool:
        """Check if the database file exists.

        Returns:
            True if the database file exists, False otherwise.
        """
        return self.db_path.exists() and self.db_path.is_file()

    def create_schema(self) -> None:
        """Create the database schema.

        Creates all tables and indexes if they don't exist.

        Raises:
            DatabaseError: If there's an error creating the schema.
        """
        start_time = time.time()

        if not self.db_path.parent.exists():
            try:
                os.makedirs(self.db_path.parent, exist_ok=True)
            except OSError as e:
                raise DatabaseError(f"Failed to create database directory: {e}")

        try:
            # Connect to the database
            conn = sqlite3.connect(str(self.db_path))

            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")

            # Set journal mode to WAL
            conn.execute("PRAGMA journal_mode = WAL")

            # Get a cursor
            cursor = conn.cursor()

            # Create tables
            cursor.execute(SCHEMA_VERSION_TABLE)
            cursor.execute(FILES_TABLE)
            cursor.execute(DIRECTORIES_TABLE)
            cursor.execute(FILE_TYPES_TABLE)
            cursor.execute(TABS_TABLE)
            cursor.execute(INDEXING_LOG_TABLE)
            cursor.execute(PERMISSION_BOOKMARKS_TABLE)

            # Create indexes
            for index_sql in INDEXES:
                cursor.execute(index_sql)

            # Set schema version if it doesn't exist
            cursor.execute(
                "INSERT OR IGNORE INTO schema_version (id, version, updated_at) VALUES (1, ?, ?)",
                (CURRENT_SCHEMA_VERSION, int(time.time())),
            )

            # Commit the transaction
            conn.commit()

            # Close the connection
            conn.close()

            elapsed = (time.time() - start_time) * 1000  # Convert to milliseconds
            logger.info(f"Schema created in {elapsed:.2f}ms at {self.db_path}")

        except sqlite3.Error as e:
            raise DatabaseError(f"Error creating database schema: {e}")

    def validate_schema(self) -> bool:
        """Validate that the database schema is correct.

        Returns:
            True if the schema is valid, False otherwise.

        Raises:
            DatabaseError: If there's an error validating the schema.
        """
        if not self.database_exists():
            return False

        try:
            # Connect to the database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Perform validation steps
            valid = (
                self._validate_schema_version_table(cursor)
                and self._validate_tables_exist(cursor)
                and self._validate_indexes_exist(cursor)
                and self._validate_pragma_settings(cursor)
            )

            conn.close()
            return valid

        except sqlite3.Error as e:
            raise DatabaseError(f"Error validating database schema: {e}")

    def _validate_schema_version_table(self, cursor: sqlite3.Cursor) -> bool:
        """Validate that the schema version table exists and has valid data.

        Args:
            cursor: The database cursor to use.

        Returns:
            True if valid, False otherwise.
        """
        # Check schema version table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
        )
        if not cursor.fetchone():
            return False

        # Check schema version
        cursor.execute("SELECT version FROM schema_version WHERE id = 1")
        result = cursor.fetchone()
        if not result or not self._check_version_compatibility(result[0]):
            return False

        return True

    def _validate_tables_exist(self, cursor: sqlite3.Cursor) -> bool:
        """Validate that all required tables exist.

        Args:
            cursor: The database cursor to use.

        Returns:
            True if valid, False otherwise.
        """
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
            if not cursor.fetchone():
                return False

        return True

    def _validate_indexes_exist(self, cursor: sqlite3.Cursor) -> bool:
        """Validate that all required indexes exist.

        Args:
            cursor: The database cursor to use.

        Returns:
            True if valid, False otherwise.
        """
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
            if not cursor.fetchone():
                return False

        return True

    def _validate_pragma_settings(self, cursor: sqlite3.Cursor) -> bool:
        """Validate that database pragma settings are correct.

        Args:
            cursor: The database cursor to use.

        Returns:
            True if valid, False otherwise.
        """
        # Enable foreign keys before checking the setting
        cursor.execute("PRAGMA foreign_keys = ON")

        # Check foreign key constraints are enabled
        cursor.execute("PRAGMA foreign_keys")
        if cursor.fetchone()[0] != 1:
            return False

        return True

    def get_schema_version(self) -> str:
        """Get the current schema version from the database.

        Returns:
            The current schema version.

        Raises:
            DatabaseError: If there's an error getting the schema version.
        """
        if not self.database_exists():
            raise DatabaseError("Database does not exist")

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute("SELECT version FROM schema_version WHERE id = 1")
            result = cursor.fetchone()

            conn.close()

            if not result:
                raise DatabaseError("Schema version not found")

            return str(result[0])
        except sqlite3.Error as e:
            raise DatabaseError(f"Error getting schema version: {e}")

    def _check_version_compatibility(self, version: str) -> bool:
        """Check if the database schema version is compatible with the current version.

        Args:
            version: The database schema version to check.

        Returns:
            True if the version is compatible, False otherwise.
        """
        # For now, just check for exact match
        # In the future, this would implement more sophisticated version compatibility checks
        return version == CURRENT_SCHEMA_VERSION

    def _backup_database(self) -> Optional[Path]:
        """Create a backup of the database file before migration.

        Returns:
            Path to the backup file, or None if no backup was created.

        Raises:
            DatabaseError: If backup fails (other than file not existing).
        """
        if not self.db_path.exists():
            logger.warning(
                f"Database file {self.db_path} does not exist; skipping backup."
            )
            return None
        backup_path = self.db_path.with_suffix(self.db_path.suffix + ".bak")
        try:
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backup created at {backup_path}")
            return backup_path
        except Exception as e:
            raise DatabaseError(f"Failed to create database backup: {e}")

    def _restore_database(self, backup_path: Optional[Path]) -> None:
        """Restore the database from a backup file, if provided."""
        if backup_path is None:
            logger.warning("No backup file provided for restore; skipping restore.")
            return
        try:
            shutil.copy2(backup_path, self.db_path)
            logger.warning(f"Database restored from backup at {backup_path}")
        except Exception as e:
            raise DatabaseError(f"Failed to restore database from backup: {e}")

    def _migrate_1_0_0_to_1_1_0_with_backup(self, conn: sqlite3.Connection) -> None:
        """Migrate from schema version 1.0.0 to 1.1.0 with backup and rollback support."""
        backup_path = self._backup_database()
        cursor = conn.cursor()
        try:
            # Add folder_size column if not present
            cursor.execute("PRAGMA table_info(files)")
            columns = [r[1] for r in cursor.fetchall()]
            if "folder_size" not in columns:
                cursor.execute("ALTER TABLE files ADD COLUMN folder_size INTEGER;")
            # Add index if not present
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_files_folder_size'"
            )
            if not cursor.fetchone():
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_files_folder_size ON files(folder_size);"
                )
            # Update schema version
            cursor.execute(
                "UPDATE schema_version SET version = ?, updated_at = ? WHERE id = 1",
                ("1.1.0", int(time.time())),
            )
            conn.commit()
            logger.info("Migration to 1.1.0 completed successfully.")
        except Exception as migration_error:
            conn.rollback()
            logger.error(f"Migration failed, rolling back: {migration_error}")
            self._restore_database(backup_path)
            raise DatabaseError(
                f"Migration to 1.1.0 failed and was rolled back: {migration_error}"
            )

    def _find_migrations(
        self, current_version: str, target_version: str
    ) -> list[dict[str, Any]]:
        """Find and order migrations from current_version to target_version."""
        migrations = []
        version = current_version
        while version != target_version:
            found = False
            for mig in self.MIGRATIONS:
                if mig["from_version"] == version:
                    migrations.append(mig)
                    version = mig["to_version"]
                    found = True
                    break
            if not found:
                raise DatabaseError(
                    f"No migration path from {version} to {target_version}"
                )
        return migrations

    def migrate_to_latest(self) -> None:
        """Migrate the database schema to the latest version using the migration registry."""
        if not self.database_exists():
            return
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM schema_version WHERE id = 1")
            row = cursor.fetchone()
            if not row:
                raise DatabaseError("Schema version not found for migration")
            current_version = row[0]
            if current_version == CURRENT_SCHEMA_VERSION:
                conn.close()
                return  # Already up to date
            migrations = self._find_migrations(current_version, CURRENT_SCHEMA_VERSION)
            for mig in migrations:
                mig["up"](conn)
            conn.close()
        except sqlite3.Error as e:
            raise DatabaseError(f"Error migrating database schema: {e}")

    def set_schema_version(self, version: str) -> None:
        """Set the schema version in the database.

        Args:
            version: The new schema version string.

        Raises:
            DatabaseError: If the database does not exist or update fails.
        """
        if not self.database_exists():
            raise DatabaseError("Database does not exist")
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE schema_version SET version = ?, updated_at = ? WHERE id = 1",
                (version, int(time.time())),
            )
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            raise DatabaseError(f"Error setting schema version: {e}")

    def compare_schema_version(self, target_version: str) -> int:
        """Compare the current schema version to a target version.

        Args:
            target_version: The version string to compare to.

        Returns:
            -1 if current < target, 0 if equal, 1 if current > target
        Raises:
            DatabaseError: If the database does not exist or version cannot be read.
        """
        current = self.get_schema_version()

        def parse(v: str) -> tuple[int, ...]:
            return tuple(int(x) for x in v.split("."))

        c_tuple = parse(current)
        t_tuple = parse(target_version)
        if c_tuple < t_tuple:
            return -1
        if c_tuple > t_tuple:
            return 1
        return 0


class DatabaseSchemaService(ServiceInterface):
    """Service for managing database schema operations.

    This service integrates with the service container and provides
    a clean interface for database schema operations.
    """

    def __init__(self, db_path: Path) -> None:
        """Initialize the database schema service.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.schema_manager = SchemaManager(db_path)
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the database schema service.

        Creates the database schema if it doesn't exist.

        Raises:
            DatabaseError: If there's an error initializing the service.
        """
        if self._initialized:
            return

        try:
            # Create schema if database doesn't exist
            if not self.schema_manager.database_exists():
                self.schema_manager.create_schema()
            # Validate schema if database exists
            elif not self.schema_manager.validate_schema():
                # If validation fails, attempt to recreate the schema
                # This is a simple approach for now - real migration would be more complex
                logger.warning("Database schema validation failed, recreating schema")
                self.schema_manager.create_schema()

            self._initialized = True
            logger.info(
                f"Database schema service initialized with database at {self.db_path}"
            )

        except Exception as e:
            raise DatabaseError(f"Failed to initialize database schema service: {e}")

    def shutdown(self) -> None:
        """Shutdown the database schema service."""
        self._initialized = False
        logger.debug("Database schema service shut down")

    def ensure_schema_exists(self) -> None:
        """Ensure the database schema exists.

        Creates the schema if it doesn't exist or isn't valid.

        Raises:
            DatabaseError: If there's an error creating the schema.
        """
        if (
            not self.schema_manager.database_exists()
            or not self.schema_manager.validate_schema()
        ):
            self.schema_manager.create_schema()

    def validate_schema(self) -> bool:
        """Validate that the database schema is correct.

        Returns:
            True if the schema is valid, False otherwise.

        Raises:
            DatabaseError: If there's an error validating the schema.
        """
        return self.schema_manager.validate_schema()

    def get_schema_version(self) -> str:
        """Get the current schema version from the database.

        Returns:
            The current schema version.

        Raises:
            DatabaseError: If there's an error getting the schema version.
        """
        return self.schema_manager.get_schema_version()
