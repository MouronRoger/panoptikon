# PyObjC Typing Solution for Panoptikon

This document explains the "boundary pattern" solution we've implemented to address the type checking issues with PyObjC in our macOS application.

## The Problem

PyObjC stubs are incompatible with our Python version, leaving PyObjC code without proper type checking. This prevents us from maintaining a strictly typed codebase while using PyObjC for macOS native UI components.

## The Solution: Boundary Pattern

We've implemented a "boundary pattern" that:

1. Creates a clear separation between typed Python code and untyped PyObjC code
2. Contains `# type: ignore` comments only within the boundary classes
3. Provides properly typed interfaces for the rest of the application

## Key Components

### 1. Wrapper Classes (`src/panoptikon/ui/objc_wrappers.py`)

These classes:
- Wrap PyObjC interfaces with proper Python type annotations
- Isolate all `# type: ignore` comments
- Provide a clean, typed API for the rest of the application

Example for NSSearchField:

```python
class SearchFieldWrapper:
    """Typed wrapper for NSSearchField."""

    def __init__(self, frame: Optional[Rect] = None) -> None:
        """Initialize with an optional frame rectangle."""
        if frame is not None:
            self._search_field = AppKit.NSSearchField.alloc().initWithFrame_(
                Foundation.NSMakeRect(*frame)
            )
        else:
            self._search_field = AppKit.NSSearchField.alloc().init()

    def set_placeholder(self, text: str) -> None:
        """Set the placeholder text."""
        cell = self._search_field.cell()
        cell.setPlaceholderString_(text)

    @property
    def ns_object(self) -> Any:
        """Get the underlying NSSearchField object."""
        return self._search_field
```

### 2. Custom Type Stubs (`src/panoptikon/typings/`)

We've created minimal type stubs (.pyi files) for critical PyObjC components:
- AppKit (NSSearchField, NSTableView, NSSegmentedControl)
- Foundation
- objc

These stubs define just enough types to support our application without requiring full PyObjC typing support.

### 3. MyPy Configuration

The `pyproject.toml` has been updated with:

```toml
[tool.mypy]
# Existing config...
mypy_path = ["src/panoptikon/typings"]
warn_unused_ignores = false  # Changed because we need to use # type: ignore for PyObjC

# Ignore PyObjC related imports in type checking
[[tool.mypy.overrides]]
module = "objc"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "Foundation"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "AppKit"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "Cocoa"
ignore_missing_imports = true
```

### 4. Runtime Validation (`src/panoptikon/ui/validators.py`)

We've created runtime validators that:
- Verify PyObjC method existence
- Validate protocol implementation
- Provide decorator for validating PyObjC calls at runtime

Example:

```python
def validate_table_data_source(obj: Any) -> bool:
    """Validate that an object can serve as an NSTableViewDataSource."""
    required_methods = [
        "numberOfRowsInTableView_",
        "tableView_objectValueForTableColumn_row_",
    ]
    return validate_objc_protocol_conformance(obj, required_methods)
```

### 5. Integration Tests (`tests/ui/test_objc_integration.py`)

Tests that verify:
- Wrappers correctly interact with PyObjC
- Runtime validations catch interface errors early
- PyObjC functionality works as expected

The tests are skipped if PyObjC is not available, allowing testing on systems without PyObjC.

## Usage Example (`src/panoptikon/ui/macos_app.py`)

The `FileSearchApp` class demonstrates:
- Using the wrapper classes for PyObjC components
- Runtime validation of delegate implementations
- Proper typing for the application logic
- Isolating PyObjC imports within limited scope

## Benefits

1. **Type Safety**: The codebase maintains strict typing for all Python code
2. **Isolation**: PyObjC code is clearly separated and contained
3. **Early Error Detection**: Runtime validation catches interface errors early
4. **Maintainability**: Clear boundaries make the code easier to understand and maintain
5. **Testability**: The solution allows for testing PyObjC code in controlled environments

## Conclusion

This solution provides a robust approach to using PyObjC in a strictly typed Python application. By creating a clear boundary between typed Python code and untyped PyObjC code, we can maintain type safety throughout the codebase while still leveraging the power of PyObjC for macOS native UI components. 