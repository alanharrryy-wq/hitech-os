#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from capatch_runtime.workspace_cleaner import load_workspace_cleaner_policy, run_shutdown_cleaner, run_startup_cleaner



def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Run CAPATCH workspace cleaner manually.')
    parser.add_argument('--phase', default='both', choices=['startup', 'shutdown', 'both'])
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    policy = load_workspace_cleaner_policy(ROOT)
    payload: dict[str, object] = {}
    if args.phase in {'startup', 'both'}:
        payload['startup'] = run_startup_cleaner(ROOT, policy=policy, dry_run=bool(args.dry_run))
    if args.phase in {'shutdown', 'both'}:
        payload['shutdown'] = run_shutdown_cleaner(ROOT, policy=policy, dry_run=bool(args.dry_run), run_summary={'invoked_via': 'tooling/run_workspace_cleaner.py'})
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
