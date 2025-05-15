"""Pytest configuration and fixtures."""

# ---------------------------------------------------------------------------
# Shared configuration section model used across the test-suite
# ---------------------------------------------------------------------------
from __future__ import annotations

from collections.abc import Generator
import os
from pathlib import Path
import tempfile
from typing import Any, Dict, Optional, Set

from pydantic import Field
import pytest

from src.panoptikon.core.config import ConfigDict, ConfigSection, ConfigurationSystem
from src.panoptikon.core.events import EventBus

# The model definition is the superset of required fields so individual test
# modules no longer need to re-declare their own variants.


class TestConfigSection(ConfigSection):
    """Reusable configuration section model for tests."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        validate_default=True,
        arbitrary_types_allowed=True,
    )

    string_value: str = "default"
    int_value: int = 42
    list_value: list[str] = Field(default_factory=list)
    optional_value: Optional[str] = None  # noqa: ANN401
    complex_value: Dict[str, Any] = Field(default_factory=dict)
    set_value: Set[int] = Field(default_factory=set)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


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


@pytest.fixture()
def temp_config_dir() -> Generator[Path, None, None]:
    """Return a temporary directory that is automatically cleaned-up."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture()
def event_bus() -> EventBus:
    """An :class:`EventBus` instance for tests."""
    return EventBus()


@pytest.fixture(name="config_system")
def fixture_config_system(
    temp_config_dir: Path, event_bus: EventBus
) -> ConfigurationSystem:
    """A *non*-hot-reloading :class:`ConfigurationSystem` instance."""
    return ConfigurationSystem(event_bus, config_dir=temp_config_dir, hot_reload=False)


@pytest.fixture(name="config_system_hot")
def fixture_config_system_hot(
    temp_config_dir: Path, event_bus: EventBus
) -> ConfigurationSystem:
    """A *hot-reloading* :class:`ConfigurationSystem` instance."""
    return ConfigurationSystem(event_bus, config_dir=temp_config_dir, hot_reload=True)
