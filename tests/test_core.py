"""Core functionality tests for Panoptikon."""

import pytest

from panoptikon import __version__


def test_version() -> None:
    """Test that version is a string."""
    assert isinstance(__version__, str)
    assert __version__ == "0.1.0"


@pytest.mark.unit
def test_placeholder() -> None:
    """Placeholder test.

    This test will be replaced with actual tests as functionality is implemented.
    """
    assert True
