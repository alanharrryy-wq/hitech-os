from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class CenterPlanPanel(QWidget):
    """Plan surface.

    The panel renders an upstream plan payload and emits item selection.
    It does not derive plan state or perform orchestration.
    """

    item_selected = Signal(object)

    def __init__(
        self,
        parent: QWidget | None = None,
        on_item_selected: Callable[[object], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_item_selected = on_item_selected
        self._session_label = QLabel('Session: —')
        self._state_label = QLabel('State: —')
        self._plan_id_value = QLabel('—')
        self._title_value = QLabel('—')
        self._status_value = QLabel('—')
        self._summary_value = QLabel('—')
        self._items_tree = QTreeWidget(self)
        self._detail_view = QPlainTextEdit(self)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)

        header = QHBoxLayout()
        header.addWidget(self._session_label)
        header.addWidget(self._state_label)
        header.addStretch(1)
        root.addLayout(header)

        summary_box = QGroupBox('Plan Summary', self)
        summary_layout = QFormLayout(summary_box)
        summary_layout.addRow('Id', self._plan_id_value)
        summary_layout.addRow('Title', self._title_value)
        summary_layout.addRow('Status', self._status_value)
        summary_layout.addRow('Summary', self._summary_value)
        root.addWidget(summary_box)

        splitter = QSplitter(Qt.Horizontal, self)
        self._items_tree.setColumnCount(2)
        self._items_tree.setHeaderLabels(['Item', 'Status'])
        self._items_tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self._items_tree.itemSelectionChanged.connect(self._handle_tree_selection_changed)
        splitter.addWidget(self._items_tree)

        self._detail_view.setReadOnly(True)
        self._detail_view.setLineWrapMode(QPlainTextEdit.NoWrap)
        splitter.addWidget(self._detail_view)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        root.addWidget(splitter, 1)

    def set_session_context(self, session_id: object | None, session_state: str | None) -> None:
        self._session_label.setText(f'Session: {self._to_text(session_id)}')
        self._state_label.setText(f'State: {self._to_text(session_state)}')

    def set_plan(self, plan: Mapping[str, Any] | None) -> None:
        plan = dict(plan or {})
        self._plan_id_value.setText(self._to_text(plan.get('id')))
        self._title_value.setText(self._to_text(plan.get('title')))
        self._status_value.setText(self._to_text(plan.get('status')))
        self._summary_value.setText(self._to_text(plan.get('summary')))
        self._items_tree.clear()

        items = plan.get('items') or ()
        for item in items:
            if isinstance(item, Mapping):
                self._items_tree.addTopLevelItem(self._make_tree_item(item))

        detail_text = plan.get('text') or plan.get('raw_text') or ''
        self._detail_view.setPlainText(str(detail_text))
        self._items_tree.expandAll()

    def _make_tree_item(self, payload: Mapping[str, Any]) -> QTreeWidgetItem:
        title = self._to_text(payload.get('title') or payload.get('label') or payload.get('name') or payload.get('id'))
        status = self._to_text(payload.get('status'))
        item = QTreeWidgetItem([title, status])
        item.setData(0, Qt.UserRole, dict(payload))
        for child_payload in payload.get('children') or ():
            if isinstance(child_payload, Mapping):
                item.addChild(self._make_tree_item(child_payload))
        return item

    def _handle_tree_selection_changed(self) -> None:
        selected_items = self._items_tree.selectedItems()
        if not selected_items:
            return
        payload = selected_items[0].data(0, Qt.UserRole)
        detail = ''
        if isinstance(payload, Mapping):
            detail = str(payload.get('detail') or payload.get('text') or payload.get('summary') or '')
        self._detail_view.setPlainText(detail)
        self.item_selected.emit(payload)
        if self._on_item_selected is not None:
            self._on_item_selected(payload)

    @staticmethod
    def _to_text(value: object | None) -> str:
        if value in (None, ''):
            return '—'
        return str(value)


__all__ = ['CenterPlanPanel']
