import os
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from panoptikon.benchmark.sorting_benchmark import run_sorting_benchmark
from panoptikon.search.result import SearchResultImpl
from panoptikon.search.sorting import (
    AttributeSortCriteria,
    FolderSizeSortCriteria,
    SortingEngine,
)


def collect_filesystem_data(start_path: str, max_files: int = 20000) -> list:
    files: list = []
    for root, dirs, filenames in os.walk(start_path, topdown=True):
        if len(files) >= max_files:
            break
        for fname in filenames:
            if len(files) >= max_files:
                break
            fpath = os.path.join(root, fname)
            try:
                stat = os.stat(fpath)
                files.append(
                    SearchResultImpl(
                        name=fname,
                        path=fpath,
                        metadata={
                            "size": stat.st_size,
                            "date_created": getattr(stat, "st_ctime", 0),
                            "date_modified": getattr(stat, "st_mtime", 0),
                            "extension": os.path.splitext(fname)[1][1:],
                            "file_type": "file",
                            "folder_size": None,
                        },
                    )
                )
            except Exception:
                continue
        for dname in dirs:
            if len(files) >= max_files:
                break
            dpath = os.path.join(root, dname)
            try:
                stat = os.stat(dpath)
                folder_size = 0
                for dirpath, _, fnames in os.walk(dpath):
                    for fn in fnames:
                        try:
                            fstat = os.stat(os.path.join(dirpath, fn))
                            folder_size += fstat.st_size
                        except Exception:
                            continue
                files.append(
                    SearchResultImpl(
                        name=dname,
                        path=dpath,
                        metadata={
                            "size": stat.st_size,
                            "date_created": getattr(stat, "st_ctime", 0),
                            "date_modified": getattr(stat, "st_mtime", 0),
                            "extension": "",
                            "file_type": "folder",
                            "folder_size": folder_size,
                        },
                    )
                )
            except Exception:
                continue
    return files


@pytest.mark.skipif(
    len(collect_filesystem_data(str(Path.home()), 10000)) < 10000,
    reason="Not enough files for live sorting performance test",
)
def test_sorting_performance_live() -> None:
    files = collect_filesystem_data(str(Path.home()), 20000)
    engine = SortingEngine()
    sort_criteria_list = [
        ("Sort by name (asc)", AttributeSortCriteria("name"), "asc"),
        ("Sort by name (desc)", AttributeSortCriteria("name"), "desc"),
        ("Sort by date_modified (asc)", AttributeSortCriteria("date_modified"), "asc"),
        (
            "Sort by date_modified (desc)",
            AttributeSortCriteria("date_modified"),
            "desc",
        ),
        ("Sort by size (asc)", AttributeSortCriteria("size"), "asc"),
        ("Sort by size (desc)", AttributeSortCriteria("size"), "desc"),
        ("Sort by folder size (asc)", FolderSizeSortCriteria(), "asc"),
        ("Sort by folder size (desc)", FolderSizeSortCriteria(), "desc"),
        (
            "Sort by directory+name (asc)",
            [AttributeSortCriteria("file_type"), AttributeSortCriteria("name")],
            "asc",
        ),
    ]
    results = run_sorting_benchmark(files, engine, sort_criteria_list, iterations=5)
    for sort_name, stats in results.items():
        assert stats["mean"] <= 100, (
            f"{sort_name} exceeded 100ms: {stats['mean']:.2f}ms"
        )
