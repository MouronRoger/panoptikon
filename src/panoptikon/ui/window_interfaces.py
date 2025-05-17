from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from panoptikon.core.service import ServiceInterface


class WindowState:
    """Class defining window state properties."""

    def __init__(self, is_main: bool) -> None:
        """Initialize window state."""
        self.is_main: bool = is_main
        self.is_active: bool = is_main  # Main window starts as active
        self.search_query: str = ""
        self.selected_files: List[str] = []
        self.scroll_position: Tuple[float, float] = (0.0, 0.0)


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
    def coordinate_drag_operation(
        self, is_from_main_window: bool, files: List[str]
    ) -> None:
        """Coordinate a drag operation between windows."""
        pass
