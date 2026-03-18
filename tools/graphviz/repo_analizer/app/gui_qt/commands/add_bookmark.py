"""Add bookmark command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..command_dispatcher import Command

if TYPE_CHECKING:
    from ..main_window import RepoAnalyzerMainWindow


class AddBookmarkCommand(Command):
    """
    Add current preview to bookmarks.

    Dependencies:
        main_window: RepoAnalyzerMainWindow instance

    Example:
        cmd = AddBookmarkCommand(main_window)
        cmd.execute()
    """

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        """
        Initialize the command.

        Args:
            main_window: Main window instance
        """
        self.main_window = main_window

    def _resolve_current_preview_rel(self) -> str | None:
        """
        Resolve current preview relpath with compatibility fallback.

        Prefers current shell state (`current_preview_rel`) and falls back to the
        legacy attribute name used by older wrappers.
        """
        relpath = getattr(self.main_window, 'current_preview_rel', None)
        if isinstance(relpath, str) and relpath.strip():
            return relpath

        legacy_relpath = getattr(self.main_window, '_current_preview_relpath', None)
        if isinstance(legacy_relpath, str) and legacy_relpath.strip():
            return legacy_relpath

        return None

    def can_execute(self) -> bool:
        """Check if there is a current preview to bookmark."""
        return self.main_window is not None and self._resolve_current_preview_rel() is not None

    def execute(self) -> None:
        """Execute the add bookmark operation."""
        if not self.can_execute():
            return
        self.main_window.add_current_preview_bookmark()
