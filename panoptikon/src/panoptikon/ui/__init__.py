"""UI components for Panoptikon.

This module is responsible for:
1. Providing the graphical user interface
2. Handling user input and search queries
3. Displaying search results
4. Managing user preferences and settings

The UI is built using PyObjC for native macOS integration.
"""

from panoptikon.ui.app_launcher import launch

__all__ = ["launch"]
