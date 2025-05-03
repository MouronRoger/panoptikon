"""Path utility functions for Panoptikon.

This module provides utilities for path manipulation and validation.
"""

import os
from pathlib import Path
from typing import List, Optional


def get_app_data_dir() -> Path:
    """Get the application data directory.

    Returns:
        Path to the application data directory
    """
    home = Path.home()
    app_data_dir = home / ".panoptikon"
    app_data_dir.mkdir(exist_ok=True)
    return app_data_dir


def get_db_path() -> Path:
    """Get the path to the database file.

    Returns:
        Path to the database file
    """
    return get_app_data_dir() / "panoptikon.db"


def get_config_path() -> Path:
    """Get the path to the configuration file.

    Returns:
        Path to the configuration file
    """
    return get_app_data_dir() / "config.json"


def is_hidden(path: Path) -> bool:
    """Check if a path is hidden.

    Args:
        path: Path to check

    Returns:
        True if the path is hidden, False otherwise
    """
    # macOS hidden files start with a dot
    return path.name.startswith(".")


def get_user_home_dir() -> Path:
    """Get the user's home directory.

    Returns:
        Path to the user's home directory
    """
    return Path.home()


def normalize_path(path: str) -> Path:
    """Normalize a path string to a Path object.

    Args:
        path: Path string to normalize

    Returns:
        Normalized Path object
    """
    path_obj = Path(path).expanduser().resolve()
    return path_obj 