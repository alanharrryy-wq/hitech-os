"""Navigate back command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..command_dispatcher import Command

if TYPE_CHECKING:
    from ..navigation_controller import NavigationController


class NavigateBackCommand(Command):
    """
    Navigate to previous preview in history.

    Dependencies:
        navigation_controller: NavigationController instance

    Example:
        cmd = NavigateBackCommand(navigation_controller)
        cmd.execute()
    """

    def __init__(self, navigation_controller: NavigationController) -> None:
        """
        Initialize the command.

        Args:
            navigation_controller: NavigationController to use
        """
        self.navigation_controller = navigation_controller

    def can_execute(self) -> bool:
        """Check if back navigation is available."""
        if not self.navigation_controller:
            return False
        return self.navigation_controller._preview_history_index > 0

    def execute(self) -> None:
        """Execute the back navigation."""
        self.navigation_controller.navigate_back()
