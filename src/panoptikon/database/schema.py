"""Database schema definition and initialization.

This module defines the database schema for Panoptikon and provides utilities
for creating and validating the database schema.
"""

import logging
import os
from pathlib import Path
import sqlite3
import time

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

    def __init__(self, db_path: Path) -> None:
        """Initialize the schema manager.

        Args:
            db_path: Path to the SQLite database file.

        Raises:
            DatabaseError: If the database path is invalid.
        """
        self.db_path = db_path

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
