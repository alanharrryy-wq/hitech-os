from __future__ import annotations

BARRIER_REQUIREMENTS = {
    "scan": [],
    "registry": ["signals"],
    "switch": ["module_registry", "switch_registry"],
    "validate": ["module_registry", "boundary_registry", "contract_registry", "switch_registry", "switch_resolutions", "query_index"],
    "annotate": ["module_registry", "validation_report", "switch_resolutions"],
}
