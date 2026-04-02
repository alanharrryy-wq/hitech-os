from __future__ import annotations

from typing import Optional

from PySide6 import QtCore, QtWidgets


class BusyDialog(QtWidgets.QDialog):
    def __init__(
        self,
        title: str = 'Please wait',
        body: str = 'The operation is in progress.',
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(360)

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = QtWidgets.QFrame(self)
        card.setObjectName('BusyDialogCard')
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(12)

        self._title = QtWidgets.QLabel(title, card)
        self._title.setObjectName('DialogTitle')
        self._body = QtWidgets.QLabel(body, card)
        self._body.setObjectName('DialogBody')
        self._body.setWordWrap(True)

        self._progress = QtWidgets.QProgressBar(card)
        self._progress.setObjectName('BusyProgress')
        self._progress.setTextVisible(False)
        self._progress.setRange(0, 0)

        card_layout.addWidget(self._title)
        card_layout.addWidget(self._body)
        card_layout.addWidget(self._progress)
        root.addWidget(card)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

    def set_title(self, title: str) -> None:
        self._title.setText(title)
        self.setWindowTitle(title)

    def set_body(self, body: str) -> None:
        self._body.setText(body)
