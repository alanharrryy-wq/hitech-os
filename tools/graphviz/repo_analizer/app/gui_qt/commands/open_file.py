"""Open file command."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..command_dispatcher import Command

if TYPE_CHECKING:
    from ..preview_controller import PreviewController


class OpenFileCommand(Command):
    """
    Opens a file for preview.

    Dependencies:
        preview_controller: PreviewController instance

    Example:
        cmd = OpenFileCommand(preview_controller)
        cmd.execute(relpath='src/main.py', line=10)
    """

    def __init__(self, preview_controller: PreviewController) -> None:
        """
        Initialize the command.

        Args:
            preview_controller: PreviewController to use for opening file
        """
        self.preview_controller = preview_controller

    def can_execute(self) -> bool:
        """Check if preview controller is available."""
        return self.preview_controller is not None

    def execute(
        self, relpath: str, line: int = 0, add_history: bool = True
    ) -> None:
        """
        Execute the command.

        Args:
            relpath: Relative path to file
            line: Line number to jump to
            add_history: Whether to add to navigation history
        """
        self.preview_controller.show_preview_for_relpath(
            relpath, line, add_history=add_history
        )
