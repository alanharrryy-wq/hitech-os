#!/usr/bin/env python3
from __future__ import annotations

import sys
import argparse
import datetime as dt
from pathlib import Path
from typing import Any

_BOOT = Path(__file__).resolve()
for _parent in (_BOOT.parent, *_BOOT.parents):
    if (_parent / "package.json").exists() and (_parent / "pnpm-workspace.yaml").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from tools.hos._core.repo_root import find_repo_root
from tools.hos._core.reports import timestamp_slug
from tools.hos._core.stable_json import dump_json
from tools.hos.data.export_api_mock import export_api_mock
from tools.hos.data.export_json import export_series_csv, export_simulation_bundle
from tools.hos.data.keystone_shapes import to_endpoint_payloads
from tools.hos.data.scenarios import SCENARIOS
from tools.hos.data.simulator_core import ScenarioDefinition, SimulationConfig, generate_simulation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic Keystone-oriented data simulator.")
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), default="normal", help="Scenario name.")
    parser.add_argument("--seed", type=int, default=1337, help="Deterministic seed.")
    parser.add_argument("--run-count", type=int, default=0, help="Override run count.")
    parser.add_argument("--duration-minutes", type=int, default=0, help="Override duration in minutes.")
    parser.add_argument(
        "--output-dir",
        default="",
        help="Output directory (default: tools/_local/data_sims/<timestamp>/<scenario>_seed<seed>).",
    )
    parser.add_argument("--export-api-mock", action="store_true", help="Emit mock endpoint JSON payloads.")
    parser.add_argument("--json", action="store_true", help="Print summary JSON payload.")
    return parser.parse_args()


def scenario_with_overrides(base: ScenarioDefinition, run_count: int, duration_minutes: int) -> ScenarioDefinition:
    return ScenarioDefinition(
        name=base.name,
        description=base.description,
        run_count=run_count if run_count > 0 else base.run_count,
        duration_minutes=duration_minutes if duration_minutes > 0 else base.duration_minutes,
        baseline_cpu=base.baseline_cpu,
        baseline_memory_mb=base.baseline_memory_mb,
        baseline_throughput=base.baseline_throughput,
        baseline_latency_ms=base.baseline_latency_ms,
        error_ratio=base.error_ratio,
        critical_event_ratio=base.critical_event_ratio,
        burst_chance=base.burst_chance,
        burst_scale=base.burst_scale,
        queue_pressure_base=base.queue_pressure_base,
        recovery_bias=base.recovery_bias,
    )


def resolve_output_dir(repo_root: Path, requested: str, scenario: str, seed: int) -> Path:
    if requested:
        path = Path(requested)
        if not path.is_absolute():
            path = (repo_root / path).resolve()
        return path
    slug = timestamp_slug()
    return (repo_root / "tools/_local/data_sims" / slug / f"{scenario}_seed{seed}").resolve()


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root()
    scenario = scenario_with_overrides(SCENARIOS[args.scenario], args.run_count, args.duration_minutes)
    start_at = dt.datetime.now(dt.timezone.utc).replace(second=0, microsecond=0)

    config = SimulationConfig(scenario=scenario, seed=args.seed, start_at=start_at)
    bundle = generate_simulation(config)
    payload = {
        "metadata": bundle.metadata,
        "series": bundle.series,
        "runs": bundle.runs,
        "activity": bundle.activity,
        "widgets": bundle.widgets,
        "layout": bundle.layout,
    }

    out_dir = resolve_output_dir(
        repo_root=repo_root,
        requested=args.output_dir,
        scenario=scenario.name,
        seed=args.seed,
    )
    bundle_path = export_simulation_bundle(output_dir=out_dir, payload=payload)
    csv_path = export_series_csv(output_dir=out_dir, series=bundle.series)
    api_files: list[Path] = []
    if args.export_api_mock:
        api_payloads = to_endpoint_payloads(bundle=bundle, seed=args.seed)
        api_files = export_api_mock(output_dir=out_dir, payloads=api_payloads)

    summary: dict[str, Any] = {
        "scenario": scenario.name,
        "seed": args.seed,
        "runCount": len(bundle.runs),
        "activityCount": len(bundle.activity),
        "widgetCount": len(bundle.widgets),
        "seriesCount": len(bundle.series),
        "determinismHash": bundle.metadata.get("determinismHash"),
        "outputDir": out_dir.as_posix(),
        "bundleFile": bundle_path.as_posix(),
        "seriesCsv": csv_path.as_posix(),
        "apiMockFiles": [item.as_posix() for item in api_files],
    }

    if args.json:
        print(dump_json(summary), end="")
    else:
        print(
            f"[cli_simulate] scenario={scenario.name} seed={args.seed} runs={len(bundle.runs)} "
            f"activity={len(bundle.activity)} widgets={len(bundle.widgets)}"
        )
        print(f"[cli_simulate] output={out_dir.as_posix()}")
        print(f"[cli_simulate] determinismHash={bundle.metadata.get('determinismHash')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
