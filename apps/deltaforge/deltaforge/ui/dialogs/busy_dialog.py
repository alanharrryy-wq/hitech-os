from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QProgressBar, QVBoxLayout


class BusyDialog(QDialog):
    def __init__(self, title: str, detail: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)

        self.detail_label = QLabel(detail)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)

        layout.addWidget(self.detail_label)
        layout.addWidget(self.progress)

    def update_detail(self, detail: str) -> None:
        self.detail_label.setText(detail)
