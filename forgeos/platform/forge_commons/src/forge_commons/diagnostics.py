from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping

from .lifecycle import CapabilityLifecycle, CapabilityRuntimeState


@dataclass(frozen=True)
class DiagnosticEvent:
    severity: str
    component: str
    message: str
    actor: str
    metadata: Mapping[str, str]
    occurred_at_utc: str


class DiagnosticsCapability:
    """Shared diagnostics capability for runtime evidence."""

    capability_id = "forge.commons.diagnostics"

    def __init__(self) -> None:
        self.lifecycle = CapabilityLifecycle(self.capability_id)
        self._events: list[DiagnosticEvent] = []

    def activate(self) -> CapabilityRuntimeState:
        return self.lifecycle.activate()

    def dispose(self) -> CapabilityRuntimeState:
        self._events.clear()
        return self.lifecycle.dispose()

    def emit(
        self,
        severity: str,
        component: str,
        message: str,
        actor: str,
        metadata: Mapping[str, str] | None = None,
    ) -> DiagnosticEvent:
        event = DiagnosticEvent(
            severity=severity,
            component=component,
            message=message,
            actor=actor,
            metadata=metadata or {},
            occurred_at_utc=datetime.now(tz=timezone.utc).isoformat(),
        )
        self._events.append(event)
        return event

    def events(self) -> list[DiagnosticEvent]:
        return list(self._events)

    def health_snapshot(self) -> dict[str, int]:
        counts: dict[str, int] = {"info": 0, "warning": 0, "error": 0}
        for event in self._events:
            key = event.severity.lower()
            if key not in counts:
                counts[key] = 0
            counts[key] += 1
        return counts
