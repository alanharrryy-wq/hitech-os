from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pya.contracts.event_contracts import build_event, validate_event


class EventBus:
    def __init__(self, traces_dir: Path, execution_id: str, timestamp: str):
        self._events: list[dict[str, Any]] = []
        self._traces_dir = traces_dir
        self._execution_id = execution_id
        self._timestamp = timestamp

    @property
    def events(self) -> list[dict[str, Any]]:
        return list(self._events)

    def emit(self, *, name: str, producer: str, target: str, payload: dict[str, Any], severity: str = "info", correlation_id: str | None = None) -> dict[str, Any]:
        event = build_event(
            name=name,
            producer=producer,
            target=target,
            payload={**payload, "execution_id": self._execution_id},
            severity=severity,
            timestamp=self._timestamp,
            correlation_id=correlation_id,
        )
        validate_event(event)
        self._events.append(event)
        return event

    def flush(self) -> Path:
        self._traces_dir.mkdir(parents=True, exist_ok=True)
        target = self._traces_dir / f"events_{self._execution_id}.json"
        target.write_text(json.dumps(self._events, indent=2, sort_keys=True), encoding="utf-8")
        return target
