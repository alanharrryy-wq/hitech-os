from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from .exceptions import CommonsRuleViolation


class CapabilityRuntimeState(str, Enum):
    DECLARED = "declared"
    VALIDATED = "validated"
    READY = "ready"
    SERVING = "serving"
    DEGRADED = "degraded"
    DISPOSING = "disposing"
    DISPOSED = "disposed"


@dataclass(frozen=True)
class CapabilityLifecycleEvent:
    capability_id: str
    from_state: CapabilityRuntimeState
    to_state: CapabilityRuntimeState
    reason: str
    occurred_at_utc: str


_ALLOWED_TRANSITIONS: dict[CapabilityRuntimeState, set[CapabilityRuntimeState]] = {
    CapabilityRuntimeState.DECLARED: {CapabilityRuntimeState.VALIDATED},
    CapabilityRuntimeState.VALIDATED: {CapabilityRuntimeState.READY, CapabilityRuntimeState.DISPOSING},
    CapabilityRuntimeState.READY: {CapabilityRuntimeState.SERVING, CapabilityRuntimeState.DISPOSING},
    CapabilityRuntimeState.SERVING: {
        CapabilityRuntimeState.DEGRADED,
        CapabilityRuntimeState.DISPOSING,
    },
    CapabilityRuntimeState.DEGRADED: {
        CapabilityRuntimeState.SERVING,
        CapabilityRuntimeState.DISPOSING,
    },
    CapabilityRuntimeState.DISPOSING: {CapabilityRuntimeState.DISPOSED},
    CapabilityRuntimeState.DISPOSED: set(),
}


class CapabilityLifecycle:
    """Lifecycle controller for commons capabilities."""

    def __init__(self, capability_id: str) -> None:
        if not capability_id:
            raise CommonsRuleViolation("capability_id is required")
        self._capability_id = capability_id
        self._state = CapabilityRuntimeState.DECLARED
        self._events: list[CapabilityLifecycleEvent] = []

    @property
    def state(self) -> CapabilityRuntimeState:
        return self._state

    def transition(self, target_state: CapabilityRuntimeState, reason: str) -> CapabilityRuntimeState:
        allowed = _ALLOWED_TRANSITIONS[self._state]
        if target_state not in allowed:
            raise CommonsRuleViolation(
                f"invalid capability transition: {self._state.value} -> {target_state.value}"
            )
        previous = self._state
        self._state = target_state
        self._events.append(
            CapabilityLifecycleEvent(
                capability_id=self._capability_id,
                from_state=previous,
                to_state=target_state,
                reason=reason,
                occurred_at_utc=datetime.now(tz=timezone.utc).isoformat(),
            )
        )
        return self._state

    def activate(self) -> CapabilityRuntimeState:
        self.transition(CapabilityRuntimeState.VALIDATED, "validated")
        self.transition(CapabilityRuntimeState.READY, "ready")
        return self.transition(CapabilityRuntimeState.SERVING, "serving")

    def dispose(self) -> CapabilityRuntimeState:
        if self._state is CapabilityRuntimeState.DISPOSED:
            return self._state
        if self._state is not CapabilityRuntimeState.DISPOSING:
            self.transition(CapabilityRuntimeState.DISPOSING, "disposing")
        return self.transition(CapabilityRuntimeState.DISPOSED, "disposed")

    def history(self) -> list[CapabilityLifecycleEvent]:
        return list(self._events)
