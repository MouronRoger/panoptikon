"""Database configuration management.

This module provides configuration models and utilities for database settings.
"""

from pathlib import Path

from pydantic import ConfigDict, validator

from ..core.config import ConfigSection


class DatabaseConfig(ConfigSection):
    """Configuration settings for the database.

    Attributes:
        path: Path to the database file.
        timeout: Connection timeout in seconds.
        pragma_synchronous: SQLite synchronous setting (0=OFF, 1=NORMAL, 2=FULL,
            3=EXTRA).
        pragma_journal_mode: SQLite journal mode setting (DELETE, TRUNCATE, PERSIST,
            MEMORY, WAL).
        pragma_temp_store: SQLite temp store setting (0=DEFAULT, 1=FILE, 2=MEMORY).
        pragma_cache_size: SQLite cache size in kilobytes.
        create_if_missing: Whether to create the database if it doesn't exist.
    """

    path: Path
    timeout: float = 5.0
    pragma_synchronous: int = 1  # NORMAL
    pragma_journal_mode: str = "WAL"
    pragma_temp_store: int = 2  # MEMORY
    pragma_cache_size: int = 2000  # 2MB
    create_if_missing: bool = True

    model_config = ConfigDict(
        validate_assignment=True,
        frozen=True,
    )

    @classmethod
    @validator("pragma_synchronous")
    def validate_pragma_synchronous(cls, v: int) -> int:
        """Validate the pragma_synchronous setting.

        Args:
            v: The value to validate.

        Returns:
            The validated value.

        Raises:
            ValueError: If the value is not valid.
        """
        if v not in (0, 1, 2, 3):
            raise ValueError("pragma_synchronous must be 0, 1, 2, or 3")
        return v

    @classmethod
    @validator("pragma_journal_mode")
    def validate_pragma_journal_mode(cls, v: str) -> str:
        """Validate the pragma_journal_mode setting.

        Args:
            v: The value to validate.

        Returns:
            The validated value.

        Raises:
            ValueError: If the value is not valid.
        """
        valid_modes = ("DELETE", "TRUNCATE", "PERSIST", "MEMORY", "WAL")
        if v.upper() not in valid_modes:
            raise ValueError(f"pragma_journal_mode must be one of {valid_modes}")
        return v.upper()

    @classmethod
    @validator("pragma_temp_store")
    def validate_pragma_temp_store(cls, v: int) -> int:
        """Validate the pragma_temp_store setting.

        Args:
            v: The value to validate.

        Returns:
            The validated value.

        Raises:
            ValueError: If the value is not valid.
        """
        if v not in (0, 1, 2):
            raise ValueError("pragma_temp_store must be 0, 1, or 2")
        return v

    @classmethod
    @validator("pragma_cache_size")
    def validate_pragma_cache_size(cls, v: int) -> int:
        """Validate the pragma_cache_size setting.

        Args:
            v: The value to validate.

        Returns:
            The validated value.

        Raises:
            ValueError: If the value is not valid.
        """
        if v < 0:
            raise ValueError("pragma_cache_size must be non-negative")
        return v


def get_default_config() -> dict[str, object]:
    """Get the default database configuration.

    Returns:
        Dictionary with default database configuration values.
    """
    from . import get_default_db_path

    return {
        "path": get_default_db_path(),
        "timeout": 5.0,
        "pragma_synchronous": 1,  # NORMAL
        "pragma_journal_mode": "WAL",
        "pragma_temp_store": 2,  # MEMORY
        "pragma_cache_size": 2000,  # 2MB
        "create_if_missing": True,
    }
