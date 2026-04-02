from __future__ import annotations

import json

from PySide6.QtWidgets import QTabWidget, QTextEdit, QVBoxLayout, QWidget


class BottomResultsTabs(QWidget):
    TAB_ORDER = ('events', 'validation', 'plan', 'apply', 'rollback')

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.tabs = QTabWidget(self)
        self.tabs.setDocumentMode(True)
        self._views: dict[str, QTextEdit] = {}
        for name in self.TAB_ORDER:
            view = QTextEdit(self)
            view.setReadOnly(True)
            view.setProperty('readonly', 'true')
            self._views[name] = view
            self.tabs.addTab(view, name.title())
        layout.addWidget(self.tabs)

    def set_payloads(self, payloads: dict | None) -> None:
        payloads = payloads or {}
        for name, view in self._views.items():
            payload = payloads.get(name, '')
            if isinstance(payload, str):
                view.setPlainText(payload)
            else:
                view.setPlainText(json.dumps(payload, indent=2, ensure_ascii=False))
