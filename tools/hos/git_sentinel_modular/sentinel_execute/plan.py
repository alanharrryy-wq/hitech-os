from __future__ import annotations

from pathlib import Path

from .path_guard import is_protected_path
from .policy_loader import default_policy

def _append_action(actions: list[dict], action: dict) -> None:
    actions.append(action)

def build_execution_plan(diff_manifest: dict, target_root: str | Path, candidate_root: str | Path, policy: dict | None = None) -> dict:
    active_policy = policy or default_policy()
    actions: list[dict] = []
    blocked = 0
    warnings = 0
    for relpath in diff_manifest.get("added", []):
        _append_action(actions, {"action": "add", "relpath": relpath, "source": str(Path(candidate_root) / relpath)})
    for relpath in diff_manifest.get("changed", []):
        _append_action(actions, {"action": "update", "relpath": relpath, "source": str(Path(candidate_root) / relpath)})
    for relpath in diff_manifest.get("removed", []):
        if is_protected_path(relpath, active_policy["protected_prefixes"]) or not active_policy["allow_delete"]:
            blocked += 1
            warnings += 1
            continue
        _append_action(actions, {"action": "delete", "relpath": relpath})
    return {
        "actions": actions,
        "blocked": blocked,
        "warnings": warnings,
        "counts": {
            "actions": len(actions),
            "blocked": blocked,
            "warnings": warnings,
            "adds": len(diff_manifest.get("added", [])),
            "updates": len(diff_manifest.get("changed", [])),
            "deletes": max(0, len(diff_manifest.get("removed", [])) - blocked),
        },
        "target_root": str(target_root),
    }
