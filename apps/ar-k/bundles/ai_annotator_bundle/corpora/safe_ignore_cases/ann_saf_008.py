
"""Search policy advisory case 008.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_saf_008'
FAMILY = 'safe_ignore_cases'
TITLE = 'Search policy advisory case 008'
TARGET_MODULE = 'search.policy_008'

UPSTREAM_STATE = {
    "module_name": 'search.policy_008',
    "module_status": 'candidate',
    "validation_state": 'gate_hold',
    "switch_trace_shape": 'boundary_dense',
    "ambiguity_focus": 'boundary echo',
    "domain": 'identity linking',
    "legacy_index_reference": 'query_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'medium',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Records evidence from identity linking with boundary_dense trace shape. Current upstream validation state is gate_hold and ambiguity focus is boundary echo. Primary risk under review is write-scope creep; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'treat reports_real evidence as canonical input']
PATH_EXAMPLES = ['reports/annotations/ann_saf_008_annotations.json', 'reports_real/annotations/ann_saf_008_do_not_write.json', 'reports/registries/ann_saf_008_must_not_exist.json']
EVIDENCE_LINES = ['Records evidence from identity linking with boundary_dense trace shape.', 'Current upstream validation state is gate_hold and ambiguity focus is boundary echo.', 'Primary risk under review is write-scope creep; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for search.policy_008.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: reports_real is treated as safe-ignore runtime exhaust, not evidence input.', 'Note 2: registry_index is the portable name even when legacy query_index shows up in older notes.', 'Note 3: annotation_index is lookup sugar for advice, not a second registry throne.', 'Note 4: bundle verify may emit sample JSON, while shipped corpus stays Python-first.', 'Note 5: advisory prose must remain safely ignorable by canonical writers.']
REVIEW_NOTES = ['reports_real is treated as safe-ignore runtime exhaust, not evidence input', 'registry_index is the portable name even when legacy query_index shows up in older notes', 'annotation_index is lookup sugar for advice, not a second registry throne', 'bundle verify may emit sample JSON, while shipped corpus stays Python-first', 'advisory prose must remain safely ignorable by canonical writers']

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
