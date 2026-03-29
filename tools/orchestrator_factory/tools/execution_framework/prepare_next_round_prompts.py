from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from lib.common import discover_repo_root, read_json, write_text
from lib.config import load_system_config


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate retry or next-round prompts from an acceptance report.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--round-id", required=True)
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    system = load_system_config(repo_root)
    round_root = repo_root / system["runs_root"] / args.run_id / system["rounds_dir_name"] / args.round_id
    reports_dir = round_root / system["reports_dir_name"]
    prompts_dir = round_root / "next_prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    acceptance = read_json(reports_dir / "acceptance_report.json")
    retry_template = (repo_root / system["retry_prompt_template"]).read_text(encoding="utf-8")
    for item in acceptance["package_results"]:
        if item["status"] in {"reject", "accept_with_conditions"}:
            lines = [retry_template, "", f"Package: {item['package_id']}", "", "Corrections or conditions:"]
            for correction in item["corrections"]:
                lines.append(f"- {correction}")
            write_text(prompts_dir / f"{item['package_id']}.retry.md", "\n".join(lines) + "\n")
    print(f"[OK] wrote retry prompts in {prompts_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
