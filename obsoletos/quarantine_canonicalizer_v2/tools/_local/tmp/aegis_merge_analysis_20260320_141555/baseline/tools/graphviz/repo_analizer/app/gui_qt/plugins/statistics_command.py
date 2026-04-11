"""Display statistics command for file statistics plugin."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..command_dispatcher import Command

if TYPE_CHECKING:
    from .file_statistics_plugin import FileStatisticsPlugin


class DisplayStatisticsCommand(Command):
    """
    Display file statistics.

    Example:
        cmd = DisplayStatisticsCommand(plugin)
        stats = cmd.execute()
    """

    def __init__(self, plugin: FileStatisticsPlugin) -> None:
        """
        Initialize the command.

        Args:
            plugin: FileStatisticsPlugin instance
        """
        self.plugin = plugin

    def can_execute(self) -> bool:
        """Check if plugin is available."""
        return self.plugin is not None and self.plugin.enabled

    def execute(self) -> dict[str, int]:
        """
        Execute the command.

        Returns:
            Statistics dictionary
        """
        stats = self.plugin.get_statistics()
        return stats
