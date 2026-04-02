from __future__ import annotations

from typing import Any, Mapping, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class BottomEventsPanel(QWidget):
    """Session-scoped event stream surface."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session_label = QLabel('Session: —')
        self._state_label = QLabel('State: —')
        self._count_label = QLabel('Events: 0')
        self._table = QTableWidget(self)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(8)

        header = QHBoxLayout()
        header.addWidget(self._session_label)
        header.addWidget(self._state_label)
        header.addStretch(1)
        header.addWidget(self._count_label)
        root.addLayout(header)

        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(['Time', 'Event', 'Level', 'Message'])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self._table, 1)

    def set_session_context(self, session_id: object | None, session_state: str | None) -> None:
        self._session_label.setText(f'Session: {self._to_text(session_id)}')
        self._state_label.setText(f'State: {self._to_text(session_state)}')

    def set_events(self, events: Sequence[Mapping[str, Any]]) -> None:
        self._table.setRowCount(len(events))
        for row_index, event in enumerate(events):
            time_value = self._to_text(event.get('timestamp') or event.get('time') or event.get('created_at'))
            name_value = self._to_text(event.get('event') or event.get('name') or event.get('type'))
            level_value = self._to_text(event.get('level'))
            message_value = self._to_text(event.get('message') or event.get('summary') or event.get('detail'))
            self._table.setItem(row_index, 0, QTableWidgetItem(time_value))
            self._table.setItem(row_index, 1, QTableWidgetItem(name_value))
            self._table.setItem(row_index, 2, QTableWidgetItem(level_value))
            self._table.setItem(row_index, 3, QTableWidgetItem(message_value))
        self._count_label.setText(f'Events: {len(events)}')
        self._table.resizeColumnsToContents()

    @staticmethod
    def _to_text(value: object | None) -> str:
        if value in (None, ''):
            return '—'
        return str(value)


__all__ = ['BottomEventsPanel']
