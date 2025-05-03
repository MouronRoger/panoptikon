# Panoptikon Project: Engineered Prompts & Documentation Chain

## Overview

This document outlines a complete system of engineered prompts and documentation artifacts to guide Cursor AI through the development of the Panoptikon file search application. Each phase includes:

1. **Status Document** - The current state of the project
2. **Execution Prompt** - Instructions for Cursor AI to implement the current phase
3. **Verification Prompt** - Instructions to verify implementation and document results
4. **Transition Document** - A handoff document for the next phase

## Documentation Chain Architecture

Each phase will maintain and update these key documents:

1. **`project_status.md`** - Current phase, completed work, and next steps
2. **`implementation_log.md`** - Detailed records of all implemented components
3. **`verification_results.md`** - Test results and quality checks
4. **`architecture_blueprint.md`** - System architecture and design decisions

## Phase 0: Project Bootstrapping

### Status Document: `phase0_status.md`
```markdown
# Panoptikon Project Status: Phase 0 (Project Bootstrapping)

## Current Phase
- Initializing project structure and quality infrastructure

## Required Implementation
- Project directory scaffold
- Quality tooling configuration
- Test framework setup
- Module structure definition

## Next Steps
- Set up the entire project environment with linters, formatters, test scaffolding, and modular structure
- Ensure all code passes lint/test CI from the beginning
```

### Execution Prompt: Phase 0 Implementation
```
I need you to bootstrap the Panoptikon file search application with a focus on quality from day one. Please implement:

1. Create the basic project structure:
   - Initialize a Python package structure for the Panoptikon application
   - Set up the directory structure according to the specifications in document 5
   - Create initial __init__.py files for proper module structure

2. Configure quality tools:
   - Implement linting with ruff, flake8, and pylint
   - Set up code formatting with black (120 char line length)
   - Configure mypy for static type checking
   - Set up pre-commit hooks for quality enforcement

3. Create test infrastructure:
   - Set up pytest for test execution
   - Configure coverage.py for tracking test coverage
   - Create test directory structure mirroring the main package
   - Set up basic fixture patterns for future use

4. Documentation framework:
   - Create README.md with project overview
   - Set up project documentation structure
   - Initialize CONTRIBUTING.md with quality guidelines

Refer to document 5 (quality-standards-implementation.md) for detailed specifications on quality standards.

Refer to documents 1 and 4 for the project structure recommendations.

Deliverables:
1. Complete project skeleton with all required directories and files
2. Configuration files for all quality tools
3. Functional test framework
4. Basic documentation structure

After implementation, create a detailed status document at 'docs/phase0_complete.md' that includes:
1. Project structure diagram
2. List of all configured quality checks
3. Instructions for running tests
4. Next steps for Phase 1

This document is CRITICAL for continuity as it will be used in subsequent tasks.
```

### Verification Prompt: Phase 0 Verification
```
I need you to verify the Phase 0 implementation of the Panoptikon project bootstrapping.

First, read the implementation documentation:
read_file docs/phase0_complete.md

Then, perform these verification steps:

1. Verify project structure:
   - Check that all required directories exist
   - Confirm proper package structure with __init__.py files
   - Validate module boundaries are clearly defined

2. Verify quality tool configuration:
   - Run linters to confirm they're properly configured
   - Test formatting tools on sample files
   - Verify mypy type checking is working

3. Test the test framework:
   - Run a basic test to confirm pytest is working
   - Check that coverage reporting is functional
   - Verify test directory structure mirrors main package

4. Documentation check:
   - Review README.md for completeness
   - Confirm CONTRIBUTING.md contains quality guidelines
   - Check documentation structure is in place

Create a verification report at 'docs/phase0_verification.md' that includes:
1. Results of all verification steps
2. Any issues or discrepancies found
3. Recommendations for improvements
4. Confirmation that Phase 0 is complete and ready for Phase 1

This verification document is CRITICAL for continuity and will be used to begin Phase 1.
```

### Transition Document: Phase 1 Preparation
```markdown
# Transition to Phase 1: MVP Implementation

## Phase 0 Completion Status
- Project structure established ✓
- Quality tools configured ✓  
- Test framework implemented ✓
- Documentation initialized ✓

## Phase 1 Objectives
- Implement recursive file indexer
- Create persistent metadata store (SQLite)
- Develop terminal-based search interface
- Complete all core MVP functionality

## Required Components
- File system crawler
- SQLite schema and operations
- Search API with basic functionality
- Command-line interface for testing

## Development Guidelines
- Follow the quality standards established in Phase 0
- Maintain test coverage for all new components
- Update documentation for all implemented features
- Use the modular architecture defined in the blueprint
```

## Phase 1: MVP Implementation

### Status Document: `phase1_status.md`
```markdown
# Panoptikon Project Status: Phase 1 (MVP)

## Current Phase
- Implementing core MVP functionality

## Components to Implement
- File indexing system (crawler, metadata extractor)
- Database schema and operations
- Basic search functionality
- Terminal interface

## Required Features
- Recursive file indexing
- Metadata collection and storage
- Basic as-you-type filename/path search
- Search performance under 200ms

## Next Steps
- Implement each component according to the quality standards
- Create comprehensive tests for all functionality
- Document the API and usage patterns
```

### Execution Prompt: Phase 1 Implementation
```
I need you to implement the core MVP functionality for Panoptikon. This includes the file indexer, database, and search functionality.

First, read the project status:
read_file docs/phase0_verification.md

Then, implement the following components:

1. File Indexing System:
   - Create a recursive file crawler (src/panoptikon/index/crawler.py) that traverses directories
   - Implement metadata extraction (src/panoptikon/index/metadata.py) for collecting file info
   - Add a file system monitor (src/panoptikon/index/monitor.py) for detecting changes
   - Implement indexing controller (src/panoptikon/index/indexer.py) to manage the process

2. Database Module:
   - Create database schema (src/panoptikon/db/schema.py) for storing file metadata
   - Implement database operations (src/panoptikon/db/operations.py) for CRUD functionality
   - Add migration support (src/panoptikon/db/migrations.py) for schema versioning
   - Create connection management (src/panoptikon/db/connection.py) for database access

3. Search Functionality:
   - Implement search engine (src/panoptikon/search/engine.py) for executing queries
   - Create query parser (src/panoptikon/search/parser.py) for handling search syntax
   - Add filter builder (src/panoptikon/search/filters.py) for query constraints
   - Implement result ranking (src/panoptikon/search/ranker.py) for relevance sorting

4. Terminal Interface:
   - Create a simple CLI (src/panoptikon/cli/interface.py) for testing
   - Implement as-you-type search in terminal

For each component:
1. Follow the project quality standards
2. Write comprehensive tests
3. Add complete type annotations and docstrings
4. Ensure performance meets requirements

After implementation, create a detailed implementation log at 'docs/phase1_implementation.md' that includes:
1. Description of all implemented components
2. API documentation for each module
3. Performance characteristics
4. Test coverage report
5. Known limitations or future improvements

This document is CRITICAL for continuity as it will be used in subsequent tasks.
```

### Verification Prompt: Phase 1 Verification
```
I need you to verify the Phase 1 MVP implementation of the Panoptikon project.

First, read the implementation documentation:
read_file docs/phase1_implementation.md

Then, perform these verification steps:

1. Code Quality Verification:
   - Run all linters and check for any violations
   - Verify type annotations are complete
   - Check docstring coverage
   - Confirm code structure follows project guidelines

2. Functionality Testing:
   - Test file indexing with sample directories
   - Verify database operations store metadata correctly
   - Test search functionality with basic queries
   - Check CLI interface operations

3. Performance Validation:
   - Measure indexing speed (should process 1000+ files/second)
   - Test search response time (should be under 200ms)
   - Check memory usage during operation

4. Test Coverage:
   - Run test suite with coverage
   - Verify 80%+ code coverage
   - Identify any untested edge cases

Create a verification report at 'docs/phase1_verification.md' that includes:
1. Results of all verification steps
2. Performance metrics
3. Test coverage statistics
4. Any issues or limitations found
5. Recommendations for Phase 2
6. Confirmation that Phase 1 is complete

This verification document is CRITICAL for continuity and will be used to begin Phase 2.
```

### Transition Document: Phase 2 Preparation
```markdown
# Transition to Phase 2: Native macOS UI

## Phase 1 Completion Status
- File indexing system implemented ✓
- Database module completed ✓
- Search functionality working ✓
- Terminal interface operational ✓

## Phase 2 Objectives
- Implement native macOS UI using PyObjC
- Create search box with live results
- Add column sorting and file operations
- Integrate with menu bar

## Required Components
- PyObjC window and application setup
- UI components for search and results
- File operation handlers
- Menu bar integration

## Development Guidelines
- Continue following quality standards
- Maintain separation between UI and core functionality
- Document all Objective-C interop clearly
- Handle memory management properly in PyObjC code
```

## Phase 2: Native macOS UI

### Status Document: `phase2_status.md`
```markdown
# Panoptikon Project Status: Phase 2 (Native macOS UI)

## Current Phase
- Implementing native macOS UI with PyObjC

## Components to Implement
- Application window and controllers
- Search interface components
- Results display with sorting
- File operation handlers
- Menu bar integration

## Required Features
- Native .app window via PyObjC
- Search box with live result list
- Column sorting, open file, reveal in Finder
- Basic menu bar integration

## Next Steps
- Set up PyObjC environment
- Implement UI components
- Connect UI to existing search functionality
- Create file operation handlers
```

### Execution Prompt: Phase 2 Implementation
```
I need you to implement the native macOS UI for Panoptikon using PyObjC, creating a proper desktop application.

First, read the project status documents:
read_file docs/phase1_verification.md

Then, implement the following components:

1. Application Framework:
   - Create app delegate (src/panoptikon/ui/app.py) for application lifecycle
   - Implement window controller (src/panoptikon/ui/window.py) for main window
   - Add view controller structure (src/panoptikon/ui/viewcontroller.py)
   - Set up PyObjC integration with the existing Python code

2. UI Components:
   - Create search field (src/panoptikon/ui/components/search_field.py) for input
   - Implement results table (src/panoptikon/ui/components/results_table.py) for displaying files
   - Add column headers and sorting (src/panoptikon/ui/components/table_header.py)
   - Create file preview (src/panoptikon/ui/components/preview.py) if possible

3. File Operations:
   - Implement open file functionality (src/panoptikon/ui/operations/open.py)
   - Add reveal in Finder (src/panoptikon/ui/operations/reveal.py)
   - Create context menu (src/panoptikon/ui/components/context_menu.py)
   - Implement drag and drop support if time permits

4. Menu Bar Integration:
   - Create status item (src/panoptikon/ui/menubar.py) for menu bar
   - Implement menu with common actions
   - Add application menu with standard macOS items

For each component:
1. Follow the project quality standards
2. Properly document all Objective-C interop
3. Handle memory management correctly
4. Maintain separation between UI and core logic

After implementation, create a detailed implementation log at 'docs/phase2_implementation.md' that includes:
1. Description of all implemented UI components
2. Explanation of PyObjC integration methods
3. Memory management approach
4. Known limitations or future improvements
5. Screenshots or descriptions of the UI

This document is CRITICAL for continuity as it will be used in subsequent tasks.
```

### Verification Prompt: Phase 2 Verification
```
I need you to verify the Phase 2 Native macOS UI implementation of the Panoptikon project.

First, read the implementation documentation:
read_file docs/phase2_implementation.md

Then, perform these verification steps:

1. UI Functionality Verification:
   - Test application launch and window display
   - Verify search field works with as-you-type results
   - Test results table sorting and selection
   - Check file operations (open, reveal in Finder)
   - Test menu bar integration

2. Code Quality Verification:
   - Run all linters and check for any violations
   - Verify type annotations are complete
   - Check docstring coverage
   - Confirm PyObjC integration follows best practices

3. Memory Management:
   - Check for proper release patterns in PyObjC code
   - Test for memory leaks during UI operations
   - Verify resource cleanup on window/app close

4. Performance Validation:
   - Test UI responsiveness during search
   - Verify scrolling performance with large result sets
   - Check startup time

Create a verification report at 'docs/phase2_verification.md' that includes:
1. Results of all verification steps
2. UI functionality assessment
3. Performance metrics
4. Any issues or limitations found
5. Recommendations for Phase 3
6. Confirmation that Phase 2 is complete

This verification document is CRITICAL for continuity and will be used to begin Phase 3.
```

### Transition Document: Phase 3 Preparation
```markdown
# Transition to Phase 3: Cloud Integration

## Phase 2 Completion Status
- PyObjC application framework implemented ✓
- UI components completed ✓
- File operations working ✓
- Menu bar integration completed ✓

## Phase 3 Objectives
- Implement cloud storage integration
- Add cloud-aware metadata
- Create advanced search syntax
- Support live file system updates

## Required Components
- Cloud provider detection module
- Download status tracking
- Extended search filters for cloud
- File system change monitoring

## Development Guidelines
- Maintain UI responsiveness with cloud operations
- Handle provider-specific peculiarities
- Document limitations with each cloud provider
- Gracefully handle disconnected cloud storage
```

## Phase 3: Cloud Integration

### Status Document: `phase3_status.md`
```markdown
# Panoptikon Project Status: Phase 3 (Cloud Integration)

## Current Phase
- Implementing cloud storage integration

## Components to Implement
- Cloud provider detection
- Download status tracking
- Extended search syntax for cloud
- Live file system updates

## Required Features
- Cloud storage status detection
- cloud: and status: filters
- Incremental index updates
- Saved searches

## Next Steps
- Develop provider detection system
- Implement status tracking
- Extend search syntax
- Create monitoring system for file changes
```

### Execution Prompt: Phase 3 Implementation
```
I need you to implement the cloud storage integration for Panoptikon, adding support for cloud providers and extended search capabilities.

First, read the project status:
read_file docs/phase2_verification.md

Then, implement the following components:

1. Cloud Provider Detection:
   - Create provider detector (src/panoptikon/cloud/detector.py) for identifying cloud storage
   - Implement provider registry (src/panoptikon/cloud/registry.py) for managing providers
   - Add provider-specific implementations for:
     * iCloud (src/panoptikon/cloud/providers/icloud.py)
     * Dropbox (src/panoptikon/cloud/providers/dropbox.py)
     * Google Drive (src/panoptikon/cloud/providers/gdrive.py)
     * OneDrive (src/panoptikon/cloud/providers/onedrive.py)
     * Box (src/panoptikon/cloud/providers/box.py)

2. Status Tracking:
   - Implement status tracker (src/panoptikon/cloud/status.py) for download status
   - Create status cache (src/panoptikon/cloud/cache.py) for performance
   - Add status change monitoring (src/panoptikon/cloud/monitor.py)

3. Extended Search:
   - Extend query parser (src/panoptikon/search/parser.py) for cloud syntax
   - Add cloud filters (src/panoptikon/search/filters.py) for provider/status
   - Implement UI updates for cloud status display (src/panoptikon/ui/components/cloud_status.py)

4. Live Updates:
   - Create file system monitor (src/panoptikon/index/monitor.py) for changes
   - Implement incremental indexing (src/panoptikon/index/incremental.py)
   - Add event system for UI updates (src/panoptikon/utils/events.py)

5. Saved Searches:
   - Implement saved search storage (src/panoptikon/search/saved.py)
   - Add UI for saved searches (src/panoptikon/ui/components/saved_searches.py)

For each component:
1. Follow the project quality standards
2. Write comprehensive tests for cloud functionality
3. Document provider-specific limitations
4. Handle error cases gracefully

After implementation, create a detailed implementation log at 'docs/phase3_implementation.md' that includes:
1. Description of all implemented cloud components
2. Provider detection methods
3. Status tracking approach
4. Extended search syntax documentation
5. Known limitations with each provider

This document is CRITICAL for continuity as it will be used in subsequent tasks.
```

### Verification Prompt: Phase 3 Verification
```
I need you to verify the Phase 3 Cloud Integration implementation of the Panoptikon project.

First, read the implementation documentation:
read_file docs/phase3_implementation.md

Then, perform these verification steps:

1. Cloud Provider Detection:
   - Test detection of each supported cloud provider
   - Verify correct identification of nested providers
   - Check performance of detection algorithms

2. Status Tracking:
   - Verify correct identification of download status
   - Test status change detection
   - Check caching mechanisms

3. Extended Search:
   - Test cloud: filter syntax
   - Test status: filter syntax
   - Verify combined filters work correctly
   - Check performance impact of cloud filtering

4. Live Updates:
   - Test detection of file system changes
   - Verify incremental indexing works correctly
   - Check UI updates when files change

5. Saved Searches:
   - Test saving and loading searches
   - Verify persistence across application restarts

Create a verification report at 'docs/phase3_verification.md' that includes:
1. Results of all verification steps
2. Provider-specific test results
3. Performance metrics for cloud operations
4. Any issues or limitations found
5. Recommendations for Phase 4
6. Confirmation that Phase 3 is complete

This verification document is CRITICAL for continuity and will be used to begin Phase 4.
```

### Transition Document: Phase 4 Preparation
```markdown
# Transition to Phase 4: Finalization and Distribution

## Phase 3 Completion Status
- Cloud provider detection implemented ✓
- Status tracking working ✓
- Extended search syntax completed ✓
- Live updates functioning ✓
- Saved searches implemented ✓

## Phase 4 Objectives
- Finalize application for distribution
- Implement code signing and notarization
- Add auto-update support
- Perform final UX and accessibility pass

## Required Components
- Application bundling system
- Code signing script
- Update mechanism
- Accessibility improvements

## Development Guidelines
- Follow Apple guidelines for distribution
- Ensure proper entitlements for file access
- Document the release process
- Create comprehensive user documentation
```

## Phase 4: Finalization and Distribution

### Status Document: `phase4_status.md`
```markdown
# Panoptikon Project Status: Phase 4 (Finalization)

## Current Phase
- Finalizing the application for distribution

## Components to Implement
- Application packaging
- Code signing and notarization
- Auto-update system
- Final UX improvements

## Required Features
- Signed .app bundle
- Distribution-ready build scripts
- User documentation
- Accessibility compliance

## Next Steps
- Create packaging infrastructure
- Implement signing process
- Add update mechanism
- Complete user documentation
```

### Execution Prompt: Phase 4 Implementation
```
I need you to finalize the Panoptikon application for distribution, implementing packaging, signing, and update capabilities.

First, read the project status:
read_file docs/phase3_verification.md

Then, implement the following components:

1. Application Packaging:
   - Create app bundling script (scripts/bundle_app.py) for .app creation
   - Implement resource management (src/panoptikon/utils/resources.py)
   - Add Icon and asset bundling (assets/*)
   - Create DMG builder (scripts/create_dmg.py) for distribution

2. Code Signing:
   - Implement signing script (scripts/sign_app.py)
   - Create entitlements file (scripts/entitlements.plist)
   - Add notarization support (scripts/notarize_app.py)
   - Document the entire signing process

3. Update System:
   - Create update checker (src/panoptikon/utils/updater.py)
   - Implement update downloader (src/panoptikon/utils/download.py)
   - Add update UI (src/panoptikon/ui/components/update_dialog.py)
   - Create update packaging script (scripts/package_update.py)

4. Final UX Improvements:
   - Implement dark mode support if not already done
   - Add accessibility labels (src/panoptikon/ui/accessibility.py)
   - Create keyboard shortcut system (src/panoptikon/ui/shortcuts.py)
   - Finalize preferences UI (src/panoptikon/ui/preferences.py)

5. Documentation:
   - Create user manual (docs/user/manual.md)
   - Add quick start guide (docs/user/quickstart.md)
   - Create search syntax reference (docs/user/search_syntax.md)
   - Write developer documentation (docs/dev/*)

For each component:
1. Follow the project quality standards
2. Document all distribution processes clearly
3. Test on multiple macOS versions if possible
4. Ensure security best practices are followed

After implementation, create a detailed implementation log at 'docs/phase4_implementation.md' that includes:
1. Description of all distribution components
2. Signing and notarization process
3. Update mechanism details
4. Accessibility improvements
5. Documentation overview

This document is CRITICAL for continuity as it will be used in subsequent tasks.
```

### Verification Prompt: Phase 4 Verification
```
I need you to verify the Phase 4 Finalization implementation of the Panoptikon project.

First, read the implementation documentation:
read_file docs/phase4_implementation.md

Then, perform these verification steps:

1. Application Packaging:
   - Test bundle creation process
   - Verify all resources are correctly included
   - Check DMG building and mounting
   - Verify application launches from DMG

2. Code Signing:
   - Verify signing process works correctly
   - Test notarization workflow
   - Check entitlements are properly applied
   - Verify Gatekeeper allows the application to run

3. Update System:
   - Test update checking mechanism
   - Verify update download and installation
   - Check UI for update notifications
   - Test rollback if possible

4. UX and Accessibility:
   - Test dark mode support
   - Verify accessibility features
   - Check keyboard shortcuts
   - Test preferences system

5. Documentation:
   - Review all user documentation
   - Verify search syntax documentation is complete
   - Check developer documentation

Create a final verification report at 'docs/final_verification.md' that includes:
1. Results of all verification steps
2. Packaging and distribution assessment
3. User experience evaluation
4. Documentation quality review
5. Any final issues or recommendations
6. Confirmation that the project is complete

This verification document represents the final state of the project and confirms readiness for distribution.
```

## Complete Project Documentation

### Final Status Document: `project_complete.md`
```markdown
# Panoptikon Project: Completion Report

## Project Status
- All phases completed successfully
- Application ready for distribution

## Implemented Features
- Fast file search with <200ms response time
- Recursive file indexing
- Cloud storage integration
- Native macOS UI
- Advanced search syntax
- Code signing and distribution

## Project Structure
- Core search engine
- File indexing system
- Database module
- Cloud integration
- PyObjC UI
- Distribution tooling

## Documentation
- User manual and quick start guide
- Developer documentation
- Architecture overview
- Search syntax reference

## Distribution
- Signed and notarized .app bundle
- DMG installer
- Update mechanism

## Future Improvements
- Additional cloud providers
- Windows/Linux versions
- Search result previews
- Extended metadata indexing

The Panoptikon project has been successfully completed according to all requirements and specifications.
```
