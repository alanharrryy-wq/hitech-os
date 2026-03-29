
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from lib.common import discover_repo_root, stable_json_dumps, write_json
from lib.readiness import build_readiness_report


def main() -> int:
    parser = argparse.ArgumentParser(description='Check framework, project, run, and round readiness gates.')
    parser.add_argument('--project-id')
    parser.add_argument('--run-id')
    parser.add_argument('--round-id')
    parser.add_argument('--output')
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    report = build_readiness_report(repo_root, project_id=args.project_id, run_id=args.run_id, round_id=args.round_id)
    if args.output:
        write_json(Path(args.output), report)
    print(stable_json_dumps(report))
    return 0 if report['overall_status'] != 'not_ready' else 1


if __name__ == '__main__':
    raise SystemExit(main())
