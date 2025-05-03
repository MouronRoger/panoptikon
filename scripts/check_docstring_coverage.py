#!/usr/bin/env python
"""Check docstring coverage script for pre-commit hook.

This script verifies that Python files have the required docstring coverage.
"""

import argparse
import ast
import sys
from typing import Dict, Tuple


class DocstringVisitor(ast.NodeVisitor):
    """AST visitor that checks for docstrings in functions and classes."""

    def __init__(self) -> None:
        """Initialize the visitor."""
        self.stats = {
            "functions": {"total": 0, "with_docstring": 0},
            "classes": {"total": 0, "with_docstring": 0},
            "methods": {"total": 0, "with_docstring": 0},
            "modules": {"total": 0, "with_docstring": 0},
        }
        self.current_class = None

    def visit_Module(self, node: ast.Module) -> None:
        """Visit a module node.

        Args:
            node: The module node to visit
        """
        self.stats["modules"]["total"] += 1
        if ast.get_docstring(node):
            self.stats["modules"]["with_docstring"] += 1
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition node.

        Args:
            node: The class definition node to visit
        """
        self.stats["classes"]["total"] += 1
        if ast.get_docstring(node):
            self.stats["classes"]["with_docstring"] += 1
        
        old_class = self.current_class
        self.current_class = node
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition node.

        Args:
            node: The function definition node to visit
        """
        if self.current_class:
            self.stats["methods"]["total"] += 1
            if ast.get_docstring(node):
                self.stats["methods"]["with_docstring"] += 1
        else:
            self.stats["functions"]["total"] += 1
            if ast.get_docstring(node):
                self.stats["functions"]["with_docstring"] += 1
        
        self.generic_visit(node)


def calculate_coverage(stats: Dict) -> float:
    """Calculate the overall docstring coverage.

    Args:
        stats: Statistics dictionary from DocstringVisitor

    Returns:
        Coverage percentage (0-100)
    """
    total = 0
    with_docstring = 0
    
    for category in stats.values():
        total += category["total"]
        with_docstring += category["with_docstring"]
    
    if total == 0:
        return 100.0
    
    return (with_docstring / total) * 100


def check_file_docstrings(file_path: str) -> Tuple[float, Dict]:
    """Check docstring coverage for a file.

    Args:
        file_path: Path to the file to check

    Returns:
        Tuple of (coverage_percentage, statistics)
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    tree = ast.parse(content)
    visitor = DocstringVisitor()
    visitor.visit(tree)
    
    coverage = calculate_coverage(visitor.stats)
    
    return coverage, visitor.stats


def main() -> int:
    """Run the docstring coverage checker.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(description="Check docstring coverage")
    parser.add_argument(
        "--min-coverage",
        type=float,
        default=95.0,
        help="Minimum docstring coverage percentage"
    )
    parser.add_argument("files", nargs="*", help="Files to check")
    
    args = parser.parse_args()
    
    violations = []
    
    for file_path in args.files:
        coverage, stats = check_file_docstrings(file_path)
        if coverage < args.min_coverage:
            violations.append((file_path, coverage, stats))
    
    if violations:
        for file_path, coverage, stats in violations:
            print(f"{file_path}: {coverage:.1f}% coverage (below {args.min_coverage}%)")
            for category, counts in stats.items():
                if counts["total"] > 0:
                    cat_coverage = (counts["with_docstring"] / counts["total"]) * 100
                    print(f"  {category}: {counts['with_docstring']}/{counts['total']} "
                          f"({cat_coverage:.1f}%)")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 