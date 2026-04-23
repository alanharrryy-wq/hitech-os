from __future__ import annotations

MANIFEST = {
    'engine_id': 'scanner',
    'stage': 'stage_01_scan',
    'entrypoint': 'scanner_engine_snapshot:ScannerEngineSnapshot',
    'purpose': 'Discover source trees and emit observed-only artifacts without canonical writes.',
    'outputs_declared': [
        'scan_observed_modules.json',
        'scan_observed_boundaries.json',
        'scan_observed_paths.json',
        'scan_observed_summary.json',
    ],
    'forbidden_writes': [
        'module_registry.json',
        'boundary_registry.json',
        'registry_index.json',
        'switch_decision_registry.json',
        'switch_decision_trace.json',
        'validation_report.json',
        'gate_decisions.json',
        'annotations.json',
        'annotation_index.json',
    ],
}
