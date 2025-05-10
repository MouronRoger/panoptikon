"""Pytest configuration and fixtures."""

from typing import Generator

import pytest


@pytest.fixture(autouse=True)
def _setup_test_env() -> Generator[None, None, None]:
    """Set up test environment before each test."""
    # Add any setup code here
    yield
    # Add any teardown code here 