from pathlib import Path
import argparse
import json

from .bundle import build_promotion_bundle

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build a promotion review bundle from a shadow workspace."
    )
    parser.add_argument(
        "--workspace-root",
        required=True,
        help="Path to the shadow workspace root that contains manifests/",
    )
    parser.add_argument(
        "--policy",
        required=False,
        help="Optional path to a promotion policy JSON override.",
    )

    args = parser.parse_args(argv)

    result = build_promotion_bundle(
        workspace_root=Path(args.workspace_root),
        policy_path=Path(args.policy) if args.policy else None,
    )

    print(json.dumps({
        "review_dir": str(result["review_dir"]),
        "status": result["decision"]["status"],
        "reviewers": result["decision"]["reviewers"],
    }, indent=2, sort_keys=True))

    return 0
