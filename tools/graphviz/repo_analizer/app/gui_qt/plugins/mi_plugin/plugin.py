from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLabel, QMessageBox, QVBoxLayout, QWidget

from app.gui_qt.plugins.plugin_base import Plugin, PluginContext


class MiPluginPlugin(Plugin):
    name = "mi_plugin"
    version = "0.1.0"
    description = "Plugin de prueba"
    author = "Mi rey"

    DOCK_ID = "mi_plugin.dock"
    TOOLBAR_ID = "mi_plugin.toolbar_action"
    MENU_ID = "mi_plugin.menu_action"

    def __init__(self) -> None:
        super().__init__()
        self.context: Optional[PluginContext] = None
        self._dock_widget: Optional[QWidget] = None

    def initialize(self, context: PluginContext) -> None:
        self.context = context
        context.register_safe_dock(
            contribution_id=self.DOCK_ID,
            title="Mi Plugin",
            widget_factory=self._create_dock_widget,
            area="right",
            visible=True,
            object_name="miPluginDockSurface",
        )
        context.register_safe_toolbar_action(
            contribution_id=self.TOOLBAR_ID,
            text="Mi Plugin",
            callback=self._on_toolbar_action,
            tooltip="Run Mi Plugin toolbar action.",
        )
        context.register_safe_menu_action(
            contribution_id=self.MENU_ID,
            menu_path="Plugins",
            text="Mi Plugin",
            callback=self._on_menu_action,
            tooltip="Run Mi Plugin menu action.",
        )
        print(f"[OK] Plugin '{self.name}' initialized")

    def _create_dock_widget(self, *args, **kwargs) -> QWidget:
        if self._dock_widget is not None:
            return self._dock_widget

        parent = kwargs.get("parent")
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Mi Plugin runtime dock ready."))
        self._dock_widget = widget
        return widget

    def _on_toolbar_action(self, *args, **kwargs) -> None:
        self._show_message("Toolbar action", "Mi Plugin toolbar action fired.")

    def _on_menu_action(self, *args, **kwargs) -> None:
        self._show_message("Menu action", "Mi Plugin menu action fired.")

    def _show_message(self, title: str, text: str) -> None:
        parent = self._dock_widget if isinstance(self._dock_widget, QWidget) else None
        QMessageBox.information(parent, title, text)


PluginImplementation = MiPluginPlugin
