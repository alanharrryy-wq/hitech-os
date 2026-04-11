"""Execute search command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..command_dispatcher import Command

if TYPE_CHECKING:
    from ..search_controller import SearchController


class ExecuteSearchCommand(Command):
    """
    Executes a search operation.

    Dependencies:
        search_controller: SearchController instance

    Trigger:
        Emits 'search_started' and 'search_completed' events via event bus

    Example:
        cmd = ExecuteSearchCommand(search_controller)
        cmd.execute()
    """

    def __init__(self, search_controller: SearchController) -> None:
        """
        Initialize the command.

        Args:
            search_controller: SearchController to use for searching
        """
        self.search_controller = search_controller

    def can_execute(self) -> bool:
        """Check if search controller is available."""
        return self.search_controller is not None

    def execute(self) -> None:
        """Execute the search operation."""
        self.search_controller.start_search()
