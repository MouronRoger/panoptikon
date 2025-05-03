# Phase 1: MVP Implementation - Execution Prompt

I need you to implement the core MVP functionality for Panoptikon according to the specification document and project structure established in Phase 0.

## Task Overview

You're implementing the minimal viable system for Panoptikon, consisting of:
1. A recursive file indexer
2. A persistent metadata store using SQLite
3. A basic search API
4. A terminal-based search interface for testing

## Step 1: First, Read Project Status

Begin by reading the verification report from Phase 0 and the status document for Phase 1:

```
read_file docs/phase0_verification.md
read_file docs/phase1_status.md
```

## Step 2: File Indexing System Implementation

Create the file indexing system with the following components:

1. **File System Crawler** (`src/panoptikon/index/crawler.py`):
   - Implement a recursive directory crawler that traverses file systems
   - Use pathlib instead of os.path for all path operations
   - Handle permissions errors gracefully
   - Support exclusion patterns for directories/files
   - Include progress reporting mechanism
   - Implement proper resource management

2. **Metadata Extractor** (`src/panoptikon/index/metadata.py`):
   - Extract required metadata: filename, path, size, dates, extension
   - Implement efficient metadata collection methods
   - Handle different file systems and encodings
   - Support extended attributes where available

3. **Indexing Manager** (`src/panoptikon/index/indexer.py`):
   - Coordinate crawling and metadata extraction
   - Manage threading for performance (1000+ files/second)
   - Implement throttling to minimize system impact
   - Provide progress feedback mechanism
   - Handle interruptions gracefully

4. **Directory Monitor** (`src/panoptikon/index/monitor.py`):
   - Create a basic file system change monitor
   - Support watching directories for changes
   - Implement event queuing system
   - Use efficient native APIs where possible

## Step 3: Database Module Implementation

Create the database module with these components:

1. **Database Schema** (`src/panoptikon/db/schema.py`):
   - Define SQLite schema for storing file metadata
   - Implement proper indexes for fast searching
   - Support all required metadata fields
   - Include versioning for future migrations

2. **Database Operations** (`src/panoptikon/db/operations.py`):
   - Implement CRUD operations for file metadata
   - Create batch operation methods for performance
   - Use parameterized queries for security
   - Support transaction management

3. **Connection Manager** (`src/panoptikon/db/connection.py`):
   - Implement proper connection pooling
   - Handle database file creation and initialization
   - Manage connection lifecycle
   - Include error handling and recovery

4. **Migration Support** (`src/panoptikon/db/migrations.py`):
   - Create migration framework for schema changes
   - Implement version tracking in database
   - Support automatic migrations on startup
   - Include validation of schema integrity

## Step 4: Search Functionality Implementation

Create the search module with these components:

1. **Search Engine** (`src/panoptikon/search/engine.py`):
   - Implement core search execution logic
   - Optimize for performance (<200ms response time)
   - Support incremental search (refining as user types)
   - Include relevance ranking

2. **Query Parser** (`src/panoptikon/search/parser.py`):
   - Create basic parser for search terms
   - Support simple patterns and wildcards
   - Implement case sensitivity options
   - Prepare for extended syntax in future phases

3. **Filter Builder** (`src/panoptikon/search/filters.py`):
   - Implement filter construction for queries
   - Support filtering by name, path, extension
   - Convert filters to efficient SQL queries
   - Include optimization for common cases

4. **Result Manager** (`src/panoptikon/search/results.py`):
   - Implement result object structure
   - Support sorting by relevance and metadata
   - Create paging mechanism for large results
   - Include serialization for display

## Step 5: Terminal Interface Implementation

Create a simple command-line interface for testing:

1. **Terminal Interface** (`src/panoptikon/cli/interface.py`):
   - Implement a basic terminal UI
   - Support as-you-type search
   - Display search results in tabular format
   - Include commands for indexing and searching
   - Show progress during indexing

2. **CLI Arguments** (`src/panoptikon/cli/args.py`):
   - Parse command-line arguments
   - Support options for verbosity, paths, etc.
   - Include help documentation

## Step 6: Comprehensive Tests

Create thorough tests for all components:

1. **Indexer Tests** (`tests/test_index/`):
   - Test crawler with various directory structures
   - Verify metadata extraction accuracy
   - Test indexing performance
   - Validate monitor functionality

2. **Database Tests** (`tests/test_db/`):
   - Test schema creation and migrations
   - Verify CRUD operations
   - Test transaction handling
   - Validate connection management

3. **Search Tests** (`tests/test_search/`):
   - Test search performance and accuracy
   - Verify query parsing
   - Test filter construction
   - Validate result sorting and ranking

4. **CLI Tests** (`tests/test_cli/`):
   - Test command-line interface
   - Verify output formatting
   - Test progress reporting

## Deliverables

After implementing all components, create these documentation files:

1. **Implementation Log** (`docs/phase1_implementation.md`):
   - Detailed description of all implemented components
   - API documentation for each module
   - Design decisions and patterns used
   - Performance characteristics and benchmarks
   - Known limitations or edge cases

2. **Test Report** (`docs/phase1_test_report.md`):
   - Test coverage statistics
   - Performance test results
   - Validation of requirements

3. **Updated Project Status** (`docs/project_status.md`):
   - Update with Phase 1 completion
   - Document next steps for Phase 2

These documents are CRITICAL for continuity as they will be used by the next instance of Claude to proceed with verification and future phases.

## Quality Standards

All implementation must adhere to these standards:

- Complete type annotations for all functions and methods
- Comprehensive docstrings following Google style
- Maximum file length of 500 lines
- Maximum function length of 50 lines
- No circular dependencies between modules
- Clear separation of concerns
- Minimum 80% test coverage
- All tests must pass
- Performance requirements must be met

## References

Refer to:
- The Panoptikon specifications in document 2
- The implementation plan in document 1
- The quality standards in document 5
