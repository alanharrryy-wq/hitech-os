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
    QSplitter,
    QVBoxLayout,
    QWidget,
)


class CenterDiffPanel(QWidget):
    """Diff surface.

    The panel renders a diff payload or per-file diff entries and only emits
    file-selection intent.
    """

    file_selected = Signal(object)

    def __init__(
        self,
        parent: QWidget | None = None,
        on_file_selected: Callable[[object], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_file_selected = on_file_selected
        self._session_label = QLabel('Session: —')
        self._state_label = QLabel('State: —')
        self._diff_id_value = QLabel('—')
        self._title_value = QLabel('—')
        self._status_value = QLabel('—')
        self._summary_value = QLabel('—')
        self._files_list = QListWidget(self)
        self._diff_view = QPlainTextEdit(self)
        self._full_text = ''
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

        summary_box = QGroupBox('Diff Summary', self)
        summary_layout = QFormLayout(summary_box)
        summary_layout.addRow('Id', self._diff_id_value)
        summary_layout.addRow('Title', self._title_value)
        summary_layout.addRow('Status', self._status_value)
        summary_layout.addRow('Summary', self._summary_value)
        root.addWidget(summary_box)

        splitter = QSplitter(Qt.Horizontal, self)
        self._files_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self._files_list.itemSelectionChanged.connect(self._handle_file_selection_changed)
        splitter.addWidget(self._files_list)

        self._diff_view.setReadOnly(True)
        self._diff_view.setLineWrapMode(QPlainTextEdit.NoWrap)
        splitter.addWidget(self._diff_view)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 4)
        root.addWidget(splitter, 1)

    def set_session_context(self, session_id: object | None, session_state: str | None) -> None:
        self._session_label.setText(f'Session: {self._to_text(session_id)}')
        self._state_label.setText(f'State: {self._to_text(session_state)}')

    def set_diff(self, diff: Mapping[str, Any] | None) -> None:
        diff = dict(diff or {})
        self._diff_id_value.setText(self._to_text(diff.get('id')))
        self._title_value.setText(self._to_text(diff.get('title')))
        self._status_value.setText(self._to_text(diff.get('status')))
        self._summary_value.setText(self._to_text(diff.get('summary')))
        self._full_text = str(diff.get('text') or diff.get('patch') or '')
        self._populate_files(diff.get('files') or ())
        if self._files_list.count() == 0:
            self._diff_view.setPlainText(self._full_text)
        else:
            self._files_list.setCurrentRow(0)

    def _populate_files(self, files: Sequence[Any]) -> None:
        self._files_list.clear()
        for file_entry in files:
            if isinstance(file_entry, Mapping):
                label = self._to_text(file_entry.get('label') or file_entry.get('path') or file_entry.get('name') or file_entry.get('id'))
                payload: object = dict(file_entry)
            else:
                label = self._to_text(file_entry)
                payload = {'label': label, 'patch': ''}
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, payload)
            self._files_list.addItem(item)

    def _handle_file_selection_changed(self) -> None:
        item = self._files_list.currentItem()
        if item is None:
            return
        payload = item.data(Qt.UserRole)
        text = self._full_text
        if isinstance(payload, Mapping):
            text = str(payload.get('patch') or payload.get('text') or self._full_text)
        self._diff_view.setPlainText(text)
        self.file_selected.emit(payload)
        if self._on_file_selected is not None:
            self._on_file_selected(payload)

    @staticmethod
    def _to_text(value: object | None) -> str:
        if value in (None, ''):
            return '—'
        return str(value)


__all__ = ['CenterDiffPanel']
