from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .policies import ApplyPolicy, default_policy
from .safe_paths import assert_safe_relative_path, assert_within_directory

def _write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target

def apply_overlay_to_candidate(
    candidate_root: str | Path,
    overlay_plan: list[dict[str, Any]],
    policy: ApplyPolicy | None = None,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    candidate = Path(candidate_root)
    candidate.mkdir(parents=True, exist_ok=True)
    active_policy = policy or default_policy()
    manifest = {
        "applied": 0,
        "skipped": 0,
        "rejected": 0,
        "total_considered": len(overlay_plan),
    }
    decisions: list[dict[str, Any]] = []
    for item in overlay_plan:
        relpath = assert_safe_relative_path(item["relpath"])
        if any(relpath.startswith(prefix) for prefix in active_policy.rejected_prefixes):
            manifest["rejected"] += 1
            decisions.append({"relpath": relpath, "decision": "rejected"})
            continue
        if item.get("action") == "delete" and not active_policy.allow_delete:
            manifest["skipped"] += 1
            decisions.append({"relpath": relpath, "decision": "skipped_delete"})
            continue
        target = assert_within_directory(candidate, candidate / relpath)
        if not dry_run:
            if item.get("action") == "delete":
                if target.exists():
                    target.unlink()
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(item.get("content", ""), encoding="utf-8")
        manifest["applied"] += 1
        decisions.append({"relpath": relpath, "decision": "applied"})
    payload = {"manifest": manifest, "decisions": decisions, "dry_run": dry_run}
    return payload
