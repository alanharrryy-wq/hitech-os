from __future__ import annotations

from dataclasses import dataclass
import sys
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QMainWindow, QVBoxLayout, QWidget

from ui.widgets.command_bar import CommandBar
from ui.widgets.session_tabs import SessionTabs
from ui.widgets.session_workspace import SessionWorkspace
from ui.widgets.status_widgets import StatusStrip
from ui.window.interop import ControllerBridge, WorkspaceFacadeBridge

_REPO_ROOT = Path(__file__).resolve().parents[4]
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)

from forgeos.shared.pyside6_glass.scene import (
    build_glass_dialog_scene as shared_build_glass_dialog_scene,
)
from ui.adapters.glass_framework_adapter import configure_deltaforge_glass_framework


@dataclass(slots=True)
class WindowBindings:
    workspace_facade: Any
    command_controller: Any
    initial_theme: str = 'dark'


class DeltaForgeMainWindow(QMainWindow):
    def __init__(self, bindings: WindowBindings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        configure_deltaforge_glass_framework()
        self.bindings = bindings
        self._facade_bridge = WorkspaceFacadeBridge(bindings.workspace_facade)
        self._controller_bridge = ControllerBridge(bindings.command_controller)
        self.setObjectName('DeltaForgeMainWindow')
        self.setWindowTitle('DeltaForge')
        self.resize(1460, 940)

        self.shell_host = QWidget(self)
        self.shell_host.setObjectName('DeltaForgeShell')
        self.setCentralWidget(self.shell_host)

        outer, content_layer, self._glass_backdrop = shared_build_glass_dialog_scene(
            self.shell_host,
            margins=(10, 10, 10, 10),
            apply_stylesheet=False,
        )
        outer.setSpacing(0)

        stage_layout = QVBoxLayout(content_layer)
        stage_layout.setContentsMargins(8, 8, 8, 8)
        stage_layout.setSpacing(0)

        self.shell = QFrame(content_layer)
        self.shell.setObjectName('Shell')
        self.shell.setProperty('variant', 'selector')
        stage_layout.addWidget(self.shell)

        layout = QVBoxLayout(self.shell)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.session_tabs = SessionTabs(self.shell)
        self.command_bar = CommandBar(self.shell)
        self.workspace = SessionWorkspace(self.shell)
        self.status_strip = StatusStrip(self.shell)

        layout.addWidget(self.session_tabs, 0, Qt.AlignTop)
        layout.addWidget(self.command_bar, 0, Qt.AlignTop)
        layout.addWidget(self.workspace, 1)
        layout.addWidget(self.status_strip, 0, Qt.AlignBottom)

        self._wire_signals()
        self.refresh_from_projection()

    def _wire_signals(self) -> None:
        controller = self._controller_bridge
        self.session_tabs.createRequested.connect(lambda: self._call(controller, 'create_session'))
        self.session_tabs.closeRequested.connect(lambda session_id: self._call(controller, 'close_session', session_id))
        self.session_tabs.currentChanged.connect(lambda session_id: self._call(controller, 'select_session', session_id))

        self.command_bar.browseRequested.connect(lambda: self._call(controller, 'browse_root_dir'))
        self.command_bar.validateRequested.connect(lambda: self._call(controller, 'validate_active'))
        self.command_bar.planRequested.connect(lambda: self._call(controller, 'plan_active'))
        self.command_bar.applyRequested.connect(lambda: self._call(controller, 'apply_active'))
        self.command_bar.rollbackRequested.connect(lambda: self._call(controller, 'rollback_active'))
        self.command_bar.refreshRequested.connect(lambda: self._call(controller, 'refresh_active'))

        self.workspace.opSelected.connect(lambda payload: self._call(controller, 'select_op', payload))
        self.workspace.targetSelected.connect(lambda payload: self._call(controller, 'select_target', payload))

    def _call(self, target: Any, name: str, *args: Any) -> None:
        callback = getattr(target, name, None)
        if not callable(callback):
            return
        result = callback(*args)
        if result is not False:
            self.refresh_from_projection()

    def refresh_from_projection(self) -> None:
        facade = self._facade_bridge
        tabs = self._maybe_call(facade, 'get_session_tabs_projection', [])
        active_session_id = self._maybe_call(facade, 'get_active_session_id', None)
        command_bar_projection = self._maybe_call(facade, 'get_command_bar_projection', {})
        workspace_projection = self._maybe_call(facade, 'get_workspace_projection', {})
        status_projection = self._maybe_call(facade, 'get_status_projection', {})

        self.session_tabs.set_tabs(tabs or [], active_session_id=active_session_id)
        self.command_bar.set_state(command_bar_projection or {})
        self.workspace.set_projection(workspace_projection or {})
        self.status_strip.set_summary(status_projection or {})

    def _maybe_call(self, target: Any, name: str, default: Any) -> Any:
        callback = getattr(target, name, None)
        if callable(callback):
            return callback()
        return default
