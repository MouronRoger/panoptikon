# 🚧 STAGE 6: INDEXING SYSTEM

## 📝 OBJECTIVES
- Implement file system scanning and indexing
- Create metadata extraction system
- Build incremental update mechanism
- Develop indexing prioritization
- Implement progress tracking

## 🔧 IMPLEMENTATION TASKS

1. **Initial Scanner**:
   - Build recursive directory scanning
   - Implement path rule evaluation during scan
   - Create batch processing for efficiency
   - Design throttling for system impact

2. **Metadata Extraction**:
   - Implement file metadata extraction
   - Create file type identification
   - Build attribute harvesting
   - Support cloud metadata handling

3. **Incremental Updates**:
   - Implement change-based index updates
   - Create event-driven indexing
   - Build diff detection for efficient updates
   - Design conflict resolution

4. **Priority Management**:
   - Build intelligent scanning prioritization
   - Implement user focus areas
   - Create frequency-based prioritization
   - Support manual priority overrides

5. **Progress Tracking**:
   - Implement indexing progress monitoring
   - Create status reporting
   - Build ETA calculation
   - Support cancellation and pausing

## 🧪 TESTING REQUIREMENTS
- Verify indexing processes >1000 files/second
- Test incremental updates with various changes
- Validate metadata extraction accuracy
- Measure indexing performance with benchmarks
- Verify prioritization correctly orders operations
- Test progress tracking accuracy
- Maintain 95% code coverage

## 🚫 CONSTRAINTS
- Design for low system impact during indexing
- Support background operation
- Maintain incremental progress persistence
- Ensure thread safety across operations

## 📋 DEPENDENCIES
- Stage 2 service container
- Stage 2 event bus
- Stage 3 filesystem operations
- Stage 3 FSEvents wrapper
- Stage 4 database schema

## Folder Size Calculation

- The `folder_size` column is present in the schema as of version 1.1.0 (migration complete; see [Folder Size Implementation](../../components/folder-size-implementation.md)).
- The migration system (Stage 4.3) ensures all databases are upgraded before folder size calculation logic is implemented.
- Implement recursive folder size calculation for all indexed directories (pending).
- Store calculated folder sizes in the `folder_size` column of the files table.
- Update folder sizes incrementally as files are added, removed, or changed.
- Handle symlinks, hard links, and permission errors robustly.
- This enables instant folder size display and sorting in the UI (see Integration Report).
- Add tests to ensure accuracy and performance of folder size calculation.
