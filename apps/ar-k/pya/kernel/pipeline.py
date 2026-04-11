from __future__ import annotations

from pathlib import Path
from typing import Any

from pya.contracts.engine_contracts import validate_execution_summary
from pya.kernel.barriers import BARRIER_REQUIREMENTS
from pya.kernel.engine_loader import discover_and_load_engines
from pya.kernel.reporter import write_execution_report


class PipelineCoordinator:
    def __init__(self, context: "RuntimeContext"):
        self.context = context
        self.engines = discover_and_load_engines(context.paths.root, context.root_manifest)

    def _check_barrier(self, stage: str) -> None:
        for registry_name in BARRIER_REQUIREMENTS.get(stage, []):
            path = self.context.paths.registries / f"{registry_name}.json"
            if registry_name == "query_index":
                path = self.context.paths.indices / f"{registry_name}.json"
            if not path.exists():
                raise RuntimeError(f"Barrier failed for stage {stage}: missing {registry_name}")

    def run(self) -> dict[str, Any]:
        summaries: list[dict[str, Any]] = []
        for engine in self.engines:
            self._check_barrier(engine.stage)
            result = engine.run(self.context)
            validate_execution_summary(result.execution_summary)
            summaries.append(result.execution_summary)
        events_file = self.context.event_bus.flush()
        report = {
            "execution_id": self.context.execution_id,
            "execution_time": self.context.execution_time,
            "engine_order": [engine.engine_id for engine in self.engines],
            "summaries": summaries,
            "events_file": str(events_file),
        }
        write_execution_report(self.context.paths.reports / "execution_summary.json", report)
        return report
