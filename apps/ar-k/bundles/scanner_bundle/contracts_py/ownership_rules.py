from __future__ import annotations

TOOL_OWNERSHIP = {
    'scanner': {
        'writes': (
            'scan_observed_modules.json',
            'scan_observed_boundaries.json',
            'scan_observed_paths.json',
            'scan_observed_summary.json',
        ),
        'forbidden': (
            'module_registry.json',
            'boundary_registry.json',
            'registry_index.json',
            'switch_decision_registry.json',
            'switch_decision_trace.json',
            'validation_report.json',
            'gate_decisions.json',
            'annotations.json',
            'annotation_index.json',
        ),
    },
    'registry_builder': {
        'writes': ('module_registry.json', 'boundary_registry.json', 'registry_index.json'),
        'forbidden': ('switch_decision_registry.json', 'annotations.json'),
    },
    'switch_engine': {
        'writes': ('switch_decision_registry.json', 'switch_decision_trace.json'),
        'forbidden': ('module_registry.json', 'annotations.json'),
    },
    'contract_validator': {
        'writes': ('validation_report.json', 'gate_decisions.json'),
        'forbidden': ('module_registry.json', 'annotations.json'),
    },
    'ai_annotator': {
        'writes': ('annotations.json', 'annotation_index.json'),
        'forbidden': ('module_registry.json', 'gate_decisions.json'),
    },
}

def scanner_may_write(name: str) -> bool:
    return name in TOOL_OWNERSHIP['scanner']['writes']

def scanner_must_not_write(name: str) -> bool:
    return name in TOOL_OWNERSHIP['scanner']['forbidden']
