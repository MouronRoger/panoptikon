from __future__ import annotations

import logging

from panoptikon.core.service import ServiceContainer

logger = logging.getLogger(__name__)


def register_window_manager_hooks(container: ServiceContainer) -> None:
    """Register hooks for the window manager service.

    Note: This is a placeholder function for the future hook system that will be
    implemented in Stage 7 (UI Framework). The current ServiceContainer does not
    support hooks.

    TODO (Stage 7): Implement hook system in ServiceContainer or create an alternative
    approach for lifecycle management of the DualWindowManager.

    Args:
        container: The service container
    """
    logger.info(
        "Window manager hooks requested - feature will be implemented in Stage 7"
    )

    # Document what we would do if hooks were available
    """
    # Future implementation (Stage 7):
    container.register_factory_hook(
        WindowManagerInterface,
        lambda impl: impl,
        priority=100  # High priority to ensure early initialization
    )

    # Register shutdown hook
    container.register_shutdown_hook(
        WindowManagerInterface,
        lambda svc: svc.close_secondary_window() if svc.is_secondary_window_open() else None,
        priority=10  # Low priority to ensure late shutdown
    )
    """
