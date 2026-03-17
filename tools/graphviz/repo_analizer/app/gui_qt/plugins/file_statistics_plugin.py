"""
Example Plugin: File Statistics

This plugin demonstrates the plugin architecture by adding file statistics
functionality. It monitors file selections and tracks statistics.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..plugin_base import Plugin, PluginContext

if TYPE_CHECKING:
    pass


class FileStatisticsPlugin(Plugin):
    """
    File Statistics Plugin.

    Demonstrates plugin capabilities by tracking file statistics
    and providing example event subscriptions and command registration.

    Features:
    - Tracks file selections
    - Maintains statistics (files opened, searches performed)
    - Provides a simple stats display command
    """

    name = 'file_statistics'
    version = '1.0.0'
    description = 'Track file selection and search statistics'
    author = 'Repo Analyzer Team'

    def __init__(self) -> None:
        """Initialize the plugin."""
        super().__init__()
        self.stats = {
            'files_opened': 0,
            'searches_executed': 0,
            'previews_shown': 0,
        }

    def initialize(self, context: PluginContext) -> None:
        """
        Initialize the plugin.

        Subscribes to events and registers commands.

        Args:
            context: PluginContext
        """
        # Subscribe to events
        self._subscribe_to_events(context)

        # Register commands
        self._register_commands(context)

        print(f"✓ Plugin '{self.name}' initialized")

    def _subscribe_to_events(self, context: PluginContext) -> None:
        """Subscribe to application events."""
        from ..event_bus import Events

        # Track file selections
        self.subscribe_event(context, Events.FILE_SELECTED, self._on_file_selected)

        # Track search execution
        self.subscribe_event(context, Events.SEARCH_COMPLETED, self._on_search_completed)

        # Track preview
        self.subscribe_event(context, Events.PREVIEW_OPENED, self._on_preview_opened)

    def _register_commands(self, context: PluginContext) -> None:
        """Register plugin commands."""
        from .statistics_command import DisplayStatisticsCommand

        cmd = DisplayStatisticsCommand(self)
        self.register_command(context, 'show_statistics', cmd)

    def _on_file_selected(self, payload: Any) -> None:
        """Handle file selection event."""
        self.stats['files_opened'] += 1

    def _on_search_completed(self, payload: Any) -> None:
        """Handle search completion event."""
        self.stats['searches_executed'] += 1

    def _on_preview_opened(self, payload: Any) -> None:
        """Handle preview opened event."""
        self.stats['previews_shown'] += 1

    def get_statistics(self) -> dict:
        """Get current statistics."""
        return self.stats.copy()

    def reset_statistics(self) -> None:
        """Reset statistics."""
        for key in self.stats:
            self.stats[key] = 0

    def shutdown(self) -> None:
        """Clean up when plugin is unloaded."""
        super().shutdown()
        print(f"✓ Plugin '{self.name}' shut down")
