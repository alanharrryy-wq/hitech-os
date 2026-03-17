from __future__ import annotations

"""
Runtime validation plugin for the installed Plugin UI API.

Registers:
- 1 dock widget
- 1 toolbar action
- 1 menu action

Design goals:
- self-contained
- real runtime asset
- no direct host mutation
- uses the actual PluginContext API already present in plugin_base.py
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Ensure "app" package imports work even if the loader falls back to file-based load.
_THIS_FILE = Path(__file__).resolve()
_APP_ROOT = _THIS_FILE.parents[3]
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.gui_qt.plugins.plugin_base import Plugin, PluginContext

LOGGER = logging.getLogger(__name__)


class DemoUIValidationPlugin(Plugin):
    """
    Minimal but real plugin used to validate Plugin UI API runtime wiring.
    """

    name = "demo_ui_validation"
    version = "1.0.0"
    description = "Validates dock, toolbar and menu plugin contributions at runtime."
    author = "OpenAI"

    DOCK_ID = "demo_ui_validation.dock"
    DOCK_TITLE = "Demo UI Validation"

    TOOLBAR_ACTION_ID = "demo_ui_validation.toolbar_action"
    TOOLBAR_TEXT = "Demo Ping"

    MENU_ACTION_ID = "demo_ui_validation.menu_action"
    MENU_PATH = "Plugins"
    MENU_TEXT = "Demo UI Validation"

    def __init__(self) -> None:
        super().__init__()
        self.context: Optional[PluginContext] = None
        self._dock_widget: Optional[QWidget] = None
        self._status_label: Optional[QLabel] = None
        self._counter_label: Optional[QLabel] = None
        self._activation_count = 0
        self._ui_registered = False

    def initialize(self, context: PluginContext) -> None:
        self.context = context

        if self._ui_registered:
            return

        context.register_dock(
            contribution_id=self.DOCK_ID,
            title=self.DOCK_TITLE,
            widget_factory=self._create_dock_widget,
            area="right",
            visible=True,
        )

        context.register_toolbar_action(
            contribution_id=self.TOOLBAR_ACTION_ID,
            text=self.TOOLBAR_TEXT,
            callback=self._on_toolbar_action,
            tooltip="Trigger the demo plugin toolbar validation action.",
        )

        context.register_menu_action(
            contribution_id=self.MENU_ACTION_ID,
            menu_path=self.MENU_PATH,
            text=self.MENU_TEXT,
            callback=self._on_menu_action,
            tooltip="Trigger the demo plugin menu validation action.",
        )

        self._ui_registered = True
        self._log_info("Demo UI Validation plugin registered dock, toolbar and menu contributions.")

    def shutdown(self) -> None:
        super().shutdown()
        self._ui_registered = False
        self._dock_widget = None
        self._status_label = None
        self._counter_label = None

    def _create_dock_widget(self, *args, **kwargs) -> QWidget:
        if self._dock_widget is not None:
            return self._dock_widget

        parent = kwargs.get("parent")
        if parent is None and args:
            candidate = args[0]
            if isinstance(candidate, QWidget):
                parent = candidate

        root = QWidget(parent)
        root.setObjectName(self.DOCK_ID)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("Plugin UI API runtime validation")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title.setStyleSheet("font-weight: 600;")

        description = QLabel(
            "Este dock confirma que el plugin demo puede registrar UI real sin tocar el host directo."
        )
        description.setWordWrap(True)

        self._status_label = QLabel("Estado: listo")
        self._counter_label = QLabel("Activaciones: 0")

        buttons_row = QHBoxLayout()

        toolbar_btn = QPushButton("Simular toolbar")
        toolbar_btn.clicked.connect(self._on_toolbar_action)

        menu_btn = QPushButton("Simular menu")
        menu_btn.clicked.connect(self._on_menu_action)

        buttons_row.addWidget(toolbar_btn)
        buttons_row.addWidget(menu_btn)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self._status_label)
        layout.addWidget(self._counter_label)
        layout.addLayout(buttons_row)
        layout.addStretch(1)

        self._dock_widget = root
        return root

    def _on_toolbar_action(self, *args, **kwargs) -> None:
        self._mark_activation("toolbar")
        self._show_message(
            "Toolbar action OK",
            "La accion del toolbar del plugin demo respondio bien.",
        )

    def _on_menu_action(self, *args, **kwargs) -> None:
        self._mark_activation("menu")
        self._show_message(
            "Menu action OK",
            "La accion de menu del plugin demo respondio bien.",
        )

    def _mark_activation(self, source: str) -> None:
        self._activation_count += 1

        if self._status_label is not None:
            self._status_label.setText(f"Estado: ultimo disparo desde {source}")

        if self._counter_label is not None:
            self._counter_label.setText(f"Activaciones: {self._activation_count}")

        self._log_info(f"Demo UI Validation plugin action fired from {source}.")

    def _show_message(self, title: str, text: str) -> None:
        parent = self._dock_widget if isinstance(self._dock_widget, QWidget) else None
        QMessageBox.information(parent, title, text)

    def _log_info(self, message: str) -> None:
        LOGGER.info(message)

        if self.context is None:
            return

        context_logger = getattr(self.context, "logger", None)
        if context_logger is None:
            return

        for method_name in ("info", "log", "debug"):
            method = getattr(context_logger, method_name, None)
            if callable(method):
                try:
                    method(message)
                    return
                except Exception:
                    continue


PLUGIN_CLASS = DemoUIValidationPlugin
plugin_class = DemoUIValidationPlugin
PluginImplementation = DemoUIValidationPlugin


def create_plugin(*args, **kwargs) -> DemoUIValidationPlugin:
    return DemoUIValidationPlugin()