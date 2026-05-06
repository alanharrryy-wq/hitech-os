
"""Search service advisory case 057.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_amb_057'
FAMILY = 'ambiguity_cases'
TITLE = 'Search service advisory case 057'
TARGET_MODULE = 'search.service_057'

UPSTREAM_STATE = {
    "module_name": 'search.service_057',
    "module_status": 'candidate',
    "validation_state": 'error_shadow',
    "switch_trace_shape": 'legacy_alias',
    "ambiguity_focus": 'naming collision',
    "domain": 'ops runbooks',
    "legacy_index_reference": 'registry_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'low',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Captures evidence from ops runbooks with legacy_alias trace shape. Current upstream validation state is error_shadow and ambiguity focus is naming collision. Primary risk under review is false certainty; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'pretend uncertainty is resolved upstream']
PATH_EXAMPLES = ['reports/annotations/ann_amb_057_annotations.json', 'reports_real/annotations/ann_amb_057_do_not_write.json', 'reports/registries/ann_amb_057_must_not_exist.json']
EVIDENCE_LINES = ['Captures evidence from ops runbooks with legacy_alias trace shape.', 'Current upstream validation state is error_shadow and ambiguity focus is naming collision.', 'Primary risk under review is false certainty; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for search.service_057.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: registry_index is the portable name even when legacy query_index shows up in older notes.', 'Note 2: bundle verify may emit sample JSON, while shipped corpus stays Python-first.', 'Note 3: upstream gate outcome is evidence, never a thing to overwrite.', 'Note 4: annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay.', 'Note 5: switch traces may be cited but never rewritten by annotations.']
REVIEW_NOTES = ['registry_index is the portable name even when legacy query_index shows up in older notes', 'bundle verify may emit sample JSON, while shipped corpus stays Python-first', 'upstream gate outcome is evidence, never a thing to overwrite', 'annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay', 'switch traces may be cited but never rewritten by annotations']

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
