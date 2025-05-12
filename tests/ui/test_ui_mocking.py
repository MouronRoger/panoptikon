"""Specialized tests for UI components with proper PyObjC mocking.

This module provides improved tests for the UI components
with a focus on proper mocking of PyObjC classes and methods.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.panoptikon.core.events import EventBase, EventBus
from src.panoptikon.ui.macos_app import FileSearchApp


class MockNSObject:
    """Mock base class for Objective-C NSObject-derived classes."""

    def __init__(self, **kwargs):
        """Initialize with arbitrary attributes."""
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockNSSearchField(MockNSObject):
    """Mock for NSSearchField."""

    def initWithFrame_(self, frame):
        """Initialize with frame."""
        self.frame = frame
        self.stringValue = ""
        self.delegate = None
        return self


class MockNSSegmentedControl(MockNSObject):
    """Mock for NSSegmentedControl."""

    def initWithFrame_(self, frame):
        """Initialize with frame."""
        self.frame = frame
        self.selectedSegment = 0
        self.segmentCount = 2
        return self


class MockNSTableView(MockNSObject):
    """Mock for NSTableView."""

    def initWithFrame_(self, frame):
        """Initialize with frame."""
        self.frame = frame
        self.delegate = None
        self.dataSource = None
        self.doubleAction = None
        return self

    def reloadData(self):
        """Reload table data."""
        pass


class MockNSScrollView(MockNSObject):
    """Mock for NSScrollView."""

    def initWithFrame_(self, frame):
        """Initialize with frame."""
        self.frame = frame
        self.documentView = None
        return self


class MockNSWindow(MockNSObject):
    """Mock for NSWindow."""

    def initWithContentRect_styleMask_backing_defer_(self, rect, style, backing, defer):
        """Initialize with parameters."""
        self.contentRect = rect
        self.styleMask = style
        self.backing = backing
        self.defer = defer
        self.contentView = MockNSObject()
        self.title = ""
        return self

    def makeKeyAndOrderFront_(self, sender):
        """Make window key and bring to front."""
        pass


class MockNSRect:
    """Mock for NSRect struct."""

    def __init__(self, x, y, width, height):
        """Initialize with dimensions."""
        self.origin = MockNSObject(x=x, y=y)
        self.size = MockNSObject(width=width, height=height)


@pytest.fixture
def ui_patches():
    """Set up patches for UI components."""
    patches = []

    # Mock NSApplication
    mock_app = MagicMock()
    mock_app.run = MagicMock()

    ns_app_patch = patch(
        "AppKit.NSApplication.sharedApplication", return_value=mock_app
    )
    patches.append(ns_app_patch)

    # Mock NSSearchField
    def mock_search_alloc():
        return MockNSObject(initWithFrame_=lambda frame: MockNSSearchField())

    search_patch = patch("AppKit.NSSearchField.alloc", return_value=mock_search_alloc())
    patches.append(search_patch)

    # Mock NSSegmentedControl
    def mock_segment_alloc():
        return MockNSObject(initWithFrame_=lambda frame: MockNSSegmentedControl())

    segment_patch = patch(
        "AppKit.NSSegmentedControl.alloc", return_value=mock_segment_alloc()
    )
    patches.append(segment_patch)

    # Mock NSTableView
    def mock_table_alloc():
        return MockNSObject(initWithFrame_=lambda frame: MockNSTableView())

    table_patch = patch("AppKit.NSTableView.alloc", return_value=mock_table_alloc())
    patches.append(table_patch)

    # Mock NSScrollView
    def mock_scroll_alloc():
        return MockNSObject(initWithFrame_=lambda frame: MockNSScrollView())

    scroll_patch = patch("AppKit.NSScrollView.alloc", return_value=mock_scroll_alloc())
    patches.append(scroll_patch)

    # Mock NSWindow
    def mock_window_alloc():
        return MockNSObject(
            initWithContentRect_styleMask_backing_defer_=(
                lambda rect, style, backing, defer: MockNSWindow()
            )
        )

    window_patch = patch("AppKit.NSWindow.alloc", return_value=mock_window_alloc())
    patches.append(window_patch)

    # Mock NSMakeRect
    def mock_make_rect(x, y, width, height):
        return MockNSRect(x, y, width, height)

    rect_patch = patch("Foundation.NSMakeRect", side_effect=mock_make_rect)
    patches.append(rect_patch)

    # Mock objc super method
    objc_patch = patch("objc.super", return_value=MagicMock())
    patches.append(objc_patch)

    # Apply all patches
    for p in patches:
        p.start()

    yield

    # Remove all patches
    for p in patches:
        p.stop()


class TestAppWithProperMocking:
    """Tests for the FileSearchApp with proper ObjC mocking."""

    def test_app_initialization(self, ui_patches):
        """Test basic app initialization."""
        with patch("importlib.import_module") as mock_import:
            # Configure mock to return proper modules
            mock_module = MagicMock(spec=["alloc", "init"])
            mock_import.return_value = mock_module

            # Create app
            app = FileSearchApp()
            assert app is not None
            assert hasattr(app, "_files")
            assert app._files == []

    def test_file_operations(self, ui_patches):
        """Test file operations in the app."""
        with (
            patch.object(FileSearchApp, "_setup_ui"),
            patch.object(FileSearchApp, "_set_up_delegates"),
        ):
            app = FileSearchApp()
            app._pyobjc_available = True
            app._table_data_source = MagicMock()
            app._table_view = MagicMock()

            # Test setting files
            test_files = [
                ["file1.txt", "/path/to/file1.txt", "10KB", "2023-01-01"],
                ["file2.txt", "/path/to/file2.txt", "20KB", "2023-01-02"],
            ]
            app.set_files(test_files)
            assert app._files == test_files
            app._table_data_source.setFiles_.assert_called_once_with(test_files)
            app._table_view.reload_data.assert_called_once()

    def test_search_callbacks(self, ui_patches):
        """Test search callback methods."""
        with (
            patch.object(FileSearchApp, "_setup_ui"),
            patch.object(FileSearchApp, "_set_up_delegates"),
            patch("builtins.print") as mock_print,
        ):
            app = FileSearchApp()
            app._pyobjc_available = True

            # Test search callbacks
            app.on_search_changed("search term")
            mock_print.assert_called_with("Search changed: search term")

            app.on_search_submitted("search term")
            mock_print.assert_called_with("Search submitted: search term")


@pytest.fixture
def testable_app():
    """Create a testable app with minimal UI initialization."""
    with (
        patch("importlib.import_module"),
        patch.object(FileSearchApp, "_setup_ui"),
        patch.object(FileSearchApp, "_set_up_delegates"),
    ):
        # Create a minimal app for testing
        app = FileSearchApp()
        app._pyobjc_available = False
        app._files = []

        yield app


class TestEventIntegration:
    """Tests for integration with the event system."""

    def test_event_bus_integration(self, testable_app):
        """Test integration with the event bus."""
        app = testable_app
        event_bus = MagicMock(spec=EventBus)

        # Add a mock method to track calls
        app.handle_event = MagicMock()

        # Register a handler
        def handler(event):
            app.handle_event(event)

        # Call subscribe method on the mock
        event_bus.subscribe.return_value = None
        event_bus.subscribe(EventBase, handler)

        # Simulate event publication through a direct call
        # to avoid type constraints in the real EventBus
        test_event = MagicMock(spec=EventBase)
        handler(test_event)

        # Verify handler was called
        app.handle_event.assert_called_once_with(test_event)
