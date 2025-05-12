"""Extended tests for the configuration system to improve coverage."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.panoptikon.core.config import (
    ConfigChangedEvent,
    ConfigFileError,
    ConfigSource,
    ConfigurationSystem,
)
from src.panoptikon.core.events import EventBus
from tests.conftest import TestConfigSection

# ruff: noqa: I001 -- order preserved after automated removal of unused imports


def test_config_validation(config_system_hot: ConfigurationSystem) -> None:
    """Test validation of configuration values."""
    config_system_hot.initialize()
    config_system_hot.register_section("test", TestConfigSection)

    # Test valid values
    config_system_hot.set("test", "int_value", 100)
    assert config_system_hot.get("test", "int_value") == 100

    # Test invalid values (type error)
    with pytest.raises((TypeError, ValueError, Exception)):
        config_system_hot.set("test", "int_value", "not_an_int")


def test_get_as_model_validation(config_system_hot: ConfigurationSystem) -> None:
    """Test get_as_model with validation."""
    config_system_hot.initialize()
    config_system_hot.register_section("test", TestConfigSection)

    # Set some values
    config_system_hot.set("test", "string_value", "model test")
    config_system_hot.set("test", "int_value", 123)
    config_system_hot.set("test", "list_value", ["a", "b", "c"])

    # Get as model
    model = config_system_hot.get_as_model("test")
    assert model.string_value == "model test"  # type: ignore[attr-defined]
    assert model.int_value == 123  # type: ignore[attr-defined]
    assert model.list_value == ["a", "b", "c"]  # type: ignore[attr-defined]
    assert model.optional_value is None  # type: ignore[attr-defined]
    assert model.complex_value == {}  # type: ignore[attr-defined]
    assert model.set_value == set()  # type: ignore[attr-defined]


def test_config_file_error_handling(temp_config_dir: Path, event_bus: EventBus) -> None:
    """Test handling of config file errors."""
    config_system = ConfigurationSystem(
        event_bus, config_dir=temp_config_dir, hot_reload=False
    )
    config_system.initialize()
    config_system.register_section("test", TestConfigSection)

    # Set a value
    config_system.set("test", "string_value", "test value", source=ConfigSource.USER)

    # Mock json.dump to raise an error
    with (
        patch("json.dump", side_effect=OSError("Mock file error")),
        pytest.raises(ConfigFileError),
    ):
        config_system.save()


def test_load_invalid_config_file(temp_config_dir: Path, event_bus: EventBus) -> None:
    """Test loading an invalid configuration file."""
    # Create an invalid JSON file
    config_file = temp_config_dir / "config.json"
    with open(config_file, "w") as f:
        f.write("this is not valid json")

    # Initialize with this invalid file
    config_system = ConfigurationSystem(
        event_bus, config_dir=temp_config_dir, hot_reload=False
    )

    # Test what happens when loading an invalid file
    with pytest.raises(ConfigFileError) as exc_info:
        config_system.initialize()

    assert "Invalid configuration file" in str(exc_info.value)


def test_hot_reload(
    config_system_hot: ConfigurationSystem, temp_config_dir: Path
) -> None:
    """Test hot reloading of configuration from disk."""
    config_system_hot.initialize()
    config_system_hot.register_section("test", TestConfigSection)

    # Set a user-level value and save
    config_system_hot.set("test", "string_value", "original", source=ConfigSource.USER)
    config_system_hot.save()

    # Directly call the reload method with a mocked _load_user_config
    with patch.object(
        config_system_hot, "_load_user_config", return_value=True
    ) as mock_load:
        result = config_system_hot.reload()
        assert result is True
        assert mock_load.call_count == 1


def test_emit_config_change_events(
    config_system_hot: ConfigurationSystem, event_bus: EventBus
) -> None:
    """Test emitting of configuration change events."""
    # Create a mock event handler
    mock_handler = MagicMock()
    event_bus.subscribe(ConfigChangedEvent, mock_handler)

    config_system_hot.initialize()
    config_system_hot.register_section("test", TestConfigSection)

    # Create old and new configs for testing
    old_config = {"test": {"string_value": "old", "int_value": 1}}
    new_config = {"test": {"string_value": "new", "int_value": 2, "list_value": ["a"]}}

    # Call the method directly
    config_system_hot._emit_config_change_events(old_config, new_config)

    # Verify events were published
    assert mock_handler.called
    # Should be called 3 times: string_value changed, int_value changed, list_value added
    assert mock_handler.call_count == 3


@pytest.mark.skipif(os.name != "nt", reason="Windows-specific test")
def test_windows_config_dir() -> None:
    """Test Windows-specific configuration directory detection."""
    event_bus = EventBus()

    with patch.dict("os.environ", {"APPDATA": r"C:\Users\Test\AppData\Roaming"}):
        config_system = ConfigurationSystem(event_bus)
        assert "Panoptikon" in str(config_system._config_dir)


def test_config_dir_detection() -> None:
    """Test configuration directory detection with proper mocking."""
    event_bus = EventBus()

    # Test with mocked _get_default_config_dir
    with (
        patch.object(
            ConfigurationSystem,
            "_get_default_config_dir",
            return_value=Path("/tmp/mock_config_dir"),
        ),
        patch("os.makedirs"),
    ):
        config_system = ConfigurationSystem(event_bus)
        assert str(config_system._config_dir) == "/tmp/mock_config_dir"


def test_file_watching(config_system_hot: ConfigurationSystem) -> None:
    """Test file watching functionality."""
    # Mock both methods before initializing
    with patch.object(config_system_hot, "_start_file_watching") as mock_start:
        config_system_hot.initialize()
        # Since hot_reload=True in the fixture, this should be called
        assert mock_start.call_count == 1

    # For shutdown, we need to mock the file watcher attribute since it doesn't exist
    config_system_hot._file_watcher = MagicMock()  # type: ignore[assignment]
    with patch.object(config_system_hot, "_stop_file_watching") as mock_stop:
        config_system_hot.shutdown()
        assert mock_stop.call_count == 1


def test_config_changed_event_validation() -> None:
    """Test validation of ConfigChangedEvent."""
    # Valid event
    event = ConfigChangedEvent(
        section="test", key="value", old_value="old", new_value="new"
    )
    assert event.section == "test"
    assert event.key == "value"

    # Invalid event - empty section
    with pytest.raises(ValueError):
        ConfigChangedEvent(section="", key="value")

    # Invalid event - empty key
    with pytest.raises(ValueError):
        ConfigChangedEvent(section="test", key="")
