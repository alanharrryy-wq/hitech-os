from __future__ import annotations

import argparse
import json
import os

from .final_runner import run_operational_atlas


def main(argv=None):
    parser = argparse.ArgumentParser(prog="code-atlas-operational")
    parser.add_argument("--repo", default=os.environ.get("CODE_ATLAS_PROJECT_ROOT", "."))
    parser.add_argument("--out", default=os.environ.get("CODE_ATLAS_OUTPUT_ROOT"), required=os.environ.get("CODE_ATLAS_OUTPUT_ROOT") is None)
    parser.add_argument("--result-root", default=os.environ.get("CODE_ATLAS_RESULT_ROOT"))
    parser.add_argument("--profile", default=os.environ.get("CODE_ATLAS_PROFILE"), help="Optional project profile JSON. Product adapters are selected only through explicit profile metadata.")
    args = parser.parse_args(argv)
    if args.profile:
        os.environ["CODE_ATLAS_PROFILE"] = args.profile
    print(json.dumps(run_operational_atlas(args.repo, args.out, args.result_root), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
