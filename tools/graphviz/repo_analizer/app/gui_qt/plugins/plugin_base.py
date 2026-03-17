"""Base plugin class for the plugin system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ..command_dispatcher import CommandDispatcher
    from ..event_bus import EventBus
    from ..services import ServiceContainer
    from ..ui_contribution_registry import UIContributionRegistry


class Plugin(ABC):
    """
    Base class for application plugins.

    Plugins can register commands, subscribe to events, and contribute UI.

    Example:
        class MyPlugin(Plugin):
            name = 'my_plugin'
            version = '1.0.0'

            def initialize(self, context: PluginContext) -> None:
                self.context = context
                self.register_commands()
                self.subscribe_events()

            def register_commands(self) -> None:
                cmd = MyCommand(...)
                self.context.dispatcher.register('my_command', cmd)

            def subscribe_events(self) -> None:
                self.context.event_bus.subscribe('some_event', self.on_event)

            def on_event(self, payload):
                pass
    """

    #: Plugin name (must be unique)
    name: str = 'unknown'

    #: Plugin version
    version: str = '0.1.0'

    #: Plugin description
    description: str = ''

    #: Plugin author
    author: str = ''

    def __init__(self) -> None:
        """Initialize the plugin."""
        self.enabled = True
        self._unsubscribe_handlers: list[callable] = []

    @abstractmethod
    def initialize(self, context: PluginContext) -> None:
        """
        Initialize the plugin.

        Called when plugin is loaded. Use this to register commands,
        subscribe to events, etc.

        Args:
            context: PluginContext with access to services
        """
        pass

    def shutdown(self) -> None:
        """
        Clean up when plugin is unloaded.

        Override to clean up resources, unsubscribe from events, etc.
        """
        for handler in self._unsubscribe_handlers:
            handler()
        self._unsubscribe_handlers.clear()

    def register_command(
        self, context: PluginContext, name: str, command: Any
    ) -> None:
        """
        Register a command.

        Args:
            context: PluginContext
            name: Command name
            command: Command instance
        """
        context.dispatcher.register(name, command)

    def subscribe_event(
        self, context: PluginContext, event: str, handler: callable
    ) -> None:
        """
        Subscribe to an event.

        Args:
            context: PluginContext
            event: Event name
            handler: Handler callable
        """
        unsub = context.event_bus.subscribe(event, handler)
        self._unsubscribe_handlers.append(unsub)

    def emit_event(
        self, context: PluginContext, event: str, payload: Any = None
    ) -> None:
        """
        Emit an event.

        Args:
            context: PluginContext
            event: Event name
            payload: Event payload
        """
        context.event_bus.publish(event, payload)


class PluginContext:
    """
    Context passed to plugins during initialization.

    Provides access to services like event bus, command dispatcher, and
    a declarative Plugin UI API backed by the service container.
    """

    def __init__(
        self,
        event_bus: EventBus,
        dispatcher: CommandDispatcher,
        container: ServiceContainer,
    ) -> None:
        """
        Initialize the plugin context.

        Args:
            event_bus: EventBus instance
            dispatcher: CommandDispatcher instance
            container: ServiceContainer instance
        """
        self.event_bus = event_bus
        self.dispatcher = dispatcher
        self.container = container

    def get_service(self, name: str) -> Optional[Any]:
        """
        Get a service from the container.

        Args:
            name: Service name

        Returns:
            Service instance or None
        """
        return self.container.get(name)

    @property
    def ui_registry(self) -> UIContributionRegistry:
        """Get the UI contribution registry service."""
        registry = self.container.get('ui_contribution_registry')
        if registry is None:
            raise RuntimeError('UI contribution registry service is not registered')
        return registry

    def register_dock(
        self,
        contribution_id: str,
        title: str,
        widget_factory: Any,
        *,
        area: Any = 'right',
        visible: bool = True,
        closable: bool = True,
        floatable: bool = True,
        movable: bool = True,
        allowed_areas: Any = None,
    ) -> None:
        """Register a dock widget contribution for later application."""
        from ..ui_contribution_registry import DockContribution

        contribution = DockContribution(
            contribution_id=contribution_id,
            title=title,
            widget_factory=widget_factory,
            area=area,
            visible=visible,
            closable=closable,
            floatable=floatable,
            movable=movable,
            allowed_areas=allowed_areas,
        )
        self.ui_registry.register_dock(contribution)

    def register_toolbar_action(
        self,
        contribution_id: str,
        text: str,
        callback: Any,
        *,
        target: str = 'command',
        tooltip: str = '',
        shortcut: str = '',
    ) -> None:
        """Register a toolbar action contribution for later application."""
        from ..ui_contribution_registry import ToolbarActionContribution

        contribution = ToolbarActionContribution(
            contribution_id=contribution_id,
            text=text,
            callback=callback,
            target=target,
            tooltip=tooltip,
            shortcut=shortcut,
        )
        self.ui_registry.register_toolbar_action(contribution)

    def register_menu_action(
        self,
        contribution_id: str,
        menu_path: str,
        text: str,
        callback: Any,
        *,
        tooltip: str = '',
        shortcut: str = '',
    ) -> None:
        """Register a menu action contribution for later application."""
        from ..ui_contribution_registry import MenuActionContribution

        contribution = MenuActionContribution(
            contribution_id=contribution_id,
            menu_path=menu_path,
            text=text,
            callback=callback,
            tooltip=tooltip,
            shortcut=shortcut,
        )
        self.ui_registry.register_menu_action(contribution)
