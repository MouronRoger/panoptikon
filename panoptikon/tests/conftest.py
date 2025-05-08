"""Test fixtures for Panoptikon."""

import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for file system testing.

    Yields:
        Path: The path to the temporary directory.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_files(temp_dir: Path) -> List[Path]:
    """Create sample files for testing.

    Args:
        temp_dir: The temporary directory to create files in.

    Returns:
        List[Path]: A list of paths to the created files.
    """
    # Create a sample directory structure with files
    files = []
    
    # Create some directories
    docs_dir = temp_dir / "docs"
    code_dir = temp_dir / "code"
    code_subdir = code_dir / "python"
    
    for dir_path in [docs_dir, code_dir, code_subdir]:
        dir_path.mkdir(exist_ok=True)
    
    # Create some files
    text_file = docs_dir / "document.txt"
    text_file.write_text("This is a sample document.")
    files.append(text_file)
    
    python_file = code_dir / "script.py"
    python_file.write_text("def hello():\n    print('Hello, world!')")
    files.append(python_file)
    
    config_file = temp_dir / "config.json"
    config_file.write_text('{"key": "value"}')
    files.append(config_file)
    
    return files


@pytest.fixture
def in_memory_db_engine() -> Engine:
    """Create an in-memory SQLite database engine for testing.

    Returns:
        Engine: SQLAlchemy database engine.
    """
    return create_engine("sqlite:///:memory:")


@pytest.fixture
def db_session(in_memory_db_engine: Engine) -> Generator[Session, None, None]:
    """Create a database session for testing.

    Args:
        in_memory_db_engine: SQLAlchemy database engine.

    Yields:
        Session: SQLAlchemy session.
    """
    Session = sessionmaker(bind=in_memory_db_engine)
    session = Session()
    
    yield session
    
    session.close()


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Create a sample configuration for testing.

    Returns:
        Dict[str, Any]: A dictionary with sample configuration values.
    """
    return {
        "index": {
            "excluded_paths": ["/tmp", "/System"],
            "excluded_extensions": [".tmp", ".bak"],
            "max_file_size_mb": 100
        },
        "search": {
            "max_results": 1000,
            "case_sensitive": False,
            "fuzzy_matching": True
        },
        "ui": {
            "theme": "light",
            "font_size": 12,
            "max_recent_searches": 10
        }
    }


@pytest.fixture
def mock_fs_event_handler() -> Callable:
    """Create a mock filesystem event handler for testing.

    Returns:
        Callable: A callable that tracks filesystem events.
    """
    events = []
    
    def handler(event_type: str, file_path: str) -> None:
        events.append({"type": event_type, "path": file_path})
    
    handler.events = events  # type: ignore
    return handler
