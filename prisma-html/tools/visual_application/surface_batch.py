from __future__ import annotations

import argparse
import json
from collections import Counter
from typing import Any

from .target_index import (
    CENSUS_KIND,
    DISCOVERY_ONLY,
    ENFORCED,
    EXACT_KIND,
    SURFACES,
    build_index,
)


def plan_surface(surface: str, *, index: dict[str, Any] | None = None, wave_size: int = 50) -> dict[str, Any]:
    if surface not in SURFACES:
        raise ValueError(f"unknown surface: {surface}")
    if wave_size < 1 or wave_size > 500:
        raise ValueError("wave_size must be between 1 and 500")

    index = index or build_index()
    if index.get("globalBlockers"):
        return {
            "schema": "prisma.visual.application.surface-batch-plan.v1",
            "surface": surface,
            "status": "BLOCKED_GLOBAL_AUTHORITY",
            "globalBlockers": index.get("globalBlockers"),
            "ready": False,
            "waves": [],
        }

    rows = [row for row in index.get("records", []) if row.get("surface") == surface]
    exact = [
        row for row in rows
        if row.get("recordKind") == EXACT_KIND and row.get("enforcement") == ENFORCED
    ]
    census = [
        row for row in rows
        if row.get("recordKind") == CENSUS_KIND or row.get("enforcement") == DISCOVERY_ONLY
    ]
    ready_exact = [row for row in exact if row.get("status") == "APPLY_READY"]
    blocked_exact = [row for row in exact if row.get("status") != "APPLY_READY"]

    blocker_counts: Counter[str] = Counter()
    for row in blocked_exact + census:
        blocker_counts.update(str(value) for value in row.get("blockers", []))

    ready = bool(rows) and bool(exact) and not census and not blocked_exact
    waves = [
        [row["targetId"] for row in ready_exact[offset:offset + wave_size]]
        for offset in range(0, len(ready_exact), wave_size)
    ] if ready else []

    return {
        "schema": "prisma.visual.application.surface-batch-plan.v1",
        "surface": surface,
        "status": "SURFACE_BATCH_READY" if ready else "BLOCKED_SURFACE_BATCH",
        "ready": ready,
        "recordCount": len(rows),
        "exactTargetCount": len(exact),
        "applyReadyExactCount": len(ready_exact),
        "blockedExactCount": len(blocked_exact),
        "discoveryOnlyCount": len(census),
        "blockerCounts": dict(sorted(blocker_counts.items())),
        "waveSize": wave_size,
        "waveCount": len(waves),
        "waves": waves,
        "hardTruth": (
            "Surface batch never weakens exact-target authority. Any discovery-only or blocked exact "
            "target keeps the entire surface batch fail-closed."
        ),
        "runtimeVisualGreen": False,
        "productionCertified": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GVAE read-only whole-surface batch readiness planner")
    parser.add_argument("--surface", required=True, choices=SURFACES)
    parser.add_argument("--wave-size", type=int, default=50)
    args = parser.parse_args(argv)
    try:
        plan = plan_surface(args.surface, wave_size=args.wave_size)
    except ValueError as exc:
        print(json.dumps({"status": "BLOCKED_SURFACE_BATCH", "errors": [str(exc)]}, indent=2))
        return 2
    print(json.dumps(plan, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if plan["ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
