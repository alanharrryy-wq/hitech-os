from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QListWidget, QPlainTextEdit, QVBoxLayout, QWidget

from domain.models import SessionWorkspace
from ui.primitives import SectionCard


class LeftPane(QWidget):
    ops_text_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._updating = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(10)

        self.scope_card = SectionCard("Scope / Targets", "Archivos y carpetas bajo control")
        self.scope_list = QListWidget()
        self.scope_card.content_layout.addWidget(self.scope_list)
        self.scope_hint = QLabel("Sin scope cargado")
        self.scope_hint.setProperty("role", "hint")
        self.scope_card.content_layout.addWidget(self.scope_hint)

        self.ops_card = SectionCard("Ops Document", "Declarativo y versionable", alt=True)
        self.ops_editor = QPlainTextEdit()
        self.ops_editor.setPlaceholderText("Describe aquí operaciones declarativas...")
        self.ops_editor.textChanged.connect(self._on_ops_text_changed)
        self.ops_path_hint = QLabel("Ops source: -")
        self.ops_path_hint.setProperty("role", "hint")
        self.ops_card.content_layout.addWidget(self.ops_path_hint)
        self.ops_card.content_layout.addWidget(self.ops_editor)

        outer.addWidget(self.scope_card, 1)
        outer.addWidget(self.ops_card, 1)

    def set_session(self, session: SessionWorkspace | None) -> None:
        self._updating = True
        self.scope_list.clear()

        if session is None:
            self.scope_hint.setText("Sin scope cargado")
            self.ops_editor.setPlainText("")
            self.ops_path_hint.setText("Ops source: -")
            self._updating = False
            return

        for target in session.scope.targets:
            self.scope_list.addItem(target)

        self.scope_hint.setText(f"{session.scope.count} target(s)")
        self.ops_editor.setPlainText(session.ops_document.text)

        source = session.ops_document.source_path
        if source:
            source_name = Path(source).name
            self.ops_path_hint.setText(f"Ops source: {source_name}")
        else:
            self.ops_path_hint.setText("Ops source: inline")

        self._updating = False

    def ops_text(self) -> str:
        return self.ops_editor.toPlainText()

    def focus_scope(self) -> None:
        self.scope_list.setFocus()

    def _on_ops_text_changed(self) -> None:
        if self._updating:
            return
        self.ops_text_changed.emit(self.ops_editor.toPlainText())
