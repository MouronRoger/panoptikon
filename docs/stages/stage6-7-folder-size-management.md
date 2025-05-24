# Stage 6.7: Folder Size Management

## Overview

The Folder Size Management module implements efficient calculation, storage, and incremental updates of directory sizes. This component is critical for the folder size display and sorting requirements specified in the project requirements, requiring careful optimization to maintain performance while providing accurate information.

## Objectives

- Implement efficient recursive folder size calculation
- Create database storage and indexing for size information
- Build incremental update system for maintaining size accuracy
- Optimize for performance while ensuring accurate and user-friendly sorting

## Implementation Tasks

### 1. Size Calculation Logic

- Implement recursive folder size calculation:
  ```python
  def calculate_folder_size(folder_path, cache=None):
      """Calculate total size of folder contents recursively."""
      if cache is None:
          cache = {}
          
      # Return cached value if available
      if folder_path in cache:
          return cache[folder_path]
          
      # Initialize size counter
      total_size = 0
      
      try:
          # Scan folder contents
          for entry in os.scandir(folder_path):
              try:
                  # Add file size directly
                  if entry.is_file(follow_symlinks=False):
                      total_size += entry.stat().st_size
                  # Recursively calculate subfolder size
                  elif entry.is_dir(follow_symlinks=False):
                      subfolder_size = calculate_folder_size(entry.path, cache)
                      total_size += subfolder_size
              except OSError:
                  # Skip entries with permission issues
                  continue
                  
          # Cache and return result
          cache[folder_path] = total_size
          return total_size
      except OSError:
          # Handle permission issues
          return 0
  ```

- Create optimization strategies:
  - Implement caching for intermediate results
  - Use memoization for repeated calculations
  - Support partial recalculation for updates

- Build size aggregation algorithm:
  - Optimize for depth-first calculation
  - Implement parallel processing for large directories
  - Create progress reporting integration

### 2. Database Integration

- Update schema and indexes:
  ```sql
  -- Add folder_size column to files table
  ALTER TABLE files ADD COLUMN folder_size INTEGER;
  
  -- Create index for efficient sorting
  CREATE INDEX idx_files_folder_size ON files(folder_size);
  
  -- Update schema version
  UPDATE schema_version SET version = '1.1.0', updated_at = ?;
  ```

- Implement efficient querying:
  - Create optimized queries for folder size retrieval
  - Build sorting support for size-based ordering
  - Implement filtering by size range

- Create migration process:
  - Handle existing databases
  - Implement background migration
  - Provide progress feedback during upgrade

### 3. Incremental Updates

- Implement size delta propagation:
  ```python
  def update_folder_size_incremental(file_path, size_delta, db_connection):
      """Update folder size by propagating a delta up the path tree."""
      # No update needed for zero delta
      if size_delta == 0:
          return
          
      # Get parent path
      current_path = os.path.dirname(file_path)
      
      # Continue while path exists and isn't root
      while current_path and current_path != '/':
          # Update size for current path
          cursor = db_connection.cursor()
          cursor.execute("""
              UPDATE files 
              SET folder_size = folder_size + ? 
              WHERE path = ? AND is_directory = 1
          """, (size_delta, current_path))
          
          # Move to parent directory
          current_path = os.path.dirname(current_path)
  ```

- Create parent directory update chain:
  - Efficiently propagate changes up directory tree
  - Handle file creation, modification, deletion
  - Optimize transaction batching

- Build efficient update algorithm:
  - Minimize database operations
  - Batch updates for related changes
  - Track and verify size consistency

### 4. Integration with File System Events

- Connect with file monitoring system:
  - Extract size information from file events
  - Process size changes in event handlers
  - Prioritize user-visible directory updates

- Implement verification and repair:
  - Periodic validation of directory sizes
  - Detect and correct inconsistencies
  - Schedule background verification

### 5. User-Focused Calculation Priority

- Implement prioritized calculation queue:
  ```python
  def calculate_folder_size_priority(folder_path, is_visible=False, is_user_action=False):
      """Determine calculation priority for a folder."""
      priority = 0  # Lower number = higher priority
      
      if is_user_action:
          # User is actively working with this folder - highest priority
          priority -= 100
      
      if is_visible:
          # Folder is visible in current search results - high priority
          priority -= 50
      
      # Adjust for folder depth (prioritize shallow folders)
      depth = folder_path.count(os.sep)
      priority += depth * 5
      
      return priority
  ```

- Create active window prioritization:
  - Give highest priority to user-created or modified folders
  - Elevate priority for folders visible in current search results
  - Process user actions immediately when possible

- Implement two-track processing:
  - Fast path: Direct size updates for known changes (e.g., adding a file)
  - Standard path: Background calculation for complex or initial sizing

### 6. Sorting System Integration

- Implement NULL value handling in sorting:
  - Treat NULL (uncalculated) folder sizes as having a small default value (1KB)
  - This ensures new folders remain visible in sorted results

- Update sort criteria implementation:
  ```python
  def _get_attribute_value(self, result):
      """Get attribute value, treating NULL folder sizes as 1KB."""
      value = result.metadata.get(self.attribute_name)
      
      # Special case for folder size attribute
      if self.attribute_name == "folder_size" and value is None:
          # Treat uncalculated folders as having a small default size
          return 1024  # 1KB
          
      return value
  ```

- Ensure sorting stability:
  - Maintain position of folders during calculation
  - Provide clear visual indicators for calculation state

## Testing Requirements

1. **Unit Tests**
   - Test size calculation with various directory structures
   - Verify delta propagation accuracy
   - Test database integration
   - Validate sorting behavior with different folder states

2. **Integration Tests**
   - Test with file system operations:
     - File creation, modification, deletion
     - Directory creation and deletion
     - File moves between directories
   - Verify size consistency across operations
   - Test sorting with mixed calculated and uncalculated folders

3. **Performance Tests**
   - Benchmark calculation speed for various directory sizes
   - Measure update performance under load
   - Test with large directory hierarchies (10k+ files)
   - Verify sorting performance with large result sets

4. **UX Tests**
   - Verify new folders appear appropriately in sorted results
   - Confirm calculating folders don't disrupt user experience
   - Test user-initiated actions get immediate priority

## Success Criteria

- Folder size calculation accurate within 1% margin
- Size updates correctly propagated through directory hierarchy
- Database queries optimized for efficient sorting
- Calculation performance sufficient for interactive use
- Incremental updates complete in <50ms for typical changes
- New folders appear in appropriate positions when sorted
- 95% test coverage achieved
- Memory usage remains within constraints during large calculations

## Dependencies

- **Requires**: Core Indexing Framework (Stage 6.1), Metadata Extraction (Stage 6.3), Incremental Updates (Stage 6.4)
- **Required by**: None (final feature in Stage 6)

## Time Estimate

- Implementation: 2-3 days
- Testing: 1-2 days

## Design Decisions

### Folder Size States and Representation

| State | Database Value | Display | Sorting Behavior |
|-------|---------------|---------|------------------|
| Never Calculated | NULL | "Calculating..." | Sort as 1KB (small but visible) |
| Empty | 0 bytes | "Empty" or "0 bytes" | Sort as 0 bytes |
| Partially Calculated | Previous value | Current value with indicator | Sort by current value |
| Fully Calculated | Actual size | Actual size | Sort by actual size |

### User Experience Considerations

- **Immediate Visibility**: New folders must appear in search results immediately
- **Responsive Updates**: Size changes should reflect quickly when users add/remove files
- **Stable Sorting**: Folders shouldn't jump around in sorted views during calculation
- **Accurate Representation**: Clear distinction between calculated, empty, and pending folders

These design decisions ensure that folder size calculation aligns with user expectations and provides a smooth, intuitive experience even while calculations are in progress.