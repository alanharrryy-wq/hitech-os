"""Remove bookmark command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..command_dispatcher import Command

if TYPE_CHECKING:
    from ..main_window import RepoAnalyzerMainWindow


class RemoveBookmarkCommand(Command):
    """
    Remove selected bookmark.

    Dependencies:
        main_window: RepoAnalyzerMainWindow instance

    Example:
        cmd = RemoveBookmarkCommand(main_window)
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
        """Check if there is a selected bookmark."""
        if self.main_window is None:
            return False

        bookmarks_list = getattr(self.main_window, 'bookmarks_list', None)
        if bookmarks_list is None or not hasattr(bookmarks_list, 'currentItem'):
            return False

        try:
            return bookmarks_list.currentItem() is not None
        except RuntimeError:
            return False

    def execute(self) -> None:
        """Execute the remove bookmark operation."""
        if not self.can_execute():
            return
        self.main_window.remove_selected_bookmark()
