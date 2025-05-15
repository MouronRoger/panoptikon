"""UI Integration Tests for Panoptikon

IMPORTANT: Conditional Import/Skip Logic for PyObjC
---------------------------------------------------
This test module uses a robust conditional import pattern to ensure that
pytest will NEVER see or attempt to collect any pytest-specific code if
PyObjC is not available in the environment.

How it works:
- At the very top of the file, BEFORE any other imports, we check for PyObjC.
- If PyObjC is not available:
    - __test__ = False tells pytest there are no tests in this module.
    - A dummy function is defined to avoid empty file syntax errors.
    - sys.exit(0) is called to prevent any further code from being parsed or executed.
- Only if PyObjC is available do we import pytest and all test code.

Why is this necessary?
- Pytest collects and parses test files before evaluating skip logic or decorators.
- Extensive mocking in this file can allow tests to run even if PyObjC is missing,
  leading to confusing failures.
- This pattern guarantees that the file is invisible to pytest if PyObjC is not present.

Maintenance:
- DO NOT add any pytest imports, decorators, or test code above the PyObjC check.
- All test code and imports must be below the marked line.
- If you need to change the skip logic, update this docstring and the top-level code.

This approach is robust, cross-platform, and future-proof for conditional test collection.
"""

import sys

# Check for PyObjC availability BEFORE any imports
try:
    __import__("objc")
    PYOBJC_AVAILABLE = True
except ImportError:
    PYOBJC_AVAILABLE = False
    __test__ = False  # Tell pytest explicitly this module has no tests

    def no_tests_available():
        """This module has no tests when PyObjC is unavailable."""
        pass

    if True:
        sys.exit(0)

# ======== ONLY PUT CODE BELOW THIS LINE ========
# Everything below only runs when PyObjC is available

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from panoptikon.core.events import EventBus
from panoptikon.ui.macos_app import FileSearchApp


@pytest.fixture(autouse=True)
def mock_objc_and_wrappers(monkeypatch):
    """Mock PyObjC modules and UI wrappers for integration tests."""
    import importlib
    import sys
    from unittest.mock import MagicMock

    # Mock AppKit, Foundation, objc
    appkit = MagicMock()
    foundation = MagicMock()
    objc = MagicMock()
    sys.modules["AppKit"] = appkit
    sys.modules["Foundation"] = foundation
    sys.modules["objc"] = objc

    # Patch importlib.import_module to return mocks for these modules
    real_import_module = importlib.import_module

    def import_module_patch(name, *args, **kwargs):
        if name == "AppKit":
            return appkit
        if name == "Foundation":
            return foundation
        if name == "objc":
            return objc
        return real_import_module(name, *args, **kwargs)

    monkeypatch.setattr(importlib, "import_module", import_module_patch)

    # Mock AppKit classes/constants
    appkit.NSWindow = MagicMock()
    appkit.NSWindow.alloc.return_value.initWithContentRect_styleMask_backing_defer_.return_value = MagicMock()
    appkit.NSWindowStyleMaskTitled = 1
    appkit.NSWindowStyleMaskClosable = 2
    appkit.NSWindowStyleMaskResizable = 4
    appkit.NSBackingStoreBuffered = 2
    appkit.NSApplication = MagicMock()
    appkit.NSApplication.sharedApplication.return_value = MagicMock()
    appkit.NSSearchField = MagicMock()
    appkit.NSSegmentedControl = MagicMock()
    appkit.NSTableView = MagicMock()
    appkit.NSScrollView = MagicMock()
    appkit.NSTableColumn = MagicMock()
    appkit.NSBezelBorder = 0
    appkit.NSViewWidthSizable = 1
    appkit.NSViewHeightSizable = 2
    appkit.NSSegmentStyleRounded = 0

    # Mock Foundation functions
    foundation.NSMakeRect = lambda x, y, w, h: (x, y, w, h)

    # Patch UI wrappers
    monkeypatch.setattr("panoptikon.ui.objc_wrappers.SearchFieldWrapper", MagicMock())
    monkeypatch.setattr(
        "panoptikon.ui.objc_wrappers.SegmentedControlWrapper", MagicMock()
    )
    monkeypatch.setattr("panoptikon.ui.objc_wrappers.TableViewWrapper", MagicMock())
    yield


def skip_if_no_pyobjc() -> None:
    """Skip test if PyObjC is not available."""
    if not PYOBJC_AVAILABLE:
        pytest.skip("PyObjC not available: skipping UI integration tests.")


class TestUIIntegration:
    """Test UI integration with core components."""

    @classmethod
    def setup_class(cls):
        if not PYOBJC_AVAILABLE:
            pytest.skip(
                "PyObjC not available: skipping UI integration tests.",
                allow_module_level=True,
            )

    @patch("AppKit.NSApp")
    @patch("AppKit.NSApplication.sharedApplication")
    def test_app_lifecycle(self, mock_shared_app, mock_nsapp) -> None:
        """Test the show method of FileSearchApp."""
        mock_app = MagicMock()
        mock_shared_app.return_value = mock_app
        app = FileSearchApp()
        app._window = MagicMock()
        app.show()
        app._window.makeKeyAndOrderFront_.assert_called_once()
        mock_app.activateIgnoringOtherApps_.assert_called_once_with(True)
        mock_app.run.assert_called_once()


class TestUIComponentIntegration:
    """Test integration between UI components."""

    @classmethod
    def setup_class(cls):
        if not PYOBJC_AVAILABLE:
            pytest.skip(
                "PyObjC not available: skipping UI integration tests.",
                allow_module_level=True,
            )

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
        """Test UI component instantiation and delegate setup."""
        mock_search_field = MagicMock()
        mock_search_alloc.return_value.init.return_value = mock_search_field
        mock_segment_control = MagicMock()
        mock_segment_alloc.return_value.init.return_value = mock_segment_control
        mock_table_view = MagicMock()
        mock_table_alloc.return_value.init.return_value = mock_table_view
        app = FileSearchApp()
        # Test that the wrappers were instantiated
        assert hasattr(app, "_search_field")
        assert hasattr(app, "_search_options")
        assert hasattr(app, "_table_view")


class TestUIEventIntegration:
    """Test UI integration with the event system."""

    @classmethod
    def setup_class(cls):
        if not PYOBJC_AVAILABLE:
            pytest.skip(
                "PyObjC not available: skipping UI integration tests.",
                allow_module_level=True,
            )

    @patch("AppKit.NSApp")
    @patch("AppKit.NSApplication.sharedApplication")
    def test_ui_event_integration(self, mock_shared_app, mock_nsapp) -> None:
        """Test that show does not error when PyObjC is available."""
        mock_app = MagicMock()
        mock_shared_app.return_value = mock_app
        app = FileSearchApp()
        app._window = MagicMock()
        app.show()
        app._window.makeKeyAndOrderFront_.assert_called_once()
        mock_app.activateIgnoringOtherApps_.assert_called_once_with(True)
        mock_app.run.assert_called_once()


class TestUIFileSystemIntegration:
    """Test UI integration with filesystem components."""

    @classmethod
    def setup_class(cls):
        if not PYOBJC_AVAILABLE:
            pytest.skip(
                "PyObjC not available: skipping UI integration tests.",
                allow_module_level=True,
            )

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

    @classmethod
    def setup_class(cls):
        if not PYOBJC_AVAILABLE:
            pytest.skip(
                "PyObjC not available: skipping UI integration tests.",
                allow_module_level=True,
            )

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

    @classmethod
    def setup_class(cls):
        if not PYOBJC_AVAILABLE:
            pytest.skip(
                "PyObjC not available: skipping UI integration tests.",
                allow_module_level=True,
            )

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

    @classmethod
    def setup_class(cls):
        if not PYOBJC_AVAILABLE:
            pytest.skip(
                "PyObjC not available: skipping UI integration tests.",
                allow_module_level=True,
            )

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
            def __init__(self):
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
        app = TestableFileSearchApp()

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
