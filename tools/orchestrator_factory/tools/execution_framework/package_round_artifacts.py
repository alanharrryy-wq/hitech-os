from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from lib.common import deterministic_zip_dir, discover_repo_root
from lib.config import load_system_config


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a deterministic zip of a round folder.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--round-id", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    system = load_system_config(repo_root)
    round_dir = repo_root / system["runs_root"] / args.run_id / system["rounds_dir_name"] / args.round_id
    deterministic_zip_dir(round_dir, Path(args.output))
    print(f"[OK] packaged {round_dir} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
