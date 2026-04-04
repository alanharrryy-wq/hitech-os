from __future__ import annotations

from typing import Iterable, Optional, Sequence

from PySide6 import QtCore, QtWidgets


class ListSurface(QtWidgets.QListWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName('ListSurface')
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(False)
        self.setUniformItemSizes(False)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def set_items(self, items: Sequence[str]) -> None:
        self.clear()
        for text in items:
            self.addItem(text)

    def add_items(self, items: Iterable[str]) -> None:
        for text in items:
            self.addItem(text)
