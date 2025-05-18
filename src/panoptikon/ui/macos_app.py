"""MacOS application using PyObjC with proper type safety.

This module demonstrates how to implement a macOS application using PyObjC
while maintaining type safety through the boundary pattern.
"""

# pylint: disable=import-error
from __future__ import annotations

import importlib
from types import ModuleType
from typing import Any, Protocol

# All PyObjC imports are contained in the wrapper classes
# or used with type: ignore to maintain clean type checking
from panoptikon.ui.objc_wrappers import (
    SearchFieldWrapper,
    SegmentedControlWrapper,
    TableViewWrapper,
)
from panoptikon.ui.validators import validate_table_data_source

# For type checking
pass


class SearchDelegate(Protocol):
    """Protocol for search field delegates."""

    def on_search_changed(self, search_text: str) -> None:
        """Called when search text changes.

        Args:
            search_text: The current search text
        """
        ...

    def on_search_submitted(self, search_text: str) -> None:
        """Called when search is submitted (enter key).

        Args:
            search_text: The submitted search text
        """
        ...


class FileSearchApp:
    """Main application class using PyObjC boundary pattern.

    This class demonstrates how to implement a macOS application while
    maintaining proper type safety by using wrapper classes that isolate
    the untyped PyObjC code.
    """

    def __init__(self) -> None:
        """Initialize the application."""
        # Buffer for table content – created early so delegates can rely on it.
        self._files: list[list[str]] = []
        self._pyobjc_available: bool
        try:
            # Try importing each required module and confirm they're genuine modules
            for name in ("AppKit", "Foundation", "objc"):
                try:
                    module = importlib.import_module(name)
                    if not isinstance(module, ModuleType):
                        raise ImportError(f"{name} is not a valid module")
                except (ImportError, AttributeError):
                    # Either module not found or has invalid structure
                    raise ImportError(f"Failed to import {name}") from None

            self._pyobjc_available = True
        except ImportError:
            # Any problem importing (or validating) the modules means PyObjC
            # is effectively unavailable for our purposes.
            self._pyobjc_available = False
            print("PyObjC not available - UI features disabled")
            return

        # Create UI components using our typed wrappers
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI components.

        This method creates the application window and UI components.
        """
        if not self._pyobjc_available:
            return

        # Import PyObjC modules only within the methods that use them
        import AppKit  # type: ignore[import-untyped]
        import Foundation  # type: ignore[import-untyped]

        # Create a window
        frame = (200, 200, 800, 600)  # x, y, width, height
        self._window: Any = (
            AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                Foundation.NSMakeRect(*frame),
                AppKit.NSWindowStyleMaskTitled
                | AppKit.NSWindowStyleMaskClosable
                | AppKit.NSWindowStyleMaskResizable,
                AppKit.NSBackingStoreBuffered,
                False,
            )
        )
        self._window.setTitle_("Panoptikon File Search")
        self._window.setReleasedWhenClosed_(False)

        # Create a content view
        content_view: Any = self._window.contentView()

        # Create search field using our wrapper
        search_frame = (20, frame[3] - 60, frame[2] - 40, 30)
        self._search_field = SearchFieldWrapper(search_frame)
        self._search_field.set_placeholder("Search files...")

        # Create segmented control for search options
        segments = ["Name", "Content", "Date", "Size"]
        segment_frame = (20, frame[3] - 100, 300, 24)
        self._search_options = SegmentedControlWrapper(segments, segment_frame, 1)

        # Create table view for results
        table_frame = (20, 20, frame[2] - 40, frame[3] - 140)
        self._table_view = TableViewWrapper(table_frame)
        self._table_view.add_column("0", "Name", 300)
        self._table_view.add_column("1", "Path", 200)
        self._table_view.add_column("2", "Size", 100)
        self._table_view.add_column("3", "Date", 150)

        # Add components to window
        content_view.addSubview_(self._search_field.ns_object)
        content_view.addSubview_(self._search_options.ns_object)
        content_view.addSubview_(self._table_view.ns_scroll_view)

        # Set up delegates
        self._set_up_delegates()

    def _set_up_delegates(self) -> None:
        """Set up the delegates for UI components."""
        if not self._pyobjc_available:
            return

        # Import PyObjC modules only within the methods that use them

        self._table_delegate: Any = _TableDelegate()
        self._table_data_source: Any = _TableDataSource()
        self._table_data_source.setFiles_(self._files)

        # Validate delegates before setting them
        assert validate_table_data_source(self._table_data_source)

        # Set delegates
        self._table_view.set_delegate(self._table_delegate)
        self._table_view.set_data_source(self._table_data_source)

        # Create and set search field delegate
        self._search_delegate: Any = _SearchFieldDelegate()
        self._search_delegate.setCallback_(self)
        self._search_field.set_delegate(self._search_delegate)

        # Set up segmented control action
        self._search_options.set_target_action(self, "on_search_option_changed")

    def show(self) -> None:
        """Show the application window."""
        if not self._pyobjc_available:
            print("Cannot show UI - PyObjC not available")
            return

        self._window.makeKeyAndOrderFront_(None)

        # Get the shared application and run it
        import AppKit

        app: Any = AppKit.NSApplication.sharedApplication()
        app.activateIgnoringOtherApps_(True)
        app.run()

    def set_files(self, files: list[list[str]]) -> None:
        """Set the files to display in the table.

        Args:
            files: List of file data (name, path, size, date)
        """
        self._files = files
        if self._pyobjc_available and hasattr(self, "_table_data_source"):
            self._table_data_source.setFiles_(self._files)
            self._table_view.reload_data()

    def on_search_changed(self, search_text: str) -> None:
        """Called when search text changes.

        Args:
            search_text: The current search text
        """
        print(f"Search changed: {search_text}")
        # In a real implementation, this would update search results

    def on_search_submitted(self, search_text: str) -> None:
        """Called when search is submitted.

        Args:
            search_text: The submitted search text
        """
        print(f"Search submitted: {search_text}")
        # In a real implementation, this would perform the search

    def on_search_option_changed(self, sender: Any) -> None:
        """Called when search option segment changes.

        Args:
            sender: The NSSegmentedControl that sent the action
        """
        option_index: int = self._search_options.get_selected_segment()
        option_name: str = ["Name", "Content", "Date", "Size"][option_index]
        print(f"Search option changed to: {option_name}")


# PyObjC delegate and data source classes
# These contain the actual Objective-C integration code and are
# isolated from the rest of the application with type: ignore


# Note: In a real implementation, these would be defined using
# proper PyObjC subclassing techniques. This is a simplified example.
class _TableDataSource:
    """NSTableViewDataSource implementation."""

    def __init__(self) -> None:
        """Initialize the data source."""
        self.files: list[list[str]] = []

    def setFiles_(self, files: list[list[str]]) -> None:
        """Set the files data.

        Args:
            files: List of file data
        """
        self.files = files

    def numberOfRowsInTableView_(self, table_view: Any) -> int:
        """Return the number of rows.

        Args:
            table_view: The NSTableView

        Returns:
            The number of rows
        """
        return len(self.files)

    def tableView_objectValueForTableColumn_row_(
        self, table_view: Any, column: Any, row: int
    ) -> str:
        """Return data for a table cell.

        Args:
            table_view: The NSTableView
            column: The NSTableColumn
            row: The row index

        Returns:
            The cell value
        """
        col_id = column.identifier()
        if col_id < len(self.files[row]):
            return self.files[row][int(col_id)]
        return ""


class _TableDelegate:
    """NSTableViewDelegate implementation."""

    def __init__(self) -> None:
        pass

    def tableViewSelectionDidChange_(self, notification: Any) -> None:
        """Handle selection changes.

        Args:
            notification: The notification object
        """
        table_view = notification.object()
        selected_row = table_view.selectedRow()
        if selected_row >= 0:
            print(f"Selected row: {selected_row}")


class _SearchFieldDelegate:
    """NSSearchFieldDelegate implementation."""

    def __init__(self) -> None:
        self.callback: Any = None

    def setCallback_(self, callback: Any) -> None:
        """Set the callback object.

        Args:
            callback: The object that will receive search events
        """
        self.callback = callback

    def controlTextDidChange_(self, notification: Any) -> None:
        """Handle text changes.

        Args:
            notification: The notification object
        """
        if self.callback is not None:
            search_field = notification.object()
            text = search_field.stringValue()
            self.callback.on_search_changed(text)

    def controlTextDidEndEditing_(self, notification: Any) -> None:
        """Handle end of editing (Enter key).

        Args:
            notification: The notification object
        """
        if self.callback is not None:
            search_field = notification.object()
            text = search_field.stringValue()
            # Check if Enter key was pressed (not Tab or other ending)
            if notification.userInfo()["NSTextMovement"] == 13:  # Enter key
                self.callback.on_search_submitted(text)


def main() -> None:
    """Run the application."""
    app = FileSearchApp()

    # Set up some sample data
    sample_files = [
        ["document.txt", "/Users/user/Documents/document.txt", "10 KB", "2023-01-15"],
        ["image.jpg", "/Users/user/Pictures/image.jpg", "1.2 MB", "2023-02-20"],
        ["notes.md", "/Users/user/Documents/notes.md", "5 KB", "2023-03-10"],
    ]
    app.set_files(sample_files)

    # Show the application
    app.show()


if __name__ == "__main__":
    main()
