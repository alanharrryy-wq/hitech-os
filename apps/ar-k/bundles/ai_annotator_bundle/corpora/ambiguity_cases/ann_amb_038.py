
"""Catalog repository advisory case 038.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_amb_038'
FAMILY = 'ambiguity_cases'
TITLE = 'Catalog repository advisory case 038'
TARGET_MODULE = 'catalog.repository_038'

UPSTREAM_STATE = {
    "module_name": 'catalog.repository_038',
    "module_status": 'candidate',
    "validation_state": 'gate_hold',
    "switch_trace_shape": 'legacy_alias',
    "ambiguity_focus": 'late validation note',
    "domain": 'identity linking',
    "legacy_index_reference": 'registry_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'low',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Highlights evidence from identity linking with legacy_alias trace shape. Current upstream validation state is gate_hold and ambiguity focus is late validation note. Primary risk under review is legacy alias confusion; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'pretend uncertainty is resolved upstream']
PATH_EXAMPLES = ['reports/annotations/ann_amb_038_annotations.json', 'reports_real/annotations/ann_amb_038_do_not_write.json', 'reports/registries/ann_amb_038_must_not_exist.json']
EVIDENCE_LINES = ['Highlights evidence from identity linking with legacy_alias trace shape.', 'Current upstream validation state is gate_hold and ambiguity focus is late validation note.', 'Primary risk under review is legacy alias confusion; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for catalog.repository_038.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti.', 'Note 2: registry_index is the portable name even when legacy query_index shows up in older notes.', 'Note 3: AI Annotator may summarize conflicts, but cannot resolve ownership boundaries.', 'Note 4: switch traces may be cited but never rewritten by annotations.', 'Note 5: reports_real is treated as safe-ignore runtime exhaust, not evidence input.']
REVIEW_NOTES = ['installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti', 'registry_index is the portable name even when legacy query_index shows up in older notes', 'AI Annotator may summarize conflicts, but cannot resolve ownership boundaries', 'switch traces may be cited but never rewritten by annotations', 'reports_real is treated as safe-ignore runtime exhaust, not evidence input']

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
