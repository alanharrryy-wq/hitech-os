from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

from .common import REPO_ROOT, RUNS_DIR, iso_utc
from .config import load_factory_config, resolve_config_path
from .schemas import contracts_check
from .skills_index import (
    DEFAULT_SKILLS_ROOT,
    EXPECTED_FACTORY_ROLES,
    SKILLS_ROOT_CANDIDATES,
    build_skills_index,
    generate_and_write_skills_index,
    resolve_skills_root,
)


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


def _check_meaningful_gate_contract() -> dict[str, Any]:
    schema_path = REPO_ROOT / "tools" / "codex" / "schemas" / "files_changed.schema.json"
    if not schema_path.exists():
        return {
            "check": "meaningful_gate_contract",
            "status": "BLOCKED",
            "detail": "files_changed.schema.json is missing",
            "next_action": f"Restore `{schema_path.as_posix()}`.",
        }
    try:
        payload = json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "check": "meaningful_gate_contract",
            "status": "BLOCKED",
            "detail": f"schema read error: {exc}",
            "next_action": "Fix files_changed schema JSON syntax.",
        }
    properties = payload.get("properties", {}) if isinstance(payload, dict) else {}
    any_of = payload.get("anyOf", []) if isinstance(payload, dict) else []
    has_noop = all(name in properties for name in ("noop", "noop_reason", "noop_ack"))
    has_gate_clause = isinstance(any_of, list) and len(any_of) > 0
    ok = bool(has_noop and has_gate_clause)
    return {
        "check": "meaningful_gate_contract",
        "status": "PASS" if ok else "BLOCKED",
        "detail": f"noop_fields={has_noop} anyOf={has_gate_clause}",
        "next_action": "" if ok else "Add noop fields + anyOf rule to files_changed schema.",
    }


def _check_skills_root() -> dict[str, Any]:
    root_info = resolve_skills_root(repo_root=REPO_ROOT)
    skills_root = Path(str(root_info["path"]))
    exists = skills_root.exists() and skills_root.is_dir()
    candidates = ", ".join(SKILLS_ROOT_CANDIDATES)
    return {
        "check": "skills_autoload_root",
        "status": "PASS" if exists else "WARN",
        "detail": skills_root.as_posix() if exists else f"missing candidates: {candidates}",
        "next_action": ""
        if exists
        else f"Create `{DEFAULT_SKILLS_ROOT}` (preferred) with role folders and SKILL.md files.",
    }


def _check_skills_docs() -> dict[str, Any]:
    root_info = resolve_skills_root(repo_root=REPO_ROOT)
    skills_root = Path(str(root_info["path"]))
    if not skills_root.exists() or not skills_root.is_dir():
        return {
            "check": "skills_autoload_docs",
            "status": "WARN",
            "detail": "skills root is missing",
            "next_action": f"Create `{DEFAULT_SKILLS_ROOT}` before enabling role-skills auto-load.",
        }
    docs = sorted(skills_root.rglob("SKILL.md"), key=lambda path: (path.as_posix().lower(), path.as_posix()))
    return {
        "check": "skills_autoload_docs",
        "status": "PASS" if len(docs) > 0 else "WARN",
        "detail": f"skill_docs={len(docs)}",
        "next_action": "" if docs else f"Add at least one `SKILL.md` under `{skills_root.as_posix()}/<role>/`.",
    }


def _check_skills_role_coverage() -> dict[str, Any]:
    try:
        index = build_skills_index(repo_root=REPO_ROOT)
    except Exception as exc:
        return {
            "check": "skills_autoload_role_coverage",
            "status": "BLOCKED",
            "detail": f"index error: {exc}",
            "next_action": "Fix skills indexing errors before running factory flows.",
        }
    sources = index.get("role_sources", {}) if isinstance(index, dict) else {}
    missing = [role for role in EXPECTED_FACTORY_ROLES if not str(sources.get(role, "")).strip()]
    mapped = [role for role in EXPECTED_FACTORY_ROLES if str(sources.get(role, "")).strip()]
    if not mapped:
        return {
            "check": "skills_autoload_role_coverage",
            "status": "WARN",
            "detail": "no role mappings discovered (skills root unavailable)",
            "next_action": f"Add role folders under `{DEFAULT_SKILLS_ROOT}` to enable skills injection.",
        }
    return {
        "check": "skills_autoload_role_coverage",
        "status": "PASS" if not missing else "BLOCKED",
        "detail": "all roles mapped" if not missing else f"missing role mappings: {','.join(missing)}",
        "next_action": ""
        if not missing
        else "Add direct role folders or legacy-mapped folders under the active skills root.",
    }


def _check_skills_index_generation() -> dict[str, Any]:
    try:
        payload = generate_and_write_skills_index(repo_root=REPO_ROOT)
    except Exception as exc:
        return {
            "check": "skills_autoload_index_generation",
            "status": "BLOCKED",
            "detail": f"generation error: {exc}",
            "next_action": "Run `python -m tools.codex.factory skills:index` and fix reported errors.",
        }
    return {
        "check": "skills_autoload_index_generation",
        "status": "PASS",
        "detail": f"index_json={payload.get('index_json', '')} index_md={payload.get('index_md', '')}",
        "next_action": "",
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
    checks.append(_check_path(REPO_ROOT / "tools" / "codex" / "verify" / "meaningful_gate.py", required=True))
    checks.append(_check_path(RUNS_DIR, required=False))
    checks.append(_check_skills_root())
    checks.append(_check_skills_docs())
    checks.append(_check_skills_role_coverage())
    checks.append(_check_skills_index_generation())

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
    checks.append(_check_meaningful_gate_contract())

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
