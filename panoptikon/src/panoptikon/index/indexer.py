"""File system indexer for Panoptikon.

This module handles the crawling and indexing of files in the file system.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set

from panoptikon.db import file_store
from panoptikon.utils import path_utils


def index_path(path: str, recursive: bool = True) -> int:
    """Index files in the specified path.

    Args:
        path: The directory path to index.
        recursive: Whether to recursively index subdirectories.

    Returns:
        int: Number of files indexed.

    Raises:
        FileNotFoundError: If the specified path does not exist.
        PermissionError: If permission is denied for accessing the path.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    
    if not path_obj.is_dir():
        # Index a single file
        _index_file(path_obj)
        return 1
    
    return _index_directory(path_obj, recursive=recursive)


def index_default_paths() -> int:
    """Index the default paths configured for the application.

    Returns:
        int: Number of files indexed.
    """
    from panoptikon.config import config_manager
    
    config = config_manager.get_config()
    paths = config.get("index", {}).get("default_paths", [])
    
    total_indexed = 0
    for path in paths:
        try:
            total_indexed += index_path(path)
        except (FileNotFoundError, PermissionError) as e:
            # Log the error but continue with other paths
            print(f"Error indexing {path}: {e}")
    
    return total_indexed


def _index_directory(directory: Path, recursive: bool = True) -> int:
    """Index all files within a directory.

    Args:
        directory: The directory path to index.
        recursive: Whether to recursively index subdirectories.

    Returns:
        int: Number of files indexed.
    """
    indexed_count = 0
    
    try:
        # Get the list of excluded paths and extensions from config
        from panoptikon.config import config_manager
        
        config = config_manager.get_config()
        excluded_paths = set(config.get("index", {}).get("excluded_paths", []))
        excluded_extensions = set(config.get("index", {}).get("excluded_extensions", []))
        
        # Walk the directory
        for item in directory.iterdir():
            # Skip if the path is in excluded paths
            if str(item) in excluded_paths or any(item.match(pattern) for pattern in excluded_paths):
                continue
            
            if item.is_file():
                # Skip if the file extension is excluded
                if item.suffix.lower() in excluded_extensions:
                    continue
                
                _index_file(item)
                indexed_count += 1
            
            elif item.is_dir() and recursive:
                # Recursively index subdirectories
                indexed_count += _index_directory(item, recursive=True)
    
    except PermissionError:
        # Log the error but continue with accessible directories
        print(f"Permission denied for directory: {directory}")
    
    return indexed_count


def _index_file(file_path: Path) -> None:
    """Index a single file.

    Args:
        file_path: Path to the file to index.
    """
    file_info = {
        "path": str(file_path),
        "name": file_path.name,
        "extension": file_path.suffix.lower(),
        "size": file_path.stat().st_size,
        "modified_time": file_path.stat().st_mtime,
        "parent_dir": str(file_path.parent)
    }
    
    # Store the file information in the database
    file_store.save_file_info(file_info) 