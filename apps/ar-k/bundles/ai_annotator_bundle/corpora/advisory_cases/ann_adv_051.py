
"""Search service advisory case 051.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_adv_051'
FAMILY = 'advisory_cases'
TITLE = 'Search service advisory case 051'
TARGET_MODULE = 'search.service_051'

UPSTREAM_STATE = {
    "module_name": 'search.service_051',
    "module_status": 'canonical',
    "validation_state": 'warning',
    "switch_trace_shape": 'single_source',
    "ambiguity_focus": 'late validation note',
    "domain": 'catalog caching',
    "legacy_index_reference": 'registry_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'medium',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Captures evidence from catalog caching with single_source trace shape. Current upstream validation state is warning and ambiguity focus is late validation note. Primary risk under review is legacy alias confusion; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json']
PATH_EXAMPLES = ['reports/annotations/ann_adv_051_annotations.json', 'reports_real/annotations/ann_adv_051_do_not_write.json', 'reports/registries/ann_adv_051_must_not_exist.json']
EVIDENCE_LINES = ['Captures evidence from catalog caching with single_source trace shape.', 'Current upstream validation state is warning and ambiguity focus is late validation note.', 'Primary risk under review is legacy alias confusion; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for search.service_051.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: registry_index is the portable name even when legacy query_index shows up in older notes.', 'Note 2: bundle verify may emit sample JSON, while shipped corpus stays Python-first.', 'Note 3: reports_real is treated as safe-ignore runtime exhaust, not evidence input.', 'Note 4: AI Annotator may summarize conflicts, but cannot resolve ownership boundaries.', 'Note 5: advisory prose must remain safely ignorable by canonical writers.']
REVIEW_NOTES = ['registry_index is the portable name even when legacy query_index shows up in older notes', 'bundle verify may emit sample JSON, while shipped corpus stays Python-first', 'reports_real is treated as safe-ignore runtime exhaust, not evidence input', 'AI Annotator may summarize conflicts, but cannot resolve ownership boundaries', 'advisory prose must remain safely ignorable by canonical writers']

CASE = {
    "case_id": CASE_ID,
    "family": FAMILY,
    "title": TITLE,
    "target_module": TARGET_MODULE,
    "upstream_state": UPSTREAM_STATE,
    "advisory_expectation": ADVISORY_EXPECTATION,
    "forbidden_actions": FORBIDDEN_ACTIONS,
    "path_examples": PATH_EXAMPLES,
    "notes": EVIDENCE_LINES + REVIEW_NOTES,
}
