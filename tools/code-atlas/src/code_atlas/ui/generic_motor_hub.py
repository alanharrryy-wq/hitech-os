"""Generic, profile-driven Motor Hub for Code Atlas.

The dialog renders whatever motors are present in the explicit Motor Registry.
It does not assume any product, operating system, drive, port, external tool,
or surface taxonomy.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from code_atlas.motors.registry import grouped_motor_registry
from code_atlas.motors.results import default_output_root, find_latest_fail_zip, find_latest_result_zip
from code_atlas.motors.runner import MotorProcessRunner
from code_atlas.motors.specs import MotorSpec


_STYLE = """
QDialog { background: #111822; color: #eef7ff; }
QFrame#hero { background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.14); border-radius: 18px; }
QFrame#group { background: rgba(255,255,255,0.045); border: 1px solid rgba(255,255,255,0.10); border-radius: 15px; }
QLabel#title { font-size: 22px; font-weight: 700; }
QLabel#groupTitle { font-size: 15px; font-weight: 700; }
QLabel#muted { color: rgba(235,247,255,0.70); }
QPushButton { min-height: 34px; border-radius: 11px; padding: 6px 12px; background: rgba(154,221,255,0.13); border: 1px solid rgba(176,230,255,0.22); color: #f5fbff; }
QPushButton:hover { background: rgba(154,221,255,0.22); }
QPushButton:disabled { color: rgba(245,251,255,0.38); background: rgba(255,255,255,0.04); }
QPlainTextEdit { background: rgba(2,8,16,0.72); border: 1px solid rgba(255,255,255,0.10); border-radius: 13px; padding: 8px; color: #dff6ff; }
"""


class MotorHubDialog(QDialog):
    """Neutral Motor Hub backed only by the explicit registry/profile."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Code Atlas Motor Hub")
        self.resize(920, 720)
        self.setStyleSheet(_STYLE)
        self._runner = MotorProcessRunner(self)
        self._buttons: list[QPushButton] = []
        self._output_root = default_output_root()
        self._build_ui()
        self._wire_runner()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        hero = QFrame()
        hero.setObjectName("hero")
        hero_layout = QVBoxLayout(hero)
        title = QLabel("Code Atlas Motor Hub")
        title.setObjectName("title")
        subtitle = QLabel("Explicit registry only. No product or workstation assumptions are selected by default.")
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)
        root.addWidget(hero)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        host = QWidget()
        groups_layout = QVBoxLayout(host)
        groups_layout.setContentsMargins(0, 0, 0, 0)
        groups_layout.setSpacing(10)

        groups = grouped_motor_registry()
        if not groups:
            empty = QFrame()
            empty.setObjectName("group")
            layout = QVBoxLayout(empty)
            label = QLabel("No motors configured")
            label.setObjectName("groupTitle")
            note = QLabel("Set CODE_ATLAS_MOTOR_REGISTRY or select a project profile with metadata.motorRegistry.")
            note.setObjectName("muted")
            note.setWordWrap(True)
            layout.addWidget(label)
            layout.addWidget(note)
            groups_layout.addWidget(empty)
        else:
            for group_name, specs in groups.items():
                groups_layout.addWidget(self._group_widget(group_name, specs))
        groups_layout.addStretch(1)
        scroll.setWidget(host)
        root.addWidget(scroll, 1)

        self._console = QPlainTextEdit()
        self._console.setReadOnly(True)
        self._console.setMaximumBlockCount(5000)
        self._console.setPlaceholderText("Motor output")
        root.addWidget(self._console, 1)

        actions = QHBoxLayout()
        actions.addWidget(self._action_button("Open output", lambda: self._open_path(self._output_root)))
        actions.addWidget(self._action_button("Open latest result", self._open_latest_result))
        actions.addWidget(self._action_button("Open latest failure", self._open_latest_fail))
        actions.addStretch(1)
        close = self._action_button("Close", self.close)
        actions.addWidget(close)
        root.addLayout(actions)

        self._status = QLabel("Ready")
        self._status.setObjectName("muted")
        root.addWidget(self._status)

    def _group_widget(self, group_name: str, specs: list[MotorSpec]) -> QFrame:
        frame = QFrame()
        frame.setObjectName("group")
        layout = QVBoxLayout(frame)
        label = QLabel(group_name)
        label.setObjectName("groupTitle")
        layout.addWidget(label)
        for spec in specs:
            row = QHBoxLayout()
            button = self._action_button(spec.label, lambda checked=False, item=spec: self._start(item))
            self._buttons.append(button)
            row.addWidget(button)
            description = QLabel(spec.description or spec.motor_id)
            description.setObjectName("muted")
            description.setWordWrap(True)
            row.addWidget(description, 1)
            layout.addLayout(row)
        return frame

    def _action_button(self, text: str, callback) -> QPushButton:
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(callback)
        return button

    def _wire_runner(self) -> None:
        self._runner.started.connect(self._on_started)
        self._runner.output_ready.connect(self._on_output)
        self._runner.finished.connect(self._on_finished)
        self._runner.failed_to_start.connect(self._on_failed)

    def _start(self, spec: MotorSpec) -> None:
        try:
            self._runner.start(spec)
        except Exception as exc:
            QMessageBox.warning(self, "Motor Hub", str(exc))

    def _on_started(self, spec: MotorSpec) -> None:
        self._status.setText(f"Running: {spec.label}")
        self._console.appendPlainText(f"\n> {spec.command_preview()}\n")
        for button in self._buttons:
            button.setEnabled(False)

    def _on_output(self, channel: str, text: str) -> None:
        prefix = "[stderr] " if channel == "stderr" else ""
        self._console.appendPlainText(prefix + text.rstrip())

    def _on_finished(self, spec: MotorSpec, exit_code: int, exit_status: str) -> None:
        self._status.setText(f"Finished: {spec.label} | exit={exit_code} | {exit_status}")
        for button in self._buttons:
            button.setEnabled(True)

    def _on_failed(self, spec: MotorSpec, error: str) -> None:
        self._status.setText(f"Failed to start: {spec.label}")
        for button in self._buttons:
            button.setEnabled(True)
        QMessageBox.warning(self, "Motor Hub", error)

    def _open_latest_result(self) -> None:
        path = find_latest_result_zip(self._output_root)
        if path is None:
            QMessageBox.information(self, "Motor Hub", f"No result ZIP found under {self._output_root}.")
            return
        self._open_path(path)

    def _open_latest_fail(self) -> None:
        path = find_latest_fail_zip(self._output_root)
        if path is None:
            QMessageBox.information(self, "Motor Hub", f"No failure ZIP found under {self._output_root}.")
            return
        self._open_path(path)

    @staticmethod
    def _open_path(path: Path) -> None:
        target = path if path.exists() else path.parent
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(target.resolve())))
