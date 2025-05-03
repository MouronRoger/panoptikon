#!/usr/bin/env python
"""Check file length script for pre-commit hook.

This script checks if Python files exceed the maximum allowed length.
"""

import argparse
import sys
from typing import Tuple


def check_file_length(file_path: str, max_lines: int) -> Tuple[bool, int]:
    """Check if a file exceeds the maximum number of lines.

    Args:
        file_path: Path to the file to check
        max_lines: Maximum number of lines allowed

    Returns:
        Tuple of (is_valid, actual_line_count)
    """
    with open(file_path, "r", encoding="utf-8") as file:
        line_count = sum(1 for _ in file)
    
    return line_count <= max_lines, line_count


def main() -> int:
    """Run the file length checker.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(description="Check file length")
    parser.add_argument("--max-lines", type=int, default=500,
                        help="Maximum number of lines per file")
    parser.add_argument("files", nargs="*", help="Files to check")
    
    args = parser.parse_args()
    
    violations = []
    
    for file_path in args.files:
        is_valid, line_count = check_file_length(file_path, args.max_lines)
        if not is_valid:
            violations.append((file_path, line_count))
    
    if violations:
        for file_path, line_count in violations:
            print(f"{file_path}: {line_count} lines (exceeds {args.max_lines})")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 