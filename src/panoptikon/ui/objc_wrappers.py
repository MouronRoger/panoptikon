"""Interface adapters for PyObjC components.

This module provides properly typed Python wrapper classes for PyObjC components.
The type: ignore comments are isolated to this file, creating a clear boundary
between typed Python code and untyped PyObjC interfaces.
"""

from __future__ import annotations

from typing import Any, TypeVar

# PyObjC imports with type ignores isolated to this file
import AppKit  # type: ignore
import Foundation  # type: ignore
import objc  # type: ignore

T = TypeVar("T")
Rect = tuple[float, float, float, float]  # (x, y, width, height)
Point = tuple[float, float]  # (x, y)
Size = tuple[float, float]  # (width, height)


class SearchFieldWrapper:
    """Typed wrapper for NSSearchField."""

    def __init__(self, frame: Rect | None = None) -> None:
        """Initialize with an optional frame rectangle.

        Args:
            frame: The frame rectangle as (x, y, width, height)
        """
        if frame is not None:
            self._search_field = AppKit.NSSearchField.alloc().initWithFrame_(
                Foundation.NSMakeRect(*frame)
            )
        else:
            self._search_field = AppKit.NSSearchField.alloc().init()

    def set_placeholder(self, text: str) -> None:
        """Set the placeholder text.

        Args:
            text: The placeholder text to display
        """
        cell = self._search_field.cell()
        cell.setPlaceholderString_(text)

    def set_delegate(self, delegate: Any) -> None:
        """Set the delegate for the search field.

        Args:
            delegate: An object that implements the NSSearchFieldDelegate methods
        """
        self._search_field.setDelegate_(delegate)

    def get_string_value(self) -> str:
        """Get the current string value.

        Returns:
            The current text in the search field
        """
        return str(self._search_field.stringValue())

    def set_string_value(self, value: str) -> None:
        """Set the string value.

        Args:
            value: The text to set
        """
        self._search_field.setStringValue_(value)

    @property
    def ns_object(self) -> Any:
        """Get the underlying NSSearchField object.

        Returns:
            The raw NSSearchField object
        """
        return self._search_field


class TableViewWrapper:
    """Typed wrapper for NSTableView."""

    def __init__(self, frame: Rect | None = None) -> None:
        """Initialize with an optional frame rectangle.

        Args:
            frame: The frame rectangle as (x, y, width, height)
        """
        if frame is not None:
            self._table_view = AppKit.NSTableView.alloc().initWithFrame_(
                Foundation.NSMakeRect(*frame)
            )
        else:
            self._table_view = AppKit.NSTableView.alloc().init()

        # Create a scroll view container
        if frame is not None:
            self._scroll_view = AppKit.NSScrollView.alloc().initWithFrame_(
                Foundation.NSMakeRect(*frame)
            )
        else:
            self._scroll_view = AppKit.NSScrollView.alloc().init()

        # Configure scroll view
        self._scroll_view.setHasVerticalScroller_(True)
        self._scroll_view.setHasHorizontalScroller_(True)
        self._scroll_view.setBorderType_(AppKit.NSBezelBorder)
        self._scroll_view.setAutoresizingMask_(
            AppKit.NSViewWidthSizable | AppKit.NSViewHeightSizable
        )

        # Add table view to scroll view
        self._scroll_view.setDocumentView_(self._table_view)

    def add_column(self, identifier: str, title: str, width: float) -> None:
        """Add a column to the table view.

        Args:
            identifier: Unique identifier for the column
            title: The column title
            width: The column width
        """
        column = AppKit.NSTableColumn.alloc().initWithIdentifier_(identifier)
        column.setWidth_(width)
        column.headerCell().setStringValue_(title)
        self._table_view.addTableColumn_(column)

    def set_delegate(self, delegate: Any) -> None:
        """Set the delegate.

        Args:
            delegate: An object that implements NSTableViewDelegate methods
        """
        self._table_view.setDelegate_(delegate)

    def set_data_source(self, data_source: Any) -> None:
        """Set the data source.

        Args:
            data_source: An object that implements NSTableViewDataSource methods
        """
        self._table_view.setDataSource_(data_source)

    def reload_data(self) -> None:
        """Reload all table data."""
        self._table_view.reloadData()

    @property
    def ns_object(self) -> Any:
        """Get the underlying NSTableView object.

        Returns:
            The raw NSTableView object
        """
        return self._table_view

    @property
    def ns_scroll_view(self) -> Any:
        """Get the NSScrollView containing the table view.

        Returns:
            The NSScrollView containing the table view
        """
        return self._scroll_view


class SegmentedControlWrapper:
    """Typed wrapper for NSSegmentedControl."""

    def __init__(
        self, segments: list[str], frame: Rect | None = None, tracking_mode: int = 0
    ) -> None:
        """Initialize with segments and an optional frame rectangle.

        Args:
            segments: List of segment labels
            frame: The frame rectangle as (x, y, width, height)
            tracking_mode: Tracking mode (0=momentary, 1=select, 2=selectAny)
        """
        if frame is not None:
            self._control = AppKit.NSSegmentedControl.alloc().initWithFrame_(
                Foundation.NSMakeRect(*frame)
            )
        else:
            self._control = AppKit.NSSegmentedControl.alloc().init()

        self._control.setSegmentCount_(len(segments))

        for i, name in enumerate(segments):
            self._control.setLabel_forSegment_(name, i)
            self._control.setWidth_forSegment_(0, i)  # 0 means auto-size

        self._control.setTrackingMode_(tracking_mode)
        self._control.setSegmentStyle_(AppKit.NSSegmentStyleRounded)
        self._control.sizeToFit()

    def set_selected_segment(self, index: int) -> None:
        """Set the selected segment.

        Args:
            index: The index of the segment to select
        """
        self._control.setSelectedSegment_(index)

    def get_selected_segment(self) -> int:
        """Get the index of the selected segment.

        Returns:
            The index of the selected segment
        """
        return int(self._control.selectedSegment())

    def set_target_action(self, target: Any, action: str) -> None:
        """Set the target and action for the control.

        Args:
            target: The target object
            action: The selector string for the action method
        """
        selector = objc.selector(getattr(target, action), signature=b"v@:@")
        self._control.setTarget_(target)
        self._control.setAction_(selector)

    @property
    def ns_object(self) -> Any:
        """Get the underlying NSSegmentedControl object.

        Returns:
            The raw NSSegmentedControl object
        """
        return self._control
