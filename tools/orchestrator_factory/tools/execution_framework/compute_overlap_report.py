from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from lib.bundles import validate_bundle_zip
from lib.common import discover_repo_root, write_json
from lib.config import load_system_config
from lib.reports import compute_overlap


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute overlap report for all incoming bundles in a round.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--round-id", required=True)
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    system = load_system_config(repo_root)
    round_root = repo_root / system["runs_root"] / args.run_id / system["rounds_dir_name"] / args.round_id
    incoming = round_root / system["incoming_dir_name"]
    reports_dir = round_root / system["reports_dir_name"]
    bundle_reports = [validate_bundle_zip(path, repo_root) for path in sorted(incoming.glob("*.zip"))]
    overlap = compute_overlap(bundle_reports)
    write_json(reports_dir / "overlap_report.json", overlap)
    print(f"[OK] wrote {reports_dir / 'overlap_report.json'}")
    return 0 if overlap["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
