from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable

from .heartbeat import Heartbeat
from .runtime_repair import ensure_runtime_health
from .stale_lock_cleanup import cleanup_stale_locks
from .zombie_guard import detect_zombie_state
from ..shared.runtime_paths import RuntimePaths, build_runtime_paths

class SentinelSupervisor:
    def __init__(self, paths: RuntimePaths | None = None) -> None:
        self.paths = (paths or build_runtime_paths()).ensure()

    def supervised_run(self, task: Callable[[], Any], run_id: str) -> dict[str, Any]:
        ensure_runtime_health(self.paths)
        heartbeat_path = self.paths.state_root / "heartbeat.json"
        heartbeat = Heartbeat(run_id=run_id, pid=os.getpid())
        heartbeat.write(heartbeat_path)
        result = task()
        heartbeat.status = "completed"
        heartbeat.touch()
        heartbeat.write(heartbeat_path)
        return {
            "run_id": run_id,
            "result": result,
            "heartbeat_file": str(heartbeat_path),
            "zombie_detected": detect_zombie_state(heartbeat_path),
        }

def supervised_run(task: Callable[[], Any], run_id: str, paths: RuntimePaths | None = None) -> dict[str, Any]:
    supervisor = SentinelSupervisor(paths=paths)
    lock_dir = supervisor.paths.state_root / "locks"
    cleaned = cleanup_stale_locks(lock_dir)
    payload = supervisor.supervised_run(task, run_id=run_id)
    payload["cleaned_locks"] = cleaned
    return payload
