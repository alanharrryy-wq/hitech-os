from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from forgeos.shared.pyside6_glass.controls import create_button


@dataclass(frozen=True)
class CommandBarState:
    root_dir: str = ''
    mode_label: str = 'workspace'
    busy: bool = False


class CommandBar(QWidget):
    browseRequested = Signal()
    validateRequested = Signal()
    planRequested = Signal()
    applyRequested = Signal()
    rollbackRequested = Signal()
    refreshRequested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty('role', 'command-bar')

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        frame = QFrame(self)
        frame.setProperty('role', 'surface')
        outer.addWidget(frame)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel('Command Bar', frame)
        title.setProperty('role', 'surface-title')
        meta = QLabel('Projection-only UI surface.', frame)
        meta.setProperty('role', 'surface-meta')
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(meta)
        layout.addLayout(header)

        row = QHBoxLayout()
        row.setSpacing(8)
        self.root_dir_input = QLineEdit(frame)
        self.root_dir_input.setPlaceholderText('Root dir projection')
        self.root_dir_input.setReadOnly(True)
        self.root_dir_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        row.addWidget(self.root_dir_input, 1)

        self.browse_button = create_button(
            'Browse',
            'secondary',
            self.browseRequested.emit,
            parent=frame,
            icon_name='folder-open',
        )
        row.addWidget(self.browse_button)
        layout.addLayout(row)

        actions = QHBoxLayout()
        actions.setSpacing(8)
        self.validate_button = self._make_button('Validate', 'primary', self.validateRequested.emit, icon_name='check-circle')
        self.plan_button = self._make_button('Plan', 'secondary', self.planRequested.emit, icon_name='layers')
        self.apply_button = self._make_button('Apply', 'secondary', self.applyRequested.emit, icon_name='play')
        self.rollback_button = self._make_button('Rollback', 'ghost', self.rollbackRequested.emit, icon_name='arrow-left')
        self.refresh_button = self._make_button('Refresh', 'ghost', self.refreshRequested.emit, icon_name='refresh-cw')
        for button in (
            self.validate_button,
            self.plan_button,
            self.apply_button,
            self.rollback_button,
            self.refresh_button,
        ):
            actions.addWidget(button)
        actions.addStretch(1)
        self.mode_label = QLabel('workspace', frame)
        self.mode_label.setProperty('role', 'status-chip')
        self.mode_label.setProperty('tone', 'accent')
        actions.addWidget(self.mode_label)
        layout.addLayout(actions)

    def _make_button(self, text: str, kind: str, callback, *, icon_name: str | None = None):
        return create_button(
            text,
            kind,
            callback,
            parent=self,
            icon_name=icon_name,
        )

    def set_state(self, state: CommandBarState | dict | None) -> None:
        if state is None:
            state = CommandBarState()
        if isinstance(state, dict):
            state = CommandBarState(
                root_dir=str(state.get('root_dir', '')),
                mode_label=str(state.get('mode_label', state.get('mode', 'workspace'))),
                busy=bool(state.get('busy', False)),
            )
        self.root_dir_input.setText(state.root_dir)
        self.root_dir_input.setCursorPosition(0)
        self.mode_label.setText(state.mode_label)
        enabled = not state.busy
        for button in (
            self.browse_button,
            self.validate_button,
            self.plan_button,
            self.apply_button,
            self.rollback_button,
            self.refresh_button,
        ):
            button.setEnabled(enabled)
