# Day-One Quality Standards Implementation

This guide provides detailed implementation steps for establishing rigorous quality standards for the Panoptikon project from day one. These standards are designed to be implemented immediately and enforced throughout the development process.

## Configuration Files Implementation

### 1. Cursor AI Integration

Create `.cursor/settings.json`:

```json
{
  "editor": {
    "formatOnSave": true,
    "rulers": [120],
    "showHints": true,
    "lintOnSave": true
  },
  "linting": {
    "enabled": true,
    "pylintEnabled": true,
    "flake8Enabled": true,
    "mypyEnabled": true
  },
  "ai": {
    "contextPrompts": [
      "Always follow the project's quality standards:",
      "- Maximum line length: 120 characters",
      "- All functions must have docstrings",
      "- All parameters must have type annotations",
      "- Maximum function length: 50 lines",
      "- Maximum file length: 500 lines",
      "- Use pathlib instead of os.path",
      "- No bare except statements",
      "- Prefer composition over inheritance",
      "- No circular dependencies"
    ]
  },
  "python": {
    "formatting": {
      "provider": "black",
      "blackArgs": ["--line-length", "120"]
    },
    "linting": {
      "pylintArgs": ["--rcfile=.pylintrc"],
      "flake8Args": ["--config=.flake8"],
      "mypyArgs": ["--config-file=pyproject.toml"]
    }
  }
}
```

### 2. Linting Configuration

#### 2.1 Flake8 Configuration

Create `.flake8`:

```ini
[flake8]
max-line-length = 120
exclude = .git,__pycache__,build,dist,.cursor
# Docstring checking
docstring-convention = google
# Ignore specific errors
ignore = E203,W503,E501
per-file-ignores = 
    tests/*:D100,D101,D102,D103
    __init__.py:F401
# Select specific checks
select = E,F,W,C,D,N
```

#### 2.2 Pylint Configuration

Create `.pylintrc`:

```ini
[MASTER]
ignore=CVS
ignore-patterns=
jobs=0
persistent=yes
extension-pkg-whitelist=PyObjC

[MESSAGES CONTROL]
disable=
    C0111, # missing-docstring
    C0103, # invalid-name
    C0330, # bad-continuation
    C1801, # len-as-condition
    W0511, # fixme
    R0903, # too-few-public-methods
    R0201, # no-self-use
    R0913, # too-many-arguments (will be handled by complexity limits)

[REPORTS]
output-format=text
reports=yes
evaluation=10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10)

[BASIC]
good-names=i,j,k,ex,Run,_
bad-names=foo,bar,baz

[DESIGN]
max-args=6
max-attributes=12
max-bool-expr=5
max-branches=12
max-locals=15
max-parents=3
max-public-methods=25
max-returns=6
max-statements=50
min-public-methods=1

[SIMILARITIES]
min-similarity-lines=10
ignore-comments=yes
ignore-docstrings=yes
ignore-imports=yes

[FORMAT]
max-line-length=120
```

### 3. Code Formatting Configuration

Update `pyproject.toml`:

```toml
[tool.black]
line-length = 120
target-version = ['py39']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
  | __pycache__
)/
'''

[tool.isort]
profile = "black"
line_length = 120
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
strict_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
disallow_incomplete_defs = false

[tool.ruff]
line-length = 120
target-version = "py39"
select = ["E", "F", "B", "I", "N", "D"]
ignore = ["E203", "D203", "D213"]
fixable = ["I", "F", "B"]

[tool.ruff.pydocstyle]
convention = "google"
```

### 4. Pre-commit Configuration

Create `.pre-commit-config.yaml`:

```yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
        args: ['--maxkb=500']
    -   id: debug-statements
    -   id: check-merge-conflict
    -   id: detect-private-key

-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort
        name: isort (python)
        args: ["--profile", "black", "--line-length", "120"]

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black
        args: ["--line-length", "120"]

-   repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: 'v0.0.262'
    hooks:
    -   id: ruff
        args: ["--fix", "--line-length", "120"]

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    -   id: mypy
        additional_dependencies: [types-requests, types-PyYAML]

-   repo: local
    hooks:
    -   id: check-file-length
        name: check file length
        entry: python scripts/check_file_length.py
        language: python
        types: [python]
        args: ["--max-lines=500"]

    -   id: check-docstring-coverage
        name: check docstring coverage
        entry: python scripts/check_docstring_coverage.py
        language: python
        types: [python]
        args: ["--min-coverage=95"]
```

### 5. Directory Structure Template

Create `directory_structure.md`:

```markdown
# Panoptikon Directory Structure

This document defines the component boundaries and module responsibilities for the Panoptikon project.

## Root Structure

```
panoptikon/
├── src/
│   └── panoptikon/       # Main package
├── tests/                # Test suite
├── scripts/              # Build and utility scripts
├── docs/                 # Documentation
├── assets/               # Non-code resources
└── .github/              # GitHub configuration
```

## Core Package Structure

```
src/panoptikon/
├── __init__.py            # Package initialization
├── index/                 # File indexing system
│   ├── __init__.py
│   ├── crawler.py         # File system traversal
│   ├── monitor.py         # File system change detection
│   └── exclusion.py       # Directory/file exclusion
├── db/                    # Database operations
│   ├── __init__.py
│   ├── schema.py          # Database schema
│   ├── operations.py      # CRUD operations
│   ├── migrations.py      # Schema migrations
│   └── connection.py      # Connection management
├── search/                # Search functionality
│   ├── __init__.py
│   ├── engine.py          # Search core
│   ├── query.py           # Query parsing
│   ├── filters.py         # Filter implementation
│   └── ranker.py          # Result ranking
├── cloud/                 # Cloud provider integration
│   ├── __init__.py
│   ├── detector.py        # Provider detection
│   ├── status.py          # Status tracking
│   └── providers/         # Provider-specific code
│       ├── __init__.py
│       ├── icloud.py
│       ├── dropbox.py
│       ├── gdrive.py
│       └── onedrive.py
├── ui/                    # PyObjC interface
│   ├── __init__.py
│   ├── app.py             # Application container
│   ├── window.py          # Main window
│   ├── components/        # UI components
│   │   ├── __init__.py
│   │   ├── search.py      # Search field
│   │   ├── results.py     # Results list
│   │   └── tree.py        # Tree view
│   └── viewmodels/        # View models for UI
│       ├── __init__.py
│       ├── search_vm.py   # Search view model
│       ├── results_vm.py  # Results view model
│       └── tree_vm.py     # Tree view model
├── config/                # Application settings
│   ├── __init__.py
│   └── settings.py        # Settings management
└── utils/                 # Common utilities
    ├── __init__.py
    ├── paths.py           # Path operations
    ├── logger.py          # Logging system
    └── threading.py       # Threading utilities
```

## Component Responsibilities

### index

Responsible for discovering and monitoring files in the file system.

- **crawler.py**: Traverses directory structures to find files
- **monitor.py**: Detects changes to the file system
- **exclusion.py**: Manages patterns for excluding files/directories

### db

Manages database operations and schema.

- **schema.py**: Defines database structure
- **operations.py**: Provides CRUD operations
- **migrations.py**: Handles schema versioning
- **connection.py**: Manages database connections

### search

Implements search functionality.

- **engine.py**: Coordinates search operations
- **query.py**: Parses search queries
- **filters.py**: Implements filtering logic
- **ranker.py**: Ranks search results

### cloud

Handles cloud storage integration.

- **detector.py**: Identifies cloud providers
- **status.py**: Tracks download status
- **providers/**: Provider-specific implementations

### ui

Implements the PyObjC user interface.

- **app.py**: Application entry point
- **window.py**: Main window controller
- **components/**: UI components
- **viewmodels/**: View models (MVVM pattern)

### config

Manages application configuration.

- **settings.py**: Stores and retrieves settings

### utils

Common utilities used across the application.

- **paths.py**: Path manipulation utilities
- **logger.py**: Logging infrastructure
- **threading.py**: Threading utilities

## Module Design Guidelines

1. **Single Responsibility**: Each module should have a single, well-defined responsibility
2. **Encapsulation**: Implementation details should be hidden behind clean interfaces
3. **Dependency Direction**: Dependencies should point inward (utils → core modules → UI)
4. **No Circular Dependencies**: Modules should not directly or indirectly depend on themselves
5. **Interface Stability**: Public interfaces should be clearly marked and stable
6. **Size Limits**:
   - Files: Maximum 500 lines
   - Classes: Maximum 200 lines
   - Functions: Maximum 50 lines
   - Methods: Maximum 30 lines
```

### 6. Technical Debt Tracking

Create `.github/quality/legacy_registry.json`:

```json
{
  "schemaVersion": 1,
  "exceptions": [
    {
      "file": "example/path/file.py",
      "rule": "file-length",
      "reason": "Initial import of legacy code. Will be refactored.",
      "created": "2023-05-01",
      "expires": "2023-06-01",
      "ticketLink": "https://github.com/user/panoptikon/issues/123"
    }
  ],
  "metricGoals": {
    "maxFileLengthLines": 500,
    "maxMethodLengthLines": 50,
    "maxClassLengthLines": 200,
    "maxCyclomaticComplexity": 10,
    "minTestCoveragePercent": 80,
    "maxAllowedExceptions": 5
  },
  "technicalDebtPolicy": {
    "newExceptionsRequireTicket": true,
    "maximumExceptionDuration": "30 days",
    "requireExpirationDate": true
  }
}
```

## Additional Quality Scripts

### 1. File Length Checker

Create `scripts/check_file_length.py`:

```python
#!/usr/bin/env python
"""Check file length script for pre-commit hook.

This script checks if Python files exceed the maximum allowed length.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple


def check_file_length(file_path: str, max_lines: int) -> Tuple[bool, int]:
    """Check if a file exceeds the maximum number of lines.

    Args:
        file_path: Path to the file to check
        max_lines: Maximum number of lines allowed

    Returns:
        Tuple of (is_valid, actual_line_count)
    """
    with open(file_path, "r", encoding="utf-8") as file:
        line_count = sum(1 for _ in file)
    
    return line_count <= max_lines, line_count


def main() -> int:
    """Run the file length checker.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(description="Check file length")
    parser.add_argument("--max-lines", type=int, default=500,
                        help="Maximum number of lines per file")
    parser.add_argument("files", nargs="*", help="Files to check")
    
    args = parser.parse_args()
    
    violations = []
    
    for file_path in args.files:
        is_valid, line_count = check_file_length(file_path, args.max_lines)
        if not is_valid:
            violations.append((file_path, line_count))
    
    if violations:
        for file_path, line_count in violations:
            print(f"{file_path}: {line_count} lines (exceeds {args.max_lines})")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### 2. Docstring Coverage Checker

Create `scripts/check_docstring_coverage.py`:

```python
#!/usr/bin/env python
"""Check docstring coverage script for pre-commit hook.

This script verifies that Python files have the required docstring coverage.
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class DocstringVisitor(ast.NodeVisitor):
    """AST visitor that checks for docstrings in functions and classes."""

    def __init__(self) -> None:
        """Initialize the visitor."""
        self.stats = {
            "functions": {"total": 0, "with_docstring": 0},
            "classes": {"total": 0, "with_docstring": 0},
            "methods": {"total": 0, "with_docstring": 0},
            "modules": {"total": 0, "with_docstring": 0},
        }
        self.current_class = None

    def visit_Module(self, node: ast.Module) -> None:
        """Visit a module node.

        Args:
            node: The module node to visit
        """
        self.stats["modules"]["total"] += 1
        if ast.get_docstring(node):
            self.stats["modules"]["with_docstring"] += 1
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition node.

        Args:
            node: The class definition node to visit
        """
        self.stats["classes"]["total"] += 1
        if ast.get_docstring(node):
            self.stats["classes"]["with_docstring"] += 1
        
        old_class = self.current_class
        self.current_class = node
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition node.

        Args:
            node: The function definition node to visit
        """
        if self.current_class:
            self.stats["methods"]["total"] += 1
            if ast.get_docstring(node):
                self.stats["methods"]["with_docstring"] += 1
        else:
            self.stats["functions"]["total"] += 1
            if ast.get_docstring(node):
                self.stats["functions"]["with_docstring"] += 1
        
        self.generic_visit(node)


def calculate_coverage(stats: Dict) -> float:
    """Calculate the overall docstring coverage.

    Args:
        stats: Statistics dictionary from DocstringVisitor

    Returns:
        Coverage percentage (0-100)
    """
    total = 0
    with_docstring = 0
    
    for category in stats.values():
        total += category["total"]
        with_docstring += category["with_docstring"]
    
    if total == 0:
        return 100.0
    
    return (with_docstring / total) * 100


def check_file_docstrings(file_path: str) -> Tuple[float, Dict]:
    """Check docstring coverage for a file.

    Args:
        file_path: Path to the file to check

    Returns:
        Tuple of (coverage_percentage, statistics)
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    tree = ast.parse(content)
    visitor = DocstringVisitor()
    visitor.visit(tree)
    
    coverage = calculate_coverage(visitor.stats)
    
    return coverage, visitor.stats


def main() -> int:
    """Run the docstring coverage checker.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(description="Check docstring coverage")
    parser.add_argument("--min-coverage", type=float, default=95.0,
                        help="Minimum docstring coverage percentage")
    parser.add_argument("files", nargs="*", help="Files to check")
    
    args = parser.parse_args()
    
    violations = []
    
    for file_path in args.files:
        coverage, stats = check_file_docstrings(file_path)
        if coverage < args.min_coverage:
            violations.append((file_path, coverage, stats))
    
    if violations:
        for file_path, coverage, stats in violations:
            print(f"{file_path}: {coverage:.1f}% coverage (below {args.min_coverage}%)")
            for category, counts in stats.items():
                if counts["total"] > 0:
                    cat_coverage = (counts["with_docstring"] / counts["total"]) * 100
                    print(f"  {category}: {counts['with_docstring']}/{counts['total']} ({cat_coverage:.1f}%)")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Quality Documentation

### Add to README.md:

```markdown
## Code Quality Standards

This project follows strict quality standards from day one:

- **Line Length**: Maximum 120 characters per line
- **File Size**: Maximum 500 lines per file
- **Function Size**: Maximum 50 lines per function
- **Class Size**: Maximum 200 lines per class
- **Complexity**: Maximum cyclomatic complexity of 10
- **Docstrings**: 95%+ coverage for all public APIs
- **Type Hints**: Required for all function parameters and returns
- **Test Coverage**: Minimum 80% code coverage

### Setting Up Development Environment

1. Install pre-commit hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Run tests:
   ```bash
   pytest
   ```

4. Check code quality:
   ```bash
   # Formatting
   black .
   isort .
   
   # Linting
   ruff .
   
   # Type checking
   mypy .
   ```

### Quality Exceptions

If you need to create an exception to any quality rule:

1. Add an entry to `.github/quality/legacy_registry.json`
2. Create a corresponding GitHub issue
3. Set an expiration date (maximum 30 days)
4. Document the reason in the code

All exceptions will be reviewed regularly and must be resolved by their expiration date.
```

### Create CONTRIBUTING.md:

```markdown
# Contributing to Panoptikon

Thank you for considering contributing to Panoptikon! This document outlines our quality standards and contribution workflow.

## Quality First Approach

We prioritize code quality from day one, following strict standards:

- **Readability**: Code should be self-explanatory and well-documented
- **Testability**: All code must be testable and include tests
- **Maintainability**: Code should be modular with clear responsibilities
- **Performance**: Critical paths must be optimized and benchmarked

## Quality Standards

All contributions must adhere to these standards:

1. **Code Structure**:
   - Maximum 500 lines per file
   - Maximum 50 lines per function
   - Maximum 200 lines per class
   - Maximum 10 cyclomatic complexity

2. **Documentation**:
   - All modules must have module docstrings
   - All public functions, classes, and methods must have docstrings
   - Complex algorithms must include inline comments
   - 95%+ docstring coverage required

3. **Testing**:
   - Minimum 80% test coverage
   - Unit tests for all functionality
   - Integration tests for component interactions
   - Performance tests for critical paths

4. **Code Style**:
   - Black formatting (120 character line length)
   - Ruff linting
   - MyPy type checking
   - No disabled warnings without explanation

## Contribution Workflow

1. **Before Coding**:
   - Check the issue tracker for existing issues
   - Discuss major changes in an issue first
   - Review the architectural patterns in `directory_structure.md`

2. **During Development**:
   - Follow the established patterns
   - Write tests alongside code
   - Run pre-commit hooks locally
   - Document as you go

3. **Pull Request Process**:
   - Create a focused PR addressing a single concern
   - Ensure all tests pass
   - Verify code coverage requirements
   - Complete the PR template

4. **Code Review**:
   - All code requires review before merging
   - Address all review comments
   - Maintain quality standards in revisions
   - Be receptive to feedback

## Technical Debt Management

If you must create an exception to quality standards:

1. Document the exception in `.github/quality/legacy_registry.json`
2. Create a ticket for resolving the exception
3. Set an expiration date (maximum 30 days)
4. Get approval from a maintainer

## Questions?

If you have questions about contribution or quality standards, please open an issue for discussion.
```

## Implementation Process

1. **Initial Setup**:
   - Create all configuration files
   - Set up pre-commit hooks
   - Document quality standards

2. **Developer Onboarding**:
   - Train all developers on quality standards
   - Review quality expectations
   - Set up IDE configurations

3. **Continuous Integration**:
   - Configure GitHub Actions for quality checks
   - Set up automated quality reporting
   - Implement quality gates in the pipeline

4. **Monitoring and Maintenance**:
   - Regular review of quality metrics
   - Scheduled technical debt reduction
   - Quality standard revisions as needed

## Quality Verification

To verify quality standards implementation:

1. Run all pre-commit hooks on the codebase
2. Verify configuration file correctness
3. Check test coverage for core components
4. Review docstring coverage
5. Verify IDE integration with quality tools

This ensures all quality standards are properly established before development begins.
