
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from lib.common import discover_repo_root, stable_json_dumps
from lib.projects import initialize_project_baseline


def main() -> int:
    parser = argparse.ArgumentParser(description='Initialize a homologated project baseline skeleton.')
    parser.add_argument('--project-id', required=True)
    parser.add_argument('--project-name', required=True)
    parser.add_argument('--initiative-type', required=True)
    parser.add_argument('--objective', required=True)
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    result = initialize_project_baseline(args.project_id, args.project_name, args.initiative_type, args.objective, repo_root, force=args.force)
    print(stable_json_dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
