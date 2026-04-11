from __future__ import annotations

from typing import Callable, Mapping

from .annotation_contracts import validate_annotation
from .artifact_contracts import validate_artifact
from .engine_contracts import validate_engine_manifest, validate_execution_summary
from .event_contracts import validate_event
from .index_contracts import validate_query_index_entry
from .registry_contracts import (
    build_contract_registry_entry,
    validate_boundary_entry,
    validate_contract_registry_entry,
    validate_module_registry_entry,
    validate_registry_build_summary,
)
from .signal_contract import validate_signal
from .snapshot_contracts import validate_delta, validate_snapshot
from .switch_contracts import validate_switch_registry_entry, validate_switch_resolution
from .validation_contracts import validate_contract_health_summary, validate_validation_violation

CONTRACT_VERSIONS = {
    "signal": "1.0.0",
    "module_registry_entry": "1.0.0",
    "boundary_entry": "1.0.0",
    "switch_registry_entry": "1.0.0",
    "switch_resolution": "1.0.0",
    "validation_violation": "1.0.0",
    "annotation": "1.0.0",
    "artifact": "1.0.0",
    "snapshot": "1.0.0",
    "delta": "1.0.0",
    "engine_manifest": "1.0.0",
    "execution_summary": "1.0.0",
    "event": "1.0.0",
    "query_index": "1.0.0",
    "contract_registry_entry": "1.0.0",
    "registry_build_summary": "1.0.0",
    "contract_health_summary": "1.0.0",
}

CONTRACT_MODULES = {
    "annotation": "pya.contracts.annotation_contracts",
    "artifact": "pya.contracts.artifact_contracts",
    "boundary_entry": "pya.contracts.registry_contracts",
    "contract_health_summary": "pya.contracts.validation_contracts",
    "contract_registry_entry": "pya.contracts.registry_contracts",
    "delta": "pya.contracts.snapshot_contracts",
    "engine_manifest": "pya.contracts.engine_contracts",
    "event": "pya.contracts.event_contracts",
    "execution_summary": "pya.contracts.engine_contracts",
    "module_registry_entry": "pya.contracts.registry_contracts",
    "query_index": "pya.contracts.index_contracts",
    "registry_build_summary": "pya.contracts.registry_contracts",
    "signal": "pya.contracts.signal_contract",
    "snapshot": "pya.contracts.snapshot_contracts",
    "switch_registry_entry": "pya.contracts.switch_contracts",
    "switch_resolution": "pya.contracts.switch_contracts",
    "validation_violation": "pya.contracts.validation_contracts",
}

CONTRACT_VALIDATORS: dict[str, Callable[[Mapping[str, object]], Mapping[str, object]]] = {
    "signal": validate_signal,
    "module_registry_entry": validate_module_registry_entry,
    "boundary_entry": validate_boundary_entry,
    "switch_registry_entry": validate_switch_registry_entry,
    "switch_resolution": validate_switch_resolution,
    "validation_violation": validate_validation_violation,
    "annotation": validate_annotation,
    "artifact": validate_artifact,
    "snapshot": validate_snapshot,
    "delta": validate_delta,
    "engine_manifest": validate_engine_manifest,
    "execution_summary": validate_execution_summary,
    "event": validate_event,
    "query_index": validate_query_index_entry,
    "contract_registry_entry": validate_contract_registry_entry,
    "registry_build_summary": validate_registry_build_summary,
    "contract_health_summary": validate_contract_health_summary,
}


def get_contract_registry_entries() -> list[dict[str, object]]:
    missing_modules = sorted(set(CONTRACT_VERSIONS) - set(CONTRACT_MODULES))
    if missing_modules:
        raise ValueError(f"Missing contract module mapping for: {', '.join(missing_modules)}")
    return [
        build_contract_registry_entry(
            contract_id=name,
            version=version,
            owner="contracts",
            module=CONTRACT_MODULES[name],
            description=f"Canonical contract for {name.replace('_', ' ')}",
        )
        for name, version in sorted(CONTRACT_VERSIONS.items())
    ]
