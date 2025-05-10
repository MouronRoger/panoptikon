"""Integration tests for PyObjC wrapper interfaces.

These tests verify that the wrappers correctly interact with PyObjC
and catch interface errors early.
"""

from typing import Any, List

import pytest

# Skip the tests if PyObjC is not installed
try:
    import objc  # type: ignore
    
    PYOBJC_AVAILABLE = True
except ImportError:
    PYOBJC_AVAILABLE = False

# Import our wrapper classes
from panoptikon.ui.objc_wrappers import (
    SearchFieldWrapper,
    SegmentedControlWrapper,
    TableViewWrapper,
)
from panoptikon.ui.validators import (
    assert_objc_method_exists,
    validate_objc_method_exists,
    validate_table_data_source,
)

# Mark all tests in this file as requiring PyObjC
pytestmark = pytest.mark.skipif(
    not PYOBJC_AVAILABLE, reason="PyObjC not installed"
)


class MockTableDataSource:
    """Mock implementation of NSTableViewDataSource."""

    def __init__(self, data: List[List[str]]) -> None:
        """Initialize with test data.

        Args:
            data: A 2D array representing table data
        """
        self.data = data

    def numberOfRowsInTableView_(self, table_view: Any) -> int:
        """Return the number of rows.

        Args:
            table_view: The NSTableView

        Returns:
            The number of data rows
        """
        return len(self.data)

    def tableView_objectValueForTableColumn_row_(
        self, table_view: Any, column: Any, row: int
    ) -> Any:
        """Return the value for a cell.

        Args:
            table_view: The NSTableView
            column: The NSTableColumn
            row: The row index

        Returns:
            The cell value
        """
        if row < len(self.data) and column.identifier() < len(self.data[row]):
            return self.data[row][int(column.identifier())]
        return ""


class TestTableViewWrapper:
    """Tests for the TableViewWrapper class."""

    def test_create_table_view(self) -> None:
        """Test creating a table view with columns."""
        # Skip test if PyObjC is not available
        if not PYOBJC_AVAILABLE:
            pytest.skip("PyObjC not available")

        # Create the table view wrapper
        table_view = TableViewWrapper()

        # Add columns
        table_view.add_column("0", "Name", 200)
        table_view.add_column("1", "Size", 100)

        # Create a data source with test data
        data = [
            ["File 1", "10 KB"],
            ["File 2", "20 KB"],
            ["File 3", "30 KB"],
        ]
        data_source = MockTableDataSource(data)

        # Verify our data source passes the validation
        assert validate_table_data_source(data_source)

        # Set the data source
        table_view.set_data_source(data_source)

        # Reload data (should not raise any exceptions)
        table_view.reload_data()

        # Get the underlying NSTableView
        ns_table_view = table_view.ns_object

        # Verify basic assertions about the table view
        assert ns_table_view is not None
        assert hasattr(ns_table_view, "numberOfColumns")
        assert ns_table_view.numberOfColumns() == 2


class TestSearchFieldWrapper:
    """Tests for the SearchFieldWrapper class."""

    def test_search_field(self) -> None:
        """Test creating and manipulating a search field."""
        # Skip test if PyObjC is not available
        if not PYOBJC_AVAILABLE:
            pytest.skip("PyObjC not available")

        # Create the search field wrapper
        search_field = SearchFieldWrapper()

        # Set placeholder text
        placeholder = "Search files..."
        search_field.set_placeholder(placeholder)

        # Set a test value
        test_value = "test search"
        search_field.set_string_value(test_value)

        # Get the value back
        value = search_field.get_string_value()

        # Verify the value was set correctly
        assert value == test_value

        # Get the underlying NSSearchField
        ns_search_field = search_field.ns_object

        # Verify basic assertions about the search field
        assert ns_search_field is not None
        assert hasattr(ns_search_field, "cell")
        cell = ns_search_field.cell()
        assert hasattr(cell, "placeholderString")
        assert cell.placeholderString() == placeholder


class TestSegmentedControlWrapper:
    """Tests for the SegmentedControlWrapper class."""

    def test_segmented_control(self) -> None:
        """Test creating and manipulating a segmented control."""
        # Skip test if PyObjC is not available
        if not PYOBJC_AVAILABLE:
            pytest.skip("PyObjC not available")

        # Create the segmented control wrapper with segments
        segments = ["Names", "Dates", "Size"]
        control = SegmentedControlWrapper(segments)

        # Select a segment
        segment_index = 1
        control.set_selected_segment(segment_index)

        # Get the selected segment
        selected = control.get_selected_segment()

        # Verify the segment was selected correctly
        assert selected == segment_index

        # Get the underlying NSSegmentedControl
        ns_control = control.ns_object

        # Verify basic assertions about the segmented control
        assert ns_control is not None
        assert hasattr(ns_control, "segmentCount")
        assert ns_control.segmentCount() == len(segments)
        assert hasattr(ns_control, "labelForSegment_")
        for i, segment in enumerate(segments):
            assert ns_control.labelForSegment_(i) == segment


def test_objc_method_validation() -> None:
    """Test method validation logic."""
    # Skip test if PyObjC is not available
    if not PYOBJC_AVAILABLE:
        pytest.skip("PyObjC not available")

    # Create a test object
    table_view = TableViewWrapper()
    ns_object = table_view.ns_object

    # Test validation of existing method
    assert validate_objc_method_exists(ns_object, "reloadData")

    # Test validation of non-existent method
    assert not validate_objc_method_exists(ns_object, "nonExistentMethod_")

    # Test assert method
    assert_objc_method_exists(ns_object, "reloadData")

    # Test assert method with non-existent method (should raise AssertionError)
    with pytest.raises(AssertionError):
        assert_objc_method_exists(ns_object, "nonExistentMethod_") 