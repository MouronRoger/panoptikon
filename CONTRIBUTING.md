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
   - Review the architectural patterns

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

1. Document the exception
2. Create a ticket for resolving the exception
3. Set an expiration date (maximum 30 days)
4. Get approval from a maintainer

## Development Environment Setup

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

## Questions?

If you have questions about contribution or quality standards, please open an issue for discussion. 