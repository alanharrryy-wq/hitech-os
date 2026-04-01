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
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class LeftScopePanel(QWidget):
    """Scope and target surface.

    The panel renders session-scoped scope information, targets and watch paths.
    It accepts already-resolved data and emits only selection intent.
    """

    target_selected = Signal(object)

    def __init__(
        self,
        parent: QWidget | None = None,
        on_target_selected: Callable[[object], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_target_selected = on_target_selected
        self._session_label = QLabel('Session: —')
        self._state_label = QLabel('State: —')
        self._kind_value = QLabel('—')
        self._path_value = QLabel('—')
        self._source_value = QLabel('—')
        self._summary_value = QLabel('—')
        self._targets_list = QListWidget(self)
        self._watch_paths_list = QListWidget(self)
        self._metadata_table = QTableWidget(self)
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

        summary_box = QGroupBox('Scope Summary', self)
        summary_layout = QFormLayout(summary_box)
        summary_layout.addRow('Kind', self._kind_value)
        summary_layout.addRow('Path', self._path_value)
        summary_layout.addRow('Source', self._source_value)
        summary_layout.addRow('Summary', self._summary_value)
        root.addWidget(summary_box)

        targets_box = QGroupBox('Targets', self)
        targets_layout = QVBoxLayout(targets_box)
        self._targets_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self._targets_list.itemSelectionChanged.connect(self._handle_target_selection_changed)
        targets_layout.addWidget(self._targets_list)
        root.addWidget(targets_box, 1)

        watch_box = QGroupBox('Watch Paths', self)
        watch_layout = QVBoxLayout(watch_box)
        watch_layout.addWidget(self._watch_paths_list)
        root.addWidget(watch_box, 1)

        meta_box = QGroupBox('Metadata', self)
        meta_layout = QVBoxLayout(meta_box)
        self._metadata_table.setColumnCount(2)
        self._metadata_table.setHorizontalHeaderLabels(['Key', 'Value'])
        self._metadata_table.verticalHeader().setVisible(False)
        self._metadata_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._metadata_table.setSelectionMode(QAbstractItemView.NoSelection)
        self._metadata_table.horizontalHeader().setStretchLastSection(True)
        meta_layout.addWidget(self._metadata_table)
        root.addWidget(meta_box, 1)

    def _handle_target_selection_changed(self) -> None:
        item = self._targets_list.currentItem()
        if item is None:
            return
        payload = item.data(Qt.UserRole)
        self.target_selected.emit(payload)
        if self._on_target_selected is not None:
            self._on_target_selected(payload)

    def set_session_context(self, session_id: object | None, session_state: str | None) -> None:
        self._session_label.setText(f'Session: {self._to_text(session_id)}')
        self._state_label.setText(f'State: {self._to_text(session_state)}')

    def set_scope(self, scope: Mapping[str, Any] | None) -> None:
        scope = dict(scope or {})
        self._kind_value.setText(self._to_text(scope.get('kind')))
        self._path_value.setText(self._to_text(scope.get('path')))
        self._source_value.setText(self._to_text(scope.get('source')))
        self._summary_value.setText(self._to_text(scope.get('summary')))
        self._populate_list(self._targets_list, scope.get('targets') or ())
        self._populate_list(self._watch_paths_list, scope.get('watch_paths') or ())
        metadata = scope.get('metadata') or {}
        self._populate_metadata(metadata)

    def _populate_list(self, widget: QListWidget, values: Sequence[Any]) -> None:
        widget.clear()
        for value in values:
            if isinstance(value, Mapping):
                label = self._to_text(value.get('label') or value.get('path') or value.get('name') or value.get('id'))
                payload: object = dict(value)
            else:
                label = self._to_text(value)
                payload = value
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, payload)
            widget.addItem(item)

    def _populate_metadata(self, metadata: Mapping[str, Any]) -> None:
        rows = list(metadata.items())
        self._metadata_table.setRowCount(len(rows))
        for row_index, (key, value) in enumerate(rows):
            self._metadata_table.setItem(row_index, 0, QTableWidgetItem(self._to_text(key)))
            self._metadata_table.setItem(row_index, 1, QTableWidgetItem(self._to_text(value)))
        self._metadata_table.resizeColumnsToContents()

    @staticmethod
    def _to_text(value: object | None) -> str:
        if value in (None, ''):
            return '—'
        return str(value)


__all__ = ['LeftScopePanel']
