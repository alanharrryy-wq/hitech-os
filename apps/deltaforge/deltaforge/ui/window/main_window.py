from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from deltaforge.application.controllers import CommandController, StatusBarController
from deltaforge.application.session_manager import SessionManager
from deltaforge.domain import AppEvent, REQUIRED_EVENT_NAMES
from deltaforge.domain.models import SessionWorkspace
from deltaforge.infrastructure.event_bus import EventBus
from deltaforge.infrastructure.watcher import FileWatcherService
from deltaforge.ui.dialogs import RollbackDialog, show_info, show_warning
from deltaforge.ui.panes import BottomPane, CenterPane, LeftPane, RightPane
from deltaforge.ui.primitives import MainShellFrame
from deltaforge.ui.shortcuts import install_shortcuts
from deltaforge.ui.widgets import CommandBar, SessionTabStrip, WorkstationStatusBar


class DeltaForgeMainWindow(QMainWindow):
    def __init__(
        self,
        *,
        manager: SessionManager,
        event_bus: EventBus,
        watcher: FileWatcherService,
        engine,
        initial_size: tuple[int, int] = (1680, 980),
    ) -> None:
        super().__init__()
        self.setWindowTitle("DeltaForge Console")
        self.resize(*initial_size)
        self.setMinimumSize(1320, 820)

        self._manager = manager
        self._event_bus = event_bus
        self._watcher = watcher

        self.command_bar = CommandBar()
        self.tab_strip = SessionTabStrip()

        self.left_pane = LeftPane()
        self.center_pane = CenterPane()
        self.right_pane = RightPane()
        self.bottom_pane = BottomPane()

        self.status_bar_widget = WorkstationStatusBar()
        self.setStatusBar(self.status_bar_widget)

        self._status_controller = StatusBarController(self.status_bar_widget, self._manager)
        self._command_controller = CommandController(
            ui=self,
            manager=self._manager,
            event_bus=self._event_bus,
            watcher=self._watcher,
            engine=engine,
        )

        self._build_layout()
        self._bind_events()
        self._install_shortcuts()
        self._command_controller.bootstrap()

    def _build_layout(self) -> None:
        shell = MainShellFrame()
        layout = QVBoxLayout(shell)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        layout.addWidget(self.command_bar)
        layout.addWidget(self.tab_strip)

        top_split = QSplitter(Qt.Horizontal)
        top_split.addWidget(self.left_pane)
        top_split.addWidget(self.center_pane)
        top_split.addWidget(self.right_pane)
        top_split.setStretchFactor(0, 2)
        top_split.setStretchFactor(1, 5)
        top_split.setStretchFactor(2, 2)

        main_split = QSplitter(Qt.Vertical)
        main_split.addWidget(top_split)
        main_split.addWidget(self.bottom_pane)
        main_split.setStretchFactor(0, 6)
        main_split.setStretchFactor(1, 3)

        layout.addWidget(main_split, 1)

        container = QWidget()
        root = QVBoxLayout(container)
        root.setContentsMargins(8, 8, 8, 8)
        root.addWidget(shell)
        self.setCentralWidget(container)

    def _bind_events(self) -> None:
        self.command_bar.command_invoked.connect(self._dispatch_command)
        self.tab_strip.session_selected.connect(self._command_controller.activate_session)

        self.left_pane.ops_text_changed.connect(self._command_controller.on_ops_text_changed)
        self.center_pane.plan_item_selected.connect(self.right_pane.show_payload)

        for event_name in REQUIRED_EVENT_NAMES:
            self._event_bus.subscribe(event_name, self._on_bus_event)

    def _install_shortcuts(self) -> None:
        handlers = {
            "new_session": self._command_controller.new_session,
            "clone_session": self._command_controller.clone_session,
            "close_session": self._command_controller.close_session,
            "choose_files": self._command_controller.choose_files,
            "choose_folder": self._command_controller.choose_folder,
            "load_ops": self._command_controller.load_ops,
            "save_ops": self._command_controller.save_ops,
            "refresh": self._command_controller.refresh,
            "validate": self._command_controller.validate,
            "plan": self._command_controller.plan,
            "apply": self._command_controller.apply,
            "rollback": self._command_controller.rollback,
            "focus_left": self.left_pane.focus_scope,
            "focus_center": self.center_pane.focus_panel,
            "focus_right": self.right_pane.focus_panel,
            "focus_bottom": self.bottom_pane.focus_panel,
            "next_session": self._command_controller.next_session,
            "prev_session": self._command_controller.prev_session,
        }
        self._shortcuts = install_shortcuts(self, handlers)

    def _dispatch_command(self, command_id: str) -> None:
        routes = {
            "new_session": self._command_controller.new_session,
            "clone_session": self._command_controller.clone_session,
            "close_session": self._command_controller.close_session,
            "choose_files": self._command_controller.choose_files,
            "choose_folder": self._command_controller.choose_folder,
            "clear_scope": self._command_controller.clear_scope,
            "load_ops": self._command_controller.load_ops,
            "save_ops": self._command_controller.save_ops,
            "validate": self._command_controller.validate,
            "plan": self._command_controller.plan,
            "apply": self._command_controller.apply,
            "rollback": self._command_controller.rollback,
            "refresh": self._command_controller.refresh,
            "open_root": self._command_controller.open_root,
            "settings": self._command_controller.settings,
        }

        callback = routes.get(command_id)
        if callback is not None:
            callback()

    def _on_bus_event(self, event: AppEvent) -> None:
        self.bottom_pane.append_event(event)
        if event.session_id and event.session_id == self._manager.current_session_id:
            self.refresh_ui(self._manager.current())

    # ---- CommandUiBridge implementation ----
    def refresh_ui(self, session: SessionWorkspace | None = None) -> None:
        current = session or self._manager.current()
        self.tab_strip.set_sessions(self._manager.sessions, self._manager.current_session_id)
        self.left_pane.set_session(current)
        self.right_pane.show_session(current)

        if current is None:
            self.center_pane.set_plan_result(None)
            self.center_pane.set_diff_preview(None)
            self.bottom_pane.set_validation(None)
            self.bottom_pane.set_plan(None)
            self.bottom_pane.set_apply(None)
            self.bottom_pane.set_rollback(None)
            self._status_controller.refresh()
            return

        self.center_pane.set_plan_result(current.plan_result)
        self.center_pane.set_diff_preview(current.plan_result.diff_preview if current.plan_result else None)

        self.bottom_pane.set_validation(current.validation_result)
        self.bottom_pane.set_plan(current.plan_result)
        self.bottom_pane.set_apply(current.apply_result)
        self.bottom_pane.set_rollback(current.rollback_result)

        self._status_controller.refresh()

    def pick_files(self) -> list[str]:
        selected, _ = QFileDialog.getOpenFileNames(
            self,
            "Choose File(s)",
            "",
            "All Files (*);;Text Files (*.txt *.md *.json *.yaml *.yml *.py)",
        )
        return selected

    def pick_folder(self) -> str:
        return QFileDialog.getExistingDirectory(self, "Choose Folder")

    def pick_ops_to_load(self) -> str:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Ops",
            "",
            "Ops Files (*.ops *.md *.yaml *.yml *.json *.txt);;All Files (*)",
        )
        return path

    def pick_ops_to_save(self) -> str:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Ops",
            "ops_document.ops",
            "Ops Files (*.ops *.md *.yaml *.yml *.json *.txt);;All Files (*)",
        )
        return path

    def current_ops_text(self) -> str:
        return self.left_pane.ops_text()

    def choose_rollback_token(self, rollback_tokens: list[str]) -> str:
        dialog = RollbackDialog(rollback_tokens, self)
        if dialog.exec() != dialog.Accepted:
            return ""
        return dialog.selected_token

    def show_info(self, message: str) -> None:
        show_info(self, "DeltaForge", message)

    def show_warning(self, message: str) -> None:
        show_warning(self, "DeltaForge", message)

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "DeltaForge", message)

    def open_path(self, path: str) -> None:
        resolved = str(Path(path).expanduser())
        try:
            if hasattr(os, "startfile"):
                os.startfile(resolved)  # type: ignore[attr-defined]
                return

            if sys.platform == "darwin":
                subprocess.Popen(["open", resolved])
            else:
                subprocess.Popen(["xdg-open", resolved])
        except Exception as exc:
            self.show_warning(f"No se pudo abrir la ruta: {exc}")
