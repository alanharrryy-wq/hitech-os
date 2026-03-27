from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ENV = "GSM_REPO_ROOT"
DOWNLOADS_ENV = "GSM_DOWNLOADS_ROOT"
RUNTIME_ENV = "GSM_RUNTIME_ROOT"
DEFAULT_WINDOWS_DOWNLOADS = Path(r"F:\OneDrive\Descargas")
DEFAULT_WINDOWS_RUNTIME = Path(r"C:\Users\alanh\AppData\Local\HITECH-OS\git_sentinel\runtime")

@dataclass(frozen=True)
class RuntimePaths:
    repo_root: Path
    package_root: Path
    package_parent: Path
    downloads_root: Path
    runtime_root: Path
    shadow_root: Path
    logs_root: Path
    state_root: Path
    reports_root: Path
    plugin_state_root: Path

    def ensure(self) -> "RuntimePaths":
        for path in (
            self.downloads_root,
            self.runtime_root,
            self.shadow_root,
            self.logs_root,
            self.state_root,
            self.reports_root,
            self.plugin_state_root,
        ):
            path.mkdir(parents=True, exist_ok=True)
        return self

    def workspace_root(self, run_id: str) -> Path:
        return self.shadow_root / run_id

    def to_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in asdict(self).items()}

def _package_root_from_file() -> Path:
    return Path(__file__).resolve().parents[1]

def _repo_root_from_package(package_root: Path) -> Path:
    return package_root.parents[2]

def _default_downloads_root() -> Path:
    if os.name == "nt":
        return DEFAULT_WINDOWS_DOWNLOADS
    return Path.home() / "Downloads"

def _default_runtime_root(repo_root: Path) -> Path:
    if os.name == "nt":
        return DEFAULT_WINDOWS_RUNTIME
    return repo_root / ".runtime" / "git_sentinel_modular"

def build_runtime_paths(
    repo_root: str | Path | None = None,
    downloads_root: str | Path | None = None,
    runtime_root: str | Path | None = None,
) -> RuntimePaths:
    package_root = _package_root_from_file()
    resolved_repo = Path(repo_root or os.environ.get(REPO_ENV) or _repo_root_from_package(package_root)).resolve()
    resolved_downloads = Path(downloads_root or os.environ.get(DOWNLOADS_ENV) or _default_downloads_root()).resolve()
    resolved_runtime = Path(runtime_root or os.environ.get(RUNTIME_ENV) or _default_runtime_root(resolved_repo)).resolve()

    return RuntimePaths(
        repo_root=resolved_repo,
        package_root=package_root,
        package_parent=package_root.parent,
        downloads_root=resolved_downloads,
        runtime_root=resolved_runtime,
        shadow_root=resolved_runtime / "shadow_mode",
        logs_root=resolved_runtime / "logs",
        state_root=resolved_runtime / "state",
        reports_root=resolved_runtime / "reports",
        plugin_state_root=resolved_runtime / "plugins",
    )
