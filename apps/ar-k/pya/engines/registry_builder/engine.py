from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from pya.contracts.base import deterministic_id
from pya.contracts.engine_contracts import build_execution_summary
from pya.contracts.enums import State
from pya.contracts.index_contracts import build_query_index_entry
from pya.contracts.registry_contracts import (
    build_boundary_entry,
    build_module_registry_entry,
    build_registry_build_summary,
)
from pya.contracts.switch_contracts import build_switch_registry_entry
from pya.contracts.contract_registry import get_contract_registry_entries
from pya.kernel.identity import module_id_from_path
from pya.kernel.models import EngineRunResult
from pya.system.state_model import validate_state_producer


@dataclass
class RegistryBuilderEngine:
    manifest: dict[str, Any]
    engine_id: str = "registry_builder"
    stage: str = "registry"

    def _module_name(self, signal: dict[str, Any]) -> str:
        return signal.get("module_name") or signal["source_path"][:-3].replace("/", ".")

    def run(self, context) -> EngineRunResult:
        started_at = context.execution_time
        emitted_events = []
        artifacts: list[dict[str, Any]] = []
        signals = context.storage.read_registry(self.engine_id, "signals", default=[])
        context.event_bus.emit(
            name="registry_builder.started",
            producer=self.engine_id,
            target=str(context.paths.registries),
            payload={"signal_count": len(signals)},
        )
        emitted_events.append("registry_builder.started")

        module_signals = [signal for signal in signals if signal["signal_type"] == "module_candidate"]
        import_signals = [signal for signal in signals if signal["signal_type"] == "import_edge"]
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for signal in module_signals:
            grouped[self._module_name(signal)].append(signal)

        module_registry: list[dict[str, Any]] = []
        canonical_by_name: dict[str, dict[str, Any]] = {}
        module_id_by_path: dict[str, str] = {}
        conflicts: list[dict[str, Any]] = []

        for module_name in sorted(grouped):
            candidates = sorted(grouped[module_name], key=lambda item: item["source_path"])
            if len(candidates) > 1:
                conflicts.append(
                    {
                        "module_name": module_name,
                        "paths": [item["source_path"] for item in candidates],
                        "resolution": candidates[0]["source_path"],
                    }
                )
            for index, signal in enumerate(candidates):
                is_ambiguous = signal["state"] == State.AMBIGUOUS.value
                if is_ambiguous:
                    status = State.CANDIDATE.value
                elif index == 0:
                    status = State.CANONICAL.value
                else:
                    status = State.SUPERSEDED.value
                validate_state_producer(self.engine_id, status)
                module_id = module_id_from_path(signal["source_path"])
                module_id_by_path[signal["source_path"]] = module_id
                switch_id = f"module.enabled:{module_id}"
                entry = build_module_registry_entry(
                    module_id=module_id,
                    name=module_name,
                    kind="python_module",
                    area=module_name.split(".", 1)[0],
                    status=status,
                    source_of_truth="scanner.signals",
                    confidence=min(0.95, float(signal["confidence"]) + (0.1 if status == State.CANONICAL.value else 0.0)),
                    declared_by=[self.engine_id],
                    observed_in=[signal["source_path"]],
                    tags=signal.get("tags", []),
                    boundaries=[],
                    switches=[switch_id],
                    contracts=["signal", "module_registry_entry"],
                    artifacts=[],
                    updated_at=context.execution_time,
                    snapshot_id=context.execution_id,
                )
                module_registry.append(entry)
                if status == State.CANONICAL.value:
                    canonical_by_name[module_name] = entry

        switch_registry: list[dict[str, Any]] = []
        for module in sorted(module_registry, key=lambda item: item["module_id"]):
            switch_registry.append(
                build_switch_registry_entry(
                    switch_id=module["switches"][0],
                    target_type="module",
                    target_id=module["module_id"],
                    default_value=True,
                    applicable_rules=["default_true", "switch_override", "target_override"],
                    allowed_overrides=["switch_id", "target_id"],
                    rollout={"strategy": "static", "owner": self.engine_id},
                    metadata={"module_name": module["name"]},
                    state=State.CANONICAL.value,
                    updated_at=context.execution_time,
                )
            )

        def resolve_import_name(source_module_name: str, imported: str) -> str:
            if not imported.startswith("."):
                return imported
            level = len(imported) - len(imported.lstrip("."))
            suffix = imported.lstrip(".")
            source_parts = source_module_name.split(".")
            base_parts = source_parts[:-1]
            if level > 1:
                base_parts = base_parts[: max(0, len(base_parts) - (level - 1))]
            if suffix:
                base_parts = [*base_parts, suffix]
            return ".".join(part for part in base_parts if part)

        boundary_registry: list[dict[str, Any]] = []
        boundary_ids_by_source: dict[str, list[str]] = defaultdict(list)
        for signal in sorted(import_signals, key=lambda item: (item["source_path"], item["evidence"].get("target_import", ""))):
            source_module_id = module_id_by_path.get(signal["source_path"])
            if not source_module_id:
                continue
            imported = signal["evidence"].get("target_import", "")
            source_module_name = signal["evidence"].get("module_name") or signal["source_path"][:-3].replace("/", ".")
            resolved_import = resolve_import_name(source_module_name, imported)
            target_type = "module" if resolved_import in canonical_by_name else "external"
            target_id = canonical_by_name[resolved_import]["module_id"] if resolved_import in canonical_by_name else f"external:{resolved_import}"
            boundary = build_boundary_entry(
                source_module_id=source_module_id,
                target_id=target_id,
                target_type=target_type,
                boundary_type="import",
                source_of_truth="scanner.signals",
                status=State.CANONICAL.value,
                evidence={"source_path": signal["source_path"], "import": imported},
                snapshot_id=context.execution_id,
                updated_at=context.execution_time,
            )
            boundary_registry.append(boundary)
            boundary_ids_by_source[source_module_id].append(boundary["boundary_id"])

        for module in module_registry:
            module["boundaries"] = sorted(boundary_ids_by_source.get(module["module_id"], []))

        contract_registry = get_contract_registry_entries()
        for entry in contract_registry:
            entry["updated_at"] = context.execution_time

        query_index = []
        for module in sorted(module_registry, key=lambda item: item["module_id"]):
            query_index.append(
                build_query_index_entry(
                    entity_type="module",
                    entity_id=module["module_id"],
                    lookup_keys=sorted(set([module["name"], module["module_id"], *module["observed_in"], *module["tags"]])),
                    registry_source="module_registry",
                    snapshot_id=context.execution_id,
                    updated_at=context.execution_time,
                )
            )

        context.storage.write_registry(self.engine_id, "module_registry", module_registry)
        context.storage.write_registry(self.engine_id, "boundary_registry", boundary_registry)
        context.storage.write_registry(self.engine_id, "contract_registry", contract_registry)
        context.storage.write_registry(self.engine_id, "switch_registry", switch_registry)
        context.storage.write_index(self.engine_id, "query_index", query_index)

        registry_bundle = {
            "module_registry": module_registry,
            "boundary_registry": boundary_registry,
            "contract_registry": contract_registry,
            "switch_registry": switch_registry,
            "query_index": query_index,
        }
        artifacts.append(context.storage.write_snapshot(self.engine_id, "registry_bundle", registry_bundle))
        artifacts.append(context.storage.write_delta(self.engine_id, "registry_bundle", {"previous": None, "current": registry_bundle}))
        summary_payload = build_registry_build_summary(
            snapshot_id=context.execution_id,
            module_count=len(module_registry),
            boundary_count=len(boundary_registry),
            contract_count=len(contract_registry),
            conflicts=conflicts,
            created_at=context.execution_time,
        )
        artifacts.append(context.storage.write_artifact(self.engine_id, "metrics", "registry_build_summary.json", summary_payload))
        metrics = {
            "module_count": len(module_registry),
            "boundary_count": len(boundary_registry),
            "contract_count": len(contract_registry),
            "conflict_count": len(conflicts),
        }
        context.event_bus.emit(
            name="registry_builder.completed",
            producer=self.engine_id,
            target=str(context.paths.registries),
            payload=metrics,
        )
        emitted_events.append("registry_builder.completed")

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
