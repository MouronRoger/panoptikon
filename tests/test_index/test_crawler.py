"""Tests for the file system crawler."""

from pathlib import Path

import pytest

from panoptikon.index.crawler import FileCrawler


def test_crawler_init() -> None:
    """Test crawler initialization."""
    roots = [Path("/tmp"), Path.home()]
    excluded = {Path("/tmp/excluded")}
    patterns = {"*.tmp", "*.cache"}
    
    crawler = FileCrawler(roots, excluded, patterns)
    
    assert crawler.root_dirs == roots
    assert crawler.excluded_dirs == excluded
    assert crawler.excluded_patterns == patterns


def test_crawler_with_sample_files(sample_files: Path) -> None:
    """Test crawler with sample files.
    
    Args:
        sample_files: Fixture providing a directory with sample files
    """
    crawler = FileCrawler([sample_files])
    
    # Collect all found files
    found_files = list(crawler.crawl())
    
    # Check if all files were found (6 files: 4 in root, 2 in subdir)
    assert len(found_files) == 6
    
    # Check if paths are all Path objects
    assert all(isinstance(path, Path) for path in found_files)
    
    # Check if specific files are in the results
    file_names = [p.name for p in found_files]
    assert "file1.txt" in file_names
    assert "file2.md" in file_names
    assert "image.jpg" in file_names
    assert "document.pdf" in file_names
    assert "subfile1.txt" in file_names
    assert "subfile2.py" in file_names


def test_crawler_with_exclusions(sample_files: Path) -> None:
    """Test crawler with exclusion patterns.
    
    Args:
        sample_files: Fixture providing a directory with sample files
    """
    # Exclude txt files and the subdir directory
    patterns = {"*.txt"}
    excluded_dirs = {sample_files / "subdir"}
    
    crawler = FileCrawler([sample_files], excluded_dirs, patterns)
    
    # Collect all found files
    found_files = list(crawler.crawl())
    
    # Should find 3 files: file2.md, image.jpg, document.pdf
    # Both txt files and subdirectory should be excluded
    assert len(found_files) == 3
    
    # Check file names
    file_names = [p.name for p in found_files]
    assert "file1.txt" not in file_names  # Excluded by pattern
    assert "file2.md" in file_names
    assert "image.jpg" in file_names
    assert "document.pdf" in file_names
    assert "subfile1.txt" not in file_names  # Excluded by directory
    assert "subfile2.py" not in file_names  # Excluded by directory 