from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

EventName = Literal[
    "session_created",
    "session_cloned",
    "session_closed",
    "scope_loaded",
    "scope_cleared",
    "ops_loaded",
    "ops_saved",
    "validation_started",
    "validation_finished",
    "plan_started",
    "plan_finished",
    "apply_started",
    "apply_finished",
    "rollback_started",
    "rollback_finished",
    "filesystem_changed",
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
    "validation_started",
    "validation_finished",
    "plan_started",
    "plan_finished",
    "apply_started",
    "apply_finished",
    "rollback_started",
    "rollback_finished",
    "filesystem_changed",
    "session_marked_stale",
)


@dataclass(slots=True)
class AppEvent:
    name: EventName
    session_id: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
