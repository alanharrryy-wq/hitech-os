from __future__ import annotations

from PySide6 import QtWidgets

from ui.primitives.confirm_dialog import ConfirmDialog


def confirm_action(parent: QtWidgets.QWidget, title: str, message: str) -> bool:
    dialog = ConfirmDialog(
        title=title,
        body=message,
        confirm_text='Confirmar',
        cancel_text='Cancelar',
        confirm_variant='primary',
        show_cancel=True,
        parent=parent,
    )
    return dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted


def show_warning(parent: QtWidgets.QWidget, title: str, message: str) -> None:
    dialog = ConfirmDialog(
        title=title,
        body=message,
        confirm_text='Entendido',
        cancel_text='',
        confirm_variant='danger',
        show_cancel=False,
        parent=parent,
    )
    dialog.exec()


def show_info(parent: QtWidgets.QWidget, title: str, message: str) -> None:
    dialog = ConfirmDialog(
        title=title,
        body=message,
        confirm_text='OK',
        cancel_text='',
        confirm_variant='primary',
        show_cancel=False,
        parent=parent,
    )
    dialog.exec()
