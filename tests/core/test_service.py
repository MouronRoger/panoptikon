"""Unit tests for the service container."""

from typing import Optional

import pytest

from src.panoptikon.core.service import (
    CircularDependencyError,
    ServiceContainer,
    ServiceInterface,
    ServiceLifetime,
    ServiceNotRegisteredError,
)


class MockService(ServiceInterface):
    """Mock service for testing."""

    def __init__(self) -> None:
        """Initialize the mock service."""
        self.initialized = False
        self.shutdown_called = False

    def initialize(self) -> None:
        """Initialize the service."""
        self.initialized = True

    def shutdown(self) -> None:
        """Shut down the service."""
        self.shutdown_called = True


class DependentService(ServiceInterface):
    """Service that depends on another service."""

    def __init__(self, dependency: MockService) -> None:
        """Initialize with a dependency.

        Args:
            dependency: The required dependency.
        """
        self.dependency = dependency
        self.initialized = False
        self.shutdown_called = False

    def initialize(self) -> None:
        """Initialize the service."""
        self.initialized = True

    def shutdown(self) -> None:
        """Shut down the service."""
        self.shutdown_called = True


class CircularService1(ServiceInterface):
    """First service in a circular dependency."""

    def __init__(self, dependency: Optional["CircularService2"] = None) -> None:
        """Initialize with a circular dependency.

        Args:
            dependency: The circular dependency.
        """
        self.dependency = dependency

    def initialize(self) -> None:
        """Initialize the service."""
        pass

    def shutdown(self) -> None:
        """Shut down the service."""
        pass


class CircularService2(ServiceInterface):
    """Second service in a circular dependency."""

    def __init__(self, dependency: CircularService1) -> None:
        """Initialize with a circular dependency.

        Args:
            dependency: The circular dependency.
        """
        self.dependency = dependency

    def initialize(self) -> None:
        """Initialize the service."""
        pass

    def shutdown(self) -> None:
        """Shut down the service."""
        pass


def test_registration_and_resolution() -> None:
    """Test service registration and resolution."""
    container = ServiceContainer()
    container.register(MockService, implementation_type=MockService)
    service = container.resolve(MockService)
    assert isinstance(service, MockService)


def test_singleton_lifecycle() -> None:
    """Test singleton service lifecycle."""
    container = ServiceContainer()

    # Register a singleton service
    container.register(MockService, MockService, lifetime=ServiceLifetime.SINGLETON)

    # Resolve the service twice
    service1 = container.resolve(MockService)
    service2 = container.resolve(MockService)

    # Should be the same instance
    assert service1 is service2

    # Initialize services
    container.initialize_all()

    assert service1.initialized

    # Shutdown services
    container.shutdown_all()

    assert service1.shutdown_called


def test_transient_lifecycle() -> None:
    """Test transient service lifecycle."""
    container = ServiceContainer()

    # Register a transient service
    container.register(MockService, MockService, lifetime=ServiceLifetime.TRANSIENT)

    # Resolve the service twice
    service1 = container.resolve(MockService)
    service2 = container.resolve(MockService)

    # Should be different instances
    assert service1 is not service2

    # Initialize services
    container.initialize_all()

    # Only singleton services are initialized automatically
    assert not service1.initialized

    # Shutdown services
    container.shutdown_all()

    # Transient services aren't tracked for shutdown
    assert not service1.shutdown_called


def test_factory_registration() -> None:
    """Test service registration with a factory function."""
    container = ServiceContainer()

    # Register with a factory
    container.register(MockService, factory=lambda c: MockService())

    # Resolve the service
    service = container.resolve(MockService)

    assert isinstance(service, MockService)


def test_dependency_injection() -> None:
    """Test automatic dependency injection."""
    container = ServiceContainer()

    # Register services
    container.register(MockService, MockService)
    container.register(DependentService, DependentService)

    # Resolve dependent service
    service = container.resolve(DependentService)

    assert isinstance(service, DependentService)
    assert isinstance(service.dependency, MockService)


def test_unregistered_service() -> None:
    """Test resolving an unregistered service."""
    container = ServiceContainer()

    # Try to resolve unregistered service
    with pytest.raises(ServiceNotRegisteredError):
        container.resolve(MockService)


def test_circular_dependency_detection() -> None:
    """Test detection of circular dependencies."""
    container = ServiceContainer()

    # Register services with circular dependency
    container.register(CircularService1, CircularService1)
    container.register(CircularService2, CircularService2)

    # Validate dependencies should fail
    with pytest.raises(CircularDependencyError):
        container.validate_dependencies()


def test_dependency_validation() -> None:
    """Test dependency validation."""
    container = ServiceContainer()

    # Register services with valid dependencies
    container.register(MockService, MockService)
    container.register(DependentService, DependentService)

    # Validation should succeed
    container.validate_dependencies()


def test_invalid_registration() -> None:
    """Test invalid service registration."""
    container = ServiceContainer()

    # Neither implementation nor factory
    with pytest.raises(ValueError):
        container.register(MockService)

    # Both implementation and factory
    with pytest.raises(ValueError):
        container.register(MockService, MockService, factory=lambda c: MockService())
