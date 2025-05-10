"""MacOS application using PyObjC with proper type safety.

This module demonstrates how to implement a macOS application using PyObjC
while maintaining type safety through the boundary pattern.
"""

from __future__ import annotations

from typing import Any, List, Protocol

# All PyObjC imports are contained in the wrapper classes
# or used with type: ignore to maintain clean type checking
from panoptikon.ui.objc_wrappers import (
    SearchFieldWrapper,
    SegmentedControlWrapper,
    TableViewWrapper,
)
from panoptikon.ui.validators import validate_table_data_source


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
        # We'll import PyObjC modules only within the methods that use them
        # to keep the type checker happy in the rest of the code
        try:
            import AppKit  # type: ignore
            import Foundation  # type: ignore
            import objc  # type: ignore

            self._pyobjc_available = True
        except ImportError:
            self._pyobjc_available = False
            print("PyObjC not available - UI features disabled")
            return

        # Create UI components using our typed wrappers
        self._setup_ui()
        self._files: List[List[str]] = []

    def _setup_ui(self) -> None:
        """Set up the UI components.

        This method creates the application window and UI components.
        """
        if not self._pyobjc_available:
            return

        # Import PyObjC modules only within the methods that use them
        import AppKit  # type: ignore
        import Foundation  # type: ignore

        # Create a window
        frame = (200, 200, 800, 600)  # x, y, width, height
        self._window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            Foundation.NSMakeRect(*frame),
            AppKit.NSWindowStyleMaskTitled
            | AppKit.NSWindowStyleMaskClosable
            | AppKit.NSWindowStyleMaskResizable,
            AppKit.NSBackingStoreBuffered,
            False,
        )
        self._window.setTitle_("Panoptikon File Search")
        self._window.setReleasedWhenClosed_(False)

        # Create a content view
        content_view = self._window.contentView()

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
        import AppKit  # type: ignore
        import Foundation  # type: ignore
        import objc  # type: ignore

        # Create and set table data source
        self._table_delegate = _TableDelegate.alloc().init()
        self._table_data_source = _TableDataSource.alloc().init()
        self._table_data_source.setFiles_(self._files)
        
        # Validate delegates before setting them
        assert validate_table_data_source(self._table_data_source)
        
        # Set delegates
        self._table_view.set_delegate(self._table_delegate)
        self._table_view.set_data_source(self._table_data_source)
        
        # Create and set search field delegate
        self._search_delegate = _SearchFieldDelegate.alloc().init()
        self._search_delegate.setCallback_(self)
        self._search_field.set_delegate(self._search_delegate)
        
        # Set up segmented control action
        self._search_options.set_target_action(self, "onSearchOptionChanged")

    def show(self) -> None:
        """Show the application window."""
        if not self._pyobjc_available:
            print("Cannot show UI - PyObjC not available")
            return

        self._window.makeKeyAndOrderFront_(None)
        
        # Get the shared application and run it
        import AppKit  # type: ignore
        app = AppKit.NSApplication.sharedApplication()
        app.activateIgnoringOtherApps_(True)
        app.run()

    def set_files(self, files: List[List[str]]) -> None:
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

    # This method will be called via PyObjC
    def onSearchOptionChanged(self, sender: Any) -> None:  # type: ignore
        """Called when search option segment changes.

        Args:
            sender: The NSSegmentedControl that sent the action
        """
        option_index = self._search_options.get_selected_segment()
        option_name = ["Name", "Content", "Date", "Size"][option_index]
        print(f"Search option changed to: {option_name}")


# PyObjC delegate and data source classes
# These contain the actual Objective-C integration code and are
# isolated from the rest of the application with type: ignore


# Note: In a real implementation, these would be defined using
# proper PyObjC subclassing techniques. This is a simplified example.
class _TableDataSource:  # type: ignore
    """NSTableViewDataSource implementation."""

    def init(self):
        """Initialize the data source."""
        self = objc.super(_TableDataSource, self).init()
        if self is None:
            return None
        self.files = []
        return self

    def setFiles_(self, files):
        """Set the files data.

        Args:
            files: List of file data
        """
        self.files = files

    def numberOfRowsInTableView_(self, tableView):
        """Return the number of rows.

        Args:
            tableView: The NSTableView

        Returns:
            The number of rows
        """
        return len(self.files)

    def tableView_objectValueForTableColumn_row_(self, tableView, column, row):
        """Return data for a table cell.

        Args:
            tableView: The NSTableView
            column: The NSTableColumn
            row: The row index

        Returns:
            The cell value
        """
        col_id = column.identifier()
        if col_id < len(self.files[row]):
            return self.files[row][int(col_id)]
        return ""


class _TableDelegate:  # type: ignore
    """NSTableViewDelegate implementation."""

    def tableViewSelectionDidChange_(self, notification):
        """Handle selection changes.

        Args:
            notification: The notification object
        """
        tableView = notification.object()
        selectedRow = tableView.selectedRow()
        if selectedRow >= 0:
            print(f"Selected row: {selectedRow}")


class _SearchFieldDelegate:  # type: ignore
    """NSSearchFieldDelegate implementation."""

    def init(self):
        """Initialize the delegate."""
        self = objc.super(_SearchFieldDelegate, self).init()
        if self is None:
            return None
        self.callback = None
        return self

    def setCallback_(self, callback):
        """Set the callback object.

        Args:
            callback: The object that will receive search events
        """
        self.callback = callback

    def controlTextDidChange_(self, notification):
        """Handle text changes.

        Args:
            notification: The notification object
        """
        if self.callback is not None:
            search_field = notification.object()
            text = search_field.stringValue()
            self.callback.on_search_changed(text)

    def controlTextDidEndEditing_(self, notification):
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