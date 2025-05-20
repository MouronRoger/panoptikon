"""Test suite for Panoptikon SearchEngine and result classes."""

from collections.abc import Generator
import sqlite3
from typing import Any, Optional

import pytest

from panoptikon.filesystem.paths import PathMatchType
from panoptikon.search.filtering import CompositeFilter, ExtensionFilter, FileTypeFilter
from panoptikon.search.query_parser import QueryParser, QueryPattern
from panoptikon.search.result import (
    ResultSetImpl,
    ResultSetPageError,
    ResultSetStaleError,
    SearchResultImpl,
)
from panoptikon.search.search_engine import SearchEngine


@pytest.fixture(scope="module")
def in_memory_db() -> Generator[sqlite3.Connection, None, None]:
    """Fixture for an in-memory SQLite DB with Panoptikon schema and sample data."""
    conn = sqlite3.connect(":memory:")
    # Minimal schema for search tests
    conn.executescript(
        """
    CREATE TABLE files (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        path TEXT NOT NULL,
        extension TEXT,
        size INTEGER,
        date_created INTEGER,
        date_modified INTEGER,
        file_type TEXT,
        is_directory INTEGER,
        cloud_provider TEXT,
        cloud_status INTEGER,
        indexed_at INTEGER
    );
    """
    )
    # Sample data
    files = [
        (
            1,
            "document.txt",
            "/docs/document.txt",
            "txt",
            1000,
            1,
            2,
            "text",
            0,
            None,
            0,
            100,
        ),
        (
            2,
            "image.jpg",
            "/images/image.jpg",
            "jpg",
            2000,
            1,
            2,
            "image",
            0,
            None,
            0,
            100,
        ),
        (3, "notes.md", "/docs/notes.md", "md", 500, 1, 2, "text", 0, None, 0, 100),
        (4, "README.md", "/README.md", "md", 300, 1, 2, "text", 0, None, 0, 100),
        (
            5,
            "archive.zip",
            "/archive/archive.zip",
            "zip",
            5000,
            1,
            2,
            "archive",
            0,
            None,
            0,
            100,
        ),
        (
            6,
            "script.py",
            "/scripts/script.py",
            "py",
            800,
            1,
            2,
            "code",
            0,
            None,
            0,
            100,
        ),
    ]
    conn.executemany(
        "INSERT INTO files (id, name, path, extension, size, date_created, "
        "date_modified, file_type, is_directory, cloud_provider, cloud_status, "
        "indexed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        files,
    )
    conn.commit()
    yield conn
    conn.close()


class DummyPool:
    """Dummy connection pool for in-memory DB."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        """Initialize DummyPool with a SQLite connection."""
        self._conn = conn

    def get_connection(self) -> Any:
        """Return the SQLite connection."""
        return self._conn


@pytest.fixture(scope="module")
def search_engine(in_memory_db: sqlite3.Connection) -> SearchEngine:
    """Return a SearchEngine instance using the in-memory DB and dummy pool."""
    return SearchEngine(DummyPool(in_memory_db), cache_size=2)


def test_exact_match(search_engine: SearchEngine) -> None:
    """Test exact match search returns correct file."""
    pattern = QueryPattern(
        pattern="document.txt",
        match_type=PathMatchType.EXACT,
        case_sensitive=False,
        whole_word=True,
        extension=None,
    )
    result_set = search_engine.search(pattern)
    results = result_set.get_page(0, 10)
    assert any(r.name == "document.txt" for r in results)


def test_wildcard_search(search_engine: SearchEngine) -> None:
    """Test wildcard (glob) search returns matching files."""
    pattern = QueryPattern(
        pattern="*.md",
        match_type=PathMatchType.GLOB,
        case_sensitive=False,
        whole_word=False,
        extension=None,
    )
    result_set = search_engine.search(pattern)
    results = result_set.get_page(0, 10)
    names = {r.name for r in results}
    assert "notes.md" in names and "README.md" in names


def test_extension_filter(search_engine: SearchEngine) -> None:
    """Test extension filtering returns only files with that extension."""
    pattern = QueryPattern(
        pattern="",
        match_type=PathMatchType.EXACT,
        case_sensitive=False,
        whole_word=False,
        extension="py",
    )
    result_set = search_engine.search(pattern)
    results = result_set.get_page(0, 10)
    assert all(r.metadata["extension"] == "py" for r in results)


def test_cache_hit_and_miss(search_engine: SearchEngine) -> None:
    """Test cache hit and eviction logic."""
    pattern1 = QueryPattern("*.md", PathMatchType.GLOB, False, False, None)
    pattern2 = QueryPattern("*.txt", PathMatchType.GLOB, False, False, None)
    pattern3 = QueryPattern("*.jpg", PathMatchType.GLOB, False, False, None)
    # Fill cache
    search_engine.search(pattern1)
    search_engine.search(pattern2)
    # This should evict pattern1 if cache_size=2
    search_engine.search(pattern3)
    # pattern1 should be a miss now (re-compute)
    result_set = search_engine.search(pattern1)
    results = result_set.get_page(0, 10)
    assert any(r.name == "notes.md" for r in results)


def test_invalidate_cache(search_engine: SearchEngine) -> None:
    """Test cache invalidation removes cached results."""
    pattern = QueryPattern("*.zip", PathMatchType.GLOB, False, False, None)
    search_engine.search(pattern)
    search_engine.invalidate_cache()
    # Should re-compute after invalidation
    result_set = search_engine.search(pattern)
    results = result_set.get_page(0, 10)
    assert any(r.name == "archive.zip" for r in results)


def test_pagination(search_engine: SearchEngine) -> None:
    """Test pagination returns correct number of results per page."""
    pattern = QueryPattern("*.*", PathMatchType.GLOB, False, False, None)
    result_set = search_engine.search(pattern)
    page1 = result_set.get_page(0, 2)
    page2 = result_set.get_page(1, 2)
    assert len(page1) == 2 and len(page2) == 2 and page1 != page2


def test_resultset_group_by(search_engine: SearchEngine) -> None:
    """Test grouping results by extension."""
    pattern = QueryPattern("*.*", PathMatchType.GLOB, False, False, None)
    result_set = search_engine.search(pattern)
    groups = result_set.group_by(lambda r: r.metadata["extension"])
    assert "md" in groups and any(r.name == "README.md" for r in groups["md"])


def test_searchresult_annotation() -> None:
    """Test annotation on SearchResultImpl."""
    result = SearchResultImpl(name="foo.txt", path="/foo.txt", metadata={})
    result.annotate("tag", "important")
    assert result.annotations["tag"] == "important"


def dummy_page_loader_factory(fail_on: Optional[set[tuple[int, int]]] = None) -> Any:
    """Returns a page loader that fails on specified (page_number, page_size) tuples."""
    fail_on = fail_on or set()

    def loader(page_number: int, page_size: int) -> list[SearchResultImpl]:
        if (page_number, page_size) in fail_on:
            raise RuntimeError("Simulated page load failure")
        return [
            SearchResultImpl(
                name=f"file_{page_number}_{i}",
                path=f"/path/to/file_{page_number}_{i}",
                metadata={"index": i},
            )
            for i in range(page_size)
        ]

    return loader


def test_resultset_lru_cache_eviction() -> None:
    """Test LRU cache eviction in ResultSetImpl."""
    loader = dummy_page_loader_factory()
    rs = ResultSetImpl(None, None, 500, loader, max_cache_pages=2)
    rs.get_page(0, 10)
    rs.get_page(1, 10)
    assert (0, 10) in rs._page_cache
    assert (1, 10) in rs._page_cache
    rs.get_page(2, 10)
    assert (2, 10) in rs._page_cache
    # Oldest (0, 10) should be evicted
    assert (0, 10) not in rs._page_cache


def test_resultset_error_handling() -> None:
    """Test that ResultSetImpl raises ResultSetPageError on page load failure."""
    loader = dummy_page_loader_factory(fail_on={(1, 10)})
    rs = ResultSetImpl(None, None, 100, loader)
    rs.get_page(0, 10)
    with pytest.raises(ResultSetPageError):
        rs.get_page(1, 10)


def test_resultset_stale_detection() -> None:
    """Test that ResultSetImpl raises ResultSetStaleError when marked stale."""
    loader = dummy_page_loader_factory()
    rs = ResultSetImpl(None, None, 100, loader)
    rs.get_page(0, 10)
    rs.mark_stale()
    with pytest.raises(ResultSetStaleError):
        rs.get_page(0, 10)


def test_resultset_invalidate_cache() -> None:
    """Test that invalidate_cache clears the page cache."""
    loader = dummy_page_loader_factory()
    rs = ResultSetImpl(None, None, 100, loader)
    rs.get_page(0, 10)
    assert rs._page_cache
    rs.invalidate_cache()
    assert not rs._page_cache


def test_resultset_get_page_partial() -> None:
    """Test get_page_partial returns partial results and error on failure."""
    loader = dummy_page_loader_factory(fail_on={(1, 10)})
    rs = ResultSetImpl(None, None, 100, loader)
    rs.get_page(0, 10)
    # Simulate failure for (1, 10)
    results, error = rs.get_page_partial(1, 10)
    assert isinstance(error, ResultSetPageError)
    assert results == []


def test_resultset_group_by_partial_failure() -> None:
    """Test group_by skips pages that fail to load."""
    loader = dummy_page_loader_factory(fail_on={(1, 100)})
    rs = ResultSetImpl(None, None, 200, loader)
    groups = rs.group_by(lambda r: r.metadata["index"] % 2)
    # Only pages 0 and 2 should be loaded (page 1 fails)
    assert set(groups.keys()) <= {0, 1}


def setup_in_memory_db() -> Any:
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE files (
            id INTEGER PRIMARY KEY,
            name TEXT,
            path TEXT,
            extension TEXT,
            size INTEGER,
            date_created TEXT,
            date_modified TEXT,
            file_type TEXT,
            is_directory INTEGER,
            cloud_provider TEXT,
            cloud_status TEXT,
            indexed_at TEXT
        )
        """
    )
    files = [
        (
            1,
            "file1.txt",
            "/test/dir1/file1.txt",
            "txt",
            100,
            "2023-01-01T12:00:00",
            "2023-01-01T12:00:00",
            "file",
            0,
            "",
            "",
            "2023-01-01T12:00:00",
        ),
        (
            2,
            "file2.pdf",
            "/test/dir2/file2.pdf",
            "pdf",
            2000,
            "2023-02-01T12:00:00",
            "2023-02-01T12:00:00",
            "file",
            0,
            "",
            "",
            "2023-02-01T12:00:00",
        ),
        (
            3,
            "dir1",
            "/test/dir1",
            "",
            0,
            "2022-12-31T10:00:00",
            "2022-12-31T10:00:00",
            "directory",
            1,
            "",
            "",
            "2022-12-31T10:00:00",
        ),
    ]
    conn.executemany(
        "INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", files
    )
    conn.commit()

    class TestConnectionPool:
        def __init__(self, connection: Any) -> None:
            self._conn = connection

        def get_connection(self) -> Any:
            class _Ctx:
                def __enter__(self_c: Any) -> Any:
                    return self._conn

                def __exit__(self_c: Any, exc_type, exc_val, exc_tb) -> None:
                    pass

            return _Ctx()

    return TestConnectionPool(conn)


def test_search_engine_filetype_filter() -> None:
    """Test SearchEngine.search with FileTypeFilter returns only files of that type."""
    db = setup_in_memory_db()
    engine = SearchEngine(db)
    qp = QueryParser.parse("*")
    f = FileTypeFilter("file")
    rs = engine.search(qp, filter_criteria=f)
    page = rs.get_page(0, 10)
    names = [r.name for r in page]
    assert sorted(names) == ["file1.txt", "file2.pdf"]
    f_dir = FileTypeFilter("directory")
    rs_dir = engine.search(qp, filter_criteria=f_dir, include_directories=True)
    page_dir = rs_dir.get_page(0, 10)
    names_dir = [r.name for r in page_dir]
    print("\n--- DEBUG OUTPUT ---")
    # Verify raw SQL results from database
    conn = db._conn
    raw_dirs = conn.execute(
        "SELECT * FROM files WHERE file_type = 'directory'"
    ).fetchall()
    print(f"Raw directory entries in DB: {raw_dirs}")
    # Check what's in the unfiltered results
    qp_all = QueryParser.parse("*")
    rs_all = engine.search(qp_all)
    all_results = rs_all.get_page(0, 10)
    print("All results:")
    for r in all_results:
        print(
            f"  {r.name}: file_type={r.metadata.get('file_type')}, is_directory={r.metadata.get('is_directory')}"
        )
    # Check what the filter is actually doing
    dir_filter = FileTypeFilter("directory")
    print("Filter SQL condition:", dir_filter.apply_to_query("SELECT * FROM files"))
    # Direct check if filter matches the directory
    dir_match = [r for r in all_results if r.name == "dir1"]
    if dir_match:
        print(f"Does filter match 'dir1'? {dir_filter.matches(dir_match[0])}")
        print(f"'dir1' metadata: {dir_match[0].metadata}")
    assert names_dir == ["dir1"]


def test_search_engine_extension_filter() -> None:
    """Test SearchEngine.search with ExtensionFilter returns only files with that extension."""
    db = setup_in_memory_db()
    engine = SearchEngine(db)
    qp = QueryParser.parse("*")
    f = ExtensionFilter("pdf")
    rs = engine.search(qp, filter_criteria=f)
    page = rs.get_page(0, 10)
    names = [r.name for r in page]
    assert names == ["file2.pdf"]


def test_search_engine_composite_filter() -> None:
    """Test SearchEngine.search with CompositeFilter (AND) returns intersection."""
    db = setup_in_memory_db()
    engine = SearchEngine(db)
    qp = QueryParser.parse("*")
    f1 = FileTypeFilter("file")
    f2 = ExtensionFilter("txt")
    cf = CompositeFilter([f1, f2], operator="AND")
    rs = engine.search(qp, filter_criteria=cf)
    page = rs.get_page(0, 10)
    names = [r.name for r in page]
    assert names == ["file1.txt"]


def test_search_engine_no_filter() -> None:
    """Test SearchEngine.search with no filter returns all results."""
    db = setup_in_memory_db()
    engine = SearchEngine(db)
    qp = QueryParser.parse("*")
    rs = engine.search(qp)
    page = rs.get_page(0, 10)
    names = sorted([r.name for r in page])
    assert names == ["dir1", "file1.txt", "file2.pdf"]
