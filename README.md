# Panoptikon

> **Knowledge System:** The canonical sources are: 1) Markdown files in `/docs/*` (truth), 2) MCP Knowledge Graph in `memory.jsonl` (relationships), 3) Session logs in `ai_docs.md` (history). Qdrant is just a search tool. See [AI_DOCUMENTATION_GUIDE.md](docs/AI_DOCUMENTATION_GUIDE.md) for details.

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

## Type Checking

This project uses [Pyright](https://github.com/microsoft/pyright) for static type checking, with [mypy](http://mypy-lang.org/) temporarily retained during migration. See `docs/spec/Pyright Migration Plan - Post Phase 4.md` for details.

To run type checks:

```bash
pyright
mypy src/panoptikon
```

## License

MIT License - see LICENSE file for details.

## Database Connection Pool System

### Overview
Panoptikon uses a robust, thread-safe connection pool for SQLite database access. The pool provides:
- Efficient connection reuse and recycling
- Health monitoring and automatic reconnection
- Support for transactions, savepoints, and context manager usage
- Detailed metrics and structured logging for debugging and performance analysis

### Quick Start Usage
```python
from panoptikon.database.pool import ConnectionPool
from pathlib import Path

# Create and initialize a pool
pool = ConnectionPool(db_path=Path("mydb.sqlite3"), max_connections=10)
pool.initialize()

# Acquire a connection (context manager)
with pool.get_connection() as conn:
    conn.execute("SELECT 1")

# Run a transaction
with pool.transaction() as conn:
    conn.execute("INSERT INTO mytable (col) VALUES (?)", ("value",))

# Use a savepoint (nested transaction)
with pool.transaction() as conn:
    with pool.savepoint("sp1") as sp_conn:
        sp_conn.execute("UPDATE mytable SET col=? WHERE id=?", ("new", 1))
```

### Thread-Safety and SQLite Limitations
- **Thread-Safety:** All public methods are thread-safe. Each thread gets its own connection; connections are never shared between threads.
- **SQLite Single-Writer Limitation:** Only one write transaction can be active at a time. Under high concurrency, some threads may experience `database is locked` errors or timeouts. The pool will retry and recycle connections as needed, but users should expect write contention and handle exceptions accordingly.

### Metrics and Debugging
- **Metrics:** Call `pool.get_stats()` to get detailed metrics, including:
  - Active/idle/created/closed connections
  - Total acquisitions, timeouts, acquisition times (avg/max/percentiles)
  - Health check failures, connection errors, peak usage, recycled connections
- **Performance Tracking:** The pool tracks rolling window acquisition times and error counts for percentiles and trends.
- **Debug Mode:** Set `pool.debug_mode = True` to enable stack trace and state transition logging for each connection (for development only).
- **Structured Logging:** Key events (acquisition, timeout, health check fail, state transitions) are logged with structured fields for easy analysis.

### Custom Exception Hierarchy
- `ConnectionPoolError`: Base exception for all pool-related errors
- `ConnectionAcquisitionTimeout`: Raised when a connection cannot be acquired within the timeout
- `ConnectionHealthError`: Raised when a connection is found to be unhealthy

### Performance Benchmarking
- Run the benchmark script:
  ```sh
  python scripts/benchmark_pool.py
  ```
- Results are output to the console and to `benchmark_results.md` (Markdown table).
- Benchmarks include connection acquisition latency and transaction throughput under various thread counts.

### Configuration Options
| Option                  | Default   | Description                                      |
|-------------------------|-----------|--------------------------------------------------|
| db_path                 | (required)| Path to the SQLite database file                  |
| max_connections         | 10        | Maximum number of connections in the pool         |
| min_connections         | 1         | Minimum number of connections to maintain         |
| connection_timeout      | 5.0       | Timeout (seconds) for acquiring a connection      |
| connection_max_age      | 600.0     | Max age (seconds) before recycling a connection   |
| health_check_interval   | 60.0      | Interval (seconds) between health checks          |

### Migration Notes
- If upgrading from a previous version:
  - All Pydantic validators have been migrated to v2 (`@field_validator`).
  - The connection pool now uses a custom exception hierarchy; update your error handling accordingly.
  - The pool exposes enhanced metrics and structured logging for easier debugging and monitoring.
  - See the migration plan in `docs/spec/phases/phase4_3_migration_plan.md` for schema changes and data migration steps (if any).

## Knowledge System (Canonical)

Panoptikon uses a robust, script-driven knowledge/documentation system. The canonical specification is in `docs/spec/knowledge-system-mid-path-3.md`.

### Key Scripts
- `scripts/knowledge/memory_manager.py`: CLI for adding, listing, and pruning entities and relations in the knowledge memory file.
- `scripts/knowledge/relationship_extractor.py`: Extracts relationships from markdown documentation and adds them to the memory file.
- `scripts/knowledge/gen_template.py`: Generates documentation templates with a relationships section for components, decisions, or phases.
- `scripts/knowledge/doc_lint.py`: Lints documentation files to ensure relationship sections are present and non-empty (used in pre-commit and CI).

**All documentation and knowledge graph operations should follow the canonical spec.** 