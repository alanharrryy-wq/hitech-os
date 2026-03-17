from pathlib import Path

def detect_zombie_state(runtime_root, heartbeat_name="sentinel.heartbeat", zombie_after_seconds=900):
    runtime_root = Path(runtime_root)
    heartbeat = runtime_root / "state" / heartbeat_name

    if not heartbeat.exists():
        return {
            "zombie": False,
            "reason": "heartbeat_missing"
        }

    try:
        import time
        last = float(heartbeat.read_text(encoding="utf-8").strip())
        age = time.time() - last
    except Exception:
        return {
            "zombie": True,
            "reason": "heartbeat_corrupt"
        }

    if age > zombie_after_seconds:
        return {
            "zombie": True,
            "reason": f"heartbeat_stale:{age:.1f}s"
        }

    return {
        "zombie": False,
        "reason": f"heartbeat_healthy:{age:.1f}s"
    }
