# PyObjC UI Typing Patterns Reference

This document provides common typing patterns for PyObjC-based UI code in Panoptikon. Use these as a cookbook for consistent, type-safe UI development.

---

## 1. Table/Data Source Methods

```python
def numberOfRowsInTableView_(self, table_view: NSTableView) -> int:
    """Return the number of rows in the table view."""
    ...

def tableView_objectValueForTableColumn_row_(
    self, table_view: NSTableView, column: NSTableColumn, row: int
) -> Any:
    """Return the value for a table cell."""
    ...
```

## 2. Table Delegate Methods

```python
def tableViewSelectionDidChange_(self, notification: Any) -> None:
    """Handle selection changes in the table view."""
    ...
```

## 3. Search Field Delegate Methods

```python
def controlTextDidChange_(self, notification: Any) -> None:
    """Handle text changes in the search field."""
    ...

def controlTextDidEndEditing_(self, notification: Any) -> None:
    """Handle end of editing (e.g., Enter key)."""
    ...
```

## 4. Wrapper Class Patterns

```python
class SearchFieldWrapper:
    def set_delegate(self, delegate: Any) -> None: ...
    def get_string_value(self) -> str: ...
    def set_string_value(self, value: str) -> None: ...

class TableViewWrapper:
    def set_delegate(self, delegate: Any) -> None: ...
    def set_data_source(self, data_source: Any) -> None: ...
    def reload_data(self) -> None: ...
```

## 5. Notification/Event Handler Signatures

```python
def on_search_changed(self, search_text: str) -> None: ...
def on_search_submitted(self, search_text: str) -> None: ...
def on_search_option_changed(self, sender: Any) -> None: ...
```

## 6. General PyObjC Patterns

- Use `Any` for PyObjC objects unless a stub exists.
- Use wrapper classes to isolate untyped PyObjC code.
- Use `# type: ignore` only for dynamic or complex cases.
- Prefer explicit signatures and docstrings for all delegate/data source methods.

---

_Expand this file as new patterns emerge during migration._ 