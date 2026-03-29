from pathlib import Path
import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(description="Create a shadow workspace using sentinel_shadow.")
    parser.add_argument("--modular-root", required=True)
    parser.add_argument("--run-id", required=False)
    args = parser.parse_args()

    modular_root = Path(args.modular_root)
    if not modular_root.exists():
        raise SystemExit(f"Modular root not found: {modular_root}")

    sys.path.insert(0, str(modular_root))

    from sentinel_shadow import prepare_shadow_run

    result = prepare_shadow_run(source_root=modular_root, run_id=args.run_id)
    workspace = result["workspace"]

    payload = {
        "run_id": workspace.run_id,
        "workspace_root": str(workspace.root),
        "baseline_dir": str(workspace.baseline_dir),
        "candidate_dir": str(workspace.candidate_dir),
        "manifests_dir": str(workspace.manifests_dir),
        "run_manifest_path": str(result["run_manifest_path"]),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
