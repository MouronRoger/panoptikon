#!/usr/bin/env python3
"""Documentation linter - checks for empty relationship sections"""

import re
import sys
from pathlib import Path


def check_doc_file(filepath: str) -> bool:
    """Check a documentation file for empty relationship sections."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    rel_section_match = re.search(
        r"## Relationships.*?(?=^##|\Z)", content, re.DOTALL | re.MULTILINE
    )
    if not rel_section_match:
        return True
    rel_section = rel_section_match.group(0)
    rel_lines = re.findall(r"^\s*-\s*\*\*(.*?)\*\*:", rel_section, re.MULTILINE)
    if not rel_lines:
        print(
            f"Error: {filepath} has a Relationships section but no relationship entries"
        )
        print("Add at least one relationship line with format: - **Type**: Entity")
        return False
    return True


def main() -> None:
    """Check all files passed as arguments."""
    if len(sys.argv) < 2:
        print("Usage: python doc_lint.py <file1> [<file2> ...]")
        sys.exit(1)
    all_valid = True
    for filepath in sys.argv[1:]:
        if not Path(filepath).exists():
            print(f"Warning: File not found: {filepath}")
            continue
        if not filepath.endswith(".md"):
            continue
        if not check_doc_file(filepath):
            all_valid = False
    if not all_valid:
        sys.exit(1)


if __name__ == "__main__":
    main()
