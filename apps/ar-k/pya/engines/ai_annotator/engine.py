from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pya.contracts.annotation_contracts import build_annotation
from pya.contracts.engine_contracts import build_execution_summary
from pya.contracts.enums import Severity, State
from pya.kernel.models import EngineRunResult
from pya.system.state_model import validate_state_producer


@dataclass
class AIAnnotatorEngine:
    manifest: dict[str, Any]
    engine_id: str = "ai_annotator"
    stage: str = "annotate"

    def _confidence(self, module: dict[str, Any], enabled: bool, module_violations: list[dict[str, Any]]) -> float:
        value = 0.55
        if module["status"] == State.CANONICAL.value:
            value += 0.1
        if enabled:
            value += 0.05
        if not module_violations:
            value += 0.1
        if module["status"] != State.CANONICAL.value:
            value -= 0.2
        if any(item["severity"] in {"error", "critical"} for item in module_violations):
            value -= 0.15
        if any(item["severity"] == "warning" for item in module_violations):
            value -= 0.05
        return max(0.2, min(0.89, round(value, 3)))

    def run(self, context) -> EngineRunResult:
        started_at = context.execution_time
        emitted_events = []
        artifacts: list[dict[str, Any]] = []
        module_registry = context.storage.read_registry(self.engine_id, "module_registry", default=[])
        boundary_registry = context.storage.read_registry(self.engine_id, "boundary_registry", default=[])
        validation_report = context.storage.read_registry(self.engine_id, "validation_report", default={"summary": {}, "violations": []})
        switch_resolutions = context.storage.read_registry(self.engine_id, "switch_resolutions", default=[])
        context.event_bus.emit(
            name="ai_annotator.started",
            producer=self.engine_id,
            target=str(context.paths.annotations),
            payload={"module_count": len(module_registry)},
        )
        emitted_events.append("ai_annotator.started")

        boundaries_by_source: dict[str, list[dict[str, Any]]] = {}
        for boundary in boundary_registry:
            boundaries_by_source.setdefault(boundary["source_module_id"], []).append(boundary)
        switch_by_target = {entry["target_id"]: entry for entry in switch_resolutions}
        violations = validation_report.get("violations", [])
        annotations = []
        for module in sorted(module_registry, key=lambda item: item["name"]):
            validate_state_producer(self.engine_id, State.SUGGESTED.value)
            module_violations = [item for item in violations if item["entity_id"] == module["module_id"]]
            related_boundaries = boundaries_by_source.get(module["module_id"], [])
            resolution = switch_by_target.get(module["module_id"])
            enabled = bool(resolution["resolved_value"]) if resolution else True
            ambiguity_note = " Evidence remains ambiguous." if module["status"] != State.CANONICAL.value else ""
            summary = (
                f"Module {module['name']} in area {module['area']} exposes {len(related_boundaries)} boundary links "
                f"and is currently {'enabled' if enabled else 'disabled'}."
            )
            rationale = (
                f"Based on registry state {module['status']}, {len(module_violations)} validator findings, "
                f"and {len(related_boundaries)} observed import boundaries.{ambiguity_note}"
            )
            confidence = self._confidence(module, enabled, module_violations)
            annotations.append(
                build_annotation(
                    target_type="module",
                    target_id=module["module_id"],
                    annotation_kind="module_summary",
                    summary=summary,
                    rationale=rationale,
                    source_basis={
                        "module": module["name"],
                        "switch": resolution["switch_id"] if resolution else None,
                        "validation_status": validation_report.get("summary", {}).get("status"),
                    },
                    confidence=confidence,
                    status=State.SUGGESTED.value,
                    model_info={"model": "rule-based-baseline", "owner": self.engine_id},
                    snapshot_id=context.execution_id,
                    created_at=context.execution_time,
                )
            )
        context.storage.write_registry(self.engine_id, "annotations", annotations)
        artifacts.append(context.storage.write_artifact(self.engine_id, "annotations", "annotations.json", annotations))
        metrics = {
            "annotation_count": len(annotations),
            "average_confidence": round(sum(item["confidence"] for item in annotations) / len(annotations), 3) if annotations else 0.0,
        }
        context.event_bus.emit(
            name="ai_annotator.completed",
            producer=self.engine_id,
            target=str(context.paths.annotations),
            payload=metrics,
            severity=Severity.INFO.value,
        )
        emitted_events.append("ai_annotator.completed")
        summary = build_execution_summary(
            execution_id=context.execution_id,
            engine_id=self.engine_id,
            stage=self.stage,
            status="ok",
            started_at=started_at,
            finished_at=context.execution_time,
            metrics=metrics,
            registries_written=context.storage.written_registries(self.engine_id),
            artifacts=artifacts,
            events=emitted_events,
        )
        return EngineRunResult(execution_summary=summary)
