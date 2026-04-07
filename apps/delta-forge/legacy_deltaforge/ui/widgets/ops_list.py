from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget


class OpsList(QListWidget):
    selectionChangedByUser = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.itemSelectionChanged.connect(self._emit_current)

    def set_items(self, items: Iterable[dict | str]) -> None:
        self.clear()
        for item in items:
            if isinstance(item, str):
                text = item
                payload = {'label': item}
            else:
                text = str(item.get('label', item.get('title', 'item')))
                payload = dict(item)
            widget_item = QListWidgetItem(text)
            widget_item.setData(32, payload)
            self.addItem(widget_item)

    def _emit_current(self) -> None:
        item = self.currentItem()
        payload = item.data(32) if item is not None else None
        self.selectionChangedByUser.emit(payload)
