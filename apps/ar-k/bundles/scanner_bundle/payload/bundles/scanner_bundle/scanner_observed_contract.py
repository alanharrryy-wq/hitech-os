from __future__ import annotations

REQUIRED_OBSERVED_ARTIFACTS = (
    'scan_observed_modules.json',
    'scan_observed_boundaries.json',
    'scan_observed_paths.json',
    'scan_observed_summary.json',
)
FORBIDDEN_WRITES = (
    'module_registry.json',
    'boundary_registry.json',
    'registry_index.json',
    'switch_decision_registry.json',
    'switch_decision_trace.json',
    'validation_report.json',
    'gate_decisions.json',
    'annotations.json',
    'annotation_index.json',
)


def is_forbidden_write(name: str) -> bool:
    return name in FORBIDDEN_WRITES
