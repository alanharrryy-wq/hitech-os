from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Mapping

from .exceptions import KernelRuleViolation


class RuntimeState(str, Enum):
    DISCOVERED = "discovered"
    REGISTERED = "registered"
    PREPARED = "prepared"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    FAULTED = "faulted"
    DISPOSING = "disposing"
    DISPOSED = "disposed"


_ALLOWED_TRANSITIONS: dict[RuntimeState, set[RuntimeState]] = {
    RuntimeState.DISCOVERED: {RuntimeState.REGISTERED},
    RuntimeState.REGISTERED: {RuntimeState.PREPARED, RuntimeState.DISPOSING},
    RuntimeState.PREPARED: {RuntimeState.ACTIVE, RuntimeState.DISPOSING},
    RuntimeState.ACTIVE: {
        RuntimeState.SUSPENDED,
        RuntimeState.FAULTED,
        RuntimeState.DISPOSING,
    },
    RuntimeState.SUSPENDED: {RuntimeState.ACTIVE, RuntimeState.DISPOSING},
    RuntimeState.FAULTED: {RuntimeState.DISPOSING},
    RuntimeState.DISPOSING: {RuntimeState.DISPOSED},
    RuntimeState.DISPOSED: set(),
}


@dataclass(frozen=True)
class LifecycleEvent:
    runtime_id: str
    from_state: RuntimeState
    to_state: RuntimeState
    reason: str
    metadata: Mapping[str, str]
    occurred_at_utc: str


class LifecycleAuthority:
    """Kernel-owned lifecycle authority for runtime units."""

    def __init__(self) -> None:
        self._states: dict[str, RuntimeState] = {}
        self._events: list[LifecycleEvent] = []

    def register_runtime(
        self,
        runtime_id: str,
        metadata: Mapping[str, str] | None = None,
    ) -> RuntimeState:
        if not runtime_id:
            raise KernelRuleViolation("runtime_id is required")
        if runtime_id in self._states:
            raise KernelRuleViolation(f"runtime '{runtime_id}' is already registered")
        self._states[runtime_id] = RuntimeState.REGISTERED
        self._record_event(
            runtime_id=runtime_id,
            from_state=RuntimeState.DISCOVERED,
            to_state=RuntimeState.REGISTERED,
            reason="runtime_registered",
            metadata=metadata or {},
        )
        return RuntimeState.REGISTERED

    def transition(
        self,
        runtime_id: str,
        target_state: RuntimeState,
        reason: str,
        metadata: Mapping[str, str] | None = None,
    ) -> RuntimeState:
        if runtime_id not in self._states:
            raise KernelRuleViolation(f"runtime '{runtime_id}' is not registered")
        current = self._states[runtime_id]
        allowed = _ALLOWED_TRANSITIONS[current]
        if target_state not in allowed:
            raise KernelRuleViolation(
                f"invalid lifecycle transition: {current.value} -> {target_state.value}"
            )
        self._states[runtime_id] = target_state
        self._record_event(
            runtime_id=runtime_id,
            from_state=current,
            to_state=target_state,
            reason=reason,
            metadata=metadata or {},
        )
        return target_state

    def mark_fault(
        self,
        runtime_id: str,
        reason: str,
        metadata: Mapping[str, str] | None = None,
    ) -> RuntimeState:
        return self.transition(
            runtime_id=runtime_id,
            target_state=RuntimeState.FAULTED,
            reason=reason,
            metadata=metadata,
        )

    def state_for(self, runtime_id: str) -> RuntimeState:
        if runtime_id not in self._states:
            raise KernelRuleViolation(f"runtime '{runtime_id}' is not registered")
        return self._states[runtime_id]

    def history(self, runtime_id: str | None = None) -> list[LifecycleEvent]:
        if runtime_id is None:
            return list(self._events)
        return [event for event in self._events if event.runtime_id == runtime_id]

    def _record_event(
        self,
        runtime_id: str,
        from_state: RuntimeState,
        to_state: RuntimeState,
        reason: str,
        metadata: Mapping[str, str],
    ) -> None:
        timestamp = datetime.now(tz=timezone.utc).isoformat()
        self._events.append(
            LifecycleEvent(
                runtime_id=runtime_id,
                from_state=from_state,
                to_state=to_state,
                reason=reason,
                metadata=metadata,
                occurred_at_utc=timestamp,
            )
        )
