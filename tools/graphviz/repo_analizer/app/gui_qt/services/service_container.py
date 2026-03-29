"""
Service Container for Dependency Injection.

Manages application services (event bus, command dispatcher, controllers, etc.)
and provides them to components that need them.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Type, TypeVar

from ..command_dispatcher import CommandDispatcher
from ..event_bus import EventBus

T = TypeVar('T')


class ServiceContainer:
    """
    Lightweight dependency injection container.

    Manages singleton services and allows components to request dependencies
    without creating them manually.

    Example:
        container = ServiceContainer()
        container.register('event_bus', EventBus())
        container.register('prefix_dispatcher', CommandDispatcher())

        event_bus = container.get('event_bus')
        dispatcher = container.get('prefix_dispatcher')
    """

    def __init__(self) -> None:
        """Initialize the service container."""
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}
        self._singletons: Dict[str, Any] = {}

    def register(self, name: str, service: Any) -> None:
        """
        Register a service (singleton).

        Args:
            name: Service identifier
            service: Service instance

        Raises:
            ValueError: If service already registered
        """
        if name in self._services or name in self._factories:
            raise ValueError(f"Service '{name}' already registered")
        self._services[name] = service

    def register_factory(self, name: str, factory: callable) -> None:
        """
        Register a factory function.

        Factory will be called each time service is requested (not a singleton).

        Args:
            name: Service identifier
            factory: Callable that returns service instance

        Raises:
            ValueError: If service already registered
        """
        if name in self._services or name in self._factories:
            raise ValueError(f"Service '{name}' already registered")
        self._factories[name] = factory

    def register_singleton_factory(self, name: str, factory: callable) -> None:
        """
        Register a singleton factory.

        Factory will be called once, result cached and reused.

        Args:
            name: Service identifier
            factory: Callable that returns service instance

        Raises:
            ValueError: If service already registered
        """
        if name in self._services or name in self._factories:
            raise ValueError(f"Service '{name}' already registered")
        self._factories[name] = ('singleton', factory)

    def get(self, name: str) -> Optional[Any]:
        """
        Get a service.

        Args:
            name: Service identifier

        Returns:
            Service instance or None if not found
        """
        # Check if already registered as singleton
        if name in self._services:
            return self._services[name]

        # Check if cached singleton
        if name in self._singletons:
            return self._singletons[name]

        # Check if factory
        if name in self._factories:
            factory_def = self._factories[name]

            # Singleton factory
            if isinstance(factory_def, tuple) and factory_def[0] == 'singleton':
                service = factory_def[1]()
                self._singletons[name] = service
                return service

            # Regular factory
            return factory_def()

        return None

    def has(self, name: str) -> bool:
        """
        Check if service is registered.

        Args:
            name: Service identifier

        Returns:
            True if service is registered
        """
        return name in self._services or name in self._factories or name in self._singletons

    def unregister(self, name: str) -> None:
        """
        Unregister a service.

        Args:
            name: Service identifier
        """
        if name in self._services:
            del self._services[name]
        if name in self._factories:
            del self._factories[name]
        if name in self._singletons:
            del self._singletons[name]

    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()

    def get_all_names(self) -> list[str]:
        """
        Get all registered service names.

        Returns:
            List of service identifiers
        """
        return list(
            set(self._services.keys())
            | set(self._factories.keys())
            | set(self._singletons.keys())
        )
