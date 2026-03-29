from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from lib.common import discover_repo_root, read_json
from lib.rounds import initialize_round


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a round inside an existing run.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--round-id", required=True)
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    run_manifest = read_json(repo_root / "ops/runs" / args.run_id / "run_manifest.json")
    manifest = initialize_round(run_manifest["project_id"], args.run_id, args.round_id, repo_root)
    print(f"[OK] initialized {manifest['round_id']} in {args.run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
