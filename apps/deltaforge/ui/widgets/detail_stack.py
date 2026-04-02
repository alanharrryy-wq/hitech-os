from __future__ import annotations

import json

from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget


class DetailStack(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.title = QLabel('Detail', self)
        self.title.setProperty('role', 'surface-title')
        layout.addWidget(self.title)

        self.body = QTextEdit(self)
        self.body.setReadOnly(True)
        self.body.setProperty('readonly', 'true')
        layout.addWidget(self.body, 1)

    def set_detail(self, payload: dict | list | str | None) -> None:
        if payload is None:
            self.body.setPlainText('Select an op or grouped item to inspect detail.')
            return
        if isinstance(payload, str):
            self.body.setPlainText(payload)
            return
        self.body.setPlainText(json.dumps(payload, indent=2, ensure_ascii=False))
