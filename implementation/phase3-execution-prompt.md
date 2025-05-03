# Phase 3: Cloud Integration - Execution Prompt

I need you to implement the cloud storage integration for Panoptikon, extending the application to support cloud providers and enhancing the search capabilities with cloud-specific features.

## Task Overview

You're implementing cloud storage integration for Panoptikon, which includes provider detection, status tracking, extended search syntax, and UI integration for cloud status. This builds upon the native macOS UI and core functionality implemented in previous phases.

## Step 1: First, Read Project Status

Begin by reading the verification report from Phase 2 and the status document for Phase 3:

```
read_file docs/phase2_verification.md
read_file docs/phase3_status.md
```

## Step 2: Cloud Provider Detection

Create the cloud provider detection system with the following components:

1. **Provider Detector** (`src/panoptikon/cloud/detector.py`):
   - Implement detection of cloud storage locations
   - Support all required providers: iCloud, Dropbox, Google Drive, OneDrive, Box
   - Create efficient path-based detection algorithms
   - Include caching mechanism for performance
   - Handle nested provider situations
   - Implement factory pattern for provider instantiation

2. **Provider Registry** (`src/panoptikon/cloud/registry.py`):
   - Create registry for managing provider implementations
   - Implement provider discovery and registration
   - Support dynamic loading of providers
   - Use dependency injection pattern
   - Create clear interface abstractions

3. **Provider Interface** (`src/panoptikon/cloud/provider.py`):
   - Define common provider interface
   - Include detection methods
   - Specify status reporting API
   - Create path transformation utilities
   - Implement serialization support

4. **Provider Implementations**:
   - iCloud Provider (`src/panoptikon/cloud/providers/icloud.py`)
   - Dropbox Provider (`src/panoptikon/cloud/providers/dropbox.py`)
   - Google Drive Provider (`src/panoptikon/cloud/providers/gdrive.py`)
   - OneDrive Provider (`src/panoptikon/cloud/providers/onedrive.py`)
   - Box Provider (`src/panoptikon/cloud/providers/box.py`)

   Each implementation should:
   - Follow the common provider interface
   - Implement provider-specific detection logic
   - Handle provider-specific file system quirks
   - Include comprehensive documentation
   - Include proper error handling

## Step 3: Status Tracking

Implement cloud file status tracking:

1. **Status Tracker** (`src/panoptikon/cloud/status.py`):
   - Create status tracking for cloud files
   - Determine download status (downloaded vs. online-only)
   - Implement provider-specific status detection
   - Use heuristics when APIs aren't available
   - Include caching for performance
   - Follow observer pattern for updates

2. **Status Cache** (`src/panoptikon/cloud/cache.py`):
   - Implement caching mechanism for status information
   - Create invalidation strategies
   - Optimize for performance
   - Handle provider-specific caching needs
   - Include persistence across sessions

3. **Status Monitor** (`src/panoptikon/cloud/monitor.py`):
   - Create monitoring system for status changes
   - Implement event-based notification
   - Handle provider-specific change detection
   - Use efficient monitoring approaches
   - Include throttling for performance

## Step 4: Extended Search Integration

Implement cloud-aware search capabilities:

1. **Cloud Filter Extensions** (`src/panoptikon/search/extensions/cloud.py`):
   - Extend search filter system for cloud properties
   - Implement cloud: filter for provider filtering
   - Add status: filter for download status
   - Create optimized query generation
   - Integrate with existing filter system
   - Follow clean extension pattern

2. **Query Parser Extensions** (`src/panoptikon/search/parser_extensions.py`):
   - Extend query parser for cloud syntax
   - Add support for cloud filter expressions
   - Implement provider and status query parsing
   - Create clean syntax documentation
   - Integrate with existing parser

3. **Cloud Search Enhancements** (`src/panoptikon/search/cloud_search.py`):
   - Add cloud-specific search optimizations
   - Implement ranking adjustments for cloud files
   - Create specialized sorting for cloud status
   - Optimize performance for cloud queries
   - Integrate with existing search engine

## Step 5: UI Integration

Implement UI components for cloud awareness:

1. **Cloud Status Display** (`src/panoptikon/ui/components/cloud_status.py`):
   - Create status indicators for results table
   - Implement cloud provider icons
   - Add download status visualization
   - Create tooltips for status information
   - Use proper NSCell subclassing

2. **Cloud Filter UI** (`src/panoptikon/ui/components/cloud_filter.py`):
   - Implement UI for cloud filtering
   - Create provider selection interface
   - Add status filter controls
   - Integrate with search field
   - Follow macOS design guidelines

3. **Cloud Operations** (`src/panoptikon/ui/operations/cloud_ops.py`):
   - Implement operations for cloud files
   - Add download/upload functionality
   - Create provider-specific operations
   - Integrate with context menu
   - Handle errors gracefully

4. **Cloud Status View Model** (`src/panoptikon/ui/viewmodels/cloud_vm.py`):
   - Create view model for cloud status
   - Implement binding to UI components
   - Add transformations for display
   - Create status update handling
   - Follow MVVM pattern

## Step 6: Live File System Updates

Enhance the file system monitoring for cloud awareness:

1. **Enhanced File Monitor** (`src/panoptikon/index/cloud_monitor.py`):
   - Extend file system monitor for cloud awareness
   - Implement provider-specific change detection
   - Add cloud status change tracking
   - Create efficient update batching
   - Handle provider-specific events

2. **Incremental Indexing** (`src/panoptikon/index/incremental.py`):
   - Implement incremental index updates
   - Create efficient update algorithms
   - Add cloud-specific optimization
   - Minimize impact on performance
   - Integrate with existing indexing system

3. **Event System** (`src/panoptikon/utils/events.py`):
   - Create application-wide event system
   - Implement observer pattern
   - Add event types for cloud changes
   - Create subscription mechanism
   - Optimize for performance

## Step 7: Database Enhancements

Update the database to support cloud metadata:

1. **Schema Updates** (`src/panoptikon/db/cloud_schema.py`):
   - Add cloud provider and status fields
   - Create appropriate indexes
   - Implement migration for existing data
   - Optimize for query performance
   - Document schema changes

2. **Cloud Metadata Operations** (`src/panoptikon/db/cloud_operations.py`):
   - Implement operations for cloud metadata
   - Create batch update methods
   - Add provider-specific handling
   - Optimize for performance
   - Integrate with existing operations

## Step 8: Comprehensive Tests

Create thorough tests for all cloud components:

1. **Cloud Provider Tests** (`tests/test_cloud/test_providers/`):
   - Test provider detection
   - Verify interface implementation
   - Test provider-specific functionality
   - Check error handling
   - Validate caching

2. **Status Tracking Tests** (`tests/test_cloud/test_status/`):
   - Test status detection
   - Verify cache functionality
   - Test monitoring and updates
   - Check performance
   - Validate heuristics

3. **Search Integration Tests** (`tests/test_search/test_cloud/`):
   - Test cloud filter syntax
   - Verify query parsing
   - Test result ranking
   - Check search performance
   - Validate UI integration

4. **UI Component Tests** (`tests/test_ui/test_cloud/`):
   - Test status display
   - Verify filter controls
   - Test operations
   - Check view model binding
   - Validate user experience

## Deliverables

After implementing all components, create these documentation files:

1. **Implementation Log** (`docs/phase3_implementation.md`):
   - Detailed description of all implemented cloud components
   - Provider detection methods
   - Status tracking approach
   - Extended search syntax documentation
   - UI integration details
   - Known limitations with each provider

2. **Test Report** (`docs/phase3_test_report.md`):
   - Test coverage statistics
   - Provider-specific test results
   - Performance measurements
   - Validation of requirements

3. **Updated Project Status** (`docs/project_status.md`):
   - Update with Phase 3 completion
   - Document next steps for Phase 4

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
- Graceful handling of cloud provider errors
- Clear documentation of provider limitations

## References

Refer to:
- The Panoptikon specifications in document 2 (cloud storage section)
- The implementation plan in document 1
- The quality standards in document 5
