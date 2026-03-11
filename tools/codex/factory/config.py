from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from .common import (
    FACTORY_DIR,
    REPO_ROOT,
    canonical_worker_id,
    ensure_dir,
    read_json,
    write_json,
)
from .schemas import validate_payload

DEFAULT_CONFIG_PATH = FACTORY_DIR / "factory.config.json"
ENV_PREFIX = "FACTORY_"
IGNORED_ENV_KEYS = {
    "FACTORY_AHK_EXE",
    "FACTORY_SLOW_TESTS",
    "FACTORY_WORKTREE_MODE",
}
IGNORED_ENV_PREFIXES = (
    "FACTORY_DISPATCH__",
)


def default_factory_config() -> dict[str, Any]:
    return {
        "schema_version": 2,
        "contract_version": 2,
        "run": {
            "kind": "factory",
            "run_prefix": "factory",
            "branch_prefix": "codex/factory",
            "base_ref": "HEAD",
            "strict_collision_mode": True,
            "allow_identical_patch_overlap": False,
            "enforce_anti_padding_gate": False,
            "quarantine_on_suspicious_bundle": True,
            "auto_closeout_workers": True,
            "auto_preflight_repair": True,
            "auto_repair_missing_folders": True,
            "integrator_watch_ledger": True,
            "integrator_wait_for_workers": True,
            "visual_baseline_owner": "C_features",
            "visual_baseline_update_default": True,
            "chat_hygiene_policy": "clean_start_required",
        },
        "paths": {
            "repo_root": REPO_ROOT.as_posix(),
            "runs_dir": (REPO_ROOT / "tools" / "codex" / "runs").as_posix(),
            "worktrees_dir": (REPO_ROOT / "tools" / "codex" / "worktrees").as_posix(),
        },
        "workers": {
            "required_worker_files": [
                "STATUS.json",
                "SUMMARY.md",
                "FILES_CHANGED.json",
                "DIFF.patch",
                "SUGGESTIONS.md",
                "SCOPE_LOCK.json",
                "HANDOFF_NOTE.json",
                "LOGS/INDEX.json",
                "CODEX_OUTPUT.txt",
            ],
            "required_integrator_files": [
                "STATUS.json",
                "FINAL_REPORT.txt",
                "FILES_CHANGED.json",
                "DIFF.patch",
                "MERGE_PLAN.md",
                "LOGS/INDEX.json",
            ],
            "allowlist_globs": {
                "A_core": ["apps/**", "packages/**", "docs/**"],
                "B_tooling": ["tools/**", "docs/**", "packages/**"],
                "C_features": [
                    "apps/**",
                    "packages/**",
                    "docs/**",
                    "docs/visual-baselines/**",
                    "tools/_local/visual/**",
                ],
                "D_validation": ["docs/**", "tools/**", "packages/**"],
            },
            "denylist_globs": {
                "A_core": [".github/workflows/**", ".git/**", ".env", ".env.*"],
                "B_tooling": [".github/workflows/**", ".git/**", ".env", ".env.*"],
                "C_features": [".github/workflows/**", ".git/**", ".env", ".env.*"],
                "D_validation": [".github/workflows/**", ".git/**", ".env", ".env.*"],
            },
        },
        "security": {
            "allow_shell_execution": False,
            "allow_executable_artifacts": False,
            "secret_scan_enabled": True,
        },
        "feature_flags": {
            "enable_identical_patch_overlap": False,
            "enable_quarantine": False,
            "enable_ledger_compaction": False,
        },
    }


def _deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    all_keys = sorted(set(base.keys()) | set(override.keys()))
    for key in all_keys:
        left = base.get(key)
        right = override.get(key)
        if isinstance(left, Mapping) and isinstance(right, Mapping):
            merged[key] = _deep_merge(dict(left), dict(right))
        elif key in override:
            merged[key] = deepcopy(right)
        else:
            merged[key] = deepcopy(left)
    return merged


def _coerce_scalar(value: str) -> Any:
    raw = value.strip()
    lowered = raw.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None
    if lowered.lstrip("-").isdigit():
        try:
            return int(lowered)
        except ValueError:
            pass
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _set_nested(payload: dict[str, Any], dotted_key: str, value: Any) -> None:
    parts = [part for part in dotted_key.split(".") if part]
    if not parts:
        return
    cursor: dict[str, Any] = payload
    for part in parts[:-1]:
        current = cursor.get(part)
        if not isinstance(current, dict):
            current = {}
            cursor[part] = current
        cursor = current
    cursor[parts[-1]] = value


def _env_to_config(env: Mapping[str, str]) -> dict[str, Any]:
    overlay: dict[str, Any] = {}
    for key in sorted(env):
        if not key.startswith(ENV_PREFIX):
            continue
        if key in IGNORED_ENV_KEYS:
            continue
        if any(key.startswith(prefix) for prefix in IGNORED_ENV_PREFIXES):
            continue
        dotted = key[len(ENV_PREFIX) :].lower().replace("__", ".")
        value = _coerce_scalar(env[key])
        _set_nested(overlay, dotted, value)
    return overlay


def _canonicalize_worker_globs(section: Any) -> dict[str, Any]:
    if not isinstance(section, Mapping):
        return {}
    normalized: dict[str, Any] = {}
    for worker, value in section.items():
        canonical = canonical_worker_id(str(worker).strip())
        if not canonical:
            continue
        existing = normalized.get(canonical)
        if isinstance(existing, list) and isinstance(value, list):
            merged: list[Any] = [*existing]
            for item in value:
                if item not in merged:
                    merged.append(item)
            normalized[canonical] = merged
        else:
            normalized[canonical] = deepcopy(value)
    return normalized


def _canonicalize_merged_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    merged = deepcopy(dict(payload))
    run_block = merged.get("run", {})
    if isinstance(run_block, Mapping):
        run_obj = dict(run_block)
        owner = run_obj.get("visual_baseline_owner")
        if isinstance(owner, str):
            run_obj["visual_baseline_owner"] = canonical_worker_id(owner)
        merged["run"] = run_obj

    workers_block = merged.get("workers", {})
    if isinstance(workers_block, Mapping):
        workers_obj = dict(workers_block)
        workers_obj["allowlist_globs"] = _canonicalize_worker_globs(workers_obj.get("allowlist_globs", {}))
        workers_obj["denylist_globs"] = _canonicalize_worker_globs(workers_obj.get("denylist_globs", {}))
        merged["workers"] = workers_obj
    return merged


def resolve_config_path(explicit_path: str | None = None) -> Path:
    if explicit_path:
        return Path(explicit_path).expanduser().resolve(strict=False)
    return DEFAULT_CONFIG_PATH


def load_config_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = read_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"factory config must be an object: {path.as_posix()}")
    return payload


def validate_config(payload: Mapping[str, Any]) -> list[str]:
    return validate_payload("factory_config", dict(payload))


def load_factory_config(
    *,
    config_path: str | None = None,
    env: Mapping[str, str] | None = None,
    cli_overrides: Mapping[str, Any] | None = None,
    strict: bool = True,
) -> dict[str, Any]:
    defaults = default_factory_config()
    resolved_path = resolve_config_path(config_path)
    file_payload = load_config_file(resolved_path)
    env_payload = _env_to_config(env or os.environ)
    cli_payload = dict(cli_overrides or {})

    merged = _deep_merge(defaults, file_payload)
    merged = _deep_merge(merged, env_payload)
    merged = _deep_merge(merged, cli_payload)
    merged = _canonicalize_merged_config(merged)

    meta = {
        "config_path": resolved_path.as_posix(),
        "config_exists": resolved_path.exists(),
        "env_prefix": ENV_PREFIX,
        "strict": bool(strict),
    }
    merged["_meta"] = meta
    errors = validate_config(merged)
    if errors and strict:
        joined = "\n".join(errors)
        raise ValueError(f"factory config invalid:\n{joined}")
    merged["_validation_errors"] = errors
    return merged


def write_default_config(path: str | None = None) -> Path:
    target = resolve_config_path(path)
    ensure_dir(target.parent)
    if not target.exists():
        write_json(target, default_factory_config())
    return target
