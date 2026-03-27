from __future__ import annotations

from pathlib import Path
from typing import Any

from ..sentinel_observability.failure_snapshot import capture_failure
from ..sentinel_observability.run_metrics import RunMetrics
from ..sentinel_observability.structured_logger import log_event
from .runtime import get_runtime_paths

def emit_event(event: str, **fields: Any) -> dict[str, Any]:
    paths = get_runtime_paths()
    return log_event(paths.logs_root / "events.jsonl", event, **fields)

def create_run_metrics(run_id: str) -> RunMetrics:
    return RunMetrics(run_id=run_id)

def persist_metrics(metrics: RunMetrics) -> Path:
    paths = get_runtime_paths()
    return metrics.write(paths.logs_root / f"metrics_{metrics.run_id}.json")

def snapshot_failure(exc: BaseException, **context: Any) -> Path:
    paths = get_runtime_paths()
    return capture_failure(paths.logs_root, exc, context=context)
