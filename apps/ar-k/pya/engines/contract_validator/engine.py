from __future__ import annotations

import importlib.util

from collections import Counter
from dataclasses import dataclass
from typing import Any, Callable

from pya.contracts.contract_registry import CONTRACT_VALIDATORS
from pya.contracts.engine_contracts import build_execution_summary
from pya.contracts.enums import Severity
from pya.contracts.validation_contracts import build_contract_health_summary, build_validation_violation
from pya.kernel.models import EngineRunResult


def _safe_validate(contract_name: str, payload: dict[str, Any], entity_type: str, entity_id: str, location: str, snapshot_id: str) -> list[dict[str, Any]]:
    violations = []
    try:
        CONTRACT_VALIDATORS[contract_name](payload)
    except Exception as exc:
        violations.append(
            build_validation_violation(
                rule_id=f"schema:{contract_name}",
                severity=Severity.ERROR.value,
                entity_type=entity_type,
                entity_id=entity_id,
                location=location,
                message=str(exc),
                expected=contract_name,
                observed=payload,
                autofixable=False,
                snapshot_id=snapshot_id,
            )
        )
    return violations


@dataclass
class ContractValidatorEngine:
    manifest: dict[str, Any]
    engine_id: str = "contract_validator"
    stage: str = "validate"

    def run(self, context) -> EngineRunResult:
        started_at = context.execution_time
        emitted_events = []
        artifacts: list[dict[str, Any]] = []
        module_registry = context.storage.read_registry(self.engine_id, "module_registry", default=[])
        boundary_registry = context.storage.read_registry(self.engine_id, "boundary_registry", default=[])
        contract_registry = context.storage.read_registry(self.engine_id, "contract_registry", default=[])
        switch_registry = context.storage.read_registry(self.engine_id, "switch_registry", default=[])
        switch_resolutions = context.storage.read_registry(self.engine_id, "switch_resolutions", default=[])
        query_index = context.storage.read_index(self.engine_id, "query_index", default=[])

        context.event_bus.emit(
            name="contract_validator.started",
            producer=self.engine_id,
            target=str(context.paths.registries),
            payload={"module_count": len(module_registry)},
        )
        emitted_events.append("contract_validator.started")

        violations: list[dict[str, Any]] = []
        for entry in module_registry:
            violations.extend(_safe_validate("module_registry_entry", entry, "module", entry.get("module_id", "unknown"), "module_registry", context.execution_id))
        for entry in boundary_registry:
            violations.extend(_safe_validate("boundary_entry", entry, "boundary", entry.get("boundary_id", "unknown"), "boundary_registry", context.execution_id))
        for entry in contract_registry:
            violations.extend(_safe_validate("contract_registry_entry", entry, "contract", entry.get("contract_id", "unknown"), "contract_registry", context.execution_id))
            module_name = entry.get("module", "")
            try:
                spec = importlib.util.find_spec(module_name) if module_name else None
            except (ImportError, ModuleNotFoundError, ValueError):
                spec = None
            if spec is None:
                violations.append(
                    build_validation_violation(
                        rule_id="reference:contract.module",
                        severity=Severity.ERROR.value,
                        entity_type="contract",
                        entity_id=entry.get("contract_id", "unknown"),
                        location="contract_registry.module",
                        message="Contract registry module is not importable",
                        expected="importable module path",
                        observed=module_name,
                        snapshot_id=context.execution_id,
                    )
                )
        for entry in switch_registry:
            violations.extend(_safe_validate("switch_registry_entry", entry, "switch", entry.get("switch_id", "unknown"), "switch_registry", context.execution_id))
        for entry in switch_resolutions:
            violations.extend(_safe_validate("switch_resolution", entry, "switch_resolution", entry.get("switch_id", "unknown"), "switch_resolutions", context.execution_id))
        for entry in query_index:
            violations.extend(_safe_validate("query_index", entry, "query_index", entry.get("index_id", "unknown"), "query_index", context.execution_id))

        module_ids = {entry["module_id"] for entry in module_registry}
        boundary_ids = {entry["boundary_id"] for entry in boundary_registry}
        switch_ids = {entry["switch_id"] for entry in switch_registry}
        index_entity_ids = {entry["entity_id"] for entry in query_index}

        for module in module_registry:
            for boundary_id in module["boundaries"]:
                if boundary_id not in boundary_ids:
                    violations.append(
                        build_validation_violation(
                            rule_id="reference:module.boundaries",
                            severity=Severity.ERROR.value,
                            entity_type="module",
                            entity_id=module["module_id"],
                            location="module_registry.boundaries",
                            message=f"Unknown boundary reference {boundary_id}",
                            expected="boundary_id in boundary_registry",
                            observed=boundary_id,
                            snapshot_id=context.execution_id,
                        )
                    )
            for switch_id in module["switches"]:
                if switch_id not in switch_ids:
                    violations.append(
                        build_validation_violation(
                            rule_id="reference:module.switches",
                            severity=Severity.ERROR.value,
                            entity_type="module",
                            entity_id=module["module_id"],
                            location="module_registry.switches",
                            message=f"Unknown switch reference {switch_id}",
                            expected="switch_id in switch_registry",
                            observed=switch_id,
                            snapshot_id=context.execution_id,
                        )
                    )
            if module["module_id"] not in index_entity_ids:
                violations.append(
                    build_validation_violation(
                        rule_id="reference:query_index.module",
                        severity=Severity.WARNING.value,
                        entity_type="module",
                        entity_id=module["module_id"],
                        location="indices.query_index",
                        message="Module missing from query index",
                        expected="module_id indexed",
                        observed="missing",
                        snapshot_id=context.execution_id,
                    )
                )

        for boundary in boundary_registry:
            if boundary["source_module_id"] not in module_ids:
                violations.append(
                    build_validation_violation(
                        rule_id="reference:boundary.source",
                        severity=Severity.ERROR.value,
                        entity_type="boundary",
                        entity_id=boundary["boundary_id"],
                        location="boundary_registry.source_module_id",
                        message="Boundary source module does not exist",
                        expected="module_id in module_registry",
                        observed=boundary["source_module_id"],
                        snapshot_id=context.execution_id,
                    )
                )
            if boundary["target_type"] == "module" and boundary["target_id"] not in module_ids:
                violations.append(
                    build_validation_violation(
                        rule_id="reference:boundary.target",
                        severity=Severity.ERROR.value,
                        entity_type="boundary",
                        entity_id=boundary["boundary_id"],
                        location="boundary_registry.target_id",
                        message="Boundary target module does not exist",
                        expected="module_id in module_registry",
                        observed=boundary["target_id"],
                        snapshot_id=context.execution_id,
                    )
                )

        switch_by_id = {entry["switch_id"]: entry for entry in switch_registry}
        for entry in switch_registry:
            if entry["target_type"] == "module" and entry["target_id"] not in module_ids:
                violations.append(
                    build_validation_violation(
                        rule_id="reference:switch.target",
                        severity=Severity.ERROR.value,
                        entity_type="switch",
                        entity_id=entry["switch_id"],
                        location="switch_registry.target_id",
                        message="Switch target module does not exist",
                        expected="module_id in module_registry",
                        observed=entry["target_id"],
                        snapshot_id=context.execution_id,
                    )
                )
        for resolution in switch_resolutions:
            switch_entry = switch_by_id.get(resolution["switch_id"])
            if not switch_entry:
                violations.append(
                    build_validation_violation(
                        rule_id="reference:switch_resolution.switch",
                        severity=Severity.ERROR.value,
                        entity_type="switch_resolution",
                        entity_id=resolution["switch_id"],
                        location="switch_resolutions.switch_id",
                        message="Switch resolution references unknown switch",
                        expected="switch_id in switch_registry",
                        observed=resolution["switch_id"],
                        snapshot_id=context.execution_id,
                    )
                )
            elif resolution["target_id"] != switch_entry["target_id"]:
                violations.append(
                    build_validation_violation(
                        rule_id="consistency:switch_resolution.target",
                        severity=Severity.CRITICAL.value,
                        entity_type="switch_resolution",
                        entity_id=resolution["switch_id"],
                        location="switch_resolutions.target_id",
                        message="Switch resolution target disagrees with switch registry",
                        expected=switch_entry["target_id"],
                        observed=resolution["target_id"],
                        snapshot_id=context.execution_id,
                    )
                )

        severity_counts = Counter({severity.value: 0 for severity in Severity})
        severity_counts.update(violation["severity"] for violation in violations)
        summary_payload = build_contract_health_summary(
            snapshot_id=context.execution_id,
            total_rules=7,
            total_violations=len(violations),
            counts_by_severity=dict(severity_counts),
            validated_at=context.execution_time,
        )
        validation_report = {
            "summary": summary_payload,
            "violations": violations,
        }
        context.storage.write_registry(self.engine_id, "validation_report", validation_report)
        artifacts.append(context.storage.write_artifact(self.engine_id, "validation_report", "validation_report.json", validation_report))
        metrics = {
            "violation_count": len(violations),
            "critical_count": severity_counts[Severity.CRITICAL.value],
            "error_count": severity_counts[Severity.ERROR.value],
            "warning_count": severity_counts[Severity.WARNING.value],
        }
        context.event_bus.emit(
            name="contract_validator.completed",
            producer=self.engine_id,
            target=str(context.paths.registries),
            payload=metrics,
            severity=Severity.INFO.value if metrics["error_count"] == 0 and metrics["critical_count"] == 0 else Severity.WARNING.value,
        )
        emitted_events.append("contract_validator.completed")
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
