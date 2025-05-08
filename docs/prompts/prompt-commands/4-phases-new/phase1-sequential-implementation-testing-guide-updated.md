# Phase 1: Sequential Implementation and Testing Guide

This document provides a complete sequential implementation and testing workflow for Phase 1 (Core Indexing) of the Panoptikon file search application. Each step includes both implementation and testing instructions for Cursor. Follow these steps in exact order.

## Initial Setup

1. **Quality Standards Setup**: Create the following files before beginning implementation:
   - `.cursor/settings.json` for editor configuration
   - `pyproject.toml` with Black, isort, ruff, and mypy configuration
   - `.pre-commit-config.yaml` for quality checks
   - Create base directory structure as per project layout

## Implementation Sequence

### Step 1: File Crawler

#### Code: Create File Crawler
```
Implement the FileCrawler in src/panoptikon/index/crawler.py:

1. Create a recursive directory traversal system that:
   - Uses pathlib instead of os.path
   - Supports exclusion patterns 
   - Handles permission errors gracefully
   - Reports progress during crawling
   - Uses generator pattern to minimize memory usage
   - Has configurable depth limit

2. Implement the following interface:

class FileCrawler:
    """Crawls the file system recursively to discover files."""
    
    def __init__(self, 
                 root_paths: List[Path], 
                 exclusions: Optional[List[str]] = None,
                 max_depth: Optional[int] = None):
        """Initialize the file crawler.
        
        Args:
            root_paths: List of root directories to crawl
            exclusions: List of glob patterns to exclude
            max_depth: Maximum recursion depth (None for unlimited)
        """
        ...
        
    def crawl(self) -> Iterator[Path]:
        """Crawl the file system and yield discovered file paths.
        
        Yields:
            Path objects for each discovered file
        """
        ...
        
    def crawl_with_progress(self) -> Iterator[Tuple[Path, int, Optional[int]]]:
        """Crawl with progress information.
        
        Yields:
            Tuples of (path, current_count, total_count)
            where total_count may be None if unknown
        """
        ...
```

#### Test: Verify File Crawler
```
Create and run tests for the FileCrawler in tests/test_index/test_crawler.py:

1. Write tests that verify:
   - Recursive directory traversal works correctly
   - Exclusion patterns are respected
   - Error handling works for inaccessible directories
   - Progress reporting provides accurate information
   - Memory usage remains low even with large directories
   - Maximum depth limitation works properly

2. Include specific test cases:
   - Test with empty directories
   - Test with nested directory structures
   - Test with symlinks (both circular and normal)
   - Test with different path formats (relative, absolute)
   - Test performance with large directory structures

3. Run the tests using pytest:
   ```
   pytest tests/test_index/test_crawler.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_index/test_crawler.py --cov=src.panoptikon.index.crawler
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase1-component01.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 2: Metadata Extractor

#### Code: Create Metadata Extractor
```
Implement the MetadataExtractor in src/panoptikon/index/metadata.py:

1. Create a metadata extraction system that:
   - Extracts all required file metadata (name, path, size, dates, extension)
   - Uses efficient OS calls to minimize I/O
   - Handles errors for inaccessible files
   - Supports batch processing for performance
   - Has a consistent return format using dataclasses

2. Implement the following interface:

@dataclass
class FileMetadata:
    """File metadata container."""
    path: Path
    name: str
    extension: str
    size: int
    created_at: datetime
    modified_at: datetime
    is_directory: bool
    # Additional metadata fields as needed

class MetadataExtractor:
    """Extracts metadata from files."""
    
    def extract(self, path: Path) -> FileMetadata:
        """Extract metadata from a single file.
        
        Args:
            path: Path to the file
            
        Returns:
            FileMetadata object with extracted information
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If the file can't be accessed
        """
        ...
        
    def extract_batch(self, paths: List[Path]) -> List[FileMetadata]:
        """Extract metadata from multiple files efficiently.
        
        Args:
            paths: List of paths to process
            
        Returns:
            List of FileMetadata objects
        """
        ...
```

#### Test: Verify Metadata Extractor
```
Create and run tests for the MetadataExtractor in tests/test_index/test_metadata.py:

1. Write tests that verify:
   - All metadata fields are correctly extracted
   - Error handling works for missing or inaccessible files
   - Batch processing improves performance
   - Different file types are handled correctly

2. Include specific test cases:
   - Test with various file types (text, binary, empty)
   - Test with files having different timestamps
   - Test with special characters in filenames
   - Test with read-only files
   - Test performance with large batches

3. Run the tests using pytest:
   ```
   pytest tests/test_index/test_metadata.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_index/test_metadata.py --cov=src.panoptikon.index.metadata
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase1-component02.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 3: Database Schema

#### Code: Create Database Schema
```
Implement the DatabaseSchema in src/panoptikon/db/schema.py:

1. Create a database schema that:
   - Defines tables for files, directories, and metadata
   - Includes proper indexes for performance
   - Uses appropriate constraints for data integrity
   - Supports version tracking for migrations
   - Uses SQLite as the database engine

2. Implement the following interface:

class DatabaseSchema:
    """Manages the database schema for Panoptikon."""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the schema manager.
        
        Args:
            connection_manager: Database connection manager
        """
        ...
        
    def create_tables(self) -> None:
        """Create all tables if they don't exist."""
        ...
        
    def get_schema_version(self) -> int:
        """Get the current schema version.
        
        Returns:
            Current schema version number
        """
        ...
        
    def get_table_definitions(self) -> Dict[str, str]:
        """Get SQL definitions for all tables.
        
        Returns:
            Dictionary mapping table names to their SQL definitions
        """
        ...
```

#### Test: Verify Database Schema
```
Create and run tests for the DatabaseSchema in tests/test_db/test_schema.py:

1. Write tests that verify:
   - Tables are created correctly
   - Indexes are created for performance
   - Constraints enforce data integrity
   - Schema version tracking works
   - Table definitions match expected SQL

2. Include specific test cases:
   - Test creating tables in a new database
   - Test schema version detection
   - Test constraint enforcement
   - Test index creation
   - Measure query performance with and without indexes

3. Run the tests using pytest:
   ```
   pytest tests/test_db/test_schema.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_db/test_schema.py --cov=src.panoptikon.db.schema
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase1-component03.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 4: Connection Manager

#### Code: Create Connection Manager
```
Implement the ConnectionManager in src/panoptikon/db/connection.py:

1. Create a connection manager that:
   - Manages SQLite connections efficiently
   - Supports connection pooling for concurrent access
   - Implements proper context management
   - Handles errors and retries
   - Provides transaction management
   - Is thread-safe for concurrent operations

2. Implement the following interface:

class ConnectionManager:
    """Manages database connections for Panoptikon."""
    
    def __init__(self, db_path: Path, max_connections: int = 5):
        """Initialize the connection manager.
        
        Args:
            db_path: Path to the SQLite database file
            max_connections: Maximum number of concurrent connections
        """
        ...
        
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection from the pool.
        
        Returns:
            SQLite connection object
            
        Raises:
            ConnectionError: If a connection cannot be established
        """
        ...
        
    def execute(self, query: str, params: Optional[Tuple] = None) -> sqlite3.Cursor:
        """Execute a query and return the cursor.
        
        Args:
            query: SQL query to execute
            params: Parameters for the query
            
        Returns:
            SQLite cursor object
        """
        ...
        
    def transaction(self) -> ContextManager:
        """Create a transaction context.
        
        Returns:
            Context manager for a transaction
        """
        ...
        
    def close_all(self) -> None:
        """Close all connections in the pool."""
        ...
```

#### Test: Verify Connection Manager
```
Create and run tests for the ConnectionManager in tests/test_db/test_connection.py:

1. Write tests that verify:
   - Connections are created and managed correctly
   - Pooling works for multiple concurrent operations
   - Transactions commit and rollback properly
   - Connection context managers work correctly
   - Errors are handled appropriately

2. Include specific test cases:
   - Test connection pooling under load
   - Test transaction isolation
   - Test error handling for corrupt databases
   - Test concurrent access patterns
   - Measure connection performance

3. Run the tests using pytest:
   ```
   pytest tests/test_db/test_connection.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_db/test_connection.py --cov=src.panoptikon.db.connection
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase1-component04.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 5: Database Operations

#### Code: Create Database Operations
```
Implement the DatabaseOperations in src/panoptikon/db/operations.py:

1. Create database operations that:
   - Provide CRUD operations for files and metadata
   - Use parameterized queries for security
   - Support batch operations for performance
   - Include optimized query patterns
   - Handle errors consistently
   - Use the connection manager for all database access

2. Implement the following interface:

class DatabaseOperations:
    """Provides database operations for Panoptikon."""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize database operations.
        
        Args:
            connection_manager: Database connection manager
        """
        ...
        
    def insert_file(self, metadata: FileMetadata) -> int:
        """Insert a file into the database.
        
        Args:
            metadata: File metadata to insert
            
        Returns:
            ID of the inserted file record
        """
        ...
        
    def insert_files_batch(self, metadata_batch: List[FileMetadata]) -> List[int]:
        """Insert multiple files in a batch operation.
        
        Args:
            metadata_batch: List of file metadata to insert
            
        Returns:
            List of inserted file record IDs
        """
        ...
        
    def get_file_by_path(self, path: Path) -> Optional[FileMetadata]:
        """Get file metadata by path.
        
        Args:
            path: Path to the file
            
        Returns:
            FileMetadata if found, None otherwise
        """
        ...
        
    def search_files(self, query: str) -> List[FileMetadata]:
        """Search for files matching a query.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching FileMetadata objects
        """
        ...
        
    def update_file(self, metadata: FileMetadata) -> bool:
        """Update an existing file record.
        
        Args:
            metadata: Updated file metadata
            
        Returns:
            True if the file was updated, False if not found
        """
        ...
        
    def delete_file(self, path: Path) -> bool:
        """Delete a file record.
        
        Args:
            path: Path to the file
            
        Returns:
            True if the file was deleted, False if not found
        """
        ...
```

#### Test: Verify Database Operations
```
Create and run tests for the DatabaseOperations in tests/test_db/test_operations.py:

1. Write tests that verify:
   - CRUD operations work correctly
   - Batch operations improve performance
   - Search functionality returns correct results
   - Error handling works appropriately
   - Edge cases are handled properly

2. Include specific test cases:
   - Test inserting and retrieving files
   - Test batch operations with various sizes
   - Test search with different queries
   - Test update and delete operations
   - Measure performance with large datasets

3. Run the tests using pytest:
   ```
   pytest tests/test_db/test_operations.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_db/test_operations.py --cov=src.panoptikon.db.operations
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase1-component05.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 6: Migration Manager

#### Code: Create Migration Manager
```
Implement the MigrationManager in src/panoptikon/db/migrations.py:

1. Create a migration manager that:
   - Manages database schema versions
   - Applies migrations in sequence
   - Supports both forward and backward migrations
   - Handles errors during migration
   - Logs migration operations
   - Maintains data integrity during migrations

2. Implement the following interface:

class Migration:
    """Base class for database migrations."""
    
    version: int
    description: str
    
    def up(self, connection: sqlite3.Connection) -> None:
        """Apply the migration.
        
        Args:
            connection: Database connection
        """
        ...
        
    def down(self, connection: sqlite3.Connection) -> None:
        """Reverse the migration.
        
        Args:
            connection: Database connection
        """
        ...

class MigrationManager:
    """Manages database migrations for Panoptikon."""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the migration manager.
        
        Args:
            connection_manager: Database connection manager
        """
        ...
        
    def get_current_version(self) -> int:
        """Get the current database version.
        
        Returns:
            Current version number
        """
        ...
        
    def get_available_migrations(self) -> List[Migration]:
        """Get all available migrations.
        
        Returns:
            List of available migrations
        """
        ...
        
    def migrate(self, target_version: Optional[int] = None) -> int:
        """Migrate the database to a target version.
        
        Args:
            target_version: Target version, or None for latest
            
        Returns:
            New database version
        """
        ...
        
    def needs_migration(self) -> bool:
        """Check if the database needs migration.
        
        Returns:
            True if migration is needed, False otherwise
        """
        ...
```

#### Test: Verify Migration Manager
```
Create and run tests for the MigrationManager in tests/test_db/test_migrations.py:

1. Write tests that verify:
   - Migrations are applied in the correct order
   - Forward and backward migrations work
   - Version tracking is accurate
   - Error handling works during migration
   - Data integrity is maintained

2. Include specific test cases:
   - Test migrations with empty database
   - Test upgrades and downgrades
   - Test migration sequence enforcement
   - Test error recovery during migration
   - Verify data integrity after migrations

3. Run the tests using pytest:
   ```
   pytest tests/test_db/test_migrations.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_db/test_migrations.py --cov=src.panoptikon.db.migrations
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase1-component06.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 7: Indexing Manager

#### Code: Create Indexing Manager
```
Implement the IndexingManager in src/panoptikon/index/indexer.py:

1. Create an indexing manager that:
   - Coordinates file crawling and metadata extraction
   - Stores file information in the database
   - Uses multiple threads for performance
   - Provides progress reporting
   - Implements throttling to limit system impact
   - Handles errors during indexing

2. Implement the following interface:

class IndexingManager:
    """Manages the file indexing process."""
    
    def __init__(self, 
                crawler: FileCrawler,
                metadata_extractor: MetadataExtractor,
                db_operations: DatabaseOperations,
                max_threads: int = 4):
        """Initialize the indexing manager.
        
        Args:
            crawler: File crawler
            metadata_extractor: Metadata extractor
            db_operations: Database operations
            max_threads: Maximum number of worker threads
        """
        ...
        
    def index(self, callback: Optional[Callable[[int, Optional[int]], None]] = None) -> int:
        """Index all files from the crawler.
        
        Args:
            callback: Optional progress callback
            
        Returns:
            Number of files indexed
        """
        ...
        
    def index_path(self, path: Path) -> int:
        """Index a specific path.
        
        Args:
            path: Path to index
            
        Returns:
            Number of files indexed
        """
        ...
        
    def stop(self) -> None:
        """Stop the indexing process."""
        ...
        
    def set_throttle(self, files_per_second: int) -> None:
        """Set indexing speed throttle.
        
        Args:
            files_per_second: Target files indexed per second
        """
        ...
```

#### Test: Verify Indexing Manager
```
Create and run tests for the IndexingManager in tests/test_index/test_indexer.py:

1. Write tests that verify:
   - Files are correctly indexed
   - Multithreading improves performance
   - Progress reporting is accurate
   - Throttling limits system impact
   - Error handling works properly

2. Include specific test cases:
   - Test with various directory structures
   - Test performance with different thread counts
   - Test throttling effectiveness
   - Test error handling with inaccessible files
   - Measure indexing speed (target: 1000+ files/second)

3. Run the tests using pytest:
   ```
   pytest tests/test_index/test_indexer.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_index/test_indexer.py --cov=src.panoptikon.index.indexer
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase1-component07.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 8: Indexing Module Integration Testing

```
Implement and run integration tests for the Indexing Module in tests/integration/phase1/test_indexing_integration.py:

1. Create integration tests that:
   - Verify all indexing components work together
   - Test the complete flow from crawling to database storage
   - Validate real-world directory structures are handled correctly
   - Measure end-to-end performance
   - Test error recovery across component boundaries

2. Include specific test scenarios:
   - Test indexing a directory with nested structure
   - Test incremental updates when files change
   - Test handling of various file types and edge cases
   - Test with moderate data volumes (10,000+ files)
   - Measure memory and CPU usage during indexing

3. Run the integration tests:
   ```
   pytest tests/integration/phase1/test_indexing_integration.py -v
   ```

4. Debug and fix any integration issues until all tests pass.

5. Measure and optimize performance:
   - Ensure indexing performance exceeds 1,000 files/second
   - Monitor memory usage during large indexing operations
   - Verify database operations are efficient

6. Success criteria:
   - All components work together seamlessly
   - Indexing performance exceeds 1,000 files/second
   - Memory usage remains reasonable during indexing
   - Error handling works across component boundaries
   - Database accurately reflects the file system

7. Create an integration report at:
   `/docs/reports/integration/phase1-indexing-integration.md`
   Include detailed metrics, performance results, and any issues encountered.
```

### Step 9: Directory Monitor

#### Code: Create Directory Monitor
```
Implement the DirectoryMonitor in src/panoptikon/index/monitor.py:

1. Create a directory monitor that:
   - Watches for file system changes
   - Uses efficient platform-specific APIs (FSEvents, inotify, etc.)
   - Throttles and batches events for performance
   - Integrates with the indexing manager
   - Minimizes resource usage
   - Handles temporary files and rapid changes

2. Implement the following interface:

class DirectoryMonitor:
    """Monitors directories for file system changes."""
    
    def __init__(self, 
                 paths: List[Path],
                 indexing_manager: IndexingManager,
                 batch_delay_ms: int = 500):
        """Initialize the directory monitor.
        
        Args:
            paths: Paths to monitor
            indexing_manager: Indexing manager for updates
            batch_delay_ms: Delay for event batching
        """
        ...
        
    def start(self) -> None:
        """Start monitoring."""
        ...
        
    def stop(self) -> None:
        """Stop monitoring."""
        ...
        
    def is_running(self) -> bool:
        """Check if monitoring is active.
        
        Returns:
            True if monitoring is active, False otherwise
        """
        ...
        
    def add_path(self, path: Path) -> None:
        """Add a new path to monitor.
        
        Args:
            path: Path to add
        """
        ...
        
    def remove_path(self, path: Path) -> None:
        """Remove a monitored path.
        
        Args:
            path: Path to remove
        """
        ...
```

#### Test: Verify Directory Monitor
```
Create and run tests for the DirectoryMonitor in tests/test_index/test_monitor.py:

1. Write tests that verify:
   - Changes are detected correctly
   - Events are batched appropriately
   - Resource usage is minimal
   - Integration with the indexing manager works
   - Error handling is robust

2. Include specific test cases:
   - Test file creation detection
   - Test file modification detection
   - Test file deletion detection
   - Test with rapid file changes
   - Measure resource usage during monitoring

3. Run the tests using pytest:
   ```
   pytest tests/test_index/test_monitor.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_index/test_monitor.py --cov=src.panoptikon.index.monitor
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase1-component08.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 10: Search Engine

#### Code: Create Search Engine
```
Implement the SearchEngine in src/panoptikon/search/engine.py:

1. Create a search engine that:
   - Executes search queries against the database
   - Implements efficient query patterns
   - Supports pagination for large result sets
   - Provides relevant result ranking
   - Handles errors gracefully
   - Supports cancellation of long-running queries

2. Implement the following interface:

class SearchEngine:
    """Executes search queries and returns results."""
    
    def __init__(self, db_operations: DatabaseOperations):
        """Initialize the search engine.
        
        Args:
            db_operations: Database operations
        """
        ...
        
    def search(self, 
               query: str, 
               limit: int = 100, 
               offset: int = 0) -> Tuple[List[FileMetadata], int]:
        """Search for files matching the query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            offset: Result offset for pagination
            
        Returns:
            Tuple of (results, total_count)
        """
        ...
        
    def search_async(self, 
                    query: str, 
                    callback: Callable[[List[FileMetadata], int], None],
                    limit: int = 100, 
                    offset: int = 0) -> Cancellable:
        """Search asynchronously with a callback.
        
        Args:
            query: Search query
            callback: Result callback
            limit: Maximum number of results
            offset: Result offset for pagination
            
        Returns:
            Cancellable object for the search operation
        """
        ...
```

#### Test: Verify Search Engine
```
Create and run tests for the SearchEngine in tests/test_search/test_engine.py:

1. Write tests that verify:
   - Search results are correct
   - Pagination works properly
   - Performance meets requirements
   - Cancellation works for long queries
   - Error handling is robust

2. Include specific test cases:
   - Test basic search functionality
   - Test with various query patterns
   - Test pagination with large result sets
   - Test asynchronous search
   - Measure search performance (target: <200ms)

3. Run the tests using pytest:
   ```
   pytest tests/test_search/test_engine.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_search/test_engine.py --cov=src.panoptikon.search.engine
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase1-component09.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 11: Query Parser

#### Code: Create Query Parser
```
Implement the QueryParser in src/panoptikon/search/parser.py:

1. Create a query parser that:
   - Parses search queries into structured representations
   - Supports basic text search
   - Handles special operators and modifiers
   - Provides helpful error messages for invalid syntax
   - Is extensible for future query capabilities
   - Generates optimized database queries

2. Implement the following interface:

class QueryNode:
    """Base class for query AST nodes."""
    pass

class TextNode(QueryNode):
    """Text search node."""
    text: str

class AndNode(QueryNode):
    """Logical AND node."""
    children: List[QueryNode]

class OrNode(QueryNode):
    """Logical OR node."""
    children: List[QueryNode]

class NotNode(QueryNode):
    """Logical NOT node."""
    child: QueryNode

class QueryParser:
    """Parses search queries into query trees."""
    
    def parse(self, query_string: str) -> QueryNode:
        """Parse a query string into a query tree.
        
        Args:
            query_string: Query string to parse
            
        Returns:
            Root query node
            
        Raises:
            QuerySyntaxError: If the query syntax is invalid
        """
        ...
        
    def to_sql(self, node: QueryNode) -> Tuple[str, List]:
        """Convert a query node to an SQL WHERE clause.
        
        Args:
            node: Query node
            
        Returns:
            Tuple of (sql_clause, parameters)
        """
        ...
```

#### Test: Verify Query Parser
```
Create and run tests for the QueryParser in tests/test_search/test_parser.py:

1. Write tests that verify:
   - Query parsing works correctly
   - SQL generation is optimized
   - Error handling provides useful messages
   - All query features are supported
   - Performance is acceptable

2. Include specific test cases:
   - Test basic text queries
   - Test logical operators (AND, OR, NOT)
   - Test error handling for invalid syntax
   - Test SQL generation for various queries
   - Measure parsing performance

3. Run the tests using pytest:
   ```
   pytest tests/test_search/test_parser.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_search/test_parser.py --cov=src.panoptikon.search.parser
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase1-component10.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 12: Filter Builder

#### Code: Create Filter Builder
```
Implement the FilterBuilder in src/panoptikon/search/filters.py:

1. Create a filter builder that:
   - Constructs filters from parsed queries
   - Supports various filter types (text, date, size, etc.)
   - Generates optimized SQL for each filter type
   - Combines filters efficiently
   - Handles different comparison operators
   - Is extensible for new filter types

2. Implement the following interface:

class Filter:
    """Base class for search filters."""
    
    def to_sql(self) -> Tuple[str, List]:
        """Convert filter to SQL.
        
        Returns:
            Tuple of (sql_clause, parameters)
        """
        ...

class TextFilter(Filter):
    """Text search filter."""
    
    def __init__(self, field: str, text: str, match_type: str = 'contains'):
        """Initialize text filter.
        
        Args:
            field: Field to search
            text: Text to search for
            match_type: Match type ('contains', 'starts', 'ends', 'exact')
        """
        ...

class DateFilter(Filter):
    """Date comparison filter."""
    
    def __init__(self, field: str, date: datetime, operator: str = '='):
        """Initialize date filter.
        
        Args:
            field: Date field to compare
            date: Date to compare against
            operator: Comparison operator ('=', '<', '>', '<=', '>=')
        """
        ...

class SizeFilter(Filter):
    """File size filter."""
    
    def __init__(self, size: int, operator: str = '='):
        """Initialize size filter.
        
        Args:
            size: Size in bytes
            operator: Comparison operator ('=', '<', '>', '<=', '>=')
        """
        ...

class FilterBuilder:
    """Builds search filters from query nodes."""
    
    def build(self, node: QueryNode) -> Filter:
        """Build a filter from a query node.
        
        Args:
            node: Query node
            
        Returns:
            Filter object
        """
        ...
```

#### Test: Verify Filter Builder
```
Create and run tests for the FilterBuilder in tests/test_search/test_filters.py:

1. Write tests that verify:
   - Filters are built correctly from query nodes
   - SQL generation is optimized
   - Different filter types work as expected
   - Filters combine properly
   - Performance is acceptable

2. Include specific test cases:
   - Test text filters with different match types
   - Test date filters with various operators
   - Test size filters with different units
   - Test combined filters
   - Measure filter building performance

3. Run the tests using pytest:
   ```
   pytest tests/test_search/test_filters.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_search/test_filters.py --cov=src.panoptikon.search.filters
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase1-component11.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 13: Results Manager

#### Code: Create Results Manager
```
Implement the ResultsManager in src/panoptikon/search/results.py:

1. Create a results manager that:
   - Handles large result sets efficiently
   - Implements pagination and sorting
   - Provides result ranking
   - Supports asynchronous result fetching
   - Offers memory-efficient iteration
   - Includes result metadata for UI display

2. Implement the following interface:

class SearchResult:
    """Container for search results."""
    
    def __init__(self, 
                 metadata: List[FileMetadata], 
                 total_count: int, 
                 query: str,
                 execution_time_ms: float):
        """Initialize search result.
        
        Args:
            metadata: List of file metadata
            total_count: Total result count
            query: Original query string
            execution_time_ms: Query execution time
        """
        ...
        
    def has_more(self) -> bool:
        """Check if there are more results.
        
        Returns:
            True if there are more results, False otherwise
        """
        ...
        
    def get_page(self, page: int, page_size: int) -> List[FileMetadata]:
        """Get a results page.
        
        Args:
            page: Page number (0-based)
            page_size: Page size
            
        Returns:
            List of file metadata for the page
        """
        ...

class ResultsManager:
    """Manages search results."""
    
    def __init__(self, search_engine: SearchEngine):
        """Initialize results manager.
        
        Args:
            search_engine: Search engine
        """
        ...
        
    def get_results(self, 
                   query: str, 
                   limit: int = 100, 
                   offset: int = 0) -> SearchResult:
        """Get search results.
        
        Args:
            query: Search query
            limit: Maximum number of results
            offset: Result offset
            
        Returns:
            Search result object
        """
        ...
        
    def get_results_async(self, 
                         query: str, 
                         callback: Callable[[SearchResult], None],
                         limit: int = 100, 
                         offset: int = 0) -> Cancellable:
        """Get search results asynchronously.
        
        Args:
            query: Search query
            callback: Result callback
            limit: Maximum number of results
            offset: Result offset
            
        Returns:
            Cancellable object
        """
        ...
        
    def sort_results(self, 
                    result: SearchResult, 
                    sort_by: str, 
                    ascending: bool = True) -> SearchResult:
        """Sort search results.
        
        Args:
            result: Search result
            sort_by: Field to sort by
            ascending: Sort in ascending order
            
        Returns:
            Sorted search result
        """
        ...
```

#### Test: Verify Results Manager
```
Create and run tests for the ResultsManager in tests/test_search/test_results.py:

1. Write tests that verify:
   - Result pagination works correctly
   - Sorting functions properly
   - Asynchronous fetching works
   - Memory usage remains reasonable with large results
   - Performance meets requirements

2. Include specific test cases:
   - Test with various page sizes
   - Test sorting by different fields
   - Test asynchronous result fetching
   - Test with large result sets
   - Measure memory usage during result handling

3. Run the tests using pytest:
   ```
   pytest tests/test_search/test_results.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_search/test_results.py --cov=src.panoptikon.search.results
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase1-component12.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 14: Search Module Integration Testing

```
Implement and run integration tests for the Search Module in tests/integration/phase1/test_search_integration.py:

1. Create integration tests that:
   - Verify all search components work together
   - Test the complete flow from query to results
   - Validate search performance meets requirements
   - Test with realistic search patterns
   - Verify result accuracy

2. Include specific test scenarios:
   - Test basic text search
   - Test complex queries with operators
   - Test pagination and sorting
   - Test with large indexes (100,000+ files)
   - Measure search performance (target: <200ms)

3. Run the integration tests:
   ```
   pytest tests/integration/phase1/test_search_integration.py -v
   ```

4. Debug and fix any integration issues until all tests pass.

5. Measure and optimize performance:
   - Ensure search response time is under 200ms for typical queries
   - Monitor memory usage during searches with large result sets
   - Verify result accuracy across different query types

6. Success criteria:
   - All components work together seamlessly
   - Search performance meets the 200ms requirement
   - Result accuracy is high
   - Memory usage remains reasonable
   - Error handling works across component boundaries

7. Create an integration report at:
   `/docs/reports/integration/phase1-search-integration.md`
   Include detailed metrics, performance results, and any issues encountered.
```

### Step 15: Terminal Interface

#### Code: Create Terminal Interface
```
Implement the TerminalInterface in src/panoptikon/ui/terminal.py:

1. Create a terminal interface that:
   - Provides a text-based user interface
   - Implements interactive search
   - Displays results in a readable format
   - Supports basic navigation and file operations
   - Handles terminal resizing
   - Has a clean shutdown process

2. Implement the following interface:

class TerminalInterface:
    """Text-based terminal interface for Panoptikon."""
    
    def __init__(self, 
                 results_manager: ResultsManager,
                 indexing_manager: IndexingManager):
        """Initialize terminal interface.
        
        Args:
            results_manager: Search results manager
            indexing_manager: Indexing manager
        """
        ...
        
    def run(self) -> None:
        """Run the terminal interface."""
        ...
        
    def show_results(self, results: SearchResult) -> None:
        """Display search results.
        
        Args:
            results: Search results
        """
        ...
        
    def handle_command(self, command: str) -> bool:
        """Handle a command.
        
        Args:
            command: Command string
            
        Returns:
            True to continue, False to exit
        """
        ...
        
    def shutdown(self) -> None:
        """Clean shutdown of the interface."""
        ...
```

#### Test: Verify Terminal Interface
```
Create and run tests for the TerminalInterface in tests/test_ui/test_terminal.py:

1. Write tests that verify:
   - Commands are parsed correctly
   - Results are displayed properly
   - Navigation works as expected
   - Error handling is user-friendly
   - Clean shutdown works

2. Include specific test cases:
   - Test search command processing
   - Test result display formatting
   - Test navigation commands
   - Test error handling for invalid commands
   - Test graceful shutdown

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/test_terminal.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/test_terminal.py --cov=src.panoptikon.ui.terminal
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase1-component13.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 16: Command Line Arguments

#### Code: Create Command Line Arguments
```
Implement the CommandLineArguments in src/panoptikon/ui/cli.py:

1. Create a command line argument parser that:
   - Processes command line options
   - Supports various run modes
   - Includes help text
   - Validates inputs
   - Provides sensible defaults
   - Configures logging based on verbosity

2. Implement the following interface:

class CommandLineArguments:
    """Processes command line arguments."""
    
    def __init__(self):
        """Initialize command line argument parser."""
        ...
        
    def parse(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """Parse command line arguments.
        
        Args:
            args: Command line arguments, or None for sys.argv
            
        Returns:
            Parsed arguments
        """
        ...
        
    def show_help(self) -> None:
        """Display help text."""
        ...
        
    def configure_logging(self, args: argparse.Namespace) -> None:
        """Configure logging based on arguments.
        
        Args:
            args: Parsed arguments
        """
        ...
```

#### Test: Verify Command Line Arguments
```
Create and run tests for the CommandLineArguments in tests/test_ui/test_cli.py:

1. Write tests that verify:
   - Arguments are parsed correctly
   - Help text is comprehensive
   - Validation catches invalid inputs
   - Defaults are sensible
   - Logging is configured correctly

2. Include specific test cases:
   - Test with various argument combinations
   - Test help text generation
   - Test validation of invalid arguments
   - Test default values
   - Test logging configuration

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/test_cli.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/test_cli.py --cov=src.panoptikon.ui.cli
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase1-component14.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 17: Final Application Testing and Build

```
Implement and run application-level tests and build for Phase 1 in tests/application/test_phase1_application.py:

1. Create application tests that:
   - Verify the entire application works end-to-end
   - Test realistic user workflows
   - Validate performance requirements
   - Test with substantial data volumes
   - Verify usability of the terminal interface

2. Include specific test scenarios:
   - Test application startup and shutdown
   - Test indexing large directory structures
   - Test search performance and accuracy
   - Test user interface responsiveness
   - Measure resource usage during operation

3. Run the application tests:
   ```
   pytest tests/application/test_phase1_application.py -v
   ```

4. Debug and fix any application issues until all tests pass.

5. Create a build script in scripts/build_phase1.py that:
   - Creates a runnable terminal application
   - Packages all dependencies
   - Configures logging
   - Sets up proper environment
   - Provides documentation

6. Run the build script and verify the built application:
   ```
   python scripts/build_phase1.py
   ```

7. Test the built application manually with real-world scenarios.

8. Success criteria:
   - All application tests pass
   - The application builds successfully
   - Indexing performance exceeds 1,000 files/second
   - Search response time is under 200ms
   - Memory usage is within acceptable limits
   - User experience is smooth and intuitive

9. Create a final phase report at:
   `/docs/reports/phase1_completion_report.md`
   Include comprehensive metrics, performance results, and an overview of the implementation.
```

## Implementation Notes

1. **Starting Incrementally**: Implement one component at a time, fully testing each before proceeding.
2. **Quality First**: Never compromise on quality standards.
3. **Performance Emphasis**: Focus on the two critical performance metrics early:
   - 1,000+ files per second for indexing
   - <200ms response time for searches
4. **Use Test-Driven Development**: Consider writing tests before implementation.
5. **Document As You Go**: Keep documentation in sync with code.

## Progress Tracking

Create a project board that tracks:
1. Components completed with test coverage metrics
2. Integration test results
3. Performance benchmarks
4. Outstanding issues and technical debt

Update this board after each component and integration test is completed.
