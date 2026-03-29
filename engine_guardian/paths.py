from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


DEFAULT_REPO_ROOT = Path(r"F:\repos\hitech-os")
DEFAULT_DOWNLOADS_ROOT = Path(r"F:\OneDrive\Descargas")
DEFAULT_RUNTIME_ROOT = DEFAULT_DOWNLOADS_ROOT / "engine_guardian"
DEFAULT_PUBLIC_URL = "https://engine.hitechrts.com"
DEFAULT_ORIGIN_URL = "http://127.0.0.1:3100"
DEFAULT_CLOUDFLARED_CONFIG = Path(r"C:\Users\alanh\.cloudflared\config.yml")
DEFAULT_CLOUDFLARED_CREDENTIALS = Path(r"C:\Users\alanh\.cloudflared\64106de5-03a9-4d88-a447-7e90827eafb2.json")


@dataclass(frozen=True)
class GuardianPaths:
    repo_root: Path
    package_root: Path
    runtime_root: Path
    downloads_root: Path
    state_dir: Path
    locks_dir: Path
    logs_dir: Path
    reports_dir: Path
    snapshots_dir: Path
    backups_dir: Path
    install_dir: Path
    igniters_dir: Path
    docs_dir: Path
    cloudflare_docs_dir: Path
    cloudflare_tools_dir: Path
    repo_analyzer_dir: Path
    public_url: str
    origin_url: str
    cloudflared_config_path: Path
    cloudflared_credentials_path: Path

    @property
    def python_cli_path(self) -> Path:
        return self.package_root / "cli.py"

    @property
    def ensure_origin_script(self) -> Path:
        return self.cloudflare_tools_dir / "ensure_origin.py"

    @property
    def ensure_service_script(self) -> Path:
        return self.cloudflare_tools_dir / "ensure_service.py"

    @property
    def validate_tunnel_script(self) -> Path:
        return self.cloudflare_tools_dir / "validate_tunnel.py"

    @property
    def repo_analyzer_main(self) -> Path:
        return self.repo_analyzer_dir / "main.py"

    @property
    def repo_analyzer_self_test(self) -> Path:
        return self.repo_analyzer_dir / "dev_self_test.py"

    def runtime_dirs(self) -> List[Path]:
        return [
            self.runtime_root,
            self.state_dir,
            self.locks_dir,
            self.logs_dir,
            self.reports_dir,
            self.snapshots_dir,
            self.backups_dir,
            self.install_dir,
        ]

    def ensure_runtime_layout(self) -> None:
        for directory in self.runtime_dirs():
            directory.mkdir(parents=True, exist_ok=True)

    def as_dict(self) -> Dict[str, str]:
        return {
            "repo_root": str(self.repo_root),
            "package_root": str(self.package_root),
            "runtime_root": str(self.runtime_root),
            "downloads_root": str(self.downloads_root),
            "state_dir": str(self.state_dir),
            "locks_dir": str(self.locks_dir),
            "logs_dir": str(self.logs_dir),
            "reports_dir": str(self.reports_dir),
            "snapshots_dir": str(self.snapshots_dir),
            "backups_dir": str(self.backups_dir),
            "install_dir": str(self.install_dir),
            "igniters_dir": str(self.igniters_dir),
            "docs_dir": str(self.docs_dir),
            "cloudflare_docs_dir": str(self.cloudflare_docs_dir),
            "cloudflare_tools_dir": str(self.cloudflare_tools_dir),
            "repo_analyzer_dir": str(self.repo_analyzer_dir),
            "public_url": self.public_url,
            "origin_url": self.origin_url,
            "cloudflared_config_path": str(self.cloudflared_config_path),
            "cloudflared_credentials_path": str(self.cloudflared_credentials_path),
            "ensure_origin_script": str(self.ensure_origin_script),
            "ensure_service_script": str(self.ensure_service_script),
            "validate_tunnel_script": str(self.validate_tunnel_script),
            "repo_analyzer_main": str(self.repo_analyzer_main),
            "repo_analyzer_self_test": str(self.repo_analyzer_self_test),
            "python_cli_path": str(self.python_cli_path),
        }


def _repo_root_from_file() -> Path:
    here = Path(__file__).resolve()
    repo_candidate = here.parent.parent
    if (repo_candidate / "engine_guardian").exists():
        return repo_candidate
    return DEFAULT_REPO_ROOT


def resolve_repo_root() -> Path:
    env_override = os.getenv("ENGINE_GUARDIAN_REPO_ROOT")
    if env_override:
        return Path(env_override).expanduser().resolve()
    return _repo_root_from_file()


def resolve_downloads_root() -> Path:
    env_override = os.getenv("ENGINE_GUARDIAN_DOWNLOADS_ROOT")
    if env_override:
        return Path(env_override).expanduser().resolve()
    return DEFAULT_DOWNLOADS_ROOT


def resolve_runtime_root(downloads_root: Path | None = None) -> Path:
    env_override = os.getenv("ENGINE_GUARDIAN_RUNTIME_ROOT")
    if env_override:
        return Path(env_override).expanduser().resolve()
    return (downloads_root or resolve_downloads_root()) / "engine_guardian"


def build_paths() -> GuardianPaths:
    repo_root = resolve_repo_root()
    downloads_root = resolve_downloads_root()
    runtime_root = resolve_runtime_root(downloads_root)
    package_root = repo_root / "engine_guardian"
    return GuardianPaths(
        repo_root=repo_root,
        package_root=package_root,
        runtime_root=runtime_root,
        downloads_root=downloads_root,
        state_dir=runtime_root / "state",
        locks_dir=runtime_root / "locks",
        logs_dir=runtime_root / "logs",
        reports_dir=runtime_root / "reports",
        snapshots_dir=runtime_root / "snapshots",
        backups_dir=runtime_root / "backups",
        install_dir=runtime_root / "install",
        igniters_dir=repo_root / "igniters",
        docs_dir=repo_root / "docs" / "infra" / "engine_guardian",
        cloudflare_docs_dir=repo_root / "docs" / "infra" / "cloudflare",
        cloudflare_tools_dir=repo_root / "tools" / "infra" / "cloudflare",
        repo_analyzer_dir=repo_root / "tools" / "graphviz" / "repo_analizer",
        public_url=os.getenv("ENGINE_GUARDIAN_PUBLIC_URL", DEFAULT_PUBLIC_URL),
        origin_url=os.getenv("ENGINE_GUARDIAN_ORIGIN_URL", DEFAULT_ORIGIN_URL),
        cloudflared_config_path=Path(
            os.getenv("ENGINE_GUARDIAN_CLOUDFLARED_CONFIG", str(DEFAULT_CLOUDFLARED_CONFIG))
        ),
        cloudflared_credentials_path=Path(
            os.getenv("ENGINE_GUARDIAN_CLOUDFLARED_CREDENTIALS", str(DEFAULT_CLOUDFLARED_CREDENTIALS))
        ),
    )
