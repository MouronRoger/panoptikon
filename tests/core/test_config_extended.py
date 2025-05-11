"""Extended tests for the configuration system.

These tests focus on features that aren't well covered in the existing test suite.
"""

from collections.abc import Generator
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from src.panoptikon.core.config import (
    ConfigDict,
    ConfigFileError,
    ConfigSection,
    ConfigSource,
    ConfigurationSystem,
    ConfigValidationError,
)
from src.panoptikon.core.events import EventBus


class TestConfigSection(ConfigSection):
    """Test configuration section for testing."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        validate_default=True,
        arbitrary_types_allowed=True,
    )

    test_string: str = "default"
    test_int: int = 42
    test_bool: bool = True


@pytest.fixture
def temp_config_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for configuration files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_event_bus() -> MagicMock:
    """Create a mock event bus."""
    mock = MagicMock(spec=EventBus)
    return mock


@pytest.fixture
def config_system(
    temp_config_dir: Path, mock_event_bus: MagicMock
) -> ConfigurationSystem:
    """Create a configuration system with a temporary directory."""
    return ConfigurationSystem(
        event_bus=mock_event_bus,
        config_dir=temp_config_dir,
        config_filename="test_config.json",
    )


def test_get_default_config_dir() -> None:
    """Test the default configuration directory detection."""
    mock_event_bus = MagicMock(spec=EventBus)
    config_system = ConfigurationSystem(mock_event_bus)
    config_dir = config_system._get_default_config_dir()
    
    # Check that we got a path
    assert isinstance(config_dir, Path)
    
    # Depending on the platform, check for expected parts
    if os.name == "nt":  # Windows
        assert "AppData" in str(config_dir) or "APPDATA" in str(config_dir)
    elif os.name == "posix":  # macOS, Linux
        if os.path.exists(str(Path.home() / "Library")):
            assert "Library" in str(config_dir)
        else:
            assert ".config" in str(config_dir) or "XDG_CONFIG_HOME" in str(config_dir)


def test_hot_reload_disabled(
    temp_config_dir: Path, mock_event_bus: MagicMock
) -> None:
    """Test configuration system with hot reload disabled."""
    config_system = ConfigurationSystem(
        event_bus=mock_event_bus,
        config_dir=temp_config_dir,
        config_filename="test_config.json",
        hot_reload=False,
    )
    
    with patch.object(config_system, "_start_file_watching") as mock_start_watching:
        config_system.initialize()
        mock_start_watching.assert_not_called()


def test_auto_save_disabled(
    temp_config_dir: Path, mock_event_bus: MagicMock
) -> None:
    """Test configuration system with auto save disabled."""
    config_system = ConfigurationSystem(
        event_bus=mock_event_bus,
        config_dir=temp_config_dir,
        config_filename="test_config.json",
        auto_save=False,
    )
    
    config_system.initialize()
    config_system.register_section("test", TestConfigSection)
    
    # Setting a value should not trigger a save
    with patch.object(config_system, "save") as mock_save:
        config_system.set("test", "test_string", "new value", ConfigSource.USER)
        mock_save.assert_not_called()


def test_validation_error(
    config_system: ConfigurationSystem,
) -> None:
    """Test validation error handling."""
    config_system.initialize()
    config_system.register_section("test", TestConfigSection)
    
    # Try to set an invalid value (string where int is expected)
    with pytest.raises(ConfigValidationError):
        config_system.set("test", "test_int", "not an integer", ConfigSource.USER)


def test_default_user_runtime_precedence(
    config_system: ConfigurationSystem,
) -> None:
    """Test that runtime values take precedence over user values over defaults."""
    config_system.initialize()
    config_system.register_section("test", TestConfigSection)
    
    # Set values at different levels
    config_system.set("test", "test_string", "default value", ConfigSource.DEFAULT)
    config_system.set("test", "test_string", "user value", ConfigSource.USER)
    config_system.set("test", "test_string", "runtime value", ConfigSource.RUNTIME)
    
    # Runtime should win
    assert config_system.get("test", "test_string") == "runtime value"
    
    # Remove runtime value, user should win
    config_system.reset_to_defaults("test")
    assert config_system.get("test", "test_string") == "user value"
    
    # Create a new system to test defaults
    new_config = ConfigurationSystem(
        event_bus=MagicMock(spec=EventBus),
        config_dir=config_system._config_dir,
        # Use different file to avoid loading user config
        config_filename="different_file.json", 
    )
    new_config.initialize()
    new_config.register_section("test", TestConfigSection)
    assert new_config.get("test", "test_string") == "default"


def test_update_section(
    config_system: ConfigurationSystem,
) -> None:
    """Test updating multiple values in a section at once."""
    config_system.initialize()
    config_system.register_section("test", TestConfigSection)
    
    # Update multiple values
    updates = {
        "test_string": "updated string",
        "test_int": 100,
        "test_bool": False,
    }
    config_system.update_section("test", updates, ConfigSource.USER)
    
    # Verify all values were updated
    assert config_system.get("test", "test_string") == "updated string"
    assert config_system.get("test", "test_int") == 100
    assert config_system.get("test", "test_bool") is False


def test_config_file_handling(
    config_system: ConfigurationSystem, temp_config_dir: Path
) -> None:
    """Test configuration file handling including error cases."""
    config_system.initialize()
    config_system.register_section("test", TestConfigSection)
    
    # Set a value and save
    config_system.set("test", "test_string", "saved value", ConfigSource.USER)
    config_system.save()
    
    # Check that the file exists and has the correct content
    config_file = temp_config_dir / "test_config.json"
    assert config_file.exists()
    
    with open(config_file) as f:
        data = json.load(f)
    assert "test" in data
    assert "test_string" in data["test"]
    assert data["test"]["test_string"] == "saved value"
    
    # Test loading from file
    with open(config_file, "w") as f:
        json.dump({"test": {"test_string": "file value"}}, f)
    
    # Reload and check value
    config_system.reload()
    assert config_system.get("test", "test_string") == "file value"
    
    # Test invalid JSON
    with open(config_file, "w") as f:
        f.write("invalid json")
    
    # Should raise ConfigFileError on reload
    with pytest.raises(ConfigFileError):
        config_system.reload()


def test_reset_to_defaults(
    config_system: ConfigurationSystem,
) -> None:
    """Test resetting configuration to defaults."""
    config_system.initialize()
    config_system.register_section("test", TestConfigSection)
    
    # Set runtime and user values
    config_system.set("test", "test_string", "user value", ConfigSource.USER)
    config_system.set("test", "test_string", "runtime value", ConfigSource.RUNTIME)
    
    # Reset just the runtime values
    config_system.reset_to_defaults("test")
    
    # Should fall back to user value
    assert config_system.get("test", "test_string") == "user value"
    
    # Reset all sections
    config_system.set("test", "test_string", "runtime value", ConfigSource.RUNTIME)
    config_system.reset_to_defaults()
    
    # Should fall back to user value
    assert config_system.get("test", "test_string") == "user value"


def test_get_as_model(
    config_system: ConfigurationSystem,
) -> None:
    """Test getting configuration as a validated model."""
    config_system.initialize()
    config_system.register_section("test", TestConfigSection)
    
    # Update values
    config_system.set("test", "test_string", "model test", ConfigSource.USER)
    config_system.set("test", "test_int", 99, ConfigSource.USER)
    
    # Get as model
    model = config_system.get_as_model("test")
    
    # Verify it's the right type and has the right values
    assert isinstance(model, TestConfigSection)
    assert model.test_string == "model test"
    assert model.test_int == 99
    assert model.test_bool is True  # Default value


def test_file_watcher_functions(
    config_system: ConfigurationSystem,
) -> None:
    """Test file watcher functions."""
    # These methods don't do anything yet, but we should test them for coverage
    config_system._start_file_watching()
    config_system._stop_file_watching()
    config_system._check_file_modified()
    
    # No assertions needed as the methods are empty placeholders 