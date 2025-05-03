"""Pytest configuration for Panoptikon tests."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests.

    Yields:
        Path: Path to the temporary directory
    """
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_files(temp_dir):
    """Create sample files for testing.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path: Path to the directory containing sample files
    """
    # Create a directory structure with some files
    sample_dir = temp_dir / "sample"
    sample_dir.mkdir()

    # Create a few test files
    files = [
        "file1.txt",
        "file2.md",
        "image.jpg",
        "document.pdf",
    ]

    for file_name in files:
        file_path = sample_dir / file_name
        with open(file_path, "w") as f:
            f.write(f"Content for {file_name}")

    # Create a subdirectory with files
    subdir = sample_dir / "subdir"
    subdir.mkdir()
    
    subdir_files = [
        "subfile1.txt",
        "subfile2.py",
    ]
    
    for file_name in subdir_files:
        file_path = subdir / file_name
        with open(file_path, "w") as f:
            f.write(f"Content for {file_name}")

    return sample_dir


@pytest.fixture
def mock_db_path(temp_dir):
    """Create a temporary database path.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path: Path to the temporary database file
    """
    return temp_dir / "test.db" 