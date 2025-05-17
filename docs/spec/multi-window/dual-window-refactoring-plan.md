# 🚧 DUAL-WINDOW REFACTORING PLAN

## 📌 OVERVIEW
This plan outlines the phased implementation of the dual-window feature for Panoptikon, following the V6.1 multi-stage template methodology. The dual-window feature is a significant USP that enables cross-window drag-and-drop operations, differentiating Panoptikon from competitors like Everything.

## 📋 PREREQUISITES
- Current codebase is at Stage 4.3 (Schema Migration Framework)
- Core infrastructure (service container, event bus) is in place
- UI layer with single-window implementation exists
- PyObjC bindings are functional

## 🎯 OBJECTIVES
1. Implement binary window management (main + secondary)
2. Enable independent search contexts per window
3. Support cross-window drag-and-drop operations
4. Provide distinct visual states for active/inactive windows
5. Manage resources efficiently between windows
6. Maintain performance targets (switching < 100ms, inactive window memory < 10MB)

---

# STAGE 1 — DUAL-WINDOW CORE ARCHITECTURE

## 1. LOAD STAGE SPEC
- 📄 From: Dual window specification, integration report, and refactoring report
- 🔍 Development Phase: UI Framework (Phase 3)

## 2. ANALYZE CONTEXT
- **Stage objectives**: Implement core dual-window architecture
- **Interfaces**: Service container, event bus, UI application
- **Constraints**:
  - Must maintain existing service architecture
  - Binary window model only (main + secondary)
  - Maintain performance standards
- **Dependencies**:
  - Service container implementation
  - EventBus for cross-component communication
  - UI implementation using PyObjC

## 3. STAGE SEGMENTATION

### SEGMENT 1: Window-Related Events
- Define all window-related events
- Integrate with existing EventBus

### SEGMENT 2: WindowState Class
- Define window state model
- Implement persistence of window-specific properties

### SEGMENT 3: DualWindowManager Service
- Create service interface for window management
- Implement lifecycle methods
- Add window activation/deactivation logic

### SEGMENT 4: Service Registration
- Register DualWindowManager in service container
- Establish dependency relationships

## 4. IMPLEMENTATION AND TESTING

### SEGMENT 1: Window-Related Events
#### Test-First:
- Window events defined correctly with required properties
- Events can be serialized/deserialized properly
- Event hierarchy follows existing patterns

#### Implementation:
```python
# src/panoptikon/ui/events.py

from dataclasses import dataclass
from typing import Optional, Tuple, List

from panoptikon.core.events import EventBase

@dataclass
class SecondaryWindowCreatedEvent(EventBase):
    """Event issued when the secondary window is created."""
    position: Tuple[int, int]

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
    files: List[str]
```

#### Verification:
- Unit tests for event creation and properties
- Verify event serialization works
- Test event equality and hashing

### SEGMENT 2: WindowState Class
#### Test-First:
- WindowState properly initializes with main/secondary flag
- State properties can be updated and retrieved
- State can maintain search context independently

#### Implementation:
```python
# src/panoptikon/ui/window_state.py

from typing import Any, Dict, List, Optional, Tuple

class WindowState:
    """Represents the state of a window."""
    
    def __init__(self, is_main: bool) -> None:
        """Initialize window state.
        
        Args:
            is_main: Whether this is the main window
        """
        self.is_main = is_main
        self.is_active = is_main  # Main window starts as active
        self.search_query = ""
        self.selected_files: List[str] = []
        self.search_results: List[Any] = []
        self.scroll_position: Tuple[float, float] = (0, 0)
        self.filter_state: Dict[str, Any] = {}
        self.column_settings: Dict[str, Any] = {}
    
    def update_search_query(self, query: str) -> None:
        """Update the search query.
        
        Args:
            query: The new search query
        """
        self.search_query = query
    
    def update_selection(self, files: List[str]) -> None:
        """Update the selected files.
        
        Args:
            files: The list of selected files
        """
        self.selected_files = files.copy()
    
    def update_scroll_position(self, position: Tuple[float, float]) -> None:
        """Update the scroll position.
        
        Args:
            position: The scroll position (x, y)
        """
        self.scroll_position = position
    
    def reset(self) -> None:
        """Reset the state to default values."""
        self.search_query = ""
        self.selected_files = []
        self.search_results = []
        self.scroll_position = (0, 0)
```

#### Verification:
- Unit tests for WindowState initialization
- Verify state update methods work correctly
- Test state reset functionality

### SEGMENT 3: DualWindowManager Service
#### Test-First:
- DualWindowManager initializes with main window state
- Secondary window can be created and closed
- Window activation properly updates states
- Event publishing works correctly

#### Implementation:
```python
# src/panoptikon/ui/window_manager.py

from typing import Optional, Tuple

from panoptikon.core.events import EventBus
from panoptikon.core.service import ServiceInterface
from panoptikon.ui.events import (
    SecondaryWindowCreatedEvent,
    SecondaryWindowClosedEvent,
    WindowActivatedEvent,
    WindowResourceSuspendedEvent,
    WindowResourceResumedEvent,
    WindowDragOperationEvent,
)
from panoptikon.ui.window_state import WindowState

class DualWindowManager(ServiceInterface):
    """Manages two application windows (main and secondary)."""
    
    def __init__(self, event_bus: EventBus) -> None:
        """Initialize the window manager.
        
        Args:
            event_bus: Event bus for publishing events
        """
        self._main_window_state = WindowState(is_main=True)
        self._secondary_window_state: Optional[WindowState] = None
        self._active_window = "main"  # "main" or "secondary"
        self._event_bus = event_bus
        
    def initialize(self) -> None:
        """Initialize the service."""
        # Register for window activation events
        self._event_bus.subscribe(
            WindowActivatedEvent,
            self._handle_window_activation
        )
        
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
        """Activate a specific window and deactivate the other.
        
        Args:
            window_type: The window type to activate ("main" or "secondary")
        """
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
        """Check if secondary window is open.
        
        Returns:
            True if secondary window is open, False otherwise
        """
        return self._secondary_window_state is not None
        
    def get_active_window_type(self) -> str:
        """Get the active window type ('main' or 'secondary').
        
        Returns:
            The active window type
        """
        return self._active_window
        
    def get_main_window_state(self) -> WindowState:
        """Get the main window state.
        
        Returns:
            The main window state
        """
        return self._main_window_state
        
    def get_secondary_window_state(self) -> Optional[WindowState]:
        """Get the secondary window state.
        
        Returns:
            The secondary window state, or None if it doesn't exist
        """
        return self._secondary_window_state
        
    def coordinate_drag_operation(self, is_from_main_window: bool, files: list[str]) -> None:
        """Coordinate a drag operation between windows.
        
        Args:
            is_from_main_window: Whether the drag originated from the main window
            files: List of files being dragged
        """
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
        
    def _calculate_secondary_window_position(self) -> Tuple[int, int]:
        """Calculate the position for the secondary window.
        
        Returns:
            The position (x, y) for the secondary window
        """
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
        """Suspend resource-intensive operations for inactive window.
        
        Args:
            window_type: The window type to suspend resources for
        """
        # Publish event for other services to handle
        self._event_bus.publish(
            WindowResourceSuspendedEvent(window_type=window_type)
        )
        
    def _resume_window_resources(self, window_type: str) -> None:
        """Resume operations for active window.
        
        Args:
            window_type: The window type to resume resources for
        """
        # Publish event for other services to handle
        self._event_bus.publish(
            WindowResourceResumedEvent(window_type=window_type)
        )
        
    def _handle_window_activation(self, event: WindowActivatedEvent) -> None:
        """Handle window activation event.
        
        Args:
            event: The window activation event
        """
        # Ensure internal state matches the event
        self._active_window = event.window_type
        
        # Update window active states
        self._main_window_state.is_active = (event.window_type == "main")
        if self._secondary_window_state:
            self._secondary_window_state.is_active = (event.window_type == "secondary")
```

#### Verification:
- Unit tests for window manager functionality
- Verify window state is correctly maintained
- Test event publishing for all operations
- Verify resource suspension/resumption

### SEGMENT 4: Service Registration
#### Test-First:
- Service can be registered in container
- Manager is available as a singleton
- Dependencies are correctly established

#### Implementation:
```python
# Update src/panoptikon/__main__.py

# Add import
from panoptikon.ui.window_manager import DualWindowManager

# Add to main() function after event_bus creation
window_manager = DualWindowManager(event_bus)
container.register(DualWindowManager, factory=lambda c: window_manager)
```

#### Verification:
- Test service registration
- Verify service can be resolved
- Check for dependency cycles

## 5. STAGE INTEGRATION TEST
- Run integration tests for all segments
- Verify service container resolves DualWindowManager
- Ensure events are properly published and received
- Test window activation flow

## 6. PROPAGATE STATE
- Write `stage1_report.md`
- Document current implementation and next steps
- Update mCP with implementation details

---

# STAGE 2 — UI IMPLEMENTATION

## 1. LOAD STAGE SPEC
- 📄 From: Dual window specification, integration report, and previous stage report
- 🔍 Development Phase: UI Framework (Phase 3)

## 2. ANALYZE CONTEXT
- **Stage objectives**: Implement dual-window UI components
- **Interfaces**: PyObjC, NSWindow, UI components
- **Constraints**:
  - Must work with or without PyObjC
  - Window styling must differentiate active/inactive windows
  - Performance requirements for window switching
- **Dependencies**:
  - DualWindowManager from Stage 1
  - PyObjC wrapper components
  - Event system for window coordination

## 3. STAGE SEGMENTATION

### SEGMENT 1: Window Delegate
- Implement NSWindowDelegate for window activation tracking
- Create PyObjC bridge for activation events

### SEGMENT 2: Main UI Refactoring
- Refactor FileSearchApp to support dual-window model
- Add window state tracking
- Implement toggle button

### SEGMENT 3: Secondary Window Implementation
- Create secondary window UI
- Handle window creation/closing
- Synchronize window appearance

### SEGMENT 4: Window Styling
- Implement active/inactive window visual states
- Create style management system
- Apply proper grayscale/color styling

## 4. IMPLEMENTATION AND TESTING

### SEGMENT 1: Window Delegate
#### Test-First:
- Delegate properly tracks window activation
- Activation callback works correctly
- Main/secondary window identification functions

#### Implementation:
```python
# src/panoptikon/ui/window_delegate.py

from typing import Any, Protocol

class WindowCallbackProtocol(Protocol):
    """Protocol for window activation callbacks."""
    
    def on_window_activated(self, is_main: bool) -> None:
        """Called when a window is activated.
        
        Args:
            is_main: Whether the activated window is the main window
        """
        ...

class WindowDelegate:
    """NSWindowDelegate implementation for tracking window activation."""
    
    @classmethod
    def alloc(cls):
        """Allocate the delegate class (PyObjC bridge).
        
        Returns:
            Allocated delegate class
        """
        try:
            import objc
            
            # Create Objective-C class
            DelegateClass = objc.createClass(
                "PanoptikonWindowDelegate",
                superclass=objc.lookUpClass("NSObject"),
                protocols=["NSWindowDelegate"]
            )
            
            # Add methods
            def init(self):
                """Initialize the delegate."""
                self = objc.super(DelegateClass, self).init()
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
                if hasattr(self, "callback") and self.callback is not None:
                    self.callback.on_window_activated(self.is_main)
            
            # Register methods with the class
            objc.registerSelector(b"init", [b"@", b":", b"@"])
            objc.registerSelector(b"setCallback:", [b"v", b":", b"@"])
            objc.registerSelector(b"setIsMain:", [b"v", b":", b"B"])
            objc.registerSelector(b"windowDidBecomeKey:", [b"v", b":", b"@"])
            
            DelegateClass.addMethod(b"init", init)
            DelegateClass.addMethod(b"setCallback:", setCallback_)
            DelegateClass.addMethod(b"setIsMain:", setIsMain_)
            DelegateClass.addMethod(b"windowDidBecomeKey:", windowDidBecomeKey_)
            
            return DelegateClass.alloc()
        except ImportError:
            # Return dummy object if PyObjC not available
            return DummyDelegate.alloc()

class DummyDelegate:
    """Dummy delegate for when PyObjC is not available."""
    
    @classmethod
    def alloc(cls):
        """Allocate the delegate class."""
        return cls()
    
    def init(self):
        """Initialize the delegate."""
        return self
    
    def setCallback_(self, callback):
        """Set the callback object."""
        pass
    
    def setIsMain_(self, is_main):
        """Set whether this is the main window."""
        pass
```

#### Verification:
- Test delegate initialization with and without PyObjC
- Verify method signatures match Objective-C expectations
- Test callback invocation

### SEGMENT 2: Main UI Refactoring
#### Test-First:
- UI initialization handles dual-window dependencies
- Event subscribers are properly registered
- Window manager is correctly resolved from service container

#### Implementation:
```python
# Update src/panoptikon/ui/macos_app.py

import importlib
from types import ModuleType
from typing import Any, Optional, List, Tuple

from panoptikon.core.events import EventBus
from panoptikon.core.service import ServiceContainer
from panoptikon.ui.events import (
    SecondaryWindowCreatedEvent,
    SecondaryWindowClosedEvent,
    WindowActivatedEvent,
)
from panoptikon.ui.window_delegate import WindowDelegate
from panoptikon.ui.window_manager import DualWindowManager
from panoptikon.ui.objc_wrappers import (
    SearchFieldWrapper,
    SegmentedControlWrapper,
    TableViewWrapper,
)

class FileSearchApp:
    """Main application class supporting dual window layout."""
    
    def __init__(self, service_container: ServiceContainer) -> None:
        """Initialize the application.
        
        Args:
            service_container: Service container for dependency resolution
        """
        self._service_container = service_container
        self._window_manager = service_container.resolve(DualWindowManager)
        self._event_bus = service_container.resolve(EventBus)
        
        # Buffer for window content
        self._main_files: List[List[str]] = []
        self._secondary_files: List[List[str]] = []
        
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
        
        # Set up search field, table view, etc. (existing implementation)
        # ...
        
        # Set delegate to monitor window activation
        self._main_window_delegate = WindowDelegate.alloc().init()
        self._main_window_delegate.setCallback_(self)
        self._main_window_delegate.setIsMain_(True)
        self._main_window.setDelegate_(self._main_window_delegate)
        
        # Show the window
        self._main_window.makeKeyAndOrderFront_(None)
        
    def _setup_toggle_button(self, content_view: Any) -> None:
        """Set up the toggle button for the secondary window.
        
        Args:
            content_view: The content view to add the button to
        """
        if not self._pyobjc_available:
            return
            
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
        """Handle toggle button click.
        
        Args:
            sender: The sender of the action
        """
        self._window_manager.toggle_secondary_window()
        
    def on_window_activated(self, is_main: bool) -> None:
        """Called when a window is activated.
        
        Args:
            is_main: Whether the activated window is the main window
        """
        if is_main:
            self._window_manager.activate_main_window()
        else:
            self._window_manager.activate_secondary_window()
```

#### Verification:
- Test main window setup
- Verify toggle button creation
- Test window activation callback
- Check service resolution

### SEGMENT 3: Secondary Window Implementation
#### Test-First:
- Secondary window creates correctly
- Window positioning is appropriate
- Window closes properly
- Events are handled correctly

#### Implementation:
```python
# Add to src/panoptikon/ui/macos_app.py

def _setup_secondary_window(self, position: Tuple[int, int]) -> None:
    """Set up the secondary application window.
    
    Args:
        position: The position (x, y) for the window
    """
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
    
    # Set up UI components (similar to main window)
    # ...
    
    # Set delegate to monitor window activation
    self._secondary_window_delegate = WindowDelegate.alloc().init()
    self._secondary_window_delegate.setCallback_(self)
    self._secondary_window_delegate.setIsMain_(False)
    self._secondary_window.setDelegate_(self._secondary_window_delegate)
    
    # Show window
    self._secondary_window.makeKeyAndOrderFront_(None)
    
def _handle_secondary_window_created(self, event: SecondaryWindowCreatedEvent) -> None:
    """Handle secondary window creation event.
    
    Args:
        event: The window creation event
    """
    self._setup_secondary_window(event.position)
    
def _handle_secondary_window_closed(self, event: SecondaryWindowClosedEvent) -> None:
    """Handle secondary window closed event.
    
    Args:
        event: The window closed event
    """
    if not self._secondary_window:
        return
        
    self._secondary_window.close()
    self._secondary_window = None
    self._secondary_search_field = None
    self._secondary_table_view = None
```

#### Verification:
- Test secondary window creation
- Verify window delegate setup
- Test window closing
- Check event handling

### SEGMENT 4: Window Styling
#### Test-First:
- Active/inactive visual states apply correctly
- Style transitions are smooth
- Style differences are noticeable but not distracting

#### Implementation:
```python
# Add to src/panoptikon/ui/macos_app.py

def _handle_window_activated(self, event: WindowActivatedEvent) -> None:
    """Handle window activation event.
    
    Args:
        event: The window activation event
    """
    # Update UI to reflect active state
    self._update_window_appearance(event.window_type, event.previous_window)
    
def _update_window_appearance(self, active_window: str, inactive_window: str) -> None:
    """Update window appearance based on active/inactive state.
    
    Args:
        active_window: The active window type
        inactive_window: The previous active window type
    """
    if not self._pyobjc_available:
        return
        
    # Apply styling to main window
    if self._main_window:
        if active_window == "main":
            self._apply_active_styling(self._main_window)
            self._main_window.setTitle_("Panoptikon File Search")
        else:
            self._apply_inactive_styling(self._main_window)
            self._main_window.setTitle_("Panoptikon File Search [INACTIVE]")
            
    # Apply styling to secondary window
    if self._secondary_window:
        if active_window == "secondary":
            self._apply_active_styling(self._secondary_window)
            self._secondary_window.setTitle_("Panoptikon - Secondary Window")
        else:
            self._apply_inactive_styling(self._secondary_window)
            self._secondary_window.setTitle_("Panoptikon - Secondary Window [INACTIVE]")
            
def _apply_active_styling(self, window: Any) -> None:
    """Apply active styling (full color) to a window.
    
    Args:
        window: The window to style
    """
    # In a real implementation, this would restore normal colors
    # For demonstration, we'll just update the window appearance
    import AppKit
    
    # Get content view
    content_view = window.contentView()
    
    # Reset any effects
    if hasattr(content_view, "_grayscale_effect"):
        effect = getattr(content_view, "_grayscale_effect")
        effect.removeFromSuperview()
        delattr(content_view, "_grayscale_effect")
    
def _apply_inactive_styling(self, window: Any) -> None:
    """Apply inactive styling (grayscale) to a window.
    
    Args:
        window: The window to style
    """
    # In a real implementation, this would apply a grayscale filter
    import AppKit
    
    # Get content view
    content_view = window.contentView()
    
    # Apply grayscale effect using Core Image Filter
    if hasattr(AppKit, "NSVisualEffectView") and not hasattr(content_view, "_grayscale_effect"):
        # Create a visual effect view
        frame = content_view.frame()
        effect_view = AppKit.NSVisualEffectView.alloc().initWithFrame_(frame)
        effect_view.setBlendingMode_(AppKit.NSVisualEffectBlendingModeBehindWindow)
        effect_view.setState_(AppKit.NSVisualEffectStateActive)
        effect_view.setAlphaValue_(0.3)  # Partial transparency
        
        # Insert behind all other views
        content_view.addSubview_positioned_relativeTo_(
            effect_view,
            AppKit.NSWindowBelow,
            None
        )
        
        # Store for later removal
        setattr(content_view, "_grayscale_effect", effect_view)
```

#### Verification:
- Test style application with active/inactive states
- Verify visual differences between windows
- Test style transitions during window switching
- Check appearance consistency

## 5. STAGE INTEGRATION TEST
- Run integration tests for all UI components
- Test window creation and closing
- Verify visual state transitions
- Test keyboard shortcuts (Cmd+N) for window toggle

## 6. PROPAGATE STATE
- Write `stage2_report.md`
- Document UI implementation and visual design
- Update mCP with implementation details

---

# STAGE 3 — RESOURCE MANAGEMENT

## 1. LOAD STAGE SPEC
- 📄 From: Dual window specification, integration report, and previous stage reports
- 🔍 Development Phase: UI Framework (Phase 3)

## 2. ANALYZE CONTEXT
- **Stage objectives**: Implement resource management for dual windows
- **Interfaces**: Window manager, service system
- **Constraints**:
  - Only active window should use full resources
  - Inactive window must be responsive but minimal resource usage
  - Performance targets for window switching
- **Dependencies**:
  - DualWindowManager from Stage 1
  - UI implementation from Stage 2
  - Service container for resource coordination

## 3. STAGE SEGMENTATION

### SEGMENT 1: Resource Suspension Interface
- Define resource suspension/resumption interfaces
- Create window-aware resource hooks

### SEGMENT 2: Search Service Integration
- Modify search service to be window-aware
- Implement per-window search context

### SEGMENT 3: File System Service Integration
- Adapt file system monitoring for dual windows
- Implement activation-based resource management

### SEGMENT 4: Window State Caching
- Create window state caching system
- Implement efficient state restoration

## 4. IMPLEMENTATION AND TESTING

### SEGMENT 1: Resource Suspension Interface
#### Test-First:
- Resource suspension events are processed correctly
- Services respond to window activation events
- Resource management follows window active status

#### Implementation:
```python
# src/panoptikon/core/resource_manager.py

from abc import ABC, abstractmethod
from typing import Protocol

from panoptikon.core.events import EventBus
from panoptikon.core.service import ServiceInterface
from panoptikon.ui.events import WindowResourceSuspendedEvent, WindowResourceResumedEvent

class WindowAwareResource(Protocol):
    """Protocol for resources that are aware of window state."""
    
    def suspend(self, window_type: str) -> None:
        """Suspend resource usage for a window.
        
        Args:
            window_type: The window type to suspend resources for
        """
        ...
    
    def resume(self, window_type: str) -> None:
        """Resume resource usage for a window.
        
        Args:
            window_type: The window type to resume resources for
        """
        ...

class ResourceManager(ServiceInterface):
    """Manages resources based on window state."""
    
    def __init__(self, event_bus: EventBus) -> None:
        """Initialize the resource manager.
        
        Args:
            event_bus: Event bus for subscribing to events
        """
        self._event_bus = event_bus
        self._resources: list[WindowAwareResource] = []
        
    def initialize(self) -> None:
        """Initialize the service."""
        # Subscribe to resource events
        self._event_bus.subscribe(
            WindowResourceSuspendedEvent,
            self._handle_resource_suspended
        )
        self._event_bus.subscribe(
            WindowResourceResumedEvent,
            self._handle_resource_resumed
        )
        
    def shutdown(self) -> None:
        """Clean up resources."""
        self._resources.clear()
        
    def register_resource(self, resource: WindowAwareResource) -> None:
        """Register a window-aware resource.
        
        Args:
            resource: The resource to register
        """
        self._resources.append(resource)
        
    def unregister_resource(self, resource: WindowAwareResource) -> None:
        """Unregister a window-aware resource.
        
        Args:
            resource: The resource to unregister
        """
        if resource in self._resources:
            self._resources.remove(resource)
            
    def _handle_resource_suspended(self, event: WindowResourceSuspendedEvent) -> None:
        """Handle resource suspended event.
        
        Args:
            event: The resource suspended event
        """
        for resource in self._resources:
            resource.suspend(event.window_type)
            
    def _handle_resource_resumed(self, event: WindowResourceResumedEvent) -> None:
        """Handle resource resumed event.
        
        Args:
            event: The resource resumed event
        """
        for resource in self._resources:
            resource.resume(event.window_type)
```

#### Verification:
- Test resource manager initialization
- Verify event handling
- Test resource registration/unregistration
- Check resource suspension/resumption

### SEGMENT 2: Search Service Integration
#### Test-First:
- Search service handles window context correctly
- Search results are stored per window
- Query execution respects resource constraints

#### Implementation:
```python
# Update search service to be window-aware

from typing import Any, List, Optional

from panoptikon.core.events import EventBus
from panoptikon.core.service import ServiceContainer, ServiceInterface
from panoptikon.ui.window_manager import DualWindowManager

class SearchService(ServiceInterface, WindowAwareResource):
    """Provides search functionality with window awareness."""
    
    def __init__(
        self,
        service_container: ServiceContainer,
        event_bus: EventBus
    ) -> None:
        """Initialize the search service.
        
        Args:
            service_container: Service container
            event_bus: Event bus
        """
        self._service_container = service_container
        self._event_bus = event_bus
        self._window_manager = service_container.resolve(DualWindowManager)
        self._resource_manager = service_container.resolve(ResourceManager)
        
        # Search state
        self._main_results_cache: List[Any] = []
        self._secondary_results_cache: Optional[List[Any]] = None
        self._main_query: str = ""
        self._secondary_query: Optional[str] = None
        
        # Resource state
        self._main_suspended = False
        self._secondary_suspended = True
        
    def initialize(self) -> None:
        """Initialize the service."""
        # Register as a window-aware resource
        self._resource_manager.register_resource(self)
        
    def shutdown(self) -> None:
        """Clean up resources."""
        self._resource_manager.unregister_resource(self)
        
    def suspend(self, window_type: str) -> None:
        """Suspend resource usage for a window.
        
        Args:
            window_type: The window type to suspend resources for
        """
        if window_type == "main":
            self._main_suspended = True
        else:
            self._secondary_suspended = True
            
    def resume(self, window_type: str) -> None:
        """Resume resource usage for a window.
        
        Args:
            window_type: The window type to resume resources for
        """
        if window_type == "main":
            self._main_suspended = False
            # Refresh if needed
            if self._main_query:
                self._refresh_main_results()
        else:
            self._secondary_suspended = False
            # Refresh if needed
            if self._secondary_query:
                self._refresh_secondary_results()
                
    def search(self, query: str, is_main_window: Optional[bool] = None) -> List[Any]:
        """Perform a search with window context.
        
        Args:
            query: The search query
            is_main_window: Whether the search is for the main window
            
        Returns:
            The search results
        """
        if is_main_window is None:
            # Use active window
            is_main_window = self._window_manager.get_active_window_type() == "main"
        
        # Store query
        if is_main_window:
            self._main_query = query
            
            # Update window state
            window_state = self._window_manager.get_main_window_state()
            window_state.update_search_query(query)
            
            # Perform search if not suspended
            if not self._main_suspended:
                self._refresh_main_results()
                
            return self._main_results_cache
        else:
            # Secondary window
            self._secondary_query = query
            
            # Get window state
            window_state = self._window_manager.get_secondary_window_state()
            if not window_state:
                return []  # Secondary window doesn't exist
                
            # Update window state
            window_state.update_search_query(query)
            
            # Perform search if not suspended
            if not self._secondary_suspended and self._secondary_results_cache is not None:
                self._refresh_secondary_results()
                
            return self._secondary_results_cache or []
            
    def _refresh_main_results(self) -> None:
        """Refresh main window search results."""
        # In a real implementation, this would perform the actual search
        # For now, just use a placeholder
        self._main_results_cache = [
            ["File 1", "/path/to/file1", "10 KB", "2023-01-01"],
            ["File 2", "/path/to/file2", "20 KB", "2023-01-02"],
        ]
        
    def _refresh_secondary_results(self) -> None:
        """Refresh secondary window search results."""
        # In a real implementation, this would perform the actual search
        # For now, just use a placeholder
        self._secondary_results_cache = [
            ["File 3", "/path/to/file3", "30 KB", "2023-01-03"],
            ["File 4", "/path/to/file4", "40 KB", "2023-01-04"],
        ]
```

#### Verification:
- Test window-specific search results
- Verify search query persistence
- Test resource suspension effects
- Check result caching

### SEGMENT 3: File System Service Integration
#### Test-First:
- File system watchers respect window activation
- Monitoring resources are properly managed
- Events are routed to correct window

#### Implementation:
```python
# Update filesystem service to be window-aware

from typing import Dict, Optional, Set

from panoptikon.core.events import EventBus
from panoptikon.core.service import ServiceContainer, ServiceInterface
from panoptikon.ui.window_manager import DualWindowManager

class FileSystemService(ServiceInterface, WindowAwareResource):
    """Provides file system monitoring with window awareness."""
    
    def __init__(
        self,
        service_container: ServiceContainer,
        event_bus: EventBus
    ) -> None:
        """Initialize the file system service.
        
        Args:
            service_container: Service container
            event_bus: Event bus
        """
        self._service_container = service_container
        self._event_bus = event_bus
        self._window_manager = service_container.resolve(DualWindowManager)
        self._resource_manager = service_container.resolve(ResourceManager)
        
        # Monitoring state
        self._main_paths: Set[str] = set()
        self._secondary_paths: Set[str] = set()
        
        # Resource state
        self._main_suspended = False
        self._secondary_suspended = True
        
        # Watchers
        self._main_watcher = None
        self._secondary_watcher = None
        
    def initialize(self) -> None:
        """Initialize the service."""
        # Register as a window-aware resource
        self._resource_manager.register_resource(self)
        
        # Initialize watchers
        self._init_main_watcher()
        
    def shutdown(self) -> None:
        """Clean up resources."""
        self._resource_manager.unregister_resource(self)
        
        # Stop watchers
        self._stop_main_watcher()
        self._stop_secondary_watcher()
        
    def suspend(self, window_type: str) -> None:
        """Suspend resource usage for a window.
        
        Args:
            window_type: The window type to suspend resources for
        """
        if window_type == "main":
            self._main_suspended = True
            self._pause_main_watcher()
        else:
            self._secondary_suspended = True
            self._pause_secondary_watcher()
            
    def resume(self, window_type: str) -> None:
        """Resume resource usage for a window.
        
        Args:
            window_type: The window type to resume resources for
        """
        if window_type == "main":
            self._main_suspended = False
            self._resume_main_watcher()
        else:
            self._secondary_suspended = False
            if self._window_manager.is_secondary_window_open():
                self._init_secondary_watcher()
                
    def add_watched_path(self, path: str, is_main_window: Optional[bool] = None) -> None:
        """Add a path to watch.
        
        Args:
            path: The path to watch
            is_main_window: Whether the path is for the main window
        """
        if is_main_window is None:
            # Use active window
            is_main_window = self._window_manager.get_active_window_type() == "main"
            
        if is_main_window:
            self._main_paths.add(path)
            if not self._main_suspended:
                self._update_main_watcher()
        else:
            self._secondary_paths.add(path)
            if not self._secondary_suspended and self._window_manager.is_secondary_window_open():
                self._update_secondary_watcher()
                
    def remove_watched_path(self, path: str, is_main_window: Optional[bool] = None) -> None:
        """Remove a path from watching.
        
        Args:
            path: The path to remove
            is_main_window: Whether the path is for the main window
        """
        if is_main_window is None:
            # Use active window
            is_main_window = self._window_manager.get_active_window_type() == "main"
            
        if is_main_window:
            if path in self._main_paths:
                self._main_paths.remove(path)
                if not self._main_suspended:
                    self._update_main_watcher()
        else:
            if path in self._secondary_paths:
                self._secondary_paths.remove(path)
                if not self._secondary_suspended and self._window_manager.is_secondary_window_open():
                    self._update_secondary_watcher()
                    
    def _init_main_watcher(self) -> None:
        """Initialize main window watcher."""
        # In a real implementation, this would create the FSEvents watcher
        self._main_watcher = {}
        
    def _init_secondary_watcher(self) -> None:
        """Initialize secondary window watcher."""
        # In a real implementation, this would create the FSEvents watcher
        self._secondary_watcher = {}
        
    def _stop_main_watcher(self) -> None:
        """Stop main window watcher."""
        # In a real implementation, this would stop the FSEvents watcher
        self._main_watcher = None
        
    def _stop_secondary_watcher(self) -> None:
        """Stop secondary window watcher."""
        # In a real implementation, this would stop the FSEvents watcher
        self._secondary_watcher = None
        
    def _pause_main_watcher(self) -> None:
        """Pause main window watcher."""
        # In a real implementation, this would pause the FSEvents watcher
        pass
        
    def _pause_secondary_watcher(self) -> None:
        """Pause secondary window watcher."""
        # In a real implementation, this would pause the FSEvents watcher
        pass
        
    def _resume_main_watcher(self) -> None:
        """Resume main window watcher."""
        # In a real implementation, this would resume the FSEvents watcher
        pass
        
    def _resume_secondary_watcher(self) -> None:
        """Resume secondary window watcher."""
        # In a real implementation, this would resume the FSEvents watcher
        pass
        
    def _update_main_watcher(self) -> None:
        """Update main window watcher paths."""
        # In a real implementation, this would update the FSEvents watcher paths
        pass
        
    def _update_secondary_watcher(self) -> None:
        """Update secondary window watcher paths."""
        # In a real implementation, this would update the FSEvents watcher paths
        pass
```

#### Verification:
- Test watcher initialization
- Verify suspension/resumption
- Test path management
- Check window-specific watchers

### SEGMENT 4: Window State Caching
#### Test-First:
- Window state is properly cached during deactivation
- State is restored on activation
- Memory usage remains within limits

#### Implementation:
```python
# Update src/panoptikon/ui/window_manager.py

# Add to DualWindowManager class

def cache_window_state(self, window_type: str) -> None:
    """Cache window state for later restoration.
    
    Args:
        window_type: The window type to cache state for
    """
    if window_type == "main":
        # Store main window state (already exists, so nothing to do)
        pass
    elif window_type == "secondary" and self._secondary_window_state:
        # Store secondary window state
        # In a real implementation, this might compress or reduce the state
        # to minimize memory usage
        pass
    
def restore_window_state(self, window_type: str) -> None:
    """Restore window state from cache.
    
    Args:
        window_type: The window type to restore state for
    """
    if window_type == "main":
        # Restore main window state (already exists, so nothing to do)
        pass
    elif window_type == "secondary" and self._secondary_window_state:
        # Restore secondary window state
        # In a real implementation, this might reinflate the state from
        # a compressed or reduced version
        pass

# Update _activate_window method
def _activate_window(self, window_type: str) -> None:
    """Activate a specific window and deactivate the other.
    
    Args:
        window_type: The window type to activate ("main" or "secondary")
    """
    if window_type not in ["main", "secondary"]:
        return
        
    if window_type == self._active_window:
        return  # Already active
        
    # Deactivate current window
    if self._active_window == "main":
        self._main_window_state.is_active = False
        self.cache_window_state("main")
        self._suspend_window_resources("main")
    else:
        if self._secondary_window_state:
            self._secondary_window_state.is_active = False
            self.cache_window_state("secondary")
            self._suspend_window_resources("secondary")
            
    # Activate requested window
    previous_window = self._active_window
    self._active_window = window_type
    
    if window_type == "main":
        self._main_window_state.is_active = True
        self.restore_window_state("main")
        self._resume_window_resources("main")
    else:
        if self._secondary_window_state:
            self._secondary_window_state.is_active = True
            self.restore_window_state("secondary")
            self._resume_window_resources("secondary")
            
    # Publish activation event
    self._event_bus.publish(
        WindowActivatedEvent(
            window_type=window_type,
            previous_window=previous_window
        )
    )
```

#### Verification:
- Test state caching
- Verify state restoration
- Check memory usage
- Test activation/deactivation cycle

## 5. STAGE INTEGRATION TEST
- Run integration tests for resource management
- Verify window-aware service behavior
- Test resource suspension/resumption
- Measure memory usage during window switching

## 6. PROPAGATE STATE
- Write `stage3_report.md`
- Document resource management strategy
- Update mCP with implementation details

---

# STAGE 4 — DRAG AND DROP SUPPORT

## 1. LOAD STAGE SPEC
- 📄 From: Dual window specification, integration report, and previous stage reports
- 🔍 Development Phase: UI Framework (Phase 3)

## 2. ANALYZE CONTEXT
- **Stage objectives**: Implement cross-window drag and drop operations
- **Interfaces**: NSTableView, NSPasteboard, DualWindowManager
- **Constraints**:
  - Must support dragging between windows
  - Must handle activation correctly
  - Must maintain data integrity
- **Dependencies**:
  - DualWindowManager from Stage 1
  - UI implementation from Stage 2
  - Resource management from Stage 3

## 3. STAGE SEGMENTATION

### SEGMENT 1: Drag Source Implementation
- Create drag source protocol
- Implement table view drag source
- Configure drag representation

### SEGMENT 2: Drop Target Implementation
- Create drop target protocol
- Implement table view drop target
- Handle drop operations

### SEGMENT 3: Drag Coordination
- Implement drag coordination between windows
- Handle window activation during drag
- Track drag operation state

### SEGMENT 4: Operation Finalization
- Complete drag operations
- Verify data integrity
- Update UI state

## 4. IMPLEMENTATION AND TESTING

### SEGMENT 1: Drag Source Implementation
#### Test-First:
- Drag sources initialize correctly
- Drag operation starts correctly
- Drag representation is appropriate
- Source window activates on drag

#### Implementation:
```python
# src/panoptikon/ui/drag_source.py

from typing import Any, List, Protocol

class DragSourceDelegate(Protocol):
    """Protocol for drag source delegates."""
    
    def handle_drag_start(self, is_main: bool, files: List[str]) -> None:
        """Handle drag start from a window.
        
        Args:
            is_main: Whether the drag is from the main window
            files: List of files being dragged
        """
        ...

class TableDragSource:
    """NSTableView drag source implementation."""
    
    @classmethod
    def alloc(cls):
        """Allocate the drag source class (PyObjC bridge).
        
        Returns:
            Allocated drag source class
        """
        try:
            import objc
            
            # Create Objective-C class
            DragSourceClass = objc.createClass(
                "PanoptikonTableDragSource",
                superclass=objc.lookUpClass("NSObject"),
                protocols=["NSTableViewDataSource"]
            )
            
            # Add methods
            def init(self):
                """Initialize the drag source."""
                self = objc.super(DragSourceClass, self).init()
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
            
            def tableView_writeRowsWithIndexes_toPasteboard_(self, table_view, row_indexes, pasteboard):
                """Handle drag start.
                
                Args:
                    table_view: The table view
                    row_indexes: The row indexes
                    pasteboard: The pasteboard
                
                Returns:
                    True if drag started, False otherwise
                """
                import AppKit
                import Foundation
                
                # Get selected files
                files = []
                for i in range(row_indexes.count()):
                    row = row_indexes.objectAtIndex_(i)
                    # In a real implementation, this would get the file at the row
                    files.append(f"/path/to/file{row}")
                
                # Set pasteboard data
                pasteboard.declareTypes_owner_([AppKit.NSFilenamesPboardType], None)
                pasteboard.setPropertyList_forType_(files, AppKit.NSFilenamesPboardType)
                
                # Notify callback
                if hasattr(self, "callback") and self.callback is not None:
                    self.callback.handle_drag_start(self.is_main, files)
                
                return True
            
            # Register methods with the class
            objc.registerSelector(b"init", [b"@", b":", b"@"])
            objc.registerSelector(b"setCallback:", [b"v", b":", b"@"])
            objc.registerSelector(b"setIsMain:", [b"v", b":", b"B"])
            objc.registerSelector(b"tableView:writeRowsWithIndexes:toPasteboard:", [b"B", b":", b"@", b"@", b"@"])
            
            DragSourceClass.addMethod(b"init", init)
            DragSourceClass.addMethod(b"setCallback:", setCallback_)
            DragSourceClass.addMethod(b"setIsMain:", setIsMain_)
            DragSourceClass.addMethod(b"tableView:writeRowsWithIndexes:toPasteboard:", tableView_writeRowsWithIndexes_toPasteboard_)
            
            return DragSourceClass.alloc()
        except ImportError:
            # Return dummy object if PyObjC not available
            return DummyDragSource.alloc()

class DummyDragSource:
    """Dummy drag source for when PyObjC is not available."""
    
    @classmethod
    def alloc(cls):
        """Allocate the drag source class."""
        return cls()
    
    def init(self):
        """Initialize the drag source."""
        return self
    
    def setCallback_(self, callback):
        """Set the callback object."""
        pass
    
    def setIsMain_(self, is_main):
        """Set whether this is the main window."""
        pass
```

#### Verification:
- Test drag source initialization
- Verify callback invocation
- Test pasteboard data setting
- Check is_main flag handling

### SEGMENT 2: Drop Target Implementation
#### Test-First:
- Drop targets initialize correctly
- Drop validation works correctly
- Drop handling responds appropriately
- Target window activates on drop

#### Implementation:
```python
# src/panoptikon/ui/drop_target.py

from typing import Any, List, Protocol

class DropTargetDelegate(Protocol):
    """Protocol for drop target delegates."""
    
    def handle_drop(self, is_main: bool) -> bool:
        """Handle drop in a window.
        
        Args:
            is_main: Whether the drop is in the main window
            
        Returns:
            True if drop handled, False otherwise
        """
        ...

class TableDropTarget:
    """NSTableView drop target implementation."""
    
    @classmethod
    def alloc(cls):
        """Allocate the drop target class (PyObjC bridge).
        
        Returns:
            Allocated drop target class
        """
        try:
            import objc
            
            # Create Objective-C class
            DropTargetClass = objc.createClass(
                "PanoptikonTableDropTarget",
                superclass=objc.lookUpClass("NSObject"),
                protocols=["NSTableViewDataSource"]
            )
            
            # Add methods
            def init(self):
                """Initialize the drop target."""
                self = objc.super(DropTargetClass, self).init()
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
            
            def tableView_validateDrop_proposedRow_proposedDropOperation_(self, table_view, info, row, operation):
                """Validate drop.
                
                Args:
                    table_view: The table view
                    info: The drag info
                    row: The proposed row
                    operation: The proposed operation
                
                Returns:
                    The operation to perform
                """
                import AppKit
                
                # Accept drop if it contains files
                pasteboard = info.draggingPasteboard()
                if pasteboard.availableTypeFromArray_([AppKit.NSFilenamesPboardType]):
                    return AppKit.NSDragOperationCopy
                
                return AppKit.NSDragOperationNone
            
            def tableView_acceptDrop_row_dropOperation_(self, table_view, info, row, operation):
                """Accept drop.
                
                Args:
                    table_view: The table view
                    info: The drag info
                    row: The drop row
                    operation: The drop operation
                
                Returns:
                    True if drop accepted, False otherwise
                """
                # Notify callback
                if hasattr(self, "callback") and self.callback is not None:
                    return self.callback.handle_drop(self.is_main)
                
                return False
            
            # Register methods with the class
            objc.registerSelector(b"init", [b"@", b":", b"@"])
            objc.registerSelector(b"setCallback:", [b"v", b":", b"@"])
            objc.registerSelector(b"setIsMain:", [b"v", b":", b"B"])
            objc.registerSelector(b"tableView:validateDrop:proposedRow:proposedDropOperation:", [b"I", b":", b"@", b"@", b"i", b"I"])
            objc.registerSelector(b"tableView:acceptDrop:row:dropOperation:", [b"B", b":", b"@", b"@", b"i", b"I"])
            
            DropTargetClass.addMethod(b"init", init)
            DropTargetClass.addMethod(b"setCallback:", setCallback_)
            DropTargetClass.addMethod(b"setIsMain:", setIsMain_)
            DropTargetClass.addMethod(b"tableView:validateDrop:proposedRow:proposedDropOperation:", tableView_validateDrop_proposedRow_proposedDropOperation_)
            DropTargetClass.addMethod(b"tableView:acceptDrop:row:dropOperation:", tableView_acceptDrop_row_dropOperation_)
            
            return DropTargetClass.alloc()
        except ImportError:
            # Return dummy object if PyObjC not available
            return DummyDropTarget.alloc()

class DummyDropTarget:
    """Dummy drop target for when PyObjC is not available."""
    
    @classmethod
    def alloc(cls):
        """Allocate the drop target class."""
        return cls()
    
    def init(self):
        """Initialize the drop target."""
        return self
    
    def setCallback_(self, callback):
        """Set the callback object."""
        pass
    
    def setIsMain_(self, is_main):
        """Set whether this is the main window."""
        pass
```

#### Verification:
- Test drop target initialization
- Verify validation functionality
- Test drop acceptance
- Check callback invocation

### SEGMENT 3: Drag Coordination
#### Test-First:
- Drag coordination works between windows
- Drag source tracking is maintained
- Files are correctly identified
- Window activation happens at right time

#### Implementation:
```python
# Update src/panoptikon/ui/macos_app.py with drag-drop implementation

# Add to FileSearchApp class

def _setup_drag_drop(self, table_view: Any, is_main: bool) -> None:
    """Set up drag and drop for a table view.
    
    Args:
        table_view: The table view
        is_main: Whether this is the main window
    """
    if not self._pyobjc_available:
        return
        
    import AppKit
    
    # Register for drag operations
    table_view.registerForDraggedTypes_([AppKit.NSFilenamesPboardType])
    
    # Create drag source/destination handlers
    table_drag_source = TableDragSource.alloc().init()
    table_drag_source.setCallback_(self)
    table_drag_source.setIsMain_(is_main)
    
    table_drag_dest = TableDropTarget.alloc().init()
    table_drag_dest.setCallback_(self)
    table_drag_dest.setIsMain_(is_main)
    
    # Set delegates
    table_view.setDraggingSource_(table_drag_source)
    table_view.setDraggingDestination_(table_drag_dest)
    
def handle_drag_start(self, is_main: bool, files: List[str]) -> None:
    """Handle drag start from a window.
    
    Args:
        is_main: Whether the drag is from the main window
        files: List of files being dragged
    """
    # Activate the source window
    if is_main:
        self._window_manager.activate_main_window()
    else:
        self._window_manager.activate_secondary_window()
        
    # Store drag source info for drop handling
    self._drag_source_is_main = is_main
    self._dragged_files = files
    
def handle_drop(self, is_main: bool) -> bool:
    """Handle drop in a window.
    
    Args:
        is_main: Whether the drop is in the main window
        
    Returns:
        True if drop handled, False otherwise
    """
    # Ensure we have a valid drag operation
    if not hasattr(self, "_drag_source_is_main") or not hasattr(self, "_dragged_files"):
        return False
        
    # Don't allow dropping in same window
    if self._drag_source_is_main == is_main:
        return False
        
    # Activate target window
    if is_main:
        self._window_manager.activate_main_window()
    else:
        self._window_manager.activate_secondary_window()
        
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

#### Verification:
- Test drag setup
- Verify drag start handling
- Test drop handling
- Check window activation

### SEGMENT 4: Operation Finalization
#### Test-First:
- Operations complete successfully
- File lists are properly transferred
- Events are correctly published
- UI updates appropriately

#### Implementation:
```python
# Update src/panoptikon/ui/window_manager.py

# Add to DualWindowManager class

def handle_drag_operation_complete(self, event: WindowDragOperationEvent) -> None:
    """Handle drag operation completion.
    
    Args:
        event: The drag operation event
    """
    # In a real implementation, this would handle any necessary updates
    # after the drag operation is complete
    
    # Update window states
    if event.source_window == "main":
        source_state = self._main_window_state
    else:
        source_state = self._secondary_window_state
        
    if event.target_window == "main":
        target_state = self._main_window_state
    else:
        target_state = self._secondary_window_state
        
    # Log the operation
    print(f"Drag operation: {len(event.files)} files from {event.source_window} to {event.target_window}")
    
    # In a real implementation, this might trigger file operations
    # like move or copy, depending on user preference
```

#### Verification:
- Test operation completion
- Verify state updates
- Test file operations
- Check UI refresh

## 5. STAGE INTEGRATION TEST
- Run integration tests for drag and drop
- Test cross-window operations
- Verify file integrity
- Check UI updates

## 6. PROPAGATE STATE
- Write `stage4_report.md`
- Document drag and drop implementation
- Update mCP with implementation details

---

# STAGE 5 — PERFORMANCE OPTIMIZATION

## 1. LOAD STAGE SPEC
- 📄 From: Dual window specification, integration report, and previous stage reports
- 🔍 Development Phase: UI Framework (Phase 3)

## 2. ANALYZE CONTEXT
- **Stage objectives**: Optimize dual-window performance
- **Interfaces**: Resource management, window rendering
- **Constraints**:
  - Window switching < 100ms
  - Inactive window memory < 10MB
  - No visual lag during transitions
- **Dependencies**:
  - All previous stages

## 3. STAGE SEGMENTATION

### SEGMENT 1: Window Switching Optimization
- Measure switching performance
- Optimize state transitions
- Reduce activation overhead

### SEGMENT 2: Memory Footprint Reduction
- Analyze memory usage
- Implement aggressive caching
- Optimize storage formats

### SEGMENT 3: Visual Transition Enhancement
- Smooth visual state changes
- Optimize rendering pipeline
- Reduce UI flicker

### SEGMENT 4: Performance Testing
- Create comprehensive benchmarks
- Test various scenarios
- Verify metrics

## 4. IMPLEMENTATION AND TESTING

### SEGMENT 1: Window Switching Optimization
#### Test-First:
- Window switching completes in < 100ms
- Time is measured accurately
- Transitions run efficiently

#### Implementation:
```python
# Update DualWindowManager._activate_window method with performance optimizations

import time

def _activate_window(self, window_type: str) -> None:
    """Activate a specific window and deactivate the other.
    
    Args:
        window_type: The window type to activate ("main" or "secondary")
    """
    if window_type not in ["main", "secondary"]:
        return
        
    if window_type == self._active_window:
        return  # Already active
        
    # Measure performance
    start_time = time.time()
    
    # Deactivate current window (minimal operations)
    previous_window = self._active_window
    
    # Update state flags first (fast operation)
    if previous_window == "main":
        self._main_window_state.is_active = False
    else:
        if self._secondary_window_state:
            self._secondary_window_state.is_active = False
    
    # Update active window
    self._active_window = window_type
    
    # Update new active window state
    if window_type == "main":
        self._main_window_state.is_active = True
    else:
        if self._secondary_window_state:
            self._secondary_window_state.is_active = True
    
    # Immediately publish activation event
    # This allows UI to start updating visuals while resource operations happen
    self._event_bus.publish(
        WindowActivatedEvent(
            window_type=window_type,
            previous_window=previous_window
        )
    )
    
    # Now handle resource operations in background or with lower priority
    # These can happen while the UI is already updating
    if previous_window == "main":
        self.cache_window_state("main")
        self._suspend_window_resources("main")
    else:
        if self._secondary_window_state:
            self.cache_window_state("secondary")
            self._suspend_window_resources("secondary")
    
    if window_type == "main":
        self.restore_window_state("main")
        self._resume_window_resources("main")
    else:
        if self._secondary_window_state:
            self.restore_window_state("secondary")
            self._resume_window_resources("secondary")
    
    # Check performance
    elapsed_time = (time.time() - start_time) * 1000
    if elapsed_time > 100:
        print(f"Warning: Window activation took {elapsed_time:.2f}ms (target: <100ms)")
```

#### Verification:
- Test window switch timing
- Verify state changes
- Test visual response
- Check resource operations

### SEGMENT 2: Memory Footprint Reduction
#### Test-First:
- Memory usage stays below 10MB for inactive window
- Resources are properly released
- Cache size is limited

#### Implementation:
```python
# Update WindowState with memory optimizations

class WindowState:
    """Represents the state of a window."""
    
    def __init__(self, is_main: bool) -> None:
        """Initialize window state.
        
        Args:
            is_main: Whether this is the main window
        """
        self.is_main = is_main
        self.is_active = is_main  # Main window starts as active
        self.search_query = ""
        self.selected_files: List[str] = []
        self.search_results: List[Any] = []
        self.scroll_position: Tuple[float, float] = (0, 0)
        self.filter_state: Dict[str, Any] = {}
        self.column_settings: Dict[str, Any] = {}
        
        # Memory optimizations
        self._full_results_cache: Optional[List[Any]] = None
        self._compressed_results: Optional[bytes] = None
        self._result_size_limit = 1000  # Max number of results to cache
    
    def minimize_memory_usage(self) -> None:
        """Minimize memory usage for inactive window."""
        if len(self.search_results) > self._result_size_limit:
            # Store limited number of results
            self._full_results_cache = self.search_results
            self.search_results = self.search_results[:self._result_size_limit]
        
        # In a real implementation, this might compress state or
        # store it in a more memory-efficient format
        
    def restore_memory_usage(self) -> None:
        """Restore memory usage for active window."""
        if self._full_results_cache is not None:
            self.search_results = self._full_results_cache
            self._full_results_cache = None
            
        # In a real implementation, this might decompress state or
        # restore it from a memory-efficient format
```

#### Verification:
- Test memory usage
- Verify cache functionality
- Test state restoration
- Check compression efficiency

### SEGMENT 3: Visual Transition Enhancement
#### Test-First:
- Visual transitions are smooth
- UI remains responsive
- Style changes are clear

#### Implementation:
```python
# Update visual transition code in FileSearchApp

def _update_window_appearance(self, active_window: str, inactive_window: str) -> None:
    """Update window appearance based on active/inactive state.
    
    Args:
        active_window: The active window type
        inactive_window: The previous active window type
    """
    if not self._pyobjc_available:
        return
        
    import AppKit
    
    # Optimize transitions by using animation blocks
    
    # First, update titles immediately for instant visual feedback
    if self._main_window:
        if active_window == "main":
            self._main_window.setTitle_("Panoptikon File Search")
        else:
            self._main_window.setTitle_("Panoptikon File Search [INACTIVE]")
            
    if self._secondary_window:
        if active_window == "secondary":
            self._secondary_window.setTitle_("Panoptikon - Secondary Window")
        else:
            self._secondary_window.setTitle_("Panoptikon - Secondary Window [INACTIVE]")
    
    # Then, update the appearance with animation
    AppKit.NSAnimationContext.beginGrouping()
    AppKit.NSAnimationContext.currentContext().setDuration_(0.15)  # Short duration for smoothness
    
    if self._main_window:
        if active_window == "main":
            self._apply_active_styling(self._main_window)
        else:
            self._apply_inactive_styling(self._main_window)
            
    if self._secondary_window:
        if active_window == "secondary":
            self._apply_active_styling(self._secondary_window)
        else:
            self._apply_inactive_styling(self._secondary_window)
    
    AppKit.NSAnimationContext.endGrouping()
```

#### Verification:
- Test transition smoothness
- Verify animation performance
- Test visual clarity
- Check UI responsiveness

### SEGMENT 4: Performance Testing
#### Test-First:
- Tests cover all performance metrics
- Results are measured accurately
- Benchmarks are comprehensive

#### Implementation:
```python
# src/tests/ui/test_performance.py

import time
import unittest
from unittest.mock import MagicMock, patch

from panoptikon.core.events import EventBus
from panoptikon.ui.window_manager import DualWindowManager
from panoptikon.ui.window_state import WindowState

class DualWindowPerformanceTest(unittest.TestCase):
    """Test dual window performance."""
    
    def setUp(self):
        """Set up test environment."""
        self.event_bus = MagicMock(spec=EventBus)
        self.window_manager = DualWindowManager(self.event_bus)
        
        # Create secondary window
        self.window_manager.create_secondary_window()
        
        # Reset event bus for clean test
        self.event_bus.reset_mock()
        
    def test_window_switching_performance(self):
        """Test window switching performance."""
        # Ensure main window is active
        self.window_manager.activate_main_window()
        self.event_bus.reset_mock()
        
        # Measure switch to secondary
        start_time = time.time()
        self.window_manager.activate_secondary_window()
        secondary_time = (time.time() - start_time) * 1000
        
        # Measure switch to main
        start_time = time.time()
        self.window_manager.activate_main_window()
        main_time = (time.time() - start_time) * 1000
        
        # Verify performance
        self.assertLess(secondary_time, 100, "Secondary window activation took too long")
        self.assertLess(main_time, 100, "Main window activation took too long")
        
    def test_memory_usage(self):
        """Test memory usage."""
        import sys
        import gc
        
        # Create window states with realistic data
        main_state = self.window_manager.get_main_window_state()
        secondary_state = self.window_manager.get_secondary_window_state()
        
        # Fill with test data
        main_state.search_results = [["File 1", "/path/to/file1", "10 KB", "2023-01-01"]] * 1000
        secondary_state.search_results = [["File 2", "/path/to/file2", "20 KB", "2023-01-02"]] * 1000
        
        # Activate main window (secondary becomes inactive)
        self.window_manager.activate_main_window()
        
        # Force garbage collection
        gc.collect()
        
        # Measure secondary window state size
        secondary_size = sys.getsizeof(secondary_state)
        for attr in dir(secondary_state):
            if not attr.startswith('_') and not callable(getattr(secondary_state, attr)):
                secondary_size += sys.getsizeof(getattr(secondary_state, attr))
                
        # Convert to MB
        secondary_size_mb = secondary_size / (1024 * 1024)
        
        # Verify memory usage
        self.assertLess(secondary_size_mb, 10, "Secondary window uses too much memory")
```

#### Verification:
- Test window switching speed
- Verify memory usage
- Test resource allocation
- Check overall performance

## 5. STAGE INTEGRATION TEST
- Run all performance tests
- Measure real-world scenarios
- Verify metrics are met
- Identify any remaining issues

## 6. PROPAGATE STATE
- Write `stage5_report.md`
- Document performance optimization results
- Update mCP with implementation details

---

## 📦 SUMMARY

This multi-stage refactoring plan provides a comprehensive approach to implementing the dual-window feature in Panoptikon. By following the V6.1 multi-stage template methodology, the implementation is broken down into manageable, testable segments that ensure quality and maintainability.

The key highlights of this implementation are:

1. **Window Management Core** - Establishes the foundation with DualWindowManager and WindowState classes.
2. **UI Implementation** - Refactors the UI to support dual windows with independent search contexts.
3. **Resource Management** - Ensures efficient resource usage with window-specific allocation.
4. **Drag and Drop Support** - Implements the USP of cross-window drag-and-drop operations.
5. **Performance Optimization** - Ensures the implementation meets performance targets.

Each stage builds upon the previous ones, with clear verification steps to ensure quality. The plan adheres to the Land Rover philosophy of simplicity, robustness, and fitness for purpose, delivering a dual-window implementation that satisfies user needs without unnecessary complexity.
