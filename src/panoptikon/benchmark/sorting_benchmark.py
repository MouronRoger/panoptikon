"""Sorting performance benchmark core logic for Panoptikon."""

from __future__ import annotations

from collections.abc import Sequence
import statistics
import time

from panoptikon.search.result import SearchResult
from panoptikon.search.sorting import SortCriteria, SortingEngine


def run_sorting_benchmark(
    files: Sequence[SearchResult],
    sorting_engine: SortingEngine,
    sort_criteria_list: list[tuple[str, SortCriteria | list[SortCriteria], str]],
    iterations: int = 5,
) -> dict[str, dict[str, float]]:
    """Benchmark sorting performance on the provided files using the given sorting engine.

    Args:
        files: Sequence of SearchResult objects to sort.
        sorting_engine: SortingEngine instance to use.
        sort_criteria_list: List of tuples (sort_name, criteria, direction).
        iterations: Number of times to run each sort for consistency.

    Returns:
        Dictionary mapping sort_name to statistics (mean, median, min, max in ms).
    """
    results: dict[str, dict[str, float]] = {}
    for sort_name, criteria, direction in sort_criteria_list:
        times: list[float] = []
        for _ in range(iterations):
            data = list(files)  # Copy to avoid in-place sort issues
            start = time.perf_counter()
            sorting_engine.apply_sort(data, criteria, direction)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # ms
        # Drop highest and lowest for outlier reduction if enough samples
        trimmed = times
        if len(times) > 3:
            trimmed = sorted(times)[1:-1]
        results[sort_name] = {
            "mean": statistics.mean(trimmed),
            "median": statistics.median(trimmed),
            "min": min(trimmed),
            "max": max(trimmed),
        }
    return results
