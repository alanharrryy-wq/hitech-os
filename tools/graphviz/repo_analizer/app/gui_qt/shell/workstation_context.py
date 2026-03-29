from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from PySide6.QtCore import QObject

from ..event_bus import Events


@dataclass(slots=True)
class WorkstationContext:
    active_group: str = ""
    repo_root: str = ""
    repo_name: str = ""
    active_tool_id: str = ""
    active_file_relpath: str = ""
    active_query: str = ""
    last_command: str = ""
    active_scope: str = ""
    active_extension: str = ""
    results_count: int = 0
    runtime_density: str = ""
    runtime_motion: str = ""
    runtime_performance: str = ""
    status_text: str = ""
    hostname: str = ""
    tunnel_id: str = ""
    origin_expected: str = ""
    origin_observed: str = ""
    config_path: str = ""
    last_good_state: str = ""
    current_error: str = ""
    last_check_time: str = ""


class WorkstationContextRuntime(QObject):
    """Central app-wide context shared across shell and tools."""

    def __init__(self, event_bus, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.event_bus = event_bus
        self._context = WorkstationContext()

    @property
    def current(self) -> WorkstationContext:
        return self._context

    def update(self, **changes: Any) -> WorkstationContext:
        before = asdict(self._context)
        payload = dict(before)
        changed = False
        for key, value in changes.items():
            if key not in payload:
                continue
            if payload[key] != value:
                payload[key] = value
                changed = True
        if not changed:
            return self._context

        self._context = WorkstationContext(**payload)
        self.event_bus.publish(
            Events.WORKSTATION_CONTEXT_CHANGED,
            asdict(self._context),
        )
        return self._context

    def snapshot(self) -> dict[str, Any]:
        return asdict(self._context)
