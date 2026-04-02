from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget


class DiffBlockContainer(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setProperty("role", "mono")
        layout.addWidget(self.text)

    def set_diff_text(self, value: str) -> None:
        self.text.setPlainText(value)
