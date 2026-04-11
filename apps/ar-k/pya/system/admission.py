from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from pya.contracts.engine_contracts import validate_engine_manifest
from pya.system.compatibility import is_kernel_compatible
from pya.system.execution import CANONICAL_STAGE_ORDER
from pya.system.ownership import may_write


@dataclass
class AdmissionDecision:
    engine_id: str
    admitted: bool
    reasons: list[str]


def admit_engine_manifest(manifest: Mapping[str, Any], root_manifest: Mapping[str, Any]) -> AdmissionDecision:
    reasons: list[str] = []
    engine_id = str(manifest.get("engine_id", "unknown"))
    try:
        validate_engine_manifest(manifest)
    except Exception as exc:
        return AdmissionDecision(engine_id=engine_id, admitted=False, reasons=[str(exc)])

    if manifest["engine_type"] != engine_id:
        reasons.append("engine_type must match engine_id for canonical engines")

    kernel_requirement = manifest["compatibility"].get("kernel", "")
    if not is_kernel_compatible(kernel_requirement, root_manifest["version"]):
        reasons.append(f"kernel compatibility failed: required {kernel_requirement}, actual {root_manifest['version']}")

    stage = manifest["stage"]
    if stage not in CANONICAL_STAGE_ORDER:
        reasons.append(f"unknown stage: {stage}")

    writes = manifest["registries_touched"].get("writes", [])
    for registry_name in writes:
        if not may_write(engine_id, registry_name):
            reasons.append(f"{engine_id} is not the sovereign writer for registry {registry_name}")

    if engine_id not in root_manifest["canonical_engines"]:
        reasons.append(f"{engine_id} is not listed in canonical_engines")

    if manifest["stage"] != root_manifest["canonical_engines"].get(engine_id, {}).get("stage"):
        reasons.append(f"stage mismatch for {engine_id}")

    declared_contracts = set(manifest["compatibility"].get("contracts", {}).keys())
    required_contracts = set(root_manifest["contract_versions"].keys())
    missing = sorted(required_contracts.intersection({"signal", "module_registry_entry", "boundary_entry", "switch_registry_entry", "switch_resolution", "validation_violation", "annotation", "event", "execution_summary"}) - declared_contracts)
    if engine_id == "scanner":
        expected = {"signal", "event", "execution_summary"}
        undeclared = sorted(expected - declared_contracts)
        if undeclared:
            reasons.append(f"scanner missing contract declarations: {', '.join(undeclared)}")

    permissions = manifest["permissions"]
    if sorted(permissions.keys()) != ["reads", "writes"]:
        reasons.append("permissions must contain reads and writes")

    return AdmissionDecision(engine_id=engine_id, admitted=not reasons, reasons=reasons)
