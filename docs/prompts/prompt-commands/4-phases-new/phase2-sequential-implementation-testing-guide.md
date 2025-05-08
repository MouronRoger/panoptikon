# Phase 2: Sequential Implementation and Testing Guide (Native macOS UI)

This document provides a complete sequential implementation and testing workflow for Phase 2 (Native macOS UI) of the Panoptikon file search application. Each step includes both implementation and testing instructions for Cursor. Follow these steps in exact order.

## Initial Setup and Documentation Review

1. **Review specification documentation**: Before beginning implementation, carefully read:
   - Read the project specification: `/docs/panoptikon-specification.md`
   - Review the implementation plan: `/docs/phased-implementation-plan.md`
   - Study the UI requirements in section 2.3 of the specification
   - Examine the PyObjC-specific recommendations in the implementation plan

2. **Verify Phase 1 components**:
   - Ensure all Phase 1 components are complete and passing tests
   - Understand the interfaces provided by Phase 1 components, particularly the search engine and indexing manager

3. **Set up PyObjC environment**:
   - Install necessary PyObjC packages
   - Configure build environment for macOS application development
   - Set up code signing capabilities if available

## Implementation Sequence

### Step 1: Application Delegate

#### Code: Create Application Delegate
```
Implement the ApplicationDelegate in src/panoptikon/ui/app_delegate.py:

1. Create an application delegate that:
   - Initializes the application
   - Manages application lifecycle events
   - Coordinates core components
   - Handles activation and deactivation
   - Implements proper memory management
   - Uses PyObjC conventions correctly

2. Implement the following interface:

class ApplicationDelegate(NSObject):
    """Main application delegate for Panoptikon."""
    
    window = objc.ivar('window')
    search_coordinator = objc.ivar('search_coordinator')
    
    def applicationDidFinishLaunching_(self, notification: NSNotification) -> None:
        """Called when the application has finished launching.
        
        Args:
            notification: Launch notification
        """
        ...
        
    def applicationWillTerminate_(self, notification: NSNotification) -> None:
        """Called when the application is about to terminate.
        
        Args:
            notification: Termination notification
        """
        ...
        
    def applicationShouldTerminateAfterLastWindowClosed_(self, sender: NSApplication) -> bool:
        """Decide if application should terminate when last window is closed.
        
        Args:
            sender: Application object
            
        Returns:
            True to terminate, False otherwise
        """
        ...
```

#### Test: Verify Application Delegate
```
Create and run tests for the ApplicationDelegate in tests/test_ui/test_app_delegate.py:

1. Write tests that verify:
   - Application lifecycle methods are called correctly
   - Components are initialized properly
   - Memory management is handled correctly
   - Application responds to activation/deactivation

2. Include specific test cases:
   - Test application startup sequence
   - Test termination handling
   - Test window management
   - Test memory management

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/test_app_delegate.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/test_app_delegate.py --cov=src.panoptikon.ui.app_delegate
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component01.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 2: Window Controller

#### Code: Create Window Controller
```
Implement the WindowController in src/panoptikon/ui/window_controller.py:

1. Create a window controller that:
   - Manages the main application window
   - Handles window lifecycle events
   - Coordinates view controllers
   - Implements proper size and position management
   - Handles window state restoration
   - Uses PyObjC conventions correctly

2. Implement the following interface:

class WindowController(NSWindowController):
    """Main window controller for Panoptikon."""
    
    content_view_controller = objc.ivar('content_view_controller')
    
    def initWithWindow_(self, window: NSWindow) -> 'WindowController':
        """Initialize with a window.
        
        Args:
            window: Window to control
            
        Returns:
            Initialized controller
        """
        ...
        
    def windowDidLoad(self) -> None:
        """Called when the window has loaded."""
        ...
        
    def windowWillClose_(self, notification: NSNotification) -> None:
        """Called when the window is about to close.
        
        Args:
            notification: Close notification
        """
        ...
        
    def setupWindow(self) -> None:
        """Set up the window appearance and behavior."""
        ...
```

#### Test: Verify Window Controller
```
Create and run tests for the WindowController in tests/test_ui/test_window_controller.py:

1. Write tests that verify:
   - Window is created with correct settings
   - Lifecycle methods are called correctly
   - View controllers are managed properly
   - Window state is handled correctly

2. Include specific test cases:
   - Test window creation
   - Test view controller setup
   - Test window close handling
   - Test window restoration

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/test_window_controller.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/test_window_controller.py --cov=src.panoptikon.ui.window_controller
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component02.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 3: View Controller Architecture

#### Code: Create View Controller Architecture
```
Implement the view controller architecture in src/panoptikon/ui/view_controller.py:

1. Create a view controller architecture that:
   - Implements MVVM pattern for UI components
   - Separates view models from views
   - Provides base classes for view controllers
   - Establishes a consistent component hierarchy
   - Handles view lifecycle events properly
   - Implements proper memory management

2. Implement the following interfaces:

class ViewModel(NSObject):
    """Base class for view models."""
    
    def init(self) -> 'ViewModel':
        """Initialize the view model.
        
        Returns:
            Initialized view model
        """
        ...
        
    def addObserver_forKeyPath_options_context_(self, observer: Any, keyPath: str, 
                                              options: int, context: Any) -> None:
        """Add an observer for a key path.
        
        Args:
            observer: Observer object
            keyPath: Key path to observe
            options: Observation options
            context: Context pointer
        """
        ...

class ViewController(NSViewController):
    """Base class for view controllers."""
    
    view_model = objc.ivar('view_model')
    
    def initWithViewModel_(self, view_model: ViewModel) -> 'ViewController':
        """Initialize with a view model.
        
        Args:
            view_model: View model to use
            
        Returns:
            Initialized view controller
        """
        ...
        
    def loadView(self) -> None:
        """Load the view."""
        ...
        
    def viewDidLoad(self) -> None:
        """Called when the view has loaded."""
        ...
        
    def viewWillAppear(self) -> None:
        """Called when the view is about to appear."""
        ...
        
    def bind_view_model(self) -> None:
        """Bind the view model to the view."""
        ...
```

#### Test: Verify View Controller Architecture
```
Create and run tests for the view controller architecture in tests/test_ui/test_view_controller.py:

1. Write tests that verify:
   - View model binding works correctly
   - View controller lifecycle methods are called
   - Memory management is handled correctly
   - MVVM pattern is correctly implemented

2. Include specific test cases:
   - Test view controller initialization
   - Test view model binding
   - Test view lifecycle methods
   - Test memory management

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/test_view_controller.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/test_view_controller.py --cov=src.panoptikon.ui.view_controller
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component03.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 4: Application Entry Point

#### Code: Create Application Entry Point
```
Implement the application entry point in src/panoptikon/ui/main.py:

1. Create an application entry point that:
   - Initializes the application
   - Handles command line arguments
   - Sets up logging
   - Creates the application delegate
   - Runs the application event loop
   - Implements clean shutdown

2. Implement the following interface:

def initialize_application() -> NSApplication:
    """Initialize the application.
    
    Returns:
        NSApplication instance
    """
    ...

def create_application_delegate() -> ApplicationDelegate:
    """Create the application delegate.
    
    Returns:
        ApplicationDelegate instance
    """
    ...

def setup_menu() -> None:
    """Set up the application menu."""
    ...

def run_application() -> int:
    """Run the application.
    
    Returns:
        Exit code
    """
    ...

def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code
    """
    ...

if __name__ == "__main__":
    sys.exit(main())
```

#### Test: Verify Application Entry Point
```
Create and run tests for the application entry point in tests/test_ui/test_main.py:

1. Write tests that verify:
   - Application initializes correctly
   - Command line arguments are processed
   - Application delegate is created
   - Event loop runs correctly
   - Shutdown is handled properly

2. Include specific test cases:
   - Test application initialization
   - Test delegate creation
   - Test menu setup
   - Test application run

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/test_main.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/test_main.py --cov=src.panoptikon.ui.main
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component04.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 5: Core Application Integration Testing

```
Implement and run integration tests for the Core Application in tests/integration/phase2/test_core_application.py:

1. Create integration tests that:
   - Verify all core application components work together
   - Test the application lifecycle
   - Validate window management
   - Test integration with Phase 1 components

2. Include specific test scenarios:
   - Test application startup and initialization
   - Test window creation and management
   - Test application delegate functionality
   - Test view controller integration

3. Run the integration tests:
   ```
   pytest tests/integration/phase2/test_core_application.py -v
   ```

4. Debug and fix any integration issues until all tests pass.

5. Success criteria:
   - Application launches successfully
   - Window is created and displayed
   - View controllers are initialized
   - Application responds to lifecycle events
   - Integration with Phase 1 components works

6. Create an integration report at:
   `/docs/reports/integration/phase2-core-application.md`
   Include detailed findings, metrics, and any issues encountered.
```

### Step 6: Search Field Component

#### Code: Create Search Field Component
```
Implement the SearchField in src/panoptikon/ui/components/search_field.py:

1. Create a search field component that:
   - Provides as-you-type searching
   - Implements NSSearchField customizations
   - Handles search history
   - Manages focus and keyboard events
   - Uses proper delegate patterns
   - Integrates with the search engine

2. Implement the following interface:

class SearchFieldDelegate(NSObject):
    """Delegate for the search field."""
    
    search_controller = objc.ivar('search_controller')
    
    def searchFieldDidStartSearching_(self, sender: NSSearchField) -> None:
        """Called when the search field starts searching.
        
        Args:
            sender: Search field
        """
        ...
        
    def searchFieldDidEndSearching_(self, sender: NSSearchField) -> None:
        """Called when the search field ends searching.
        
        Args:
            sender: Search field
        """
        ...
        
    def control_textView_doCommandBySelector_(self, control: NSControl, 
                                            textView: NSTextView, 
                                            selector: SEL) -> bool:
        """Handle command from text view.
        
        Args:
            control: Control
            textView: Text view
            selector: Command selector
            
        Returns:
            True if handled, False otherwise
        """
        ...

class SearchField(NSSearchField):
    """Custom search field for Panoptikon."""
    
    delegate = objc.ivar('delegate')
    
    def initWithFrame_(self, frame: NSRect) -> 'SearchField':
        """Initialize with frame.
        
        Args:
            frame: Frame rect
            
        Returns:
            Initialized search field
        """
        ...
        
    def configure(self) -> None:
        """Configure the search field."""
        ...
        
    def setSearchHistory_(self, history: List[str]) -> None:
        """Set the search history.
        
        Args:
            history: Search history
        """
        ...
```

#### Test: Verify Search Field Component
```
Create and run tests for the SearchField in tests/test_ui/components/test_search_field.py:

1. Write tests that verify:
   - Search field is created with correct settings
   - Delegate methods are called correctly
   - Search history works
   - Keyboard events are handled

2. Include specific test cases:
   - Test search field creation
   - Test delegate callbacks
   - Test search history
   - Test keyboard handling

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/components/test_search_field.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/components/test_search_field.py --cov=src.panoptikon.ui.components.search_field
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component05.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 7: Results Table Component

#### Code: Create Results Table Component
```
Implement the ResultsTable in src/panoptikon/ui/components/results_table.py:

1. Create a results table component that:
   - Displays search results in a table
   - Supports virtual scrolling for large result sets
   - Implements proper data source and delegate
   - Provides column sorting
   - Handles selection and keyboard navigation
   - Shows file metadata with appropriate formatting

2. Implement the following interface:

class ResultsTableDataSource(NSObject):
    """Data source for the results table."""
    
    results = objc.ivar('results')
    
    def numberOfRowsInTableView_(self, tableView: NSTableView) -> int:
        """Get the number of rows.
        
        Args:
            tableView: Table view
            
        Returns:
            Number of rows
        """
        ...
        
    def tableView_objectValueForTableColumn_row_(self, tableView: NSTableView, 
                                               tableColumn: NSTableColumn, 
                                               row: int) -> Any:
        """Get the object value for a cell.
        
        Args:
            tableView: Table view
            tableColumn: Table column
            row: Row index
            
        Returns:
            Cell value
        """
        ...

class ResultsTable(NSTableView):
    """Table view for displaying search results."""
    
    data_source = objc.ivar('data_source')
    
    def initWithFrame_(self, frame: NSRect) -> 'ResultsTable':
        """Initialize with frame.
        
        Args:
            frame: Frame rect
            
        Returns:
            Initialized table view
        """
        ...
        
    def configure(self) -> None:
        """Configure the table view."""
        ...
        
    def setResults_(self, results: SearchResult) -> None:
        """Set the search results.
        
        Args:
            results: Search results
        """
        ...
        
    def selectedResults(self) -> List[FileMetadata]:
        """Get the selected results.
        
        Returns:
            List of selected file metadata
        """
        ...
```

#### Test: Verify Results Table Component
```
Create and run tests for the ResultsTable in tests/test_ui/components/test_results_table.py:

1. Write tests that verify:
   - Table is created with correct settings
   - Data source provides correct data
   - Virtual scrolling works for large result sets
   - Selection works correctly

2. Include specific test cases:
   - Test table initialization
   - Test data source methods
   - Test with large result sets
   - Test selection handling

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/components/test_results_table.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/components/test_results_table.py --cov=src.panoptikon.ui.components.results_table
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component06.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 8: Status Bar Component

#### Code: Create Status Bar Component
```
Implement the StatusBar in src/panoptikon/ui/components/status_bar.py:

1. Create a status bar component that:
   - Displays application status
   - Shows indexing progress
   - Indicates search status
   - Provides file count information
   - Updates dynamically
   - Uses appropriate visual style

2. Implement the following interface:

class StatusBar(NSView):
    """Status bar for displaying application status."""
    
    status_text = objc.ivar('status_text')
    progress_indicator = objc.ivar('progress_indicator')
    
    def initWithFrame_(self, frame: NSRect) -> 'StatusBar':
        """Initialize with frame.
        
        Args:
            frame: Frame rect
            
        Returns:
            Initialized status bar
        """
        ...
        
    def configure(self) -> None:
        """Configure the status bar."""
        ...
        
    def setStatus_(self, status: str) -> None:
        """Set the status text.
        
        Args:
            status: Status text
        """
        ...
        
    def showProgress_(self, show: bool) -> None:
        """Show or hide the progress indicator.
        
        Args:
            show: True to show, False to hide
        """
        ...
        
    def setProgress_(self, progress: float) -> None:
        """Set the progress value.
        
        Args:
            progress: Progress value (0.0 to 1.0)
        """
        ...
```

#### Test: Verify Status Bar Component
```
Create and run tests for the StatusBar in tests/test_ui/components/test_status_bar.py:

1. Write tests that verify:
   - Status bar is created with correct settings
   - Status text updates correctly
   - Progress indicator works
   - Layout is correct

2. Include specific test cases:
   - Test status bar creation
   - Test status text updates
   - Test progress indicator
   - Test layout and appearance

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/components/test_status_bar.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/components/test_status_bar.py --cov=src.panoptikon.ui.components.status_bar
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component07.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 9: Toolbar Component

#### Code: Create Toolbar Component
```
Implement the Toolbar in src/panoptikon/ui/components/toolbar.py:

1. Create a toolbar component that:
   - Provides standard file operations
   - Includes search controls
   - Supports customization
   - Manages toolbar items
   - Handles item validation
   - Follows macOS design guidelines

2. Implement the following interface:

class ToolbarDelegate(NSObject):
    """Delegate for the toolbar."""
    
    view_controller = objc.ivar('view_controller')
    
    def toolbar_itemForItemIdentifier_willBeInsertedIntoToolbar_(
        self, toolbar: NSToolbar, itemIdentifier: str, flag: bool
    ) -> NSToolbarItem:
        """Create a toolbar item.
        
        Args:
            toolbar: Toolbar
            itemIdentifier: Item identifier
            flag: Will be inserted flag
            
        Returns:
            Toolbar item
        """
        ...
        
    def toolbarAllowedItemIdentifiers_(self, toolbar: NSToolbar) -> List[str]:
        """Get allowed item identifiers.
        
        Args:
            toolbar: Toolbar
            
        Returns:
            List of allowed identifiers
        """
        ...
        
    def toolbarDefaultItemIdentifiers_(self, toolbar: NSToolbar) -> List[str]:
        """Get default item identifiers.
        
        Args:
            toolbar: Toolbar
            
        Returns:
            List of default identifiers
        """
        ...

class Toolbar(NSToolbar):
    """Toolbar for the main window."""
    
    delegate = objc.ivar('delegate')
    
    def initWithIdentifier_(self, identifier: str) -> 'Toolbar':
        """Initialize with identifier.
        
        Args:
            identifier: Toolbar identifier
            
        Returns:
            Initialized toolbar
        """
        ...
        
    def configure(self) -> None:
        """Configure the toolbar."""
        ...
```

#### Test: Verify Toolbar Component
```
Create and run tests for the Toolbar in tests/test_ui/components/test_toolbar.py:

1. Write tests that verify:
   - Toolbar is created with correct settings
   - Delegate methods are called correctly
   - Toolbar items are created correctly
   - Item validation works

2. Include specific test cases:
   - Test toolbar creation
   - Test item creation
   - Test allowed/default items
   - Test item validation

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/components/test_toolbar.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/components/test_toolbar.py --cov=src.panoptikon.ui.components.toolbar
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component08.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 10: UI Framework Integration Testing

```
Implement and run integration tests for the UI Framework in tests/integration/phase2/test_ui_framework.py:

1. Create integration tests that:
   - Verify all UI components work together
   - Test layout and appearance
   - Validate user interactions
   - Test keyboard navigation

2. Include specific test scenarios:
   - Test search field with results table
   - Test toolbar with status bar
   - Test keyboard navigation between components
   - Test component layout and appearance

3. Run the integration tests:
   ```
   pytest tests/integration/phase2/test_ui_framework.py -v
   ```

4. Debug and fix any integration issues until all tests pass.

5. Success criteria:
   - All components work together seamlessly
   - Layout is correct and responsive
   - Keyboard navigation works as expected
   - Visual appearance follows macOS guidelines

6. Create an integration report at:
   `/docs/reports/integration/phase2-ui-framework.md`
   Include detailed findings, metrics, and any issues encountered.
```

### Step 11: First UI Prototype Build

```
Create a buildable prototype of the Panoptikon UI:

1. Create a build script in scripts/build_phase2_prototype.py that:
   - Packages all implemented components
   - Creates a runnable macOS application
   - Sets up proper resources
   - Configures logging
   - Includes basic documentation

2. Run the build script:
   ```
   python scripts/build_phase2_prototype.py
   ```

3. Test the prototype application manually:
   - Verify application launches
   - Test basic UI functionality
   - Check integration with Phase 1 components
   - Validate appearance and behavior

4. Success criteria:
   - Application builds successfully
   - UI components display correctly
   - Basic search functionality works
   - Integration with Phase 1 components is functional

5. Create a prototype build report at:
   `/docs/reports/builds/phase2-prototype-build.md`
   Include build details, test results, screenshots, and any issues encountered.
```

### Step 12: File Operations Manager

#### Code: Create File Operations Manager
```
Implement the FileOperationsManager in src/panoptikon/ui/operations.py:

1. Create a file operations manager that:
   - Handles opening files with default applications
   - Implements "reveal in Finder" functionality
   - Manages file operations permissions
   - Handles multiple file selections
   - Uses native file APIs
   - Provides operation feedback

2. Implement the following interface:

class FileOperationsManager(NSObject):
    """Manages file operations."""
    
    def openFile_(self, path: Path) -> bool:
        """Open a file with its default application.
        
        Args:
            path: File path
            
        Returns:
            True if successful, False otherwise
        """
        ...
        
    def openFiles_(self, paths: List[Path]) -> bool:
        """Open multiple files with their default applications.
        
        Args:
            paths: File paths
            
        Returns:
            True if all files were opened successfully, False otherwise
        """
        ...
        
    def revealInFinder_(self, path: Path) -> bool:
        """Reveal a file in the Finder.
        
        Args:
            path: File path
            
        Returns:
            True if successful, False otherwise
        """
        ...
        
    def revealInFinderMultiple_(self, paths: List[Path]) -> bool:
        """Reveal multiple files in the Finder.
        
        Args:
            paths: File paths
            
        Returns:
            True if successful, False otherwise
        """
        ...
        
    def canPerformOperation_onPath_(self, operation: str, path: Path) -> bool:
        """Check if an operation can be performed on a path.
        
        Args:
            operation: Operation name
            path: File path
            
        Returns:
            True if the operation can be performed, False otherwise
        """
        ...
```

#### Test: Verify File Operations Manager
```
Create and run tests for the FileOperationsManager in tests/test_ui/test_operations.py:

1. Write tests that verify:
   - Files open correctly
   - Reveal in Finder works
   - Permission checking works
   - Multiple file operations work

2. Include specific test cases:
   - Test opening different file types
   - Test revealing files in Finder
   - Test permission validation
   - Test with multiple files

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/test_operations.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/test_operations.py --cov=src.panoptikon.ui.operations
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component09.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 13: Context Menu Component

#### Code: Create Context Menu Component
```
Implement the ContextMenu in src/panoptikon/ui/components/context_menu.py:

1. Create a context menu component that:
   - Provides file operations in a context menu
   - Handles menu item validation
   - Supports dynamic menu generation
   - Adapts based on selection
   - Follows macOS menu guidelines
   - Integrates with file operations manager

2. Implement the following interface:

class ContextMenuDelegate(NSObject):
    """Delegate for context menu."""
    
    file_operations_manager = objc.ivar('file_operations_manager')
    
    def menuNeedsUpdate_(self, menu: NSMenu) -> None:
        """Called when the menu needs to be updated.
        
        Args:
            menu: Menu to update
        """
        ...
        
    def validateMenuItem_(self, menuItem: NSMenuItem) -> bool:
        """Validate a menu item.
        
        Args:
            menuItem: Menu item
            
        Returns:
            True if the item is valid, False otherwise
        """
        ...
        
    def menuForSelection_(self, selection: List[FileMetadata]) -> NSMenu:
        """Create a menu for the selection.
        
        Args:
            selection: Selected files
            
        Returns:
            Context menu
        """
        ...

class ContextMenu(NSMenu):
    """Context menu for file operations."""
    
    delegate = objc.ivar('delegate')
    
    def initWithTitle_(self, title: str) -> 'ContextMenu':
        """Initialize with title.
        
        Args:
            title: Menu title
            
        Returns:
            Initialized menu
        """
        ...
        
    def configure(self) -> None:
        """Configure the menu."""
        ...
```

#### Test: Verify Context Menu Component
```
Create and run tests for the ContextMenu in tests/test_ui/components/test_context_menu.py:

1. Write tests that verify:
   - Menu is created with correct items
   - Delegate methods are called correctly
   - Item validation works
   - Dynamic menu generation works

2. Include specific test cases:
   - Test menu creation
   - Test with different file selections
   - Test item validation
   - Test menu actions

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/components/test_context_menu.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/components/test_context_menu.py --cov=src.panoptikon.ui.components.context_menu
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component10.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 14: Drag and Drop Support

#### Code: Create Drag and Drop Support
```
Implement drag and drop support in src/panoptikon/ui/components/drag_drop.py:

1. Create drag and drop support that:
   - Enables dragging files from results table
   - Handles pasteboard operations
   - Supports multiple file selection
   - Provides visual feedback during drag
   - Follows macOS drag and drop guidelines
   - Integrates with file operations

2. Implement the following interface:

class DragSourceView(NSView):
    """View that supports dragging files."""
    
    data_source = objc.ivar('data_source')
    
    def initWithFrame_(self, frame: NSRect) -> 'DragSourceView':
        """Initialize with frame.
        
        Args:
            frame: Frame rect
            
        Returns:
            Initialized view
        """
        ...
        
    def draggingSession_sourceOperationMaskForDraggingContext_(
        self, session: NSDraggingSession, context: NSDraggingContext
    ) -> NSDragOperation:
        """Get the drag operation mask.
        
        Args:
            session: Dragging session
            context: Dragging context
            
        Returns:
            Drag operation mask
        """
        ...
        
    def setDataSource_(self, dataSource: Any) -> None:
        """Set the data source.
        
        Args:
            dataSource: Data source
        """
        ...
        
    def beginDragWithItems_event_(self, items: List[Any], event: NSEvent) -> None:
        """Begin a drag operation.
        
        Args:
            items: Items to drag
            event: Mouse event
        """
        ...

class DragDropManager(NSObject):
    """Manages drag and drop operations."""
    
    def registerDragSource_(self, view: NSView) -> None:
        """Register a drag source.
        
        Args:
            view: View to register
        """
        ...
        
    def fileItemsForDrag_(self, paths: List[Path]) -> List[NSPasteboardItem]:
        """Create pasteboard items for files.
        
        Args:
            paths: File paths
            
        Returns:
            Pasteboard items
        """
        ...
```

#### Test: Verify Drag and Drop Support
```
Create and run tests for the drag and drop support in tests/test_ui/components/test_drag_drop.py:

1. Write tests that verify:
   - Drag operation works correctly
   - Pasteboard items are created properly
   - Multiple file selection works
   - Visual feedback is correct

2. Include specific test cases:
   - Test drag initialization
   - Test with different file selections
   - Test pasteboard operations
   - Test drag operations

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/components/test_drag_drop.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/components/test_drag_drop.py --cov=src.panoptikon.ui.components.drag_drop
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component11.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 15: Menu Bar Component

#### Code: Create Menu Bar Component
```
Implement the MenuBar in src/panoptikon/ui/menu_bar.py:

1. Create a menu bar component that:
   - Implements NSStatusItem for menu bar presence
   - Provides quick search access
   - Shows application status
   - Handles activation and deactivation
   - Follows macOS menu bar guidelines
   - Integrates with the application

2. Implement the following interface:

class MenuBarController(NSObject):
    """Controller for the menu bar item."""
    
    status_item = objc.ivar('status_item')
    menu = objc.ivar('menu')
    
    def init(self) -> 'MenuBarController':
        """Initialize the controller.
        
        Returns:
            Initialized controller
        """
        ...
        
    def setupStatusItem(self) -> None:
        """Set up the status item."""
        ...
        
    def setupMenu(self) -> None:
        """Set up the menu."""
        ...
        
    def updateStatus_(self, status: str) -> None:
        """Update the status text.
        
        Args:
            status: Status text
        """
        ...
        
    def showMainWindow_(self, sender: Any) -> None:
        """Show the main window.
        
        Args:
            sender: Sender
        """
        ...
        
    def hideMainWindow_(self, sender: Any) -> None:
        """Hide the main window.
        
        Args:
            sender: Sender
        """
        ...
```

#### Test: Verify Menu Bar Component
```
Create and run tests for the MenuBar in tests/test_ui/test_menu_bar.py:

1. Write tests that verify:
   - Status item is created correctly
   - Menu is created with proper items
   - Status updates work
   - Window show/hide actions work

2. Include specific test cases:
   - Test status item creation
   - Test menu setup
   - Test status updates
   - Test window actions

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/test_menu_bar.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/test_menu_bar.py --cov=src.panoptikon.ui.menu_bar
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component12.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 16: Application Menu

#### Code: Create Application Menu
```
Implement the ApplicationMenu in src/panoptikon/ui/app_menu.py:

1. Create an application menu that:
   - Implements standard macOS application menu
   - Provides file and edit menus
   - Includes view and window menus
   - Supports keyboard shortcuts
   - Follows macOS menu guidelines
   - Provides consistent actions

2. Implement the following interface:

class ApplicationMenu(NSObject):
    """Manages the application menu."""
    
    main_menu = objc.ivar('main_menu')
    
    def init(self) -> 'ApplicationMenu':
        """Initialize the application menu.
        
        Returns:
            Initialized menu manager
        """
        ...
        
    def setupMainMenu(self) -> None:
        """Set up the main menu."""
        ...
        
    def createApplicationMenu(self) -> NSMenu:
        """Create the application menu.
        
        Returns:
            Application menu
        """
        ...
        
    def createFileMenu(self) -> NSMenu:
        """Create the file menu.
        
        Returns:
            File menu
        """
        ...
        
    def createEditMenu(self) -> NSMenu:
        """Create the edit menu.
        
        Returns:
            Edit menu
        """
        ...
        
    def createViewMenu(self) -> NSMenu:
        """Create the view menu.
        
        Returns:
            View menu
        """
        ...
        
    def createWindowMenu(self) -> NSMenu:
        """Create the window menu.
        
        Returns:
            Window menu
        """
        ...
        
    def createHelpMenu(self) -> NSMenu:
        """Create the help menu.
        
        Returns:
            Help menu
        """
        ...
```

#### Test: Verify Application Menu
```
Create and run tests for the ApplicationMenu in tests/test_ui/test_app_menu.py:

1. Write tests that verify:
   - Main menu is created correctly
   - All standard menus are created
   - Menu items have proper actions
   - Keyboard shortcuts are set correctly

2. Include specific test cases:
   - Test main menu creation
   - Test individual menu creation
   - Test menu item actions
   - Test keyboard shortcuts

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/test_app_menu.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/test_app_menu.py --cov=src.panoptikon.ui.app_menu
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component13.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 17: Preferences Window

#### Code: Create Preferences Window
```
Implement the PreferencesWindow in src/panoptikon/ui/preferences.py:

1. Create a preferences window that:
   - Implements a standard tabbed preferences window
   - Provides general, indexing, and search tabs
   - Handles preference persistence
   - Validates user input
   - Follows macOS preferences guidelines
   - Applies changes immediately where appropriate

2. Implement the following interface:

class PreferencesWindowController(NSWindowController):
    """Controller for the preferences window."""
    
    tab_view = objc.ivar('tab_view')
    
    def initWithWindow_(self, window: NSWindow) -> 'PreferencesWindowController':
        """Initialize with window.
        
        Args:
            window: Window
            
        Returns:
            Initialized controller
        """
        ...
        
    def windowDidLoad(self) -> None:
        """Called when the window has loaded."""
        ...
        
    def setupTabs(self) -> None:
        """Set up the tab view."""
        ...
        
    def selectTabWithIdentifier_(self, identifier: str) -> None:
        """Select a tab.
        
        Args:
            identifier: Tab identifier
        """
        ...

class PreferencesViewController(NSViewController):
    """Base class for preference view controllers."""
    
    def loadView(self) -> None:
        """Load the view."""
        ...
        
    def viewDidLoad(self) -> None:
        """Called when the view has loaded."""
        ...
        
    def savePreferences(self) -> None:
        """Save preferences."""
        ...
        
    def loadPreferences(self) -> None:
        """Load preferences."""
        ...
```

#### Test: Verify Preferences Window
```
Create and run tests for the PreferencesWindow in tests/test_ui/test_preferences.py:

1. Write tests that verify:
   - Preferences window is created correctly
   - Tabs are created and switch properly
   - Preferences are saved and loaded
   - Input validation works

2. Include specific test cases:
   - Test window creation
   - Test tab switching
   - Test preference saving
   - Test input validation

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/test_preferences.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/test_preferences.py --cov=src.panoptikon.ui.preferences
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component14.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 18: File and Menu Integration Testing

```
Implement and run integration tests for File and Menu Integration in tests/integration/phase2/test_file_menu_integration.py:

1. Create integration tests that:
   - Verify file operations, context menu, and application menu work together
   - Test drag and drop with file operations
   - Validate preferences with application settings
   - Test menu bar integration

2. Include specific test scenarios:
   - Test file operations through context menu
   - Test drag and drop operations
   - Test preferences window with settings
   - Test menu bar with application window

3. Run the integration tests:
   ```
   pytest tests/integration/phase2/test_file_menu_integration.py -v
   ```

4. Debug and fix any integration issues until all tests pass.

5. Success criteria:
   - File operations work through all interfaces
   - Context menu and application menu are consistent
   - Preferences window correctly affects application settings
   - Menu bar functions work correctly

6. Create an integration report at:
   `/docs/reports/integration/phase2-file-menu-integration.md`
   Include detailed findings, metrics, and any issues encountered.
```

### Step 19: Search View Model

#### Code: Create Search View Model
```
Implement the SearchViewModel in src/panoptikon/ui/viewmodels/search_vm.py:

1. Create a search view model that:
   - Manages search state
   - Handles query execution
   - Controls results pagination
   - Implements filtering logic
   - Provides sort order management
   - Separates UI from search logic

2. Implement the following interface:

class SearchViewModel(ViewModel):
    """View model for search functionality."""
    
    search_engine = objc.ivar('search_engine')
    results = objc.ivar('results')
    
    def init(self) -> 'SearchViewModel':
        """Initialize the view model.
        
        Returns:
            Initialized view model
        """
        ...
        
    def setSearchEngine_(self, searchEngine: SearchEngine) -> None:
        """Set the search engine.
        
        Args:
            searchEngine: Search engine
        """
        ...
        
    def search_(self, query: str) -> None:
        """Perform a search.
        
        Args:
            query: Search query
        """
        ...
        
    def getResults(self) -> SearchResult:
        """Get the search results.
        
        Returns:
            Search results
        """
        ...
        
    def sortResultsBy_ascending_(self, field: str, ascending: bool) -> None:
        """Sort the results.
        
        Args:
            field: Field to sort by
            ascending: Sort in ascending order
        """
        ...
        
    def getPage_size_(self, page: int, size: int) -> List[FileMetadata]:
        """Get a page of results.
        
        Args:
            page: Page number
            size: Page size
            
        Returns:
            List of file metadata for the page
        """
        ...
```

#### Test: Verify Search View Model
```
Create and run tests for the SearchViewModel in tests/test_ui/viewmodels/test_search_vm.py:

1. Write tests that verify:
   - Search operations work correctly
   - Results are managed properly
   - Pagination works
   - Sorting functions correctly

2. Include specific test cases:
   - Test search operation
   - Test result management
   - Test pagination
   - Test sorting

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/viewmodels/test_search_vm.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/viewmodels/test_search_vm.py --cov=src.panoptikon.ui.viewmodels.search_vm
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component15.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 20: Results View Model

#### Code: Create Results View Model
```
Implement the ResultsViewModel in src/panoptikon/ui/viewmodels/results_vm.py:

1. Create a results view model that:
   - Manages search result display
   - Handles selection state
   - Controls file operations
   - Provides result filtering
   - Manages sorting and grouping
   - Separates UI from result logic

2. Implement the following interface:

class ResultsViewModel(ViewModel):
    """View model for results display."""
    
    search_vm = objc.ivar('search_vm')
    file_operations = objc.ivar('file_operations')
    selection = objc.ivar('selection')
    
    def init(self) -> 'ResultsViewModel':
        """Initialize the view model.
        
        Returns:
            Initialized view model
        """
        ...
        
    def setSearchViewModel_(self, searchVM: SearchViewModel) -> None:
        """Set the search view model.
        
        Args:
            searchVM: Search view model
        """
        ...
        
    def setFileOperations_(self, fileOperations: FileOperationsManager) -> None:
        """Set the file operations manager.
        
        Args:
            fileOperations: File operations manager
        """
        ...
        
    def updateResults(self) -> None:
        """Update results from the search view model."""
        ...
        
    def setSelection_(self, selection: List[FileMetadata]) -> None:
        """Set the selection.
        
        Args:
            selection: Selected items
        """
        ...
        
    def getSelection(self) -> List[FileMetadata]:
        """Get the selection.
        
        Returns:
            Selected items
        """
        ...
        
    def openSelection(self) -> bool:
        """Open the selected files.
        
        Returns:
            True if successful, False otherwise
        """
        ...
        
    def revealSelection(self) -> bool:
        """Reveal the selected files in Finder.
        
        Returns:
            True if successful, False otherwise
        """
        ...
```

#### Test: Verify Results View Model
```
Create and run tests for the ResultsViewModel in tests/test_ui/viewmodels/test_results_vm.py:

1. Write tests that verify:
   - Results are updated correctly
   - Selection works properly
   - File operations integration works
   - Result filtering and sorting work

2. Include specific test cases:
   - Test result updates
   - Test selection management
   - Test file operations
   - Test filtering and sorting

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/viewmodels/test_results_vm.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/viewmodels/test_results_vm.py --cov=src.panoptikon.ui.viewmodels.results_vm
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component16.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 21: Application View Model

#### Code: Create Application View Model
```
Implement the ApplicationViewModel in src/panoptikon/ui/viewmodels/app_vm.py:

1. Create an application view model that:
   - Manages application state
   - Coordinates other view models
   - Handles application settings
   - Manages indexing status
   - Controls window visibility
   - Provides application-level operations

2. Implement the following interface:

class ApplicationViewModel(ViewModel):
    """View model for the application."""
    
    indexing_manager = objc.ivar('indexing_manager')
    search_vm = objc.ivar('search_vm')
    results_vm = objc.ivar('results_vm')
    
    def init(self) -> 'ApplicationViewModel':
        """Initialize the view model.
        
        Returns:
            Initialized view model
        """
        ...
        
    def setup(self) -> None:
        """Set up the view model."""
        ...
        
    def setIndexingManager_(self, indexingManager: IndexingManager) -> None:
        """Set the indexing manager.
        
        Args:
            indexingManager: Indexing manager
        """
        ...
        
    def startIndexing(self) -> None:
        """Start indexing."""
        ...
        
    def stopIndexing(self) -> None:
        """Stop indexing."""
        ...
        
    def getIndexingStatus(self) -> Tuple[str, Optional[float]]:
        """Get the indexing status.
        
        Returns:
            Tuple of (status text, progress)
        """
        ...
        
    def loadSettings(self) -> None:
        """Load application settings."""
        ...
        
    def saveSettings(self) -> None:
        """Save application settings."""
        ...
```

#### Test: Verify Application View Model
```
Create and run tests for the ApplicationViewModel in tests/test_ui/viewmodels/test_app_vm.py:

1. Write tests that verify:
   - View model coordination works
   - Indexing management functions correctly
   - Settings are loaded and saved properly
   - Application state is managed correctly

2. Include specific test cases:
   - Test view model setup
   - Test indexing control
   - Test settings management
   - Test application state

3. Run the tests using pytest:
   ```
   pytest tests/test_ui/viewmodels/test_app_vm.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_ui/viewmodels/test_app_vm.py --cov=src.panoptikon.ui.viewmodels.app_vm
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase2-component17.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 22: View Model Integration Testing

```
Implement and run integration tests for the View Model Integration in tests/integration/phase2/test_viewmodel_integration.py:

1. Create integration tests that:
   - Verify all view models work together
   - Test data binding with UI components
   - Validate end-to-end workflows
   - Test MVVM pattern implementation

2. Include specific test scenarios:
   - Test search workflow with view models
   - Test file operations through view models
   - Test application state management
   - Test view model updates to UI

3. Run the integration tests:
   ```
   pytest tests/integration/phase2/test_viewmodel_integration.py -v
   ```

4. Debug and fix any integration issues until all tests pass.

5. Success criteria:
   - All view models work together seamlessly
   - Data binding works correctly
   - UI updates reflect view model changes
   - MVVM pattern is correctly implemented

6. Create an integration report at:
   `/docs/reports/integration/phase2-viewmodel-integration.md`
   Include detailed findings, metrics, and any issues encountered.
```

### Step 23: Complete UI Application Build

```
Create a buildable version of the complete Panoptikon UI:

1. Create a build script in scripts/build_phase2_complete.py that:
   - Packages all implemented components
   - Creates a runnable macOS application
   - Sets up proper resources and icons
   - Configures logging and error handling
   - Includes comprehensive documentation
   - Prepares for notarization (if applicable)

2. Run the build script:
   ```
   python scripts/build_phase2_complete.py
   ```

3. Test the complete application manually:
   - Verify all UI components work together
   - Test end-to-end workflows
   - Check integration with Phase 1 components
   - Validate appearance and behavior
   - Test performance under load

4. Success criteria:
   - Application builds successfully
   - All UI components function correctly
   - Integration with Phase 1 components is seamless
   - Performance meets requirements
   - User experience is smooth and intuitive

5. Create a complete build report at:
   `/docs/reports/builds/phase2-complete-build.md`
   Include build details, test results, screenshots, and any issues encountered.
```

### Step 24: Phase 2 Comprehensive UI Testing

```
Implement and run comprehensive UI tests for the complete Phase 2 application in tests/application/test_phase2_application.py:

1. Create application tests that:
   - Verify the entire UI application works end-to-end
   - Test all user workflows
   - Validate UI responsiveness
   - Test with substantial data volumes
   - Verify integration with Phase 1 components

2. Include specific test scenarios:
   - Test application startup and shutdown
   - Test search workflow with UI components
   - Test file operations through UI
   - Test preferences and settings
   - Test menu bar integration
   - Test keyboard navigation
   - Test accessibility features

3. Run the application tests:
   ```
   pytest tests/application/test_phase2_application.py -v
   ```

4. Debug and fix any application issues until all tests pass.

5. Success criteria:
   - All application tests pass
   - UI is responsive and functional
   - Integration with Phase 1 components works seamlessly
   - User experience meets macOS guidelines
   - Performance meets requirements

6. Create a final phase report at:
   `/docs/reports/phase2_completion_report.md`
   Include comprehensive metrics, performance results, and an overview of the implementation.
```

## Implementation Notes

1. **Starting Incrementally**: Implement one component at a time, fully testing each before proceeding.
2. **Quality First**: Never compromise on quality standards.
3. **PyObjC Best Practices**:
   - Use proper memory management
   - Document ownership semantics
   - Implement proper delegate patterns
   - Follow macOS design guidelines
4. **UI Testing Focus**:
   - Validate appearance and behavior
   - Test keyboard navigation
   - Verify accessibility compliance
   - Test memory management

## Progress Tracking

Create a project board that tracks:
1. Components completed with test coverage metrics
2. Integration test results
3. UI performance metrics
4. Outstanding issues and technical debt

Update this board after each component and integration test is completed.
