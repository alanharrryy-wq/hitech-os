import time
from pathlib import Path

class Heartbeat:
    def __init__(self, runtime_root, name="sentinel.heartbeat"):
        self.runtime_root = Path(runtime_root)
        self.heartbeat_file = self.runtime_root / "state" / name

    def touch(self):
        self.heartbeat_file.parent.mkdir(parents=True, exist_ok=True)
        self.heartbeat_file.write_text(str(time.time()), encoding="utf-8")

    def age_seconds(self):
        if not self.heartbeat_file.exists():
            return None
        try:
            last = float(self.heartbeat_file.read_text(encoding="utf-8").strip())
            return time.time() - last
        except Exception:
            return None
