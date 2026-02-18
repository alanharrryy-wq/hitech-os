from __future__ import annotations

import platform
import shutil
import sys
from pathlib import Path
from typing import Any

from .common import CODEX_DIR, CONTRACTS_DIR, REPO_ROOT, RUNS_DIR, ensure_dir, iso_utc, write_json


def _check_exists(path: Path, *, required: bool = True) -> dict[str, Any]:
    ok = path.exists()
    return {
        "check": "path_exists",
        "path": path.as_posix(),
        "required": required,
        "status": "PASS" if ok else ("BLOCKED" if required else "WARN"),
        "detail": "present" if ok else "missing",
    }


def _check_command(name: str, *, required: bool = True) -> dict[str, Any]:
    executable = shutil.which(name)
    ok = executable is not None
    return {
        "check": "command_available",
        "command": name,
        "required": required,
        "status": "PASS" if ok else ("BLOCKED" if required else "WARN"),
        "detail": executable or "not found",
    }


def _check_python_version(min_major: int, min_minor: int) -> dict[str, Any]:
    current = sys.version_info
    ok = (current.major, current.minor) >= (min_major, min_minor)
    return {
        "check": "python_version",
        "required": True,
        "status": "PASS" if ok else "BLOCKED",
        "detail": f"{current.major}.{current.minor}.{current.micro}",
        "minimum": f"{min_major}.{min_minor}",
    }


def run_preflight(run_id: str | None = None) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    checks.append(_check_python_version(3, 10))
    checks.append(_check_command("git", required=True))
    checks.append(_check_command("python", required=True))
    checks.append(_check_command("node", required=False))
    checks.append(_check_command("pnpm", required=False))
    checks.append(_check_command("code", required=False))

    required_paths = [
        REPO_ROOT / ".git",
        REPO_ROOT / "tools" / "codex" / "run.py",
        REPO_ROOT / "tools" / "codex" / "validation.json",
        REPO_ROOT / "docs",
        CONTRACTS_DIR,
        CODEX_DIR / "schemas",
    ]
    for item in required_paths:
        checks.append(_check_exists(item, required=True))

    optional_paths = [
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / "docs" / "factory" / "AGENTS_FALLBACK.md",
    ]
    for item in optional_paths:
        checks.append(_check_exists(item, required=False))

    blocked = [entry for entry in checks if entry["status"] == "BLOCKED"]
    warnings = [entry for entry in checks if entry["status"] == "WARN"]

    payload: dict[str, Any] = {
        "schema_version": 1,
        "run_id": run_id or "",
        "status": "PASS" if not blocked else "BLOCKED",
        "started_at": iso_utc(),
        "ended_at": iso_utc(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "checks": checks,
        "blocked": len(blocked),
        "warnings": len(warnings),
    }

    if run_id:
        out_dir = RUNS_DIR / run_id / "logs"
        ensure_dir(out_dir)
        write_json(out_dir / "preflight_STATUS.json", payload)

    return payload
