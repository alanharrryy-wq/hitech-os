
"""Ops client advisory case 034.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_amb_034'
FAMILY = 'ambiguity_cases'
TITLE = 'Ops client advisory case 034'
TARGET_MODULE = 'ops.client_034'

UPSTREAM_STATE = {
    "module_name": 'ops.client_034',
    "module_status": 'candidate',
    "validation_state": 'ambiguous',
    "switch_trace_shape": 'legacy_alias',
    "ambiguity_focus": 'late validation note',
    "domain": 'search ranking',
    "legacy_index_reference": 'registry_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'low',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Highlights evidence from search ranking with legacy_alias trace shape. Current upstream validation state is ambiguous and ambiguity focus is late validation note. Primary risk under review is legacy alias confusion; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'pretend uncertainty is resolved upstream']
PATH_EXAMPLES = ['reports/annotations/ann_amb_034_annotations.json', 'reports_real/annotations/ann_amb_034_do_not_write.json', 'reports/registries/ann_amb_034_must_not_exist.json']
EVIDENCE_LINES = ['Highlights evidence from search ranking with legacy_alias trace shape.', 'Current upstream validation state is ambiguous and ambiguity focus is late validation note.', 'Primary risk under review is legacy alias confusion; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for ops.client_034.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti.', 'Note 2: upstream gate outcome is evidence, never a thing to overwrite.', 'Note 3: AI Annotator may summarize conflicts, but cannot resolve ownership boundaries.', 'Note 4: registry_index is the portable name even when legacy query_index shows up in older notes.', 'Note 5: annotation_index is lookup sugar for advice, not a second registry throne.']
REVIEW_NOTES = ['installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti', 'upstream gate outcome is evidence, never a thing to overwrite', 'AI Annotator may summarize conflicts, but cannot resolve ownership boundaries', 'registry_index is the portable name even when legacy query_index shows up in older notes', 'annotation_index is lookup sugar for advice, not a second registry throne']

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
