"""Configuration manager for Panoptikon.

This module handles loading, validating, and providing access to application configuration.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import pydantic
from pydantic import BaseModel, Field, validator

# Global configuration variable
_config: Dict[str, Any] = {}


class IndexConfig(BaseModel):
    """Index configuration settings.

    Attributes:
        default_paths: List of default paths to index.
        excluded_paths: List of paths to exclude from indexing.
        excluded_extensions: List of file extensions to exclude from indexing.
        max_file_size_mb: Maximum file size to index in megabytes.
        watch_for_changes: Whether to watch for file system changes.
    """

    default_paths: list[str] = Field(default_factory=list)
    excluded_paths: list[str] = Field(default_factory=list)
    excluded_extensions: list[str] = Field(default_factory=list)
    max_file_size_mb: int = 100
    watch_for_changes: bool = True


class SearchConfig(BaseModel):
    """Search configuration settings.

    Attributes:
        max_results: Maximum number of results to return.
        case_sensitive: Whether searches are case-sensitive by default.
        fuzzy_matching: Whether to use fuzzy matching for searches.
    """

    max_results: int = 1000
    case_sensitive: bool = False
    fuzzy_matching: bool = True


class UIConfig(BaseModel):
    """UI configuration settings.

    Attributes:
        theme: UI theme.
        font_size: Font size for UI elements.
        max_recent_searches: Maximum number of recent searches to store.
    """

    theme: str = "light"
    font_size: int = 12
    max_recent_searches: int = 10


class AppConfig(BaseModel):
    """Application configuration model.

    Attributes:
        index: Indexing configuration.
        search: Search configuration.
        ui: UI configuration.
    """

    index: IndexConfig = Field(default_factory=IndexConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    ui: UIConfig = Field(default_factory=UIConfig)


def get_config() -> Dict[str, Any]:
    """Get the current configuration.

    Returns:
        The current application configuration.
    """
    return _config


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from a file.

    Args:
        config_path: Path to the configuration file.

    Returns:
        The loaded configuration.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        json.JSONDecodeError: If the configuration file is not valid JSON.
        pydantic.ValidationError: If the configuration does not match the expected schema.
    """
    global _config
    
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(path, "r") as f:
        config_data = json.load(f)
    
    # Validate the configuration
    validated_config = AppConfig(**config_data).dict()
    _config = validated_config
    return _config


def load_default_config() -> Dict[str, Any]:
    """Load the default configuration.

    If a configuration file exists at the default location, it will be loaded.
    Otherwise, a default configuration will be created.

    Returns:
        The default configuration.
    """
    global _config
    
    # Get the default configuration path
    config_dir = _get_config_dir()
    config_path = config_dir / "config.json"
    
    if config_path.exists():
        try:
            return load_config(str(config_path))
        except (json.JSONDecodeError, pydantic.ValidationError):
            # If the configuration is invalid, fall back to the default
            pass
    
    # Create a default configuration
    _config = AppConfig().dict()
    
    # Set default paths based on the platform
    if os.name == "posix":  # macOS, Linux
        home = Path.home()
        _config["index"]["default_paths"] = [str(home)]
    elif os.name == "nt":  # Windows
        home = Path.home()
        _config["index"]["default_paths"] = [str(home)]
    
    # Save the default configuration
    save_config(str(config_path))
    
    return _config


def save_config(config_path: Optional[str] = None) -> None:
    """Save the current configuration to a file.

    Args:
        config_path: Path to save the configuration to. If not provided,
            the default path will be used.
    """
    if config_path is None:
        config_dir = _get_config_dir()
        config_path = str(config_dir / "config.json")
    
    # Ensure the directory exists
    config_dir = Path(config_path).parent
    os.makedirs(config_dir, exist_ok=True)
    
    # Save the configuration
    with open(config_path, "w") as f:
        json.dump(_config, f, indent=2)


def _get_config_dir() -> Path:
    """Get the configuration directory based on the platform.

    Returns:
        Path to the configuration directory.
    """
    if os.name == "posix":  # macOS, Linux
        config_dir = Path.home() / ".config" / "panoptikon"
    elif os.name == "nt":  # Windows
        config_dir = Path(os.environ.get("APPDATA", "")) / "Panoptikon"
    else:
        config_dir = Path.home() / ".panoptikon"
    
    os.makedirs(config_dir, exist_ok=True)
    return config_dir 