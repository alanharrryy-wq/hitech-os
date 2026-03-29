from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from lib.common import discover_repo_root, read_json, write_json, write_text
from lib.config import load_system_config
from lib.rounds import build_work_packet


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate package work packets for a round.')
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--round-id', required=True)
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    system = load_system_config(repo_root)
    run_manifest = read_json(repo_root / system['runs_root'] / args.run_id / 'run_manifest.json')
    packets_root = repo_root / system['runs_root'] / args.run_id / system['rounds_dir_name'] / args.round_id / system['packets_dir_name']
    packets_root.mkdir(parents=True, exist_ok=True)
    for package_id in system['active_package_ids']:
        packet = build_work_packet(run_manifest['project_id'], args.run_id, args.round_id, package_id, repo_root)
        package_dir = packets_root / package_id
        write_json(package_dir / 'work_packet.json', packet)
        write_text(
            package_dir / 'README.md',
            f"# {package_id}\n\n"
            f"This packet describes the package scope, communication rules, and output contract for the round.\n\n"
            f"- baseline refs: {', '.join(packet['baseline_refs'])}\n"
            f"- communication rules: {', '.join(packet['communication_rules'])}\n",
        )
    print(f'[OK] generated work packets in {packets_root}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
