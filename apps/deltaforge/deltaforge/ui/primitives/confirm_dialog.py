from __future__ import annotations

from typing import Optional

from PySide6 import QtWidgets

from deltaforge.ui.primitives.buttons import CommandButton


class ConfirmDialog(QtWidgets.QDialog):
    def __init__(
        self,
        title: str = 'Confirm action',
        body: str = 'Please confirm to continue.',
        confirm_text: str = 'Confirm',
        cancel_text: str = 'Cancel',
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = QtWidgets.QFrame(self)
        card.setObjectName('ConfirmDialogCard')
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(14)

        self._title = QtWidgets.QLabel(title, card)
        self._title.setObjectName('DialogTitle')

        self._body = QtWidgets.QLabel(body, card)
        self._body.setObjectName('DialogBody')
        self._body.setWordWrap(True)

        actions = QtWidgets.QHBoxLayout()
        actions.addStretch(1)

        self.cancel_button = CommandButton(cancel_text, variant='ghost', parent=card)
        self.confirm_button = CommandButton(confirm_text, variant='primary', parent=card)

        self.cancel_button.clicked.connect(self.reject)
        self.confirm_button.clicked.connect(self.accept)

        actions.addWidget(self.cancel_button)
        actions.addWidget(self.confirm_button)

        card_layout.addWidget(self._title)
        card_layout.addWidget(self._body)
        card_layout.addLayout(actions)
        root.addWidget(card)

    def set_title(self, title: str) -> None:
        self._title.setText(title)
        self.setWindowTitle(title)

    def set_body(self, body: str) -> None:
        self._body.setText(body)

    def set_confirm_text(self, text: str) -> None:
        self.confirm_button.setText(text)

    def set_cancel_text(self, text: str) -> None:
        self.cancel_button.setText(text)
