from PySide6.QtWidgets import QMessageBox, QWidget


def confirm_action(parent: QWidget, title: str, message: str) -> bool:
    answer = QMessageBox.question(parent, title, message)
    return answer == QMessageBox.Yes


def show_warning(parent: QWidget, title: str, message: str) -> None:
    QMessageBox.warning(parent, title, message)


def show_info(parent: QWidget, title: str, message: str) -> None:
    QMessageBox.information(parent, title, message)
