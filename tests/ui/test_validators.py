"""Tests for PyObjC interface validation."""

from typing import Any

import pytest

from src.panoptikon.ui.validators import (
    assert_objc_method_exists,
    assert_objc_protocol_conformance,
    validate_objc_method_exists,
    validate_objc_protocol_conformance,
    validate_search_field_delegate,
    validate_table_data_source,
    validate_table_delegate,
    validated_objc_call,
)


class MockObjC:
    """Mock PyObjC object for testing."""

    def __init__(self, methods: list[str]) -> None:
        """Initialize with a list of method names."""
        self._methods = methods

    def __getattr__(self, name: str) -> Any:
        """Return a callable if the method exists."""
        if name in self._methods:
            return lambda *args, **kwargs: None
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")


def test_validate_objc_method_exists() -> None:
    """Test validation of individual Objective-C methods."""
    # Test with existing method
    obj = MockObjC(["test_method_"])
    assert validate_objc_method_exists(obj, "test_method_")

    # Test with missing method
    assert not validate_objc_method_exists(obj, "missing_method_")

    # Test with non-callable attribute
    obj = type("TestObj", (), {"test_method_": "not callable"})()
    assert not validate_objc_method_exists(obj, "test_method_")


def test_validate_objc_protocol_conformance() -> None:
    """Test validation of Objective-C protocol conformance."""
    # Test with all methods present
    obj = MockObjC(["method1_", "method2_"])
    assert validate_objc_protocol_conformance(obj, ["method1_", "method2_"])

    # Test with missing method
    assert not validate_objc_protocol_conformance(obj, ["method1_", "missing_"])

    # Test with empty protocol
    assert validate_objc_protocol_conformance(obj, [])


def test_assert_objc_method_exists() -> None:
    """Test assertion of Objective-C method existence."""
    # Test with existing method
    obj = MockObjC(["test_method_"])
    assert_objc_method_exists(obj, "test_method_")  # Should not raise

    # Test with missing method
    with pytest.raises(AssertionError) as exc_info:
        assert_objc_method_exists(obj, "missing_method_")
    assert "missing_method_" in str(exc_info.value)
    assert "MockObjC" in str(exc_info.value)


def test_assert_objc_protocol_conformance() -> None:
    """Test assertion of Objective-C protocol conformance."""
    # Test with all methods present
    obj = MockObjC(["method1_", "method2_"])
    assert_objc_protocol_conformance(obj, ["method1_", "method2_"])  # Should not raise

    # Test with missing method
    with pytest.raises(AssertionError) as exc_info:
        assert_objc_protocol_conformance(obj, ["method1_", "missing_"])
    assert "missing_" in str(exc_info.value)


def test_validate_table_data_source() -> None:
    """Test validation of NSTableViewDataSource conformance."""
    # Test with required methods
    obj = MockObjC(
        [
            "numberOfRowsInTableView_",
            "tableView_objectValueForTableColumn_row_",
        ]
    )
    assert validate_table_data_source(obj)

    # Test with missing method
    obj = MockObjC(["numberOfRowsInTableView_"])
    assert not validate_table_data_source(obj)


def test_validate_table_delegate() -> None:
    """Test validation of NSTableViewDelegate conformance."""
    # Test with all common methods
    obj = MockObjC(
        [
            "tableViewSelectionDidChange_",
            "tableView_shouldSelectRow_",
        ]
    )
    assert validate_table_delegate(obj)

    # Test with one common method
    obj = MockObjC(["tableViewSelectionDidChange_"])
    assert validate_table_delegate(obj)

    # Test with no common methods
    obj = MockObjC(["other_method_"])
    assert not validate_table_delegate(obj)


def test_validate_search_field_delegate() -> None:
    """Test validation of NSSearchFieldDelegate conformance."""
    # Test with all common methods
    obj = MockObjC(
        [
            "controlTextDidChange_",
            "controlTextDidEndEditing_",
        ]
    )
    assert validate_search_field_delegate(obj)

    # Test with one common method
    obj = MockObjC(["controlTextDidChange_"])
    assert validate_search_field_delegate(obj)

    # Test with no common methods
    obj = MockObjC(["other_method_"])
    assert not validate_search_field_delegate(obj)


def test_validated_objc_call() -> None:
    """Test the validated_objc_call decorator."""
    obj = MockObjC(["test_method_"])

    # Test with valid method
    @validated_objc_call
    def test_method(target: Any) -> None:
        pass

    test_method(obj)  # Should not raise

    # Test with missing method
    @validated_objc_call
    def missing_method(target: Any) -> None:
        pass

    with pytest.raises(AssertionError) as exc_info:
        missing_method(obj)
    assert "missing_method_" in str(exc_info.value)

    # Test with no arguments
    @validated_objc_call
    def no_args() -> None:
        pass

    no_args()  # Should not raise


def test_validate_search_field_delegate_true() -> None:
    """Test validate_search_field_delegate returns True if any method exists."""

    class Dummy:
        def controlTextDidChange_(self) -> None:
            pass

    obj = Dummy()
    assert validate_search_field_delegate(obj) is True
