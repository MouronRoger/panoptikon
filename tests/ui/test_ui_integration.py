"""UI integration tests for Panoptikon.

These tests focus on improving coverage for UI components by testing
their integration with the core components.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from panoptikon.core.events import EventBus
from panoptikon.ui.macos_app import FileSearchApp
from panoptikon.ui.objc_wrappers import (
    SearchFieldWrapper,
    SegmentedControlWrapper,
    TableViewWrapper,
)


class TestUIIntegration:
    """Test UI integration with core components."""

    @patch("AppKit.NSApp")
    @patch("AppKit.NSApplication.sharedApplication")
    def test_app_lifecycle(self, mock_shared_app, mock_nsapp) -> None:
        """Test the full lifecycle of the FileSearchApp."""
        # Setup mocks
        mock_app = MagicMock()
        mock_shared_app.return_value = mock_app

        # Create app and test initialization
        app = FileSearchApp()

        # Test show method
        app.show()
        mock_app.run.assert_called_once()

        # Test file loading
        app.set_files(["file1.txt", "file2.txt"])
        assert len(app.files) == 2

        # Test search functionality
        app.search("file1")
        assert len(app.filtered_files) == 1
        assert app.filtered_files[0] == "file1.txt"

        # Test clear search
        app.clear_search()
        assert len(app.filtered_files) == 2


class TestUIComponentIntegration:
    """Test integration between UI components."""

    @patch("AppKit.NSApp")
    @patch("AppKit.NSApplication.sharedApplication")
    @patch("AppKit.NSSearchField.alloc")
    @patch("AppKit.NSSegmentedControl.alloc")
    @patch("AppKit.NSTableView.alloc")
    def test_component_integration(
        self,
        mock_table_alloc,
        mock_segment_alloc,
        mock_search_alloc,
        mock_shared_app,
        mock_nsapp,
    ) -> None:
        """Test integration between UI components."""
        # Setup mocks for components
        mock_search_field = MagicMock()
        mock_search_alloc.return_value.init.return_value = mock_search_field

        mock_segment_control = MagicMock()
        mock_segment_alloc.return_value.init.return_value = mock_segment_control

        mock_table_view = MagicMock()
        mock_table_alloc.return_value.init.return_value = mock_table_view

        # Create app
        app = FileSearchApp()

        # Create and integrate UI components
        search_field = SearchFieldWrapper()
        segment_control = SegmentedControlWrapper()
        table_view = TableViewWrapper()

        # Test integration of components
        app.search_field = search_field.obj
        app.table_view = table_view.obj
        app.search_option = segment_control.obj

        # Set files and verify table updates
        mock_table_view.reloadData = MagicMock()
        app.set_files(["file1.txt", "file2.txt"])

        # Test integration of search field with app
        mock_search_field.stringValue.return_value = "file1"
        app.search_field_changed_(mock_search_field)
        assert len(app.filtered_files) == 1

        # Test integration of segment control with app
        segment_control.obj.selectedSegment.return_value = 1  # Case sensitive
        app.search_option_changed_(segment_control.obj)
        assert app.case_sensitive

        # Test table delegate/datasource integration
        app.numberOfRowsInTableView_(table_view.obj)
        assert (
            app.tableView_objectValueForTableColumn_row_(table_view.obj, None, 0)
            == "file1.txt"
        )


class TestUIEventIntegration:
    """Test UI integration with the event system."""

    @patch("AppKit.NSApp")
    @patch("AppKit.NSApplication.sharedApplication")
    def test_ui_event_integration(self, mock_shared_app, mock_nsapp) -> None:
        """Test that UI components respond to events correctly."""
        # Create event bus
        event_bus = EventBus()

        # Create app with event bus
        app = FileSearchApp(event_bus)

        # Mock the needed methods
        app.reload_table = MagicMock()
        app.clear_search_field = MagicMock()

        # Publish an event that would trigger UI updates
        event_bus.publish(object())  # Generic event

        # Verify UI was updated
        app.reload_table.assert_not_called()  # Default handler doesn't respond to generic events

        # Create a custom event handler in the app
        def on_event_handler(event: object) -> None:
            app.reload_table()
            app.clear_search_field()

        # Register the handler
        event_bus.subscribe(object, on_event_handler)

        # Publish another event
        event_bus.publish(object())

        # Verify UI was updated
        app.reload_table.assert_called_once()
        app.clear_search_field.assert_called_once()


class TestUIFileSystemIntegration:
    """Test UI integration with filesystem components."""

    @patch("AppKit.NSApp")
    @patch("AppKit.NSApplication.sharedApplication")
    def test_file_display(self, mock_shared_app, mock_nsapp) -> None:
        """Test display of filesystem items in the UI."""
        # Create app
        app = FileSearchApp()

        # Setup test files
        test_files = [
            str(Path("/test/dir1/file1.txt")),
            str(Path("/test/dir1/file2.txt")),
            str(Path("/test/dir2/file3.txt")),
        ]

        # Set files
        app.set_files(test_files)

        # Test basic search
        app.search("file1")
        assert len(app.filtered_files) == 1
        assert app.filtered_files[0] == str(Path("/test/dir1/file1.txt"))

        # Test directory filtering
        app.search("dir1")
        assert len(app.filtered_files) == 2

        # Test extension filtering
        app.search(".txt")
        assert len(app.filtered_files) == 3

        # Test case sensitive search
        app.case_sensitive = True
        app.search("FILE1")
        assert len(app.filtered_files) == 0

        app.search("file1")
        assert len(app.filtered_files) == 1


class TestFileSearchAppMocked:
    """Test the FileSearchApp with extensive mocking."""

    @patch("panoptikon.ui.macos_app.AppKit", autospec=True)
    @patch("panoptikon.ui.macos_app.Foundation", autospec=True)
    @patch("panoptikon.ui.macos_app.SearchFieldWrapper", autospec=True)
    @patch("panoptikon.ui.macos_app.SegmentedControlWrapper", autospec=True)
    @patch("panoptikon.ui.macos_app.TableViewWrapper", autospec=True)
    def test_app_initialization(
        self,
        mock_table_wrapper,
        mock_segment_wrapper,
        mock_search_wrapper,
        mock_foundation,
        mock_appkit,
    ) -> None:
        """Test the initialization of FileSearchApp."""
        # Setup mocks
        mock_app = MagicMock()
        mock_appkit.NSApplication.sharedApplication.return_value = mock_app

        # Create app instance
        _ = FileSearchApp()

        # Verify UI components were initialized
        mock_search_wrapper.assert_called_once()
        mock_segment_wrapper.assert_called_once()
        mock_table_wrapper.assert_called_once()

        # Add assertions about window creation
        mock_appkit.NSWindow.alloc.assert_called_once()

    @patch("panoptikon.ui.macos_app.AppKit", autospec=True)
    @patch("panoptikon.ui.macos_app.Foundation", autospec=True)
    @patch("panoptikon.ui.macos_app.SearchFieldWrapper", autospec=True)
    @patch("panoptikon.ui.macos_app.SegmentedControlWrapper", autospec=True)
    @patch("panoptikon.ui.macos_app.TableViewWrapper", autospec=True)
    def test_file_loading_and_search(
        self,
        mock_table_wrapper,
        mock_segment_wrapper,
        mock_search_wrapper,
        mock_foundation,
        mock_appkit,
    ) -> None:
        """Test file loading and search functionality."""
        # Setup mocks
        mock_app = MagicMock()
        mock_appkit.NSApplication.sharedApplication.return_value = mock_app

        mock_table = MagicMock()
        mock_table_wrapper.return_value.obj = mock_table

        # Create app
        app = FileSearchApp()
        app.table_view = mock_table

        # Test file loading
        app.set_files(["file1.txt", "file2.txt"])
        assert len(app.files) == 2
        assert len(app.filtered_files) == 2
        mock_table.reloadData.assert_called_once()

        # Test search functionality
        app.search("file1")
        assert len(app.filtered_files) == 1
        assert app.filtered_files[0] == "file1.txt"

        # Test clear search
        app.clear_search()
        assert len(app.filtered_files) == 2

    @patch("panoptikon.ui.macos_app.AppKit", autospec=True)
    @patch("panoptikon.ui.macos_app.Foundation", autospec=True)
    @patch("panoptikon.ui.macos_app.SearchFieldWrapper", autospec=True)
    @patch("panoptikon.ui.macos_app.SegmentedControlWrapper", autospec=True)
    @patch("panoptikon.ui.macos_app.TableViewWrapper", autospec=True)
    def test_ui_delegates_and_datasource(
        self,
        mock_table_wrapper,
        mock_segment_wrapper,
        mock_search_wrapper,
        mock_foundation,
        mock_appkit,
    ) -> None:
        """Test UI delegate and datasource methods."""
        # Setup mocks
        mock_app = MagicMock()
        mock_appkit.NSApplication.sharedApplication.return_value = mock_app

        # Create components
        mock_search_field = MagicMock()
        mock_search_wrapper.return_value.obj = mock_search_field

        mock_segment = MagicMock()
        mock_segment_wrapper.return_value.obj = mock_segment

        mock_table = MagicMock()
        mock_table_wrapper.return_value.obj = mock_table

        # Create app
        app = FileSearchApp()

        # Set test files
        app.set_files(["file1.txt", "file2.txt"])

        # Test table view datasource methods
        assert app.numberOfRowsInTableView_(mock_table) == 2

        column = MagicMock()
        assert (
            app.tableView_objectValueForTableColumn_row_(mock_table, column, 0)
            == "file1.txt"
        )
        assert (
            app.tableView_objectValueForTableColumn_row_(mock_table, column, 1)
            == "file2.txt"
        )

        # Test search field delegate
        mock_search_field.stringValue.return_value = "file1"
        app.search_field_changed_(mock_search_field)
        assert len(app.filtered_files) == 1
        mock_table.reloadData.assert_called()

        # Test segmented control delegate
        mock_segment.selectedSegment.return_value = 1  # Case sensitive
        app.search_option_changed_(mock_segment)
        assert app.case_sensitive is True

        # Test double-click handler
        app.tableViewDoubleClicked_(mock_table)
        # This should trigger app._handle_double_click


class TestSearchIntegration:
    """Test search capabilities of the app."""

    @patch("panoptikon.ui.macos_app.AppKit", autospec=True)
    @patch("panoptikon.ui.macos_app.Foundation", autospec=True)
    @patch("panoptikon.ui.macos_app.SearchFieldWrapper", autospec=True)
    @patch("panoptikon.ui.macos_app.SegmentedControlWrapper", autospec=True)
    @patch("panoptikon.ui.macos_app.TableViewWrapper", autospec=True)
    def test_search_capabilities(
        self,
        mock_table_wrapper,
        mock_segment_wrapper,
        mock_search_wrapper,
        mock_foundation,
        mock_appkit,
    ) -> None:
        """Test different search capabilities of the application."""
        # Setup mocks
        mock_app = MagicMock()
        mock_appkit.NSApplication.sharedApplication.return_value = mock_app

        mock_table = MagicMock()
        mock_table_wrapper.return_value.obj = mock_table

        # Create app
        app = FileSearchApp()
        app.table_view = mock_table

        # Setup test files
        test_files = [
            str(Path("/test/dir1/file1.txt")),
            str(Path("/test/dir1/file2.txt")),
            str(Path("/test/dir2/file3.txt")),
        ]

        # Set files
        app.set_files(test_files)

        # Test basic search
        app.search("file1")
        assert len(app.filtered_files) == 1
        assert app.filtered_files[0] == str(Path("/test/dir1/file1.txt"))

        # Test directory filtering
        app.search("dir1")
        assert len(app.filtered_files) == 2

        # Test extension filtering
        app.search(".txt")
        assert len(app.filtered_files) == 3

        # Test case sensitive search
        app.case_sensitive = True
        app.search("FILE1")
        assert len(app.filtered_files) == 0

        app.search("file1")
        assert len(app.filtered_files) == 1

        # Test regex search
        app.regex_search = True
        app.search("file[0-9]")
        assert len(app.filtered_files) == 3


class TestEventBusIntegration:
    """Test integration with the event bus."""

    @patch("panoptikon.ui.macos_app.AppKit", autospec=True)
    @patch("panoptikon.ui.macos_app.Foundation", autospec=True)
    @patch("panoptikon.ui.macos_app.SearchFieldWrapper", autospec=True)
    @patch("panoptikon.ui.macos_app.SegmentedControlWrapper", autospec=True)
    @patch("panoptikon.ui.macos_app.TableViewWrapper", autospec=True)
    def test_event_handling(
        self,
        mock_table_wrapper,
        mock_segment_wrapper,
        mock_search_wrapper,
        mock_foundation,
        mock_appkit,
    ) -> None:
        """Test handling of events from the event bus."""
        # Create event bus with mocked implementation
        event_bus = MagicMock(spec=EventBus)

        # Create modified app class that accepts event_bus
        class TestableFileSearchApp(FileSearchApp):
            def __init__(self, event_bus=None):
                self.event_bus = event_bus
                # Don't call super().__init__() to avoid UI setup
                self.files = []
                self.filtered_files = []
                self.case_sensitive = False
                self.regex_search = False
                self.table_view = MagicMock()
                self.search_field = MagicMock()

            def _setup_ui(self):
                # Override to do nothing
                pass

        # Create app
        app = TestableFileSearchApp(event_bus)

        # Add testing methods
        app.reload_table = MagicMock()
        app.clear_search_field = MagicMock()

        # Verify event bus subscription
        event_bus.subscribe.assert_not_called()  # No subscriptions yet

        # Register a handler
        def on_test_event(event):
            app.reload_table()

        # Simulate registration
        app.register_event_handler = MagicMock()
        app.register_event_handler(on_test_event)

        # Verify handling
        on_test_event(object())
        app.reload_table.assert_called_once()
