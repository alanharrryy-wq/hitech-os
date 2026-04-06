
from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtWidgets import QFrame, QLabel, QPlainTextEdit, QVBoxLayout, QWidget

from visuals.effects.shadow import apply_shadow


class LogConsole(QFrame):
    def __init__(self, parent: QWidget | None = None, *, title: str = "Operator notes") -> None:
        super().__init__(parent)
        self.setProperty("card", "muted")
        apply_shadow(self, blur=14.0, y_offset=5.0, alpha=10)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        heading = QLabel(title, self)
        heading.setProperty("role", "section")
        layout.addWidget(heading)

        self.console = QPlainTextEdit(self)
        self.console.setReadOnly(True)
        self.console.setMinimumHeight(140)
        layout.addWidget(self.console, 1)

    def clear_entries(self) -> None:
        self.console.clear()

    def set_lines(self, lines: Iterable[str]) -> None:
        self.console.setPlainText("\n".join(str(line) for line in lines if str(line).strip()))

    def append_line(self, line: str) -> None:
        current = self.console.toPlainText()
        chunk = str(line or "").strip()
        if not chunk:
            return
        if current:
            self.console.setPlainText(current + "\n" + chunk)
        else:
            self.console.setPlainText(chunk)
