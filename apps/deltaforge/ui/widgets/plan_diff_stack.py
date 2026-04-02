from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtWidgets import QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget


class PlanDiffStack(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.title = QLabel('Plan / Diff Preview', self)
        self.title.setProperty('role', 'surface-title')
        layout.addWidget(self.title)

        self.tree = QTreeWidget(self)
        self.tree.setHeaderLabels(['File / Group', 'Summary'])
        layout.addWidget(self.tree, 1)

    def set_groups(self, groups: Iterable[dict] | None) -> None:
        self.tree.clear()
        if not groups:
            placeholder = QTreeWidgetItem(['No grouped diff yet', 'Waiting for projection'])
            self.tree.addTopLevelItem(placeholder)
            return
        for group in groups:
            root = QTreeWidgetItem([
                str(group.get('label', group.get('file', 'group'))),
                str(group.get('summary', '')),
            ])
            for item in group.get('items', []) or []:
                child = QTreeWidgetItem([
                    str(item.get('label', item.get('title', 'item'))),
                    str(item.get('summary', '')),
                ])
                root.addChild(child)
            self.tree.addTopLevelItem(root)
            root.setExpanded(True)
