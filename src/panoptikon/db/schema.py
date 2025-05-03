"""Database schema definition for Panoptikon.

This module defines the SQLAlchemy ORM models for the application.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class File(Base):
    """Represents a file in the file system."""

    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    extension = Column(String, nullable=True, index=True)
    size = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=True)
    modified_at = Column(DateTime, nullable=True)
    indexed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    directory_id = Column(Integer, ForeignKey("directories.id"), nullable=True)
    directory = relationship("Directory", back_populates="files")

    def __init__(
        self,
        path: Path,
        size: Optional[int] = None,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
    ) -> None:
        """Initialize a file record.

        Args:
            path: Path to the file
            size: Size of the file in bytes
            created_at: Creation timestamp
            modified_at: Last modification timestamp
        """
        self.path = str(path.resolve())
        self.name = path.name
        self.extension = path.suffix[1:] if path.suffix else None
        self.size = size
        self.created_at = created_at
        self.modified_at = modified_at

    def __repr__(self) -> str:
        """Return string representation of the file.

        Returns:
            String representation
        """
        return f"<File(path='{self.path}')>"


class Directory(Base):
    """Represents a directory in the file system."""

    __tablename__ = "directories"

    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    indexed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    files = relationship("File", back_populates="directory")
    parent_id = Column(Integer, ForeignKey("directories.id"), nullable=True)
    children = relationship("Directory", backref=ForeignKey("directories.parent_id"))

    def __init__(self, path: Path) -> None:
        """Initialize a directory record.

        Args:
            path: Path to the directory
        """
        self.path = str(path.resolve())
        self.name = path.name

    def __repr__(self) -> str:
        """Return string representation of the directory.

        Returns:
            String representation
        """
        return f"<Directory(path='{self.path}')>"


def init_database(db_path: str) -> None:
    """Initialize the database with the defined schema.

    Args:
        db_path: Path to the database file
    """
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine) 