from __future__ import annotations

from typing import Optional

from PySide6 import QtWidgets


class Chip(QtWidgets.QFrame):
    def __init__(self, text: str = '', parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName('Chip')
        self.setProperty('fill', 'subtle')

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(6)

        self._label = QtWidgets.QLabel(text, self)
        self._label.setObjectName('ChipLabel')
        layout.addWidget(self._label)

    def set_text(self, text: str) -> None:
        self._label.setText(text)

    def set_fill(self, strong: bool) -> None:
        self.setProperty('fill', 'strong' if strong else 'subtle')
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
