from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QWidget

from app.gui_qt.plugins.plugin_base import Plugin, PluginContext

from .deck_shell import AegisDeckShell


class AegisDeckPlugin(Plugin):
    """Manifest-based plugin entrypoint for the Aegis Deck shell."""

    name = 'aegis_deck'
    version = '0.6.0'
    description = 'Premium, contract-tight dock plugin that hosts the Aegis Deck sibling slices.'
    author = 'OpenAI'

    DOCK_ID = 'aegis_deck.dock'

    def __init__(self) -> None:
        super().__init__()
        self.context: Optional[PluginContext] = None
        self._dock_widget: Optional[AegisDeckShell] = None

    def initialize(self, context: PluginContext) -> None:
        self.context = context
        context.register_safe_dock(
            contribution_id=self.DOCK_ID,
            title='Aegis Deck',
            widget_factory=self._create_dock_widget,
            area='right',
            visible=True,
            object_name='aegisDeckDockSurface',
            visual_role='plugin-dock-root',
            visual_tier='themed',
        )
        context.logger.info('Aegis Deck plugin registered its dock contribution')

    def shutdown(self) -> None:
        if self._dock_widget is not None:
            try:
                self._dock_widget.shutdown()
            except Exception:
                pass
        self._dock_widget = None
        super().shutdown()

    def _create_dock_widget(self, *args, **kwargs) -> QWidget:
        if self._dock_widget is not None:
            self._dock_widget.bind_plugin_context(self.context)
            self._dock_widget.refresh_from_state()
            return self._dock_widget

        parent = self._resolve_parent(args, kwargs)
        shell = AegisDeckShell(parent)
        shell.bind_plugin_context(self.context)
        shell.refresh_from_state()
        self._dock_widget = shell
        return shell

    @staticmethod
    def _resolve_parent(args, kwargs):
        if args:
            return args[0]
        return kwargs.get('parent')


PluginImplementation = AegisDeckPlugin
