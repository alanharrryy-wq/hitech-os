from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QTabBar, QWidget

from forgeos.shared.pyside6_glass.icons import apply_icon


@dataclass(frozen=True)
class SessionTabView:
    session_id: str
    title: str
    state: str = ''
    dirty: bool = False
    stale: bool = False

    @property
    def display_title(self) -> str:
        suffix = []
        if self.dirty:
            suffix.append('dirty')
        if self.stale:
            suffix.append('stale')
        tail = f" [{' · '.join(suffix)}]" if suffix else ''
        state_tail = f' · {self.state}' if self.state else ''
        return f'{self.title}{state_tail}{tail}'


class SessionTabs(QWidget):
    createRequested = Signal()
    closeRequested = Signal(str)
    currentChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty('role', 'session-tabs')
        self._session_ids: list[str] = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.tab_bar = QTabBar(self)
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setMovable(False)
        self.tab_bar.setDrawBase(False)
        self.tab_bar.currentChanged.connect(self._emit_current)
        self.tab_bar.tabCloseRequested.connect(self._emit_close)
        layout.addWidget(self.tab_bar, 1)

        self.new_button = QPushButton('+', self)
        self.new_button.setProperty('kind', 'secondary')
        self.new_button.setFixedWidth(40)
        apply_icon(self.new_button, 'plus', size=14)
        self.new_button.clicked.connect(self.createRequested.emit)
        layout.addWidget(self.new_button, 0, Qt.AlignRight)

    def set_tabs(self, tabs: Iterable[SessionTabView | dict], active_session_id: str | None = None) -> None:
        normalized: list[SessionTabView] = []
        for item in tabs:
            if isinstance(item, SessionTabView):
                normalized.append(item)
            else:
                normalized.append(
                    SessionTabView(
                        session_id=str(item.get('session_id', item.get('id', ''))),
                        title=str(item.get('title', item.get('name', 'Session'))),
                        state=str(item.get('state', '')),
                        dirty=bool(item.get('dirty', False)),
                        stale=bool(item.get('stale', False)),
                    )
                )

        self.tab_bar.blockSignals(True)
        while self.tab_bar.count():
            self.tab_bar.removeTab(0)
        self._session_ids = []
        active_index = 0
        for index, view in enumerate(normalized):
            self.tab_bar.addTab(view.display_title)
            self._session_ids.append(view.session_id)
            if active_session_id and view.session_id == active_session_id:
                active_index = index
        if normalized:
            self.tab_bar.setCurrentIndex(active_index)
        self.tab_bar.blockSignals(False)

    # Backward-compatible adapter for legacy callsites.
    def set_sessions(self, sessions: Iterable[SessionTabView | dict], active_session_id: str | None = None) -> None:
        self.set_tabs(sessions, active_session_id=active_session_id)

    def _emit_close(self, index: int) -> None:
        if 0 <= index < len(self._session_ids):
            self.closeRequested.emit(self._session_ids[index])

    def _emit_current(self, index: int) -> None:
        if 0 <= index < len(self._session_ids):
            self.currentChanged.emit(self._session_ids[index])


# Legacy alias used by transitional shims.
SessionTabStrip = SessionTabs

__all__ = ["SessionTabStrip", "SessionTabView", "SessionTabs"]
