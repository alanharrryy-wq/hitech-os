
from __future__ import annotations

import json
from typing import Any

from PySide6.QtWidgets import QFrame, QLabel, QPlainTextEdit, QVBoxLayout, QWidget

from visuals.effects.shadow import apply_shadow


class JsonViewer(QFrame):
    def __init__(self, parent: QWidget | None = None, *, title: str = "Structured payload") -> None:
        super().__init__(parent)
        self.setProperty("card", "muted")
        apply_shadow(self, blur=14.0, y_offset=5.0, alpha=10)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        heading = QLabel(title, self)
        heading.setProperty("role", "section")
        layout.addWidget(heading)

        self.editor = QPlainTextEdit(self)
        self.editor.setReadOnly(True)
        self.editor.setMinimumHeight(180)
        layout.addWidget(self.editor, 1)

    def set_payload(self, payload: Any) -> None:
        try:
            rendered = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
        except TypeError:
            rendered = json.dumps(str(payload), indent=2, ensure_ascii=False)
        self.editor.setPlainText(rendered)
