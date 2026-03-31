from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton


class CommandButton(QPushButton):
    def __init__(self, text: str, *, variant: str = "command") -> None:
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("variant", variant)
