"""Smoke/integration test for system bootstrapping and minimal end-to-end flows."""

from panoptikon.core.config import ConfigurationSystem
from panoptikon.core.errors import ApplicationError, ErrorHandlingService
from panoptikon.core.events import EventBase, EventBus
from panoptikon.core.lifecycle import ApplicationLifecycle
from panoptikon.core.service import ServiceContainer, ServiceLifetime


def test_system_bootstrap_and_minimal_flow() -> None:
    """Smoke test: system boots, minimal flows work, and shuts down cleanly."""
    container = ServiceContainer()
    container.register(
        EventBus, implementation_type=EventBus, lifetime=ServiceLifetime.SINGLETON
    )
    container.register(
        ConfigurationSystem,
        implementation_type=ConfigurationSystem,
        lifetime=ServiceLifetime.SINGLETON,
    )
    container.register(
        ErrorHandlingService,
        implementation_type=ErrorHandlingService,
        lifetime=ServiceLifetime.SINGLETON,
    )
    container.register(
        ApplicationLifecycle,
        implementation_type=ApplicationLifecycle,
        lifetime=ServiceLifetime.SINGLETON,
    )

    # Validate dependencies
    container.validate_dependencies()

    # Initialize all services
    container.initialize_all()

    # Resolve services
    event_bus: EventBus = container.resolve(EventBus)
    config: ConfigurationSystem = container.resolve(ConfigurationSystem)
    error_service: ErrorHandlingService = container.resolve(ErrorHandlingService)
    lifecycle: ApplicationLifecycle = container.resolve(ApplicationLifecycle)

    # Minimal event bus test
    received = []

    class TestEvent(EventBase):
        def __init__(self, message: str) -> None:
            super().__init__()
            self.message = message

    def handler(event: TestEvent) -> None:
        received.append(event.message)

    event_bus.subscribe(TestEvent, handler)
    event_bus.publish(TestEvent("smoke test event"))
    assert received == ["smoke test event"]

    # Minimal config test
    config.initialize()
    config.register_section("smoke", dict, {"foo": "bar"})
    config.set("smoke", "foo", "baz")
    assert config.get("smoke", "foo") == "baz"

    # Minimal error handling test
    errors = []

    def error_handler(error: ApplicationError) -> None:
        errors.append(str(error))

    error_service.register_error_handler(ApplicationError, error_handler)
    error = ApplicationError("smoke error")
    error_service.handle_error(error)
    assert errors and "smoke error" in errors[0]

    # Minimal lifecycle test
    called = []
    lifecycle.register_startup_hook("smoke_start", lambda: called.append("start"))
    lifecycle.register_shutdown_hook("smoke_stop", lambda: called.append("stop"))
    lifecycle.start()
    lifecycle.stop()
    assert called == ["start", "stop"]

    # Clean shutdown
    container.shutdown_all()
