"""Export results command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..command_dispatcher import Command

if TYPE_CHECKING:
    from ..search_controller import SearchController


class ExportResultsCommand(Command):
    """
    Exports search results to file.

    Dependencies:
        search_controller: SearchController instance

    Example:
        cmd = ExportResultsCommand(search_controller)
        cmd.execute()
    """

    def __init__(self, search_controller: SearchController) -> None:
        """
        Initialize the command.

        Args:
            search_controller: SearchController to use for exporting
        """
        self.search_controller = search_controller

    def can_execute(self) -> bool:
        """Check if search controller is available and has results."""
        return (
            self.search_controller is not None
            and self.search_controller.main.results_model is not None
            and self.search_controller.main.results_model.rowCount() > 0
        )

    def execute(self) -> None:
        """Execute the export operation."""
        self.search_controller.export_results()
