# Phase 2: Native macOS UI - Execution Prompt

I need you to implement the native macOS UI for Panoptikon using PyObjC, building upon the core functionality created in Phase 1.

## Task Overview

You're implementing a native macOS application interface using PyObjC that connects to the existing search engine, database, and indexing system. This UI should provide a clean, responsive experience that follows macOS design guidelines.

## Step 1: First, Read Project Status

Begin by reading the verification report from Phase 1 and the status document for Phase 2:

```
read_file docs/phase1_verification.md
read_file docs/phase2_status.md
```

## Step 2: PyObjC Application Framework

Create the core application framework with the following components:

1. **Application Delegate** (`src/panoptikon/ui/app.py`):
   - Implement NSApplicationDelegate for application lifecycle
   - Handle application launch, termination, and activation
   - Initialize core services and controllers
   - Set up menu bar and application menu
   - Implement proper memory management

2. **Window Controller** (`src/panoptikon/ui/window.py`):
   - Create NSWindowController subclass for main window
   - Implement window lifecycle methods
   - Manage window state and persistence
   - Handle window events and callbacks
   - Use proper delegate patterns

3. **View Controller Architecture** (`src/panoptikon/ui/viewcontroller.py`):
   - Implement base view controller patterns
   - Create view management infrastructure
   - Set up controller hierarchy
   - Establish communication patterns between controllers
   - Follow MVVM pattern for separation of concerns

4. **Application Entry Point** (`src/panoptikon/ui/main.py`):
   - Create main entry point for the application
   - Initialize PyObjC environment
   - Set up application instance
   - Handle command line arguments
   - Configure exception handling

## Step 3: UI Components Implementation

Create the core UI components for the application:

1. **Search Field** (`src/panoptikon/ui/components/search_field.py`):
   - Implement NSSearchField wrapper for input
   - Create as-you-type search functionality
   - Handle search history and suggestions
   - Set up keyboard shortcut handling
   - Use proper delegate patterns

2. **Results Table** (`src/panoptikon/ui/components/results_table.py`):
   - Implement NSTableView for displaying search results
   - Create table columns for file metadata
   - Support sorting by any column
   - Implement virtual scrolling for large result sets
   - Handle selection and keyboard navigation
   - Manage cell formatting for different data types

3. **Status Bar** (`src/panoptikon/ui/components/status_bar.py`):
   - Create status display component
   - Show indexing progress and statistics
   - Display current search information
   - Implement status updates from background operations

4. **Toolbar** (`src/panoptikon/ui/components/toolbar.py`):
   - Implement NSToolbar with common actions
   - Create toolbar items for key functions
   - Set up customization support
   - Handle item validation and state

## Step 4: File Operations Integration

Implement file operation functionality:

1. **File Operations Manager** (`src/panoptikon/ui/operations/file_ops.py`):
   - Create file opening functionality
   - Implement "Reveal in Finder" feature
   - Handle file operations with proper permissions
   - Manage multiple file selections
   - Use native macOS APIs for operations

2. **Context Menu** (`src/panoptikon/ui/components/context_menu.py`):
   - Implement NSMenu for context actions
   - Create menu items for file operations
   - Handle dynamic menu generation
   - Manage item validation
   - Support keyboard shortcuts

3. **Drag and Drop Support** (`src/panoptikon/ui/components/drag_drop.py`):
   - Implement drag source functionality
   - Set up pasteboard data provision
   - Create visual feedback during drag
   - Handle multiple item dragging
   - Follow macOS drag and drop guidelines

## Step 5: Menu Bar Integration

Create menu bar functionality:

1. **Menu Bar Component** (`src/panoptikon/ui/menubar.py`):
   - Implement NSStatusItem for menu bar presence
   - Create menu with common actions
   - Set up global keyboard shortcut handling
   - Manage activation and deactivation
   - Handle updates and state changes

2. **Application Menu** (`src/panoptikon/ui/appmenu.py`):
   - Create standard application menu structure
   - Implement menu validation
   - Set up action handlers
   - Create "About" panel
   - Follow macOS menu guidelines

3. **Preferences Window** (`src/panoptikon/ui/preferences.py`):
   - Implement basic preferences dialog
   - Create settings for indexing and search
   - Set up persistence of preferences
   - Handle preference changes and application
   - Follow macOS preferences window guidelines

## Step 6: View Models and Data Binding

Implement the connection between UI and core functionality:

1. **Search View Model** (`src/panoptikon/ui/viewmodels/search_vm.py`):
   - Create MVVM pattern for search
   - Implement data binding to search engine
   - Handle query execution and results
   - Manage state and history
   - Separate UI concerns from core logic

2. **Results View Model** (`src/panoptikon/ui/viewmodels/results_vm.py`):
   - Implement results data source
   - Create sorted and filtered views
   - Handle selection management
   - Implement pagination if needed
   - Manage result transformations

3. **Application View Model** (`src/panoptikon/ui/viewmodels/app_vm.py`):
   - Create application state management
   - Implement settings and preferences binding
   - Handle global application state
   - Manage cross-component communication
   - Coordinate background operations

## Step 7: Comprehensive Tests

Create thorough tests for all UI components:

1. **UI Framework Tests** (`tests/test_ui/test_framework/`):
   - Test application lifecycle
   - Verify window management
   - Test controller hierarchy
   - Validate memory management

2. **Component Tests** (`tests/test_ui/test_components/`):
   - Test individual UI components
   - Verify proper rendering and behavior
   - Test event handling
   - Validate accessibility features

3. **View Model Tests** (`tests/test_ui/test_viewmodels/`):
   - Test data binding functionality
   - Verify transformation logic
   - Test state management
   - Validate communication patterns

4. **Integration Tests** (`tests/test_ui/test_integration/`):
   - Test end-to-end UI flows
   - Verify UI-to-core interactions
   - Test performance under load
   - Validate user experience requirements

## Deliverables

After implementing all components, create these documentation files:

1. **Implementation Log** (`docs/phase2_implementation.md`):
   - Detailed description of all implemented UI components
   - PyObjC integration approach
   - Memory management strategy
   - Design patterns and architecture
   - Known limitations or edge cases

2. **Test Report** (`docs/phase2_test_report.md`):
   - Test coverage statistics
   - UI testing approach
   - Performance test results
   - Validation of requirements

3. **Updated Project Status** (`docs/project_status.md`):
   - Update with Phase 2 completion
   - Document next steps for Phase 3

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
- UI must be responsive (no blocking operations)
- Follow macOS design guidelines and conventions
- Properly document all PyObjC memory management

## References

Refer to:
- The Panoptikon specifications in document 2 (native macOS UI section)
- The implementation plan in document 1
- The quality standards in document 5
