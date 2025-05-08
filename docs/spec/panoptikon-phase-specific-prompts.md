# Panoptikon Phase-Specific Prompt Engineering Guide

## Introduction

This guide provides detailed, phase-specific prompt engineering strategies for implementing Panoptikon with Cursor AI and Claude 3.7 Sonnet. Each phase has unique requirements and challenges that necessitate tailored prompting approaches.

## Phase 0: Project Bootstrapping

### Critical Focus Areas
- Project structure establishment
- Quality tooling configuration
- Development environment setup
- Modular architecture foundation

### Prompt Engineering Strategy

#### 1. Project Structure Prompt

```
I need to establish the directory structure for the Panoptikon file search application following the architecture blueprint.

Please create:

1. A detailed directory structure that includes:
   - All major modules and submodules
   - Package structure following Python best practices
   - Test directory structure mirroring the main package
   - Documentation organization
   - Configuration files location

2. For each directory, include:
   - Purpose and responsibility
   - Key files to be included
   - Relationships to other directories

3. Create initialization files:
   - Root __init__.py files
   - Package metadata
   - Version information
   - Import structures

The structure should follow these architectural principles:
- Clear separation of concerns
- Single responsibility for each module
- Explicit dependencies
- No circular dependencies
- Testability by design

After generating the structure, please:
1. Explain the rationale for key design decisions
2. Highlight any trade-offs made
3. Provide recommendations for future extensibility
```

#### 2. Quality Configuration Prompt

```
I need to configure quality tools for the Panoptikon project to ensure high code quality from day one.

Please create configuration files for:

1. Linting:
   - ruff configuration in pyproject.toml
   - flake8 configuration (.flake8)
   - pylint configuration (.pylintrc)
   - Configuration should enforce:
     * Maximum line length: 120 characters
     * Docstring requirements
     * Import ordering
     * Naming conventions
     * Complexity limits

2. Formatting:
   - black configuration in pyproject.toml
   - isort configuration in pyproject.toml
   - Ensure consistency between formatters

3. Type checking:
   - mypy configuration in pyproject.toml
   - Strict typing requirements
   - Type checking for tests

4. Testing:
   - pytest configuration (pytest.ini)
   - Coverage settings (.coveragerc)
   - Test discovery rules

5. Pre-commit:
   - .pre-commit-config.yaml for enforcing standards
   - Custom hooks for project-specific checks

For each tool, include:
- Explanation of chosen settings
- Rationale for configuration choices
- How the tool contributes to overall quality

All configurations should work together harmoniously and enforce our quality standards:
- 95%+ docstring coverage
- 80%+ test coverage
- Maximum function length of 50 lines
- Maximum file length of 500 lines
- Maximum cyclomatic complexity of 10
```

#### 3. Test Framework Prompt

```
I need to set up the testing framework for the Panoptikon project with a focus on comprehensive test coverage and quality validation.

Please create:

1. Core test infrastructure:
   - Base test classes
   - Common fixtures
   - Test utilities
   - Mocking helpers
   - Parameterization patterns

2. Test organization:
   - Unit test structure
   - Integration test approach
   - Performance test framework
   - UI test infrastructure (for later phases)

3. Test configuration:
   - pytest configuration
   - Coverage reporting
   - Test discovery
   - Plugin configuration

4. Test documentation:
   - Test writing guidelines
   - Test naming conventions
   - Documentation requirements
   - Example tests for reference

The test framework should support:
- Test-driven development
- High coverage metrics
- Performance validation
- Edge case testing
- Mock-based isolation

For each component, include documentation on:
- How to use the component
- Best practices for writing tests
- Examples of good tests
- Common pitfalls to avoid
```

#### 4. Development Environment Prompt

```
I need to configure the development environment for the Panoptikon project, optimized for Cursor AI usage.

Please create:

1. Dependency management:
   - pyproject.toml with Poetry configuration
   - Development dependencies
   - Production dependencies
   - Version constraints
   - Optional dependencies

2. Cursor AI configuration:
   - .cursor/settings.json
   - Editor configuration
   - Linting integration
   - Formatting on save
   - Context prompts for quality

3. Virtual environment:
   - Environment setup instructions
   - Environment activation scripts
   - Python version requirements
   - Package installation commands

4. Development scripts:
   - Script for running tests
   - Script for checking quality
   - Script for building the application
   - Script for code generation

5. Documentation:
   - README.md with setup instructions
   - CONTRIBUTING.md with development guidelines
   - Development environment documentation
   - Workflow documentation

The environment should prioritize:
- Consistency across developers
- Automation of quality checks
- Easy setup and onboarding
- Integration with Cursor AI
- Reproducible builds
```

### Quality Verification Approach

After bootstrapping, verify with this prompt:

```
I need to verify the project bootstrapping implementation for Panoptikon.

Please check:

1. Project structure:
   - Verify all directories exist
   - Check package initialization
   - Confirm module organization
   - Test directory structure

2. Quality tools:
   - Test each linter with sample files
   - Verify formatter consistency
   - Check type checking configuration
   - Test pre-commit hooks

3. Test framework:
   - Run sample tests
   - Verify coverage reporting
   - Test fixture functionality
   - Check parameterization

4. Development environment:
   - Verify dependency installation
   - Test build process
   - Check Cursor AI integration
   - Validate script functionality

For each area, document:
- Verification results
- Any issues found
- Recommended fixes
- Confirmation of readiness

Create a verification report that can be used to begin Phase 1.
```

## Phase 1: MVP Backend

### Critical Focus Areas
- File indexing system
- Database schema and operations
- Search engine core
- Basic command-line interface

### Prompt Engineering Strategy

#### 1. File Crawler Component Prompt

```
I need to implement the file crawler component for Panoptikon, which is responsible for recursively traversing the file system to discover files for indexing.

Current project context:
The project structure and quality tools are set up. We're now implementing the core MVP functionality, starting with the file indexing system.

Please implement src/panoptikon/index/crawler.py that:

1. Core functionality:
   - Recursively traverses directories
   - Respects inclusion/exclusion patterns
   - Handles file system permissions gracefully
   - Supports throttling to limit system impact
   - Provides progress feedback
   - Handles cancellation
   - Uses pathlib for file system operations

2. API design:
   - Implements a FileCrawler class
   - Provides iterator/generator pattern for results
   - Clear method signatures with type hints
   - Comprehensive docstrings
   - Error handling strategy

3. Optimization considerations:
   - Memory-efficient traversal
   - Batch processing where appropriate
   - Configurable throttling

4. Tests (tests/test_index/test_crawler.py):
   - Test directory traversal logic
   - Test pattern matching
   - Test error handling
   - Test cancellation
   - Test progress reporting
   - Mock file system for isolation

Quality requirements:
- Complete Google-style docstrings
- Type hints for all functions and methods
- No function longer than 50 lines
- Error handling for all file operations
- 90%+ test coverage
- No direct use of os.path (use pathlib)

Related components:
- Will be used by the Indexer component
- Will work with the Exclusion component for pattern matching
- Will feed the Metadata component for extracting file information

After implementation, please:
1. Run linters and formatters
2. Run the tests
3. Document any design decisions or trade-offs
```

#### 2. Database Schema Prompt

```
I need to implement the database schema for Panoptikon, which will store file metadata and support fast searching.

Current project context:
We've implemented the file crawler component and now need to design and implement the database schema for storing the indexed file information.

Please implement src/panoptikon/db/schema.py that:

1. Core functionality:
   - Defines SQLite database schema
   - Creates tables for files, directories, and metadata
   - Implements proper indexing for search performance
   - Supports schema versioning and migrations
   - Handles large datasets efficiently

2. Schema design:
   - Files table with metadata columns
   - Directories table for inclusion/exclusion
   - Metadata table for extended attributes
   - Configuration table for settings
   - Search history table
   - Appropriate constraints and relationships

3. Implementation details:
   - Use SQLAlchemy Core for schema definition
   - Implement CREATE and migration scripts
   - Add version tracking
   - Include index creation
   - Document schema design decisions

4. Tests (tests/test_db/test_schema.py):
   - Test schema creation
   - Test migrations
   - Test data integrity constraints
   - Test performance with sample data
   - Test edge cases

Quality requirements:
- Full documentation of schema design
- Type hints for all functions
- Comprehensive docstrings
- Performance annotations for critical operations
- Complete test coverage
- Clear separation of concerns

Related components:
- Will be used by Database Operations module
- Will store data from the Indexer
- Will be queried by the Search Engine

After implementation, please:
1. Validate the schema design against search requirements
2. Run tests to verify functionality
3. Document optimization opportunities
4. Explain the indexing strategy
```

#### 3. Search Engine Core Prompt

```
I need to implement the core search engine for Panoptikon that will efficiently execute search queries against the database.

Current project context:
We've implemented the file crawler and database schema. Now we need to create the search engine that will provide fast search capabilities.

Please implement src/panoptikon/search/engine.py that:

1. Core functionality:
   - Execute search queries against the database
   - Parse search terms and filters
   - Implement relevance ranking
   - Support incremental results
   - Provide cancellation capability
   - Handle errors gracefully

2. Implementation details:
   - Clean separation between parsing and execution
   - Efficient SQL query generation
   - Proper parameter binding for security
   - Resource management
   - Performance monitoring
   - Results pagination

3. API design:
   - SearchEngine class with clear interface
   - Support for synchronous and asynchronous operations
   - Progress reporting callbacks
   - Well-defined result objects
   - Error handling strategy

4. Tests (tests/test_search/test_engine.py):
   - Test basic search functionality
   - Test advanced query features
   - Test performance with large datasets
   - Test error handling
   - Test cancellation
   - Test with mock database

Quality requirements:
- Performance optimizations for sub-200ms searches
- Complete documentation of public APIs
- Type hints for all functions
- Memory efficiency for large result sets
- Comprehensive error handling
- 90%+ test coverage

Related components:
- Will use the Database module
- Will be used by the CLI interface
- Will later integrate with the UI

After implementation, please:
1. Run performance tests to verify speed
2. Document the query execution pipeline
3. Explain ranking algorithm
4. Describe future optimization opportunities
```

#### 4. CLI Interface Prompt

```
I need to implement a command-line interface for Panoptikon to test the core functionality.

Current project context:
We've implemented the file crawler, database, and search engine components. Now we need a simple CLI to test and validate these components.

Please implement src/panoptikon/cli/interface.py that:

1. Core functionality:
   - Provide a command-line interface to Panoptikon
   - Support indexing commands
   - Implement search functionality
   - Display results in a readable format
   - Handle command-line arguments
   - Provide help and documentation

2. Implementation details:
   - Use argparse for command-line parsing
   - Implement subcommands for different functions
   - Pretty-print search results
   - Show indexing progress
   - Provide error messages
   - Support verbose/debug output

3. Commands to implement:
   - index: Start indexing directories
   - search: Search for files
   - status: Show indexing status
   - config: Configure settings
   - version: Show version information
   - help: Show help text

4. Tests (tests/test_cli/test_interface.py):
   - Test command parsing
   - Test output formatting
   - Test error handling
   - Test integration with core components
   - Test with mock components

Quality requirements:
- Clean, user-friendly interface
- Comprehensive help text
- Proper error handling
- Type hints for all functions
- Thorough docstrings
- 90%+ test coverage

Related components:
- Will use the Indexer component
- Will use the Search Engine component
- Will use the Configuration component

After implementation, please:
1. Test the CLI with sample commands
2. Document the command syntax
3. Provide usage examples
4. Explain design decisions
```

### Phase 1 Verification Prompt

```
I need to verify the Phase 1 MVP implementation of Panoptikon.

Please perform a comprehensive verification:

1. Component verification:
   - File Crawler: Test crawling different directory structures
   - Database Schema: Verify table creation and indexing
   - Search Engine: Test search performance and accuracy
   - CLI Interface: Test command functionality

2. Integration testing:
   - Test the end-to-end flow from crawling to searching
   - Verify data consistency between components
   - Check error propagation
   - Test resource cleanup

3. Performance validation:
   - Measure crawling speed (files/second)
   - Test search response time
   - Check memory usage during operation
   - Verify database size relative to indexed data

4. Quality assessment:
   - Run linters on all code
   - Check test coverage
   - Verify documentation completeness
   - Review error handling

5. User experience:
   - Test CLI usability
   - Check output formatting
   - Verify help text and documentation
   - Test with realistic user scenarios

Create a detailed verification report that includes:
- Status of each component
- Performance metrics
- Quality metrics
- Any issues or limitations found
- Recommendations for improvements
- Readiness assessment for Phase 2

This report will be critical for the transition to Phase 2.
```

## Phase 2: Native macOS UI

### Critical Focus Areas
- PyObjC integration
- Window and UI components
- MVVM architecture
- File operations

### Prompt Engineering Strategy

#### 1. UI Architecture Prompt

```
I need to design and implement the UI architecture for Panoptikon using PyObjC, establishing the foundation for the native macOS interface.

Current project context:
We've completed the core backend functionality in Phase 1 and now need to create a native macOS UI using PyObjC.

Please implement src/panoptikon/ui/architecture.py that:

1. Core functionality:
   - Define the UI architecture (MVVM pattern)
   - Create base classes for view models and views
   - Implement binding mechanisms
   - Handle PyObjC integration
   - Manage memory properly
   - Support UI updates from background threads

2. Implementation details:
   - Clear separation between models, view models, and views
   - Reactive binding pattern for updates
   - Property observation mechanisms
   - Threading and dispatch queue handling
   - Memory management patterns for Objective-C interop
   - Event handling system

3. API design:
   - Base view model class
   - Base view controller class
   - Binding utilities
   - Threading utilities
   - Memory management utilities
   - Documentation for extension

4. Tests (tests/test_ui/test_architecture.py):
   - Test binding mechanisms
   - Test update propagation
   - Test memory management
   - Test threading behavior
   - Test with mock components

Quality requirements:
- Comprehensive documentation of PyObjC patterns
- Clear memory management guidelines
- Type hints for all functions
- Docstrings with PyObjC-specific notes
- Test coverage of core functionality
- Clean separation of concerns

Related components:
- Will be used by all UI components
- Will connect to backend components
- Will provide structure for the entire UI

After implementation, please:
1. Document the architecture pattern
2. Explain memory management approach
3. Provide usage examples
4. Describe best practices for extending
```

#### 2. Window Controller Prompt

```
I need to implement the main window controller for Panoptikon using PyObjC, which will serve as the primary container for the application UI.

Current project context:
We've established the UI architecture using MVVM and now need to implement the main application window.

Please implement src/panoptikon/ui/window.py that:

1. Core functionality:
   - Create main application window
   - Implement NSWindowController subclass
   - Handle window lifecycle events
   - Manage view hierarchy
   - Support layout and resizing
   - Implement window persistence

2. Implementation details:
   - Proper initialization from NIB/XIB or programmatically
   - Delegate pattern implementation
   - View controller management
   - Window positioning and sizing
   - State restoration
   - Toolbar integration

3. UI components:
   - Main content view
   - Toolbar configuration
   - Status display area
   - Search field integration
   - Results view container
   - Split view support

4. Tests (tests/test_ui/test_window.py):
   - Test window creation
   - Test lifecycle events
   - Test view management
   - Test state persistence
   - Test with mock components

Quality requirements:
- Clear documentation of PyObjC patterns
- Memory management explicitly handled
- Type hints for all functions
- Comprehensive docstrings
- Separation between UI and business logic
- Follow macOS Human Interface Guidelines

Related components:
- Will use the UI Architecture
- Will contain Search Components
- Will contain Results View
- Will integrate with Menu Bar

After implementation, please:
1. Document window management approach
2. Explain view hierarchy
3. Describe lifecycle management
4. Provide usage examples
```

#### 3. Search Interface Prompt

```
I need to implement the search interface components for Panoptikon using PyObjC, which will provide the main user interaction point for searches.

Current project context:
We've implemented the window controller and now need to create the search interface components.

Please implement:

1. Search Field (src/panoptikon/ui/components/search_field.py):
   - Implement NSSearchField wrapper
   - Support as-you-type searching
   - Handle search history
   - Implement keyboard shortcuts
   - Provide clear button
   - Support focus management

2. Results List (src/panoptikon/ui/components/results_list.py):
   - Implement NSTableView wrapper
   - Support virtual scrolling for large results
   - Implement column management
   - Handle selection
   - Support sorting
   - Provide custom cell views

3. Search View Model (src/panoptikon/ui/viewmodels/search_vm.py):
   - Implement search state management
   - Handle query execution
   - Manage results
   - Implement history tracking
   - Provide filtering capabilities
   - Support asynchronous operations

4. Tests for each component:
   - Test component initialization
   - Test interaction handling
   - Test data binding
   - Test with mock data
   - Test performance with large datasets

Quality requirements:
- Responsive UI (sub-200ms feedback)
- Memory management for PyObjC
- Clear separation of UI and business logic
- Comprehensive documentation
- Type hints for all functions
- Test coverage of core functionality

Related components:
- Will use the UI Architecture
- Will use the Search Engine
- Will integrate with Window Controller
- Will connect to File Operations

For each component, please:
1. Document PyObjC integration points
2. Explain memory management approach
3. Describe the user interaction model
4. Provide examples of extension
```

#### 4. File Operations Prompt

```
I need to implement the file operations components for Panoptikon using PyObjC, which will handle file actions like opening, revealing in Finder, and drag-and-drop.

Current project context:
We've implemented the search interface components and now need to add file operation capabilities.

Please implement:

1. File Operations Manager (src/panoptikon/ui/operations.py):
   - Implement file opening with default applications
   - Add "Reveal in Finder" functionality
   - Handle multiple file selection
   - Manage file operation permissions
   - Provide operation feedback
   - Handle errors gracefully

2. Context Menu (src/panoptikon/ui/components/context_menu.py):
   - Create NSMenu for context operations
   - Implement menu item validation
   - Support dynamic menu generation
   - Handle keyboard shortcuts
   - Provide icons for operations
   - Support standard and custom operations

3. Drag and Drop (src/panoptikon/ui/components/drag_drop.py):
   - Implement drag source from results list
   - Handle pasteboard operations
   - Provide drag feedback
   - Support file and URL dragging
   - Manage drag images
   - Handle drop validation

4. Tests for each component:
   - Test file operations
   - Test menu generation and validation
   - Test drag and drop functionality
   - Test with mock components
   - Test error handling

Quality requirements:
- Follow macOS Human Interface Guidelines
- Proper memory management for PyObjC
- Comprehensive documentation
- Type hints for all functions
- Test coverage of core functionality
- Security considerations for file operations

Related components:
- Will use the UI Architecture
- Will integrate with Search Results
- Will use filesystem utilities
- Will connect to the Window Controller

For each component, please:
1. Document security considerations
2. Explain interaction with macOS APIs
3. Describe error handling strategy
4. Provide examples of extension
```

### Phase 2 Verification Prompt

```
I need to verify the Phase 2 Native UI implementation of Panoptikon.

Please perform a comprehensive verification:

1. UI architecture verification:
   - Test MVVM pattern implementation
   - Verify binding mechanisms
   - Check memory management
   - Test with different view models

2. Component testing:
   - Window Controller: Test lifecycle and management
   - Search Field: Verify as-you-type functionality
   - Results List: Test with large datasets
   - File Operations: Verify security and functionality

3. Integration testing:
   - Test end-to-end flows from search to file operations
   - Verify UI updates from background operations
   - Check error presentation
   - Test memory management across components

4. User experience testing:
   - Verify responsiveness (sub-200ms)
   - Check UI consistency with macOS
   - Test keyboard navigation
   - Verify accessibility features

5. Quality assessment:
   - Run linters on all code
   - Check test coverage
   - Verify documentation completeness
   - Review memory management

Create a detailed verification report that includes:
- Status of each UI component
- Performance metrics
- User experience assessment
- Memory management evaluation
- Any issues or limitations found
- Recommendations for improvements
- Readiness assessment for Phase 3

This report will be critical for the transition to Phase 3.
```

## Phase 3: Cloud Integration

### Critical Focus Areas
- Cloud provider detection
- Status tracking
- Advanced search syntax
- UI updates for cloud features

### Prompt Engineering Strategy

#### 1. Cloud Provider Detection Prompt

```
I need to implement the cloud provider detection system for Panoptikon, which will identify various cloud storage providers and their locations.

Current project context:
We've completed the native UI implementation and now need to add cloud storage integration, starting with provider detection.

Please implement:

1. Provider Detector (src/panoptikon/cloud/detector.py):
   - Identify cloud storage locations
   - Support major providers (iCloud, Dropbox, Google Drive, OneDrive, Box)
   - Use path patterns and markers
   - Implement caching for performance
   - Handle nested providers
   - Support provider-specific detection logic

2. Provider Registry (src/panoptikon/cloud/registry.py):
   - Manage provider implementations
   - Support dynamic registration
   - Provide provider discovery
   - Handle provider configuration
   - Implement factory pattern
   - Support versioning

3. Provider Base (src/panoptikon/cloud/provider_base.py):
   - Define common provider interface
   - Implement shared functionality
   - Provide extension points
   - Document required methods
   - Handle errors consistently
   - Support configuration

4. Tests for each component:
   - Test provider detection
   - Test registry functionality
   - Test with mock file systems
   - Test performance
   - Test error handling

Quality requirements:
- Efficient detection algorithms
- Clear provider abstraction
- Comprehensive documentation
- Type hints for all functions
- Test coverage of core functionality
- Extensibility for new providers

Related components:
- Will be used by the Indexer
- Will connect to Status Tracker
- Will be used by Search Filters
- Will integrate with UI

For each component, please:
1. Document detection algorithms
2. Explain provider abstraction
3. Describe extension points
4. Provide examples of adding new providers
```

#### 2. Cloud Status Tracking Prompt

```
I need to implement the cloud status tracking system for Panoptikon, which will monitor the download status of cloud files.

Current project context:
We've implemented the cloud provider detection system and now need to add status tracking.

Please implement:

1. Status Tracker (src/panoptikon/cloud/status.py):
   - Track download status of cloud files
   - Support major providers
   - Use provider-specific APIs where available
   - Implement heuristics for unknown providers
   - Cache status information
   - Handle status changes

2. Status Monitor (src/panoptikon/cloud/monitor.py):
   - Watch for status changes
   - Implement efficient monitoring
   - Use provider-specific monitoring APIs
   - Minimize resource usage
   - Support enabling/disabling
   - Provide change notifications

3. Status Cache (src/panoptikon/cloud/cache.py):
   - Store status information
   - Implement efficient caching
   - Support invalidation
   - Manage cache size
   - Persist cache between sessions
   - Provide statistics

4. Tests for each component:
   - Test status detection
   - Test monitoring functionality
   - Test cache operations
   - Test with mock providers
   - Test error handling

Quality requirements:
- Efficient status algorithms
- Minimal resource usage
   - Memory efficient caching
   - CPU efficient monitoring
- Comprehensive documentation
- Type hints for all functions
- Test coverage of core functionality
- Graceful degradation when APIs unavailable

Related components:
- Will use Provider Detection
- Will integrate with Indexer
- Will be used by Search Filters
- Will connect to UI

For each component, please:
1. Document status detection methods
2. Explain monitoring strategy
3. Describe caching approach
4. Provide performance characteristics
```

#### 3. Advanced Search Syntax Prompt

```
I need to extend the search engine to support advanced cloud-aware syntax in Panoptikon, allowing users to search and filter by cloud providers and status.

Current project context:
We've implemented cloud provider detection and status tracking, and now need to integrate this with the search functionality.

Please implement:

1. Cloud Filters (src/panoptikon/search/cloud_filter.py):
   - Implement cloud-specific filters
   - Support provider filtering (cloud:dropbox)
   - Add status filtering (status:downloaded)
   - Integrate with existing filter system
   - Generate optimized SQL
   - Support combining with other filters

2. Extended Parser (src/panoptikon/search/parser.py updates):
   - Extend query parser for cloud syntax
   - Add cloud-specific token recognition
   - Implement parser rules for cloud queries
   - Support operator combinations
   - Maintain backwards compatibility
   - Document syntax extensions

3. Cloud Search Extensions (src/panoptikon/search/extensions/cloud.py):
   - Implement plugin architecture for search
   - Add cloud-specific search capabilities
   - Provide cloud-aware sorting
   - Support cloud metadata in results
   - Optimize cloud-specific queries
   - Extend search result objects

4. Tests for each component:
   - Test cloud filters
   - Test parser extensions
   - Test search functionality
   - Test with mock cloud data
   - Test performance

Quality requirements:
- Maintain search performance (<200ms)
- Clear syntax documentation
- Comprehensive error handling
- Type hints for all functions
- Test coverage of core functionality
- Backward compatibility

Related components:
- Will extend Search Engine
- Will use Cloud Provider Detection
- Will use Status Tracking
- Will connect to UI

For each component, please:
1. Document syntax extensions
2. Explain filter implementation
3. Describe performance optimizations
4. Provide examples of cloud queries
```

#### 4. Cloud UI Integration Prompt

```
I need to implement UI components for cloud integration in Panoptikon, allowing users to see and interact with cloud storage features.

Current project context:
We've implemented the backend cloud functionality and now need to update the UI to support cloud features.

Please implement:

1. Cloud Status UI (src/panoptikon/ui/components/cloud_status.py):
   - Display cloud provider information
   - Show download status
   - Provide visual indicators
   - Support status actions
   - Implement tooltips
   - Handle status updates

2. Cloud Provider Icons (src/panoptikon/ui/components/provider_icons.py):
   - Create icon management system
   - Support provider-specific icons
   - Handle icon loading and caching
   - Support different sizes
   - Implement template images
   - Support dark mode

3. Cloud Preferences Panel (src/panoptikon/ui/preferences/cloud.py):
   - Create cloud settings UI
   - Support provider configuration
   - Implement status tracking options
   - Add cache management
   - Provide provider priority settings
   - Support enabling/disabling providers

4. Tests for each component:
   - Test UI components
   - Test icon management
   - Test preferences functionality
   - Test with mock cloud data
   - Test accessibility

Quality requirements:
- Follow macOS Human Interface Guidelines
- Proper memory management
- Comprehensive documentation
- Type hints for all functions
- Test coverage of core functionality
- Accessibility support

Related components:
- Will use UI Architecture
- Will connect to Cloud Provider Detection
   - Will use Status Tracking
   - Will integrate with Search UI

For each component, please:
1. Document user interaction model
2. Explain visualization approach
3. Describe preference management
4. Provide screenshots or mockups
```

### Phase 3 Verification Prompt

```
I need to verify the Phase 3 Cloud Integration implementation of Panoptikon.

Please perform a comprehensive verification:

1. Cloud provider detection:
   - Test detection of each supported provider
   - Verify correct identification of nested providers
   - Check performance of detection algorithms
   - Test with different directory structures

2. Status tracking:
   - Verify status detection accuracy
   - Test monitoring functionality
   - Check caching efficiency
   - Measure resource usage during monitoring

3. Advanced search:
   - Test cloud filter syntax
   - Verify integration with existing search
   - Check performance with cloud filters
   - Test complex query combinations

4. UI integration:
   - Verify status display
   - Test icon rendering
   - Check preferences functionality
   - Test with mock cloud data

5. Integration testing:
   - Test end-to-end flows with cloud files
   - Verify status updates propagate to UI
   - Check search results with cloud filters
   - Test performance with real-world data

Create a detailed verification report that includes:
- Status of each cloud component
- Performance metrics
- User experience assessment
- Any issues or limitations found
- Recommendations for improvements
- Readiness assessment for Phase 4

This report will be critical for the transition to Phase 4.
```

## Phase 4: Performance Optimization

### Critical Focus Areas
- Search performance
- Indexing speed
- Memory optimization
- UI responsiveness

### Prompt Engineering Strategy

#### 1. Search Optimization Prompt

```
I need to implement search optimizations for Panoptikon to ensure it meets the 200ms response time requirement even with large indexes.

Current project context:
We've completed the cloud integration and now need to optimize performance, starting with search operations.

Please implement:

1. Search Optimizer (src/panoptikon/search/optimizer.py):
   - Analyze query patterns
   - Implement query planning
   - Generate optimized SQL
   - Use appropriate indices
   - Cache frequent searches
   - Support query transformation

2. Index Optimizer (src/panoptikon/db/index_optimizer.py):
   - Analyze database usage
   - Recommend index improvements
   - Create/drop indices dynamically
   - Measure query performance
   - Implement index maintenance
   - Document optimization process

3. Result Cache (src/panoptikon/search/cache.py):
   - Implement LRU caching for search results
   - Support partial result caching
   - Handle cache invalidation
   - Optimize memory usage
   - Provide hit/miss metrics
   - Support configuration

4. Tests for each component:
   - Test optimization algorithms
   - Test with various query patterns
   - Benchmark performance improvements
   - Test with large datasets
   - Verify correctness

Quality requirements:
- Achieve sub-200ms search for common queries
   - Even with 100,000+ files
   - Including complex filters
- Memory-efficient caching
- Comprehensive documentation
- Type hints for all functions
- Performance metrics and logging
- Maintainable optimization code

Related components:
- Will enhance Search Engine
- Will optimize Database
- Will improve UI responsiveness
- Will connect to Indexing System

For each component, please:
1. Document optimization techniques
2. Explain performance measurements
3. Describe tradeoffs made
4. Provide benchmark results
```

#### 2. Indexing Optimization Prompt

```
I need to implement indexing optimizations for Panoptikon to achieve 1000+ files/second indexing rate while minimizing system impact.

Current project context:
We've optimized the search performance and now need to improve indexing speed and efficiency.

Please implement:

1. Indexing Optimizer (src/panoptikon/index/optimizer.py):
   - Implement batch processing
   - Optimize transaction boundaries
   - Use prepared statements
   - Manage memory usage
   - Provide performance metrics
   - Support prioritization

2. Throttling System (src/panoptikon/index/throttle.py):
   - Control indexing speed
   - Adjust based on system load
   - Respect battery status
   - Implement priority queuing
   - Support scheduling
   - Provide configuration options

3. Parallel Processing (src/panoptikon/index/parallel.py):
   - Implement thread pool for indexing
   - Optimize work distribution
   - Ensure thread safety
   - Manage resource contention
   - Handle coordination
   - Support cancelation

4. Tests for each component:
   - Test optimization algorithms
   - Benchmark indexing performance
   - Test throttling behavior
   - Verify parallel processing
   - Test with large directories

Quality requirements:
- Achieve 1000+ files/second on reference hardware
- Minimize system impact during indexing
- Clear documentation of optimization techniques
- Type hints for all functions
- Performance metrics and logging
- Maintainable optimization code

Related components:
- Will enhance Indexing System
- Will optimize Database usage
- Will improve UI responsiveness
- Will connect to File Crawler

For each component, please:
1. Document optimization techniques
2. Explain performance measurements
3. Describe throttling algorithms
4. Provide benchmark results
```

#### 3. Memory Optimization Prompt

```
I need to implement memory optimizations for Panoptikon to reduce overall memory footprint and improve efficiency.

Current project context:
We've optimized search and indexing performance and now need to focus on memory efficiency.

Please implement:

1. Memory Manager (src/panoptikon/utils/memory.py):
   - Implement memory usage tracking
   - Provide memory-efficient data structures
   - Support object pooling
   - Implement resource limits
   - Add memory pressure notifications
   - Optimize garbage collection

2. Data Structure Optimizations (src/panoptikon/utils/data_structures.py):
   - Implement specialized collections
   - Create memory-efficient representations
   - Support lazy loading
   - Implement flyweight pattern
   - Optimize for common operations
   - Provide serialization

3. Cache Manager (src/panoptikon/utils/cache.py):
   - Implement unified caching system
   - Support size-based eviction
   - Add time-based expiration
   - Provide memory-aware caching
   - Implement priority-based eviction
   - Support cache statistics

4. Tests for each component:
   - Test memory usage patterns
   - Benchmark memory improvements
   - Verify functionality
   - Test under memory pressure
   - Measure memory footprint

Quality requirements:
- Reduce memory usage by 30%+ compared to baseline
- Maintain performance while reducing memory
- Clear documentation of optimization techniques
- Type hints for all functions
- Memory usage metrics and logging
- Maintainable optimization code

Related components:
- Will be used throughout the application
- Will enhance search performance
- Will improve indexing efficiency
- Will support UI responsiveness

For each component, please:
1. Document optimization techniques
2. Explain memory usage patterns
3. Describe tradeoffs made
4. Provide benchmark results
```

#### 4. UI Performance Prompt

```
I need to implement UI performance optimizations for Panoptikon to ensure a responsive experience even with large datasets.

Current project context:
We've optimized backend performance and now need to focus on UI responsiveness.

Please implement:

1. UI Virtualization (src/panoptikon/ui/components/virtualization.py):
   - Implement virtual scrolling for large results
   - Support row recycling
   - Optimize rendering pipeline
   - Implement incremental loading
   - Add smooth scrolling
   - Support variable row heights

2. Background Processing (src/panoptikon/ui/background.py):
   - Implement background task management
   - Support progress reporting
   - Add operation cancellation
   - Optimize thread usage
   - Implement priority scheduling
   - Provide UI feedback

3. UI Optimizations (src/panoptikon/ui/optimizations.py):
   - Implement view layer optimizations
   - Reduce redraw cycles
   - Optimize binding updates
   - Implement layer-backed views
   - Add drawing optimizations
   - Support view recycling

4. Tests for each component:
   - Test UI responsiveness
   - Benchmark rendering performance
   - Verify with large datasets
   - Test scrolling behavior
   - Measure memory impact

Quality requirements:
- Maintain 60fps scrolling with 100,000+ items
- Keep UI responsive during operations
- Clear documentation of optimization techniques
- Type hints for all functions
- Performance metrics and logging
- Maintainable optimization code

Related components:
- Will enhance results display
   - Will improve search experience
   - Will optimize view models
   - Will connect to backend optimizations

For each component, please:
1. Document optimization techniques
2. Explain rendering approach
3. Describe threading model
4. Provide benchmark results
```

### Phase 4 Verification Prompt

```
I need to verify the Phase 4 Performance Optimization implementation of Panoptikon.

Please perform a comprehensive verification:

1. Search performance:
   - Measure search response time for various queries
   - Test with 100,000+ files in the index
   - Verify sub-200ms response for typical queries
   - Test complex filters and cloud queries
   - Measure memory usage during search operations

2. Indexing performance:
   - Benchmark indexing speed (files/second)
   - Test with large directory structures
   - Verify 1000+ files/second on reference hardware
   - Measure system impact during indexing
   - Test throttling behavior

3. Memory optimization:
   - Measure memory footprint with large indexes
   - Compare with pre-optimization baseline
   - Test memory pressure handling
   - Verify caching efficiency
   - Measure peak memory usage

4. UI performance:
   - Test scrolling performance with large results
   - Measure UI responsiveness during operations
   - Verify background processing effectiveness
   - Test with real-world data

5. Overall system performance:
   - Measure cold start time
   - Test with realistic usage patterns
   - Verify performance on minimum spec hardware
   - Check resource usage during idle periods

Create a detailed verification report that includes:
- Performance metrics for each area
- Comparison with pre-optimization baseline
- Memory usage statistics
- UI responsiveness measurements
- Any remaining performance issues
- Recommendations for further optimization
- Readiness assessment for Phase 5

This report will be critical for the transition to Phase 5.
```

## Phase 5: Distribution

### Critical Focus Areas
- Application packaging
- Code signing
- Update mechanism
- Documentation

### Prompt Engineering Strategy

#### 1. Application Packaging Prompt

```
I need to implement the application packaging system for Panoptikon to create a distributable macOS application bundle.

Current project context:
We've optimized the application's performance and now need to prepare it for distribution.

Please implement:

1. Bundle Script (scripts/bundle_app.py):
   - Create macOS .app bundle
   - Package all required resources
   - Embed Python environment
   - Handle dependencies
   - Optimize bundle size
   - Set proper permissions and attributes

2. Resource Management (src/panoptikon/utils/resources.py):
   - Implement resource loading from bundle
   - Support localization
   - Handle icon and image resources
   - Implement resource caching
   - Support themes and variants
   - Provide fallback mechanisms

3. Bundle Configuration (src/panoptikon/config/bundle.py):
   - Manage bundle-specific settings
   - Support different distribution channels
   - Handle environment detection
   - Implement feature flags
   - Support build configurations
   - Provide version information

4. Tests for each component:
   - Test bundle creation
   - Verify resource loading
   - Test configuration management
   - Verify with different build settings
   - Test bundle validation

Quality requirements:
- Create professional-quality .app bundle
- Minimize bundle size
- Ensure proper resource loading
- Comprehensive documentation
- Type hints for all functions
- Test coverage of core functionality

Related components:
- Will package the entire application
- Will connect to resource loading
- Will support code signing
- Will prepare for distribution

For each component, please:
1. Document bundling process
2. Explain resource management
3. Describe configuration approach
4. Provide bundle structure details
```

#### 2. Code Signing Prompt

```
I need to implement the code signing system for Panoptikon to ensure the application meets Apple's security requirements.

Current project context:
We've created the application bundle and now need to implement code signing and notarization.

Please implement:

1. Signing Script (scripts/sign_app.py):
   - Implement code signing process
   - Support developer certificates
   - Handle entitlements
   - Verify signature
   - Support different identity selection
   - Document security requirements

2. Notarization System (scripts/notarize_app.py):
   - Implement notarization workflow
   - Handle Apple authentication
   - Support upload and status checking
   - Process ticket stapling
   - Provide progress reporting
   - Handle error recovery

3. Entitlements Management (scripts/entitlements.py):
   - Create entitlements file
   - Support different entitlement profiles
   - Implement capability configuration
   - Document security implications
   - Support hardened runtime
   - Handle permission requests

4. Tests for each component:
   - Test signing process
   - Verify notarization workflow
   - Test entitlements generation
   - Verify signature validation
   - Check error handling

Quality requirements:
- Meet all Apple security requirements
   - Proper code signing
   - Successful notarization
   - Appropriate entitlements
- Comprehensive documentation
- Type hints for all functions
- Secure credential handling
- Clear error reporting

Related components:
- Will work with application bundle
   - Will prepare for distribution
   - Will integrate with update system
   - Will support security features

For each component, please:
1. Document signing process
2. Explain notarization workflow
3. Describe entitlements management
4. Provide security considerations
```

#### 3. Update Mechanism Prompt

```
I need to implement an update mechanism for Panoptikon to allow users to receive and install application updates.

Current project context:
We've implemented application packaging and code signing, and now need to add update functionality.

Please implement:

1. Update Checker (src/panoptikon/utils/updater.py):
   - Check for available updates
   - Compare version information
   - Download update packages
   - Verify package signatures
   - Handle update installation
   - Support automatic updates

2. Update Server Integration (src/panoptikon/utils/update_server.py):
   - Communicate with update server
   - Fetch update metadata
   - Support differential updates
   - Handle authentication
   - Implement retry logic
   - Support rate limiting

3. Update UI (src/panoptikon/ui/components/update_ui.py):
   - Display update availability
   - Show update details
   - Provide installation progress
   - Handle user confirmation
   - Support background updates
   - Notify about completed updates

4. Tests for each component:
   - Test update checking
   - Verify download functionality
   - Test installation process
   - Verify UI components
   - Check error handling

Quality requirements:
- Secure update process
   - Signature verification
   - Secure communication
   - Integrity checking
- Reliable installation
   - Atomic updates
   - Rollback capability
   - Error recovery
- Comprehensive documentation
- Type hints for all functions
- Test coverage of core functionality

Related components:
- Will integrate with application bundle
   - Will use code signing system
   - Will connect to UI components
   - Will support distribution process

For each component, please:
1. Document update process
2. Explain security measures
3. Describe user experience
4. Provide error handling details
```

#### 4. Documentation Prompt

```
I need to create comprehensive documentation for Panoptikon to support users and developers.

Current project context:
We've completed the application development and now need to create thorough documentation.

Please create:

1. User Documentation:
   - Getting Started Guide
   - Search Syntax Reference
   - Cloud Integration Guide
   - Preferences Documentation
   - Troubleshooting Guide
   - Keyboard Shortcuts Reference

2. Developer Documentation:
   - Architecture Overview
   - Component Descriptions
   - API Reference
   - Extension Points
   - Performance Guidelines
   - Contributing Guide

3. Distribution Documentation:
   - Installation Guide
   - Update Process
   - Security Information
   - System Requirements
   - Release Notes
   - Version History

4. Internal Documentation:
   - Code Organization
   - Design Decisions
   - Performance Characteristics
   - Testing Approach
   - Coding Standards
   - Project Roadmap

Quality requirements:
- Clear, concise writing
- Comprehensive coverage
- Well-organized structure
- Appropriate examples
- Visual aids where helpful
- Audience-appropriate language

Each documentation set should:
- Address the needs of its audience
- Provide actionable information
- Include examples and scenarios
- Cover both common and edge cases
- Be easy to navigate and search
- Follow consistent formatting

For each documentation set, please:
1. Create a structured outline
2. Develop comprehensive content
3. Include appropriate examples
4. Add visual elements where helpful
```

### Phase 5 Verification Prompt

```
I need to verify the Phase 5 Distribution implementation of Panoptikon.

Please perform a comprehensive verification:

1. Application bundle:
   - Verify bundle creation process
   - Test bundle on different macOS versions
   - Check resource loading
   - Verify file associations
   - Test application launching

2. Code signing:
   - Verify signature application
   - Test notarization workflow
   - Check entitlements configuration
   - Verify Gatekeeper compatibility
   - Test permission requests

3. Update mechanism:
   - Test update checking
   - Verify download process
   - Test installation procedure
   - Check rollback capability
   - Verify update UI

4. Documentation:
   - Review user documentation
   - Validate developer documentation
   - Check distribution documentation
   - Verify documentation accessibility
   - Test documentation search

5. Overall verification:
   - Test complete distribution flow
   - Verify user experience
   - Check performance in production
   - Test security features
   - Verify compatibility

Create a detailed verification report that includes:
- Status of each distribution component
- Installation experience assessment
   - Update process evaluation
   - Documentation quality review
   - Any issues or limitations found
   - Recommendations for improvements
   - Final project assessment

This report will represent the final project verification.
```

## Conclusion

This phase-specific prompt engineering guide provides a detailed framework for implementing Panoptikon through each development phase. By following these prompt strategies:

1. **Incremental Progress**: Build the application component by component
2. **Consistent Quality**: Maintain high-quality standards throughout
3. **Clear Verification**: Validate each phase before proceeding
4. **Comprehensive Documentation**: Document progress and decisions

Adapt these prompt strategies as needed for specific implementation challenges, while maintaining the core principles of clear requirements, quality focus, and thorough verification.
