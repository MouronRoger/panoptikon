# PyObjC Typing and Pyright Migration Guide for Panoptikon

## Table of Contents
1. [Introduction](#introduction)
2. [PyObjC Typing Strategy](#pyobjc-typing-strategy)
    - Boundary Pattern
    - Custom Type Stubs
    - Runtime Validation
    - Integration Testing
3. [Typing Patterns Cookbook](#typing-patterns-cookbook)
4. [Pyright Migration Plan](#pyright-migration-plan)
5. [Practical Migration Steps](#practical-migration-steps)
6. [Reference and Resources](#reference-and-resources)

---

## 1. Introduction

Strict typing is a core quality requirement for Panoptikon. However, using PyObjC for macOS native UI components presents unique challenges: PyObjC stubs are often incompatible with modern Python versions, and type checkers like mypy and Pyright do not natively support these dynamic Objective-C interfaces. This guide presents a robust, maintainable solution for integrating PyObjC with strict type checking, and details the migration from mypy to Pyright.

---

## 2. PyObjC Typing Strategy

### Boundary Pattern
- **Separation:** All untyped PyObjC code is isolated in wrapper classes (e.g., `src/panoptikon/ui/objc_wrappers.py`).
- **Type Ignores:** `# type: ignore` comments are used only within these boundary classes.
- **Typed API:** The rest of the application interacts only with typed Python interfaces.

**Example:**
```python
class SearchFieldWrapper:
    """Typed wrapper for NSSearchField."""
    def __init__(self, frame: Optional[Rect] = None) -> None:
        if frame is not None:
            self._search_field = AppKit.NSSearchField.alloc().initWithFrame_(
                Foundation.NSMakeRect(*frame)
            )
        else:
            self._search_field = AppKit.NSSearchField.alloc().init()
    def set_placeholder(self, text: str) -> None:
        cell = self._search_field.cell()
        cell.setPlaceholderString_(text)
    @property
    def ns_object(self) -> Any:
        return self._search_field
```

### Custom Type Stubs
- Minimal `.pyi` stubs for critical PyObjC components are placed in `src/panoptikon/typings/`.
- Stubs cover AppKit, Foundation, objc, and any other required modules.
- This enables type checkers to resolve imports and basic signatures.

### MyPy/Pyright Configuration
- `mypy_path`/`stubPath` points to the stubs directory.
- Ignore missing imports for PyObjC modules in both mypy and Pyright.
- Example Pyright config:
```json
{
  "include": ["src", "tests", "scripts"],
  "exclude": ["**/__pycache__", ".git", ".github", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv", "actions-runner/externals"],
  "typeCheckingMode": "strict",
  "pythonVersion": "3.9",
  "reportMissingImports": true,
  "reportMissingTypeStubs": false,
  "stubPath": "src/panoptikon/typings",
  "ignore": ["objc", "Foundation", "AppKit", "Cocoa"]
}
```

### Runtime Validation
- Decorators and helpers validate PyObjC protocol conformance at runtime.
- Example:
```python
def validate_table_data_source(obj: Any) -> bool:
    required_methods = [
        "numberOfRowsInTableView_",
        "tableView_objectValueForTableColumn_row_",
    ]
    return validate_objc_protocol_conformance(obj, required_methods)
```

### Integration Testing
- Tests in `tests/ui/test_objc_integration.py` verify wrappers, runtime validation, and PyObjC functionality.
- Tests are skipped if PyObjC is not available.

---

## 3. Typing Patterns Cookbook

### 3.1 Table/Data Source Methods
```python
def numberOfRowsInTableView_(self, table_view: NSTableView) -> int: ...
def tableView_objectValueForTableColumn_row_(self, table_view: NSTableView, column: NSTableColumn, row: int) -> Any: ...
```

### 3.2 Table Delegate Methods
```python
def tableViewSelectionDidChange_(self, notification: Any) -> None: ...
```

### 3.3 Search Field Delegate Methods
```python
def controlTextDidChange_(self, notification: Any) -> None: ...
def controlTextDidEndEditing_(self, notification: Any) -> None: ...
```

### 3.4 Wrapper Class Patterns
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

### 3.5 Notification/Event Handler Signatures
```python
def on_search_changed(self, search_text: str) -> None: ...
def on_search_submitted(self, search_text: str) -> None: ...
def on_search_option_changed(self, sender: Any) -> None: ...
```

### 3.6 General PyObjC Patterns
- Use `Any` for PyObjC objects unless a stub exists.
- Use wrapper classes to isolate untyped PyObjC code.
- Use `# type: ignore` only for dynamic or complex cases.
- Prefer explicit signatures and docstrings for all delegate/data source methods.

---

## 4. Pyright Migration Plan

### 4.1 Rationale
- Pyright offers faster, stricter, and more modern type checking than mypy.
- Better IDE integration (especially with VS Code).
- Migration after Phase 4 is optimal for stability.

### 4.2 Migration Steps

#### Step 1: Assessment & Setup
- Install Pyright: `pip install pyright`
- Create `pyrightconfig.json` in project root (see config above).

#### Step 2: Baseline Evaluation
- Run `pyright` and document current issues.
- Track issues in `pyright-migration.md`.

#### Step 3: Configuration Tuning
- Align config with mypy strictness.
- Add PyObjC ignore patterns.

#### Step 4: Incremental Adoption
- Add Pyright to CI and pre-commit.
- Run both mypy and Pyright temporarily.
- Fix critical errors first, then warnings.

#### Step 5: Developer Setup
- Update VS Code settings for Pyright.
- Document patterns and idioms.

#### Step 6: Migration Completion
- Switch to strict mode.
- Remove mypy and related configs.
- Clean up type comments.

#### Step 7: Documentation
- Update project docs and onboarding.
- Add Pyright usage to contributor materials.

### 4.3 Timeline
- Total: ~6.5 developer days (see original plan for breakdown).

### 4.4 Risks & Mitigations
| Risk | Mitigation |
|:-:|:-:|
| Breaking CI pipeline | Dual checking, fail-open on Pyright |
| Developer learning curve | Document patterns, provide examples |
| PyObjC compatibility | Configure ignore patterns |
| Inconsistent annotations | Identify/document idioms |

---

## 5. Practical Migration Steps

### 5.1 PyObjC Stubs
- Create minimal stubs for most-used classes/methods first.
- Use `Any` liberally at first to get things passing.

### 5.2 Strategic Type Ignores
- Use `# type: ignore[attr-defined]` for dynamic code.
- Use `# type: ignore[arg-type]` for test mocks.

### 5.3 Pattern Library
- Maintain a reference file for common PyObjC typing patterns.

### 5.4 Test Typing
- Fix test utilities and fixtures first.
- Add custom pytest plugin for typed fixtures if needed.
- Use consistent patterns for mock type annotations.

### 5.5 Automation
- Create VS Code tasks for targeted Pyright runs.
- Implement staged CI pipeline (strict on core, gradual on UI/tests).

---

## 6. Reference and Resources

- Example wrapper classes: `src/panoptikon/ui/objc_wrappers.py`
- Example stubs: `src/panoptikon/typings/`
- Integration tests: `tests/ui/test_objc_integration.py`
- Pyright and mypy config files: `pyrightconfig.json`, `pyproject.toml`
- Pattern library: `docs/guides/ui_typing_patterns.md` (now merged)

---

This guide is the single source of truth for PyObjC typing and type checking migration in Panoptikon. Expand as new patterns and requirements emerge. 