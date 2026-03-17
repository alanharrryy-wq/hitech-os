from pathlib import Path
from .defaults import runtime_root, ensure_runtime_dirs

def verify_runtime_environment():
    root = runtime_root()

    if not root.exists():
        raise RuntimeError(f"Sentinel runtime root missing: {root}")

    ensure_runtime_dirs()

    writable_test = root / "write_test.tmp"
    try:
        writable_test.write_text("ok")
        writable_test.unlink()
    except Exception as e:
        raise RuntimeError(
            f"Runtime root not writable: {root}"
        ) from e
