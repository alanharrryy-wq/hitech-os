from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from PySide6 import QtWidgets

from ui.primitives.buttons import CommandButton

_REPO_ROOT = Path(__file__).resolve().parents[4]
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)

from forgeos.shared.pyside6_glass.scene import (
    build_glass_dialog_scene as shared_build_glass_dialog_scene,
)


class ConfirmDialog(QtWidgets.QDialog):
    def __init__(
        self,
        title: str = 'Confirm action',
        body: str = 'Please confirm to continue.',
        confirm_text: str = 'Confirm',
        cancel_text: str = 'Cancel',
        confirm_variant: str = 'primary',
        show_cancel: bool = True,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setObjectName('DeltaForgeConfirmDialog')

        outer, content_layer, self._glass_backdrop = shared_build_glass_dialog_scene(
            self,
            margins=(10, 10, 10, 10),
            apply_stylesheet=False,
            variant='progress',
        )
        outer.setSpacing(0)

        stage_layout = QtWidgets.QVBoxLayout(content_layer)
        stage_layout.setContentsMargins(8, 8, 8, 8)
        stage_layout.setSpacing(0)

        shell = QtWidgets.QFrame(content_layer)
        shell.setObjectName('Shell')
        shell.setProperty('variant', 'progress')
        stage_layout.addWidget(shell)

        shell_layout = QtWidgets.QVBoxLayout(shell)
        shell_layout.setContentsMargins(16, 16, 16, 16)
        shell_layout.setSpacing(12)

        card = QtWidgets.QFrame(shell)
        card.setObjectName('ConfirmDialogCard')
        card.setProperty('card', 'true')
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
        self.confirm_button = CommandButton(confirm_text, variant=confirm_variant, parent=card)

        self.cancel_button.clicked.connect(self.reject)
        self.confirm_button.clicked.connect(self.accept)

        if show_cancel:
            actions.addWidget(self.cancel_button)
        else:
            self.cancel_button.hide()
        actions.addWidget(self.confirm_button)

        card_layout.addWidget(self._title)
        card_layout.addWidget(self._body)
        card_layout.addLayout(actions)
        shell_layout.addWidget(card)

    def set_title(self, title: str) -> None:
        self._title.setText(title)
        self.setWindowTitle(title)

    def set_body(self, body: str) -> None:
        self._body.setText(body)

    def set_confirm_text(self, text: str) -> None:
        self.confirm_button.setText(text)

    def set_cancel_text(self, text: str) -> None:
        self.cancel_button.setText(text)
