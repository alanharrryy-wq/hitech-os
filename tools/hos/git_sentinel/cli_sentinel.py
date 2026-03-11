#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_BOOT = Path(__file__).resolve()
for _parent in (_BOOT.parent, *_BOOT.parents):
    if (_parent / "package.json").exists() and (_parent / "pnpm-workspace.yaml").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        continue

from tools.hos._core.stable_json import dump_json  # noqa: E402
from tools.hos.git_sentinel.config import build_config  # noqa: E402
from tools.hos.git_sentinel.scheduler import GuardianRunOptions, run_guardian  # noqa: E402
from tools.hos.git_sentinel.sentinel import SentinelRunOptions, run_sentinel_cycle  # noqa: E402


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo-root", default=None, help="Absolute or relative repository root.")
    parser.add_argument("--config", default=None, help="Optional JSON config override path.")
    parser.add_argument(
        "--profile",
        default=None,
        choices=("safe", "strict", "aggressive"),
        help="Optional sentinel profile override.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Git Sentinel autonomous repository hygiene system.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan-only mode (no mutations).")
    _add_common_args(scan_parser)

    once_parser = subparsers.add_parser("once", help="Run one sentinel cycle.")
    _add_common_args(once_parser)
    once_parser.add_argument("--apply", action="store_true", help="Apply cleanup/repair/ignore updates.")
    once_parser.add_argument("--apply-cleanup", action="store_true", help="Apply cleanup actions only.")
    once_parser.add_argument("--apply-repair", action="store_true", help="Apply repair actions only.")
    once_parser.add_argument("--no-ignore-update", action="store_true", help="Disable ignore update.")
    once_parser.add_argument("--no-cleanup", action="store_true", help="Disable cleanup engine.")
    once_parser.add_argument("--no-repair", action="store_true", help="Disable repair engine.")
    once_parser.add_argument(
        "--restore-missing-tracked",
        action="store_true",
        help="Allow restoring deleted tracked files during repair.",
    )
    once_parser.add_argument(
        "--allow-revert-unsafe",
        action="store_true",
        help="Allow reverting tracked files flagged by high-severity security findings.",
    )

    guardian_parser = subparsers.add_parser("guardian", help="Continuous guardian mode.")
    _add_common_args(guardian_parser)
    guardian_parser.add_argument("--apply", action="store_true", help="Apply automatic maintenance actions.")
    guardian_parser.add_argument("--apply-cleanup", action="store_true", help="Apply cleanup actions only.")
    guardian_parser.add_argument("--apply-repair", action="store_true", help="Apply repair actions only.")
    guardian_parser.add_argument(
        "--interval-sec",
        type=int,
        default=0,
        help="Cycle interval in seconds (0 uses profile/default interval).",
    )
    guardian_parser.add_argument(
        "--iterations",
        type=int,
        default=0,
        help="Number of cycles to run. 0 means infinite.",
    )
    guardian_parser.add_argument("--no-ignore-update", action="store_true", help="Disable ignore update.")
    guardian_parser.add_argument("--no-cleanup", action="store_true", help="Disable cleanup engine.")
    guardian_parser.add_argument("--no-repair", action="store_true", help="Disable repair engine.")
    guardian_parser.add_argument(
        "--restore-missing-tracked",
        action="store_true",
        help="Allow restoring deleted tracked files during repair.",
    )
    guardian_parser.add_argument(
        "--allow-revert-unsafe",
        action="store_true",
        help="Allow reverting tracked files flagged by high-severity security findings.",
    )

    return parser.parse_args()


def _print_payload(payload: dict, json_output: bool) -> None:
    if json_output:
        print(dump_json(payload), end="")
        return
    if "health" in payload:
        print(
            f"[git-sentinel] health={payload.get('health', {}).get('score', 0)} "
            f"status={payload.get('health', {}).get('status', 'unknown')} "
            f"errors={len(payload.get('errors', []))}"
        )
        print(f"[git-sentinel] report={payload.get('files', {}).get('reportJson', '')}")
        print(f"[git-sentinel] dashboard={payload.get('files', {}).get('dashboardJson', '')}")
        return
    print(
        f"[git-sentinel] guardian cycles={payload.get('cycles', 0)} "
        f"apply={payload.get('applyMode', False)} "
        f"apply_cleanup={payload.get('applyCleanupMode', False)} "
        f"apply_repair={payload.get('applyRepairMode', False)}"
    )
    print(
        f"[git-sentinel] interval_start={payload.get('intervalSecondsStart', 0)} "
        f"interval_final={payload.get('intervalSecondsFinal', 0)} "
        f"autotune={payload.get('autoTuneEnabled', False)}"
    )
    lock = payload.get("lock", {})
    if isinstance(lock, dict) and lock:
        print(
            f"[git-sentinel] lock_acquired={lock.get('acquired', False)} "
            f"lock_path={lock.get('path', '')}"
        )
    print(f"[git-sentinel] summary={payload.get('summaryPath', '')}")


def main() -> int:
    args = parse_args()
    try:
        config = build_config(repo_root=args.repo_root, config_path=args.config, profile=args.profile)
    except FileNotFoundError as exc:
        print(f"[git-sentinel] stop_condition_triggered: {exc}")
        return 3

    if args.command == "scan":
        report = run_sentinel_cycle(
            config=config,
            options=SentinelRunOptions(
                apply=False,
                update_ignore=False,
                enable_cleanup=False,
                enable_repair=False,
                scan_only=True,
            ),
        )
        _print_payload(report, json_output=args.json)
        return 0

    if args.command == "once":
        report = run_sentinel_cycle(
            config=config,
            options=SentinelRunOptions(
                apply=args.apply,
                apply_cleanup=args.apply_cleanup,
                apply_repair=args.apply_repair,
                update_ignore=not args.no_ignore_update,
                enable_cleanup=not args.no_cleanup,
                enable_repair=not args.no_repair,
                restore_missing_tracked=args.restore_missing_tracked,
                allow_revert_unsafe=args.allow_revert_unsafe,
            ),
        )
        _print_payload(report, json_output=args.json)
        stop_error = any(
            str(item).startswith("stop_condition_triggered")
            for item in report.get("errors", [])
        )
        return 2 if stop_error else 0

    guardian_payload = run_guardian(
        config=config,
        options=GuardianRunOptions(
            interval_seconds=args.interval_sec,
            iterations=args.iterations,
            apply=args.apply,
            apply_cleanup=args.apply_cleanup,
            apply_repair=args.apply_repair,
            update_ignore=not args.no_ignore_update,
            cleanup=not args.no_cleanup,
            repair=not args.no_repair,
            restore_missing_tracked=args.restore_missing_tracked,
            allow_revert_unsafe=args.allow_revert_unsafe,
        ),
    )
    _print_payload(guardian_payload, json_output=args.json)
    lock_info = guardian_payload.get("lock", {})
    if isinstance(lock_info, dict) and not bool(lock_info.get("acquired", True)):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
