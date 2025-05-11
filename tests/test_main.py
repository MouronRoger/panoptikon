"""Tests for the main application entry point."""

import logging
from typing import Any, Generator, cast
from unittest.mock import patch

import pytest

from src.panoptikon.__main__ import main, setup_logging
from src.panoptikon.core.errors import ServiceNotRegisteredError
from src.panoptikon.core.lifecycle import ApplicationLifecycle, ApplicationState


@pytest.fixture
def clean_logging() -> Generator[None, None, None]:
    """Reset logging configuration before and after test."""
    # Store original handlers
    root = logging.getLogger()
    original_handlers = root.handlers.copy()
    original_level = root.level

    # Clear handlers
    root.handlers.clear()

    yield

    # Restore original handlers and level
    root.handlers = original_handlers
    root.level = original_level


def test_setup_logging(clean_logging: None) -> None:
    """Test logging setup."""
    # Set root logger to WARNING to match test environment
    root = logging.getLogger()
    root.setLevel(logging.WARNING)

    # Clear any existing handlers
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    setup_logging()

    # Check root logger configuration
    assert root.level == logging.DEBUG
    assert len(root.handlers) == 1
    assert isinstance(root.handlers[0], logging.StreamHandler)

    # Check formatter
    formatter = root.handlers[0].formatter
    assert formatter is not None
    fmt = cast(str, formatter._fmt)
    assert "%(asctime)s" in fmt
    assert "%(name)s" in fmt
    assert "%(levelname)s" in fmt
    assert "%(message)s" in fmt


def test_main_success() -> None:
    """Test successful application startup and shutdown."""
    # Mock signal handlers to avoid threading issues
    with (
        patch("signal.signal"),
        patch("src.panoptikon.__main__.ServiceContainer") as mock_container,
        patch("src.panoptikon.__main__.EventBus") as mock_event_bus,
        patch("src.panoptikon.__main__.ErrorManager") as mock_error_manager,
        patch("src.panoptikon.__main__.ConfigurationSystem") as mock_config_system,
        patch("src.panoptikon.__main__.ApplicationLifecycle") as mock_lifecycle,
    ):
        # Set up mock instances
        container_instance = mock_container.return_value
        event_bus_instance = mock_event_bus.return_value
        error_manager_instance = mock_error_manager.return_value
        config_system_instance = mock_config_system.return_value
        lifecycle_instance = mock_lifecycle.return_value

        # Configure lifecycle mock
        lifecycle_instance.get_state.return_value = ApplicationState.STOPPED
        lifecycle_instance.wait_for_shutdown.return_value = 0

        # Configure service initialization
        event_bus_instance.initialize.return_value = None
        error_manager_instance.initialize.return_value = None
        config_system_instance.initialize.return_value = None
        lifecycle_instance.initialize.return_value = None

        # Configure container
        container_instance.initialize_all.return_value = None
        container_instance.validate_dependencies.return_value = None

        # Mock the factory functions in __main__.py
        # Don't mock the resolve method directly - instead set up the registration
        # pattern as it happens in main()
        mock_event_bus.return_value = event_bus_instance
        mock_error_manager.return_value = error_manager_instance
        mock_config_system.return_value = config_system_instance
        mock_lifecycle.return_value = lifecycle_instance

        # Setup container.register to store factory functions
        factories = {}

        def mock_register(service_type: type, factory: Any) -> None:
            factories[service_type] = factory

        container_instance.register.side_effect = mock_register

        # Setup container.resolve to use the factories
        def mock_resolve(service_type: type) -> Any:
            if service_type in factories:
                return factories[service_type](container_instance)
            raise ServiceNotRegisteredError("Service not registered")

        container_instance.resolve.side_effect = mock_resolve

        # Run main and check exit code
        exit_code = main()
        assert exit_code == 0

        # Verify the application lifecycle
        lifecycle_instance.start.assert_called_once()
        lifecycle_instance.wait_for_shutdown.assert_called_once()

        # Verify container operations
        container_instance.validate_dependencies.assert_called_once()


def test_main_error() -> None:
    """Test error handling in main."""

    def mock_start() -> None:
        raise RuntimeError("Test error")

    # Patch the lifecycle start method
    original_start = ApplicationLifecycle.start
    ApplicationLifecycle.start = mock_start  # type: ignore

    try:
        # Run main and check exit code
        exit_code = main()
        assert exit_code == 1
    finally:
        # Restore original method
        ApplicationLifecycle.start = original_start  # type: ignore
