from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from deltaforge.ui.widgets.command_bar import CommandBar
from deltaforge.ui.widgets.session_tabs import SessionTabs
from deltaforge.ui.widgets.session_workspace import SessionWorkspace
from deltaforge.ui.widgets.status_widgets import StatusStrip
from deltaforge.ui.window.interop import ControllerBridge, WorkspaceFacadeBridge


@dataclass(slots=True)
class WindowBindings:
    workspace_facade: Any
    command_controller: Any
    initial_theme: str = 'dark'


class DeltaForgeMainWindow(QMainWindow):
    def __init__(self, bindings: WindowBindings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.bindings = bindings
        self._facade_bridge = WorkspaceFacadeBridge(bindings.workspace_facade)
        self._controller_bridge = ControllerBridge(bindings.command_controller)
        self.setObjectName('DeltaForgeMainWindow')
        self.setWindowTitle('DeltaForge')
        self.resize(1460, 940)

        self.shell = QWidget(self)
        self.shell.setObjectName('DeltaForgeShell')
        self.setCentralWidget(self.shell)

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
