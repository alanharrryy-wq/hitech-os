#!/usr/bin/env python3
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.hos._core.stable_json import write_json

from .config import SentinelConfig
from .sentinel import SentinelRunOptions, run_sentinel_cycle
from .utils import now_utc_iso


@dataclass(frozen=True)
class GuardianRunOptions:
    interval_seconds: int = 300
    iterations: int = 0
    apply: bool = False
    update_ignore: bool = True
    cleanup: bool = True
    repair: bool = True
    restore_missing_tracked: bool = False
    allow_revert_unsafe: bool = False


def run_guardian(config: SentinelConfig, options: GuardianRunOptions) -> dict[str, Any]:
    start_ts = now_utc_iso()
    history: list[dict[str, Any]] = []
    cycle = 0
    interval = max(10, int(options.interval_seconds))
    max_iterations = int(options.iterations)

    while True:
        cycle += 1
        run_options = SentinelRunOptions(
            apply=options.apply,
            update_ignore=options.update_ignore,
            enable_cleanup=options.cleanup,
            enable_repair=options.repair,
            restore_missing_tracked=options.restore_missing_tracked,
            allow_revert_unsafe=options.allow_revert_unsafe,
        )
        report = run_sentinel_cycle(config=config, options=run_options)
        history.append(
            {
                "cycle": cycle,
                "timestamp": report.get("timestamp"),
                "healthScore": report.get("health", {}).get("score", 0),
                "status": report.get("health", {}).get("status", "unknown"),
                "errors": report.get("errors", []),
                "reportJson": report.get("files", {}).get("reportJson", ""),
            }
        )

        if max_iterations > 0 and cycle >= max_iterations:
            break
        time.sleep(interval)

    payload = {
        "startedAt": start_ts,
        "endedAt": now_utc_iso(),
        "cycles": cycle,
        "intervalSeconds": interval,
        "applyMode": options.apply,
        "history": history,
    }
    summary_path = (config.log_dir / f"guardian_summary_{start_ts.replace(':', '').replace('-', '')}.json").resolve()
    write_json(summary_path, payload, indent=2, sort_keys=True)
    payload["summaryPath"] = summary_path.as_posix()
    return payload

