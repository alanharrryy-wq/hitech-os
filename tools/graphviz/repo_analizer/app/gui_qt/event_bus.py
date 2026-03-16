"""
Event Bus System for loosely-coupled controller communication.

Provides a lightweight publish-subscribe mechanism that allows controllers
to communicate without direct dependencies.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List


class EventBus:
    """
    Lightweight event bus for pub/sub communication between controllers.

    Allows controllers to publish events and subscribe to events without
    knowing about each other.

    Example:
        bus = EventBus()
        bus.subscribe('file_selected', handler)
        bus.publish('file_selected', {'relpath': 'src/main.py', 'line': 10})
    """

    def __init__(self) -> None:
        """Initialize the event bus."""
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: List[tuple[str, Any]] = []
        self._history_max_size = 100

    def subscribe(self, event: str, handler: Callable) -> Callable:
        """
        Subscribe to an event.

        Args:
            event: Event name (e.g., 'file_selected', 'search_completed')
            handler: Callable that takes payload as argument

        Returns:
            Unsubscribe function for easy cleanup

        Example:
            def on_file_selected(payload):
                print(f"File: {payload['relpath']}")

            unsub = bus.subscribe('file_selected', on_file_selected)
            unsub()  # Unsubscribe when done
        """
        if event not in self._subscribers:
            self._subscribers[event] = []

        self._subscribers[event].append(handler)

        # Return unsubscribe function
        def unsubscribe() -> None:
            if handler in self._subscribers[event]:
                self._subscribers[event].remove(handler)

        return unsubscribe

    def publish(self, event: str, payload: Any = None) -> None:
        """
        Publish an event.

        Args:
            event: Event name
            payload: Event data (dict, object, or None)

        Example:
            bus.publish('file_selected', {'relpath': 'src/main.py', 'line': 10})
        """
        # Record in history
        self._event_history.append((event, payload))
        if len(self._event_history) > self._history_max_size:
            self._event_history.pop(0)

        # Notify subscribers
        if event not in self._subscribers:
            return

        for handler in self._subscribers[event]:
            try:
                handler(payload)
            except Exception as e:
                # Log but don't raise - prevent one handler from breaking others
                print(f"Error in event handler for '{event}': {e}")

    def has_subscribers(self, event: str) -> bool:
        """Check if event has subscribers."""
        return event in self._subscribers and len(self._subscribers[event]) > 0

    def clear(self) -> None:
        """Clear all subscribers and history."""
        self._subscribers.clear()
        self._event_history.clear()

    def get_history(self, event: str | None = None) -> List[tuple[str, Any]]:
        """
        Get event history.

        Args:
            event: Optional event name to filter by

        Returns:
            List of (event_name, payload) tuples
        """
        if event is None:
            return self._event_history.copy()
        return [(e, p) for e, p in self._event_history if e == event]


# Standard event names
class Events:
    """Standard event names used throughout the application."""

    # Index events
    INDEX_STARTED = 'index_started'
    INDEX_COMPLETED = 'index_completed'
    INDEX_FAILED = 'index_failed'

    # Tree events
    TREE_REBUILT = 'tree_rebuilt'
    FILE_SELECTED = 'file_selected'
    TREE_FILTER_CHANGED = 'tree_filter_changed'

    # Search events
    SEARCH_STARTED = 'search_started'
    SEARCH_COMPLETED = 'search_completed'
    SEARCH_FAILED = 'search_failed'
    SEARCH_CLEARED = 'search_cleared'

    # Preview events
    PREVIEW_OPENED = 'preview_opened'
    PREVIEW_CLOSED = 'preview_closed'

    # Navigation events
    NAVIGATION_CHANGED = 'navigation_changed'
    NAVIGATION_BACK = 'navigation_back'
    NAVIGATION_FORWARD = 'navigation_forward'

    # Layout events
    LAYOUT_CHANGED = 'layout_changed'
    LAYOUT_SAVED = 'layout_saved'

    # Skin/Theme events
    SKIN_CHANGED = 'skin_changed'

    # Bookmark events
    BOOKMARK_ADDED = 'bookmark_added'
    BOOKMARK_REMOVED = 'bookmark_removed'
    BOOKMARKS_REFRESHED = 'bookmarks_refreshed'

    # General events
    ERROR_OCCURRED = 'error_occurred'
    STATUS_CHANGED = 'status_changed'
