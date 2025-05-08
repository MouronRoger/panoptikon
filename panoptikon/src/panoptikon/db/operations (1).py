"""Database operations for managing file metadata in Panoptikon."""

import datetime
import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Set, Tuple, Union

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from panoptikon.db.schema import FileRecord, IndexingTask, SearchQuery, Tag, FileTag
from panoptikon.index.metadata import FileMetadata

logger = logging.getLogger(__name__)


class DatabaseOperations:
    """Provides CRUD operations for file metadata in the database."""

    def __init__(self, engine: sa.engine.Engine):
        """Initialize with a database engine.

        Args:
            engine: SQLAlchemy engine connected to the database
        """
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        """Provide a transactional scope around a series of operations.

        This context manager handles the session lifecycle, including
        commit/rollback and session closing.

        Yields:
            SQLAlchemy session
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database operation error: {e}")
            raise
        finally:
            session.close()

    def add_file(self, file_metadata: FileMetadata) -> Optional[int]:
        """Add a single file record to the database.

        Args:
            file_metadata: File metadata to store

        Returns:
            ID of the created record or None if failed
        """
        try:
            with self.session_scope() as session:
                # Check if file already exists
                existing = session.query(FileRecord).filter(
                    FileRecord.path == file_metadata.path
                ).first()

                if existing:
                    # Update existing record
                    return self._update_file_record(session, existing, file_metadata)
                else:
                    # Create new record
                    return self._create_file_record(session, file_metadata)
        except Exception as e:
            logger.error(f"Error adding file record: {e}")
            return None

    def _create_file_record(
        self, session: Session, file_metadata: FileMetadata
    ) -> int:
        """Create a new file record in the database.

        Args:
            session: SQLAlchemy session
            file_metadata: File metadata to store

        Returns:
            ID of the created record
        """
        parent_dir = str(Path(file_metadata.path).parent)

        file_record = FileRecord(
            path=file_metadata.path,
            filename=file_metadata.filename,
            extension=file_metadata.extension,
            size=file_metadata.size,
            owner=file_metadata.owner,
            is_hidden=file_metadata.is_hidden,
            created_at=file_metadata.created_at,
            modified_at=file_metadata.modified_at,
            accessed_at=file_metadata.accessed_at,
            indexed_at=datetime.datetime.utcnow(),
            checksum=file_metadata.checksum,
            mime_type=file_metadata.mime_type,
            parent_dir=parent_dir,
            is_indexed=True,
            is_deleted=False,
        )

        session.add(file_record)
        session.flush()  # Flush to get the ID
        return file_record.id

    def _update_file_record(
        self, session: Session, existing_record: FileRecord, file_metadata: FileMetadata
    ) -> int:
        """Update an existing file record in the database.

        Args:
            session: SQLAlchemy session
            existing_record: Existing record to update
            file_metadata: New file metadata

        Returns:
            ID of the updated record
        """
        # Update fields that may have changed
        existing_record.size = file_metadata.size
        existing_record.owner = file_metadata.owner
        existing_record.is_hidden = file_metadata.is_hidden
        existing_record.modified_at = file_metadata.modified_at
        existing_record.accessed_at = file_metadata.accessed_at
        existing_record.indexed_at = datetime.datetime.utcnow()
        existing_record.checksum = file_metadata.checksum
        existing_record.mime_type = file_metadata.mime_type
        existing_record.is_deleted = False  # Mark as not deleted if it was

        return existing_record.id

    def add_files_batch(
        self, file_metadata_list: List[FileMetadata], batch_size: int = 100
    ) -> Dict[str, int]:
        """Add multiple file records in an efficient batch operation.

        Args:
            file_metadata_list: List of file metadata to store
            batch_size: Number of records to process in each batch

        Returns:
            Dictionary mapping file paths to record IDs or error counts
        """
        results = {
            "total": len(file_metadata_list),
            "inserted": 0,
            "updated": 0,
            "failed": 0,
        }

        # Process in batches for better performance
        for i in range(0, len(file_metadata_list), batch_size):
            batch = file_metadata_list[i : i + batch_size]
            
            try:
                with self.session_scope() as session:
                    # Get all existing paths in this batch
                    paths = [m.path for m in batch]
                    existing_records = {
                        r.path: r
                        for r in session.query(FileRecord).filter(
                            FileRecord.path.in_(paths)
                        ).all()
                    }
                    
                    # Process each file in the batch
                    for metadata in batch:
                        try:
                            if metadata.path in existing_records:
                                # Update existing record
                                self._update_file_record(
                                    session, 
                                    existing_records[metadata.path], 
                                    metadata
                                )
                                results["updated"] += 1
                            else:
                                # Create new record
                                self._create_file_record(session, metadata)
                                results["inserted"] += 1
                        except Exception as e:
                            logger.error(
                                f"Error processing file {metadata.path}: {e}"
                            )
                            results["failed"] += 1
            except Exception as e:
                logger.error(f"Error in batch operation: {e}")
                # Mark all files in this batch as failed
                results["failed"] += len(batch)

        return results

    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """Delete a file record from the database.

        Args:
            file_path: Path of the file to delete

        Returns:
            True if successful, False otherwise
        """
        path_str = str(file_path)
        
        try:
            with self.session_scope() as session:
                record = session.query(FileRecord).filter(
                    FileRecord.path == path_str
                ).first()
                
                if record:
                    # Soft delete
                    record.is_deleted = True
                    record.indexed_at = datetime.datetime.utcnow()
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting file record: {e}")
            return False

    def hard_delete_file(self, file_path: Union[str, Path]) -> bool:
        """Permanently delete a file record from the database.

        Args:
            file_path: Path of the file to delete

        Returns:
            True if successful, False otherwise
        """
        path_str = str(file_path)
        
        try:
            with self.session_scope() as session:
                # Delete related file tags first
                file_record = session.query(FileRecord).filter(
                    FileRecord.path == path_str
                ).first()
                
                if file_record:
                    # Delete tags associated with this file
                    session.query(FileTag).filter(
                        FileTag.file_id == file_record.id
                    ).delete()
                    
                    # Delete the file record
                    session.delete(file_record)
                    return True
                return False
        except Exception as e:
            logger.error(f"Error hard-deleting file record: {e}")
            return False

    def get_file(self, file_path: Union[str, Path]) -> Optional[Dict]:
        """Get a single file record by path.

        Args:
            file_path: Path of the file to retrieve

        Returns:
            File record as a dictionary or None if not found
        """
        path_str = str(file_path)
        
        try:
            with self.session_scope() as session:
                record = session.query(FileRecord).filter(
                    FileRecord.path == path_str
                ).first()
                
                if record:
                    return self._record_to_dict(record)
                return None
        except Exception as e:
            logger.error(f"Error retrieving file record: {e}")
            return None

    def get_files_by_path_prefix(
        self, path_prefix: str, limit: int = 1000, include_deleted: bool = False
    ) -> List[Dict]:
        """Get file records with paths starting with the given prefix.

        Args:
            path_prefix: Path prefix to match
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted records

        Returns:
            List of file records as dictionaries
        """
        try:
            with self.session_scope() as session:
                query = session.query(FileRecord).filter(
                    FileRecord.path.like(f"{path_prefix}%")
                )
                
                if not include_deleted:
                    query = query.filter(FileRecord.is_deleted == False)
                
                records = query.limit(limit).all()
                return [self._record_to_dict(r) for r in records]
        except Exception as e:
            logger.error(f"Error retrieving files by path prefix: {e}")
            return []

    def get_files_by_extension(
        self, extension: str, limit: int = 1000, include_deleted: bool = False
    ) -> List[Dict]:
        """Get file records with the given extension.

        Args:
            extension: File extension to match (with or without leading dot)
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted records

        Returns:
            List of file records as dictionaries
        """
        # Normalize extension to always start with a dot
        if extension and not extension.startswith("."):
            extension = f".{extension}"
            
        try:
            with self.session_scope() as session:
                query = session.query(FileRecord).filter(
                    FileRecord.extension == extension
                )
                
                if not include_deleted:
                    query = query.filter(FileRecord.is_deleted == False)
                
                records = query.limit(limit).all()
                return [self._record_to_dict(r) for r in records]
        except Exception as e:
            logger.error(f"Error retrieving files by extension: {e}")
            return []

    def search_files(
        self, 
        search_term: str, 
        extensions: Optional[List[str]] = None,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        modified_after: Optional[datetime.datetime] = None,
        modified_before: Optional[datetime.datetime] = None,
        paths: Optional[List[str]] = None,
        limit: int = 1000,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> Tuple[List[Dict], int]:
        """Search for files based on various criteria.

        Args:
            search_term: Text to search in filename and path
            extensions: List of file extensions to include
            min_size: Minimum file size in bytes
            max_size: Maximum file size in bytes
            modified_after: Only include files modified after this time
            modified_before: Only include files modified before this time
            paths: Only include files in these paths
            limit: Maximum number of records to return
            offset: Number of records to skip
            include_deleted: Whether to include soft-deleted records

        Returns:
            Tuple of (list of file records as dictionaries, total count)
        """
        try:
            with self.session_scope() as session:
                # Base query
                query = session.query(FileRecord)
                
                # Apply search criteria
                if search_term:
                    # Convert terms to lowercase for case-insensitive search
                    search_term = f"%{search_term.lower()}%"
                    query = query.filter(
                        sa.or_(
                            sa.func.lower(FileRecord.filename).like(search_term),
                            sa.func.lower(FileRecord.path).like(search_term),
                        )
                    )
                
                # Apply filters
                if extensions:
                    # Normalize extensions
                    normalized_extensions = []
                    for ext in extensions:
                        if ext and not ext.startswith("."):
                            normalized_extensions.append(f".{ext}")
                        else:
                            normalized_extensions.append(ext)
                    
                    query = query.filter(FileRecord.extension.in_(normalized_extensions))
                
                if min_size is not None:
                    query = query.filter(FileRecord.size >= min_size)
                
                if max_size is not None:
                    query = query.filter(FileRecord.size <= max_size)
                
                if modified_after is not None:
                    query = query.filter(FileRecord.modified_at >= modified_after)
                
                if modified_before is not None:
                    query = query.filter(FileRecord.modified_at <= modified_before)
                
                if paths:
                    path_conditions = []
                    for path in paths:
                        path_conditions.append(FileRecord.path.like(f"{path}%"))
                    
                    if path_conditions:
                        query = query.filter(sa.or_(*path_conditions))
                
                if not include_deleted:
                    query = query.filter(FileRecord.is_deleted == False)
                
                # Get total count for pagination
                total_count = query.count()
                
                # Apply pagination
                query = query.order_by(FileRecord.path).limit(limit).offset(offset)
                
                # Execute query
                records = query.all()
                
                # Log this search
                self._log_search(
                    session,
                    search_term.replace("%", "") if search_term else "",
                    len(records),
                    total_count
                )
                
                return [self._record_to_dict(r) for r in records], total_count
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return [], 0

    def _log_search(
        self, 
        session: Session, 
        query_text: str, 
        result_count: int,
        total_count: int,
    ) -> None:
        """Log a search query for history tracking.

        Args:
            session: SQLAlchemy session
            query_text: The search query text
            result_count: Number of results returned
            total_count: Total number of matching results
        """
        try:
            search_query = SearchQuery(
                query_text=query_text,
                executed_at=datetime.datetime.utcnow(),
                result_count=total_count,
            )
            session.add(search_query)
        except Exception as e:
            logger.error(f"Error logging search query: {e}")

    def _record_to_dict(self, record: FileRecord) -> Dict:
        """Convert a FileRecord object to a dictionary.

        Args:
            record: FileRecord to convert

        Returns:
            Dictionary representation of the record
        """
        return {
            "id": record.id,
            "path": record.path,
            "filename": record.filename,
            "extension": record.extension,
            "size": record.size,
            "owner": record.owner,
            "is_hidden": record.is_hidden,
            "created_at": record.created_at,
            "modified_at": record.modified_at,
            "accessed_at": record.accessed_at,
            "indexed_at": record.indexed_at,
            "checksum": record.checksum,
            "mime_type": record.mime_type,
            "parent_dir": record.parent_dir,
            "is_deleted": record.is_deleted
        }

    def record_indexing_task(self, root_path: Union[str, Path]) -> int:
        """Create a record for a new indexing task.

        Args:
            root_path: Root path being indexed

        Returns:
            ID of the created task record
        """
        path_str = str(root_path)
        
        try:
            with self.session_scope() as session:
                task = IndexingTask(
                    root_path=path_str,
                    started_at=datetime.datetime.utcnow(),
                    files_processed=0,
                    errors=0,
                )
                session.add(task)
                session.flush()
                return task.id
        except Exception as e:
            logger.error(f"Error recording indexing task: {e}")
            return -1

    def update_indexing_task(
        self, task_id: int, files_processed: int, errors: int, completed: bool = False
    ) -> bool:
        """Update an indexing task with progress information.

        Args:
            task_id: ID of the task to update
            files_processed: Number of files processed
            errors: Number of errors encountered
            completed: Whether the task is completed

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.session_scope() as session:
                task = session.query(IndexingTask).get(task_id)
                
                if task:
                    task.files_processed = files_processed
                    task.errors = errors
                    
                    if completed:
                        task.completed_at = datetime.datetime.utcnow()
                    
                    return True
                return False
        except Exception as e:
            logger.error(f"Error updating indexing task: {e}")
            return False

    def cancel_indexing_task(self, task_id: int) -> bool:
        """Mark an indexing task as cancelled.

        Args:
            task_id: ID of the task to cancel

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.session_scope() as session:
                task = session.query(IndexingTask).get(task_id)
                
                if task:
                    task.is_cancelled = True
                    task.completed_at = datetime.datetime.utcnow()
                    return True
                return False
        except Exception as e:
            logger.error(f"Error cancelling indexing task: {e}")
            return False

    def clean_database(
        self, 
        max_search_history: int = 1000, 
        remove_deleted: bool = True
    ) -> Dict[str, int]:
        """Perform database cleanup operations.

        Args:
            max_search_history: Maximum number of search history entries to keep
            remove_deleted: Whether to permanently remove soft-deleted records

        Returns:
            Dictionary with counts of affected records
        """
        results = {
            "search_history_removed": 0,
            "deleted_files_removed": 0,
        }
        
        try:
            with self.session_scope() as session:
                # Clean up search history
                if max_search_history > 0:
                    # Get IDs to keep
                    query = session.query(SearchQuery.id).order_by(
                        SearchQuery.executed_at.desc()
                    ).limit(max_search_history)
                    
                    keep_ids = [row[0] for row in query.all()]
                    
                    if keep_ids:
                        # Delete older entries
                        deleted = session.query(SearchQuery).filter(
                            ~SearchQuery.id.in_(keep_ids)
                        ).delete(synchronize_session=False)
                        
                        results["search_history_removed"] = deleted
                
                # Remove permanently deleted files
                if remove_deleted:
                    # First, delete file tags for deleted files
                    deleted_file_ids = session.query(FileRecord.id).filter(
                        FileRecord.is_deleted == True
                    ).all()
                    
                    deleted_file_ids = [row[0] for row in deleted_file_ids]
                    
                    if deleted_file_ids:
                        session.query(FileTag).filter(
                            FileTag.file_id.in_(deleted_file_ids)
                        ).delete(synchronize_session=False)
                        
                        # Then delete the file records
                        deleted = session.query(FileRecord).filter(
                            FileRecord.is_deleted == True
                        ).delete(synchronize_session=False)
                        
                        results["deleted_files_removed"] = deleted
                
                return results
        except Exception as e:
            logger.error(f"Error cleaning database: {e}")
            return {"error": str(e)}


# Convenience functions

def create_db_operations(db_path: Union[str, Path]) -> DatabaseOperations:
    """Create a DatabaseOperations instance for the given database path.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        DatabaseOperations instance
    """
    from sqlalchemy import create_engine
    
    # Make sure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Create engine with reasonable defaults for SQLite
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        poolclass=sa.pool.StaticPool,
        echo=False,
    )
    
    # Initialize the schema if needed
    from panoptikon.db.schema import create_tables
    create_tables(engine)
    
    return DatabaseOperations(engine) 