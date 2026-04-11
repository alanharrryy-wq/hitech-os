from __future__ import annotations

from pya.contracts.contract_registry import CONTRACT_VERSIONS
from pya.system.checkpoints import CHECKPOINT_POLICY
from pya.system.compatibility import COMPATIBILITY_RULES, KERNEL_VERSION
from pya.system.contract_evolution import CONTRACT_EVOLUTION_POLICY
from pya.system.execution import CANONICAL_STAGE_ORDER
from pya.system.integration_rules import INTEGRATION_RULES
from pya.system.ownership import OWNERSHIP_MATRIX
from pya.system.state_model import STATE_PRODUCERS, VALID_TRANSITIONS

ROOT_MANIFEST = {
    "system_id": "ar-k-governed-platform",
    "version": KERNEL_VERSION,
    "canonical_engines": {
        "scanner": {"stage": "scan", "purpose": "discover structure and emit signals"},
        "registry_builder": {"stage": "registry", "purpose": "consolidate observations into registries"},
        "switch_engine": {"stage": "switch", "purpose": "resolve effective switch states"},
        "contract_validator": {"stage": "validate", "purpose": "judge schema and policy compliance"},
        "ai_annotator": {"stage": "annotate", "purpose": "generate non-canonical annotations"},
    },
    "canonical_stage_order": CANONICAL_STAGE_ORDER,
    "required_registries": list(OWNERSHIP_MATRIX.keys()),
    "required_indices": ["query_index"],
    "required_artifact_families": [
        "inventory",
        "graph",
        "metrics",
        "snapshot",
        "delta",
        "execution_summary",
        "decision_trace",
    ],
    "state_model": {
        "producers": STATE_PRODUCERS,
        "transitions": {key: sorted(value) for key, value in VALID_TRANSITIONS.items()},
    },
    "compatibility_matrix": COMPATIBILITY_RULES,
    "contract_versions": CONTRACT_VERSIONS,
    "integration_policy": INTEGRATION_RULES,
    "admission_policy": {
        "required_fields": ["stage", "entrypoint", "permissions", "compatibility", "events_emitted", "registries_touched"],
        "reject_conflicting_writers": True,
        "reject_unknown_stage": True,
    },
    "ownership_policy": OWNERSHIP_MATRIX,
    "determinism_policy": {
        "stable_iteration": True,
        "stable_serialization": True,
        "canonical_hash": "sha256 over stable json",
        "normalized_paths": "relative posix-style path from execution target",
        "timestamps": "single execution timestamp passed through the run",
        "no_cwd_dependency": True,
        "no_import_side_effects": True,
        "stable_ids": True,
        "typed_errors": True,
        "reproducible_snapshots": True,
    },
    "lifecycle_policy": CHECKPOINT_POLICY,
    "contract_evolution_policy": CONTRACT_EVOLUTION_POLICY,
}


def get_root_manifest() -> dict[str, object]:
    return ROOT_MANIFEST
