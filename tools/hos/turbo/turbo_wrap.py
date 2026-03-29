#!/usr/bin/env python3
from __future__ import annotations

import sys
import argparse
import os
from pathlib import Path
from typing import Sequence

_BOOT = Path(__file__).resolve()
for _parent in (_BOOT.parent, *_BOOT.parents):
    if (_parent / "package.json").exists() and (_parent / "pnpm-workspace.yaml").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from tools.hos._core.exec import run_command
from tools.hos._core.repo_root import find_repo_root
from tools.hos._core.reports import timestamp_slug, write_json_report
from tools.hos.turbo.remote_cache_check import evaluate_remote_cache_env
from tools.hos.turbo.resolve_profile import resolve_profile


def _has_concurrency_flag(args: Sequence[str]) -> bool:
    return any(
        token == "--concurrency"
        or token.startswith("--concurrency=")
        or token.startswith("-c=")
        for token in args
    )


def _build_turbo_args(base_args: list[str], concurrency: int | str) -> list[str]:
    args = list(base_args)
    if not _has_concurrency_flag(args) and concurrency != "auto":
        args.append(f"--concurrency={concurrency}")
    return args


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Optional Turbo wrapper with deterministic profile defaults. "
            "No existing scripts are modified automatically."
        )
    )
    parser.add_argument("--profile", help="Profile name: stable|balanced|aggressive.")
    parser.add_argument("--ci", action="store_true", help="Enable CI mode (requires remote cache env vars).")
    parser.add_argument("--dry-run", action="store_true", help="Print command without executing.")
    parser.add_argument("--timeout", type=float, default=0.0, help="Timeout in seconds. 0 disables timeout.")
    parser.add_argument(
        "--report",
        action="store_true",
        help="Write run report JSON into tools/_local/reports/turbo.",
    )
    parser.add_argument(
        "turbo_args",
        nargs=argparse.REMAINDER,
        help="Arguments passed to turbo, example: -- run build --filter=@hitech/keystone",
    )
    return parser.parse_args()


def _normalize_turbo_args(raw: Sequence[str]) -> list[str]:
    if not raw:
        return ["run", "build"]
    if raw[0] == "--":
        return list(raw[1:])
    return list(raw)


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root()
    resolution = resolve_profile(repo_root=repo_root, requested=args.profile)
    turbo_args = _normalize_turbo_args(args.turbo_args)
    turbo_args = _build_turbo_args(turbo_args, concurrency=resolution.concurrency)

    remote_cache = evaluate_remote_cache_env()
    if args.ci and not remote_cache.ok:
        print("[turbo_wrap] FAIL CI mode requires TURBO_TOKEN and TURBO_TEAM env names.")
        for missing in remote_cache.required_missing:
            print(f" - missing: {missing}")
        return 2
    if not args.ci and not remote_cache.ok:
        print("[turbo_wrap] WARN remote cache env vars not fully present (local mode continues).")

    command = ["turbo", *turbo_args]
    print(
        f"[turbo_wrap] profile={resolution.profile} concurrency={resolution.concurrency} "
        f"source={resolution.source} command={' '.join(command)}"
    )

    if args.dry_run:
        return 0

    timeout = args.timeout if args.timeout > 0 else None
    result = run_command(command, cwd=repo_root, timeout_seconds=timeout, env=os.environ, check=False)
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n")

    if args.report:
        payload = {
            "ok": result.ok,
            "argv": list(result.argv),
            "cwd": result.cwd,
            "returnCode": result.returncode,
            "classification": result.classification,
            "elapsedMs": result.elapsed_ms,
            "profile": resolution.profile,
            "concurrency": resolution.concurrency,
            "source": resolution.source,
            "ciMode": args.ci,
            "remoteCache": {
                "ok": remote_cache.ok,
                "requiredPresent": list(remote_cache.required_present),
                "requiredMissing": list(remote_cache.required_missing),
                "optionalPresent": list(remote_cache.optional_present),
                "optionalMissing": list(remote_cache.optional_missing),
            },
        }
        report_name = f"turbo_wrap_{timestamp_slug()}.json"
        report_path = write_json_report(
            repo_root=repo_root,
            file_name=report_name,
            payload=payload,
            local=True,
            subdir="turbo",
        )
        print(f"[turbo_wrap] report={report_path.as_posix()}")

    return 0 if result.ok else result.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main())
