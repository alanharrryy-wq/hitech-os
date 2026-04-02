from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


@dataclass(frozen=True)
class SessionStatusSummary:
    root_dir: str = ''
    target_count: int = 0
    session_state: str = 'idle'
    current_mode: str = 'workspace'
    dirty: bool = False
    stale: bool = False


class StatusStrip(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty('role', 'surface')

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        self._labels: dict[str, QLabel] = {}

        for key in ('root_dir', 'targets', 'state', 'mode', 'flags'):
            block = self._make_block(key)
            layout.addLayout(block)
        layout.addStretch(1)

    def _make_block(self, key: str) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(2)
        title = QLabel(key.replace('_', ' ').title(), self)
        title.setProperty('role', 'surface-meta')
        value = QLabel('-', self)
        value.setProperty('role', 'status-chip')
        value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._labels[key] = value
        layout.addWidget(title)
        layout.addWidget(value)
        return layout

    def set_summary(self, summary: SessionStatusSummary | dict | None) -> None:
        if summary is None:
            summary = SessionStatusSummary()
        if isinstance(summary, dict):
            summary = SessionStatusSummary(
                root_dir=str(summary.get('root_dir', '')),
                target_count=int(summary.get('target_count', 0) or 0),
                session_state=str(summary.get('session_state', summary.get('state', 'idle'))),
                current_mode=str(summary.get('current_mode', summary.get('mode', 'workspace'))),
                dirty=bool(summary.get('dirty', False)),
                stale=bool(summary.get('stale', False)),
            )
        flags = []
        if summary.dirty:
            flags.append('dirty')
        if summary.stale:
            flags.append('stale')
        self._labels['root_dir'].setText(summary.root_dir or '-')
        self._labels['targets'].setText(str(summary.target_count))
        self._labels['state'].setText(summary.session_state)
        self._labels['mode'].setText(summary.current_mode)
        self._labels['flags'].setText(' · '.join(flags) if flags else 'clean')
