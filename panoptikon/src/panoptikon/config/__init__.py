"""Configuration management for Panoptikon.

This module is responsible for:
1. Loading configuration from files
2. Validating configuration settings
3. Providing access to configuration values
4. Saving configuration changes

The configuration system supports multiple profiles and environment-specific settings.
"""

from panoptikon.config.config_manager import (
    get_config,
    load_config,
    load_default_config,
    save_config,
)

__all__ = ["get_config", "load_config", "load_default_config", "save_config"]
