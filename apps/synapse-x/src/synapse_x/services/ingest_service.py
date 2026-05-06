from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from synapse_x.engine import SynapseEngine


@dataclass(slots=True)
class IngestRequest:
    paths: tuple[str | Path, ...] = ()
    full: bool = False


def run_ingest(engine: SynapseEngine, request: IngestRequest | None = None) -> dict:
    payload = request or IngestRequest()
    selected_paths = [str(path) for path in payload.paths] or None
    return engine.ingest(paths=selected_paths, full=payload.full)
