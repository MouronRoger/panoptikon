# Panoptikon

A high-performance file search application inspired by the Windows "Everything" utility. Panoptikon provides instantaneous file search capabilities by maintaining an efficient index of your filesystem.

## Features

- Instantaneous file search across your entire filesystem
- Low memory and CPU footprint
- Live index updates when files change
- Advanced search syntax and filtering
- Cloud storage integration
- Intuitive and responsive UI

## Installation

### Requirements

- Python 3.9 or higher
- macOS (Windows and Linux support planned)

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/example/panoptikon.git
cd panoptikon

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package and dependencies
pip install -e ".[dev]"
```

## Development Setup

### Setting Up the Development Environment

1. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

2. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

3. Run tests to verify your setup:
   ```bash
   pytest
   ```

### Directory Structure

```
panoptikon/
├── src/panoptikon/    # Main package
│   ├── index/         # File indexing system
│   ├── search/        # Search functionality
│   ├── ui/            # UI components
│   ├── db/            # Database operations
│   ├── cloud/         # Cloud provider integration
│   ├── config/        # Application settings
│   └── utils/         # Common utilities
├── tests/             # Test directory
├── scripts/           # Utility scripts
├── docs/              # Documentation
└── assets/            # Non-code resources
```

## Quality Standards

Panoptikon is developed with a strong emphasis on code quality:

- Black for code formatting (120 char line length)
- Ruff for fast linting
- MyPy for strict type checking
- Minimum 80% test coverage
- Comprehensive docstrings following Google style
- Maximum file length of 500 lines
- Maximum function length of 50 lines

## Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=src/panoptikon --cov-report=term --cov-report=html

# Run tests for a specific module
pytest tests/test_index/
```

## License

MIT

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.
