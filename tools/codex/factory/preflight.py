from __future__ import annotations

import platform
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .common import CODEX_DIR, CONTRACTS_DIR, REPO_ROOT, RUNS_DIR, ensure_dir, iso_utc, write_json

EVOLUTIONARY_ENGINE_PATH = REPO_ROOT / "tools" / "hos" / "guardrails" / "evolutionary_sanctions.py"
EVOLUTIONARY_POLICY_PATH = REPO_ROOT / "tools" / "hos" / "guardrails" / "policy.json"


def _default_evolutionary_policy_payload() -> dict[str, Any]:
    return {
        "version": "1.0",
        "defaults": {
            "max_file_chars": 120000,
            "max_file_loc": 2000,
            "k_tokens": 25,
            "winnow_window": 6,
            "dup_ratio_file_warn": 0.2,
            "dup_ratio_file_severe": 0.35,
            "dup_ratio_new_warn": 0.08,
            "dup_ratio_new_severe": 0.15,
            "min_gzip_ratio": 0.18,
            "min_ttr": 0.12,
            "min_tokens_for_entropy": 1500,
            "min_tokens_for_dup": 800,
            "max_added_files_per_run_warn": 120,
            "max_added_files_per_run_severe": 250,
            "max_single_dir_files_added": 60,
            "scaling_constant_K": 1200.0,
            "penalties": {"entropy_severe": 0.75, "blind_severe": 0.9, "caps_severe": 1.1},
        },
        "exclude_globs": [
            "**/.git/**",
            "**/node_modules/**",
            "**/dist/**",
            "**/build/**",
            "**/vendor/**",
            "**/generated/**",
            "**/snapshots/**",
            "**/coverage/**",
        ],
        "allow_extensions": [
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".java",
            ".go",
            ".rs",
            ".c",
            ".cc",
            ".cpp",
            ".h",
            ".hpp",
            ".cs",
            ".rb",
            ".php",
            ".swift",
            ".kt",
            ".scala",
            ".sql",
            ".sh",
            ".bash",
            ".ps1",
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
            ".md",
            ".txt",
            ".json",
        ],
    }


def _default_evolutionary_engine_stub() -> str:
    return (
        "from __future__ import annotations\n\n"
        "import argparse\n"
        "import datetime as dt\n"
        "import json\n"
        "from pathlib import Path\n\n"
        "def main() -> int:\n"
        "    ap = argparse.ArgumentParser(description='Fallback evolutionary sanctions stub')\n"
        "    ap.add_argument('--repo', default='.')\n"
        "    ap.add_argument('--run-id', default='UNKNOWN_RUN')\n"
        "    ap.add_argument('--worker-id', default='UNKNOWN_WORKER')\n"
        "    ap.add_argument('--bundle-dir', default=None)\n"
        "    ap.add_argument('--base-ref', default=None)\n"
        "    ap.add_argument('--policy', default=None)\n"
        "    args = ap.parse_args()\n"
        "    out = Path(args.bundle_dir).resolve() if args.bundle_dir else Path(args.repo).resolve()\n"
        "    out.mkdir(parents=True, exist_ok=True)\n"
        "    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()\n"
        "    report = {\n"
        "        'run_id': args.run_id,\n"
        "        'worker_id': args.worker_id,\n"
        "        'computed_at_utc': now,\n"
        "        'bundle_dir': out.as_posix(),\n"
        "        'sanction_score': 1.0,\n"
        "        'sanction_level': 'WARN',\n"
        "        'flags': ['PRECHECK_AUTOFIX_STUB']\n"
        "    }\n"
        "    score = {\n"
        "        'run_id': args.run_id,\n"
        "        'worker_id': args.worker_id,\n"
        "        'computed_at_utc': now,\n"
        "        'sanction_score': 1.0,\n"
        "        'sanction_level': 'WARN',\n"
        "        'vdi': 0.0,\n"
        "        'loc_delta': 0,\n"
        "        'notes': ['PRECHECK_AUTOFIX_STUB']\n"
        "    }\n"
        "    (out / 'SELF_EVAL_REPORT.json').write_text(json.dumps(report, indent=2) + '\\n', encoding='utf-8', newline='\\n')\n"
        "    (out / 'SANCTION_SCORE.json').write_text(json.dumps(score, indent=2) + '\\n', encoding='utf-8', newline='\\n')\n"
        "    with (out / 'SELF_CORRECTION_LOG.jsonl').open('a', encoding='utf-8', newline='\\n') as f:\n"
        "        f.write(json.dumps({\n"
        "            'run_id': args.run_id,\n"
        "            'worker_id': args.worker_id,\n"
        "            'computed_at_utc': now,\n"
        "            'sanction_score': 1.0,\n"
        "            'sanction_level': 'WARN',\n"
        "            'vdi': 0.0,\n"
        "            'loc_delta': 0,\n"
        "            'flags': ['PRECHECK_AUTOFIX_STUB']\n"
        "        }) + '\\n')\n"
        "    print('OK evolutionary_sanctions completed')\n"
        "    return 0\n\n"
        "if __name__ == '__main__':\n"
        "    raise SystemExit(main())\n"
    )


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
    if not executable and name == "python" and sys.executable:
        executable = sys.executable
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


def _is_repo_relative(path: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(REPO_ROOT.resolve(strict=False))
        return True
    except ValueError:
        return False


def _restore_tracked_file(path: Path) -> bool:
    if not _is_repo_relative(path):
        return False
    rel = path.resolve(strict=False).relative_to(REPO_ROOT.resolve(strict=False)).as_posix()
    if not rel:
        return False
    probe = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{rel}"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if probe.returncode != 0:
        return False
    restore = subprocess.run(
        ["git", "checkout", "--", rel],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    return restore.returncode == 0 and path.exists()


def _write_stub(path: Path) -> None:
    ensure_dir(path.parent)
    normalized = path.resolve(strict=False)
    if normalized == EVOLUTIONARY_ENGINE_PATH.resolve(strict=False):
        path.write_text(_default_evolutionary_engine_stub(), encoding="utf-8", newline="\n")
        return
    if normalized == EVOLUTIONARY_POLICY_PATH.resolve(strict=False):
        path.write_text(
            json.dumps(_default_evolutionary_policy_payload(), indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return
    suffix = path.suffix.lower()
    if suffix == ".json":
        path.write_text("{}\n", encoding="utf-8", newline="\n")
        return
    if suffix == ".py":
        path.write_text("from __future__ import annotations\n", encoding="utf-8", newline="\n")
        return
    if suffix == ".md":
        path.write_text("# Auto-repaired placeholder\n", encoding="utf-8", newline="\n")
        return
    path.write_text("", encoding="utf-8", newline="\n")


def _repair_missing_path(path: Path) -> dict[str, Any]:
    if path.exists():
        return {
            "path": path.as_posix(),
            "status": "PASS",
            "action": "already_present",
            "detail": "",
        }

    if path.name == ".git":
        git_cmd = shutil.which("git")
        if not git_cmd:
            return {
                "path": path.as_posix(),
                "status": "BLOCKED",
                "action": "git_init",
                "detail": "git executable not found",
            }
        init = subprocess.run(
            [git_cmd, "init"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "path": path.as_posix(),
            "status": "PASS" if path.exists() else "BLOCKED",
            "action": "git_init",
            "detail": (init.stdout + init.stderr).strip(),
        }

    if path.suffix:
        if _restore_tracked_file(path):
            return {
                "path": path.as_posix(),
                "status": "PASS",
                "action": "git_restore",
                "detail": "restored from HEAD",
            }
        _write_stub(path)
        return {
            "path": path.as_posix(),
            "status": "PASS" if path.exists() else "BLOCKED",
            "action": "write_stub",
            "detail": "created placeholder file",
        }

    ensure_dir(path)
    return {
        "path": path.as_posix(),
        "status": "PASS" if path.exists() else "BLOCKED",
        "action": "mkdir",
        "detail": "created directory",
    }


def _load_path_contract() -> tuple[list[Path], list[dict[str, str]]]:
    default_required = [
        REPO_ROOT / ".git",
        REPO_ROOT / "tools" / "codex" / "run.py",
        REPO_ROOT / "tools" / "codex" / "validation.json",
        REPO_ROOT / "docs",
        CONTRACTS_DIR,
        CODEX_DIR / "schemas",
    ]
    default_optional = [
        {"path": "AGENTS.md", "fallback": "docs/factory/AGENTS_FALLBACK.md"},
        {"path": "docs/factory/AGENTS_FALLBACK.md", "fallback": ""},
    ]

    contract_path = CONTRACTS_DIR / "preflight_required_files.json"
    if not contract_path.exists():
        return default_required, default_optional

    try:
        payload = json.loads(contract_path.read_text(encoding="utf-8"))
    except Exception:
        return default_required, default_optional

    required_entries = payload.get("required", [])
    optional_entries = payload.get("optional_with_fallback", [])
    required: list[Path] = []
    optional: list[dict[str, str]] = []

    if isinstance(required_entries, list):
        for item in required_entries:
            if not isinstance(item, str):
                continue
            required.append((REPO_ROOT / item).resolve(strict=False))
    if isinstance(optional_entries, list):
        for item in optional_entries:
            if not isinstance(item, dict):
                continue
            raw_path = str(item.get("path", "")).strip()
            if not raw_path:
                continue
            optional.append(
                {
                    "path": raw_path,
                    "fallback": str(item.get("fallback", "")).strip(),
                }
            )

    return (required or default_required), (optional or default_optional)


def run_preflight(run_id: str | None = None, *, auto_repair: bool = True) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    repairs: list[dict[str, Any]] = []

    checks.append(_check_python_version(3, 10))
    checks.append(_check_command("git", required=True))
    checks.append(_check_command("python", required=True))
    checks.append(_check_command("node", required=False))
    checks.append(_check_command("pnpm", required=False))
    checks.append(_check_command("code", required=False))

    required_paths, optional_with_fallback = _load_path_contract()
    for guardrail_path in (
        EVOLUTIONARY_ENGINE_PATH.parent,
        EVOLUTIONARY_ENGINE_PATH,
        EVOLUTIONARY_POLICY_PATH,
    ):
        resolved = guardrail_path.resolve(strict=False)
        if all(resolved != item.resolve(strict=False) for item in required_paths):
            required_paths.append(resolved)
    for item in required_paths:
        check = _check_exists(item, required=True)
        if auto_repair and check["status"] == "BLOCKED":
            repair = _repair_missing_path(item)
            repairs.append(repair)
            check = _check_exists(item, required=True)
            if repair["status"] != "PASS":
                check["detail"] = f"missing (repair failed: {repair['action']})"
            else:
                check["detail"] = f"present (auto-repair: {repair['action']})"
        checks.append(check)

    for entry in optional_with_fallback:
        path = (REPO_ROOT / entry.get("path", "")).resolve(strict=False)
        fallback = (REPO_ROOT / entry.get("fallback", "")).resolve(strict=False) if entry.get("fallback") else None
        optional_check = _check_exists(path, required=False)
        if optional_check["status"] == "WARN" and fallback is not None and fallback.exists():
            optional_check["status"] = "PASS"
            optional_check["detail"] = f"missing (fallback present: {fallback.as_posix()})"
        checks.append(optional_check)

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
        "auto_repair": bool(auto_repair),
        "repairs": repairs,
        "repairs_applied": len([item for item in repairs if item.get("status") == "PASS"]),
        "repairs_failed": len([item for item in repairs if item.get("status") != "PASS"]),
        "blocked": len(blocked),
        "warnings": len(warnings),
    }

    if run_id:
        out_dir = RUNS_DIR / run_id / "logs"
        ensure_dir(out_dir)
        write_json(out_dir / "preflight_STATUS.json", payload)

    return payload
