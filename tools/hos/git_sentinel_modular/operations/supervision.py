from __future__ import annotations

from ..sentinel_supervisor.runtime_repair import ensure_runtime_health
from ..sentinel_supervisor.stale_lock_cleanup import cleanup_stale_locks
from ..sentinel_supervisor.zombie_guard import detect_zombie_state
from ..shared.status_payloads import SchedulerStatus, SupervisorStatus
from .runtime import get_runtime_paths

def build_supervisor_status() -> SupervisorStatus:
    paths = get_runtime_paths()
    heartbeat = paths.state_root / "heartbeat.json"
    cleaned = cleanup_stale_locks(paths.state_root / "locks")
    zombie = detect_zombie_state(heartbeat)
    ensure_runtime_health(paths)
    return SupervisorStatus(
        status="attention" if zombie else "ready",
        stale_lock_count=cleaned,
        zombie_detected=zombie,
        heartbeat_file=str(heartbeat),
    )

def build_scheduler_status() -> SchedulerStatus:
    return SchedulerStatus(
        status="manual_or_external",
        cadence="package-owned dispatcher",
        next_action="run package CLI or external scheduler wrapper",
    )
