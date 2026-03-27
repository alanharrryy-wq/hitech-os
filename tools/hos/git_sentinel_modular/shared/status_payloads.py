from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass(slots=True)
class StageCounts:
    planned_actions: int = 0
    applied: int = 0
    blocked: int = 0
    warnings: int = 0
    added: int = 0
    removed: int = 0
    changed: int = 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)

@dataclass(slots=True)
class StageStatus:
    name: str
    status: str
    detail: str = ""
    counts: StageCounts = field(default_factory=StageCounts)
    updated_at: str = field(default_factory=utc_now_iso)
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["counts"] = self.counts.to_dict()
        return payload

@dataclass(slots=True)
class RuntimeStatus:
    repo_root: str
    runtime_root: str
    shadow_root: str
    logs_root: str
    state_root: str
    status: str
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(slots=True)
class SupervisorStatus:
    status: str
    stale_lock_count: int
    zombie_detected: bool
    heartbeat_file: str
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(slots=True)
class SchedulerStatus:
    status: str
    cadence: str
    next_action: str
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(slots=True)
class CombinedHealthSummary:
    overall_status: str
    runtime: RuntimeStatus
    supervisor: SupervisorStatus
    scheduler: SchedulerStatus
    plugins: list[dict[str, Any]] = field(default_factory=list)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_status": self.overall_status,
            "runtime": self.runtime.to_dict(),
            "supervisor": self.supervisor.to_dict(),
            "scheduler": self.scheduler.to_dict(),
            "plugins": self.plugins,
            "updated_at": self.updated_at,
        }
