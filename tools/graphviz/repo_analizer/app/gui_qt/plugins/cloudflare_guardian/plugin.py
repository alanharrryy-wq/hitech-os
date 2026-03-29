from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QWidget

from app.gui_qt.plugins.plugin_base import Plugin, PluginContext

from .guardian_widget import CloudflareGuardianDeck


class CloudflareGuardianDeckPlugin(Plugin):
    """Graph-side Cloudflare Guardian diagnostics hosted under the CloudflareGuardian tool id."""

    name = 'cloudflare_guardian'
    version = '0.7.0'
    description = 'Cloudflare Guardian diagnostics deck for the Graph group.'
    author = 'OpenAI'

    DOCK_ID = 'cloudflare_guardian.dock'

    def __init__(self) -> None:
        super().__init__()
        self.context: Optional[PluginContext] = None
        self._dock_widget: Optional[CloudflareGuardianDeck] = None

    def initialize(self, context: PluginContext) -> None:
        self.context = context
        context.register_safe_dock(
            contribution_id=self.DOCK_ID,
            title='Cloudflare Guardian Diagnostics',
            widget_factory=self._create_dock_widget,
            area='right',
            visible=True,
            object_name='cloudflare_guardianDockSurface',
            visual_role='plugin-dock-root',
            visual_tier='themed',
        )
        context.logger.info('Cloudflare Guardian diagnostics registered its dock contribution')

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
        shell = CloudflareGuardianDeck(parent)
        shell.bind_plugin_context(self.context)
        shell.refresh_from_state()
        self._dock_widget = shell
        return shell

    @staticmethod
    def _resolve_parent(args, kwargs):
        if args:
            return args[0]
        return kwargs.get('parent')


PluginImplementation = CloudflareGuardianDeckPlugin


