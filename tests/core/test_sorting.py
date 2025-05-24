from typing import Any, List, Optional, cast

import pytest

from panoptikon.search.result import SearchResult
from panoptikon.search.sorting import (
    AttributeSortCriteria,
    CustomSortCriteria,
    FolderSizeSortCriteria,
    SortCriteria,
    SortingEngine,
    SortKey,
)


class DummyResult:
    def __init__(
        self,
        name: str,
        size: Optional[int] = None,
        date: Optional[int] = None,
        extension: str = "",
        folder_size: Optional[int] = None,
        file_type: str = "file",
    ):
        self._name = name
        self._path = f"/dummy/{name}"
        self._metadata = {
            "size": size,
            "date": date,
            "extension": extension,
            "folder_size": folder_size,
            "file_type": file_type,
        }
        self.extension = extension
        self.folder_size = folder_size
        self.file_type = file_type
        self._annotations: dict[str, Any] = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> str:
        return self._path

    @property
    def metadata(self) -> dict:
        return self._metadata

    @property
    def size(self) -> Optional[int]:
        value = self._metadata["size"]
        return int(value) if value is not None else None

    @property
    def date(self) -> Optional[int]:
        value = self._metadata["date"]
        return int(value) if value is not None else None

    def annotate(self, key: str, value: Any) -> None:
        self._annotations[key] = value


@pytest.fixture
def dummy_results() -> List[DummyResult]:
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
    # With None as 1024, d(None) is smallest, then b.txt(50), c.md(75), a.txt(100), e(200)
    assert [r.name for r in sorted_results] == ["d", "b.txt", "c.md", "a.txt", "e"]


def test_sort_by_size_desc(dummy_results: List[SearchResult]) -> None:
    engine = SortingEngine()
    sorted_results = engine.apply_sort(
        dummy_results, AttributeSortCriteria("size"), "desc"
    )
    # Descending: d(None/1024) should be last
    assert [r.name for r in sorted_results] == ["e", "a.txt", "c.md", "b.txt", "d"]


def test_sort_by_folder_size_asc(dummy_results: List[SearchResult]) -> None:
    engine = SortingEngine()
    sorted_results = engine.apply_sort(dummy_results, FolderSizeSortCriteria(), "asc")
    # Ascending folder size: empty folders first, then by size
    assert [r.name for r in sorted_results] == ["c.md", "e", "d", "a.txt", "b.txt"]


@pytest.mark.xfail(reason="Folder size calculation not implemented until Stage 6")
def test_sort_by_folder_size_desc(dummy_results: List[SearchResult]) -> None:
    engine = SortingEngine()
    sorted_results = engine.apply_sort(dummy_results, FolderSizeSortCriteria(), "desc")
    # TODO: Update this test in Stage 6 when folder size calculation is implemented
    assert [r.name for r in sorted_results][0] == "b.txt"


def test_sort_by_extension_then_name(dummy_results: List[SearchResult]) -> None:
    engine = SortingEngine()
    sorted_results = engine.apply_sort(
        dummy_results,
        [AttributeSortCriteria("extension"), AttributeSortCriteria("name")],
        "asc",
    )
    assert sorted_results[0].extension == ""  # type: ignore[attr-defined]
    assert sorted_results[-1].extension == "txt"  # type: ignore[attr-defined]


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
    sorted_results = engine.apply_sort(
        cast(List[SearchResult], results), AttributeSortCriteria("size"), "asc"
    )
    assert [r.name for r in sorted_results] == ["a.txt", "b.txt", "c.txt"]


def test_sort_empty_result_set() -> None:
    """Sorting an empty result set should return an empty list."""
    engine = SortingEngine()
    results: list[SearchResult] = []
    sorted_results = engine.apply_sort(results, AttributeSortCriteria("name"), "asc")
    assert sorted_results == []


def test_sort_all_none_values() -> None:
    """Sorting when all attribute values are None should preserve order."""

    class NoneResult:
        name = None
        size = None
        metadata = {"folder_size": None}

    engine = SortingEngine()
    results = [cast(SearchResult, NoneResult()), cast(SearchResult, NoneResult())]
    sorted_results = engine.apply_sort(results, AttributeSortCriteria("size"), "asc")
    assert sorted_results == results


def test_sort_unknown_criteria_fallback() -> None:
    """Sorting with an unknown criteria type should fallback to original order."""

    class DummyCriteria(SortCriteria):
        def apply_to_query(self, query: Any, direction: str = "asc") -> Any:
            return query

        def compare(
            self, r1: SearchResult, r2: SearchResult, direction: str = "asc"
        ) -> int:
            return 0

    engine = SortingEngine()
    results = [
        cast(SearchResult, DummyResult("a")),
        cast(SearchResult, DummyResult("b")),
    ]
    sorted_results = engine.apply_sort(results, DummyCriteria(), "asc")
    assert sorted_results == results


def test_sortkey_with_unknown_criteria() -> None:
    """SortKey should handle unknown criteria gracefully."""

    class UnknownCriteria(SortCriteria):
        def apply_to_query(self, query: Any, direction: str = "asc") -> Any:
            return query

        def compare(
            self, r1: SearchResult, r2: SearchResult, direction: str = "asc"
        ) -> int:
            return 0

    dummy = DummyResult("a")
    key = SortKey(dummy, [UnknownCriteria()], "asc")
    # Should return float('-inf') for unknown
    assert key.values == [float("-inf")]


def test_create_sort_criteria_with_custom_fn() -> None:
    """SortingEngine.create_sort_criteria should return CustomSortCriteria if custom_fn is given."""
    engine = SortingEngine()

    def cmp(r1: SearchResult, r2: SearchResult) -> int:
        return 0

    crit = engine.create_sort_criteria("name", custom_fn=cmp)
    assert isinstance(crit, CustomSortCriteria)


def test_create_sort_criteria_default() -> None:
    """SortingEngine.create_sort_criteria should return AttributeSortCriteria if no custom_fn is given."""
    engine = SortingEngine()
    crit = engine.create_sort_criteria("name")
    assert isinstance(crit, AttributeSortCriteria)


def test_comparator_sort_direction_param() -> None:
    """Test comparator sort with criteria that does and does not accept direction param."""

    class NoDirectionCriteria(SortCriteria):
        def apply_to_query(self, query: Any, direction: str = "asc") -> Any:
            return query

        def compare(
            self, r1: SearchResult, r2: SearchResult, direction: str = "asc"
        ) -> int:
            return 0

    class WithDirectionCriteria(SortCriteria):
        def apply_to_query(self, query: Any, direction: str = "asc") -> Any:
            return query

        def compare(
            self, r1: SearchResult, r2: SearchResult, direction: str = "asc"
        ) -> int:
            return 0

    engine = SortingEngine()
    results = [
        cast(SearchResult, DummyResult("a")),
        cast(SearchResult, DummyResult("b")),
    ]
    # Should not raise
    sorted_results = engine.apply_sort(
        results, [NoDirectionCriteria(), WithDirectionCriteria()], "asc"
    )
    assert sorted_results == results
