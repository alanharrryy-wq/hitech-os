from __future__ import annotations

"""Resolución de target y clasificación ligera de app."""

import os
import platform
import shutil
import socket
import sys
from pathlib import Path
from typing import Any


APP_KIND_PRIORITY = [
    ("mixed", {"pyproject.toml", "requirements.txt", "package.json"}),
    ("python", {"pyproject.toml", "requirements.txt", "setup.py"}),
    ("node", {"package.json", "pnpm-lock.yaml", "package-lock.json", "yarn.lock"}),
    ("web", {"index.html", "vite.config.ts", "vite.config.js", "next.config.js", "webpack.config.js"}),
    ("desktop", {"electron-builder.yml", "tauri.conf.json", "main.py", "main.ts"}),
]


def resolve_target_path(base_dir: Path, raw_target: str | None) -> Path:
    if raw_target:
        candidate = Path(raw_target).expanduser()
        if not candidate.is_absolute():
            candidate = (base_dir / candidate).resolve()
        else:
            candidate = candidate.resolve()
        return candidate
    return base_dir.resolve()


def _iter_markers(target_path: Path) -> set[str]:
    markers: set[str] = set()
    if not target_path.exists():
        return markers
    if target_path.is_file():
        markers.add(target_path.name)
        return markers
    for child in list(target_path.iterdir())[:256]:
        markers.add(child.name)
    return markers


def detect_app_kind(target_path: Path, explicit_kind: str | None = None) -> str:
    kind = str(explicit_kind or "auto").strip().lower()
    if kind and kind != "auto":
        return kind
    markers = _iter_markers(target_path)
    hits: list[str] = []
    for candidate_kind, expected_markers in APP_KIND_PRIORITY:
        overlap = markers.intersection(expected_markers)
        if overlap:
            hits.append(candidate_kind)
    if "python" in hits and "node" in hits:
        return "mixed"
    if "mixed" in hits:
        return "mixed"
    if hits:
        return hits[0]
    if target_path.is_file():
        suffix = target_path.suffix.lower()
        if suffix in {".py", ".pyw"}:
            return "python"
        if suffix in {".js", ".jsx", ".ts", ".tsx"}:
            return "node"
    return "unknown"


def detect_workspace_markers(target_path: Path) -> dict[str, bool]:
    names = _iter_markers(target_path)
    return {
        "has_git": ".git" in names,
        "has_package_json": "package.json" in names,
        "has_pyproject": "pyproject.toml" in names,
        "has_requirements": "requirements.txt" in names,
        "has_docker_compose": "docker-compose.yml" in names or "compose.yml" in names,
        "has_logs_dir": "logs" in names,
        "has_reports_dir": "reports" in names,
    }


def build_environment_summary(base_dir: Path, target_path: Path, app_kind: str) -> dict[str, Any]:
    python_exe = Path(sys.executable).resolve()
    return {
        "cwd": str(Path.cwd().resolve()),
        "base_dir": str(base_dir.resolve()),
        "target_path": str(target_path.resolve()),
        "target_exists": target_path.exists(),
        "target_is_dir": target_path.is_dir(),
        "app_kind": app_kind,
        "hostname": socket.gethostname(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
        },
        "executables": {
            "python": str(python_exe),
            "git": shutil.which("git"),
            "node": shutil.which("node"),
            "npm": shutil.which("npm"),
            "pnpm": shutil.which("pnpm"),
            "yarn": shutil.which("yarn"),
        },
        "workspace_markers": detect_workspace_markers(target_path),
        "env_flags": {
            "VIRTUAL_ENV": os.environ.get("VIRTUAL_ENV"),
            "PYTHONPATH": os.environ.get("PYTHONPATH"),
            "NODE_ENV": os.environ.get("NODE_ENV"),
        },
    }
