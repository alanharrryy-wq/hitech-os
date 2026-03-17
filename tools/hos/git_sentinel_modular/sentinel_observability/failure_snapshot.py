import traceback
from pathlib import Path
import time

def capture_failure(runtime_root, exc):
    snapshot_dir = Path(runtime_root) / "failures"
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    name = f"failure_{int(time.time())}.txt"
    path = snapshot_dir / name

    with open(path, "w", encoding="utf-8") as f:
        f.write("SENTINEL FAILURE SNAPSHOT\n")
        f.write(traceback.format_exc())
