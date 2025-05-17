# # Dual-Window Feature Preparation Plan
# 1. Current State Analysis
The project is currently at **Stage 4.3 (Schema Migration Framework)**, which means:
* Core service container architecture is implemented
* Event bus system is functional
* Database schema and migration framework is in place
* No UI components have been implemented yet

⠀This positions us at an ideal point to prepare for the dual-window feature with minimal refactoring.
# 2. Refactoring Plan Using V6.2 Multi-Stage Template
# 🚧 STAGE R — DUAL-WINDOW PREPARATION REFACTORING
# 1. LOAD STAGE SPEC
* 📄 From: dual-window-spec.md, dual-window-integration-report.md, dual-window-refactoring-report.md
* 🔍 Development Phase: Foundation (pre-UI preparation)

⠀2. ANALYZE CONTEXT
* **Stage objectives**: Prepare existing infrastructure for dual-window support
* **Interfaces**: Service container, event bus, application lifecycle
* **Constraints**:
  * Minimal changes to existing code
  * No UI implementation yet
  * Must maintain backward compatibility
* **Dependencies**:
  * Service container implementation
  * EventBus for cross-component communication
  * Application lifecycle management

⠀3. STAGE SEGMENTATION
### SEGMENT 1: Window-Related Event Definitions
* Define all window-related events
* No implementation, just type definitions
* Ensure event hierarchy follows existing patterns

⠀SEGMENT 2: DualWindowManager Service Interface
* Create service interface for window management
* Define public methods
* Document behavior requirements

⠀SEGMENT 3: Service Registration Hooks
* Prepare service container for DualWindowManager
* Add lifecycle hooks
* Document integration points

⠀4. IMPLEMENTATION AND TESTING
### SEGMENT 1: Window-Related Event Definitions
**Test-First:**
* Event definitions match application requirements
* Events inherit correctly from EventBase
* Events include all required properties

⠀**Implementation:**

### python
*# src/panoptikon/ui/events.py*

from dataclasses import dataclass
from typing import List, Tuple

from panoptikon.core.events import EventBase

@dataclass
class WindowEvent(EventBase):
    """Base class for all window-related events."""
    pass

@dataclass
class SecondaryWindowCreatedEvent(WindowEvent):
    """Event issued when the secondary window is created."""
    position: Tuple[int, int]

@dataclass
class SecondaryWindowClosedEvent(WindowEvent):
    """Event issued when the secondary window is closed."""
    pass

@dataclass
class WindowActivatedEvent(WindowEvent):
    """Event issued when a window is activated."""
    window_type: str  *# "main" or "secondary"*
    previous_window: str  *# "main" or "secondary"*

@dataclass
class WindowResourceSuspendedEvent(WindowEvent):
    """Event issued when a window's resources are suspended."""
    window_type: str  *# "main" or "secondary"*

@dataclass
class WindowResourceResumedEvent(WindowEvent):
    """Event issued when a window's resources are resumed."""
    window_type: str  *# "main" or "secondary"*

@dataclass
class WindowDragOperationEvent(WindowEvent):
    """Event issued for drag operations between windows."""
    source_window: str  *# "main" or "secondary"*
    target_window: str  *# "main" or "secondary"* 
    files: List[str]
**Verification:**
* Test event creation and inheritance
* Verify property access
* Check equality and hashing behavior

⠀SEGMENT 2: DualWindowManager Service Interface
**Test-First:**
* Interface defines all required methods
* Method signatures match application requirements
* Interface follows existing service patterns

⠀**Implementation:**

### python
*# src/panoptikon/ui/window_interfaces.py*

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from panoptikon.core.service import ServiceInterface

class WindowState:
    """Interface defining window state properties."""
    
    def __init__(self, is_main: bool) -> None:
        """Initialize window state."""
        self.is_main = is_main
        self.is_active = is_main  *# Main window starts as active*
        self.search_query = ""
        self.selected_files: List[str] = []
        self.scroll_position: Tuple[float, float] = (0, 0)

class WindowManagerInterface(ServiceInterface, ABC):
    """Interface for dual-window management."""
    
    @abstractmethod
    def toggle_secondary_window(self) -> None:
        """Toggle the secondary window (create if doesn't exist, close if it does)."""
        pass
    
    @abstractmethod
    def create_secondary_window(self) -> None:
        """Create the secondary window."""
        pass
    
    @abstractmethod
    def close_secondary_window(self) -> None:
        """Close the secondary window."""
        pass
    
    @abstractmethod
    def activate_main_window(self) -> None:
        """Activate the main window."""
        pass
    
    @abstractmethod
    def activate_secondary_window(self) -> None:
        """Activate the secondary window."""
        pass
    
    @abstractmethod
    def is_secondary_window_open(self) -> bool:
        """Check if secondary window is open."""
        pass
    
    @abstractmethod
    def get_active_window_type(self) -> str:
        """Get the active window type ('main' or 'secondary')."""
        pass
    
    @abstractmethod
    def get_main_window_state(self) -> WindowState:
        """Get the main window state."""
        pass
    
    @abstractmethod
    def get_secondary_window_state(self) -> Optional[WindowState]:
        """Get the secondary window state."""
        pass
    
    @abstractmethod
    def coordinate_drag_operation(self, is_from_main_window: bool, files: List[str]) -> None:
        """Coordinate a drag operation between windows."""
        pass
**Verification:**
* Test interface completeness
* Verify inheritance from ServiceInterface
* Check method signatures

⠀SEGMENT 3: Service Registration Hooks
**Test-First:**
* Service interfaces can be registered
* Lifecycle hooks integrate properly
* Application handles window-related events

⠀**Implementation:**

### python
*# src/panoptikon/core/service_extensions.py*

from typing import Callable, Dict, Type

from panoptikon.core.service import ServiceContainer
from panoptikon.ui.window_interfaces import WindowManagerInterface

def register_window_manager_hooks(container: ServiceContainer) -> None:
    """Register hooks for the window manager service.
    
    This function prepares the service container for a future
    implementation of the DualWindowManager. It doesn't register
    an actual implementation, just prepares the container.
    
    Args:
        container: The service container
    """
    *# Register placeholder for later implementation*
    container.register_factory_hook(
        WindowManagerInterface,
        lambda impl: impl,
        priority=100  *# High priority to ensure early initialization*
    )
    
    *# Register shutdown hook*
    container.register_shutdown_hook(
        WindowManagerInterface,
        lambda svc: svc.close_secondary_window() if svc.is_secondary_window_open() else None,
        priority=10  *# Low priority to ensure late shutdown*
    )

### python
*# Update src/panoptikon/app.py to add lifecycle hooks*

from panoptikon.core.service_extensions import register_window_manager_hooks

*# Add to application initialization*
def initialize_application(container):
    *# Existing initialization code...*
    
    *# Register window manager hooks*
    register_window_manager_hooks(container)
    
    *# Rest of initialization...*
**Verification:**
* Test hook registration
* Verify shutdown sequence
* Check container integration

⠀5. STAGE INTEGRATION TEST
* Run integration tests for all segments
* Verify service interfaces are properly defined
* Ensure lifecycle hooks are registered
* Check event definitions are accessible

⠀6. PROPAGATE STATE
* Write dual_window_preparation_report.md
* Update MCP with implementation details
* Document integration points for future stages

⠀
