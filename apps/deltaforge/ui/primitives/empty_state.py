from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class EmptyStatePanel(QWidget):
    def __init__(self, title: str, hint: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        self.title_label = QLabel(title)
        self.title_label.setProperty("role", "field")
        self.hint_label = QLabel(hint)
        self.hint_label.setProperty("role", "hint")
        self.hint_label.setWordWrap(True)

        layout.addWidget(self.title_label)
        layout.addWidget(self.hint_label)
        layout.addStretch(1)
