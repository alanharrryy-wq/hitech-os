
"""Ops client advisory case 016.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_amb_016'
FAMILY = 'ambiguity_cases'
TITLE = 'Ops client advisory case 016'
TARGET_MODULE = 'ops.client_016'

UPSTREAM_STATE = {
    "module_name": 'ops.client_016',
    "module_status": 'candidate',
    "validation_state": 'warning',
    "switch_trace_shape": 'legacy_alias',
    "ambiguity_focus": 'late validation note',
    "domain": 'catalog caching',
    "legacy_index_reference": 'query_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'low',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Flags evidence from catalog caching with legacy_alias trace shape. Current upstream validation state is warning and ambiguity focus is late validation note. Primary risk under review is legacy alias confusion; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'pretend uncertainty is resolved upstream']
PATH_EXAMPLES = ['reports/annotations/ann_amb_016_annotations.json', 'reports_real/annotations/ann_amb_016_do_not_write.json', 'reports/registries/ann_amb_016_must_not_exist.json']
EVIDENCE_LINES = ['Flags evidence from catalog caching with legacy_alias trace shape.', 'Current upstream validation state is warning and ambiguity focus is late validation note.', 'Primary risk under review is legacy alias confusion; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for ops.client_016.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay.', 'Note 2: switch traces may be cited but never rewritten by annotations.', 'Note 3: registry_index is the portable name even when legacy query_index shows up in older notes.', 'Note 4: upstream gate outcome is evidence, never a thing to overwrite.', 'Note 5: annotation_index is lookup sugar for advice, not a second registry throne.']
REVIEW_NOTES = ['annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay', 'switch traces may be cited but never rewritten by annotations', 'registry_index is the portable name even when legacy query_index shows up in older notes', 'upstream gate outcome is evidence, never a thing to overwrite', 'annotation_index is lookup sugar for advice, not a second registry throne']

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
