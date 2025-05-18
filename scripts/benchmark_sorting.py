#!/usr/bin/env python3
"""benchmark_sorting.py - Real filesystem sorting benchmark for Panoptikon."""

# flake8: noqa: E402
from __future__ import annotations

from pathlib import Path
import sys

# Add project root to sys.path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import argparse
import os

from panoptikon.benchmark.sorting_benchmark import run_sorting_benchmark
from panoptikon.search.result import SearchResultImpl
from panoptikon.search.sorting import (
    AttributeSortCriteria,
    FolderSizeSortCriteria,
    SortingEngine,
)


def collect_file(fpath: str, fname: str) -> SearchResultImpl | None:
    """Collect metadata for a single file."""
    try:
        stat = os.stat(fpath)
        return SearchResultImpl(
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
    except Exception:
        return None


def collect_directory(dpath: str, dname: str) -> SearchResultImpl | None:
    """Collect metadata for a single directory, including folder size."""
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
        return SearchResultImpl(
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
    except Exception:
        return None


def collect_filesystem_data(
    start_path: str, max_files: int = 20000
) -> tuple[list[SearchResultImpl], int]:
    """Collect real file and directory data from the filesystem."""
    files: list[SearchResultImpl] = []
    error_count = 0
    for root, dirs, filenames in os.walk(start_path, topdown=True):
        if len(files) >= max_files:
            break
        for fname in filenames:
            if len(files) >= max_files:
                break
            fpath = os.path.join(root, fname)
            result = collect_file(fpath, fname)
            if result is not None:
                files.append(result)
            else:
                error_count += 1
        for dname in dirs:
            if len(files) >= max_files:
                break
            dpath = os.path.join(root, dname)
            result = collect_directory(dpath, dname)
            if result is not None:
                files.append(result)
            else:
                error_count += 1
    return files, error_count


def main() -> None:
    """Main benchmark execution function."""
    parser = argparse.ArgumentParser(
        description="Panoptikon live sorting system benchmark."
    )
    parser.add_argument(
        "start_path",
        type=str,
        nargs="?",
        default=str(Path.home()),
        help="Directory to scan (default: home directory)",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=20000,
        help="Maximum number of files/directories to collect (default: 20000)",
    )
    args = parser.parse_args()
    start_path = args.start_path
    max_files = args.max_files

    print(f"Collecting files from {start_path}...")
    files, error_count = collect_filesystem_data(start_path, max_files)
    print(f"Collected {len(files)} files (encountered {error_count} permission errors)")
    if len(files) < 10000:
        print(
            f"Warning: Only collected {len(files)} files, which is below the 10,000 target"
        )

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
    print("\nRunning sorting benchmarks...")
    results = run_sorting_benchmark(files, engine, sort_criteria_list, iterations=5)
    print("\nSorting Benchmark Results:")
    print("=========================")
    print(f"File count: {len(files)}")
    for sort_name, stats in results.items():
        print(f"\n{sort_name}:")
        print(f"  Average: {stats['mean']:.2f}ms")
        print(f"  Median:  {stats['median']:.2f}ms")
        print(f"  Min:     {stats['min']:.2f}ms")
        print(f"  Max:     {stats['max']:.2f}ms")
        if stats["mean"] > 100:
            print("  ⚠️ EXCEEDS 100ms TARGET ⚠️")
    failed_sorts = [name for name, stats in results.items() if stats["mean"] > 100]
    if failed_sorts:
        print(
            f"\n⚠️ {len(failed_sorts)} sort types exceed the 100ms target: {', '.join(failed_sorts)}"
        )
    else:
        print("\n✅ All sort types meet the 100ms performance target!")


if __name__ == "__main__":
    main()
