"""Tests for the path_utils module."""

import os
import platform
from pathlib import Path
from unittest import mock

import pytest

from panoptikon.utils.path_utils import (
    get_file_extension,
    get_file_size,
    get_parent_directories,
    is_hidden_file,
    normalize_path,
)


def test_normalize_path():
    """Test the normalize_path function with various inputs."""
    # Test with relative path
    assert "/" in normalize_path("test.txt")  # Should be converted to absolute path
    
    # Test with absolute path
    abs_path = os.path.abspath("/tmp/test.txt")
    norm_path = normalize_path(abs_path)
    assert "/" in norm_path
    assert "\\" not in norm_path  # Should use forward slashes


def test_normalize_path_case_sensitivity():
    """Test the case normalization behavior of normalize_path."""
    # Mock platform to test Windows behavior
    with mock.patch("platform.system", return_value="Windows"):
        assert normalize_path("TeSt.TxT").lower() == normalize_path("test.txt")
    
    # Mock platform to test macOS behavior
    with mock.patch("platform.system", return_value="Darwin"):
        with mock.patch.dict(os.environ, {"CASE_SENSITIVE_FS": "0"}):
            assert normalize_path("TeSt.TxT").lower() == normalize_path("test.txt")
        
        # Test case-sensitive macOS
        with mock.patch.dict(os.environ, {"CASE_SENSITIVE_FS": "1"}):
            if platform.system() != "Darwin":  # Skip if not actually on macOS
                pass
            # Note: We can't fully test case sensitivity without a real case-sensitive filesystem


def test_get_file_size(temp_dir):
    """Test the get_file_size function."""
    # Create a test file with known content
    test_file = temp_dir / "size_test.txt"
    test_content = b"hello world"
    test_file.write_bytes(test_content)
    
    # Test the function
    assert get_file_size(test_file) == len(test_content)
    
    # Test with non-existent file
    assert get_file_size(temp_dir / "nonexistent.txt") is None


def test_get_file_extension():
    """Test the get_file_extension function."""
    assert get_file_extension("file.txt") == ".txt"
    assert get_file_extension("file.TXT") == ".txt"  # Should be lowercase
    assert get_file_extension("file") == ""  # No extension
    assert get_file_extension("file.") == "."  # Empty extension
    assert get_file_extension(".gitignore") == ""  # Hidden files don't have an extension
    assert get_file_extension("path/to/file.py") == ".py"


def test_is_hidden_file():
    """Test the is_hidden_file function."""
    # On Unix-like systems, hidden files start with a dot
    if platform.system() != "Windows":
        assert is_hidden_file(".hidden_file")
        assert not is_hidden_file("visible_file")
    
    # For Windows we need to mock the API call since file attributes are controlled by the filesystem
    if platform.system() == "Windows":
        # Mock the Windows API call
        with mock.patch("ctypes.windll.kernel32.GetFileAttributesW", return_value=2):
            assert is_hidden_file("hidden_file.txt")
        
        with mock.patch("ctypes.windll.kernel32.GetFileAttributesW", return_value=0):
            assert not is_hidden_file("visible_file.txt")


def test_get_parent_directories():
    """Test the get_parent_directories function."""
    # Create a test path
    test_path = Path("/a/b/c/d.txt").absolute()
    
    # Test with default level (1)
    parents = get_parent_directories(test_path)
    assert len(parents) == 1
    assert parents[0] == str(test_path.parent)
    
    # Test with multiple levels
    parents = get_parent_directories(test_path, levels=3)
    assert len(parents) <= 3  # May be less if we hit the root
    
    # Test with path as string
    parents_str = get_parent_directories(str(test_path), levels=2)
    assert len(parents_str) <= 2 