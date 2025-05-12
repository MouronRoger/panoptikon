"""Tests for the MacOS application with proper mocking.

These tests use mocks to test the MacOS app functionality without requiring
the actual PyObjC environment.
"""

from collections.abc import Generator
import sys
from unittest.mock import MagicMock, patch

import pytest

from src.panoptikon.ui.macos_app import FileSearchApp


@pytest.fixture
def mock_objc_modules() -> Generator[None, None, None]:
    """Mock the required PyObjC modules to enable testing."""
    # Create mock modules if they don't exist in sys.modules
    modules_to_mock = ["AppKit", "Foundation", "objc"]
    mocked_modules = {}

    for module_name in modules_to_mock:
        if module_name not in sys.modules:
            mock_module = MagicMock()
            mocked_modules[module_name] = mock_module
            sys.modules[module_name] = mock_module

    # Mock AppKit classes and constants
    app_kit = sys.modules["AppKit"]
    # Using setattr to avoid "Module has no attribute" errors
    app_kit.NSWindow = MagicMock()
    app_kit.NSWindow.alloc.return_value.initWithContentRect_styleMask_backing_defer_.return_value = MagicMock()
    app_kit.NSWindowStyleMaskTitled = 1
    app_kit.NSWindowStyleMaskClosable = 2
    app_kit.NSWindowStyleMaskResizable = 4
    app_kit.NSBackingStoreBuffered = 2
    app_kit.NSApplication = MagicMock()
    app_kit.NSApplication.sharedApplication.return_value = MagicMock()

    # Mock Foundation classes and functions
    foundation = sys.modules["Foundation"]
    foundation.NSMakeRect = lambda x, y, w, h: (x, y, w, h)

    yield

    # Clean up added modules
    for module_name, mock_module in mocked_modules.items():
        if module_name in sys.modules and sys.modules[module_name] is mock_module:
            del sys.modules[module_name]


@pytest.fixture
def mock_wrappers() -> Generator[None, None, None]:
    """Mock the UI component wrappers."""
    with (
        patch("src.panoptikon.ui.macos_app.SearchFieldWrapper") as mock_search,
        patch("src.panoptikon.ui.macos_app.SegmentedControlWrapper") as mock_segments,
        patch("src.panoptikon.ui.macos_app.TableViewWrapper") as mock_table,
    ):
        mock_search.return_value = MagicMock()
        mock_search.return_value.ns_object = MagicMock()

        mock_segments.return_value = MagicMock()
        mock_segments.return_value.ns_object = MagicMock()

        mock_table.return_value = MagicMock()
        mock_table.return_value.ns_object = MagicMock()
        mock_table.return_value.ns_scroll_view = MagicMock()

        yield


class TestSearchDelegate:
    """Test implementation of a search delegate."""

    last_search_text: str
    last_submitted_text: str

    def setup(self) -> None:
        """Initialize with empty values."""
        self.last_search_text = ""
        self.last_submitted_text = ""

    def on_search_changed(self, search_text: str) -> None:
        """Record the changed search text.

        Args:
            search_text: The current search text
        """
        if not hasattr(self, "last_search_text"):
            self.setup()
        self.last_search_text = search_text

    def on_search_submitted(self, search_text: str) -> None:
        """Record the submitted search text.

        Args:
            search_text: The submitted search text
        """
        if not hasattr(self, "last_submitted_text"):
            self.setup()
        self.last_submitted_text = search_text


class TestFileSearchApp:
    """Tests for the FileSearchApp class."""

    def test_init_without_pyobjc(self) -> None:
        """Test initializing without PyObjC available."""
        # Mock imports to fail
        with (
            patch("src.panoptikon.ui.macos_app.FileSearchApp._setup_ui") as mock_setup,
            patch.dict(sys.modules, {"AppKit": None, "Foundation": None}),
            patch(
                "builtins.__import__",
                side_effect=lambda name, *args, **kwargs: ImportError()
                if name in ("AppKit", "Foundation", "objc")
                else __import__(name, *args, **kwargs),
            ),
        ):
            app = FileSearchApp()
            assert not getattr(app, "_pyobjc_available", True)
            mock_setup.assert_not_called()

    def test_init_with_pyobjc(
        self, mock_objc_modules: None, mock_wrappers: None
    ) -> None:
        """Test initializing with PyObjC mocked."""
        # Patch the PyObjC imports to succeed and setup UI
        with patch("src.panoptikon.ui.macos_app.FileSearchApp._set_up_delegates"):
            app = FileSearchApp()
            assert app._pyobjc_available is True
            assert hasattr(app, "_search_field")
            assert hasattr(app, "_search_options")
            assert hasattr(app, "_table_view")
            assert app._files == []

    def test_set_files(self, mock_objc_modules: None, mock_wrappers: None) -> None:
        """Test setting files data."""
        with patch("src.panoptikon.ui.macos_app.FileSearchApp._set_up_delegates"):
            app = FileSearchApp()

            # Create a mock for the data source
            app._table_data_source = MagicMock()
            app._table_view = MagicMock()

            # Set files
            test_files = [
                ["file1.txt", "/path/to/file1.txt", "10 KB", "2023-01-01"],
                ["file2.txt", "/path/to/file2.txt", "20 KB", "2023-01-02"],
            ]
            app.set_files(test_files)

            # Verify the data was set and the table was updated
            assert app._files == test_files
            app._table_data_source.setFiles_.assert_called_once_with(test_files)
            app._table_view.reload_data.assert_called_once()

    def test_search_functions(
        self, mock_objc_modules: None, mock_wrappers: None
    ) -> None:
        """Test search delegate functions."""
        with (
            patch("src.panoptikon.ui.macos_app.FileSearchApp._setup_ui"),
            patch("src.panoptikon.ui.macos_app.FileSearchApp._set_up_delegates"),
            patch("builtins.print") as mock_print,
        ):
            app = FileSearchApp()

            # Test search functions
            app.on_search_changed("test query")
            mock_print.assert_called_with("Search changed: test query")

            app.on_search_submitted("submit query")
            mock_print.assert_called_with("Search submitted: submit query")

    def test_search_option_changed(
        self, mock_objc_modules: None, mock_wrappers: None
    ) -> None:
        """Test changing search options."""
        with (
            patch("src.panoptikon.ui.macos_app.FileSearchApp._setup_ui"),
            patch("src.panoptikon.ui.macos_app.FileSearchApp._set_up_delegates"),
            patch("builtins.print") as mock_print,
        ):
            app = FileSearchApp()
            app._search_options = MagicMock()
            app._search_options.get_selected_segment.return_value = 2

            # Test option change
            app.on_search_option_changed(None)
            mock_print.assert_called_with("Search option changed to: Date")

    def test_show_with_pyobjc(
        self, mock_objc_modules: None, mock_wrappers: None
    ) -> None:
        """Test show method with PyObjC available."""
        with (
            patch("src.panoptikon.ui.macos_app.FileSearchApp._setup_ui"),
            patch("src.panoptikon.ui.macos_app.FileSearchApp._set_up_delegates"),
        ):
            app = FileSearchApp()
            app._window = MagicMock()

            # Mock AppKit.NSApplication directly instead of patching a path
            app_mock = MagicMock()

            # Store the original
            original_app = sys.modules["AppKit"].NSApplication
            original_shared_app = original_app.sharedApplication

            try:
                # Replace with mock
                sys.modules["AppKit"].NSApplication.sharedApplication = MagicMock(
                    return_value=app_mock
                )

                # Call the method
                app.show()

                # Verify the window was shown
                app._window.makeKeyAndOrderFront_.assert_called_once()
                app_mock.activateIgnoringOtherApps_.assert_called_once_with(True)
                app_mock.run.assert_called_once()
            finally:
                # Restore original
                sys.modules["AppKit"].NSApplication = original_app
                original_app.sharedApplication = original_shared_app

    def test_show_without_pyobjc(self) -> None:
        """Test showing without PyObjC available."""
        with (
            patch("src.panoptikon.ui.macos_app.FileSearchApp._setup_ui"),
            patch("builtins.print") as mock_print,
        ):
            app = FileSearchApp()
            app._pyobjc_available = False

            app.show()
            mock_print.assert_called_with("Cannot show UI - PyObjC not available")


def test_search_functions() -> None:
    """Test search delegate functionality."""
    # Create an implementation of the delegate
    test_delegate = TestSearchDelegate()

    # Test the methods (verifying it implements the interface behaviorally)
    test_delegate.on_search_changed("test")
    assert test_delegate.last_search_text == "test"

    test_delegate.on_search_submitted("submit")
    assert test_delegate.last_submitted_text == "submit"
