"""Path management utilities.

This module provides utilities for path normalization, comparison,
and rule-based path filtering.
"""

from enum import Enum
import fnmatch
from functools import lru_cache
import os
from pathlib import Path
import re
from re import Pattern
from typing import Dict, List, Optional, Union

from ..core.service import ServiceInterface


class PathMatchType(Enum):
    """Types of path matching patterns."""

    GLOB = "glob"  # Standard glob pattern (*, **, ?)
    REGEX = "regex"  # Regular expression
    EXACT = "exact"  # Exact string match


class PathRule:
    """Rule for including or excluding paths."""

    def __init__(
        self,
        pattern: str,
        match_type: PathMatchType = PathMatchType.GLOB,
        case_sensitive: bool = False,
    ) -> None:
        """Initialize a path rule.

        Args:
            pattern: Pattern to match against paths.
            match_type: Type of pattern matching to use.
            case_sensitive: Whether to do case-sensitive matching.
        """
        self.pattern = pattern
        self.match_type = match_type
        self.case_sensitive = case_sensitive

        # Pre-compile regex patterns
        if match_type == PathMatchType.REGEX:
            flags = 0 if case_sensitive else re.IGNORECASE
            self._regex: Optional[Pattern[str]] = re.compile(pattern, flags)
        else:
            self._regex = None

    def matches(self, path: Union[str, Path]) -> bool:
        """Check if this rule matches the given path.

        Args:
            path: Path to check against this rule.

        Returns:
            True if the path matches this rule, False otherwise.
        """
        path_str = str(path)

        if not self.case_sensitive:
            path_str = path_str.lower()
            pattern = self.pattern.lower()
        else:
            pattern = self.pattern

        if self.match_type == PathMatchType.EXACT:
            return path_str == pattern
        elif self.match_type == PathMatchType.GLOB:
            return fnmatch.fnmatch(path_str, pattern)
        elif self.match_type == PathMatchType.REGEX:
            if self._regex:
                return bool(self._regex.search(path_str))
            return False

        return False

    def __repr__(self) -> str:
        """Get string representation of the rule.

        Returns:
            String representation.
        """
        return (
            f"PathRule(pattern='{self.pattern}', "
            f"match_type={self.match_type}, "
            f"case_sensitive={self.case_sensitive})"
        )


class PathRuleSet:
    """Set of include and exclude rules for path filtering."""

    def __init__(self) -> None:
        """Initialize an empty rule set."""
        self.include_rules: List[PathRule] = []
        self.exclude_rules: List[PathRule] = []

    def add_include(
        self, pattern: str, match_type: PathMatchType = PathMatchType.GLOB
    ) -> None:
        """Add an include rule.

        Args:
            pattern: Pattern to match for inclusion.
            match_type: Type of pattern matching to use.
        """
        self.include_rules.append(PathRule(pattern, match_type))

    def add_exclude(
        self, pattern: str, match_type: PathMatchType = PathMatchType.GLOB
    ) -> None:
        """Add an exclude rule.

        Args:
            pattern: Pattern to match for exclusion.
            match_type: Type of pattern matching to use.
        """
        self.exclude_rules.append(PathRule(pattern, match_type))

    def should_include(self, path: Union[str, Path]) -> bool:
        """Check if a path should be included based on the rules.

        Args:
            path: Path to check.

        Returns:
            True if the path should be included, False otherwise.
        """
        # Convert path to string to ensure consistent handling
        path_str = str(path)

        # Check exclude rules first (exclusion takes precedence)
        for rule in self.exclude_rules:
            if rule.matches(path_str):
                return False

        # If no include rules, include everything not excluded
        if not self.include_rules:
            return True

        # Check include rules
        for rule in self.include_rules:
            if rule.matches(path_str):
                return True

        # If there are include rules but none matched, exclude the path
        return False

    def filter_paths(self, paths: List[Union[str, Path]]) -> List[Union[str, Path]]:
        """Filter a list of paths according to the rules.

        Args:
            paths: List of paths to filter.

        Returns:
            Filtered list of paths that should be included.
        """
        return [p for p in paths if self.should_include(p)]


class PathManager(ServiceInterface):
    """Service for path management operations."""

    def __init__(self) -> None:
        """Initialize the path manager."""
        self._path_rule_sets: Dict[str, PathRuleSet] = {}

    def initialize(self) -> None:
        """Initialize the service."""
        pass

    def shutdown(self) -> None:
        """Shut down the service."""
        self._path_rule_sets.clear()

    def create_rule_set(self, name: str) -> PathRuleSet:
        """Create a new rule set.

        Args:
            name: Name of the rule set.

        Returns:
            The newly created rule set.
        """
        rule_set = PathRuleSet()
        self._path_rule_sets[name] = rule_set
        return rule_set

    def get_rule_set(self, name: str) -> Optional[PathRuleSet]:
        """Get a rule set by name.

        Args:
            name: Name of the rule set.

        Returns:
            The rule set if found, None otherwise.
        """
        return self._path_rule_sets.get(name)

    def delete_rule_set(self, name: str) -> bool:
        """Delete a rule set.

        Args:
            name: Name of the rule set.

        Returns:
            True if deleted, False if not found.
        """
        if name in self._path_rule_sets:
            del self._path_rule_sets[name]
            return True
        return False

    @staticmethod
    @lru_cache(maxsize=1024)
    def normalize_path(path: Union[str, Path]) -> Path:
        """Normalize a path to canonical form.

        Args:
            path: Path to normalize.

        Returns:
            Normalized path.
        """
        # Convert to Path if needed
        if isinstance(path, str):
            path = Path(path)

        # Resolve symlinks, make absolute, normalize case on case-insensitive filesystems
        path = path.expanduser().resolve()

        # On macOS and Windows, store lowercase path for consistent lookups
        if os.name == "nt" or os.name == "posix" and os.uname().sysname == "Darwin":
            path = Path(str(path).lower())

        return path

    @staticmethod
    def paths_equal(path1: Union[str, Path], path2: Union[str, Path]) -> bool:
        """Check if two paths are equivalent.

        Args:
            path1: First path.
            path2: Second path.

        Returns:
            True if the paths are equivalent, False otherwise.
        """
        norm1 = PathManager.normalize_path(path1)
        norm2 = PathManager.normalize_path(path2)
        return norm1 == norm2

    @staticmethod
    def is_subpath(parent: Union[str, Path], child: Union[str, Path]) -> bool:
        """Check if child path is a subpath of parent path.

        Args:
            parent: Potential parent path.
            child: Potential child path.

        Returns:
            True if child is a subpath of parent, False otherwise.
        """
        parent_path = PathManager.normalize_path(parent)
        child_path = PathManager.normalize_path(child)

        try:
            # Check if child is a subpath of parent
            child_path.relative_to(parent_path)
            return True
        except ValueError:
            return False

    @staticmethod
    def common_prefix(paths: List[Union[str, Path]]) -> Optional[Path]:
        """Find the longest common path prefix.

        Args:
            paths: List of paths to find common prefix for.

        Returns:
            Common path prefix or None if no common prefix exists.
        """
        if not paths:
            return None

        # Normalize all paths
        norm_paths = [PathManager.normalize_path(p) for p in paths]

        # Get the shortest path
        shortest = min(norm_paths, key=lambda p: len(str(p)))

        # Try increasingly shorter prefixes
        for i in range(len(str(shortest)), 0, -1):
            prefix = Path(str(shortest)[:i])
            if prefix.is_dir() and all(
                str(p).startswith(str(prefix)) for p in norm_paths
            ):
                return prefix

        return None
