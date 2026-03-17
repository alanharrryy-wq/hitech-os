from pathlib import Path

REQUIRED_RUNTIME_DIRS = [
    "locks",
    "state",
    "failures",
    "logs",
]

def ensure_runtime_health(runtime_root):
    runtime_root = Path(runtime_root)
    runtime_root.mkdir(parents=True, exist_ok=True)

    created = []
    for rel in REQUIRED_RUNTIME_DIRS:
        path = runtime_root / rel
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(str(path))

    probe = runtime_root / "state" / "runtime_probe.tmp"
    probe.write_text("ok", encoding="utf-8")
    probe.unlink(missing_ok=True)

    return {
        "runtime_root": str(runtime_root),
        "created": created,
    }
