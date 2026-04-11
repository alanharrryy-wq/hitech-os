from __future__ import annotations

CHECKPOINT_POLICY = {
    "snapshot_writer": "registry_builder",
    "delta_writer": "registry_builder",
    "snapshot_families": ["module_registry", "boundary_registry", "contract_registry", "switch_registry", "query_index"],
    "delta_strategy": "current_minus_previous",
}
