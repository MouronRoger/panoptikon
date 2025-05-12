"""Tests for the error handling system."""

from datetime import datetime

import pytest

from src.panoptikon.core.errors import (
    ApplicationError,
    ConfigurationError,
    DatabaseError,
    ErrorCategory,
    ErrorContext,
    ErrorManager,
    ErrorSeverity,
    FileSystemError,
    SearchError,
    ValidationError,
)
from src.panoptikon.core.events import EventBus


def test_error_context() -> None:
    """Test error context creation and defaults."""
    # Test with defaults
    context = ErrorContext()
    assert isinstance(context.timestamp, datetime)
    assert context.user_action is None
    assert context.component is None
    assert context.source_location is None
    assert context.environment == {}
    assert context.related_objects == {}

    # Test with custom values
    timestamp = datetime.now()
    context = ErrorContext(
        timestamp=timestamp,
        user_action="test_action",
        component="test_component",
        source_location="test.py:123",
        environment={"key": "value"},
        related_objects={"obj": "test"},
    )
    assert context.timestamp == timestamp
    assert context.user_action == "test_action"
    assert context.component == "test_component"
    assert context.source_location == "test.py:123"
    assert context.environment == {"key": "value"}
    assert context.related_objects == {"obj": "test"}


def test_application_error() -> None:
    """Test application error creation and properties."""
    # Test with minimal arguments
    error = ApplicationError("test error")
    assert str(error) == "test error"
    assert error.message == "test error"
    assert error.severity == ErrorSeverity.ERROR
    assert error.category == ErrorCategory.UNKNOWN
    assert error.error_code.startswith("UNK-ApplicationError")
    assert error.inner_exception is None
    assert isinstance(error.context, ErrorContext)

    # Test with all arguments
    inner = ValueError("inner error")
    context = ErrorContext(component="test_component")
    error = ApplicationError(
        "test error",
        severity=ErrorSeverity.CRITICAL,
        category=ErrorCategory.VALIDATION,
        error_code="TEST-001",
        inner_exception=inner,
        context=context,
    )
    assert error.message == "test error"
    assert error.severity == ErrorSeverity.CRITICAL
    assert error.category == ErrorCategory.VALIDATION
    assert error.error_code == "TEST-001"
    assert error.inner_exception == inner
    assert error.context == context

    # Test dictionary conversion
    error_dict = error.to_dict()
    assert error_dict["message"] == "test error"
    assert error_dict["severity"] == "CRITICAL"
    assert error_dict["category"] == "VALIDATION"
    assert error_dict["error_code"] == "TEST-001"
    assert error_dict["inner_exception"] == "inner error"
    assert error_dict["component"] == "test_component"

    # Test event conversion
    event = error.to_event()
    assert event.error_type == "ApplicationError"
    assert event.message == "test error"
    assert event.severity == "CRITICAL"
    assert event.source == "test_component"


def test_specific_errors() -> None:
    """Test specific error types."""
    # Test ConfigurationError
    config_error = ConfigurationError("config error")
    assert config_error.category == ErrorCategory.CONFIGURATION
    assert config_error.error_code.startswith("CON-ConfigurationError")

    # Test DatabaseError
    db_error = DatabaseError("db error")
    assert db_error.category == ErrorCategory.DATABASE
    assert db_error.error_code.startswith("DAT-DatabaseError")

    # Test FileSystemError
    fs_error = FileSystemError("fs error")
    assert fs_error.category == ErrorCategory.FILESYSTEM
    assert fs_error.error_code.startswith("FIL-FileSystemError")

    # Test SearchError
    search_error = SearchError("search error")
    assert search_error.category == ErrorCategory.SEARCH
    assert search_error.error_code.startswith("SEA-SearchError")

    # Test ValidationError
    validation_error = ValidationError("validation error")
    assert validation_error.category == ErrorCategory.VALIDATION
    assert validation_error.error_code.startswith("VAL-ValidationError")
    assert validation_error.severity == ErrorSeverity.WARNING


@pytest.fixture
def event_bus() -> EventBus:
    """Create an event bus for testing."""
    return EventBus()


@pytest.fixture
def error_manager(event_bus: EventBus) -> ErrorManager:
    """Create an error manager for testing."""
    return ErrorManager(event_bus)


def test_error_manager_initialization(error_manager: ErrorManager) -> None:
    """Test error manager initialization."""
    assert error_manager._error_handlers == {}
    assert error_manager._recovery_handlers == {}
    assert error_manager._error_history == []
    assert error_manager._max_history_size == 100


def test_error_manager_handlers(error_manager: ErrorManager) -> None:
    """Test error handler registration and execution."""
    handled_errors: list[ApplicationError] = []

    def handler(error: ApplicationError) -> None:
        handled_errors.append(error)

    # Register handler
    error_manager.register_error_handler(ApplicationError, handler)

    # Handle error
    error = ApplicationError("test error")
    error_manager.handle_error(error)

    # Check handler was called
    assert len(handled_errors) == 1
    assert handled_errors[0] == error

    # Check error history
    history = error_manager.get_error_history()
    assert len(history) == 1
    assert history[0] == error


def test_error_manager_recovery(error_manager: ErrorManager) -> None:
    """Test error recovery handling."""

    def recovery_handler() -> str:
        return "recovered"

    # Register recovery handler
    error = ApplicationError("test error", error_code="TEST-001")
    error_manager.register_recovery_handler("TEST-001", recovery_handler)

    # Test recovery
    result = error_manager.recover_from_error(error)
    assert result == "recovered"

    # Test recovery for unknown error code
    unknown_error = ApplicationError("unknown error", error_code="UNKNOWN")
    with pytest.raises(ValueError):
        error_manager.recover_from_error(unknown_error)


def test_error_manager_history(error_manager: ErrorManager) -> None:
    """Test error history management."""
    # Set small history size
    error_manager.set_max_history_size(2)

    # Add errors
    error1 = ApplicationError("error1")
    error2 = ApplicationError("error2")
    error3 = ApplicationError("error3")

    error_manager.handle_error(error1)
    error_manager.handle_error(error2)
    error_manager.handle_error(error3)

    # Check history size and order
    history = error_manager.get_error_history()
    assert len(history) == 2
    assert history[0] == error2
    assert history[1] == error3

    # Clear history
    error_manager.clear_error_history()
    assert len(error_manager.get_error_history()) == 0

    # Test invalid history size
    with pytest.raises(ValueError):
        error_manager.set_max_history_size(0)


def test_error_manager_exception_conversion(error_manager: ErrorManager) -> None:
    """Test conversion of regular exceptions to ApplicationError."""
    # Handle regular exception
    regular_error = ValueError("test error")
    error_manager.handle_error(regular_error)

    # Check conversion
    history = error_manager.get_error_history()
    assert len(history) == 1
    converted = history[0]
    assert isinstance(converted, ApplicationError)
    assert converted.message == "test error"
    assert converted.category == ErrorCategory.UNKNOWN
    assert converted.inner_exception == regular_error


def test_error_manager_handler_inheritance(error_manager: ErrorManager) -> None:
    """Test error handler inheritance."""
    handled_base: list[ApplicationError] = []
    handled_specific: list[ApplicationError] = []

    def base_handler(error: ApplicationError) -> None:
        handled_base.append(error)

    def specific_handler(error: ApplicationError) -> None:
        if isinstance(error, ConfigurationError):
            handled_specific.append(error)

    # Register handlers
    error_manager.register_error_handler(ApplicationError, base_handler)
    error_manager.register_error_handler(ConfigurationError, specific_handler)

    # Handle specific error
    error = ConfigurationError("test error")
    error_manager.handle_error(error)

    # Both handlers should be called
    assert len(handled_base) == 1
    assert len(handled_specific) == 1
    assert handled_base[0] == error
    assert handled_specific[0] == error
