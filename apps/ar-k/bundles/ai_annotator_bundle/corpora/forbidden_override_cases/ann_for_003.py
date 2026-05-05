
"""Search service advisory case 003.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_for_003'
FAMILY = 'forbidden_override_cases'
TITLE = 'Search service advisory case 003'
TARGET_MODULE = 'search.service_003'

UPSTREAM_STATE = {
    "module_name": 'search.service_003',
    "module_status": 'candidate',
    "validation_state": 'gate_hold',
    "switch_trace_shape": 'single_source',
    "ambiguity_focus": 'late validation note',
    "domain": 'identity linking',
    "legacy_index_reference": 'registry_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'reviewed',
    "confidence_band": 'low',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Captures evidence from identity linking with single_source trace shape. Current upstream validation state is gate_hold and ambiguity focus is late validation note. Primary risk under review is legacy alias confusion; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'emit authoritative mode annotations']
PATH_EXAMPLES = ['reports/annotations/ann_for_003_annotations.json', 'reports_real/annotations/ann_for_003_do_not_write.json', 'reports/registries/ann_for_003_must_not_exist.json']
EVIDENCE_LINES = ['Captures evidence from identity linking with single_source trace shape.', 'Current upstream validation state is gate_hold and ambiguity focus is late validation note.', 'Primary risk under review is legacy alias confusion; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for search.service_003.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: advisory prose must remain safely ignorable by canonical writers.', 'Note 2: AI Annotator may summarize conflicts, but cannot resolve ownership boundaries.', 'Note 3: bundle verify may emit sample JSON, while shipped corpus stays Python-first.', 'Note 4: annotation_index is lookup sugar for advice, not a second registry throne.', 'Note 5: switch traces may be cited but never rewritten by annotations.']
REVIEW_NOTES = ['advisory prose must remain safely ignorable by canonical writers', 'AI Annotator may summarize conflicts, but cannot resolve ownership boundaries', 'bundle verify may emit sample JSON, while shipped corpus stays Python-first', 'annotation_index is lookup sugar for advice, not a second registry throne', 'switch traces may be cited but never rewritten by annotations']

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
