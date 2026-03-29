from __future__ import annotations

import time
from pathlib import Path

def cleanup_stale_locks(lock_dir: str | Path, max_age_seconds: int = 3600) -> int:
    directory = Path(lock_dir)
    if not directory.exists():
        return 0
    cleaned = 0
    now = time.time()
    for item in directory.glob("*.lock*"):
        age = now - item.stat().st_mtime
        if age >= max_age_seconds:
            item.unlink(missing_ok=True)
            cleaned += 1
    return cleaned
