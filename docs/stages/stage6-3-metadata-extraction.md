# Stage 6.3: Metadata Extraction

## Overview

The Metadata Extraction module is responsible for efficiently extracting and processing file and directory metadata during the indexing process. This component must handle various file types, calculate directory sizes, and identify cloud storage providers while optimizing for performance.

## Objectives

- Implement efficient extraction of core file metadata
- Create directory size calculation mechanism
- Build cloud provider detection and status identification
- Optimize metadata extraction for performance

## Implementation Tasks

### 1. Basic File Metadata

- Implement core attribute extraction:
  ```python
  def extract_file_metadata(file_path):
      """Extract core metadata from file path."""
      try:
          stat_result = os.stat(file_path)
          
          return {
              'name': os.path.basename(file_path),
              'extension': os.path.splitext(file_path)[1].lower()[1:],
              'path': file_path,
              'parent_path': os.path.dirname(file_path),
              'size': stat_result.st_size,
              'date_created': stat_result.st_birthtime,
              'date_modified': stat_result.st_mtime,
              'is_directory': os.path.isdir(file_path),
              # Additional metadata...
          }
      except OSError as e:
          # Handle and log error
          return None
  ```

- Create file type detection:
  - Use extension mapping for basic detection
  - Implement UTType integration for macOS file types
  - Create fallback for unknown types

- Build extension mapping system:
  - Create database table for file type mappings
  - Implement lookup by extension
  - Support custom mappings via preferences

### 2. Directory Metadata

- Implement directory size calculation:
  ```python
  def calculate_directory_size(dir_path, cache=None):
      """Calculate total size of directory contents recursively."""
      if cache is None:
          cache = {}
          
      if dir_path in cache:
          return cache[dir_path]
          
      total_size = 0
      try:
          for entry in os.scandir(dir_path):
              if entry.is_file():
                  total_size += entry.stat().st_size
              elif entry.is_dir():
                  total_size += calculate_directory_size(entry.path, cache)
                  
          cache[dir_path] = total_size
          return total_size
      except OSError:
          # Handle and log error
          return 0
  ```

- Create parent-child relationship tracking:
  - Track directory hierarchies for efficient updates
  - Implement parent path indexing
  - Create directory tree representation

- Build attribute aggregation:
  - Count files by type within directories
  - Track newest/oldest files
  - Calculate average file size

### 3. Cloud Provider Detection

- Implement cloud storage identification:
  - Create path pattern matching for known providers
  - Implement attribute detection for cloud files
  - Support major providers (iCloud, Dropbox, Google Drive, OneDrive, Box)

- Create provider-specific metadata extraction:
  - Implement provider-specific status detection
  - Create mappings for provider-specific attributes
  - Handle offline vs. online status

- Build cloud status visualization data:
  - Create status flags for UI representation
  - Implement placeholder detection
  - Track download state for cloud files

## Testing Requirements

1. **Unit Tests**
   - Test metadata extraction with various file types
   - Verify directory size calculation accuracy
   - Test cloud provider detection with sample paths

2. **Integration Tests**
   - Test with actual file system contents
   - Verify correct metadata extraction across file types
   - Test cloud provider detection with real cloud storage paths

3. **Performance Tests**
   - Benchmark metadata extraction speed
   - Measure directory size calculation performance
   - Profile memory usage during large directory processing

## Success Criteria

- All required metadata correctly extracted and stored
- Directory size calculation accurate within 1% margin
- Cloud providers correctly identified with appropriate status
- Extraction performance exceeds 1,000 files per second
- Memory usage remains within constraints during large operations
- 95% test coverage achieved
- Clear error handling for inaccessible files

## Dependencies

- **Requires**: Core Indexing Framework (Stage 6.1), Initial Scanner (Stage 6.2)
- **Required by**: Incremental Updates (Stage 6.4), Folder Size Management (Stage 6.7)

## Time Estimate

- Implementation: 2-3 days
- Testing: 1-2 days
