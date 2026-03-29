from __future__ import annotations

from ..shared.runtime_paths import RuntimePaths, build_runtime_paths
from ..shared.status_payloads import RuntimeStatus

def get_runtime_paths() -> RuntimePaths:
    return build_runtime_paths().ensure()

def build_runtime_status(paths: RuntimePaths | None = None) -> RuntimeStatus:
    runtime_paths = (paths or get_runtime_paths()).ensure()
    status = "ready" if runtime_paths.runtime_root.exists() else "missing"
    return RuntimeStatus(
        repo_root=str(runtime_paths.repo_root),
        runtime_root=str(runtime_paths.runtime_root),
        shadow_root=str(runtime_paths.shadow_root),
        logs_root=str(runtime_paths.logs_root),
        state_root=str(runtime_paths.state_root),
        status=status,
    )
