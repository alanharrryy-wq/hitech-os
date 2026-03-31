from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolBar


class CommandBar(QToolBar):
    command_invoked = Signal(str)

    ORDER: tuple[str | None, ...] = (
        "new_session",
        "clone_session",
        "close_session",
        None,
        "choose_files",
        "choose_folder",
        "clear_scope",
        None,
        "load_ops",
        "save_ops",
        None,
        "validate",
        "plan",
        "apply",
        "rollback",
        None,
        "refresh",
        "open_root",
        "settings",
    )

    LABELS: dict[str, str] = {
        "new_session": "New Session",
        "clone_session": "Clone Session",
        "close_session": "Close Session",
        "choose_files": "Choose File(s)",
        "choose_folder": "Choose Folder",
        "clear_scope": "Clear Scope",
        "load_ops": "Load Ops",
        "save_ops": "Save Ops",
        "validate": "Validate",
        "plan": "Plan",
        "apply": "Apply",
        "rollback": "Rollback",
        "refresh": "Refresh",
        "open_root": "Open Root",
        "settings": "Settings",
    }

    def __init__(self) -> None:
        super().__init__("DeltaForge Command Bar")
        self.setMovable(False)
        self.setFloatable(False)
        self.actions_by_id: dict[str, QAction] = {}
        self._build()

    def _build(self) -> None:
        for item in self.ORDER:
            if item is None:
                self.addSeparator()
                continue

            action = QAction(self.LABELS[item], self)
            action.setData(item)
            action.triggered.connect(lambda _checked=False, action_id=item: self.command_invoked.emit(action_id))
            self.addAction(action)
            self.actions_by_id[item] = action

    def action_for(self, action_id: str) -> QAction | None:
        return self.actions_by_id.get(action_id)
