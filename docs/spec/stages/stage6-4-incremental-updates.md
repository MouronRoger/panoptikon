# Stage 6.4: Incremental Updates

## Overview

The Incremental Updates module ensures the index remains fresh by efficiently processing file system changes. This component detects changes to files and directories, updates the database accordingly, and propagates changes to parent directories, focusing on minimizing processing overhead while maintaining index accuracy.

## Objectives

- Implement efficient change detection for files and directories
- Create optimized database update operations
- Build parent directory update propagation
- Optimize for low-latency updates while maintaining accuracy

## Implementation Tasks

### 1. Change Detection Logic

- Implement file comparison:
  ```python
  def has_file_changed(file_path, known_metadata):
      """Determine if file has changed compared to known metadata."""
      try:
          current_stat = os.stat(file_path)
          
          # Fast comparison using modification time and size
          if (current_stat.st_mtime != known_metadata['date_modified'] or
              current_stat.st_size != known_metadata['size']):
              return True
              
          # For critical files, could add content-based verification:
          # if is_critical_file(file_path):
          #     return file_checksum(file_path) != known_metadata.get('checksum')
              
          return False
      except OSError:
          # File no longer exists or is inaccessible
          return True
  ```

- Create verification strategies:
  - Time/size-based comparison for speed
  - Optional content hash for critical files
  - Modified attribute detection for cloud files

- Build change prioritization:
  - Prioritize recent user activity
  - Queue changes by importance
  - Batch similar changes together

### 2. Incremental Update Operations

- Implement single file updates:
  - Extract and update metadata for changed files
  - Handle file creation and deletion
  - Process file moves and renames

- Create directory update propagation:
  - Update parent directory on child changes
  - Recalculate directory sizes efficiently
  - Update directory metadata based on changes

- Build batch update optimization:
  - Group related changes
  - Process batches by directory
  - Use transaction batching for efficiency

### 3. Database Update Optimization

- Implement differential updates:
  ```python
  def update_file_metadata(file_id, old_metadata, new_metadata):
      """Update only changed metadata fields in database."""
      changes = {}
      
      for key, new_value in new_metadata.items():
          if key not in old_metadata or old_metadata[key] != new_value:
              changes[key] = new_value
              
      if not changes:
          return False  # No changes to update
          
      # Update only changed fields
      update_query = "UPDATE files SET "
      update_query += ", ".join([f"{k} = ?" for k in changes.keys()])
      update_query += " WHERE id = ?"
      
      params = list(changes.values()) + [file_id]
      
      # Execute query...
      return True
  ```

- Create update batching:
  - Group similar updates into single statements
  - Use parameterized queries
  - Implement prepared statement caching

- Build conflict resolution:
  - Handle race conditions between monitoring and scanning
  - Implement last-writer-wins strategy
  - Create change history for complex scenarios

## Testing Requirements

1. **Unit Tests**
   - Test change detection with various file modifications
   - Verify differential update generation
   - Test conflict resolution strategies

2. **Integration Tests**
   - Test database updates with real file changes
   - Verify directory propagation with nested structures
   - Test with various file operations (create, modify, delete, rename)

3. **Performance Tests**
   - Benchmark update performance (changes per second)
   - Measure transaction overhead
   - Test with various batch sizes
   - Verify sub-50ms processing for typical changes

## Success Criteria

- File changes correctly detected with >99% accuracy
- Database updates limited to changed fields only
- Parent directory updates correctly propagated
- Update operations complete in <50ms for typical changes
- Batch operations scale effectively with number of changes
- 95% test coverage achieved
- Memory usage remains within constraints during large update operations

## Dependencies

- **Requires**: Core Indexing Framework (Stage 6.1), Metadata Extraction (Stage 6.3)
- **Required by**: File System Monitoring (Stage 6.5), Folder Size Management (Stage 6.7)

## Time Estimate

- Implementation: 3-4 days
- Testing: 1-2 days
