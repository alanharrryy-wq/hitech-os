from __future__ import annotations

from typing import Optional, Sequence

from PySide6 import QtWidgets


class TabStyle(QtWidgets.QTabWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setDocumentMode(True)
        self.setMovable(False)
        self.setTabsClosable(False)

    def add_labeled_tab(self, widget: QtWidgets.QWidget, label: str) -> int:
        return self.addTab(widget, label)

    def set_tab_labels(self, labels: Sequence[str]) -> None:
        for index, label in enumerate(labels):
            if index < self.count():
                self.setTabText(index, label)
