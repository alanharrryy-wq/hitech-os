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
        self._logger = _PluginContextLogger(container)

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

    @property
    def logger(self):
        """Logger shim for plugins (`info`, `warning`, `debug`, `log`)."""
        return self._logger

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

        self._require_non_empty('contribution_id', contribution_id)
        self._require_non_empty('title', title)
        if not callable(widget_factory):
            raise ValueError('widget_factory must be callable')

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

    def register_safe_dock(
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
        object_name: str = '',
        visual_role: str = 'plugin-dock-root',
        visual_tier: str = 'themed',
    ) -> None:
        """
        Register a dock using a safer default wrapper.

        The wrapper guarantees:
        - callable validation
        - non-empty IDs/titles
        - dock content visual markers for runtime integration
        - deterministic objectName when possible
        """
        self._require_non_empty('contribution_id', contribution_id)
        self._require_non_empty('title', title)
        if not callable(widget_factory):
            raise ValueError('widget_factory must be callable')

        safe_object_name = object_name.strip() or f"plugin_surface_{self._sanitize_ui_id(contribution_id)}"

        def safe_factory(parent):
            widget = self._call_widget_factory(widget_factory, parent)
            if widget is None:
                raise RuntimeError(
                    f"Dock widget factory returned None for contribution '{contribution_id}'"
                )
            try:
                if hasattr(widget, 'objectName') and hasattr(widget, 'setObjectName'):
                    if not widget.objectName():
                        widget.setObjectName(safe_object_name)
                if hasattr(widget, 'setProperty'):
                    widget.setProperty('dockContentRoot', True)
                    if visual_role and not widget.property('visualRole'):
                        widget.setProperty('visualRole', visual_role)
                    if visual_tier and not widget.property('visualTier'):
                        widget.setProperty('visualTier', visual_tier)
            except Exception:
                pass
            return widget

        self.register_dock(
            contribution_id=contribution_id,
            title=title,
            widget_factory=safe_factory,
            area=area,
            visible=visible,
            closable=closable,
            floatable=floatable,
            movable=movable,
            allowed_areas=allowed_areas,
        )

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

        self._require_non_empty('contribution_id', contribution_id)
        self._require_non_empty('text', text)
        if not callable(callback):
            raise ValueError('callback must be callable')

        contribution = ToolbarActionContribution(
            contribution_id=contribution_id,
            text=text,
            callback=callback,
            target=target,
            tooltip=tooltip,
            shortcut=shortcut,
        )
        self.ui_registry.register_toolbar_action(contribution)

    def register_safe_toolbar_action(
        self,
        contribution_id: str,
        text: str,
        callback: Any,
        *,
        target: str = 'command',
        tooltip: str = '',
        shortcut: str = '',
    ) -> None:
        """Register toolbar action with safe defaults and validation."""
        safe_tooltip = tooltip.strip() or f"Run '{text}' action."
        self.register_toolbar_action(
            contribution_id=contribution_id,
            text=text,
            callback=callback,
            target=target,
            tooltip=safe_tooltip,
            shortcut=shortcut,
        )

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

        self._require_non_empty('contribution_id', contribution_id)
        self._require_non_empty('menu_path', menu_path)
        self._require_non_empty('text', text)
        if not callable(callback):
            raise ValueError('callback must be callable')

        contribution = MenuActionContribution(
            contribution_id=contribution_id,
            menu_path=menu_path,
            text=text,
            callback=callback,
            tooltip=tooltip,
            shortcut=shortcut,
        )
        self.ui_registry.register_menu_action(contribution)

    def register_safe_menu_action(
        self,
        contribution_id: str,
        menu_path: str,
        text: str,
        callback: Any,
        *,
        tooltip: str = '',
        shortcut: str = '',
    ) -> None:
        """Register menu action with safe defaults and validation."""
        safe_tooltip = tooltip.strip() or f"Run '{text}' action."
        self.register_menu_action(
            contribution_id=contribution_id,
            menu_path=menu_path,
            text=text,
            callback=callback,
            tooltip=safe_tooltip,
            shortcut=shortcut,
        )

    def _require_non_empty(self, field_name: str, value: Any) -> None:
        if not str(value or '').strip():
            raise ValueError(f'{field_name} cannot be empty')

    def _sanitize_ui_id(self, value: str) -> str:
        sanitized = ''.join(ch if ch.isalnum() else '_' for ch in value.strip().lower())
        return sanitized.strip('_') or 'plugin'

    def _call_widget_factory(self, factory: Any, parent: Any):
        try:
            return factory(parent)
        except TypeError:
            pass

        try:
            return factory(parent=parent)
        except TypeError:
            pass

        return factory()


class _PluginContextLogger:
    """Minimal logger adapter exposed as `PluginContext.logger`."""

    def __init__(self, container: ServiceContainer) -> None:
        self._container = container

    def debug(self, message: str) -> None:
        self._emit('debug', message)

    def info(self, message: str) -> None:
        self._emit('info', message)

    def warning(self, message: str) -> None:
        self._emit('warning', message)

    def log(self, message: str) -> None:
        self._emit('log', message)

    def _emit(self, level: str, message: str) -> None:
        diagnostics = self._container.get('runtime_diagnostics')
        if diagnostics is not None and hasattr(diagnostics, 'trace'):
            try:
                diagnostics.trace(
                    'plugin-context',
                    f'{level}: {message}',
                )
            except Exception:
                pass

        main_window = self._container.get('main_window')
        logger = getattr(main_window, 'log', None)
        if callable(logger):
            try:
                logger(f"[plugin-context:{level}] {message}")
                return
            except Exception:
                pass
        print(f"[plugin-context:{level}] {message}")
