import random
import string
import time
from typing import Any, Dict, List, Optional

import pytest

from panoptikon.search.result import SearchResult
from panoptikon.search.sorting import (
    AttributeSortCriteria,
    FolderSizeSortCriteria,
    SortingEngine,
)


class DummyResult(SearchResult):
    def __init__(
        self,
        name: str,
        size: int,
        date: int,
        extension: str,
        folder_size: Optional[int],
        file_type: str = "file",
    ) -> None:
        self._name = name
        self._size = size
        self._date = date
        self._extension = extension
        self._file_type = file_type
        self._metadata: Dict[str, Any] = {
            "size": size,
            "date_created": date,
            "extension": extension,
            "file_type": file_type,
            "folder_size": folder_size,
        }

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> str:
        return f"/mock/{self._name}"

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata

    def annotate(self, key: str, value: Any) -> None:
        pass


def random_string(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_letters, k=length))


def generate_mock_results(n: int) -> List[SearchResult]:
    results: List[SearchResult] = []
    for _ in range(n):
        name = (
            random_string(8) + "." + random.choice(["txt", "md", "py", "csv", "json"])
        )
        size = random.randint(0, 10_000_000)
        date = random.randint(1_600_000_000, 1_700_000_000)
        extension = name.split(".")[-1]
        folder_size: Optional[int] = random.choice(
            [random.randint(0, 100_000_000), None]
        )
        file_type = random.choice(["file", "folder"])
        results.append(DummyResult(name, size, date, extension, folder_size, file_type))
    return results


@pytest.mark.parametrize("n", [10_000])
def test_sorting_performance_mock_data(n: int) -> None:
    engine = SortingEngine()
    results = generate_mock_results(n)
    # Sort by name
    t0 = time.perf_counter()
    engine.apply_sort(results, AttributeSortCriteria("name"), "asc")
    t1 = time.perf_counter()
    # Sort by size
    engine.apply_sort(results, AttributeSortCriteria("size"), "asc")
    t2 = time.perf_counter()
    # Sort by date
    engine.apply_sort(results, AttributeSortCriteria("date_created"), "asc")
    t3 = time.perf_counter()
    # Sort by folder size
    engine.apply_sort(results, FolderSizeSortCriteria(), "asc")
    t4 = time.perf_counter()
    # Multi-key sort (extension, then name)
    engine.apply_sort(
        results,
        [AttributeSortCriteria("extension"), AttributeSortCriteria("name")],
        "asc",
    )
    t5 = time.perf_counter()
    print(f"Sort by name: {1000 * (t1 - t0):.2f} ms")
    print(f"Sort by size: {1000 * (t2 - t1):.2f} ms")
    print(f"Sort by date: {1000 * (t3 - t2):.2f} ms")
    print(f"Sort by folder size: {1000 * (t4 - t3):.2f} ms")
    print(f"Sort by extension+name: {1000 * (t5 - t4):.2f} ms")
    assert (t1 - t0) < 0.1, f"Sort by name took too long: {t1 - t0:.3f}s"
    assert (t2 - t1) < 0.1, f"Sort by size took too long: {t2 - t1:.3f}s"
    assert (t3 - t2) < 0.1, f"Sort by date took too long: {t3 - t2:.3f}s"
    assert (t4 - t3) < 0.1, f"Sort by folder size took too long: {t4 - t3:.3f}s"
    assert (t5 - t4) < 0.1, f"Sort by extension+name took too long: {t5 - t4:.3f}s"
