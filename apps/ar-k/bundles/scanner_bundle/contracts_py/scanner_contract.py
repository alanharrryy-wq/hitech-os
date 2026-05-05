from __future__ import annotations

from dataclasses import dataclass

from .ownership_rules import scanner_may_write, scanner_must_not_write

REQUIRED_SCANNER_ARTIFACTS = (
    'scan_observed_modules.json',
    'scan_observed_boundaries.json',
    'scan_observed_paths.json',
    'scan_observed_summary.json',
)
FORBIDDEN_SCANNER_WRITES = (
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

@dataclass(frozen=True)
class ScannerWriteScope:
    install_rel: str = 'bundles/scanner_bundle'
    state_rel: str = '.ark_install/scanner_bundle'
    verification_outputs_rel: str = '.ark_install/scanner_bundle/verification_outputs'


def validate_scanner_write_target(name: str) -> None:
    if scanner_must_not_write(name):
        raise ValueError(f'Scanner must not write canonical or downstream artifact: {name}')
    if not scanner_may_write(name):
        raise ValueError(f'Scanner write is outside homologated observed-only scope: {name}')
