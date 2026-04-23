
"""Routing repository advisory case 035.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_amb_035'
FAMILY = 'ambiguity_cases'
TITLE = 'Routing repository advisory case 035'
TARGET_MODULE = 'routing.repository_035'

UPSTREAM_STATE = {
    "module_name": 'routing.repository_035',
    "module_status": 'candidate',
    "validation_state": 'clean',
    "switch_trace_shape": 'legacy_alias',
    "ambiguity_focus": 'naming collision',
    "domain": 'checkout toggles',
    "legacy_index_reference": 'registry_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'low',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Records evidence from checkout toggles with legacy_alias trace shape. Current upstream validation state is clean and ambiguity focus is naming collision. Primary risk under review is false certainty; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'pretend uncertainty is resolved upstream']
PATH_EXAMPLES = ['reports/annotations/ann_amb_035_annotations.json', 'reports_real/annotations/ann_amb_035_do_not_write.json', 'reports/registries/ann_amb_035_must_not_exist.json']
EVIDENCE_LINES = ['Records evidence from checkout toggles with legacy_alias trace shape.', 'Current upstream validation state is clean and ambiguity focus is naming collision.', 'Primary risk under review is false certainty; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for routing.repository_035.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: registry_index is the portable name even when legacy query_index shows up in older notes.', 'Note 2: advisory prose must remain safely ignorable by canonical writers.', 'Note 3: AI Annotator may summarize conflicts, but cannot resolve ownership boundaries.', 'Note 4: installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti.', 'Note 5: annotation_index is lookup sugar for advice, not a second registry throne.']
REVIEW_NOTES = ['registry_index is the portable name even when legacy query_index shows up in older notes', 'advisory prose must remain safely ignorable by canonical writers', 'AI Annotator may summarize conflicts, but cannot resolve ownership boundaries', 'installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti', 'annotation_index is lookup sugar for advice, not a second registry throne']

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
