from pathlib import Path

from .manifest_io import read_json

def load_workspace_context(workspace_root):
    workspace_root = Path(workspace_root)
    manifests_dir = workspace_root / "manifests"
    review_bundle_dir = workspace_root / "review_bundle"
    cutover_bundle_dir = workspace_root / "cutover_bundle"
    candidate_dir = workspace_root / "candidate"
    baseline_dir = workspace_root / "baseline"

    required = {
        "run_manifest": manifests_dir / "run_manifest.json",
        "apply_manifest": manifests_dir / "apply_manifest.json",
        "diff_manifest": manifests_dir / "diff_manifest.json",
        "promotion_gate": manifests_dir / "promotion_gate.json",
        "promotion_review": review_bundle_dir / "promotion_review.json",
        "cutover_summary": cutover_bundle_dir / "release_candidate_summary.json",
    }

    missing = [name for name, path in required.items() if not path.exists()]
    if missing:
        raise RuntimeError(f"Workspace missing required files: {missing}")

    return {
        "workspace_root": workspace_root,
        "manifests_dir": manifests_dir,
        "review_bundle_dir": review_bundle_dir,
        "cutover_bundle_dir": cutover_bundle_dir,
        "candidate_dir": candidate_dir,
        "baseline_dir": baseline_dir,
        "run_manifest": read_json(required["run_manifest"]),
        "apply_manifest": read_json(required["apply_manifest"]),
        "diff_manifest": read_json(required["diff_manifest"]),
        "promotion_gate": read_json(required["promotion_gate"]),
        "promotion_review": read_json(required["promotion_review"]),
        "cutover_summary": read_json(required["cutover_summary"]),
    }
