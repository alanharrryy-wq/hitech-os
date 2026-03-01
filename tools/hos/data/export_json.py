#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.hos._core.stable_json import write_json


def export_simulation_bundle(output_dir: Path, payload: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "simulation_bundle.json"
    write_json(target, payload, indent=2, sort_keys=True)
    return target


def export_series_csv(output_dir: Path, series: list[dict[str, Any]]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "series.csv"
    lines: list[str] = []
    lines.append(
        "at,cpuPercent,memoryMb,throughputPerMin,latencyP50,latencyP95,latencyP99,queuePressure,errorRatio,successRate,activeWorkers"
    )
    for row in series:
        latency = row.get("latencyMs", {})
        lines.append(
            ",".join(
                [
                    str(row.get("at", "")),
                    str(row.get("cpuPercent", "")),
                    str(row.get("memoryMb", "")),
                    str(row.get("throughputPerMin", "")),
                    str(latency.get("p50", "")),
                    str(latency.get("p95", "")),
                    str(latency.get("p99", "")),
                    str(row.get("queuePressure", "")),
                    str(row.get("errorRatio", "")),
                    str(row.get("successRate", "")),
                    str(row.get("activeWorkers", "")),
                ]
            )
        )
    target.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return target

