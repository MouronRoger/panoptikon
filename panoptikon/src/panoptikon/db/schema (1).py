"""Database schema definition for Panoptikon."""

import datetime
import logging
from typing import Dict, List, Optional, Tuple, Union

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

# Create base class for all models
Base = declarative_base()

# Current schema version
SCHEMA_VERSION = 1


class SchemaVersion(Base):
    """Stores schema version information for migrations."""

    __tablename__ = "schema_version"

    id = sa.Column(sa.Integer, primary_key=True)
    version = sa.Column(sa.Integer, nullable=False)
    applied_at = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    description = sa.Column(sa.String, nullable=True)

    def __repr__(self) -> str:
        """Return string representation of the schema version.

        Returns:
            String representation
        """
        return f"SchemaVersion(version={self.version}, applied_at={self.applied_at})"


class FileRecord(Base):
    """Stores file metadata for indexed files."""

    __tablename__ = "files"

    id = sa.Column(sa.Integer, primary_key=True)
    path = sa.Column(sa.String, nullable=False, unique=True, index=True)
    filename = sa.Column(sa.String, nullable=False, index=True)
    extension = sa.Column(sa.String, nullable=True, index=True)
    size = sa.Column(sa.BigInteger, nullable=False, index=True)
    owner = sa.Column(sa.String, nullable=True, index=True)
    is_hidden = sa.Column(sa.Boolean, nullable=False, default=False, index=True)
    
    # Timestamps
    created_at = sa.Column(sa.DateTime, nullable=False, index=True)
    modified_at = sa.Column(sa.DateTime, nullable=False, index=True)
    accessed_at = sa.Column(sa.DateTime, nullable=True, index=True)
    indexed_at = sa.Column(
        sa.DateTime, 
        nullable=False, 
        default=datetime.datetime.utcnow,
        index=True
    )
    
    # Optional fields
    checksum = sa.Column(sa.String, nullable=True, index=True)  # MD5, SHA-1, etc.
    mime_type = sa.Column(sa.String, nullable=True, index=True)
    
    # Parent directory (extracted from path)
    parent_dir = sa.Column(sa.String, nullable=False, index=True)
    
    # Status flags
    is_indexed = sa.Column(sa.Boolean, nullable=False, default=True, index=True)
    is_deleted = sa.Column(sa.Boolean, nullable=False, default=False, index=True)
    
    def __repr__(self) -> str:
        """Return string representation of the file record.

        Returns:
            String representation
        """
        return f"FileRecord(id={self.id}, path='{self.path}', size={self.size})"


class IndexingTask(Base):
    """Stores information about indexing tasks."""

    __tablename__ = "indexing_tasks"

    id = sa.Column(sa.Integer, primary_key=True)
    root_path = sa.Column(sa.String, nullable=False, index=True)
    started_at = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    completed_at = sa.Column(sa.DateTime, nullable=True)
    is_cancelled = sa.Column(sa.Boolean, nullable=False, default=False)
    files_processed = sa.Column(sa.Integer, nullable=False, default=0)
    errors = sa.Column(sa.Integer, nullable=False, default=0)
    
    def __repr__(self) -> str:
        """Return string representation of the indexing task.

        Returns:
            String representation
        """
        status = "completed" if self.completed_at else "in_progress"
        if self.is_cancelled:
            status = "cancelled"
        
        return (
            f"IndexingTask(id={self.id}, path='{self.root_path}', "
            f"status={status}, files={self.files_processed})"
        )


class SearchQuery(Base):
    """Stores search query history."""

    __tablename__ = "search_queries"

    id = sa.Column(sa.Integer, primary_key=True)
    query_text = sa.Column(sa.String, nullable=False)
    executed_at = sa.Column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow, index=True
    )
    result_count = sa.Column(sa.Integer, nullable=True)
    execution_time_ms = sa.Column(sa.Float, nullable=True)  # execution time in milliseconds
    
    def __repr__(self) -> str:
        """Return string representation of the search query.

        Returns:
            String representation
        """
        return f"SearchQuery(query='{self.query_text}', results={self.result_count})"


class Tag(Base):
    """Defines tags that can be applied to files."""

    __tablename__ = "tags"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False, unique=True)
    color = sa.Column(sa.String, nullable=True)  # Hex color code
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    
    def __repr__(self) -> str:
        """Return string representation of the tag.

        Returns:
            String representation
        """
        return f"Tag(id={self.id}, name='{self.name}')"


class FileTag(Base):
    """Many-to-many relationship between files and tags."""

    __tablename__ = "file_tags"

    id = sa.Column(sa.Integer, primary_key=True)
    file_id = sa.Column(sa.Integer, sa.ForeignKey("files.id"), nullable=False, index=True)
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("tags.id"), nullable=False, index=True)
    applied_at = sa.Column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    
    # Create a unique constraint to prevent duplicate tagging
    __table_args__ = (sa.UniqueConstraint("file_id", "tag_id"),)
    
    def __repr__(self) -> str:
        """Return string representation of the file tag.

        Returns:
            String representation
        """
        return f"FileTag(file_id={self.file_id}, tag_id={self.tag_id})"


# Define database indexes for common query patterns
def create_indexes(engine: sa.engine.Engine) -> None:
    """Create additional indexes that can't be defined in the models.

    Args:
        engine: SQLAlchemy engine to use for creating indexes
    """
    inspector = sa.inspect(engine)
    
    # List of indexes to create beyond those in column definitions
    indexes = [
        # Compound indexes for common query patterns
        sa.Index("idx_files_ext_size", FileRecord.extension, FileRecord.size),
        sa.Index("idx_files_modified_size", FileRecord.modified_at, FileRecord.size),
        sa.Index("idx_files_parent_filename", FileRecord.parent_dir, FileRecord.filename),
        sa.Index(
            "idx_files_ext_parent", 
            FileRecord.extension, 
            FileRecord.parent_dir
        ),
        
        # Full-text search index (SQLite specific)
        # Note: SQLite FTS indexes require special handling
    ]
    
    # Create each index if it doesn't exist
    for index in indexes:
        # Check if index already exists (by name)
        if index.name not in [idx["name"] for idx in inspector.get_indexes(FileRecord.__tablename__)]:
            try:
                index.create(engine)
                logger.info(f"Created index: {index.name}")
            except Exception as e:
                logger.error(f"Failed to create index {index.name}: {e}")


# Define functions to check and update the schema version
def get_schema_version(connection: sa.engine.Connection) -> int:
    """Get the current schema version from the database.

    Args:
        connection: SQLAlchemy connection to use

    Returns:
        Current schema version or 0 if not found
    """
    try:
        result = connection.execute(
            sa.select([SchemaVersion.version])
            .order_by(SchemaVersion.version.desc())
            .limit(1)
        )
        row = result.fetchone()
        return row[0] if row else 0
    except Exception:
        # Table probably doesn't exist yet
        return 0


def update_schema_version(
    connection: sa.engine.Connection,
    version: int,
    description: Optional[str] = None,
) -> None:
    """Update the schema version in the database.

    Args:
        connection: SQLAlchemy connection to use
        version: New schema version to set
        description: Optional description of the schema update
    """
    connection.execute(
        SchemaVersion.__table__.insert().values(
            version=version,
            applied_at=datetime.datetime.utcnow(),
            description=description,
        )
    )


# Create all tables
def create_tables(engine: sa.engine.Engine) -> None:
    """Create all database tables if they don't exist.

    Args:
        engine: SQLAlchemy engine to use for creating tables
    """
    Base.metadata.create_all(engine)
    
    # Create additional indexes
    create_indexes(engine)
    
    # Initialize schema version if needed
    with engine.connect() as connection:
        version = get_schema_version(connection)
        if version == 0:
            update_schema_version(
                connection, SCHEMA_VERSION, "Initial schema creation"
            )
            logger.info(f"Initialized schema version to {SCHEMA_VERSION}")


# Drop all tables (for testing/cleanup)
def drop_tables(engine: sa.engine.Engine) -> None:
    """Drop all database tables.

    Args:
        engine: SQLAlchemy engine to use for dropping tables
    """
    Base.metadata.drop_all(engine)
    logger.info("Dropped all database tables") 