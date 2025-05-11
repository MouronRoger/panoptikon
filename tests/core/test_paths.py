"""Tests for the path manager module."""

from pathlib import Path
import tempfile
import unittest

from src.panoptikon.filesystem.paths import (
    PathManager,
    PathMatchType,
    PathRule,
    PathRuleSet,
)


class TestPathManager(unittest.TestCase):
    """Tests for the PathManager class."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name)
        self.path_manager = PathManager()

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_normalize_path(self) -> None:
        """Test path normalization."""
        # Test relative path normalization
        rel_path = "./test/../dir/./file.txt"
        expected = Path("dir/file.txt").absolute()
        result = self.path_manager.normalize_path(rel_path)

        # Use paths_equal for comparing paths
        self.assertTrue(self.path_manager.paths_equal(expected, result))

        # Test absolute path normalization
        abs_path = self.root_path / "test/../dir/./file.txt"
        expected = (self.root_path / "dir/file.txt").absolute()
        result = self.path_manager.normalize_path(abs_path)

        # Use paths_equal for comparing paths
        self.assertTrue(self.path_manager.paths_equal(expected, result))

        # Test home directory expansion
        home_path = "~/Documents/file.txt"
        expected = Path.home() / "Documents/file.txt"
        result = self.path_manager.normalize_path(home_path)

        # Use paths_equal for comparing paths
        self.assertTrue(self.path_manager.paths_equal(expected, result))

    def test_is_subpath(self) -> None:
        """Test subpath detection."""
        parent = self.root_path
        child = parent / "subdir/file.txt"

        # Child should be a subpath of parent
        self.assertTrue(self.path_manager.is_subpath(parent, child))

        # Parent should not be a subpath of child
        self.assertFalse(self.path_manager.is_subpath(child, parent))

        # A path is considered a subpath of itself (Path.is_relative_to() behavior)
        self.assertTrue(self.path_manager.is_subpath(parent, parent))

        # Unrelated paths should not be subpaths
        other_path = Path("/tmp/other")
        self.assertFalse(self.path_manager.is_subpath(other_path, child))

    def test_paths_equal(self) -> None:
        """Test path equality checking."""
        # Create test paths
        path1 = self.root_path / "dir/file.txt"
        path2 = self.root_path / "dir/./file.txt"
        path3 = self.root_path / "other/file.txt"

        # Same paths with different representations should be equal
        self.assertTrue(self.path_manager.paths_equal(path1, path2))

        # Different paths should not be equal
        self.assertFalse(self.path_manager.paths_equal(path1, path3))

    def test_path_rule_matching(self) -> None:
        """Test path rule matching."""
        # Create test paths
        python_file = self.root_path / "code/script.py"
        txt_file = self.root_path / "docs/readme.txt"
        temp_file = self.root_path / "temp/~temp123.tmp"
        hidden_file = self.root_path / ".hidden/config"

        # Create and test various rules
        py_rule = PathRule("*.py")
        txt_rule = PathRule("*.txt")
        temp_rule = PathRule("*~temp*")
        hidden_rule = PathRule("*/.hidden/*")

        # Test rule matching
        self.assertTrue(py_rule.matches(python_file))
        self.assertTrue(txt_rule.matches(txt_file))
        self.assertTrue(temp_rule.matches(temp_file))
        self.assertTrue(hidden_rule.matches(hidden_file))

        # Test non-matching
        self.assertFalse(py_rule.matches(txt_file))
        self.assertFalse(txt_rule.matches(python_file))

    def test_path_rule_set(self) -> None:
        """Test path rule set functionality."""
        # Create test paths
        python_file = self.root_path / "code/script.py"
        txt_file = self.root_path / "docs/readme.txt"
        temp_file = self.root_path / "temp/~temp123.tmp"
        hidden_file = self.root_path / ".hidden/config"

        # Create rule set
        rule_set = PathRuleSet()

        # Add rules
        rule_set.add_include("*.py")
        rule_set.add_include("*.txt")
        rule_set.add_exclude("*~temp*")
        rule_set.add_exclude("*/.hidden/*")

        # Test inclusion/exclusion
        self.assertTrue(rule_set.should_include(python_file))
        self.assertTrue(rule_set.should_include(txt_file))
        self.assertFalse(rule_set.should_include(temp_file))
        self.assertFalse(rule_set.should_include(hidden_file))

        # Test rule set filtering
        paths: list[Union[str, Path]] = [python_file, txt_file, temp_file, hidden_file]
        filtered_paths = rule_set.filter_paths(paths)
        self.assertEqual(2, len(filtered_paths))
        self.assertIn(python_file, filtered_paths)
        self.assertIn(txt_file, filtered_paths)

        # Test empty rule set (should include everything)
        empty_set = PathRuleSet()
        self.assertTrue(empty_set.should_include(python_file))
        self.assertTrue(empty_set.should_include(hidden_file))

        # Test exclude-only rule set
        exclude_set = PathRuleSet()
        exclude_set.add_exclude("*.tmp")
        self.assertTrue(exclude_set.should_include(python_file))
        self.assertFalse(exclude_set.should_include(temp_file))

    def test_rule_match_types(self) -> None:
        """Test different rule match types."""
        # Create test paths
        test_path = self.root_path / "dir/file123.txt"

        # Test glob pattern
        glob_rule = PathRule("*123.txt")
        self.assertTrue(glob_rule.matches(test_path))

        # Test regex pattern
        regex_rule = PathRule(r"file\d+\.txt", match_type=PathMatchType.REGEX)
        self.assertTrue(regex_rule.matches(test_path))

        # Test exact pattern
        exact_rule = PathRule(str(test_path), match_type=PathMatchType.EXACT)
        self.assertTrue(exact_rule.matches(test_path))

        # Test case sensitivity
        case_rule = PathRule("FILE123.txt", case_sensitive=True)
        self.assertFalse(case_rule.matches(test_path))

        # Test case insensitivity - just test the filename part
        filename = "file123.txt"
        nocase_rule = PathRule("FILE123.txt", case_sensitive=False)
        self.assertTrue(nocase_rule.matches(filename))

    def test_rule_set_management(self) -> None:
        """Test path manager rule set management."""
        # Create rule sets
        rule_set1 = self.path_manager.create_rule_set("set1")
        rule_set2 = self.path_manager.create_rule_set("set2")

        # Add rules to sets
        rule_set1.add_include("*.py")
        rule_set2.add_include("*.txt")

        # Get rule sets
        retrieved_set1 = self.path_manager.get_rule_set("set1")
        self.assertEqual(rule_set1, retrieved_set1)

        # Delete rule set
        self.assertTrue(self.path_manager.delete_rule_set("set1"))
        self.assertIsNone(self.path_manager.get_rule_set("set1"))

        # Deleting non-existent set should fail
        self.assertFalse(self.path_manager.delete_rule_set("non_existent"))
