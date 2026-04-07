from __future__ import annotations

from collections import defaultdict
from typing import Callable

from domain.events import AppEvent, EventName

EventHandler = Callable[[AppEvent], None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[EventName, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_name: EventName, handler: EventHandler) -> None:
        self._handlers[event_name].append(handler)

    def emit(self, event: AppEvent) -> None:
        handlers = list(self._handlers.get(event.name, []))
        for handler in handlers:
            handler(event)
