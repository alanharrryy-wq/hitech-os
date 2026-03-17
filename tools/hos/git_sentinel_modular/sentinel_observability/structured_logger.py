import json
import time
from pathlib import Path

LOG_FILE = "sentinel_events.log"

def log_event(runtime_root, level, message, **fields):
    event = {
        "ts": time.time(),
        "level": level,
        "message": message,
        **fields
    }
    log_path = Path(runtime_root) / LOG_FILE
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
