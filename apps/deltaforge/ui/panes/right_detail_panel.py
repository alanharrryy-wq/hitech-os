from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class RightDetailPanel(QWidget):
    """Generic detail surface for session-scoped selections."""

    related_selected = Signal(object)

    def __init__(
        self,
        parent: QWidget | None = None,
        on_related_selected: Callable[[object], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_related_selected = on_related_selected
        self._session_label = QLabel('Session: —')
        self._state_label = QLabel('State: —')
        self._title_value = QLabel('—')
        self._subtitle_value = QLabel('—')
        self._status_value = QLabel('—')
        self._metadata_table = QTableWidget(self)
        self._body_view = QPlainTextEdit(self)
        self._related_list = QListWidget(self)
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

        summary_box = QGroupBox('Detail Summary', self)
        summary_layout = QFormLayout(summary_box)
        summary_layout.addRow('Title', self._title_value)
        summary_layout.addRow('Subtitle', self._subtitle_value)
        summary_layout.addRow('Status', self._status_value)
        root.addWidget(summary_box)

        metadata_box = QGroupBox('Metadata', self)
        metadata_layout = QVBoxLayout(metadata_box)
        self._metadata_table.setColumnCount(2)
        self._metadata_table.setHorizontalHeaderLabels(['Key', 'Value'])
        self._metadata_table.verticalHeader().setVisible(False)
        self._metadata_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._metadata_table.setSelectionMode(QAbstractItemView.NoSelection)
        self._metadata_table.horizontalHeader().setStretchLastSection(True)
        metadata_layout.addWidget(self._metadata_table)
        root.addWidget(metadata_box, 1)

        body_box = QGroupBox('Body', self)
        body_layout = QVBoxLayout(body_box)
        self._body_view.setReadOnly(True)
        self._body_view.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        body_layout.addWidget(self._body_view)
        root.addWidget(body_box, 2)

        related_box = QGroupBox('Related', self)
        related_layout = QVBoxLayout(related_box)
        self._related_list.itemSelectionChanged.connect(self._handle_related_selection_changed)
        related_layout.addWidget(self._related_list)
        root.addWidget(related_box, 1)

    def set_session_context(self, session_id: object | None, session_state: str | None) -> None:
        self._session_label.setText(f'Session: {self._to_text(session_id)}')
        self._state_label.setText(f'State: {self._to_text(session_state)}')

    def set_detail(self, detail: Mapping[str, Any] | None) -> None:
        detail = dict(detail or {})
        self._title_value.setText(self._to_text(detail.get('title')))
        self._subtitle_value.setText(self._to_text(detail.get('subtitle')))
        self._status_value.setText(self._to_text(detail.get('status')))
        self._body_view.setPlainText(str(detail.get('body') or detail.get('text') or ''))
        self._populate_metadata(detail.get('metadata') or {})
        self._populate_related(detail.get('related') or ())

    def _populate_metadata(self, metadata: Mapping[str, Any]) -> None:
        rows = list(metadata.items())
        self._metadata_table.setRowCount(len(rows))
        for row_index, (key, value) in enumerate(rows):
            self._metadata_table.setItem(row_index, 0, QTableWidgetItem(self._to_text(key)))
            self._metadata_table.setItem(row_index, 1, QTableWidgetItem(self._to_text(value)))
        self._metadata_table.resizeColumnsToContents()

    def _populate_related(self, values: Sequence[Any]) -> None:
        self._related_list.clear()
        for value in values:
            if isinstance(value, Mapping):
                label = self._to_text(value.get('label') or value.get('title') or value.get('name') or value.get('id'))
                payload: object = dict(value)
            else:
                label = self._to_text(value)
                payload = value
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, payload)
            self._related_list.addItem(item)

    def _handle_related_selection_changed(self) -> None:
        item = self._related_list.currentItem()
        if item is None:
            return
        payload = item.data(Qt.UserRole)
        self.related_selected.emit(payload)
        if self._on_related_selected is not None:
            self._on_related_selected(payload)

    @staticmethod
    def _to_text(value: object | None) -> str:
        if value in (None, ''):
            return '—'
        return str(value)


__all__ = ['RightDetailPanel']
