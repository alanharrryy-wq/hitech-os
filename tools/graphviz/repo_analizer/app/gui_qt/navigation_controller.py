from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .main_window import RepoAnalyzerMainWindow


class NavigationController:
    """Manages navigation history and preview history."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window
        self._preview_history: list[tuple[str, int]] = []
        self._preview_history_index = -1
        self._history_lock = False

    def navigate_back(self) -> None:
        """Navigate to previous preview in history."""
        if self._preview_history_index <= 0:
            return

        self._preview_history_index -= 1
        relpath, line = self._preview_history[self._preview_history_index]
        self._history_lock = True
        try:
            self.main.preview_controller.show_preview_for_relpath(relpath, line, add_history=False)
        finally:
            self._history_lock = False

        self.main._update_preview_actions()

    def navigate_forward(self) -> None:
        """Navigate to next preview in history."""
        if self._preview_history_index >= len(self._preview_history) - 1:
            return

        self._preview_history_index += 1
        relpath, line = self._preview_history[self._preview_history_index]
        self._history_lock = True
        try:
            self.main.preview_controller.show_preview_for_relpath(relpath, line, add_history=False)
        finally:
            self._history_lock = False

        self.main._update_preview_actions()

    def _push_preview_history(self, relpath: str, line: int) -> None:
        """Add preview to history."""
        if self._history_lock:
            return

        entry = (relpath, line)

        # Don't add duplicate if same as current
        if (
            self._preview_history
            and self._preview_history_index >= 0
            and self._preview_history[self._preview_history_index] == entry
        ):
            return

        # Trim history if moving back then clicking new
        if self._preview_history_index < len(self._preview_history) - 1:
            self._preview_history = self._preview_history[: self._preview_history_index + 1]

        self._preview_history.append(entry)

        # Limit history to 100 entries
        if len(self._preview_history) > 100:
            self._preview_history = self._preview_history[-100:]

        self._preview_history_index = len(self._preview_history) - 1
        self.main._update_preview_actions()
