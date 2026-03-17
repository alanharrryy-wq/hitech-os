import time
from pathlib import Path
from .defaults import runtime_root, DEFAULT_SCHEDULER_MIN_INTERVAL

class SchedulerGuard:

    def __init__(self):
        self.state_file = runtime_root() / "state" / "last_run"

    def check_interval(self, min_interval=DEFAULT_SCHEDULER_MIN_INTERVAL):

        if not self.state_file.exists():
            return True

        last = float(self.state_file.read_text())
        delta = time.time() - last

        if delta < min_interval:
            raise RuntimeError(
                f"Scheduler guard: scan attempted too early ({delta:.1f}s)"
            )

        return True

    def record_run(self):
        self.state_file.write_text(str(time.time()))
