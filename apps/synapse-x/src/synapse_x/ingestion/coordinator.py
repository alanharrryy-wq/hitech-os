from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from synapse_x.engine import SynapseEngine
from synapse_x.services.ingest_service import IngestRequest, run_ingest
from synapse_x.services.repair_service import run_repair


@dataclass(slots=True)
class IngestionCoordinator:
    engine: SynapseEngine

    def ingest_now(self, paths: list[str | Path] | None = None) -> dict:
        request = IngestRequest(paths=tuple(paths or ()), full=False)
        return run_ingest(self.engine, request)

    def full_ingest(self, paths: list[str | Path] | None = None) -> dict:
        request = IngestRequest(paths=tuple(paths or ()), full=True)
        return run_ingest(self.engine, request)

    def repair(self) -> dict:
        return run_repair(self.engine)
