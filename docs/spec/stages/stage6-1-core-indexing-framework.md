# Stage 6.1: Core Indexing Framework

## Overview

The Core Indexing Framework establishes the foundation for all indexing operations in Panoptikon. This substage focuses on creating the core services, interfaces, and database access patterns needed for efficient file indexing.

## Objectives

- Create a robust service-based architecture for the indexing system
- Implement efficient database access patterns for batch operations
- Establish indexing state management for resilience and recovery
- Define the event model for indexing operations

## Implementation Tasks

### 1. Indexer Service Interface

- Create `IndexerServiceInterface` class defining the contract for all indexing operations:
  ```python
  class IndexerServiceInterface(ServiceInterface):
      """Base interface for indexing services."""
      
      def start_initial_indexing(self, paths):
          """Begin initial indexing of specified paths."""
          raise NotImplementedError
          
      def start_incremental_indexing(self, paths=None):
          """Begin incremental indexing of specified paths, or all if None."""
          raise NotImplementedError
          
      def pause_indexing(self):
          """Pause any ongoing indexing operations."""
          raise NotImplementedError
          
      def resume_indexing(self):
          """Resume previously paused indexing operations."""
          raise NotImplementedError
          
      def get_indexing_status(self):
          """Return the current indexing status."""
          raise NotImplementedError
  ```

- Implement concrete `IndexerService` class that implements this interface
- Create registration in the service container

### 2. Indexing Events

- Define event types for indexing operations:
  - `IndexingStartedEvent`: Triggered when indexing begins
  - `IndexingProgressEvent`: Triggered periodically during indexing
  - `IndexingCompletedEvent`: Triggered when indexing completes
  - `IndexingPausedEvent`: Triggered when indexing is paused
  - `IndexingResumedEvent`: Triggered when indexing is resumed
  - `IndexingErrorEvent`: Triggered when errors occur during indexing

- Implement event publication in the indexer service

### 3. Database Access Layer

- Create prepared statements for common indexing operations:
  - Batch insert of files
  - Batch update of file metadata
  - Deletion of files
  - Retrieval of indexed paths

- Implement transaction management:
  - Begin/commit/rollback handling
  - Error recovery
  - Connection pooling

- Create optimized batch operations:
  - File batch size tuning (start with 1000 files per transaction)
  - Metadata extraction optimization
  - Statement reuse

### 4. Indexing State Management

- Implement state persistence:
  - Create table structure for indexing state
  - Implement state serialization/deserialization
  - Store checkpoint information for recovery

- Create recovery mechanisms:
  - Detect interrupted indexing operations
  - Resume from last checkpoint
  - Verify data consistency

- Build progress tracking:
  - Estimated total files
  - Files processed
  - Current processing rate
  - Estimated completion time

## Testing Requirements

1. **Unit Tests**
   - Test all interface methods with mock implementations
   - Verify correct event publication
   - Test transaction management with simulated errors
   - Validate state persistence and recovery

2. **Integration Tests**
   - Test interaction between indexer service and database
   - Verify event handling across components
   - Test recovery after simulated crashes

3. **Performance Tests**
   - Benchmark batch insert operations (files per second)
   - Measure transaction overhead
   - Test with varying batch sizes to determine optimal configuration

## Success Criteria

- All interface methods correctly implemented and tested
- Database operations perform at >1000 files/second for batch inserts
- Indexing state correctly persists and recovers
- Events properly published and received
- 95% test coverage achieved
- Documentation complete for all public interfaces

## Dependencies

- **Requires**: Service Container (Stage 2), Database Foundation (Stage 4)
- **Required by**: All subsequent indexing substages

## Time Estimate

- Implementation: 2-3 days
- Testing: 1-2 days
