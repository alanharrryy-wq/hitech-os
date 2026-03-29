from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from lib.common import discover_repo_root, read_json, write_text
from lib.config import load_system_config
from lib.reports import compute_apply_order


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an integration-ready summary from acceptance report.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--round-id", required=True)
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    system = load_system_config(repo_root)
    reports_dir = repo_root / system["runs_root"] / args.run_id / system["rounds_dir_name"] / args.round_id / system["reports_dir_name"]
    acceptance = read_json(reports_dir / "acceptance_report.json")
    accepted = [item["package_id"] for item in acceptance["package_results"] if item["status"] in {"accept", "accept_with_conditions"}]
    order = compute_apply_order(repo_root, accepted)
    status = "integration_ready" if acceptance["overall_status"] in {"accept", "accept_with_conditions"} else "not_integration_ready"
    lines = [f"# Integration ready summary for {args.run_id} / {args.round_id}", ""]
    lines.append(f"Overall status: **{acceptance['overall_status']}**")
    lines.append(f"Integration status: **{status}**")
    lines.append("")
    lines.append("## Suggested apply order")
    for package_id in order:
        lines.append(f"1. {package_id}")
    lines.append("")
    lines.append("## Package status")
    for item in acceptance["package_results"]:
        lines.append(f"- {item['package_id']}: {item['status']}")
    write_text(reports_dir / "integration_ready_summary.md", "\n".join(lines) + "\n")
    print(f"[OK] wrote {reports_dir / 'integration_ready_summary.md'}")
    return 0 if status == "integration_ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
