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

    def can_execute(self) -> bool:
        """Check if there is a current preview to bookmark."""
        return (
            self.main_window is not None
            and hasattr(self.main_window, '_current_preview_relpath')
            and self.main_window._current_preview_relpath is not None
        )

    def execute(self) -> None:
        """Execute the add bookmark operation."""
        self.main_window.add_current_preview_bookmark()
