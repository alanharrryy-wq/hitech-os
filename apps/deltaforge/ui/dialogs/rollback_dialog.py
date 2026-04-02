from PySide6.QtWidgets import QDialog, QListWidget, QPushButton, QVBoxLayout


class RollbackDialog(QDialog):
    def __init__(self, rollback_tokens: list[str], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Select Rollback")
        self.selected_token = ""

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        for token in rollback_tokens:
            self.list_widget.addItem(token)
        layout.addWidget(self.list_widget)

        self.ok_button = QPushButton("Use Selected")
        self.ok_button.clicked.connect(self._accept)
        layout.addWidget(self.ok_button)

    def _accept(self) -> None:
        item = self.list_widget.currentItem()
        if item is not None:
            self.selected_token = item.text()
        self.accept()
