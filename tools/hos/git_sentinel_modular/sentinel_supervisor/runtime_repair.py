from __future__ import annotations

from pathlib import Path

from ..shared.runtime_paths import RuntimePaths, build_runtime_paths

def ensure_runtime_health(paths: RuntimePaths | None = None) -> dict[str, str]:
    runtime_paths = (paths or build_runtime_paths()).ensure()
    return {
        "runtime_root": str(runtime_paths.runtime_root),
        "state_root": str(runtime_paths.state_root),
        "logs_root": str(runtime_paths.logs_root),
    }
