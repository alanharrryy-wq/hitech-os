from __future__ import annotations

from typing import Callable, Mapping

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QSizePolicy, QToolButton, QWidget


class StatusBar(QWidget):
    """Session-aware status surface.

    It only reflects upstream status and forwards explicit callback intent.
    """

    action_requested = Signal(str)

    ACTION_ORDER = ('refresh_session', 'mark_dirty', 'mark_stale')

    def __init__(
        self,
        parent: QWidget | None = None,
        callbacks: Mapping[str, Callable[[], None] | None] | None = None,
    ) -> None:
        super().__init__(parent)
        self._callbacks: dict[str, Callable[[], None] | None] = {}
        self._buttons: dict[str, QToolButton] = {}
        self._session_label = QLabel('Session: —')
        self._state_label = QLabel('State: —')
        self._scope_label = QLabel('Scope: —')
        self._message_label = QLabel('Ready')
        self._busy_bar = QProgressBar(self)
        self._build_ui()
        self.set_callbacks(callbacks or {})

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 8, 12, 8)
        root.setSpacing(10)

        self._message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._busy_bar.setTextVisible(False)
        self._busy_bar.setFixedWidth(120)
        self._busy_bar.setRange(0, 1)
        self._busy_bar.setValue(0)

        root.addWidget(self._session_label)
        root.addWidget(self._state_label)
        root.addWidget(self._scope_label)
        root.addWidget(self._message_label, 1)
        root.addWidget(self._busy_bar)

        for action_name in self.ACTION_ORDER:
            button = QToolButton(self)
            button.setText(self._format_action_name(action_name))
            button.clicked.connect(lambda checked=False, name=action_name: self._handle_action(name))
            self._buttons[action_name] = button
            root.addWidget(button)

    @staticmethod
    def _format_action_name(action_name: str) -> str:
        return ' '.join(part.capitalize() for part in action_name.split('_'))

    def _handle_action(self, action_name: str) -> None:
        self.action_requested.emit(action_name)
        callback = self._callbacks.get(action_name)
        if callback is not None:
            callback()

    def set_callbacks(self, callbacks: Mapping[str, Callable[[], None] | None]) -> None:
        self._callbacks = dict(callbacks)
        for action_name, button in self._buttons.items():
            button.setVisible(action_name in self._callbacks)

    def set_session_context(self, session_id: object | None, session_state: str | None) -> None:
        self._session_label.setText(f'Session: {self._to_text(session_id)}')
        self._state_label.setText(f'State: {self._to_text(session_state)}')

    def set_scope_text(self, scope_text: object | None) -> None:
        self._scope_label.setText(f'Scope: {self._to_text(scope_text)}')

    def set_message(self, message: object | None) -> None:
        self._message_label.setText(self._to_text(message))

    def set_busy(self, busy: bool) -> None:
        if busy:
            self._busy_bar.setRange(0, 0)
        else:
            self._busy_bar.setRange(0, 1)
            self._busy_bar.setValue(0)

    def set_action_enabled(self, action_name: str, enabled: bool) -> None:
        button = self._buttons.get(action_name)
        if button is not None:
            button.setEnabled(enabled)

    @staticmethod
    def _to_text(value: object | None) -> str:
        if value in (None, ''):
            return '—'
        return str(value)


__all__ = ['StatusBar']
