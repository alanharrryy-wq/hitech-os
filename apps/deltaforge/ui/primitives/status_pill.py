from __future__ import annotations

from typing import Optional

from PySide6 import QtWidgets


class StatusPill(QtWidgets.QFrame):
    def __init__(self, text: str = '', tone: str = 'info', parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName('StatusPill')
        self.setProperty('tone', tone)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(6)

        self._label = QtWidgets.QLabel(text, self)
        self._label.setObjectName('StatusPillLabel')
        layout.addWidget(self._label)

        self.set_tone(tone)

    def set_text(self, text: str) -> None:
        self._label.setText(text)

    def set_tone(self, tone: str) -> None:
        self.setProperty('tone', tone)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
