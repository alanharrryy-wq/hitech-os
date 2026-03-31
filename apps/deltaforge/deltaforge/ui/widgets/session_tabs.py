from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTabBar

from deltaforge.domain.models import SessionWorkspace


class SessionTabStrip(QTabBar):
    session_selected = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setDocumentMode(True)
        self.setMovable(False)
        self.setExpanding(False)
        self._session_ids: list[str] = []
        self.currentChanged.connect(self._on_index_changed)

    def set_sessions(self, sessions: list[SessionWorkspace], current_session_id: str) -> None:
        self.blockSignals(True)
        self.clear()
        self._session_ids = [item.session_id for item in sessions]

        current_index = 0
        for index, session in enumerate(sessions):
            label = session.title
            if session.stale:
                label = f"{label} *"
            self.addTab(label)
            if session.session_id == current_session_id:
                current_index = index

        if self.count() > 0:
            self.setCurrentIndex(current_index)
        self.blockSignals(False)

    def _on_index_changed(self, index: int) -> None:
        if index < 0 or index >= len(self._session_ids):
            return
        self.session_selected.emit(self._session_ids[index])

    def current_session_id(self) -> str:
        index = self.currentIndex()
        if index < 0 or index >= len(self._session_ids):
            return ""
        return self._session_ids[index]
