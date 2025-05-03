# Panoptikon

A high-performance file search application for macOS inspired by the Windows "Everything" utility.

## Overview

Panoptikon allows you to instantly search all files on your system by maintaining a real-time index of your file system. The main features include:

- Lightning-fast file search across your entire system
- Real-time file system monitoring for up-to-date results
- Clean, native macOS interface built with PyObjC
- Cloud storage integration (iCloud, Dropbox, Google Drive, OneDrive)
- Advanced filtering options

## Installation

### Requirements

- macOS 10.15+
- Python 3.9+

### Install from Source

```bash
# Clone the repository
git clone https://github.com/user/panoptikon.git
cd panoptikon

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate

# Install the package and dependencies
pip install -e .
```

### Development Setup

For development, install the additional development dependencies:

```bash
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Usage

```bash
# Run the application
panoptikon
```

## Development

### Project Structure

The project is organized into the following modules:

- `index`: File indexing system
- `search`: Search functionality
- `ui`: PyObjC interface
- `db`: Database operations
- `cloud`: Cloud provider integration
- `config`: Application settings
- `utils`: Common utilities

Each module has well-defined responsibilities with clean interfaces.

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=src/panoptikon

# Run specific test modules
pytest tests/test_index/
```

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

## License

This project is licensed under the MIT License - see the LICENSE file for details. 