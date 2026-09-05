from __future__ import annotations

import argparse
import json
from pathlib import Path

from .control_plane import (
    ControlPlaneError,
    build_current_truth,
    build_surface_readiness,
    composer_plan,
    load_atlasfin_indexes,
    load_json,
    load_jsonl,
    ndc_prefixes_from_registry,
    validate_disjoint_write_ownership,
    validate_shard,
)


def _rows(paths: list[str]) -> list[dict]:
    return [row for path in paths for row in load_jsonl(Path(path))]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PRISMA Visual Promotion Control Plane, candidate-only and fail-closed")
    sub = parser.add_subparsers(dest="command", required=True)

    shard = sub.add_parser("validate-shard")
    shard.add_argument("--manifest", required=True)
    shard.add_argument("--candidates", action="append", default=[])
    shard.add_argument("--unresolved", action="append", default=[])
    shard.add_argument("--conflicts", action="append", default=[])
    shard.add_argument("--expected-head")
    shard.add_argument("--repo-root")
    shard.add_argument("--changed-path", action="append", default=[])
    shard.add_argument("--atlasfin-registry", action="append", default=[])
    shard.add_argument("--ndc-prefix-registry")

    plan = sub.add_parser("plan")
    plan.add_argument("--outcomes", action="append", required=True)
    plan.add_argument("--revalidated-equivalent-base", action="store_true")

    truth = sub.add_parser("current-truth")
    truth.add_argument("--target-index", required=True)
    truth.add_argument("--outcomes", action="append", default=[])

    sub.add_parser("validate-write-ownership")
    args = parser.parse_args(argv)

    try:
        if args.command == "validate-shard":
            atlasfin = load_atlasfin_indexes([Path(x) for x in args.atlasfin_registry]) if args.atlasfin_registry else None
            prefixes = ndc_prefixes_from_registry(load_json(Path(args.ndc_prefix_registry))) if args.ndc_prefix_registry else None
            result = validate_shard(
                load_json(Path(args.manifest)),
                _rows([*args.candidates, *args.unresolved, *args.conflicts]),
                expected_head=args.expected_head,
                repo_root=Path(args.repo_root) if args.repo_root else None,
                atlasfin=atlasfin,
                ndc_prefixes=prefixes,
                changed_paths=args.changed_path,
            )
        elif args.command == "plan":
            result = composer_plan(_rows(args.outcomes), revalidated_equivalent_base=args.revalidated_equivalent_base)
        elif args.command == "current-truth":
            current = build_current_truth(load_json(Path(args.target_index)), _rows(args.outcomes))
            result = {"currentTruth": current, "surfaceReadiness": build_surface_readiness(current)}
        else:
            result = validate_disjoint_write_ownership()
    except (ControlPlaneError, OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED_VISUAL_PROMOTION_CONTROL_PLANE", "errors": [f"{type(exc).__name__}:{exc}"]}, indent=2, sort_keys=True))
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
