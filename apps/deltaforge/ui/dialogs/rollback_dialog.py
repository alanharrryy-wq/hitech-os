from __future__ import annotations

import sys
from pathlib import Path

from PySide6 import QtCore, QtWidgets

from ui.primitives.buttons import CommandButton

_REPO_ROOT = Path(__file__).resolve().parents[4]
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)

from forgeos.shared.pyside6_glass.scene import (
    build_glass_dialog_scene as shared_build_glass_dialog_scene,
)


class RollbackDialog(QtWidgets.QDialog):
    def __init__(self, rollback_tokens: list[str], parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Select Rollback")
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setObjectName('DeltaForgeRollbackDialog')
        self.selected_token = ""

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
        card.setProperty('card', 'true')
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(12)

        title = QtWidgets.QLabel("Select rollback token", card)
        title.setObjectName('DialogTitle')

        self.list_widget = QtWidgets.QListWidget(card)
        for token in rollback_tokens:
            self.list_widget.addItem(token)

        actions = QtWidgets.QHBoxLayout()
        actions.addStretch(1)
        cancel_button = CommandButton("Cancel", variant='ghost', parent=card)
        apply_button = CommandButton("Use selected", variant='primary', parent=card)
        cancel_button.clicked.connect(self.reject)
        apply_button.clicked.connect(self._accept)
        actions.addWidget(cancel_button)
        actions.addWidget(apply_button)

        card_layout.addWidget(title)
        card_layout.addWidget(self.list_widget)
        card_layout.addLayout(actions)
        shell_layout.addWidget(card)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

    def _accept(self) -> None:
        item = self.list_widget.currentItem()
        if item is not None:
            self.selected_token = item.text()
        self.accept()
