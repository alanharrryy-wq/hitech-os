#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from capatch_audit import (
    compare_baseline,
    list_baselines,
    promote_checkpoint_to_baseline,
    promote_run_to_baseline,
    restore_baseline,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage official baselines.")
    parser.add_argument("--root-dir", default=str(ROOT))
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list")
    compare = sub.add_parser("compare")
    compare.add_argument("baseline_id")

    restore = sub.add_parser("restore")
    restore.add_argument("baseline_id")

    from_run = sub.add_parser("promote-run")
    from_run.add_argument("run_id")
    from_run.add_argument("label")
    from_run.add_argument("--notes", default="")
    from_run.add_argument("--blessed-by", default=None)

    from_checkpoint = sub.add_parser("promote-checkpoint")
    from_checkpoint.add_argument("checkpoint_id")
    from_checkpoint.add_argument("label")
    from_checkpoint.add_argument("--source-run-id", default=None)
    from_checkpoint.add_argument("--notes", default="")
    from_checkpoint.add_argument("--blessed-by", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root_dir = Path(args.root_dir).resolve()
    if args.command == "list":
        payload = list_baselines(root_dir)
    elif args.command == "compare":
        payload = compare_baseline(root_dir, args.baseline_id)
    elif args.command == "restore":
        payload = restore_baseline(root_dir, args.baseline_id)
    elif args.command == "promote-run":
        payload = promote_run_to_baseline(
            root_dir,
            run_id=args.run_id,
            label=args.label,
            notes=args.notes,
            blessed_by=args.blessed_by,
        )
        payload = payload.__dict__
    elif args.command == "promote-checkpoint":
        payload = promote_checkpoint_to_baseline(
            root_dir,
            checkpoint_id=args.checkpoint_id,
            label=args.label,
            source_run_id=args.source_run_id,
            notes=args.notes,
            blessed_by=args.blessed_by,
        )
        payload = payload.__dict__
    else:
        raise SystemExit(2)
    print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
