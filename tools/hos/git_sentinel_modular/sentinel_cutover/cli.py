from pathlib import Path
import argparse
import json

from .bundle import build_cutover_readiness_bundle

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build a cutover readiness bundle from a shadow workspace."
    )
    parser.add_argument(
        "--workspace-root",
        required=True,
        help="Path to the shadow workspace root.",
    )
    parser.add_argument(
        "--policy",
        required=False,
        help="Optional path to a cutover policy JSON override.",
    )

    args = parser.parse_args(argv)

    result = build_cutover_readiness_bundle(
        workspace_root=Path(args.workspace_root),
        policy_path=Path(args.policy) if args.policy else None,
    )

    print(json.dumps({
        "bundle_dir": str(result["bundle_dir"]),
        "status": result["decision"]["status"],
        "overall_risk": result["decision"]["overall_risk"],
        "reviewers": result["decision"]["reviewers"],
    }, indent=2, sort_keys=True))
    return 0
