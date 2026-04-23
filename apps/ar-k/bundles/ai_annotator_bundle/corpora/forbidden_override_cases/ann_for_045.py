
"""Search service advisory case 045.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_for_045'
FAMILY = 'forbidden_override_cases'
TITLE = 'Search service advisory case 045'
TARGET_MODULE = 'search.service_045'

UPSTREAM_STATE = {
    "module_name": 'search.service_045',
    "module_status": 'candidate',
    "validation_state": 'clean',
    "switch_trace_shape": 'single_source',
    "ambiguity_focus": 'late validation note',
    "domain": 'checkout toggles',
    "legacy_index_reference": 'registry_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'reviewed',
    "confidence_band": 'low',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Records evidence from checkout toggles with single_source trace shape. Current upstream validation state is clean and ambiguity focus is late validation note. Primary risk under review is legacy alias confusion; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'emit authoritative mode annotations']
PATH_EXAMPLES = ['reports/annotations/ann_for_045_annotations.json', 'reports_real/annotations/ann_for_045_do_not_write.json', 'reports/registries/ann_for_045_must_not_exist.json']
EVIDENCE_LINES = ['Records evidence from checkout toggles with single_source trace shape.', 'Current upstream validation state is clean and ambiguity focus is late validation note.', 'Primary risk under review is legacy alias confusion; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for search.service_045.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: bundle verify may emit sample JSON, while shipped corpus stays Python-first.', 'Note 2: upstream gate outcome is evidence, never a thing to overwrite.', 'Note 3: advisory prose must remain safely ignorable by canonical writers.', 'Note 4: registry_index is the portable name even when legacy query_index shows up in older notes.', 'Note 5: switch traces may be cited but never rewritten by annotations.']
REVIEW_NOTES = ['bundle verify may emit sample JSON, while shipped corpus stays Python-first', 'upstream gate outcome is evidence, never a thing to overwrite', 'advisory prose must remain safely ignorable by canonical writers', 'registry_index is the portable name even when legacy query_index shows up in older notes', 'switch traces may be cited but never rewritten by annotations']

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
