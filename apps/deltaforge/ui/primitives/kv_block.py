from __future__ import annotations

from typing import Optional, Sequence, Tuple

from PySide6 import QtCore, QtWidgets


KVItem = Tuple[str, str]


class KVBlock(QtWidgets.QFrame):
    def __init__(self, items: Optional[Sequence[KVItem]] = None, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName('KVBlock')
        self._layout = QtWidgets.QGridLayout(self)
        self._layout.setContentsMargins(14, 14, 14, 14)
        self._layout.setHorizontalSpacing(18)
        self._layout.setVerticalSpacing(10)
        self._layout.setColumnStretch(1, 1)
        if items:
            self.set_items(items)

    def clear(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def set_items(self, items: Sequence[KVItem]) -> None:
        self.clear()
        for row, (key, value) in enumerate(items):
            key_label = QtWidgets.QLabel(key, self)
            key_label.setObjectName('KeyLabel')
            key_label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

            value_label = QtWidgets.QLabel(value, self)
            value_label.setObjectName('ValueLabel')
            value_label.setWordWrap(True)
            value_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

            self._layout.addWidget(key_label, row, 0)
            self._layout.addWidget(value_label, row, 1)
