from __future__ import annotations

from typing import Any, Callable, Mapping

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFormLayout, QGroupBox, QHBoxLayout, QLabel, QPlainTextEdit, QVBoxLayout, QWidget


class LeftOpsPanel(QWidget):
    """Ops document surface.

    This panel only reflects and edits the current ops document text.
    It forwards text changes upstream and does not persist or validate anything.
    """

    ops_changed = Signal(str)

    def __init__(
        self,
        parent: QWidget | None = None,
        on_ops_changed: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_ops_changed = on_ops_changed
        self._is_setting_document = False
        self._session_label = QLabel('Session: —')
        self._state_label = QLabel('State: —')
        self._document_id_value = QLabel('—')
        self._title_value = QLabel('—')
        self._status_value = QLabel('—')
        self._hint_value = QLabel('—')
        self._stats_value = QLabel('Lines: 0 · Chars: 0')
        self._editor = QPlainTextEdit(self)
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

        summary_box = QGroupBox('Ops Document', self)
        summary_layout = QFormLayout(summary_box)
        summary_layout.addRow('Id', self._document_id_value)
        summary_layout.addRow('Title', self._title_value)
        summary_layout.addRow('Status', self._status_value)
        summary_layout.addRow('Hint', self._hint_value)
        root.addWidget(summary_box)

        self._editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        self._editor.textChanged.connect(self._handle_text_changed)
        root.addWidget(self._editor, 1)

        footer = QHBoxLayout()
        footer.addWidget(self._stats_value)
        footer.addStretch(1)
        root.addLayout(footer)

    def set_session_context(self, session_id: object | None, session_state: str | None) -> None:
        self._session_label.setText(f'Session: {self._to_text(session_id)}')
        self._state_label.setText(f'State: {self._to_text(session_state)}')

    def set_document(self, document: Mapping[str, Any] | None) -> None:
        document = dict(document or {})
        self._document_id_value.setText(self._to_text(document.get('id')))
        self._title_value.setText(self._to_text(document.get('title')))
        self._status_value.setText(self._to_text(document.get('status')))
        self._hint_value.setText(self._to_text(document.get('hint')))
        self._is_setting_document = True
        self._editor.setPlainText(str(document.get('content') or ''))
        self._editor.setReadOnly(bool(document.get('read_only', False)))
        self._is_setting_document = False
        self._update_stats()

    def set_read_only(self, is_read_only: bool) -> None:
        self._editor.setReadOnly(is_read_only)

    def text(self) -> str:
        return self._editor.toPlainText()

    def _handle_text_changed(self) -> None:
        self._update_stats()
        if self._is_setting_document:
            return
        text = self._editor.toPlainText()
        self.ops_changed.emit(text)
        if self._on_ops_changed is not None:
            self._on_ops_changed(text)

    def _update_stats(self) -> None:
        text = self._editor.toPlainText()
        line_count = 0 if not text else text.count('\n') + 1
        self._stats_value.setText(f'Lines: {line_count} · Chars: {len(text)}')

    @staticmethod
    def _to_text(value: object | None) -> str:
        if value in (None, ''):
            return '—'
        return str(value)


__all__ = ['LeftOpsPanel']
