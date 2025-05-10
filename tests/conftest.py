"""Pytest configuration and fixtures."""

from collections.abc import Generator
import os

import pytest


@pytest.fixture(scope="session")
def _setup_test_env() -> Generator[None, None, None]:
    """Set up the test environment.

    Yields:
        None
    """
    # Save original working directory
    original_cwd = os.getcwd()

    # Change to the project root directory
    os.chdir(os.path.dirname(os.path.dirname(__file__)))

    yield

    # Restore original working directory
    os.chdir(original_cwd)
