from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLabel, QMessageBox, QVBoxLayout, QWidget

from app.gui_qt.plugins.plugin_base import Plugin, PluginContext


class ${CLASS_NAME}(Plugin):
    name = "${PLUGIN_ID}"
    version = "0.1.0"
    description = "${DESCRIPTION}"
    author = "${AUTHOR}"

    DOCK_ID = "${PLUGIN_ID}.dock"
    TOOLBAR_ID = "${PLUGIN_ID}.toolbar_action"
    MENU_ID = "${PLUGIN_ID}.menu_action"

    def __init__(self) -> None:
        super().__init__()
        self.context: Optional[PluginContext] = None
        self._dock_widget: Optional[QWidget] = None

    def initialize(self, context: PluginContext) -> None:
        self.context = context
        context.register_safe_dock(
            contribution_id=self.DOCK_ID,
            title="${DISPLAY_NAME}",
            widget_factory=self._create_dock_widget,
            area="right",
            visible=True,
            object_name="${PLUGIN_ID}_dock_surface",
        )
        context.register_safe_toolbar_action(
            contribution_id=self.TOOLBAR_ID,
            text="${DISPLAY_NAME}",
            callback=self._on_toolbar_action,
            tooltip="Run ${DISPLAY_NAME} toolbar action.",
        )
        context.register_safe_menu_action(
            contribution_id=self.MENU_ID,
            menu_path="Plugins",
            text="${DISPLAY_NAME}",
            callback=self._on_menu_action,
            tooltip="Run ${DISPLAY_NAME} menu action.",
        )
        print(f"[OK] Plugin '{self.name}' initialized")

    def _create_dock_widget(self, *args, **kwargs) -> QWidget:
        if self._dock_widget is not None:
            return self._dock_widget

        parent = kwargs.get("parent")
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("${DISPLAY_NAME} runtime dock ready."))
        self._dock_widget = widget
        return widget

    def _on_toolbar_action(self, *args, **kwargs) -> None:
        self._show_message("Toolbar action", "${DISPLAY_NAME} toolbar action fired.")

    def _on_menu_action(self, *args, **kwargs) -> None:
        self._show_message("Menu action", "${DISPLAY_NAME} menu action fired.")

    def _show_message(self, title: str, text: str) -> None:
        parent = self._dock_widget if isinstance(self._dock_widget, QWidget) else None
        QMessageBox.information(parent, title, text)


PluginImplementation = ${CLASS_NAME}
