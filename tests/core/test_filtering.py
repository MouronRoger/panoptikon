import datetime
from typing import Any

from panoptikon.search.filtering import (
    CompositeFilter,
    DateRangeFilter,
    ExtensionFilter,
    FileTypeFilter,
    FilterEngine,
    PathFilter,
    SizeRangeFilter,
)
from panoptikon.search.result import SearchResult


class DummyResult:
    """Mock SearchResult for testing filters."""

    def __init__(self, name: str, path: str, metadata: dict[str, Any]) -> None:
        self._name = name
        self._path = path
        self._metadata = metadata

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> str:
        return self._path

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata

    def annotate(self, key: str, value: Any) -> None:
        pass


def make_dummy_results() -> list[SearchResult]:
    return [
        DummyResult(
            "file1.txt",
            "/test/dir1/file1.txt",
            {
                "file_type": "file",
                "extension": "txt",
                "size": 100,
                "date_modified": datetime.datetime(2023, 1, 1, 12, 0, 0),
            },
        ),
        DummyResult(
            "file2.pdf",
            "/test/dir2/file2.pdf",
            {
                "file_type": "file",
                "extension": "pdf",
                "size": 2000,
                "date_modified": datetime.datetime(2023, 2, 1, 12, 0, 0),
            },
        ),
        DummyResult(
            "dir1",
            "/test/dir1",
            {
                "file_type": "directory",
                "extension": "",
                "size": 0,
                "date_modified": datetime.datetime(2022, 12, 31, 10, 0, 0),
            },
        ),
    ]


def test_file_type_filter() -> None:
    """Test FileTypeFilter matches correct file types."""
    results = make_dummy_results()
    f = FileTypeFilter("file")
    assert [r.name for r in results if f.matches(r)] == ["file1.txt", "file2.pdf"]
    f_dir = FileTypeFilter("directory")
    assert [r.name for r in results if f_dir.matches(r)] == ["dir1"]


def test_extension_filter() -> None:
    """Test ExtensionFilter matches correct extensions."""
    results = make_dummy_results()
    f = ExtensionFilter("txt")
    assert [r.name for r in results if f.matches(r)] == ["file1.txt"]
    f_pdf = ExtensionFilter("pdf")
    assert [r.name for r in results if f_pdf.matches(r)] == ["file2.pdf"]


def test_date_range_filter() -> None:
    """Test DateRangeFilter matches date ranges."""
    results = make_dummy_results()
    start = datetime.datetime(2023, 1, 1)
    end = datetime.datetime(2023, 1, 31)
    f = DateRangeFilter(start=start, end=end)
    assert [r.name for r in results if f.matches(r)] == ["file1.txt"]
    f_all = DateRangeFilter(
        start=datetime.datetime(2022, 1, 1), end=datetime.datetime(2023, 12, 31)
    )
    assert sorted([r.name for r in results if f_all.matches(r)]) == [
        "dir1",
        "file1.txt",
        "file2.pdf",
    ]


def test_size_range_filter() -> None:
    """Test SizeRangeFilter matches size ranges."""
    results = make_dummy_results()
    f = SizeRangeFilter(min_size=50, max_size=150)
    assert [r.name for r in results if f.matches(r)] == ["file1.txt"]
    f_large = SizeRangeFilter(min_size=1000)
    assert [r.name for r in results if f_large.matches(r)] == ["file2.pdf"]
    f_zero = SizeRangeFilter(max_size=0)
    assert [r.name for r in results if f_zero.matches(r)] == ["dir1"]


def test_path_filter() -> None:
    """Test PathFilter matches substring in path."""
    results = make_dummy_results()
    f = PathFilter("/dir1/")
    assert [r.name for r in results if f.matches(r)] == ["file1.txt"]
    f_root = PathFilter("/test/")
    assert sorted([r.name for r in results if f_root.matches(r)]) == [
        "dir1",
        "file1.txt",
        "file2.pdf",
    ]


def test_composite_filter_and() -> None:
    """Test CompositeFilter with AND logic."""
    results = make_dummy_results()
    f1 = FileTypeFilter("file")
    f2 = ExtensionFilter("txt")
    cf = CompositeFilter([f1, f2], operator="AND")
    assert [r.name for r in results if cf.matches(r)] == ["file1.txt"]


def test_composite_filter_or() -> None:
    """Test CompositeFilter with OR logic."""
    results = make_dummy_results()
    f1 = FileTypeFilter("directory")
    f2 = ExtensionFilter("pdf")
    cf = CompositeFilter([f1, f2], operator="OR")
    assert sorted([r.name for r in results if cf.matches(r)]) == ["dir1", "file2.pdf"]


def test_composite_filter_not() -> None:
    """Test CompositeFilter with NOT logic."""
    results = make_dummy_results()
    f1 = ExtensionFilter("pdf")
    cf = CompositeFilter([f1], operator="NOT")
    assert sorted([r.name for r in results if cf.matches(r)]) == ["dir1", "file1.txt"]


def test_filter_engine_apply_filter() -> None:
    """Test FilterEngine.apply_filter applies filter to result set."""
    results = make_dummy_results()
    engine = FilterEngine()
    f = FileTypeFilter("file")
    filtered = engine.apply_filter(results, f)
    assert [r.name for r in filtered] == ["file1.txt", "file2.pdf"]


def test_filter_engine_create_and_combine() -> None:
    """Test FilterEngine.create_filter and combine_filters."""
    engine = FilterEngine()
    f1 = engine.create_filter("filetype", file_type="file")
    f2 = engine.create_filter("extension", extension="txt")
    cf = engine.combine_filters([f1, f2], operator="AND")
    results = make_dummy_results()
    filtered = engine.apply_filter(results, cf)
    assert [r.name for r in filtered] == ["file1.txt"]
