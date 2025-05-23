"""Tests for the configuration system."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, cast

import pytest
from pydantic import BaseModel, Field

from src.panoptikon.core.config import (
    ConfigChangedEvent,
    ConfigFileError,
    ConfigSection,
    ConfigSource,
    ConfigurationSystem,
)
from src.panoptikon.core.events import EventBus, EventListener


class TestConfigSection(ConfigSection):
    """Test configuration section."""

    string_value: str = "default"
    int_value: int = 42
    list_value: List[str] = Field(default_factory=list)


class TestEventListener(EventListener):
    """Test event listener for config events."""

    def __init__(self) -> None:
        """Initialize with empty event list."""
        self.events: List[ConfigChangedEvent] = []

    def handle_event(self, event: ConfigChangedEvent) -> None:
        """Store events in a list."""
        self.events.append(cast(ConfigChangedEvent, event))


@pytest.fixture
def temp_config_dir() -> Path:
    """Create a temporary directory for configuration files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def event_bus() -> EventBus:
    """Create an event bus for testing."""
    return EventBus()


@pytest.fixture
def config_system(temp_config_dir: Path, event_bus: EventBus) -> ConfigurationSystem:
    """Create a configuration system for testing."""
    return ConfigurationSystem(
        event_bus, config_dir=temp_config_dir, hot_reload=False
    )


def test_initialization(config_system: ConfigurationSystem, temp_config_dir: Path) -> None:
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


def test_set_config_value(config_system: ConfigurationSystem, event_bus: EventBus) -> None:
    """Test setting configuration values."""
    # Initialize
    config_system.initialize()
    
    # Register section
    config_system.register_section("test", TestConfigSection)
    
    # Add event listener
    listener = TestEventListener()
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


def test_save_and_reload(config_system: ConfigurationSystem, temp_config_dir: Path) -> None:
    """Test saving and reloading configuration."""
    # Initialize
    config_system.initialize()
    
    # Register section
    config_system.register_section("test", TestConfigSection)
    
    # Set a user-level value
    config_system.set("test", "string_value", "to be saved", source=ConfigSource.USER)
    
    # Save explicitly
    config_system.save()
    
    # Verify the file was saved with the expected content
    config_file = temp_config_dir / "config.json"
    with open(config_file, encoding="utf-8") as f:
        data = json.load(f)
        assert "test" in data
        assert data["test"]["string_value"] == "to be saved"
    
    # Modify the running configuration
    config_system.set("test", "string_value", "runtime only", source=ConfigSource.RUNTIME)
    assert config_system.get("test", "string_value") == "runtime only"
    
    # Reload from disk
    config_system.reload()
    
    # Runtime values should be preserved
    assert config_system.get("test", "string_value") == "runtime only"
    
    # Now reset runtime configuration and reload should show the saved value
    config_system.reset_to_defaults("test")
    assert config_system.get("test", "string_value") == "to be saved"


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
    
    # Values should be back to defaults
    assert config_system.get("test", "string_value") == "default value"
    assert config_system.get("test", "int_value") == 500
    
    # Register another section
    config_system.register_section("other", TestConfigSection)
    config_system.set("other", "string_value", "other value")
    
    # Reset all sections
    config_system.reset_to_defaults()
    
    # All values should be defaults now
    assert config_system.get("test", "string_value") == "default value"
    assert config_system.get("other", "string_value") == "default"


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