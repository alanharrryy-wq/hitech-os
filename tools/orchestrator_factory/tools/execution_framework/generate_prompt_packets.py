from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import json
from pathlib import Path
from lib.common import discover_repo_root, read_json, write_text
from lib.config import load_system_config


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate package prompt packets for a round.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--round-id", required=True)
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    system = load_system_config(repo_root)
    round_root = repo_root / system["runs_root"] / args.run_id / system["rounds_dir_name"] / args.round_id
    prompts_root = round_root / system["prompts_dir_name"]
    packets_root = round_root / system["packets_dir_name"]
    prompts_root.mkdir(parents=True, exist_ok=True)

    worker_template = (repo_root / system["worker_prompt_template"]).read_text(encoding="utf-8")
    for package_id in system["active_package_ids"]:
        packet = read_json(packets_root / package_id / "work_packet.json")
        packet_json = json.dumps(packet, indent=2, ensure_ascii=False)
        write_text(prompts_root / f"{package_id}.prompt.md", worker_template + "\n\n## Active work packet\n```json\n" + packet_json + "\n```\n")

    mission = (repo_root / system["mission_control"]["prompt_template"]).read_text(encoding="utf-8")
    write_text(prompts_root / "mission-control.prompt.md", mission)
    print(f"[OK] generated prompts in {prompts_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
