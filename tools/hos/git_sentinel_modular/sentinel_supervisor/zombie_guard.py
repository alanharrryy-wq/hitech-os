from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

def detect_zombie_state(heartbeat_path: str | Path, max_staleness_seconds: int = 600) -> bool:
    path = Path(heartbeat_path)
    if not path.exists():
        return False
    payload = json.loads(path.read_text(encoding="utf-8"))
    updated_at = payload.get("updated_at")
    if not updated_at:
        return True
    stamp = datetime.fromisoformat(updated_at)
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    age = (datetime.now(timezone.utc) - stamp).total_seconds()
    return age > max_staleness_seconds
