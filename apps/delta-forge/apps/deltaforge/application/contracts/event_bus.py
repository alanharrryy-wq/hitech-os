from __future__ import annotations

from typing import Callable, Protocol, Sequence

from domain.events import AppEvent
from domain.ids import SessionId

EventHandler = Callable[[AppEvent], None]


class EventBus(Protocol):
    def publish(self, event: AppEvent) -> None:
        ...

    def publish_many(self, events: Sequence[AppEvent]) -> None:
        ...

    def read_for_session(
        self,
        session_id: SessionId,
        *,
        limit: int | None = None,
        after_event_id: str | None = None,
    ) -> Sequence[AppEvent]:
        ...

    def subscribe(self, session_id: SessionId, handler: EventHandler) -> None:
        ...

    def unsubscribe(self, session_id: SessionId, handler: EventHandler) -> None:
        ...
