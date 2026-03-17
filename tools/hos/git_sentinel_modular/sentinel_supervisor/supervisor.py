from pathlib import Path
from .runtime_repair import ensure_runtime_health
from .stale_lock_cleanup import cleanup_stale_locks
from .zombie_guard import detect_zombie_state
from .heartbeat import Heartbeat

class SentinelSupervisor:
    def __init__(
        self,
        runtime_root,
        max_lock_age_seconds=1800,
        zombie_after_seconds=900,
    ):
        self.runtime_root = Path(runtime_root)
        self.max_lock_age_seconds = max_lock_age_seconds
        self.zombie_after_seconds = zombie_after_seconds
        self.heartbeat = Heartbeat(self.runtime_root)

    def preflight(self):
        runtime_status = ensure_runtime_health(self.runtime_root)
        zombie_status = detect_zombie_state(
            self.runtime_root,
            zombie_after_seconds=self.zombie_after_seconds,
        )
        cleaned_locks = cleanup_stale_locks(
            self.runtime_root,
            max_lock_age_seconds=self.max_lock_age_seconds,
        )

        return {
            "runtime_status": runtime_status,
            "zombie_status": zombie_status,
            "cleaned_locks": cleaned_locks,
        }

    def beat(self):
        self.heartbeat.touch()

def supervised_run(run_callable, runtime_root, on_tick=None):
    supervisor = SentinelSupervisor(runtime_root=runtime_root)
    status = supervisor.preflight()

    supervisor.beat()

    try:
        result = run_callable(supervisor)
        supervisor.beat()
        return {
            "ok": True,
            "status": status,
            "result": result,
        }
    except Exception:
        supervisor.beat()
        raise
