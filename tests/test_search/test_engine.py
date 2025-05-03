"""Tests for the search engine."""

from pathlib import Path

import pytest

from panoptikon.search.engine import SearchEngine, SearchResult


def test_search_result_init():
    """Test search result initialization."""
    path = Path("/tmp/test.txt")
    score = 0.75
    metadata = {"type": "text", "size": "10KB"}
    
    result = SearchResult(path, score, metadata)
    
    assert result.path == path
    assert result.score == score
    assert result.metadata == metadata
    
    # Test string representation
    assert str(result) == f"{path} (score: 0.75)"


def test_search_result_default_values():
    """Test search result with default values."""
    path = Path("/tmp/test.txt")
    
    result = SearchResult(path)
    
    assert result.path == path
    assert result.score == 1.0
    assert result.metadata == {}


def test_search_engine_init():
    """Test search engine initialization."""
    engine = SearchEngine()
    
    assert engine.index == {}


def test_search_engine_add_to_index():
    """Test adding files to the search index."""
    engine = SearchEngine()
    
    # Add some files to the index
    paths = [
        Path("/tmp/file1.txt"),
        Path("/tmp/file2.md"),
        Path("/home/user/document.pdf"),
    ]
    
    for path in paths:
        engine.add_to_index(path)
    
    # Check that filenames are indexed
    assert "file1.txt" in engine.index
    assert "file2.md" in engine.index
    assert "document.pdf" in engine.index
    
    # Check that path parts are indexed
    assert "tmp" in engine.index
    assert "home" in engine.index
    assert "user" in engine.index


@pytest.mark.parametrize(
    "query,expected_count",
    [
        ("file", 2),  # Matches file1.txt and file2.md
        ("txt", 1),   # Matches file1.txt
        ("pdf", 1),   # Matches document.pdf
        ("nonexistent", 0),  # No matches
        ("", 0),      # Empty query returns empty results
    ],
)
def test_search_engine_search(query, expected_count):
    """Test searching the index.
    
    Args:
        query: Search query to test
        expected_count: Expected number of search results
    """
    engine = SearchEngine()
    
    # Add some files to the index
    paths = [
        Path("/tmp/file1.txt"),
        Path("/tmp/file2.md"),
        Path("/home/user/document.pdf"),
    ]
    
    for path in paths:
        engine.add_to_index(path)
    
    # Perform the search
    results = engine.search(query)
    
    # Check the number of results
    assert len(results) == expected_count
    
    # Check that results are SearchResult objects
    assert all(isinstance(r, SearchResult) for r in results) 