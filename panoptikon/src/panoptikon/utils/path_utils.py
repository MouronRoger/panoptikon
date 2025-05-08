"""Path utilities for Panoptikon.

This module provides functions for working with file paths.
"""

import os
import platform
from pathlib import Path
from typing import Optional, Union


def normalize_path(path: Union[str, Path]) -> str:
    """Normalize a file path for consistent representation.

    This function converts a path to an absolute path with consistent separators
    and case normalization appropriate for the current platform.

    Args:
        path: The file path to normalize.

    Returns:
        Normalized path as a string.
    """
    # Convert to Path object for easier manipulation
    path_obj = Path(path).expanduser().absolute()
    
    # Convert to string with consistent separators
    normalized = str(path_obj).replace("\\", "/")
    
    # Case normalization on case-insensitive file systems
    if platform.system() == "Windows" or (
        platform.system() == "Darwin" and
        not os.getenv("CASE_SENSITIVE_FS", "0") == "1"
    ):
        normalized = normalized.lower()
    
    return normalized


def get_file_size(path: Union[str, Path]) -> Optional[int]:
    """Get the size of a file in bytes.

    Args:
        path: The file path.

    Returns:
        File size in bytes, or None if the file does not exist or is not accessible.
    """
    try:
        return Path(path).stat().st_size
    except (FileNotFoundError, PermissionError):
        return None


def get_file_extension(path: Union[str, Path]) -> str:
    """Get the file extension from a path.

    Args:
        path: The file path.

    Returns:
        The file extension (lowercase, including the dot) or empty string if none.
    """
    ext = Path(path).suffix
    return ext.lower() if ext else ""


def is_hidden_file(path: Union[str, Path]) -> bool:
    """Check if a file is hidden based on platform conventions.

    Args:
        path: The file path.

    Returns:
        True if the file is hidden, False otherwise.
    """
    # Convert to Path object
    path_obj = Path(path)
    
    # Check for hidden files based on platform
    if platform.system() == "Windows":
        # On Windows, use the FILE_ATTRIBUTE_HIDDEN attribute
        import ctypes
        
        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path_obj))  # type: ignore
        return bool(attrs & 2)  # FILE_ATTRIBUTE_HIDDEN = 2
    else:
        # On Unix-like systems, hidden files start with a dot
        return path_obj.name.startswith(".")


def get_parent_directories(path: Union[str, Path], levels: int = 1) -> list[str]:
    """Get parent directories of a path.

    Args:
        path: The file path.
        levels: Number of parent levels to return.

    Returns:
        List of parent directory paths, from closest to furthest.
    """
    path_obj = Path(path).absolute()
    parents = []
    
    for _ in range(levels):
        path_obj = path_obj.parent
        if path_obj == path_obj.parent:  # Root directory
            break
        parents.append(str(path_obj))
    
    return parents 