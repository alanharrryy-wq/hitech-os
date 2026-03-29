from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from .paths import GuardianPaths
from .state_store import StateStore, utc_now_iso


def _first_existing_path(paths: Iterable[Path]) -> Optional[Path]:
    for path in paths:
        if path.exists():
            return path
    return None


def _resolve_executable(name: str, extra_candidates: Iterable[Path] | None = None) -> Dict[str, Any]:
    which = shutil.which(name)
    candidates = list(extra_candidates or [])
    existing = _first_existing_path(candidates)
    chosen = which or (str(existing) if existing else None)
    return {
        "name": name,
        "path": chosen,
        "exists": bool(chosen),
        "source": "PATH" if which else ("candidate" if existing else "missing"),
    }


def run_preflight(paths: GuardianPaths, state_store: StateStore) -> Dict[str, Any]:
    paths.ensure_runtime_layout()
    state_store.seed_runtime_files()

    repo_root_ok = paths.repo_root.exists()
    package_root_ok = paths.package_root.exists()
    igniters_dir_ok = paths.igniters_dir.exists()
    docs_dir_ok = paths.docs_dir.exists()
    cloudflare_tools_ok = paths.cloudflare_tools_dir.exists()
    repo_analyzer_dir_ok = paths.repo_analyzer_dir.exists()
    ensure_origin_exists = paths.ensure_origin_script.exists()
    ensure_service_exists = paths.ensure_service_script.exists()
    validate_tunnel_exists = paths.validate_tunnel_script.exists()
    repo_analyzer_main_exists = paths.repo_analyzer_main.exists()
    repo_analyzer_self_test_exists = paths.repo_analyzer_self_test.exists()
    cloudflared_config_exists = paths.cloudflared_config_path.exists()
    cloudflared_credentials_exists = paths.cloudflared_credentials_path.exists()

    python_extra = [
        paths.repo_root / ".venv" / "Scripts" / "python.exe",
        Path(sys.executable),
        Path(r"C:\Python312\python.exe"),
        Path(r"C:\Python311\python.exe"),
        Path(r"C:\Python310\python.exe"),
    ]
    pwsh_extra = [
        Path(r"C:\Program Files\PowerShell\7\pwsh.exe"),
        Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"),
    ]
    pnpm_extra = [
        Path(os.getenv("APPDATA", r"C:\Users\alanh\AppData\Roaming")) / "npm" / "pnpm.cmd",
    ]
    cloudflared_extra = [
        Path(r"C:\Program Files\Cloudflare\Cloudflared\cloudflared.exe"),
        Path(r"C:\Program Files (x86)\cloudflared\cloudflared.EXE"),
        Path(r"C:\Users\alanh\.cloudflared\cloudflared.exe"),
    ]

    tools = {
        "python": _resolve_executable("python", python_extra),
        "pwsh": _resolve_executable("pwsh", pwsh_extra),
        "powershell": _resolve_executable("powershell", pwsh_extra),
        "pnpm": _resolve_executable("pnpm", pnpm_extra),
        "cloudflared": _resolve_executable("cloudflared", cloudflared_extra),
    }

    runtime_writable = True
    runtime_error = None
    try:
        probe_path = paths.state_dir / ".write_probe.tmp"
        probe_path.write_text("ok", encoding="utf-8")
        probe_path.unlink(missing_ok=True)
    except Exception as exc:
        runtime_writable = False
        runtime_error = str(exc)

    checks = {
        "repo_root_exists": repo_root_ok,
        "package_root_exists": package_root_ok,
        "igniters_dir_exists": igniters_dir_ok,
        "docs_dir_exists": docs_dir_ok,
        "cloudflare_tools_dir_exists": cloudflare_tools_ok,
        "repo_analyzer_dir_exists": repo_analyzer_dir_ok,
        "ensure_origin_exists": ensure_origin_exists,
        "ensure_service_exists": ensure_service_exists,
        "validate_tunnel_exists": validate_tunnel_exists,
        "repo_analyzer_main_exists": repo_analyzer_main_exists,
        "repo_analyzer_self_test_exists": repo_analyzer_self_test_exists,
        "cloudflared_config_exists": cloudflared_config_exists,
        "cloudflared_credentials_exists": cloudflared_credentials_exists,
        "runtime_root_writable": runtime_writable,
    }

    ok = all(
        [
            repo_root_ok,
            package_root_ok,
            igniters_dir_ok,
            docs_dir_ok,
            cloudflare_tools_ok,
            repo_analyzer_dir_ok,
            runtime_writable,
            tools["python"]["exists"],
            tools["pwsh"]["exists"] or tools["powershell"]["exists"],
        ]
    )

    result = {
        "timestamp_utc": utc_now_iso(),
        "ok": ok,
        "checks": checks,
        "runtime_write_error": runtime_error,
        "paths": paths.as_dict(),
        "resolved_tools": tools,
    }
    state_store.write_json(state_store.resolved_tools_path, result["resolved_tools"])
    state_store.write_json(paths.reports_dir / "preflight_latest.json", result)
    return result
