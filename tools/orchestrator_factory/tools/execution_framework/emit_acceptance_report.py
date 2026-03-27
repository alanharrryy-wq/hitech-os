from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from lib.bundles import validate_bundle_zip
from lib.common import discover_repo_root, read_json, write_json
from lib.config import load_system_config
from lib.reports import build_acceptance_result, compute_overlap


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit acceptance report for a round.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--round-id", required=True)
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    system = load_system_config(repo_root)
    round_root = repo_root / system["runs_root"] / args.run_id / system["rounds_dir_name"] / args.round_id
    incoming = round_root / system["incoming_dir_name"]
    reports_dir = round_root / system["reports_dir_name"]
    reports_dir.mkdir(parents=True, exist_ok=True)
    round_manifest = read_json(round_root / "round_manifest.json")
    bundle_reports = [validate_bundle_zip(path, repo_root) for path in sorted(incoming.glob("*.zip"))]
    overlap_path = reports_dir / "overlap_report.json"
    if overlap_path.exists():
        overlap = read_json(overlap_path)
    else:
        overlap = compute_overlap(bundle_reports)
        write_json(overlap_path, overlap)
    acceptance = build_acceptance_result(round_manifest["project_id"], args.run_id, args.round_id, bundle_reports, overlap)
    write_json(reports_dir / "acceptance_report.json", acceptance)
    print(f"[OK] wrote {reports_dir / 'acceptance_report.json'}")
    return 0 if acceptance["overall_status"] not in {"reject"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
