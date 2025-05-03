"""Application launcher for Panoptikon.

This module handles the initialization and launching of the UI application.
"""

import sys
from typing import Any, Dict, List

try:
    import AppKit
    from PyObjCTools import AppHelper
except ImportError:
    AppKit = None
    AppHelper = None


def launch() -> None:
    """Launch the Panoptikon application.

    This function initializes the UI and starts the application's main event loop.
    On macOS, it uses PyObjC to create a native application. On other platforms,
    a fallback UI may be used in the future.

    Raises:
        ImportError: If PyObjC is not available on macOS.
    """
    # Check if we're on macOS and have PyObjC
    if sys.platform != "darwin":
        print("Currently, only macOS is supported.")
        return
    
    if AppKit is None or AppHelper is None:
        raise ImportError("PyObjC is required for the macOS UI. Please install it with 'pip install pyobjc'.")
    
    # Import UI components here to avoid circular imports
    from panoptikon.ui.main_window import MainWindow
    from panoptikon.ui.search_controller import SearchController
    
    # Initialize the application
    app = AppKit.NSApplication.sharedApplication()
    
    # Load configuration
    from panoptikon.config import config_manager
    config = config_manager.get_config()
    
    # Initialize controllers
    search_controller = SearchController()
    
    # Create the main window
    main_window = MainWindow(search_controller)
    main_window.show()
    
    # Start the application event loop
    AppHelper.runEventLoop()


class SearchResult:
    """Represents a search result item in the UI.

    Attributes:
        file_path: The full path to the file.
        file_name: The name of the file.
        file_extension: The file extension.
        file_size: The file size in bytes.
        modified_time: The last modified time as a Unix timestamp.
    """

    def __init__(
        self,
        file_path: str,
        file_name: str,
        file_extension: str,
        file_size: int,
        modified_time: float
    ) -> None:
        """Initialize a search result.

        Args:
            file_path: The full path to the file.
            file_name: The name of the file.
            file_extension: The file extension.
            file_size: The file size in bytes.
            modified_time: The last modified time as a Unix timestamp.
        """
        self.file_path = file_path
        self.file_name = file_name
        self.file_extension = file_extension
        self.file_size = file_size
        self.modified_time = modified_time


def format_search_results(results: List[Dict[str, Any]]) -> List[SearchResult]:
    """Format raw search results into UI-friendly objects.

    Args:
        results: List of raw search result dictionaries from the database.

    Returns:
        List of SearchResult objects.
    """
    formatted_results = []
    
    for result in results:
        search_result = SearchResult(
            file_path=result["path"],
            file_name=result["name"],
            file_extension=result.get("extension", ""),
            file_size=result["size"],
            modified_time=result["modified_time"]
        )
        formatted_results.append(search_result)
    
    return formatted_results 