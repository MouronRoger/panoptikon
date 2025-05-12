"""Tests for the configuration system."""

import json
import os
from pathlib import Path

import pytest

from src.panoptikon.core.config import (
    ConfigChangedEvent,
    ConfigSource,
    ConfigurationSystem,
)
from src.panoptikon.core.events import EventBus, EventHandler
from tests.conftest import TestConfigSection


def test_initialization(
    config_system: ConfigurationSystem, temp_config_dir: Path
) -> None:
    """Test configuration system initialization."""
    # Initialize the system
    config_system.initialize()

    # Verify the config directory was created
    assert os.path.exists(temp_config_dir)

    # Verify config file was created
    config_file = temp_config_dir / "config.json"
    assert os.path.exists(config_file)

    # Read the content of the file to verify it's a valid JSON
    with open(config_file, encoding="utf-8") as f:
        data = json.load(f)
        assert isinstance(data, dict)


def test_register_section(config_system: ConfigurationSystem) -> None:
    """Test registering a configuration section."""
    # Initialize
    config_system.initialize()

    # Register section with defaults
    defaults = {"string_value": "test", "int_value": 100}
    config_system.register_section("test", TestConfigSection, defaults)

    # Check that values can be retrieved
    assert config_system.get("test", "string_value") == "test"
    assert config_system.get("test", "int_value") == 100

    # Check that default from schema is used if not in defaults dict
    assert config_system.get("test", "list_value") == []

    # Check that unknown value returns default
    assert config_system.get("test", "unknown", "default") == "default"

    # Verify that section retrieval works
    section = config_system.get_section("test")
    assert section["string_value"] == "test"
    assert section["int_value"] == 100

    # Verify that model-based retrieval works
    model = config_system.get_as_model("test")
    assert isinstance(model, TestConfigSection)
    assert model.string_value == "test"
    assert model.int_value == 100

    assert "test" in config_system._schemas


def test_set_config_value(
    config_system: ConfigurationSystem, event_bus: EventBus
) -> None:
    """Test setting configuration values."""
    # Initialize
    config_system.initialize()

    # Register section
    config_system.register_section("test", TestConfigSection)

    # Add event listener
    listener = TestEventHandler()
    event_bus.subscribe(ConfigChangedEvent, listener)

    # Set a value and verify it was set
    config_system.set("test", "string_value", "new value")
    assert config_system.get("test", "string_value") == "new value"

    # Verify event was published
    assert len(listener.events) == 1
    event = listener.events[0]
    assert event.section == "test"
    assert event.key == "string_value"
    assert event.old_value == "default"  # Default from schema
    assert event.new_value == "new value"

    # Setting to the same value should not publish an event
    config_system.set("test", "string_value", "new value")
    assert len(listener.events) == 1

    # Set a value in user config source
    config_system.set("test", "int_value", 200, source=ConfigSource.USER)
    assert config_system.get("test", "int_value") == 200

    # Verify event for that too
    assert len(listener.events) == 2
    event = listener.events[1]
    assert event.section == "test"
    assert event.key == "int_value"
    assert event.old_value == 42  # Default from schema
    assert event.new_value == 200


def test_update_section(config_system: ConfigurationSystem) -> None:
    """Test updating multiple values in a section."""
    # Initialize
    config_system.initialize()

    # Register section
    config_system.register_section("test", TestConfigSection)

    # Update multiple values
    updates = {"string_value": "bulk update", "int_value": 999}
    config_system.update_section("test", updates)

    # Verify updates
    assert config_system.get("test", "string_value") == "bulk update"
    assert config_system.get("test", "int_value") == 999


def test_save_and_reload(
    config_system: ConfigurationSystem, temp_config_dir: Path
) -> None:
    """Test saving and reloading configuration from disk."""
    config_system._config_dir = temp_config_dir
    config_system._config_file = temp_config_dir / "config.json"

    # Register the section before setting a value
    config_system.register_section("test", TestConfigSection)

    # Set a value and save
    config_system.set("test", "string_value", "save test", source=ConfigSource.USER)
    config_system.save()

    # Modify the file directly
    with open(config_system._config_file, "w") as f:
        f.write('{"test": {"string_value": "reloaded"}}')

    # Reload
    config_system.reload()
    assert config_system.get("test", "string_value") == "reloaded"


def test_reset_to_defaults(config_system: ConfigurationSystem) -> None:
    """Test resetting configuration to defaults."""
    # Initialize
    config_system.initialize()

    # Register section with defaults
    defaults = {"string_value": "default value", "int_value": 500}
    config_system.register_section("test", TestConfigSection, defaults)

    # Set some values
    config_system.set("test", "string_value", "user value", source=ConfigSource.USER)
    config_system.set("test", "int_value", 1000, source=ConfigSource.RUNTIME)

    # Reset just this section
    config_system.reset_to_defaults("test")

    # Runtime values should be cleared, user values preserved
    assert config_system.get("test", "string_value") == "user value"
    assert (
        config_system.get("test", "int_value") == 500
    )  # Default value since runtime value was cleared

    # Reset all sections
    config_system.reset_to_defaults()

    # Runtime values should be cleared, user values preserved
    assert config_system.get("test", "string_value") == "user value"
    assert (
        config_system.get("test", "int_value") == 500
    )  # Default value since runtime value was cleared


def test_error_handling(config_system: ConfigurationSystem) -> None:
    """Test error handling in the configuration system."""
    # Initialize
    config_system.initialize()

    # Trying to get from unregistered section should raise KeyError
    with pytest.raises(KeyError):
        config_system.get("nonexistent", "key")

    # Register a section
    config_system.register_section("test", TestConfigSection)

    # Try to set an invalid key
    with pytest.raises(KeyError):
        config_system.set("test", "nonexistent_key", "value")

    # Try to register the same section twice
    with pytest.raises(ValueError):
        config_system.register_section("test", TestConfigSection)


class TestEventHandler(EventHandler[ConfigChangedEvent]):
    """Collects published :class:`ConfigChangedEvent` instances for assertions."""

    events: list[ConfigChangedEvent]

    def setup(self) -> None:  # noqa: D401 – imperative mood not required
        """Initialise the handler with an empty event list."""
        self.events = []

    def handle(self, event: ConfigChangedEvent) -> None:  # noqa: D401 – imperative mood
        """Store the received *event* for later inspection."""
        if not hasattr(self, "events"):
            self.setup()
        self.events.append(event)
