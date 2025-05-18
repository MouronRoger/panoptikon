"""Error handling and reporting framework.

This module provides a comprehensive error handling system including
structured error types, error reporting, recovery mechanisms, and
diagnostic information collection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
import logging
import sys
import traceback
from typing import Any, Callable, Optional, Union

from ..core.events import ErrorEvent, EventBus
from ..core.service import ServiceInterface

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Severity levels for errors in the system."""

    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class ErrorCategory(Enum):
    """Categories of errors in the system."""

    CONFIGURATION = auto()  # Configuration-related errors
    DATABASE = auto()  # Database access errors
    FILESYSTEM = auto()  # File system errors
    NETWORK = auto()  # Network-related errors
    SEARCH = auto()  # Search engine errors
    SECURITY = auto()  # Security-related errors
    UI = auto()  # User interface errors
    VALIDATION = auto()  # Input validation errors
    UNKNOWN = auto()  # Uncategorized errors


@dataclass
class ErrorContext:
    """Context information for an error."""

    timestamp: datetime = field(default_factory=datetime.now)
    user_action: Optional[str] = None
    component: Optional[str] = None
    source_location: Optional[str] = None
    environment: dict[str, object] = field(default_factory=dict)
    related_objects: dict[str, object] = field(default_factory=dict)


class ApplicationError(Exception):
    """Base class for all application errors.

    Provides structured error information including severity, category,
    error code, and contextual information.
    """

    def __init__(
        self,
        message: str,
        *,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        error_code: Optional[str] = None,
        inner_exception: Optional[Exception] = None,
        context: Optional[ErrorContext] = None,
    ) -> None:
        """Initialize a new application error.

        Args:
            message: Human-readable error message.
            severity: Severity level of the error.
            category: Category of the error.
            error_code: Optional error code for programmatic identification.
            inner_exception: Optional exception that caused this error.
            context: Optional context information for the error.
        """
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.category = category
        self.error_code = error_code or self._generate_error_code()
        self.inner_exception = inner_exception
        self.context = context or ErrorContext()

        # Capture stack trace
        self.traceback = traceback.format_exc()
        if self.traceback == "NoneType: None\n":
            self.traceback = ""

    def _generate_error_code(self) -> str:
        """Generate a unique error code based on the error type.

        Returns:
            A string error code.
        """
        error_type = self.__class__.__name__
        return f"{self.category.name[:3]}-{error_type}"

    def to_dict(self) -> dict[str, Any]:
        """Convert error to a dictionary representation.

        Returns:
            Dictionary representation of the error.
        """
        result = {
            "message": self.message,
            "severity": self.severity.name,
            "category": self.category.name,
            "error_code": self.error_code,
            "timestamp": self.context.timestamp,
            "traceback": self.traceback or None,
        }

        if self.inner_exception:
            result["inner_exception"] = str(self.inner_exception)

        if self.context.user_action:
            result["user_action"] = self.context.user_action

        if self.context.component:
            result["component"] = self.context.component

        if self.context.source_location:
            result["source_location"] = self.context.source_location

        return result

    def to_event(self) -> ErrorEvent:
        """Convert error to an event for publication on the event bus.

        Returns:
            An ErrorEvent representing this error.
        """
        return ErrorEvent(
            error_type=self.__class__.__name__,
            message=self.message,
            traceback=self.traceback,
            severity=self.severity.name,
            source=self.context.component,
        )


class ConfigurationError(ApplicationError):
    """Raised when there's an error in configuration."""

    def __init__(
        self,
        message: str,
        *,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        inner_exception: Optional[Exception] = None,
        context: Optional[ErrorContext] = None,
    ) -> None:
        """Initialize a new configuration error.

        Args:
            message: Human-readable error message.
            severity: Severity level of the error.
            inner_exception: Optional exception that caused this error.
            context: Optional context information for the error.
        """
        super().__init__(
            message,
            severity=severity,
            category=ErrorCategory.CONFIGURATION,
            inner_exception=inner_exception,
            context=context,
        )


class DatabaseError(ApplicationError):
    """Raised when there's an error accessing the database."""

    def __init__(
        self,
        message: str,
        *,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        inner_exception: Optional[Exception] = None,
        context: Optional[ErrorContext] = None,
    ) -> None:
        """Initialize a new database error.

        Args:
            message: Human-readable error message.
            severity: Severity level of the error.
            inner_exception: Optional exception that caused this error.
            context: Optional context information for the error.
        """
        super().__init__(
            message,
            severity=severity,
            category=ErrorCategory.DATABASE,
            inner_exception=inner_exception,
            context=context,
        )


class FileSystemError(ApplicationError):
    """Raised when there's an error accessing the file system."""

    def __init__(
        self,
        message: str,
        *,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        inner_exception: Optional[Exception] = None,
        context: Optional[ErrorContext] = None,
    ) -> None:
        """Initialize a new file system error.

        Args:
            message: Human-readable error message.
            severity: Severity level of the error.
            inner_exception: Optional exception that caused this error.
            context: Optional context information for the error.
        """
        super().__init__(
            message,
            severity=severity,
            category=ErrorCategory.FILESYSTEM,
            inner_exception=inner_exception,
            context=context,
        )


class SearchError(ApplicationError):
    """Raised when there's an error in the search engine."""

    def __init__(
        self,
        message: str,
        *,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        inner_exception: Optional[Exception] = None,
        context: Optional[ErrorContext] = None,
    ) -> None:
        """Initialize a new search error.

        Args:
            message: Human-readable error message.
            severity: Severity level of the error.
            inner_exception: Optional exception that caused this error.
            context: Optional context information for the error.
        """
        super().__init__(
            message,
            severity=severity,
            category=ErrorCategory.SEARCH,
            inner_exception=inner_exception,
            context=context,
        )


class ValidationError(ApplicationError):
    """Raised when there's an error in input validation."""

    def __init__(
        self,
        message: str,
        *,
        severity: ErrorSeverity = ErrorSeverity.WARNING,
        inner_exception: Optional[Exception] = None,
        context: Optional[ErrorContext] = None,
    ) -> None:
        """Initialize a new validation error.

        Args:
            message: Human-readable error message.
            severity: Severity level of the error.
            inner_exception: Optional exception that caused this error.
            context: Optional context information for the error.
        """
        super().__init__(
            message,
            severity=severity,
            category=ErrorCategory.VALIDATION,
            inner_exception=inner_exception,
            context=context,
        )


class ServiceNotRegisteredError(ApplicationError):
    """Raised when attempting to resolve a service that hasn't been registered."""

    def __init__(
        self,
        message: str,
        *,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        inner_exception: Optional[Exception] = None,
        context: Optional[ErrorContext] = None,
    ) -> None:
        """Initialize a new service not registered error.

        Args:
            message: Human-readable error message.
            severity: Severity level of the error.
            inner_exception: Optional exception that caused this error.
            context: Optional context information for the error.
        """
        super().__init__(
            message,
            severity=severity,
            category=ErrorCategory.CONFIGURATION,
            inner_exception=inner_exception,
            context=context,
        )


class ErrorManager:
    """Central error management and reporting system.

    Provides error handling, reporting, and recovery mechanisms.
    """

    def __init__(self, event_bus: EventBus) -> None:
        """Initialize the error manager.

        Args:
            event_bus: Event bus for publishing error events.
        """
        self._event_bus = event_bus
        self._error_handlers: dict[
            type[ApplicationError], list[Callable[[ApplicationError], None]]
        ] = {}
        self._recovery_handlers: dict[str, Callable[[], Any]] = {}
        self._error_history: list[ApplicationError] = []
        self._max_history_size = 100

    def register_error_handler(
        self,
        error_type: type[ApplicationError],
        handler: Callable[[ApplicationError], None],
    ) -> None:
        """Register a handler for a specific error type.

        Args:
            error_type: Type of error to handle.
            handler: Function to call when error occurs.
        """
        if error_type not in self._error_handlers:
            self._error_handlers[error_type] = []
        self._error_handlers[error_type].append(handler)

    def register_recovery_handler(
        self, error_code: str, handler: Callable[[], Any]
    ) -> None:
        """Register a recovery handler for a specific error code.

        Args:
            error_code: Error code to handle.
            handler: Function to call for recovery.
        """
        self._recovery_handlers[error_code] = handler

    def handle_error(
        self, error: Union[ApplicationError, Exception], reraise: bool = False
    ) -> None:
        """Handle an error by logging it and calling appropriate handlers.

        Args:
            error: The error to handle.
            reraise: Whether to reraise the error after handling.
        """
        # Convert to ApplicationError if needed
        app_error = self._ensure_application_error(error)

        # Add to history
        self._error_history.append(app_error)
        if len(self._error_history) > self._max_history_size:
            self._error_history = self._error_history[-self._max_history_size :]

        # Log the error
        self._log_error(app_error)

        # Publish error event
        self._event_bus.publish(app_error.to_event())

        # Call registered handlers
        self._call_error_handlers(app_error)

        # Reraise if requested
        if reraise:
            raise app_error

    def recover_from_error(self, error: ApplicationError) -> Any:
        """Attempt to recover from an error.

        Args:
            error: The error to recover from.

        Returns:
            Result of the recovery handler.

        Raises:
            ValueError: If no recovery handler is registered for the error.
        """
        if error.error_code in self._recovery_handlers:
            return self._recovery_handlers[error.error_code]()

        raise ValueError(
            f"No recovery handler registered for error code: {error.error_code}"
        )

    def get_error_history(self) -> list[ApplicationError]:
        """Get the history of errors.

        Returns:
            List of errors that have occurred.
        """
        return self._error_history.copy()

    def clear_error_history(self) -> None:
        """Clear the error history."""
        self._error_history.clear()

    def set_max_history_size(self, size: int) -> None:
        """Set the maximum number of errors to keep in history.

        Args:
            size: Maximum number of errors to keep.

        Raises:
            ValueError: If size is not positive.
        """
        if size <= 0:
            raise ValueError("History size must be positive")
        self._max_history_size = size
        # Trim history if needed
        if len(self._error_history) > self._max_history_size:
            self._error_history = self._error_history[-self._max_history_size :]

    def _ensure_application_error(
        self, error: Union[ApplicationError, Exception]
    ) -> ApplicationError:
        """Convert a regular exception to an ApplicationError if needed.

        Args:
            error: The error to convert.

        Returns:
            An ApplicationError.
        """
        if isinstance(error, ApplicationError):
            return error

        # Create context with stack information
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_traceback:
            frame = traceback.extract_tb(exc_traceback)[-1]
            source_location = f"{frame.filename}:{frame.lineno}"
        else:
            source_location = None

        context = ErrorContext(source_location=source_location)

        # Convert to ApplicationError
        return ApplicationError(
            str(error),
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.UNKNOWN,
            inner_exception=error,
            context=context,
        )

    def _log_error(self, error: ApplicationError) -> None:
        """Log an error with appropriate severity.

        Args:
            error: The error to log.
        """
        message = f"{error.error_code}: {error.message}"

        if error.inner_exception:
            message += f" (Caused by: {error.inner_exception})"

        if error.severity == ErrorSeverity.DEBUG:
            logger.debug(message, exc_info=bool(error.traceback))
        elif error.severity == ErrorSeverity.INFO:
            logger.info(message, exc_info=bool(error.traceback))
        elif error.severity == ErrorSeverity.WARNING:
            logger.warning(message, exc_info=bool(error.traceback))
        elif error.severity == ErrorSeverity.ERROR:
            logger.error(message, exc_info=bool(error.traceback))
        elif error.severity == ErrorSeverity.CRITICAL:
            logger.critical(message, exc_info=bool(error.traceback))

    def _call_error_handlers(self, error: ApplicationError) -> None:
        """Call registered handlers for an error.

        Args:
            error: The error to handle.
        """
        # Call handlers for the specific error type
        error_type = type(error)
        if error_type in self._error_handlers:
            for handler in self._error_handlers[error_type]:
                try:
                    handler(error)
                except Exception as e:
                    logger.error(f"Error in error handler: {e}", exc_info=True)

        # Call handlers for parent error types
        for registered_type, handlers in self._error_handlers.items():
            if error_type != registered_type and issubclass(
                error_type, registered_type
            ):
                for handler in handlers:
                    try:
                        handler(error)
                    except Exception as e:
                        logger.error(f"Error in error handler: {e}", exc_info=True)


class ErrorHandlingService(ServiceInterface):
    """Service for centralized error handling across the application.

    This service integrates with the service container and event system
    to provide application-wide error handling capabilities.
    """

    def __init__(self, event_bus: EventBus) -> None:
        """Initialize the error handling service.

        Args:
            event_bus: The event bus for publishing error events.
        """
        self._error_manager = ErrorManager(event_bus)
        self._event_bus = event_bus

    def initialize(self) -> None:
        """Initialize the error handling service.

        Sets up event subscriptions and prepares the error handling system.
        """
        logger.debug("Initializing ErrorHandlingService")

    def shutdown(self) -> None:
        """Shut down the error handling service."""
        logger.debug("Shutting down ErrorHandlingService")

    def handle_error(
        self, error: Union[ApplicationError, Exception], reraise: bool = False
    ) -> None:
        """Handle an error through the error manager.

        Args:
            error: The error to handle.
            reraise: Whether to reraise the error after handling.
        """
        self._error_manager.handle_error(error, reraise)

    def register_error_handler(
        self,
        error_type: type[ApplicationError],
        handler: Callable[[ApplicationError], None],
    ) -> None:
        """Register a handler for a specific error type.

        Args:
            error_type: Type of error to handle.
            handler: Function to call when error occurs.
        """
        self._error_manager.register_error_handler(error_type, handler)

    def register_recovery_handler(
        self, error_code: str, handler: Callable[[], Any]
    ) -> None:
        """Register a recovery handler for a specific error code.

        Args:
            error_code: Error code to handle.
            handler: Function to call for recovery.
        """
        self._error_manager.register_recovery_handler(error_code, handler)

    def recover_from_error(self, error: ApplicationError) -> Any:
        """Attempt to recover from an error.

        Args:
            error: The error to recover from.

        Returns:
            Result of the recovery handler.

        Raises:
            ValueError: If no recovery handler is registered for the error.
        """
        return self._error_manager.recover_from_error(error)

    def get_error_history(self) -> list[ApplicationError]:
        """Get the history of errors.

        Returns:
            List of errors that have occurred.
        """
        return self._error_manager.get_error_history()

    def clear_error_history(self) -> None:
        """Clear the error history."""
        self._error_manager.clear_error_history()

    def set_max_history_size(self, size: int) -> None:
        """Set the maximum number of errors to keep in history.

        Args:
            size: Maximum number of errors to keep.

        Raises:
            ValueError: If size is not positive.
        """
        self._error_manager.set_max_history_size(size)
