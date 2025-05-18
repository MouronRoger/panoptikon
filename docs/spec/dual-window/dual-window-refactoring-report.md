# Dual-Window Implementation Refactoring Report

## Executive Summary

This report outlines the necessary refactoring for implementing the dual-window feature in Panoptikon as specified in the updated specification. Based on an analysis of the current codebase (Stage 4.3), several key architectural changes and new components are required to support the dual-window functionality.

The project's USP (cross-window drag-and-drop) requires careful design of window state management, resource coordination, and UI considerations. This report provides a practical approach aligned with the Land Rover philosophy: simplicity, robustness, and fitness for purpose.

## 1. Current Architecture Assessment

### 1.1 Existing Structure

The current Panoptikon implementation is based on a single-window architecture with the following key components:

- **Core Services**: Service container, event bus, lifecycle manager
- **UI Layer**: Basic macOS application using PyObjC bindings 
- **File System Operations**: File search and management
- **Data Management**: Search results and query handling

### 1.2 Key Limitations for Dual-Window Support

- **Window Management**: No concept of multiple windows or window state
- **Resource Coordination**: Resources not designed to be shared across windows
- **UI Implementation**: Single window assumption in UI layer
- **Search Context**: Search state tied to main application, not window-specific

## 2. Required New Components

### 2.1 DualWindowManager (Singleton)

```python
class DualWindowManager(ServiceInterface):
    """Manages two application windows (main and secondary)."""
    
    def __init__(self, event_bus: EventBus) -> None:
        """Initialize the window manager."""
        self._main_window_state = WindowState(is_main=True)
        self._secondary_window_state: Optional[WindowState] = None
        self._active_window = "main"  # "main" or "secondary"
        self._event_bus = event_bus
        
    def initialize(self) -> None:
        """Initialize the service."""
        # Register for window activation events
        self._event_bus.subscribe(WindowActivationEvent, self._handle_window_activation)
        
    def shutdown(self) -> None:
        """Clean up resources."""
        # Close secondary window if open
        if self._secondary_window_state:
            self.close_secondary_window()
            
    def toggle_secondary_window(self) -> None:
        """Toggle the secondary window (create if doesn't exist, close if it does)."""
        if self._secondary_window_state:
            self.close_secondary_window()
        else:
            self.create_secondary_window()
            
    def create_secondary_window(self) -> None:
        """Create the secondary window."""
        if self._secondary_window_state:
            return  # Already exists
            
        # Create window state
        self._secondary_window_state = WindowState(is_main=False)
        
        # Calculate position (side by side with main window)
        position = self._calculate_secondary_window_position()
        
        # Publish event to create UI window
        self._event_bus.publish(
            SecondaryWindowCreatedEvent(position=position)
        )
        
    def close_secondary_window(self) -> None:
        """Close the secondary window."""
        if not self._secondary_window_state:
            return  # No secondary window
            
        # Publish event to close UI window
        self._event_bus.publish(SecondaryWindowClosedEvent())
        
        # Clear state
        self._secondary_window_state = None
        
        # Ensure main window is active
        self.activate_main_window()
        
    def activate_main_window(self) -> None:
        """Activate the main window."""
        self._activate_window("main")
        
    def activate_secondary_window(self) -> None:
        """Activate the secondary window."""
        if not self._secondary_window_state:
            return  # Cannot activate non-existent window
            
        self._activate_window("secondary")
        
    def _activate_window(self, window_type: str) -> None:
        """Activate a specific window and deactivate the other."""
        if window_type not in ["main", "secondary"]:
            return
            
        if window_type == self._active_window:
            return  # Already active
            
        # Deactivate current window
        if self._active_window == "main":
            self._main_window_state.is_active = False
            self._suspend_window_resources("main")
        else:
            if self._secondary_window_state:
                self._secondary_window_state.is_active = False
                self._suspend_window_resources("secondary")
                
        # Activate requested window
        previous_window = self._active_window
        self._active_window = window_type
        
        if window_type == "main":
            self._main_window_state.is_active = True
            self._resume_window_resources("main")
        else:
            if self._secondary_window_state:
                self._secondary_window_state.is_active = True  
                self._resume_window_resources("secondary")
                
        # Publish activation event
        self._event_bus.publish(
            WindowActivatedEvent(
                window_type=window_type,
                previous_window=previous_window
            )
        )
        
    def is_secondary_window_open(self) -> bool:
        """Check if secondary window is open."""
        return self._secondary_window_state is not None
        
    def get_active_window_type(self) -> str:
        """Get the active window type ('main' or 'secondary')."""
        return self._active_window
        
    def get_main_window_state(self) -> WindowState:
        """Get the main window state."""
        return self._main_window_state
        
    def get_secondary_window_state(self) -> Optional[WindowState]:
        """Get the secondary window state."""
        return self._secondary_window_state
        
    def coordinate_drag_operation(self, is_from_main_window: bool, files: list[str]) -> None:
        """Coordinate a drag operation between windows."""
        if not self._secondary_window_state:
            return  # Cannot drag between windows when only one exists
            
        source = "main" if is_from_main_window else "secondary"
        target = "secondary" if is_from_main_window else "main"
        
        # Publish event
        self._event_bus.publish(
            WindowDragOperationEvent(
                source_window=source,
                target_window=target,
                files=files
            )
        )
        
    def _calculate_secondary_window_position(self) -> tuple[int, int]:
        """Calculate the position for the secondary window."""
        # In a real implementation, would get main window position/size
        # For now, use placeholder values
        main_pos = (200, 200)  # Placeholder
        main_size = (800, 600)  # Placeholder
        screen_width = 1920  # Placeholder
        
        # Try to position side by side if screen size permits
        if main_pos[0] + main_size[0] + main_size[0] <= screen_width:
            return (main_pos[0] + main_size[0], main_pos[1])
        else:
            # Fall back to offset position
            return (main_pos[0] + 50, main_pos[1] + 50)
            
    def _suspend_window_resources(self, window_type: str) -> None:
        """Suspend resource-intensive operations for inactive window."""
        # Publish event for other services to handle
        self._event_bus.publish(
            WindowResourceSuspendedEvent(window_type=window_type)
        )
        
    def _resume_window_resources(self, window_type: str) -> None:
        """Resume operations for active window."""
        # Publish event for other services to handle
        self._event_bus.publish(
            WindowResourceResumedEvent(window_type=window_type)
        )
```

### 2.2 WindowState Class

```python
class WindowState:
    """Represents the state of a window."""
    
    def __init__(self, is_main: bool) -> None:
        """Initialize window state."""
        self.is_main = is_main
        self.is_active = is_main  # Main window starts as active
        self.search_query = ""
        self.selected_files: list[str] = []
        self.search_results: list[Any] = []
        self.scroll_position: tuple[float, float] = (0, 0)
        self.filter_state: Dict[str, Any] = {}
        self.column_settings: Dict[str, Any] = {}
```

### 2.3 Window-Related Events

```python
@dataclass
class SecondaryWindowCreatedEvent(EventBase):
    """Event issued when the secondary window is created."""
    position: tuple[int, int]

@dataclass
class SecondaryWindowClosedEvent(EventBase):
    """Event issued when the secondary window is closed."""
    pass

@dataclass
class WindowActivatedEvent(EventBase):
    """Event issued when a window is activated."""
    window_type: str  # "main" or "secondary"
    previous_window: str  # "main" or "secondary"

@dataclass
class WindowResourceSuspendedEvent(EventBase):
    """Event issued when a window's resources are suspended."""
    window_type: str  # "main" or "secondary"

@dataclass
class WindowResourceResumedEvent(EventBase):
    """Event issued when a window's resources are resumed."""
    window_type: str  # "main" or "secondary"

@dataclass
class WindowDragOperationEvent(EventBase):
    """Event issued for drag operations between windows."""
    source_window: str  # "main" or "secondary"
    target_window: str  # "main" or "secondary" 
    files: list[str]
```

## 3. Required Refactoring

### 3.1 UI Layer Refactoring

The current `FileSearchApp` class in `macos_app.py` needs significant refactoring:

```python
class FileSearchApp:
    """Main application class supporting dual window layout."""
    
    def __init__(self, service_container: ServiceContainer) -> None:
        """Initialize the application."""
        self._service_container = service_container
        self._window_manager = service_container.resolve(DualWindowManager)
        self._event_bus = service_container.resolve(EventBus)
        
        # Buffer for window content
        self._main_files: list[list[str]] = []
        self._secondary_files: list[list[str]] = []
        
        # UI components for each window
        self._main_window = None
        self._main_search_field = None
        self._main_table_view = None
        
        self._secondary_window = None
        self._secondary_search_field = None
        self._secondary_table_view = None
        
        # Try importing PyObjC modules
        try:
            # Check if PyObjC is available
            for name in ("AppKit", "Foundation", "objc"):
                module = importlib.import_module(name)
                if not isinstance(module, ModuleType):
                    raise ImportError(f"{name} is not a valid module")
            self._pyobjc_available = True
        except ImportError:
            self._pyobjc_available = False
            print("PyObjC not available - UI features disabled")
            return
            
        # Subscribe to window events
        self._event_bus.subscribe(
            SecondaryWindowCreatedEvent, self._handle_secondary_window_created
        )
        self._event_bus.subscribe(
            SecondaryWindowClosedEvent, self._handle_secondary_window_closed
        )
        self._event_bus.subscribe(
            WindowActivatedEvent, self._handle_window_activated
        )
        
        # Create main window
        self._setup_main_window()
        
    def _setup_main_window(self) -> None:
        """Set up the main application window."""
        if not self._pyobjc_available:
            return
            
        # Import PyObjC modules
        import AppKit
        import Foundation
        
        # Create main window (similar to existing implementation)
        frame = (200, 200, 800, 600)
        self._main_window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            Foundation.NSMakeRect(*frame),
            AppKit.NSWindowStyleMaskTitled 
            | AppKit.NSWindowStyleMaskClosable
            | AppKit.NSWindowStyleMaskResizable,
            AppKit.NSBackingStoreBuffered,
            False,
        )
        self._main_window.setTitle_("Panoptikon File Search")
        
        # Add a toggle button for secondary window
        content_view = self._main_window.contentView()
        self._setup_toggle_button(content_view)
        
        # Set up search field, table view, etc.
        # ...
        
        # Set delegate to monitor window activation
        self._main_window_delegate = _WindowDelegate.alloc().init()
        self._main_window_delegate.setCallback_(self)
        self._main_window_delegate.setIsMain_(True)
        self._main_window.setDelegate_(self._main_window_delegate)
        
    def _setup_secondary_window(self, position: tuple[int, int]) -> None:
        """Set up the secondary application window."""
        if not self._pyobjc_available:
            return
            
        # Import PyObjC modules
        import AppKit
        import Foundation
        
        # Create secondary window
        frame = (*position, 800, 600)  # Use provided position
        self._secondary_window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            Foundation.NSMakeRect(*frame),
            AppKit.NSWindowStyleMaskTitled
            | AppKit.NSWindowStyleMaskClosable
            | AppKit.NSWindowStyleMaskResizable,
            AppKit.NSBackingStoreBuffered,
            False,
        )
        self._secondary_window.setTitle_("Panoptikon - Secondary Window")
        
        # Set up UI components
        # ...
        
        # Set delegate to monitor window activation
        self._secondary_window_delegate = _WindowDelegate.alloc().init()
        self._secondary_window_delegate.setCallback_(self)
        self._secondary_window_delegate.setIsMain_(False)
        self._secondary_window.setDelegate_(self._secondary_window_delegate)
        
        # Show window
        self._secondary_window.makeKeyAndOrderFront_(None)
        
    def _setup_toggle_button(self, content_view: Any) -> None:
        """Set up the toggle button for the secondary window."""
        import AppKit
        import Foundation
        
        button = AppKit.NSButton.alloc().initWithFrame_(
            Foundation.NSMakeRect(20, 20, 160, 30)
        )
        button.setTitle_("Toggle Secondary Window")
        button.setBezelStyle_(AppKit.NSBezelStyleRounded)
        button.setTarget_(self)
        button.setAction_("toggleSecondaryWindow:")
        
        content_view.addSubview_(button)
        
    def toggleSecondaryWindow_(self, sender: Any) -> None:
        """Handle toggle button click."""
        self._window_manager.toggle_secondary_window()
        
    def _handle_secondary_window_created(self, event: SecondaryWindowCreatedEvent) -> None:
        """Handle secondary window creation event."""
        self._setup_secondary_window(event.position)
        
    def _handle_secondary_window_closed(self, event: SecondaryWindowClosedEvent) -> None:
        """Handle secondary window closed event."""
        if self._secondary_window:
            self._secondary_window.close()
            self._secondary_window = None
            self._secondary_search_field = None
            self._secondary_table_view = None
            
    def _handle_window_activated(self, event: WindowActivatedEvent) -> None:
        """Handle window activation event."""
        # Update UI to reflect active state
        self._update_window_appearance(event.window_type, event.previous_window)
        
    def _update_window_appearance(self, active_window: str, inactive_window: str) -> None:
        """Update window appearance based on active/inactive state."""
        if not self._pyobjc_available:
            return
            
        # In a real implementation, this would apply color/monochrome styling
        # For demonstration, just update window titles
        if active_window == "main" and self._main_window:
            self._main_window.setTitle_("Panoptikon File Search [ACTIVE]")
        elif self._main_window:
            self._main_window.setTitle_("Panoptikon File Search [INACTIVE]")
            
        if active_window == "secondary" and self._secondary_window:
            self._secondary_window.setTitle_("Panoptikon - Secondary Window [ACTIVE]")
        elif self._secondary_window:
            self._secondary_window.setTitle_("Panoptikon - Secondary Window [INACTIVE]")
            
    def on_window_activated(self, is_main: bool) -> None:
        """Called when a window is activated."""
        if is_main:
            self._window_manager.activate_main_window()
        else:
            self._window_manager.activate_secondary_window()
```

### 3.2 Lifecycle Management Changes

The `ApplicationLifecycle` class needs to be modified to handle dual-window operations:

```python
# Add to ApplicationLifecycle.__init__
self._window_manager = service_container.resolve(DualWindowManager)

# Add to ApplicationLifecycle.stop
# Close secondary window if open
if self._window_manager.is_secondary_window_open():
    self._window_manager.close_secondary_window()
```

### 3.3 Service Container Modifications

Update the service registration in `__main__.py` to include the DualWindowManager:

```python
# Add to main() function
window_manager = DualWindowManager(event_bus)
container.register(DualWindowManager, factory=lambda c: window_manager)
```

### 3.4 Search and File System Service Changes

Modify the search and file system services to be window-aware:

```python
# In SearchService.__init__
self._window_manager = service_container.resolve(DualWindowManager)

# In SearchService.search
def search(self, query: str, is_main_window: Optional[bool] = None) -> list[Any]:
    """Perform a search with window context."""
    if is_main_window is None:
        # Use active window
        is_main_window = self._window_manager.get_active_window_type() == "main"
    
    # Perform search with window context
    # Update appropriate window state with results
    if is_main_window:
        window_state = self._window_manager.get_main_window_state()
    else:
        window_state = self._window_manager.get_secondary_window_state()
        if not window_state:
            return []  # Secondary window doesn't exist
            
    # Save query in window state
    window_state.search_query = query
    
    # Perform actual search
    # ...
```

## 4. Implementation Strategy

### 4.1 Development Phases

1. **Phase 1: Window Management Core**
   - Implement DualWindowManager and WindowState classes
   - Add window-related events
   - Register services in container

2. **Phase 2: UI Adaptation**
   - Refactor FileSearchApp to support main and secondary windows
   - Implement window styling for active/inactive states
   - Add window toggle button and shortcut (Cmd+N)

3. **Phase 3: Resource Management**
   - Modify services to be window-aware
   - Implement resource allocation/deallocation for window activation/deactivation
   - Add state caching for inactive window

4. **Phase 4: Drag and Drop Support**
   - Implement cross-window drag detection
   - Add drop target handling
   - Implement operation coordination between windows

5. **Phase 5: Polish**
   - Implement window positioning algorithm
   - Add visual indicators for active/inactive states
   - Improve keyboard shortcuts
   - Implement memory optimizations

### 4.2 Key Implementation Details

#### Window Delegate

```python
class _WindowDelegate:
    """NSWindowDelegate implementation for tracking window activation."""
    
    def init(self):
        """Initialize the delegate."""
        self = super().init()
        if self:
            self.callback = None
            self.is_main = True
        return self
        
    def setCallback_(self, callback):
        """Set the callback object."""
        self.callback = callback
        
    def setIsMain_(self, is_main):
        """Set whether this is the main window."""
        self.is_main = is_main
        
    def windowDidBecomeKey_(self, notification):
        """Called when the window becomes key (activated)."""
        if self.callback:
            self.callback.on_window_activated(self.is_main)
```

#### Drag and Drop Coordination

```python
def _setup_drag_drop(self, table_view, is_main: bool) -> None:
    """Set up drag and drop for a table view."""
    # Register for drag operations
    table_view.registerForDraggedTypes_(["NSFilenamesPboardType"])
    
    # Create drag source/destination handlers
    table_drag_source = _TableDragSource.alloc().init()
    table_drag_source.setCallback_(self)
    table_drag_source.setIsMain_(is_main)
    
    table_drag_dest = _TableDragDestination.alloc().init()
    table_drag_dest.setCallback_(self)
    table_drag_dest.setIsMain_(is_main)
    
    # Set delegates
    table_view.setDraggingSource_(table_drag_source)
    table_view.setDraggingDestination_(table_drag_dest)
```

```python
def handle_drag_start(self, is_main: bool, files: list[str]) -> None:
    """Handle drag start from a window."""
    # Activate the source window
    if is_main:
        self._window_manager.activate_main_window()
    else:
        self._window_manager.activate_secondary_window()
        
    # Store drag source info for drop handling
    self._drag_source_is_main = is_main
    self._dragged_files = files
    
def handle_drop(self, is_main: bool) -> bool:
    """Handle drop in a window."""
    # Ensure we have a valid drag operation
    if not hasattr(self, "_drag_source_is_main") or not hasattr(self, "_dragged_files"):
        return False
        
    # Don't allow dropping in same window
    if self._drag_source_is_main == is_main:
        return False
        
    # Coordinate the operation
    self._window_manager.coordinate_drag_operation(
        is_from_main_window=self._drag_source_is_main,
        files=self._dragged_files
    )
    
    # Clear drag state
    del self._drag_source_is_main
    del self._dragged_files
    
    return True
```

## 5. Visual Styling for Active/Inactive Windows

As specified in the requirements, inactive windows should have a monochrome/grayscale appearance to visually distinguish them from the active window.

### Implementation Approach

```python
def _apply_window_styling(self, window, is_active: bool) -> None:
    """Apply styling based on window active state."""
    if not window:
        return
        
    import AppKit
    
    content_view = window.contentView()
    
    if is_active:
        # Full color for active window
        self._apply_active_styling(content_view)
    else:
        # Grayscale for inactive window
        self._apply_inactive_styling(content_view)
        
def _apply_active_styling(self, view) -> None:
    """Apply active styling (full color) to a view hierarchy."""
    # In a real implementation, this would restore normal colors
    # For all UI components in the view hierarchy
    pass
    
def _apply_inactive_styling(self, view) -> None:
    """Apply inactive styling (grayscale) to a view hierarchy."""
    # In a real implementation, this would apply a grayscale filter
    # or desaturate all UI components in the view hierarchy
    pass
```

## 6. Potential Issues and Mitigation

### 6.1 Performance Concerns

**Issue**: Secondary window might cause excessive memory/CPU usage  
**Mitigation**:
- Implement strict resource management for inactive window
- Cache search results but limit cached size
- Implement memory pressure detection and cleanup

### 6.2 State Synchronization

**Issue**: File system changes while window inactive  
**Mitigation**:
- Mark inactive window as "stale"
- Add quick refresh on reactivation
- Provide visual indicator for outdated results
- Synchronize essential changes across both windows

### 6.3 User Experience

**Issue**: Unclear which window is active  
**Mitigation**:
- Implement distinct visual styling (color vs grayscale)
- Ensure immediate visual feedback on window activation
- Use macOS standard window activation behaviors

### 6.4 Drag and Drop Reliability

**Issue**: Coordination between windows might cause failures  
**Mitigation**:
- Implement robust transaction tracking
- Add operation logging for diagnostics
- Include error recovery mechanisms
- Test extensively with large file sets

## 7. Testing Strategy

### 7.1 Unit Tests

- DualWindowManager state changes
- Window toggle functionality
- Resource allocation and deallocation
- Event publishing and subscription

### 7.2 Integration Tests

- Window activation/deactivation sequence
- Cross-window drag and drop operations
- Resource management during window switching
- Multi-monitor testing

### 7.3 Performance Tests

- Memory usage with dual windows
- Resource utilization during window switching
- Drag and drop operation timing
- Search performance across both windows

## 8. Recommendations

1. **Implement in Stages**: Follow the 5-phase approach outlined in section 4.1
2. **Prioritize Core Architecture**: Start with DualWindowManager and WindowState
3. **Focus on USP**: Ensure drag-and-drop reliability as highest priority
4. **Defer Polish**: Leave visual refinements until core functionality works
5. **Monitor Resources**: Add diagnostics for window-related memory usage
6. **Visual Differentiation**: Implement the specified color vs grayscale approach
7. **Documentation**: Update all relevant documentation as code changes

## 9. Success Metrics

1. **Performance**: Window switching < 100ms
2. **Memory**: Inactive window uses < 10MB cached state
3. **Reliability**: Zero data loss during cross-window operations
4. **Usability**: Clear active window indication
5. **USP Delivery**: Seamless drag-drop between windows

## Conclusion

The dual-window implementation requires targeted refactoring of the current Panoptikon codebase but can be accomplished efficiently within stage 4.3. By focusing on the Land Rover philosophy of simplicity, robustness, and fitness for purpose, the development team can deliver this key USP with minimal complexity.

The simplification from a multi-window system to a dual-window approach reduces development time, testing complexity, and potential edge cases while still delivering the core functionality. This approach strikes an optimal balance between feature richness and implementation practicality.
