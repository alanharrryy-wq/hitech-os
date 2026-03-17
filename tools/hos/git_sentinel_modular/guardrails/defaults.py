from pathlib import Path
import os

DEFAULT_MAX_RUNTIME_SECONDS = 900
DEFAULT_LOCK_TIMEOUT = 60
DEFAULT_SCHEDULER_MIN_INTERVAL = 120

def runtime_root() -> Path:
    return Path(
        os.getenv(
            "HITECH_SENTINEL_RUNTIME",
            r"C:\Users\alanh\AppData\Local\HITECH-OS\git_sentinel\runtime",
        )
    )

def downloads_root() -> Path:
    return Path(
        os.getenv(
            "HITECH_SENTINEL_DOWNLOADS",
            r"F:\OneDrive\Descargas",
        )
    )

def ensure_runtime_dirs():
    root = runtime_root()
    (root / "locks").mkdir(parents=True, exist_ok=True)
    (root / "state").mkdir(parents=True, exist_ok=True)
