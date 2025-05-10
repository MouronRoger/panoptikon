#!/usr/bin/env python3
"""Script to check file length limits."""

import argparse
import sys
from typing import Optional, Sequence


def check_file_length(filename: str, max_lines: int) -> bool:
    """Check if a file exceeds the maximum number of lines.

    Args:
        filename: Path to the file to check
        max_lines: Maximum number of lines allowed

    Returns:
        bool: True if file is within limits, False otherwise
    """
    with open(filename, "r", encoding="utf-8") as f:
        for i, _ in enumerate(f, 1):
            if i > max_lines:
                print(f"Error: {filename} has more than {max_lines} lines")
                return False
    return True


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main entry point.

    Args:
        argv: Command line arguments

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Filenames to check")
    parser.add_argument(
        "--max-lines",
        type=int,
        default=500,
        help="Maximum number of lines allowed (default: %(default)s)",
    )

    args = parser.parse_args(argv)

    retval = 0

    for filename in args.filenames:
        if not check_file_length(filename, args.max_lines):
            retval = 1

    return retval


if __name__ == "__main__":
    sys.exit(main())
