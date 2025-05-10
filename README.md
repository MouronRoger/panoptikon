# Panoptikon

A high-performance file search application inspired by Windows 'Everything'.

## Features

- Fast file indexing and search
- Real-time file system monitoring
- Cross-platform support (macOS, Linux, Windows)
- Modern and intuitive user interface

## Requirements

- Python 3.9 or higher
- SQLAlchemy 2.0+
- Watchdog 3.0+

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/user/panoptikon.git
   cd panoptikon
   ```

2. Create and activate a virtual environment:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. Install the package in development mode:
   ```bash
   make setup
   ```

## Development

### Code Style

This project uses:
- Black for code formatting (120 character line length)
- isort for import sorting
- Ruff for fast linting
- MyPy for static type checking
- Maximum file length of 500 lines

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make coverage
```

### Code Quality Checks

```bash
# Run linting
make lint

# Format code
make format

# Clean up build artifacts
make clean
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality. They are installed automatically during setup, but you can manually install them with:

```bash
pre-commit install
```

## License

MIT License - see LICENSE file for details. 