from pathlib import Path

from .manifest_io import read_json

REQUIRED_PATHS = [
    ("manifests", "run_manifest.json"),
    ("manifests", "apply_manifest.json"),
    ("manifests", "diff_manifest.json"),
    ("manifests", "promotion_gate.json"),
    ("review_bundle", "promotion_review.json"),
]

def load_workspace_state(workspace_root):
    workspace_root = Path(workspace_root)
    manifests_dir = workspace_root / "manifests"
    review_bundle_dir = workspace_root / "review_bundle"

    return {
        "workspace_root": workspace_root,
        "manifests_dir": manifests_dir,
        "review_bundle_dir": review_bundle_dir,
    }

def run_preflight(workspace_root):
    state = load_workspace_state(workspace_root)
    issues = []
    loaded = {}

    for rel1, rel2 in REQUIRED_PATHS:
        path = state["workspace_root"] / rel1 / rel2
        if not path.exists():
            issues.append(f"missing_required_file:{path}")
        else:
            loaded[f"{rel1}/{rel2}"] = path

    if issues:
        return {
            "ok": False,
            "issues": issues,
            "state": _stringify_state(state),
            "loaded_files": {k: str(v) for k, v in loaded.items()},
        }

    run_manifest = read_json(state["manifests_dir"] / "run_manifest.json")
    apply_manifest = read_json(state["manifests_dir"] / "apply_manifest.json")
    diff_manifest = read_json(state["manifests_dir"] / "diff_manifest.json")
    gate_manifest = read_json(state["manifests_dir"] / "promotion_gate.json")
    promotion_review = read_json(state["review_bundle_dir"] / "promotion_review.json")

    run_id = run_manifest.get("run_id")
    apply_run_id = apply_manifest.get("run_id")

    if apply_run_id and run_id and apply_run_id != run_id:
        issues.append(f"run_id_mismatch:run={run_id}:apply={apply_run_id}")

    source_counts = promotion_review.get("source_counts", {})
    diff_counts = diff_manifest.get("counts", {})
    if source_counts.get("diff", {}).get("total_touched") not in (None, diff_counts.get("total_touched")):
        issues.append("promotion_review_diff_count_mismatch")

    return {
        "ok": len(issues) == 0,
        "issues": issues,
        "state": _stringify_state(state),
        "run_manifest": run_manifest,
        "apply_manifest": apply_manifest,
        "diff_manifest": diff_manifest,
        "gate_manifest": gate_manifest,
        "promotion_review": promotion_review,
    }

def _stringify_state(state):
    return {k: str(v) for k, v in state.items()}
