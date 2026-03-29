from pathlib import Path
import argparse
import json
import sys
import time

def _write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Prepare a no-op promotion/cutover pipeline for a shadow workspace.")
    parser.add_argument("--modular-root", required=True)
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--promotion-policy", required=False)
    parser.add_argument("--cutover-policy", required=False)
    args = parser.parse_args()

    modular_root = Path(args.modular_root)
    workspace_root = Path(args.workspace_root)
    if not modular_root.exists():
        raise SystemExit(f"Modular root not found: {modular_root}")
    if not workspace_root.exists():
        raise SystemExit(f"Workspace root not found: {workspace_root}")

    sys.path.insert(0, str(modular_root))

    manifests_dir = workspace_root / "manifests"
    run_manifest_path = manifests_dir / "run_manifest.json"
    if not run_manifest_path.exists():
        raise SystemExit(f"Missing run_manifest.json: {run_manifest_path}")

    run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
    run_id = run_manifest.get("run_id", "unknown")

    apply_manifest_path = manifests_dir / "apply_manifest.json"
    if not apply_manifest_path.exists():
        payload = {
            "run_id": run_id,
            "overlay_source": None,
            "applied": [],
            "skipped": [],
            "rejected": [],
            "counts": {
                "applied": 0,
                "skipped": 0,
                "rejected": 0,
                "total_considered": 0,
            },
            "prepared_as": "noop_pipeline_validation",
            "prepared_at_epoch": time.time(),
        }
        _write_json(apply_manifest_path, payload)

    from sentinel_shadow.workspace import ShadowWorkspace
    from sentinel_shadow import finalize_shadow_run
    from sentinel_promotion import build_promotion_bundle
    from sentinel_cutover import build_cutover_readiness_bundle

    workspace = ShadowWorkspace(
        run_id=run_id,
        root=workspace_root,
        baseline_dir=workspace_root / "baseline",
        candidate_dir=workspace_root / "candidate",
        manifests_dir=workspace_root / "manifests",
    )

    finalize_shadow_run(workspace)
    build_promotion_bundle(
        workspace_root=workspace_root,
        policy_path=Path(args.promotion_policy) if args.promotion_policy else None,
    )
    build_cutover_readiness_bundle(
        workspace_root=workspace_root,
        policy_path=Path(args.cutover_policy) if args.cutover_policy else None,
    )

    result = {
        "workspace_root": str(workspace_root),
        "run_id": run_id,
        "prepared": [
            str(apply_manifest_path),
            str(manifests_dir / "diff_manifest.json"),
            str(manifests_dir / "promotion_gate.json"),
            str(workspace_root / "review_bundle" / "promotion_review.json"),
            str(workspace_root / "cutover_bundle" / "release_candidate_summary.json"),
        ]
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
