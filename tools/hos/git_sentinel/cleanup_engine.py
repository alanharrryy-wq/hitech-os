#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from shutil import move
from typing import Any

from .config import SentinelConfig
from .git_utils import run_git
from .utils import is_within, now_utc_iso, safe_rmdir, safe_unlink


def _is_safe_cleanup_path(rel_path: str, config: SentinelConfig) -> bool:
    normalized = rel_path.replace("\\", "/").strip("/")
    for prefix in config.safe_cleanup_prefixes:
        prefix_norm = prefix.replace("\\", "/").strip("/")
        if normalized == prefix_norm or normalized.startswith(prefix_norm + "/"):
            return True
    return False


def plan_cleanup(
    config: SentinelConfig,
    scan_state: dict[str, Any],
    artifact_result: dict[str, Any],
) -> dict[str, Any]:
    tracked_set = set(scan_state.get("trackedFiles", []))
    actions: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []

    for row in artifact_result.get("cleanupCandidates", []):
        rel_path = str(row.get("path", ""))
        if rel_path in tracked_set:
            blocked.append({"path": rel_path, "reason": "tracked file"})
            continue
        if not _is_safe_cleanup_path(rel_path, config):
            blocked.append({"path": rel_path, "reason": "outside safe cleanup prefixes"})
            continue
        actions.append(
            {
                "type": "delete_file",
                "path": rel_path,
                "category": row.get("category", "unknown"),
                "reason": row.get("reason", "artifact cleanup"),
            }
        )

    # Duplicate cleanup: keep first lexicographic path, remove rest if safe and untracked.
    for duplicate_group in artifact_result.get("removableDuplicateGroups", []):
        paths = sorted([str(path) for path in duplicate_group.get("paths", [])])
        if len(paths) < 2:
            continue
        for candidate in paths[1:]:
            if candidate in tracked_set:
                blocked.append({"path": candidate, "reason": "duplicate but tracked"})
                continue
            if not _is_safe_cleanup_path(candidate, config):
                blocked.append({"path": candidate, "reason": "duplicate outside safe cleanup prefixes"})
                continue
            actions.append(
                {
                    "type": "delete_file",
                    "path": candidate,
                    "category": "duplicate",
                    "reason": "duplicate artifact",
                }
            )

    # Broken symlinks can be cleaned if in safe zones.
    for rel_path in scan_state.get("brokenSymlinks", []):
        rel = str(rel_path)
        if rel in tracked_set:
            blocked.append({"path": rel, "reason": "broken symlink but tracked"})
            continue
        if not _is_safe_cleanup_path(rel, config):
            blocked.append({"path": rel, "reason": "broken symlink outside safe cleanup prefixes"})
            continue
        actions.append(
            {
                "type": "delete_file",
                "path": rel,
                "category": "orphaned",
                "reason": "broken symlink",
            }
        )

    dead_worktrees = [
        row
        for row in scan_state.get("gitWorktrees", [])
        if bool(row.get("prunable", False)) or not bool(row.get("exists", True))
    ]
    if dead_worktrees:
        actions.append(
            {
                "type": "prune_worktrees",
                "count": len(dead_worktrees),
                "reason": "dead/prunable worktrees detected",
            }
        )

    deduped_actions: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for row in actions:
        key = f"{row.get('type')}::{row.get('path', row.get('reason', ''))}"
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped_actions.append(row)

    return {
        "actions": deduped_actions,
        "blockedActions": blocked,
        "summary": {
            "plannedActions": len(deduped_actions),
            "blockedActions": len(blocked),
            "deadWorktrees": len(dead_worktrees),
        },
    }


def _cleanup_empty_parents(config: SentinelConfig, rel_path: str, max_levels: int = 6) -> int:
    removed = 0
    current = (config.repo_root / rel_path).resolve().parent
    for _ in range(max_levels):
        if current == config.repo_root:
            break
        rel = current.relative_to(config.repo_root).as_posix()
        if not _is_safe_cleanup_path(rel, config):
            break
        if safe_rmdir(current):
            removed += 1
            current = current.parent
            continue
        break
    return removed


def execute_cleanup_plan(
    config: SentinelConfig,
    plan: dict[str, Any],
    apply_changes: bool,
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    deleted_files = 0
    deleted_dirs = 0
    command_log: list[str] = []

    for action in plan.get("actions", []):
        action_type = str(action.get("type", ""))
        if action_type == "prune_worktrees":
            if not apply_changes:
                results.append({"type": action_type, "status": "planned"})
                continue
            completed = run_git(config.repo_root, ["worktree", "prune", "--verbose"], check=False)
            command_log.append("git worktree prune --verbose")
            results.append(
                {
                    "type": action_type,
                    "status": "applied" if completed.returncode == 0 else "failed",
                    "stdout": completed.stdout.strip(),
                    "stderr": completed.stderr.strip(),
                }
            )
            continue

        rel_path = str(action.get("path", "")).replace("\\", "/")
        if not rel_path:
            results.append({"type": action_type, "status": "skipped", "reason": "missing path"})
            continue
        abs_path = (config.repo_root / rel_path).resolve()
        if not is_within(config.repo_root, abs_path):
            results.append({"type": action_type, "path": rel_path, "status": "blocked", "reason": "path escape"})
            continue

        if not apply_changes:
            results.append({"type": action_type, "path": rel_path, "status": "planned"})
            continue

        if abs_path.exists():
            # Reversible cleanup path: quarantine before hard delete.
            quarantine_stamp = now_utc_iso().replace(":", "").replace("-", "")
            quarantine_target = (config.quarantine_dir / quarantine_stamp / rel_path).resolve()
            quarantine_target.parent.mkdir(parents=True, exist_ok=True)
            try:
                move(str(abs_path), str(quarantine_target))
                deleted_files += 1
                deleted_dirs += _cleanup_empty_parents(config=config, rel_path=rel_path)
                results.append(
                    {
                        "type": action_type,
                        "path": rel_path,
                        "status": "quarantined",
                        "quarantinePath": quarantine_target.as_posix(),
                    }
                )
            except OSError:
                if safe_unlink(abs_path):
                    deleted_files += 1
                    deleted_dirs += _cleanup_empty_parents(config=config, rel_path=rel_path)
                    results.append({"type": action_type, "path": rel_path, "status": "applied"})
                else:
                    results.append({"type": action_type, "path": rel_path, "status": "failed"})
            continue

        results.append({"type": action_type, "path": rel_path, "status": "already_missing"})

    return {
        "summary": {
            "plannedActions": int(plan.get("summary", {}).get("plannedActions", 0)),
            "blockedActions": int(plan.get("summary", {}).get("blockedActions", 0)),
            "deletedFiles": deleted_files,
            "deletedDirs": deleted_dirs,
            "applyMode": apply_changes,
        },
        "results": results,
        "commandLog": command_log,
    }
