from __future__ import annotations

from collections import Counter
from collections import defaultdict
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

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
from pya.system.canon_policy import classify_source_path
from pya.system.state_model import validate_state_producer

PROMOTABLE_SURFACE_KINDS = {
    "python_module",
    "module",
    "entrypoint",
    "route_surface",
    "screen",
    "component",
    "desktop_bridge",
    "module_config",
}


@dataclass
class RegistryBuilderEngine:
    manifest: dict[str, Any]
    engine_id: str = "registry_builder"
    stage: str = "registry"

    def _module_name(self, signal: dict[str, Any]) -> str:
        module_name = signal.get("module_name")
        if module_name:
            return str(module_name)
        source_path = str(signal["source_path"])
        if source_path.endswith(".py"):
            return source_path[:-3].replace("/", ".")
        return source_path.replace("/", ".")

    def _module_kind(self, signal: dict[str, Any]) -> str:
        evidence = signal.get("evidence", {})
        surface_kind = evidence.get("surface_kind")
        if surface_kind:
            return str(surface_kind)
        if evidence.get("kind") == "python":
            return "python_module"
        return "module"

    def _module_area(self, signal: dict[str, Any], module_name: str) -> str:
        source_path = str(signal.get("source_path", ""))
        first = source_path.split("/", 1)[0]
        if first:
            return first
        return module_name.split(".", 1)[0]

    def _path_without_suffixes(self, value: str) -> str:
        pure = PurePosixPath(value)
        base = pure.as_posix()
        for suffix in pure.suffixes:
            if suffix and base.endswith(suffix):
                base = base[:-len(suffix)]
        return base

    def _promotion_decision(self, signal: dict[str, Any]) -> tuple[bool, str]:
        evidence = signal.get("evidence", {})
        source_path = str(signal.get("source_path", ""))
        path_policy = classify_source_path(source_path)
        if not path_policy.canonical_source:
            reason = path_policy.non_product_class or "noncanonical_path"
            return False, f"non_product:{reason}"
        if evidence.get("canonical_source") is False:
            reason = evidence.get("non_product_class") or path_policy.non_product_class or "scanner_noncanonical"
            return False, f"non_product:{reason}"
        if evidence.get("non_product_class"):
            return False, f"non_product:{evidence['non_product_class']}"
        for tag in signal.get("tags", []):
            tag_text = str(tag)
            if tag_text.startswith("non-product:"):
                return False, tag_text.replace("non-product:", "non_product:")
        surface_kind = str(evidence.get("surface_kind", ""))
        if surface_kind and surface_kind not in PROMOTABLE_SURFACE_KINDS:
            return False, f"unsupported_surface:{surface_kind}"
        return True, "promoted"

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
        boundary_signals = [signal for signal in signals if signal["signal_type"] == "boundary_candidate"]
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        skipped_module_candidates: list[dict[str, str]] = []
        for signal in module_signals:
            should_promote, reason = self._promotion_decision(signal)
            if not should_promote:
                skipped_module_candidates.append(
                    {
                        "source_path": str(signal["source_path"]),
                        "module_name": self._module_name(signal),
                        "reason": reason,
                    }
                )
                continue
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
                    kind=self._module_kind(signal),
                    area=self._module_area(signal, module_name),
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
        canonical_by_path_no_ext: dict[str, dict[str, Any]] = {}
        for module in module_registry:
            for observed in module["observed_in"]:
                canonical_by_path_no_ext[self._path_without_suffixes(observed)] = module
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

        def resolve_python_import_name(source_module_name: str, imported: str) -> str:
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

        def resolve_text_import_path(source_path: str, imported: str) -> str | None:
            cleaned = imported.split("?", 1)[0].split("#", 1)[0]
            if not cleaned:
                return None
            if cleaned.startswith("."):
                source_parent = PurePosixPath(source_path).parent
                return self._path_without_suffixes((source_parent / cleaned).as_posix())
            if cleaned.startswith("/"):
                return self._path_without_suffixes(cleaned.lstrip("/"))
            return None

        boundary_registry: list[dict[str, Any]] = []
        boundary_ids_by_source: dict[str, list[str]] = defaultdict(list)
        for signal in sorted(import_signals, key=lambda item: (item["source_path"], item["evidence"].get("target_import", ""))):
            source_module_id = module_id_by_path.get(signal["source_path"])
            if not source_module_id:
                continue
            imported = signal["evidence"].get("target_import", "")
            source_module_name = signal["evidence"].get("module_name") or self._module_name(signal)
            source_path = signal["source_path"]
            surface_kind = str(signal["evidence"].get("surface_kind", ""))
            resolved_import = resolve_python_import_name(source_module_name, imported) if surface_kind == "python_module" or str(source_path).endswith(".py") else imported
            path_candidate = None if surface_kind == "python_module" or str(source_path).endswith(".py") else resolve_text_import_path(str(source_path), imported)
            target_module = canonical_by_name.get(resolved_import)
            if target_module is None and path_candidate:
                target_module = canonical_by_path_no_ext.get(path_candidate)
            target_type = "module" if target_module else "external"
            target_id = target_module["module_id"] if target_module else f"external:{resolved_import or imported}"
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

        for signal in sorted(boundary_signals, key=lambda item: (item["source_path"], item["evidence"].get("boundary_kind", ""))):
            source_module_id = module_id_by_path.get(signal["source_path"])
            if not source_module_id:
                continue
            boundary_kind = signal["evidence"].get("boundary_kind", "observed_boundary")
            boundary = build_boundary_entry(
                source_module_id=source_module_id,
                target_id=f"capability:{boundary_kind}",
                target_type="external",
                boundary_type=str(boundary_kind),
                source_of_truth="scanner.signals",
                status=State.CANONICAL.value,
                evidence={"source_path": signal["source_path"], "boundary_kind": boundary_kind},
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
        skipped_paths = sorted({item["source_path"] for item in skipped_module_candidates})
        summary_payload["skipped_module_candidate_paths"] = skipped_paths
        summary_payload["skipped_module_candidates"] = sorted(
            skipped_module_candidates,
            key=lambda item: (item["reason"], item["source_path"], item["module_name"]),
        )
        summary_payload["skipped_module_candidate_reasons"] = dict(Counter(item["reason"] for item in skipped_module_candidates))
        artifacts.append(context.storage.write_artifact(self.engine_id, "metrics", "registry_build_summary.json", summary_payload))
        metrics = {
            "module_count": len(module_registry),
            "boundary_count": len(boundary_registry),
            "contract_count": len(contract_registry),
            "conflict_count": len(conflicts),
            "skipped_module_candidate_count": len(skipped_paths),
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
