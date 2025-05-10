"""Configuration system for settings management.

This module provides a configuration system that supports a hierarchy of
settings (defaults, user, runtime), schema validation, and hot reloading
of configuration changes.
"""

import json
import logging
import os
import threading
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional

import pydantic  # type: ignore[import-not-found]
from pydantic import BaseModel

from ..core.events import EventBase, EventBus
from ..core.service import ServiceInterface

logger = logging.getLogger(__name__)


@pydantic.dataclasses.dataclass
class ConfigChangedEvent(EventBase):
    """Event issued when configuration values change."""

    section: str = ""
    key: str = ""
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None

    def __post_init__(self) -> None:
        """Validate required fields after initialization.

        Raises:
            ValueError: If section or key is empty.
        """
        if not self.section:
            raise ValueError("section is required")
        if not self.key:
            raise ValueError("key is required")


class ConfigSource(Enum):
    """Defines the source of a configuration value."""

    DEFAULT = auto()  # Default values defined in the schema
    USER = auto()  # Values from the user config file
    RUNTIME = auto()  # Values set during runtime


class ConfigSection(BaseModel):
    """Base class for configuration sections."""

    class Config:
        """Pydantic configuration."""

        extra = "forbid"  # Prevent additional fields not in the schema
        validate_assignment = True  # Validate values on assignment
        validate_all = True  # Validate default values
        arbitrary_types_allowed = True  # Allow more complex types


class ConfigurationError(Exception):
    """Base class for configuration errors."""

    pass


class ConfigValidationError(ConfigurationError):
    """Raised when configuration validation fails."""

    pass


class ConfigFileError(ConfigurationError):
    """Raised when there's an error with the configuration file."""

    pass


class ConfigurationSystem(ServiceInterface):
    """System for managing application configuration.

    Provides a hierarchical configuration system with schema validation
    and hot-reloading support.
    """

    def __init__(
        self,
        event_bus: EventBus,
        config_dir: Optional[Path] = None,
        config_filename: str = "config.json",
        auto_save: bool = True,
        hot_reload: bool = True,
    ) -> None:
        """Initialize the configuration system.

        Args:
            event_bus: Event bus for publishing configuration changes.
            config_dir: Directory for configuration files.
                If None, uses the default platform-specific config directory.
            config_filename: Name of the main configuration file.
            auto_save: Whether to automatically save changes to disk.
            hot_reload: Whether to watch for file changes and reload.
        """
        self._event_bus = event_bus
        self._config_dir = config_dir or self._get_default_config_dir()
        self._config_file = self._config_dir / config_filename
        self._auto_save = auto_save
        self._hot_reload = hot_reload
        self._initialized = False

        # Configuration data stores
        self._default_config: dict[str, dict[str, Any]] = {}
        self._user_config: dict[str, dict[str, Any]] = {}
        self._runtime_config: dict[str, dict[str, Any]] = {}

        # Schema registry
        self._schemas: dict[str, type[ConfigSection]] = {}

        # Change monitoring
        self._file_watcher = None
        self._last_modified_time = 0.0
        self._save_lock = threading.RLock()

        # Create config directory if it doesn't exist
        os.makedirs(self._config_dir, exist_ok=True)

    def initialize(self) -> None:
        """Initialize the configuration system.

        Loads configuration from disk and sets up file watching if enabled.
        """
        if self._initialized:
            return

        # Load configuration from disk
        self._load_user_config()

        # Set up file watching if enabled
        if self._hot_reload:
            self._start_file_watching()

        self._initialized = True
        logger.debug(
            f"Configuration system initialized with config_dir: {self._config_dir}"
        )

    def shutdown(self) -> None:
        """Shut down the configuration system.

        Stops file watching and saves any pending changes.
        """
        if not self._initialized:
            return

        # Stop file watching
        if self._hot_reload and self._file_watcher:
            self._stop_file_watching()

        # Save any pending changes
        if self._auto_save:
            self.save()

        self._initialized = False
        logger.debug("Configuration system shut down")

    def register_section(
        self,
        section_name: str,
        schema: type[ConfigSection],
        defaults: Optional[dict[str, Any]] = None,
    ) -> None:
        """Register a configuration section with its schema.

        Args:
            section_name: Name of the configuration section.
            schema: Pydantic model class defining the schema.
            defaults: Optional default values for this section.

        Raises:
            ValueError: If section already registered.
        """
        if section_name in self._schemas:
            raise ValueError(
                f"Configuration section '{section_name}' already registered"
            )

        self._schemas[section_name] = schema

        # Store default values
        if defaults:
            self._default_config[section_name] = {}
            for key, value in defaults.items():
                if hasattr(schema, key):
                    self._default_config[section_name][key] = value
                else:
                    logger.warning(
                        f"Default value for '{key}' provided but not in schema "
                        f"for section '{section_name}'"
                    )

        # Initialize empty sections
        if section_name not in self._user_config:
            self._user_config[section_name] = {}
        if section_name not in self._runtime_config:
            self._runtime_config[section_name] = {}

        # Validate current values against schema
        self._validate_section(section_name)

        logger.debug(f"Registered configuration section: {section_name}")

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Looks up the value in the following order:
        1. Runtime configuration
        2. User configuration
        3. Default configuration
        4. Provided default value

        Args:
            section: Configuration section name.
            key: Configuration key.
            default: Default value if not found in any configuration source.

        Returns:
            The configuration value.

        Raises:
            KeyError: If section is not registered.
        """
        if section not in self._schemas:
            raise KeyError(f"Configuration section '{section}' not registered")

        # Check each configuration level
        if section in self._runtime_config and key in self._runtime_config[section]:
            return self._runtime_config[section][key]

        if section in self._user_config and key in self._user_config[section]:
            return self._user_config[section][key]

        if section in self._default_config and key in self._default_config[section]:
            return self._default_config[section][key]

        return default

    def get_section(self, section: str) -> dict[str, Any]:
        """Get all configuration values for a section.

        Returns merged values from all configuration sources.

        Args:
            section: Configuration section name.

        Returns:
            Dictionary of all configuration values for the section.

        Raises:
            KeyError: If section is not registered.
        """
        if section not in self._schemas:
            raise KeyError(f"Configuration section '{section}' not registered")

        # Start with defaults
        result = {}
        if section in self._default_config:
            result.update(self._default_config[section])

        # Override with user config
        if section in self._user_config:
            result.update(self._user_config[section])

        # Override with runtime config
        if section in self._runtime_config:
            result.update(self._runtime_config[section])

        return result

    def get_as_model(self, section: str) -> ConfigSection:
        """Get the configuration for a section as a validated model.

        Args:
            section: Configuration section name.

        Returns:
            A validated instance of the section's schema.

        Raises:
            KeyError: If section is not registered.
            ValidationError: If the configuration fails validation.
        """
        if section not in self._schemas:
            raise KeyError(f"Configuration section '{section}' not registered")

        # Get merged configuration
        config_data = self.get_section(section)

        # Create and validate model
        schema = self._schemas[section]
        return schema(**config_data)

    def set(
        self,
        section: str,
        key: str,
        value: Any,
        source: ConfigSource = ConfigSource.RUNTIME,
    ) -> None:
        """Set a configuration value.

        Args:
            section: Configuration section name.
            key: Configuration key.
            value: Value to set.
            source: Which configuration source to update.

        Raises:
            KeyError: If section is not registered.
            ValidationError: If value fails validation.
        """
        if section not in self._schemas:
            raise KeyError(f"Configuration section '{section}' not registered")

        # Check if key is in schema
        schema = self._schemas[section]
        if not hasattr(schema, key) and key not in schema.__annotations__:
            raise KeyError(f"Key '{key}' not in schema for section '{section}'")

        # Store old value for event
        old_value = self.get(section, key)

        # Update the appropriate config source
        if source == ConfigSource.RUNTIME:
            self._runtime_config[section][key] = value
        elif source == ConfigSource.USER:
            self._user_config[section][key] = value
            if self._auto_save:
                self.save()
        elif source == ConfigSource.DEFAULT:
            self._default_config[section][key] = value

        # Validate after update
        self._validate_section(section)

        # Publish event
        if old_value != value:
            event = ConfigChangedEvent(
                section=section,
                key=key,
                old_value=old_value,
                new_value=value
            )
            self._event_bus.publish(event)

        logger.debug(
            f"Set config value: {section}.{key} = {value} (source: {source.name})"
        )

    def update_section(
        self,
        section: str,
        values: dict[str, Any],
        source: ConfigSource = ConfigSource.RUNTIME,
    ) -> None:
        """Update multiple values in a section.

        Args:
            section: Configuration section name.
            values: Dictionary of values to update.
            source: Which configuration source to update.

        Raises:
            KeyError: If section is not registered.
            ValidationError: If any value fails validation.
        """
        if section not in self._schemas:
            raise KeyError(f"Configuration section '{section}' not registered")

        # Update each value individually
        for key, value in values.items():
            self.set(section, key, value, source)

    def save(self) -> None:
        """Save user configuration to disk.

        Raises:
            ConfigFileError: If the configuration cannot be saved.
        """
        with self._save_lock:
            try:
                with open(self._config_file, "w", encoding="utf-8") as f:
                    json.dump(self._user_config, f, indent=2, sort_keys=True)

                self._last_modified_time = float(os.path.getmtime(self._config_file))
                logger.debug(f"Saved configuration to {self._config_file}")
            except OSError as e:
                raise ConfigFileError(f"Failed to save configuration: {e}") from e

    def reload(self) -> bool:
        """Reload configuration from disk.

        Returns:
            True if configuration was changed, False otherwise.

        Raises:
            ConfigFileError: If the configuration cannot be loaded.
        """
        with self._save_lock:
            was_changed = self._load_user_config()
            if was_changed:
                logger.debug("Configuration reloaded from disk")
            return was_changed

    def reset_to_defaults(self, section: Optional[str] = None) -> None:
        """Reset configuration to default values.

        Args:
            section: Optional section to reset. If None, resets all sections.
        """
        with self._save_lock:
            if section:
                if section in self._runtime_config:
                    self._runtime_config[section] = {}
                if section in self._user_config:
                    self._user_config[section] = {}
                    if self._auto_save:
                        self.save()
            else:
                self._runtime_config = {}
                self._user_config = {}
                if self._auto_save:
                    self.save()

                # Re-initialize empty sections
                for section_name in self._schemas:
                    if section_name not in self._runtime_config:
                        self._runtime_config[section_name] = {}
                    if section_name not in self._user_config:
                        self._user_config[section_name] = {}

            logger.debug(
                f"Reset configuration to defaults: "
                f"{'all sections' if section is None else section}"
            )

    def _get_default_config_dir(self) -> Path:
        """Get the default configuration directory for the platform.

        Returns:
            Path to the default config directory.
        """
        if os.name == "nt":  # Windows
            app_data = os.environ.get("APPDATA")
            if app_data:
                return Path(app_data) / "Panoptikon"
            return Path.home() / "AppData" / "Roaming" / "Panoptikon"
        elif os.name == "posix":  # macOS, Linux
            # macOS
            if os.path.exists(str(Path.home() / "Library")):
                return Path.home() / "Library" / "Application Support" / "Panoptikon"
            # Linux
            xdg_config = os.environ.get("XDG_CONFIG_HOME")
            if xdg_config:
                return Path(xdg_config) / "panoptikon"
            return Path.home() / ".config" / "panoptikon"

        # Fallback
        return Path.home() / ".panoptikon"

    def _load_user_config(self) -> bool:
        """Load user configuration from disk.

        Returns:
            True if configuration was changed, False otherwise.

        Raises:
            ConfigFileError: If the configuration cannot be loaded.
        """
        # If file doesn't exist, create it
        if not os.path.exists(self._config_file):
            self.save()
            return False

        try:
            with open(self._config_file, encoding="utf-8") as f:
                new_config = json.load(f)

            # Update modified time
            self._last_modified_time = float(os.path.getmtime(self._config_file))

            # Check if anything changed
            if new_config == self._user_config:
                return False

            # Update configuration
            old_config = self._user_config.copy()
            self._user_config = new_config

            # Validate all sections
            for section in self._schemas:
                self._validate_section(section)

            # Emit events for changed values
            self._emit_config_change_events(old_config, new_config)

            return True
        except json.JSONDecodeError as e:
            raise ConfigFileError(f"Invalid configuration file format: {e}") from e
        except OSError as e:
            raise ConfigFileError(f"Failed to load configuration: {e}") from e

    def _emit_config_change_events(
        self,
        old_config: dict[str, dict[str, Any]],
        new_config: dict[str, dict[str, Any]],
    ) -> None:
        """Emit events for configuration changes.

        Args:
            old_config: Previous configuration.
            new_config: New configuration.
        """
        for section, section_data in new_config.items():
            if section in self._schemas:
                old_section_data = old_config.get(section, {})
                for key, value in section_data.items():
                    if key not in old_section_data or old_section_data[key] != value:
                        old_value = old_section_data.get(key)
                        event = ConfigChangedEvent(
                            section=section,
                            key=key,
                            old_value=old_value,
                            new_value=value
                        )
                        self._event_bus.publish(event)

    def _validate_section(self, section: str) -> None:
        """Validate a configuration section against its schema.

        Args:
            section: Name of the section to validate.

        Raises:
            ValidationError: If validation fails.
        """
        if section not in self._schemas:
            return

        # Get merged configuration
        config_data = self.get_section(section)

        # Validate against schema
        try:
            schema = self._schemas[section]
            schema(**config_data)
        except pydantic.ValidationError as e:
            # Log error but don't raise, to avoid breaking the application
            logger.error(
                f"Configuration validation failed for section '{section}': {e}"
            )
            raise ConfigValidationError(
                f"Validation failed for section '{section}': {e}"
            ) from e

    def _start_file_watching(self) -> None:
        """Start watching the configuration file for changes."""
        # This will be implemented if needed
        # For now, just periodically check the file modification time
        # This could be replaced with watchdog or other file watching solution
        pass

    def _stop_file_watching(self) -> None:
        """Stop watching the configuration file."""
        # This will be implemented if needed
        pass

    def _check_file_modified(self) -> None:
        """Check if the configuration file has been modified and reload if needed."""
        if not os.path.exists(self._config_file):
            return

        try:
            mtime = float(os.path.getmtime(self._config_file))
            if mtime > self._last_modified_time:
                self.reload()
        except OSError:
            # Ignore errors
            pass
