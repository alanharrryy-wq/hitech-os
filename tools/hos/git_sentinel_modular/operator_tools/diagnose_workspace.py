from pathlib import Path
import argparse
import json

REQUIRED = [
    ("manifests", "run_manifest.json"),
    ("manifests", "apply_manifest.json"),
    ("manifests", "diff_manifest.json"),
    ("manifests", "promotion_gate.json"),
    ("review_bundle", "promotion_review.json"),
    ("cutover_bundle", "release_candidate_summary.json"),
]

def main():
    parser = argparse.ArgumentParser(description="Diagnose a Git Sentinel shadow workspace for execute readiness.")
    parser.add_argument("--workspace-root", required=True)
    args = parser.parse_args()

    root = Path(args.workspace_root)
    result = {
        "workspace_root": str(root),
        "exists": root.exists(),
        "required": [],
        "missing": [],
        "present": [],
        "status": "unknown",
        "recommendations": [],
    }

    if not root.exists():
        result["status"] = "missing_workspace"
        result["recommendations"].append("Create or select a valid shadow workspace.")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2

    for a, b in REQUIRED:
        p = root / a / b
        item = {"name": f"{a}/{b}", "path": str(p), "exists": p.exists()}
        result["required"].append(item)
        if p.exists():
            result["present"].append(item["name"])
        else:
            result["missing"].append(item["name"])

    if result["missing"]:
        result["status"] = "incomplete_for_execute"
        if "manifests/apply_manifest.json" in result["missing"]:
            result["recommendations"].append("Run shadow apply or a no-op pipeline preparer to create apply_manifest.json.")
        if "manifests/diff_manifest.json" in result["missing"] or "manifests/promotion_gate.json" in result["missing"]:
            result["recommendations"].append("Finalize the shadow run to generate diff_manifest.json and promotion_gate.json.")
        if "review_bundle/promotion_review.json" in result["missing"]:
            result["recommendations"].append("Run sentinel_promotion to build review_bundle.")
        if "cutover_bundle/release_candidate_summary.json" in result["missing"]:
            result["recommendations"].append("Run sentinel_cutover to build cutover_bundle.")
    else:
        result["status"] = "ready_for_execute_module"

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
