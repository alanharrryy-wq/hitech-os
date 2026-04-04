from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PySide6.QtGui import QKeySequence, QShortcut


@dataclass(frozen=True)
class ShortcutBinding:
    command_id: str
    sequence: str


REQUIRED_SHORTCUTS: tuple[ShortcutBinding, ...] = (
    ShortcutBinding("new_session", "Ctrl+T"),
    ShortcutBinding("clone_session", "Ctrl+Shift+T"),
    ShortcutBinding("close_session", "Ctrl+W"),
    ShortcutBinding("choose_files", "Ctrl+O"),
    ShortcutBinding("choose_folder", "Ctrl+Shift+O"),
    ShortcutBinding("load_ops", "Ctrl+L"),
    ShortcutBinding("save_ops", "Ctrl+S"),
    ShortcutBinding("refresh", "F5"),
    ShortcutBinding("validate", "Ctrl+R"),
    ShortcutBinding("plan", "Ctrl+Shift+R"),
    ShortcutBinding("apply", "Ctrl+Return"),
    ShortcutBinding("rollback", "Ctrl+Z"),
    ShortcutBinding("focus_left", "Ctrl+1"),
    ShortcutBinding("focus_center", "Ctrl+2"),
    ShortcutBinding("focus_right", "Ctrl+3"),
    ShortcutBinding("focus_bottom", "Ctrl+4"),
    ShortcutBinding("next_session", "Ctrl+Tab"),
    ShortcutBinding("prev_session", "Ctrl+Shift+Tab"),
)


def install_shortcuts(parent, handlers: dict[str, Callable[[], None]]) -> list[QShortcut]:
    shortcuts: list[QShortcut] = []
    for binding in REQUIRED_SHORTCUTS:
        callback = handlers.get(binding.command_id)
        if callback is None:
            continue

        shortcut = QShortcut(QKeySequence(binding.sequence), parent)
        shortcut.activated.connect(callback)
        shortcuts.append(shortcut)
    return shortcuts
