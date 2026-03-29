#!/usr/bin/env python3
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from tools.hos._core.stable_json import write_json

from .config import SentinelConfig
from .execution_lock import acquire_guardian_lock, release_guardian_lock
from .sentinel import SentinelRunOptions, run_sentinel_cycle
from .utils import now_utc_iso


@dataclass(frozen=True)
class GuardianRunOptions:
    interval_seconds: int = 0
    iterations: int = 0
    apply: bool = False
    apply_cleanup: bool = False
    apply_repair: bool = False
    update_ignore: bool = True
    cleanup: bool = True
    repair: bool = True
    restore_missing_tracked: bool = False
    allow_revert_unsafe: bool = False


def _activity_score(report: dict[str, Any]) -> int:
    summary = report.get("summary", {})
    scan = report.get("scan", {})
    health = report.get("health", {})
    score = 0
    score += int(summary.get("artifactCount", 0))
    score += int(summary.get("securityFindings", 0)) * 40
    score += int(scan.get("untrackedFileCount", 0))
    score += len(report.get("errors", [])) * 120
    score += max(0, 100 - int(health.get("score", 0)))
    return max(0, score)


def _initial_interval(config: SentinelConfig, requested: int) -> int:
    if int(requested) > 0:
        return max(10, int(requested))
    return max(10, int(config.default_guardian_interval_seconds))


def _autotune_interval(config: SentinelConfig, current_interval: int, activity_score: int) -> int:
    if not bool(config.autotune_enabled):
        return current_interval
    min_interval = max(10, int(config.autotune_min_interval_seconds))
    max_interval = max(min_interval, int(config.autotune_max_interval_seconds))
    high_threshold = int(config.autotune_high_activity_threshold)
    low_threshold = int(config.autotune_low_activity_threshold)
    step = max(15, int(round(max(30, current_interval * 0.1))))

    if activity_score >= high_threshold:
        return max(min_interval, current_interval - step)
    if activity_score <= low_threshold:
        return min(max_interval, current_interval + step)
    return current_interval


def run_guardian(config: SentinelConfig, options: GuardianRunOptions) -> dict[str, Any]:
    start_ts = now_utc_iso()
    history: list[dict[str, Any]] = []
    cycle = 0
    interval = _initial_interval(config=config, requested=int(options.interval_seconds))
    max_iterations = int(options.iterations)
    apply_cleanup_mode = bool(options.apply or options.apply_cleanup)
    apply_repair_mode = bool(options.apply or options.apply_repair)
    lock = acquire_guardian_lock(config=config, owner_label="guardian")

    if not lock.acquired:
        payload = {
            "startedAt": start_ts,
            "endedAt": now_utc_iso(),
            "cycles": 0,
            "intervalSeconds": interval,
            "intervalSecondsStart": interval,
            "intervalSecondsFinal": interval,
            "applyMode": options.apply,
            "applyCleanupMode": apply_cleanup_mode,
            "applyRepairMode": apply_repair_mode,
            "autoTuneEnabled": bool(config.autotune_enabled),
            "history": [],
            "lock": {
                "acquired": False,
                "path": lock.lock_path.as_posix(),
                "reason": lock.reason,
                "owner": lock.owner,
            },
            "errors": [f"guardian_lock_blocked: {lock.reason}"],
        }
        summary_path = (config.log_dir / f"guardian_summary_{start_ts.replace(':', '').replace('-', '')}.json").resolve()
        write_json(summary_path, payload, indent=2, sort_keys=True)
        payload["summaryPath"] = summary_path.as_posix()
        return payload

    try:
        while True:
            cycle += 1
            run_options = SentinelRunOptions(
                apply=options.apply,
                apply_cleanup=options.apply_cleanup,
                apply_repair=options.apply_repair,
                update_ignore=options.update_ignore,
                enable_cleanup=options.cleanup,
                enable_repair=options.repair,
                restore_missing_tracked=options.restore_missing_tracked,
                allow_revert_unsafe=options.allow_revert_unsafe,
            )
            report = run_sentinel_cycle(config=config, options=run_options)
            activity = _activity_score(report=report)
            next_interval = _autotune_interval(
                config=config,
                current_interval=interval,
                activity_score=activity,
            )
            history.append(
                {
                    "cycle": cycle,
                    "timestamp": report.get("timestamp"),
                    "healthScore": report.get("health", {}).get("score", 0),
                    "status": report.get("health", {}).get("status", "unknown"),
                    "errors": report.get("errors", []),
                    "applyModes": report.get("applyModes", {}),
                    "activityScore": activity,
                    "intervalSecondsUsed": interval,
                    "nextIntervalSeconds": next_interval,
                    "reportJson": report.get("files", {}).get("reportJson", ""),
                }
            )

            if max_iterations > 0 and cycle >= max_iterations:
                interval = next_interval
                break
            time.sleep(next_interval)
            interval = next_interval
    finally:
        release_guardian_lock(lock=lock)

    payload = {
        "startedAt": start_ts,
        "endedAt": now_utc_iso(),
        "cycles": cycle,
        "intervalSeconds": interval,
        "intervalSecondsStart": _initial_interval(config=config, requested=int(options.interval_seconds)),
        "intervalSecondsFinal": interval,
        "applyMode": options.apply,
        "applyCleanupMode": apply_cleanup_mode,
        "applyRepairMode": apply_repair_mode,
        "autoTuneEnabled": bool(config.autotune_enabled),
        "lock": {
            "acquired": True,
            "path": lock.lock_path.as_posix(),
            "owner": lock.owner,
        },
        "history": history,
    }
    summary_path = (config.log_dir / f"guardian_summary_{start_ts.replace(':', '').replace('-', '')}.json").resolve()
    write_json(summary_path, payload, indent=2, sort_keys=True)
    payload["summaryPath"] = summary_path.as_posix()
    return payload
