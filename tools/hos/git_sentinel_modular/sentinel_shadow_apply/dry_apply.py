from pathlib import Path
import json
import shutil

from .policies import default_policy
from .safe_paths import assert_within_directory
from .overlay_plan import build_overlay_plan

def _write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

def apply_overlay_to_candidate(workspace, overlay_source, policy=None):
    policy = policy or default_policy()
    plan = build_overlay_plan(overlay_source=overlay_source, policy=policy)

    candidate_dir = Path(workspace.candidate_dir)
    applied = []
    rejected = []

    for action in plan["actions"]:
        relpath = action["relative_path"]
        source = Path(action["source"])
        target = assert_within_directory(candidate_dir, candidate_dir / relpath)

        if target.exists() and target.is_dir():
            rejected.append({
                "path": relpath,
                "reason": "target_is_directory",
            })
            continue

        if target.exists() and not policy.allow_overwrite:
            rejected.append({
                "path": relpath,
                "reason": "overwrite_not_allowed",
            })
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

        applied.append({
            "path": relpath,
            "bytes": source.stat().st_size,
        })

    payload = {
        "run_id": workspace.run_id,
        "overlay_source": plan["overlay_source"],
        "applied": applied,
        "skipped": plan["skipped"],
        "rejected": rejected,
        "counts": {
            "applied": len(applied),
            "skipped": len(plan["skipped"]),
            "rejected": len(rejected),
            "total_considered": len(applied) + len(plan["skipped"]) + len(rejected),
        },
    }

    manifest_path = Path(workspace.manifests_dir) / "apply_manifest.json"
    _write_json(manifest_path, payload)

    return {
        "manifest_path": manifest_path,
        "manifest": payload,
    }
