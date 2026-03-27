from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from lib.common import discover_repo_root, read_json, write_text
from lib.config import load_system_config


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble a markdown summary for a round.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--round-id", required=True)
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    system = load_system_config(repo_root)
    reports_dir = repo_root / system["runs_root"] / args.run_id / system["rounds_dir_name"] / args.round_id / system["reports_dir_name"]
    acceptance = read_json(reports_dir / "acceptance_report.json")
    overlap = read_json(reports_dir / "overlap_report.json")
    lines = [
        f"# Round summary: {args.run_id} / {args.round_id}",
        "",
        f"Overall status: **{acceptance['overall_status']}**",
        f"Overlap ok: **{overlap['ok']}**",
        "",
        "## Package results",
    ]
    for item in acceptance["package_results"]:
        lines.append(f"- {item['package_id']}: {item['status']}")
    if overlap["conflicts"]:
        lines.extend(["", "## Conflicts"])
        for conflict in overlap["conflicts"]:
            lines.append(f"- {conflict['path']}: {', '.join(conflict['packages'])}")
    write_text(reports_dir / "round_summary.md", "\n".join(lines) + "\n")
    print(f"[OK] wrote {reports_dir / 'round_summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
