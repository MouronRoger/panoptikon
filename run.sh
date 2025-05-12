#!/bin/bash

# Simple script to run tests and other development operations for Panoptikon

set -e

function show_help {
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  test                Run all tests"
    echo "  test-core           Run core tests only"
    echo "  test-filesystem     Run filesystem tests only"
    echo "  test-ui             Run UI tests only"
    echo "  test-memory-graph   Run memory graph tests only"
    echo "  coverage            Run tests with coverage report"
    echo "  coverage-html       Run tests with HTML coverage report"
    echo "  lint                Run linting"
    echo "  format              Run code formatters"
    echo "  clean               Clean build artifacts"
    echo "  help                Show this help message"
    echo ""
}

# Activate virtual environment if it exists and not already activated
if [ -d ".venv" ] && [ -z "$VIRTUAL_ENV" ]; then
    source .venv/bin/activate
fi

# Process commands
case "$1" in
    test)
        pytest tests
        ;;
    test-core)
        pytest tests/core
        ;;
    test-filesystem)
        pytest tests/core/test_paths.py tests/core/test_filesystem_integration.py tests/core/test_bookmarks.py \
               tests/core/test_bookmarks_enhanced.py tests/core/test_fs_watcher.py tests/core/test_fs_watcher_enhanced.py \
               tests/core/test_filesystem_events.py tests/core/test_cloud_storage.py tests/core/test_filesystem_access.py
        ;;
    test-ui)
        pytest tests/ui
        ;;
    test-memory-graph)
        # Add memory graph tests here
        echo "No specific memory graph tests found. Creating them..."
        # This will be implemented later once we create the tests
        ;;
    coverage)
        pytest --cov=src/panoptikon --cov-report=term-missing tests
        ;;
    coverage-html)
        pytest --cov=src/panoptikon --cov-report=html tests
        echo "HTML coverage report generated in htmlcov directory"
        ;;
    lint)
        ruff check src tests
        mypy src
        ;;
    format)
        ruff format src tests
        black src tests
        isort src tests
        ;;
    clean)
        rm -rf build/ dist/ *.egg-info/ .coverage htmlcov/ .pytest_cache/ 
        find . -type d -name "__pycache__" -exec rm -rf {} +
        find . -type f -name "*.pyc" -delete
        ;;
    help|*)
        show_help
        ;;
esac 