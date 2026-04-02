from __future__ import annotations

from dataclasses import dataclass
from typing import Final


CANONICAL_STATES: Final[tuple[str, ...]] = (
    "NEW",
    "IDLE",
    "DIRTY_OR_STALE",
    "VALIDATING",
    "PLANNING",
    "APPLYING",
    "ROLLING_BACK",
    "REFRESHING",
    "FAILED",
    "CLOSED",
)

_ACTIVE_STATES: Final[frozenset[str]] = frozenset(
    {"VALIDATING", "PLANNING", "APPLYING", "ROLLING_BACK", "REFRESHING"}
)

_TERMINAL_STATES: Final[frozenset[str]] = frozenset({"CLOSED"})

_STATE_ALIASES: Final[dict[str, str]] = {
    "": "IDLE",
    "NONE": "IDLE",
    "READY": "IDLE",
    "CLEAN": "IDLE",
    "DIRTY": "DIRTY_OR_STALE",
    "STALE": "DIRTY_OR_STALE",
    "DIRTY_STALE": "DIRTY_OR_STALE",
    "DIRTY_OR_REFRESH": "DIRTY_OR_STALE",
    "REFRESH_NEEDED": "DIRTY_OR_STALE",
    "ROLLBACK": "ROLLING_BACK",
    "ROLLINGBACK": "ROLLING_BACK",
    "PLAN": "PLANNING",
    "PLANNED": "PLANNING",
    "VALIDATE": "VALIDATING",
    "APPLY": "APPLYING",
    "REFRESH": "REFRESHING",
    "ERROR": "FAILED",
}

LEGAL_TRANSITIONS: Final[dict[str, frozenset[str]]] = {
    "NEW": frozenset({"IDLE", "DIRTY_OR_STALE", "CLOSED"}),
    "IDLE": frozenset(
        {"DIRTY_OR_STALE", "VALIDATING", "PLANNING", "APPLYING", "ROLLING_BACK", "REFRESHING", "CLOSED"}
    ),
    "DIRTY_OR_STALE": frozenset(
        {"IDLE", "VALIDATING", "PLANNING", "APPLYING", "ROLLING_BACK", "REFRESHING", "CLOSED"}
    ),
    "VALIDATING": frozenset({"IDLE", "DIRTY_OR_STALE", "FAILED"}),
    "PLANNING": frozenset({"IDLE", "DIRTY_OR_STALE", "FAILED"}),
    "APPLYING": frozenset({"IDLE", "DIRTY_OR_STALE", "FAILED"}),
    "ROLLING_BACK": frozenset({"IDLE", "DIRTY_OR_STALE", "FAILED"}),
    "REFRESHING": frozenset({"IDLE", "DIRTY_OR_STALE", "FAILED"}),
    "FAILED": frozenset({"IDLE", "DIRTY_OR_STALE", "REFRESHING", "CLOSED"}),
    "CLOSED": frozenset(),
}


@dataclass(slots=True, frozen=True)
class InvalidTransitionError(ValueError):
    current: str
    target: str
    allowed: tuple[str, ...]

    def __str__(self) -> str:
        allowed = ", ".join(self.allowed) if self.allowed else "(none)"
        return f"Illegal session transition: {self.current} -> {self.target}. Allowed: {allowed}"


def normalize_state(value: object | None) -> str:
    if value is None:
        raw = ""
    elif hasattr(value, "name") and isinstance(getattr(value, "name"), str):
        raw = str(getattr(value, "name"))
    elif hasattr(value, "value"):
        raw = str(getattr(value, "value"))
    else:
        raw = str(value)

    cleaned = raw.strip().replace("-", "_").replace(" ", "_").upper()
    canonical = _STATE_ALIASES.get(cleaned, cleaned or "IDLE")
    return canonical


def allowed_targets(current: object | None) -> tuple[str, ...]:
    current_name = normalize_state(current)
    allowed = LEGAL_TRANSITIONS.get(current_name, frozenset())
    return tuple(sorted(allowed))


def can_transition(current: object | None, target: object | None) -> bool:
    current_name = normalize_state(current)
    target_name = normalize_state(target)

    if current_name == target_name:
        return True

    allowed = LEGAL_TRANSITIONS.get(current_name, frozenset())
    return target_name in allowed


def assert_transition(current: object | None, target: object | None) -> str:
    current_name = normalize_state(current)
    target_name = normalize_state(target)

    if not can_transition(current_name, target_name):
        raise InvalidTransitionError(
            current=current_name,
            target=target_name,
            allowed=allowed_targets(current_name),
        )
    return target_name


def derive_idle_state(dirty: bool, stale: bool) -> str:
    return "DIRTY_OR_STALE" if bool(dirty or stale) else "IDLE"


def is_busy_state(state: object | None) -> bool:
    return normalize_state(state) in _ACTIVE_STATES


def is_terminal_state(state: object | None) -> bool:
    return normalize_state(state) in _TERMINAL_STATES


__all__ = [
    "CANONICAL_STATES",
    "LEGAL_TRANSITIONS",
    "InvalidTransitionError",
    "allowed_targets",
    "assert_transition",
    "can_transition",
    "derive_idle_state",
    "is_busy_state",
    "is_terminal_state",
    "normalize_state",
]
