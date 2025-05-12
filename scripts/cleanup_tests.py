#!/usr/bin/env python3
"""Script to clean up redundant test files after consolidation.

This script deletes the test files that were consolidated into
a single file for each functionality area.
"""

from pathlib import Path


def main() -> None:
    """Delete redundant test files after consolidation."""
    # Get project root
    project_root = Path(__file__).parent.parent

    # Files to delete after consolidation
    files_to_delete = [
        # Filesystem watcher tests consolidated into test_filesystem_watcher.py
        "tests/core/test_fs_watcher.py",  # Original test file
        "tests/core/test_fs_watcher_advanced.py",
        "tests/core/test_fs_watcher_edge_cases.py",
        "tests/core/test_fs_watcher_enhanced.py",
        "tests/core/test_fs_watcher_performance.py",
        # Filesystem access tests consolidated into test_filesystem_access.py
        "tests/core/test_filesystem_access_enhanced.py",
    ]

    deleted_count = 0
    for file_path in files_to_delete:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"Deleting: {file_path}")
            full_path.unlink()
            deleted_count += 1
        else:
            print(f"File not found: {file_path}")

    print(f"\nDeleted {deleted_count} redundant test files.")
    print("Consolidation complete!")


if __name__ == "__main__":
    main()
