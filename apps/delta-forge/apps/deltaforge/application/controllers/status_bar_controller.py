from __future__ import annotations

from typing import TYPE_CHECKING

from application.session_manager import SessionManager

if TYPE_CHECKING:
    from ui.widgets.status_widgets import WorkstationStatusBar


class StatusBarController:
    def __init__(self, status_bar: "WorkstationStatusBar", manager: SessionManager) -> None:
        self._status_bar = status_bar
        self._manager = manager

    def refresh(self) -> None:
        self._status_bar.update_from_session(self._manager.current())
