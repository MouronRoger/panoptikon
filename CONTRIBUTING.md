# Contributing to Panoptikon

Thank you for considering contributing to Panoptikon! This document outlines the process for contributing to the project and the quality standards we maintain.

## Quality First Approach

We prioritize code quality from day one, following strict standards:

- **Readability**: Code should be self-explanatory and well-documented
- **Testability**: All code must be testable and include tests
- **Maintainability**: Code should be modular with clear responsibilities
- **Performance**: Critical paths must be optimized and benchmarked

## Contribution Workflow

1. **Fork the Repository**: Begin by forking the repository to your GitHub account.

2. **Create a Branch**: Create a branch in your forked repository for your changes.
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**: Implement your changes, following the coding standards and quality requirements outlined below.

4. **Run Quality Checks**: Before submitting, ensure all quality checks pass.
   ```bash
   # Format code with Black
   black .
   
   # Run linting with Ruff
   ruff check --fix .
   
   # Run type checking with MyPy
   mypy .
   
   # Run tests with coverage
   pytest --cov=src/panoptikon
   ```

5. **Submit a Pull Request**: Once your changes are ready, submit a pull request to the main repository.

6. **Code Review**: Wait for code review from maintainers. Be prepared to make additional changes based on feedback.

7. **Merge**: After approval, your pull request will be merged into the main codebase.

## Quality Standards

All contributions must adhere to these standards:

1. **Code Structure**:
   - Maximum 500 lines per file
   - Maximum 50 lines per function
   - Maximum 200 lines per class
   - Maximum 10 cyclomatic complexity

2. **Documentation**:
   - All modules must have module docstrings
   - All public functions, classes, and methods must have docstrings (Google style)
   - Complex algorithms must include inline comments
   - 95%+ docstring coverage required

3. **Testing**:
   - Minimum 80% test coverage
   - Unit tests for all functionality
   - Integration tests for component interactions
   - Performance tests for critical paths
   - Test fixtures for setup and teardown
   - Parameterized tests for testing multiple similar cases

4. **Code Style and Documentation**:
   - Black formatting (88 character line length)
   - Ruff linting
   - MyPy type checking with strict mode
   - Type annotations for all functions and methods
   - No disabled warnings without explanation

5. **Code Quality**:
   - No circular dependencies
   - Separation of concerns
   - Consistent naming conventions (snake_case for variables and functions, PascalCase for classes)
   - Appropriate error handling for all operations

## Technical Debt Management

If you must create an exception to quality standards:

1. Document the exception
2. Create a ticket for resolving the exception
3. Set an expiration date (maximum 30 days)
4. Get approval from a maintainer

## Code Review Process

The code review process focuses on:

1. **Correctness**: Does the code do what it's supposed to do?
2. **Quality**: Does the code meet our quality standards?
3. **Maintainability**: Is the code easy to understand and maintain?
4. **Performance**: Is the code efficient and performant?
5. **Security**: Does the code follow security best practices?
6. **Cloud File Operations**: All cloud file operations (open, reveal, download, etc.) must be delegated to Finder/NSWorkspace. Direct cloud provider API integration is FORBIDDEN. See docs/spec/phases/phase8_prompt.md and system architecture docs for rationale.

## Testing Expectations

When adding new features or fixing bugs:

- **Add Tests**: Include tests that verify your changes work correctly.
- **Update Existing Tests**: Update tests that may be affected by your changes.
- **Run the Full Test Suite**: Ensure that all tests pass, not just your new ones.
- **Check Coverage**: Make sure your changes don't reduce the overall test coverage.

## Development Environment Setup

1. **Use a Virtual Environment**: Always work within a virtual environment.
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Development Dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Set Up Pre-commit Hooks**:
   ```bash
   pre-commit install
   ```

4. **Run Tests**:
   ```bash
   pytest
   ```

5. **Check Code Quality**:
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

Thank you for helping make Panoptikon better! 