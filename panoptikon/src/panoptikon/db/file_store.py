"""File storage and retrieval for Panoptikon.

This module handles the storage and retrieval of file information in the database.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import Column, Float, Integer, String, Text, create_engine, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# Create the base class for declarative models
Base = declarative_base()


class FileInfo(Base):
    """SQLAlchemy model for file information.

    Attributes:
        id: Unique identifier for the file record.
        path: Full path to the file.
        name: File name.
        extension: File extension (lowercase).
        size: File size in bytes.
        modified_time: Last modified time (Unix timestamp).
        parent_dir: Parent directory path.
    """

    __tablename__ = "file_info"

    id = Column(Integer, primary_key=True)
    path = Column(String(1024), unique=True, nullable=False, index=True)
    name = Column(String(256), nullable=False, index=True)
    extension = Column(String(32), nullable=True, index=True)
    size = Column(Integer, nullable=False)
    modified_time = Column(Float, nullable=False)
    parent_dir = Column(String(1024), nullable=False, index=True)


# Create a global engine and session factory
_engine = None
_Session = None


def _get_session() -> Session:
    """Get a database session.

    This function initializes the database if needed and returns a session.

    Returns:
        SQLAlchemy session.
    """
    global _engine, _Session
    
    if _engine is None:
        # Initialize the database
        db_path = _get_db_path()
        _engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(_engine)
        _Session = sessionmaker(bind=_engine)
    
    return _Session()


def _get_db_path() -> str:
    """Get the path to the database file.

    Returns:
        Path to the SQLite database file.
    """
    # Determine the database directory based on the platform
    if os.name == "posix":  # macOS, Linux
        db_dir = Path.home() / ".local" / "share" / "panoptikon"
    elif os.name == "nt":  # Windows
        db_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "Panoptikon"
    else:
        db_dir = Path.home() / ".panoptikon"
    
    os.makedirs(db_dir, exist_ok=True)
    return str(db_dir / "panoptikon.db")


def save_file_info(file_info: Dict[str, Any]) -> None:
    """Save file information to the database.

    If the file already exists in the database, it will be updated.

    Args:
        file_info: Dictionary with file information.
    """
    session = _get_session()
    
    try:
        # Check if the file already exists
        existing_file = session.query(FileInfo).filter(FileInfo.path == file_info["path"]).first()
        
        if existing_file:
            # Update the existing record
            for key, value in file_info.items():
                if key != "path":  # Don't update the path (it's the primary key)
                    setattr(existing_file, key, value)
        else:
            # Create a new record
            new_file = FileInfo(**file_info)
            session.add(new_file)
        
        session.commit()
    finally:
        session.close()


def search_files(
    query: str,
    case_sensitive: bool = False,
    extensions: Optional[List[str]] = None,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
    modified_after: Optional[float] = None,
    modified_before: Optional[float] = None,
    paths: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
    limit: int = 1000,
    offset: int = 0
) -> List[Dict[str, Union[str, int, float]]]:
    """Search for files based on the provided criteria.

    Args:
        query: Search query.
        case_sensitive: Whether the search should be case-sensitive.
        extensions: Optional list of file extensions to filter by.
        min_size: Optional minimum file size in bytes.
        max_size: Optional maximum file size in bytes.
        modified_after: Optional Unix timestamp for files modified after this time.
        modified_before: Optional Unix timestamp for files modified before this time.
        paths: Optional list of directory paths to search within.
        exclude_paths: Optional list of directory paths to exclude from search.
        limit: Maximum number of results to return.
        offset: Number of results to skip (for pagination).

    Returns:
        List of file information dictionaries matching the search criteria.
    """
    session = _get_session()
    
    try:
        # Start with a base query
        db_query = session.query(FileInfo)
        
        # Apply search filters
        if query:
            if case_sensitive:
                db_query = db_query.filter(or_(
                    FileInfo.name.contains(query),
                    FileInfo.path.contains(query)
                ))
            else:
                # SQLite's LIKE is case-insensitive by default
                db_query = db_query.filter(or_(
                    FileInfo.name.like(f"%{query}%"),
                    FileInfo.path.like(f"%{query}%")
                ))
        
        # Apply extension filters
        if extensions:
            db_query = db_query.filter(FileInfo.extension.in_([ext.lower() for ext in extensions]))
        
        # Apply size filters
        if min_size is not None:
            db_query = db_query.filter(FileInfo.size >= min_size)
        if max_size is not None:
            db_query = db_query.filter(FileInfo.size <= max_size)
        
        # Apply time filters
        if modified_after is not None:
            db_query = db_query.filter(FileInfo.modified_time >= modified_after)
        if modified_before is not None:
            db_query = db_query.filter(FileInfo.modified_time <= modified_before)
        
        # Apply path filters
        if paths:
            path_conditions = []
            for path in paths:
                path_conditions.append(FileInfo.path.like(f"{path}%"))
            db_query = db_query.filter(or_(*path_conditions))
        
        # Apply path exclusions
        if exclude_paths:
            for path in exclude_paths:
                db_query = db_query.filter(~FileInfo.path.like(f"{path}%"))
        
        # Apply limit and offset
        db_query = db_query.limit(limit).offset(offset)
        
        # Execute the query and convert results to dictionaries
        results = []
        for file_info in db_query.all():
            results.append({
                "id": file_info.id,
                "path": file_info.path,
                "name": file_info.name,
                "extension": file_info.extension,
                "size": file_info.size,
                "modified_time": file_info.modified_time,
                "parent_dir": file_info.parent_dir
            })
        
        return results
    finally:
        session.close() 