"""Service container implementation for dependency injection.

This module provides a service container that enables dependency injection
throughout the application, supporting singleton and transient service lifetimes
and preventing circular dependencies.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Callable, Optional, TypeVar, cast, get_type_hints

T = TypeVar("T")
ServiceType = TypeVar("ServiceType")


class ServiceLifetime(Enum):
    """Defines the lifetime of a registered service."""

    SINGLETON = auto()
    TRANSIENT = auto()


class ServiceInterface(ABC):
    """Base interface for all injectable services.

    All services that need to be injectable should inherit from this class.
    """

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the service.

        Called by the container when the service is first created.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Perform cleanup when the service is being disposed.

        Called by the container during application shutdown.
        """
        pass


class CircularDependencyError(Exception):
    """Raised when a circular dependency is detected in the service graph."""

    pass


class ServiceNotRegisteredError(Exception):
    """Raised when attempting to resolve a service that hasn't been registered."""

    pass


class ServiceContainer:
    """Container for managing service dependencies and lifecycle.

    Provides registration, resolution, and lifecycle management for services.
    Detects and prevents circular dependencies in the service graph.
    """

    def __init__(self) -> None:
        """Initialize an empty service container."""
        self._registrations: dict[type[Any], dict[str, Any]] = {}
        self._instances: dict[type[Any], Any] = {}
        self._resolution_stack: set[type[Any]] = set()
        self._initialized = False

    def register(
        self,
        service_type: type[ServiceType],
        implementation_type: Optional[type[ServiceType]] = None,
        factory: Optional[Callable[["ServiceContainer"], ServiceType]] = None,
        lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
    ) -> None:
        """Register a service with the container.

        Args:
            service_type: The interface or base type to register.
            implementation_type: The concrete type to instantiate
                (defaults to service_type).
            factory: Optional factory function to create the service.
            lifetime: The lifetime of the service (singleton or transient).

        Raises:
            ValueError: If neither implementation_type nor factory is provided,
                       or if both are provided.
        """
        if (implementation_type is None and factory is None) or (
            implementation_type is not None and factory is not None
        ):
            raise ValueError(
                "Either implementation_type or factory must be provided, but not both"
            )

        self._registrations[service_type] = {
            "implementation": implementation_type or service_type,
            "factory": factory,
            "lifetime": lifetime,
        }

    def resolve(self, service_type: type[T]) -> T:
        """Resolve a service instance from the container.

        Args:
            service_type: The type of service to resolve.

        Returns:
            An instance of the requested service.

        Raises:
            ServiceNotRegisteredError: If the requested service is not registered.
            CircularDependencyError: If resolving would cause a circular dependency.
        """
        if service_type not in self._registrations:
            raise ServiceNotRegisteredError(
                f"Service {service_type.__name__} not registered"
            )

        # Check for circular dependencies
        if service_type in self._resolution_stack:
            path = (
                " -> ".join(s.__name__ for s in self._resolution_stack)
                + f" -> {service_type.__name__}"
            )
            raise CircularDependencyError(f"Circular dependency detected: {path}")

        # For singleton services, return existing instance if available
        registration = self._registrations[service_type]
        if (
            registration["lifetime"] == ServiceLifetime.SINGLETON
            and service_type in self._instances
        ):
            return cast(T, self._instances[service_type])

        # Create new instance
        try:
            self._resolution_stack.add(service_type)
            instance = self._create_instance(service_type, registration)
            return cast(T, instance)
        finally:
            self._resolution_stack.remove(service_type)

    def _create_instance(
        self, service_type: type[Any], registration: dict[str, Any]
    ) -> Any:
        """Create a new instance of the service.

        Args:
            service_type: The type of service to create.
            registration: The registration data for the service.

        Returns:
            A new instance of the service.
        """
        if registration["factory"] is not None:
            instance = registration["factory"](self)
        else:
            instance = self._create_from_implementation(registration["implementation"])

        # Initialize if it's a ServiceInterface
        if isinstance(instance, ServiceInterface) and self._initialized:
            instance.initialize()

        # Store singleton instance
        if registration["lifetime"] == ServiceLifetime.SINGLETON:
            self._instances[service_type] = instance

        return instance

    def _create_from_implementation(self, implementation_type: type[Any]) -> Any:
        """Create a new instance using the implementation type.

        Args:
            implementation_type: The type to instantiate.

        Returns:
            A new instance of the implementation type.
        """
        # Get constructor dependencies
        dependencies = {}
        if hasattr(implementation_type, "__init__"):
            type_hints = get_type_hints(implementation_type.__init__)
            for param_name, param_type in type_hints.items():
                if param_name != "return" and param_name != "self":
                    dependencies[param_name] = self.resolve(param_type)

        return implementation_type(**dependencies)

    def initialize_all(self) -> None:
        """Initialize all registered singleton services.

        This method should be called during application startup.
        """
        # First set the initialized flag so that new services will be initialized as they're resolved
        self._initialized = True

        # Initialize all singleton services that may have been resolved before
        for service in self._instances.values():
            if isinstance(service, ServiceInterface):
                service.initialize()

        # Make sure all singletons are created and initialized
        for service_type, registration in self._registrations.items():
            if registration["lifetime"] == ServiceLifetime.SINGLETON:
                # This will initialize the service if it hasn't been resolved yet
                self.resolve(service_type)

    def shutdown_all(self) -> None:
        """Shut down all initialized services.

        This method should be called during application shutdown.
        """
        # Shutdown in reverse order of dependency (not perfect but helps)
        for service in reversed(list(self._instances.values())):
            if isinstance(service, ServiceInterface):
                service.shutdown()

        self._instances.clear()
        self._initialized = False

    def validate_dependencies(self) -> None:
        """Validate the dependency graph to detect circular dependencies.

        Raises:
            CircularDependencyError: If a circular dependency is detected.
        """
        for service_type in self._registrations:
            temp_stack: set[type[Any]] = set()
            self._validate_service_dependencies(service_type, temp_stack)

    def _get_service_name(self, service_type: type[Any]) -> str:
        """Get a readable name for a service type.

        Args:
            service_type: The service type.

        Returns:
            A string representation of the service type.
        """
        if hasattr(service_type, "__name__"):
            return service_type.__name__
        return str(service_type)

    def _format_dependency_path(
        self, visited: set[type[Any]], end_type: type[Any]
    ) -> str:
        """Format a dependency path for error messages.

        Args:
            visited: The set of visited service types.
            end_type: The end point of the dependency path.

        Returns:
            A formatted dependency path string.
        """
        path_names = []
        for s in visited:
            path_names.append(self._get_service_name(s))

        path_names.append(self._get_service_name(end_type))
        return " -> ".join(path_names)

    def _normalize_type(self, service_type: Any) -> Any:
        """Normalize a type, handling Optional and other container types.

        Args:
            service_type: The type to normalize.

        Returns:
            The normalized type.
        """
        # Handle Optional types (these have __origin__ attribute but no __name__)
        if hasattr(service_type, "__origin__"):
            # For Optional[Type], use the contained type
            if hasattr(service_type, "__args__") and service_type.__args__:
                return service_type.__args__[0]
        return service_type

    def _validate_service_dependencies(
        self, service_type: type[Any], visited: set[type[Any]]
    ) -> None:
        """Recursively validate dependencies for a service type.

        Args:
            service_type: The service type to validate.
            visited: Set of service types currently being validated.

        Raises:
            CircularDependencyError: If a circular dependency is detected.
            ServiceNotRegisteredError: If a required dependency is not registered.
        """
        # Normalize the type (handles Optional, etc.)
        service_type = self._normalize_type(service_type)

        # Check for circular dependencies
        if service_type in visited:
            path = self._format_dependency_path(visited, service_type)
            raise CircularDependencyError(f"Circular dependency detected: {path}")

        # Check if service is registered
        if service_type not in self._registrations:
            name = self._get_service_name(service_type)
            raise ServiceNotRegisteredError(f"Service {name} not registered")

        # Get service registration
        registration = self._registrations[service_type]

        # Skip validation for factory-created services
        if registration["factory"] is not None:
            return

        # Validate constructor dependencies
        implementation_type = registration["implementation"]
        if hasattr(implementation_type, "__init__"):
            visited.add(service_type)
            try:
                type_hints = get_type_hints(implementation_type.__init__)
                for param_name, param_type in type_hints.items():
                    if param_name != "return" and param_name != "self":
                        self._validate_service_dependencies(param_type, visited.copy())
            finally:
                visited.remove(service_type)
