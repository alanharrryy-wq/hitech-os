from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pya.contracts.engine_contracts import build_execution_summary
from pya.contracts.enums import Severity, State
from pya.contracts.switch_contracts import build_switch_resolution
from pya.kernel.models import EngineRunResult
from pya.system.state_model import validate_state_producer


def resolve_switch_entries(entries: list[dict[str, Any]], overrides: dict[str, Any], timestamp: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    resolutions: list[dict[str, Any]] = []
    trace: list[dict[str, Any]] = []
    warnings: list[str] = []
    for entry in sorted(entries, key=lambda item: item["switch_id"]):
        resolved_value = entry["default_value"]
        decision_source = "default"
        precedence_path = ["default"]
        justification = "Resolved from switch default value."
        override_used = None

        if entry["switch_id"] in overrides:
            override_used = overrides[entry["switch_id"]]
            precedence_path.append("switch_id")
            decision_source = "switch_id"
        elif entry["target_id"] in overrides:
            override_used = overrides[entry["target_id"]]
            precedence_path.append("target_id")
            decision_source = "target_id"

        if override_used is not None:
            if isinstance(override_used, bool):
                resolved_value = override_used
                justification = f"Resolved from {decision_source} override."
            else:
                warnings.append(f"Invalid override for {entry['switch_id']}: expected bool, got {type(override_used).__name__}")
                decision_source = "default"
                precedence_path = ["default", "invalid_override_ignored"]
                justification = "Invalid override ignored; default retained."

        validate_state_producer("switch_engine", State.EFFECTIVE.value)
        resolution = build_switch_resolution(
            switch_id=entry["switch_id"],
            target_type=entry["target_type"],
            target_id=entry["target_id"],
            evaluated_context={"overrides": overrides},
            default_value=entry["default_value"],
            resolved_value=resolved_value,
            decision_source=decision_source,
            precedence_path=precedence_path,
            justification=justification,
            timestamp=timestamp,
            state=State.EFFECTIVE.value,
        )
        resolutions.append(resolution)
        trace.append(
            {
                "switch_id": entry["switch_id"],
                "decision_source": decision_source,
                "resolved_value": resolved_value,
                "precedence_path": precedence_path,
            }
        )
    return resolutions, trace, warnings


@dataclass
class SwitchEngine:
    manifest: dict[str, Any]
    engine_id: str = "switch_engine"
    stage: str = "switch"

    def run(self, context) -> EngineRunResult:
        started_at = context.execution_time
        emitted_events = []
        artifacts: list[dict[str, Any]] = []
        entries = context.storage.read_registry(self.engine_id, "switch_registry", default=[])
        context.event_bus.emit(
            name="switch_engine.started",
            producer=self.engine_id,
            target=str(context.paths.registries),
            payload={"switch_count": len(entries)},
        )
        emitted_events.append("switch_engine.started")
        resolutions, trace, warnings = resolve_switch_entries(entries, context.config.switch_overrides, context.execution_time)
        context.storage.write_registry(self.engine_id, "switch_resolutions", resolutions)
        artifacts.append(context.storage.write_artifact(self.engine_id, "decision_trace", "switch_decision_trace.json", trace))
        metrics = {
            "switch_count": len(entries),
            "resolved_count": len(resolutions),
            "warning_count": len(warnings),
        }
        if warnings:
            for warning in warnings:
                context.event_bus.emit(
                    name="switch_engine.override_warning",
                    producer=self.engine_id,
                    target="switch_registry",
                    payload={"warning": warning},
                    severity=Severity.WARNING.value,
                )
                emitted_events.append("switch_engine.override_warning")
        context.event_bus.emit(
            name="switch_engine.completed",
            producer=self.engine_id,
            target=str(context.paths.registries),
            payload=metrics,
        )
        emitted_events.append("switch_engine.completed")
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
