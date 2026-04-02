from __future__ import annotations

from typing import Any, Mapping, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class BottomPlanPanel(QWidget):
    """Plan surface scoped by session inputs."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session_label = QLabel('Session: —')
        self._state_label = QLabel('State: —')
        self._status_value = QLabel('—')
        self._summary_value = QLabel('—')
        self._duration_value = QLabel('—')
        self._table = QTableWidget(self)
        self._output_view = QPlainTextEdit(self)
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
        summary_layout.addRow('Status', self._status_value)
        summary_layout.addRow('Summary', self._summary_value)
        summary_layout.addRow('Duration', self._duration_value)
        root.addWidget(summary_box)

        splitter = QSplitter(Qt.Horizontal, self)
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(['Item', 'Status', 'Detail'])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.horizontalHeader().setStretchLastSection(True)
        splitter.addWidget(self._table)

        self._output_view.setReadOnly(True)
        self._output_view.setLineWrapMode(QPlainTextEdit.NoWrap)
        splitter.addWidget(self._output_view)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 4)
        root.addWidget(splitter, 1)

    def set_session_context(self, session_id: object | None, session_state: str | None) -> None:
        self._session_label.setText(f'Session: {self._to_text(session_id)}')
        self._state_label.setText(f'State: {self._to_text(session_state)}')

    def set_plan_result(self, result: Mapping[str, Any] | None) -> None:
        result = dict(result or {})
        self._status_value.setText(self._to_text(result.get('status')))
        self._summary_value.setText(self._to_text(result.get('summary')))
        self._duration_value.setText(self._to_text(result.get('duration')))
        items = result.get('items') or ()
        self._table.setRowCount(len(items))
        for row_index, item in enumerate(items):
            if isinstance(item, Mapping):
                item_name = self._to_text(item.get('label') or item.get('name') or item.get('id'))
                item_status = self._to_text(item.get('status'))
                item_detail = self._to_text(item.get('detail') or item.get('summary') or item.get('message'))
            else:
                item_name = self._to_text(item)
                item_status = '—'
                item_detail = '—'
            self._table.setItem(row_index, 0, QTableWidgetItem(item_name))
            self._table.setItem(row_index, 1, QTableWidgetItem(item_status))
            self._table.setItem(row_index, 2, QTableWidgetItem(item_detail))
        self._table.resizeColumnsToContents()
        output_text = result.get('output') or result.get('raw_output') or result.get('text') or ''
        self._output_view.setPlainText(str(output_text))

    @staticmethod
    def _to_text(value: object | None) -> str:
        if value in (None, ''):
            return '—'
        return str(value)


__all__ = ['BottomPlanPanel']
