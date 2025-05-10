#!/usr/bin/env python3
"""Script to check docstring coverage."""

import argparse
import ast
import sys
from typing import Dict, List, Optional


class DocstringVisitor(ast.NodeVisitor):
    """AST visitor to check docstring coverage."""

    def __init__(self) -> None:
        """Initialize the visitor."""
        self.stats: Dict[str, List[str]] = {
            "missing_docstrings": [],
            "has_docstrings": [],
        }

    def visit_Module(self, node: ast.Module) -> None:
        """Visit a module node.

        Args:
            node: The module node to visit
        """
        if not ast.get_docstring(node):
            self.stats["missing_docstrings"].append("module")
        else:
            self.stats["has_docstrings"].append("module")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition node.

        Args:
            node: The class definition node to visit
        """
        if not ast.get_docstring(node):
            self.stats["missing_docstrings"].append(f"class {node.name}")
        else:
            self.stats["has_docstrings"].append(f"class {node.name}")
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition node.

        Args:
            node: The function definition node to visit
        """
        if not ast.get_docstring(node):
            self.stats["missing_docstrings"].append(f"function {node.name}")
        else:
            self.stats["has_docstrings"].append(f"function {node.name}")
        self.generic_visit(node)


def check_docstring_coverage(filename: str, min_coverage: float) -> bool:
    """Check docstring coverage for a file.

    Args:
        filename: Path to the file to check
        min_coverage: Minimum required coverage percentage

    Returns:
        bool: True if coverage meets minimum requirement, False otherwise
    """
    with open(filename, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename)

    visitor = DocstringVisitor()
    visitor.visit(tree)

    total = len(visitor.stats["missing_docstrings"]) + len(visitor.stats["has_docstrings"])
    if total == 0:
        return True

    coverage = (len(visitor.stats["has_docstrings"]) / total) * 100

    if coverage < min_coverage:
        print(f"Error: {filename} has {coverage:.1f}% docstring coverage (minimum: {min_coverage}%)")
        print("Missing docstrings:")
        for item in visitor.stats["missing_docstrings"]:
            print(f"  - {item}")
        return False

    return True


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point.

    Args:
        argv: Command line arguments

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Filenames to check")
    parser.add_argument(
        "--min-coverage",
        type=float,
        default=95.0,
        help="Minimum docstring coverage percentage (default: %(default)s)",
    )

    args = parser.parse_args(argv)

    retval = 0

    for filename in args.filenames:
        if not check_docstring_coverage(filename, args.min_coverage):
            retval = 1

    return retval


if __name__ == "__main__":
    sys.exit(main()) 