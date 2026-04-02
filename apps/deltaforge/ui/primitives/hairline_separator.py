from __future__ import annotations

from typing import Optional

from PySide6 import QtCore, QtWidgets


class HairlineSeparator(QtWidgets.QFrame):
    def __init__(
        self,
        orientation: QtCore.Qt.Orientation = QtCore.Qt.Horizontal,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName('HairlineSeparator')
        self.set_orientation(orientation)

    def set_orientation(self, orientation: QtCore.Qt.Orientation) -> None:
        if orientation == QtCore.Qt.Vertical:
            self.setFixedWidth(1)
            self.setMinimumHeight(12)
        else:
            self.setFixedHeight(1)
            self.setMinimumWidth(12)
