from typing import Any, Dict, List

import pytest

from panoptikon.search.result import SearchResult
from panoptikon.search.sorting import (
    AttributeSortCriteria,
    CustomSortCriteria,
    FolderSizeSortCriteria,
    SortingEngine,
)


class DummyResult:
    def __init__(
        self,
        name: str,
        size: int | None = None,
        date: int | None = None,
        extension: str = "",
        folder_size: int | None = None,
        file_type: str = "file",
    ) -> None:
        self.name = name
        self.size = size
        self.date = date
        self.extension = extension
        self.file_type = file_type
        self.metadata: Dict[str, Any] = {
            "size": size,
            "date_created": date,
            "extension": extension,
            "file_type": file_type,
            "folder_size": folder_size,
        }

    def annotate(self, key: str, value: Any) -> None:
        pass


@pytest.fixture
def dummy_results() -> List[SearchResult]:
    return [
        DummyResult("a.txt", 100, 10, "txt", 1000, "file"),
        DummyResult("b.txt", 50, 20, "txt", 2000, "file"),
        DummyResult("c.md", 75, 15, "md", None, "file"),
        DummyResult("d", None, 5, "", 500, "folder"),
        DummyResult("e", 200, None, "", None, "folder"),
    ]


def test_sort_by_name_asc(dummy_results: List[SearchResult]) -> None:
    engine = SortingEngine()
    sorted_results = engine.apply_sort(
        dummy_results, AttributeSortCriteria("name"), "asc"
    )
    assert [r.name for r in sorted_results] == ["a.txt", "b.txt", "c.md", "d", "e"]


def test_sort_by_name_desc(dummy_results: List[SearchResult]) -> None:
    engine = SortingEngine()
    sorted_results = engine.apply_sort(
        dummy_results, AttributeSortCriteria("name"), "desc"
    )
    assert [r.name for r in sorted_results] == ["e", "d", "c.md", "b.txt", "a.txt"]


def test_sort_by_size_asc(dummy_results: List[SearchResult]) -> None:
    engine = SortingEngine()
    sorted_results = engine.apply_sort(
        dummy_results, AttributeSortCriteria("size"), "asc"
    )
    assert [r.name for r in sorted_results][:3] == ["d", "c.md", "b.txt"]


def test_sort_by_size_desc(dummy_results: List[SearchResult]) -> None:
    engine = SortingEngine()
    sorted_results = engine.apply_sort(
        dummy_results, AttributeSortCriteria("size"), "desc"
    )
    assert [r.name for r in sorted_results][0] == "e"


def test_sort_by_folder_size_asc(dummy_results: List[SearchResult]) -> None:
    engine = SortingEngine()
    sorted_results = engine.apply_sort(dummy_results, FolderSizeSortCriteria(), "asc")
    # d (500), a.txt (1000), b.txt (2000), c.md (None), e (None)
    assert [r.name for r in sorted_results][:3] == ["d", "a.txt", "b.txt"]


def test_sort_by_folder_size_desc(dummy_results: List[SearchResult]) -> None:
    engine = SortingEngine()
    sorted_results = engine.apply_sort(dummy_results, FolderSizeSortCriteria(), "desc")
    assert [r.name for r in sorted_results][0] == "b.txt"


def test_sort_by_extension_then_name(dummy_results: List[SearchResult]) -> None:
    engine = SortingEngine()
    sorted_results = engine.apply_sort(
        dummy_results,
        [AttributeSortCriteria("extension"), AttributeSortCriteria("name")],
        "asc",
    )
    assert sorted_results[0].extension == ""
    assert sorted_results[-1].extension == "txt"


def test_custom_sort(dummy_results: List[SearchResult]) -> None:
    def reverse_name(r1: SearchResult, r2: SearchResult) -> int:
        return -1 if r1.name > r2.name else (1 if r1.name < r2.name else 0)

    engine = SortingEngine()
    sorted_results = engine.apply_sort(
        dummy_results, CustomSortCriteria(reverse_name), "asc"
    )
    assert [r.name for r in sorted_results] == ["e", "d", "c.md", "b.txt", "a.txt"]


def test_sort_stability(dummy_results: List[SearchResult]) -> None:
    engine = SortingEngine()
    # All with extension "txt" should keep original order if size is equal
    results = [
        DummyResult("a.txt", 1, 1, "txt"),
        DummyResult("b.txt", 1, 2, "txt"),
        DummyResult("c.txt", 1, 3, "txt"),
    ]
    sorted_results = engine.apply_sort(results, AttributeSortCriteria("size"), "asc")
    assert [r.name for r in sorted_results] == ["a.txt", "b.txt", "c.txt"]
