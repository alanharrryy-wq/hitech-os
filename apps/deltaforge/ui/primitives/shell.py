from PySide6.QtWidgets import QFrame


class MainShellFrame(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("MainShell")
