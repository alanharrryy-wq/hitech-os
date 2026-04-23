from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from synapse_x.ingestion.coordinator import IngestionCoordinator


def watch_loop(
    coordinator: IngestionCoordinator,
    *,
    paths: list[str | Path] | None = None,
    interval_seconds: int = 30,
    max_cycles: int | None = None,
    stop_file: str | Path | None = None,
) -> dict[str, Any]:
    stop_path = Path(stop_file).resolve() if stop_file else None
    cycles = 0
    last_result: dict[str, Any] | None = None
    failures = 0

    while max_cycles is None or cycles < max_cycles:
        if stop_path and stop_path.exists():
            stop_path.unlink(missing_ok=True)
            break
        cycles += 1
        try:
            last_result = coordinator.ingest_now(paths=paths)
        except Exception:  # noqa: BLE001
            failures += 1
            last_result = {"status": "failed", "error": "watch-ingest-exception"}
        if max_cycles is not None and cycles >= max_cycles:
            break
        time.sleep(max(0, interval_seconds))

    return {
        "status": "ok" if failures == 0 else "partial",
        "cycles": cycles,
        "failures": failures,
        "last_result": last_result or {},
    }
