from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, TypedDict

from domain.ids import SessionId, parse_session_id

EventName = Literal[
    "session_created",
    "session_cloned",
    "session_closed",
    "scope_loaded",
    "scope_cleared",
    "ops_loaded",
    "ops_saved",
    "ops_edited",
    "validation_started",
    "validation_finished",
    "plan_started",
    "plan_finished",
    "apply_started",
    "apply_finished",
    "rollback_started",
    "rollback_finished",
    "refresh_requested",
    "refresh_completed",
    "filesystem_changed",
    "external_change_detected",
    "session_marked_stale",
]

REQUIRED_EVENT_NAMES: tuple[EventName, ...] = (
    "session_created",
    "session_cloned",
    "session_closed",
    "scope_loaded",
    "scope_cleared",
    "ops_loaded",
    "ops_saved",
    "ops_edited",
    "validation_started",
    "validation_finished",
    "plan_started",
    "plan_finished",
    "apply_started",
    "apply_finished",
    "rollback_started",
    "rollback_finished",
    "refresh_requested",
    "refresh_completed",
    "filesystem_changed",
    "external_change_detected",
    "session_marked_stale",
)


class ScopeLoadedPayload(TypedDict, total=False):
    count: int
    scope_kind: str
    root_dir: str


class OpsEditedPayload(TypedDict, total=False):
    revision: int
    content_hash: str
    source_path: str


class ExternalChangePayload(TypedDict, total=False):
    path: str
    reason: str


class RefreshRequestedPayload(TypedDict, total=False):
    trigger: str
    previous_state: str


class RefreshCompletedPayload(TypedDict, total=False):
    ok: bool
    summary: str
    restored_state: str


REQUIRED_SESSION_EVENT_NAMES: tuple[EventName, ...] = REQUIRED_EVENT_NAMES


@dataclass(slots=True)
class AppEvent:
    name: EventName
    session_id: SessionId | str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.session_id is not None:
            raw = str(self.session_id).strip()
            self.session_id = parse_session_id(raw) if raw else None

        if self.name in REQUIRED_SESSION_EVENT_NAMES and self.session_id is None:
            raise ValueError(f"Event '{self.name}' requires session_id.")
