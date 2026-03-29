from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from lib.common import build_default_run_id, discover_repo_root
from lib.rounds import initialize_run


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a governed run folder structure.")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--sequence", type=int, default=1)
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    run_id = args.run_id or build_default_run_id(args.project_id, sequence=args.sequence)
    manifest = initialize_run(args.project_id, run_id, args.objective, repo_root)
    print(f"[OK] initialized {manifest['run_id']} at {repo_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
