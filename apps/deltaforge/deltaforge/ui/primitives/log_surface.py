from __future__ import annotations

from typing import Optional, Sequence

from PySide6 import QtGui, QtWidgets


class LogSurface(QtWidgets.QFrame):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName('LogSurface')
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self._viewport = QtWidgets.QPlainTextEdit(self)
        self._viewport.setObjectName('LogViewport')
        self._viewport.setReadOnly(True)
        self._viewport.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

        font = QtGui.QFont('Consolas')
        font.setStyleHint(QtGui.QFont.Monospace)
        self._viewport.setFont(font)

        layout.addWidget(self._viewport)

    def set_lines(self, lines: Sequence[str]) -> None:
        self._viewport.setPlainText('\n'.join(lines))

    def append_line(self, line: str) -> None:
        self._viewport.appendPlainText(line)

    def clear(self) -> None:
        self._viewport.clear()
