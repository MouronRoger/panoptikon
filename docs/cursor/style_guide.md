# Panoptikon Code Style Guide

This document outlines the coding standards and practices for the Panoptikon project. All code should adhere to these guidelines.

## General Principles

- **Quality First**: Prioritize code quality over development speed
- **Readability**: Write code that is easy to understand
- **Testability**: Design for testability from the beginning
- **Maintainability**: Consider future maintenance in all design decisions

## Python Coding Standards

### Code Structure

- **Line Length**: Maximum 120 characters
- **File Size**: Maximum 500 lines per file
- **Function Size**: Maximum 50 lines per function
- **Class Size**: Maximum 200 lines per class
- **Cyclomatic Complexity**: Maximum complexity of 10

### Documentation

- **Module Docstrings**: All modules must have a docstring
- **Function Docstrings**: All public functions must have a docstring following Google style
- **Class Docstrings**: All classes must have a docstring
- **Method Docstrings**: All public methods must have a docstring
- **Implementation Comments**: Complex algorithms need inline comments
- **Docstring Coverage**: Minimum 95% docstring coverage

### Type Annotations

- **Function Parameters**: All parameters must have type annotations
- **Return Values**: All functions must have return type annotations
- **Variables**: Use type annotations for complex variables
- **Generics**: Use typing.TypeVar for generic types
- **Collections**: Use typing module for collections (List, Dict, etc.)
- **Optional Values**: Use Optional[T] for nullable values
- **Union Types**: Use Union[T1, T2] for multiple types

### Imports

- **Organization**: Group imports as standard library, third-party, local
- **Formatting**: Use isort with black profile
- **Aliasing**: Avoid import aliasing except for common patterns
- **Wildcard Imports**: Never use wildcard imports (from module import *)
- **Module vs. Object**: Prefer importing modules over objects

### Naming Conventions

- **Packages**: lowercase, no underscores
- **Modules**: lowercase, underscores for readability
- **Classes**: CapWords convention
- **Functions**: lowercase, underscores for readability
- **Variables**: lowercase, underscores for readability
- **Constants**: UPPERCASE, underscores for readability
- **Type Variables**: CapWords with short names

### Code Style

- **Formatting**: Use Black formatter with line length 120
- **String Quotes**: Use double quotes for docstrings, single quotes for other strings
- **String Formatting**: Use f-strings for string interpolation
- **Comments**: Start with # and a space, sentence case, period at end
- **Trailing Commas**: Use trailing commas in multi-line collections

### Error Handling

- **Specific Exceptions**: Catch specific exceptions, not bare except
- **Error Messages**: Provide clear error messages
- **Logging**: Use the logging module instead of print statements
- **Context Managers**: Use context managers for resource management
- **Error Propagation**: Raise exceptions at the appropriate level

### Best Practices

- **Path Handling**: Use pathlib instead of os.path
- **File I/O**: Use context managers for file operations
- **Dependencies**: Avoid circular dependencies
- **Composition**: Prefer composition over inheritance
- **Immutability**: Use immutable data structures when appropriate
- **Constants**: Define constants at the module level
- **Default Arguments**: Avoid mutable default arguments

## Testing Standards

- **Coverage**: Minimum 80% code coverage
- **Unit Tests**: Write tests for all functionality
- **Test Isolation**: Tests should not depend on each other
- **Test Performance**: Tests should run quickly
- **Test Naming**: Use descriptive test names
- **Assertions**: Use appropriate assertions
- **Fixtures**: Use fixtures for test setup
- **Mocking**: Use mocking for external dependencies

## Package Structure

```
src/panoptikon/
├── __init__.py            # Package initialization
├── index/                 # File indexing system
├── db/                    # Database operations
├── search/                # Search functionality
├── cloud/                 # Cloud provider integration
├── ui/                    # PyObjC interface
├── config/                # Application settings
└── utils/                 # Common utilities
```

## Commit Standards

- **Atomic Commits**: Each commit should represent a single logical change
- **Commit Messages**: Use descriptive commit messages
- **Pre-Commit Hooks**: All commits must pass pre-commit hooks
- **Branch Strategy**: Use feature branches for development

## Quality Enforcement

- **Linting**: All code must pass flake8, pylint, and ruff checks
- **Type Checking**: All code must pass mypy type checking
- **Formatting**: All code must be formatted with Black
- **Pre-Commit**: Use pre-commit hooks to enforce standards
- **CI/CD**: Automated quality checks in CI/CD pipeline
