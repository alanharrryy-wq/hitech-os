import time
from pathlib import Path

def cleanup_stale_locks(runtime_root, max_lock_age_seconds=1800):
    runtime_root = Path(runtime_root)
    locks_dir = runtime_root / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)

    cleaned = []

    for lock_file in locks_dir.glob("*.lock"):
        try:
            raw = lock_file.read_text(encoding="utf-8").strip()
            created_at = float(raw)
        except Exception:
            created_at = lock_file.stat().st_mtime

        age = time.time() - created_at

        if age > max_lock_age_seconds:
            lock_file.unlink(missing_ok=True)
            cleaned.append(str(lock_file))

    return cleaned
