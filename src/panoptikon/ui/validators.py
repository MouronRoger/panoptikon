"""Runtime validation for PyObjC interfaces.

This module provides utilities for validating PyObjC objects at runtime,
allowing for early detection of interface errors rather than waiting for
runtime failures.
"""

from __future__ import annotations

from typing import Any, Callable, List, TypeVar

# Validation functions


def validate_objc_method_exists(obj: Any, method_name: str) -> bool:
    """Verify an Objective-C object has the specified method.

    Args:
        obj: The PyObjC object to check
        method_name: The name of the method to verify

    Returns:
        True if the method exists, False otherwise
    """
    # Check if the object has the method attribute
    if not hasattr(obj, method_name):
        return False

    # Check if the attribute is callable
    if not callable(getattr(obj, method_name)):
        return False

    return True


def validate_objc_protocol_conformance(obj: Any, protocol_methods: List[str]) -> bool:
    """Verify an object implements all methods required by a protocol.

    Args:
        obj: The PyObjC object to check
        protocol_methods: List of method names required by the protocol

    Returns:
        True if the object implements all required methods, False otherwise
    """
    return all(validate_objc_method_exists(obj, method) for method in protocol_methods)


def assert_objc_method_exists(obj: Any, method_name: str) -> None:
    """Assert that an Objective-C object has the specified method.

    Args:
        obj: The PyObjC object to check
        method_name: The name of the method that should exist

    Raises:
        AssertionError: If the method doesn't exist
    """
    assert validate_objc_method_exists(
        obj, method_name
    ), f"Required method '{method_name}' missing on {obj.__class__.__name__}"


def assert_objc_protocol_conformance(obj: Any, protocol_methods: List[str]) -> None:
    """Assert that an object conforms to a protocol.

    Args:
        obj: The PyObjC object to check
        protocol_methods: List of method names required by the protocol

    Raises:
        AssertionError: If any required method is missing
    """
    for method in protocol_methods:
        assert_objc_method_exists(obj, method)


# Specific validators for common PyObjC protocols


def validate_table_data_source(obj: Any) -> bool:
    """Validate that an object can serve as an NSTableViewDataSource.

    Args:
        obj: The object to validate

    Returns:
        True if the object conforms to NSTableViewDataSource, False otherwise
    """
    required_methods = [
        "numberOfRowsInTableView_",
        "tableView_objectValueForTableColumn_row_",
    ]
    return validate_objc_protocol_conformance(obj, required_methods)


def validate_table_delegate(obj: Any) -> bool:
    """Validate that an object can serve as an NSTableViewDelegate.

    Args:
        obj: The object to validate

    Returns:
        True if the object conforms to NSTableViewDelegate, False otherwise
    """
    # These are optional, but checking the most commonly implemented ones
    common_methods = [
        "tableViewSelectionDidChange_",
        "tableView_shouldSelectRow_",
    ]
    return any(validate_objc_method_exists(obj, method) for method in common_methods)


def validate_search_field_delegate(obj: Any) -> bool:
    """Validate that an object can serve as an NSSearchFieldDelegate.

    Args:
        obj: The object to validate

    Returns:
        True if the object conforms to NSSearchFieldDelegate, False otherwise
    """
    common_methods = [
        "controlTextDidChange_",
        "controlTextDidEndEditing_",
    ]
    return any(validate_objc_method_exists(obj, method) for method in common_methods)


T = TypeVar("T")


def validated_objc_call(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to validate PyObjC method calls.

    This decorator inspects the first argument to a wrapped function
    (the PyObjC object) and verifies that it has the expected method
    before the function is called.

    Args:
        func: The function to wrap

    Returns:
        A wrapper function that validates the PyObjC method exists
    """

    def method_name_from_func_name(name: str) -> str:
        """Convert Python-style function name to Objective-C style method name."""
        # Simple case: just add underscore
        if not name.endswith("_"):
            return f"{name}_"
        return name

    def wrapper(*args: Any, **kwargs: Any) -> T:
        """Validate PyObjC method exists before calling the wrapped function."""
        if not args:
            return func(*args, **kwargs)

        # Extract the function name and convert to expected Objective-C method name
        obj = args[0]
        func_name = func.__name__
        method_name = method_name_from_func_name(func_name)

        # Validate the method exists on the object
        assert_objc_method_exists(obj, method_name)

        return func(*args, **kwargs)

    return wrapper 