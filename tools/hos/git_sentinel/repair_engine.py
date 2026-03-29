#!/usr/bin/env python3
from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import Any

from .config import SentinelConfig
from .git_utils import run_git
from .utils import now_utc_iso, safe_unlink


def _is_safe_destructive_path(rel_path: str, config: SentinelConfig) -> bool:
    normalized = rel_path.replace("\\", "/").strip("/")
    for prefix in config.safe_cleanup_prefixes:
        prefix_norm = prefix.replace("\\", "/").strip("/")
        if normalized == prefix_norm or normalized.startswith(prefix_norm + "/"):
            return True
    return False


def _detect_git_config_issues(config: SentinelConfig) -> list[dict[str, str]]:
    target_values = {
        "fetch.prune": "true",
        "gc.auto": "256",
    }
    issues: list[dict[str, str]] = []
    for key, expected in target_values.items():
        current = run_git(config.repo_root, ["config", "--local", "--get", key], check=False)
        current_value = current.stdout.strip().lower() if current.returncode == 0 else ""
        if current_value != expected:
            issues.append(
                {
                    "type": "git_config",
                    "key": key,
                    "expected": expected,
                    "current": current_value,
                }
            )
    return issues


def plan_repairs(
    config: SentinelConfig,
    scan_state: dict[str, Any],
    security_result: dict[str, Any],
    restore_missing_tracked: bool = False,
    allow_revert_unsafe: bool = False,
) -> dict[str, Any]:
    actions: list[dict[str, Any]] = []
    risky_actions: list[dict[str, Any]] = []

    for marker in scan_state.get("nestedGitMarkers", []):
        if marker.get("kind") != "unmanaged_nested_git":
            continue
        marker_path = str(marker.get("markerPath", ""))
        if not marker_path:
            continue
        marker_abs = Path(marker_path)
        if not marker_abs.is_absolute():
            marker_abs = (config.repo_root / marker_path).resolve()
        try:
            marker_rel = marker_abs.relative_to(config.repo_root).as_posix()
        except ValueError:
            marker_rel = marker_abs.as_posix()
        action = {
            "type": "disable_nested_git_marker",
            "path": marker_rel,
            "reason": "unmanaged nested git marker",
        }
        if not _is_safe_destructive_path(marker_rel, config):
            risky_actions.append(action)
            continue
        actions.append(action)

    for broken in scan_state.get("brokenSymlinks", []):
        rel_path = str(broken)
        action = {
            "type": "remove_broken_symlink",
            "path": rel_path,
            "reason": "broken symlink repair",
        }
        if not _is_safe_destructive_path(rel_path, config):
            risky_actions.append(action)
            continue
        actions.append(action)

    for row in scan_state.get("invalidPermissions", []):
        rel_path = str(row.get("path", ""))
        if not rel_path:
            continue
        action = {
            "type": "fix_file_permissions",
            "path": rel_path,
            "reason": str(row.get("reason", "invalid permissions")),
        }
        # Permission repair is non-destructive and allowed for tracked/untracked files.
        actions.append(action)

    git_config_issues = _detect_git_config_issues(config)
    for issue in git_config_issues:
        actions.append(
            {
                "type": "fix_git_config",
                "key": issue["key"],
                "value": issue["expected"],
                "reason": "normalize git local config",
            }
        )

    missing_tracked = [str(path) for path in scan_state.get("trackedDeletedFiles", [])]
    if missing_tracked:
        action = {
            "type": "restore_missing_tracked",
            "files": sorted(missing_tracked),
            "reason": "tracked files missing from working tree",
            "enabled": bool(restore_missing_tracked),
        }
        if restore_missing_tracked:
            actions.append(action)

    high_security_paths = sorted(
        {
            str(row.get("path", ""))
            for row in security_result.get("findings", [])
            if str(row.get("severity", "low")).lower() in {"high", "critical"}
        }
    )
    modified_set = set(scan_state.get("trackedModifiedFiles", []))
    unsafe_modified = sorted([path for path in high_security_paths if path in modified_set])
    if unsafe_modified and allow_revert_unsafe:
        actions.append(
            {
                "type": "revert_unsafe_changes",
                "files": unsafe_modified,
                "reason": "tracked files with high-severity security findings",
            }
        )
    elif unsafe_modified:
        risky_actions.append(
            {
                "type": "revert_unsafe_changes",
                "files": unsafe_modified,
                "reason": "requires explicit allow_revert_unsafe",
            }
        )

    return {
        "actions": actions,
        "riskyActions": risky_actions,
        "summary": {
            "plannedActions": len(actions),
            "riskyActions": len(risky_actions),
            "gitConfigIssues": len(git_config_issues),
            "missingTrackedFiles": len(missing_tracked),
            "highSecurityModifiedFiles": len(unsafe_modified),
        },
    }


def _chunk(values: list[str], chunk_size: int = 100) -> list[list[str]]:
    if not values:
        return []
    return [values[index : index + chunk_size] for index in range(0, len(values), chunk_size)]


def execute_repairs(
    config: SentinelConfig,
    plan: dict[str, Any],
    apply_changes: bool,
) -> dict[str, Any]:
    risky_actions = plan.get("riskyActions", [])
    if apply_changes and risky_actions:
        return {
            "summary": {
                "applyMode": True,
                "executedActions": 0,
                "failedActions": 0,
                "stopTriggered": True,
            },
            "results": [],
            "blocked": risky_actions,
            "stopReason": "repair actions may affect legitimate source files or require explicit allowlist",
        }

    results: list[dict[str, Any]] = []
    executed = 0
    failed = 0

    for action in plan.get("actions", []):
        action_type = str(action.get("type", ""))
        if not apply_changes:
            results.append({"type": action_type, "status": "planned"})
            continue

        if action_type == "disable_nested_git_marker":
            rel_path = str(action.get("path", ""))
            target = (config.repo_root / rel_path).resolve()
            backup_name = f"{target.name}.sentinel-disabled-{now_utc_iso().replace(':', '').replace('-', '')}"
            backup_path = target.with_name(backup_name)
            try:
                target.rename(backup_path)
                executed += 1
                results.append(
                    {
                        "type": action_type,
                        "path": rel_path,
                        "status": "applied",
                        "backupPath": backup_path.as_posix(),
                    }
                )
            except OSError as exc:
                failed += 1
                results.append({"type": action_type, "path": rel_path, "status": "failed", "error": str(exc)})
            continue

        if action_type == "remove_broken_symlink":
            rel_path = str(action.get("path", ""))
            target = (config.repo_root / rel_path).resolve()
            if safe_unlink(target):
                executed += 1
                results.append({"type": action_type, "path": rel_path, "status": "applied"})
            else:
                if not target.exists():
                    results.append({"type": action_type, "path": rel_path, "status": "already_missing"})
                else:
                    failed += 1
                    results.append({"type": action_type, "path": rel_path, "status": "failed"})
            continue

        if action_type == "fix_git_config":
            key = str(action.get("key", ""))
            value = str(action.get("value", ""))
            completed = run_git(config.repo_root, ["config", "--local", key, value], check=False)
            if completed.returncode == 0:
                executed += 1
                results.append({"type": action_type, "key": key, "value": value, "status": "applied"})
            else:
                failed += 1
                results.append(
                    {
                        "type": action_type,
                        "key": key,
                        "status": "failed",
                        "stderr": completed.stderr.strip(),
                    }
                )
            continue

        if action_type == "fix_file_permissions":
            rel_path = str(action.get("path", ""))
            target = (config.repo_root / rel_path).resolve()
            try:
                current_mode = stat.S_IMODE(target.stat().st_mode)
                normalized_mode = current_mode | stat.S_IRUSR | stat.S_IWUSR
                os.chmod(target, normalized_mode)
                executed += 1
                results.append(
                    {
                        "type": action_type,
                        "path": rel_path,
                        "status": "applied",
                        "modeBefore": oct(current_mode),
                        "modeAfter": oct(normalized_mode),
                    }
                )
            except OSError as exc:
                failed += 1
                results.append({"type": action_type, "path": rel_path, "status": "failed", "error": str(exc)})
            continue

        if action_type in {"restore_missing_tracked", "revert_unsafe_changes"}:
            files = sorted(set(str(item) for item in action.get("files", [])))
            if not files:
                results.append({"type": action_type, "status": "skipped", "reason": "no files"})
                continue
            all_ok = True
            for chunk in _chunk(files, 80):
                completed = run_git(config.repo_root, ["restore", "--", *chunk], check=False)
                if completed.returncode != 0:
                    all_ok = False
                    failed += 1
                    results.append(
                        {
                            "type": action_type,
                            "status": "failed",
                            "files": chunk,
                            "stderr": completed.stderr.strip(),
                        }
                    )
            if all_ok:
                executed += 1
                results.append({"type": action_type, "status": "applied", "files": files})
            continue

        results.append({"type": action_type, "status": "skipped", "reason": "unsupported action"})

    return {
        "summary": {
            "applyMode": apply_changes,
            "executedActions": executed,
            "failedActions": failed,
            "stopTriggered": False,
        },
        "results": results,
        "blocked": risky_actions,
    }
