from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

from .common import REPO_ROOT, RUNS_DIR, iso_utc
from .config import load_factory_config, resolve_config_path
from .schemas import contracts_check


def _check_command(name: str) -> dict[str, Any]:
    found = shutil.which(name)
    return {
        "check": f"command:{name}",
        "status": "PASS" if found else "BLOCKED",
        "detail": found or "missing",
        "next_action": "" if found else f"Install `{name}` and add it to PATH.",
    }


def _check_path(path: Path, *, required: bool = True) -> dict[str, Any]:
    exists = path.exists()
    status = "PASS" if exists else ("BLOCKED" if required else "WARN")
    return {
        "check": f"path:{path.as_posix()}",
        "status": status,
        "detail": "present" if exists else "missing",
        "next_action": "" if exists else f"Create or restore `{path.as_posix()}`.",
    }


def run_doctor(config_path: str | None = None) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    checks.append(
        {
            "check": "python_version",
            "status": "PASS" if sys.version_info >= (3, 10) else "BLOCKED",
            "detail": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "next_action": "" if sys.version_info >= (3, 10) else "Use Python 3.10 or newer.",
        }
    )
    checks.append(_check_command("git"))
    checks.append(_check_command("python"))
    checks.append(_check_path(REPO_ROOT / ".git", required=True))
    checks.append(_check_path(REPO_ROOT / "tools" / "codex" / "run.py", required=True))
    checks.append(_check_path(REPO_ROOT / "tools" / "codex" / "validation.json", required=True))
    checks.append(_check_path(RUNS_DIR, required=False))

    config_errors: list[str] = []
    try:
        loaded = load_factory_config(config_path=config_path, strict=True)
        checks.append(
            {
                "check": "factory_config",
                "status": "PASS",
                "detail": loaded["_meta"]["config_path"],
                "next_action": "",
            }
        )
    except Exception as exc:
        config_errors.append(str(exc))
        checks.append(
            {
                "check": "factory_config",
                "status": "BLOCKED",
                "detail": str(exc),
                "next_action": f"Fix config at `{resolve_config_path(config_path).as_posix()}`.",
            }
        )

    contracts = contracts_check()
    checks.append(
        {
            "check": "contracts_check",
            "status": "PASS" if contracts.get("status") == "PASS" else "BLOCKED",
            "detail": f"failed={contracts.get('failed', 0)} total={contracts.get('total', 0)}",
            "next_action": "" if contracts.get("status") == "PASS" else "Fix schema contract validation failures.",
        }
    )

    blocked = [item for item in checks if item["status"] == "BLOCKED"]
    warnings = [item for item in checks if item["status"] == "WARN"]
    status = "PASS" if not blocked else "BLOCKED"
    return {
        "schema_version": 1,
        "ts_utc": iso_utc(),
        "status": status,
        "blocked": len(blocked),
        "warnings": len(warnings),
        "checks": checks,
        "errors": config_errors,
    }

