# Contributing to Panoptikon

Thank you for your interest in contributing to Panoptikon! This document outlines the process for contributing to the project and the quality standards we maintain.

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

## Quality Requirements

All contributions to Panoptikon must adhere to these quality standards:

### Code Style and Documentation

- **Type Annotations**: All functions and methods must have complete type annotations.
- **Docstrings**: All public APIs must include comprehensive docstrings following the Google style.
- **Line Length**: Maximum line length is 120 characters.
- **File Length**: Files should not exceed 500 lines.
- **Function Length**: Functions should not exceed 50 lines.

### Code Quality

- **No Circular Dependencies**: Modules should not have circular dependencies.
- **Separation of Concerns**: Each module should have a clear and distinct responsibility.
- **Naming Conventions**: Follow consistent naming conventions (snake_case for variables and functions, PascalCase for classes).
- **Error Handling**: Include appropriate error handling for all operations.

### Testing

- **Test Coverage**: All code should have a minimum of 80% test coverage.
- **Test Structure**: Tests should be organized to mirror the main package structure.
- **Test Fixtures**: Use fixtures for setup and teardown to avoid duplication.
- **Parameterized Tests**: Use parameterized tests for testing multiple similar cases.

## Code Review Process

The code review process focuses on:

1. **Correctness**: Does the code do what it's supposed to do?
2. **Quality**: Does the code meet our quality standards?
3. **Maintainability**: Is the code easy to understand and maintain?
4. **Performance**: Is the code efficient and performant?
5. **Security**: Does the code follow security best practices?

## Testing Expectations

When adding new features or fixing bugs:

- **Add Tests**: Include tests that verify your changes work correctly.
- **Update Existing Tests**: Update tests that may be affected by your changes.
- **Run the Full Test Suite**: Ensure that all tests pass, not just your new ones.
- **Check Coverage**: Make sure your changes don't reduce the overall test coverage.

## Development Environment

Setting up a consistent development environment:

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

Thank you for helping make Panoptikon better!
