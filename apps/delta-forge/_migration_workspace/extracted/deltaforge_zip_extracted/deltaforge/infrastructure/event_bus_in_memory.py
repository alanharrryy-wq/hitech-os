from __future__ import annotations

from collections import defaultdict
from threading import RLock
from typing import Any, Callable, DefaultDict


EventHandler = Callable[[Any], None]


class InMemoryEventBus:
    """Minimal in-memory event bus with compatibility aliases."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._subscribers: DefaultDict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: EventHandler) -> Callable[[], None]:
        if not event_name:
            raise ValueError("event_name must be a non-empty string")

        with self._lock:
            self._subscribers[event_name].append(handler)

        def _unsubscribe() -> None:
            self.unsubscribe(event_name, handler)

        return _unsubscribe

    def on(self, event_name: str, handler: EventHandler) -> Callable[[], None]:
        return self.subscribe(event_name, handler)

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        with self._lock:
            handlers = self._subscribers.get(event_name)
            if not handlers:
                return

            remaining = [existing for existing in handlers if existing is not handler]
            if remaining:
                self._subscribers[event_name] = remaining
            else:
                self._subscribers.pop(event_name, None)

    def publish(self, event_name: str, payload: Any = None) -> None:
        with self._lock:
            handlers = tuple(self._subscribers.get(event_name, ()))

        for handler in handlers:
            handler(payload)

    def emit(self, event_name: str, payload: Any = None) -> None:
        self.publish(event_name, payload)

    def emit_event(self, event_or_name: Any, payload: Any = None) -> None:
        if isinstance(event_or_name, str):
            self.publish(event_or_name, payload)
            return

        event_name = self._infer_event_name(event_or_name)
        self.publish(event_name, event_or_name)

    def clear(self) -> None:
        with self._lock:
            self._subscribers.clear()

    def subscriber_count(self, event_name: str) -> int:
        with self._lock:
            return len(self._subscribers.get(event_name, ()))

    @staticmethod
    def _infer_event_name(event: Any) -> str:
        if isinstance(event, dict):
            for key in ("event_name", "name", "type"):
                value = event.get(key)
                if isinstance(value, str) and value:
                    return value

        for attr in ("event_name", "name", "type"):
            value = getattr(event, attr, None)
            if isinstance(value, str) and value:
                return value

        raise ValueError("Unable to infer event name from payload")
