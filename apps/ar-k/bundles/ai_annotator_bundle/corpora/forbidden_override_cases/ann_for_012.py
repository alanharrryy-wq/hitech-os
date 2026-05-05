
"""Checkout service advisory case 012.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_for_012'
FAMILY = 'forbidden_override_cases'
TITLE = 'Checkout service advisory case 012'
TARGET_MODULE = 'checkout.service_012'

UPSTREAM_STATE = {
    "module_name": 'checkout.service_012',
    "module_status": 'candidate',
    "validation_state": 'error_shadow',
    "switch_trace_shape": 'single_source',
    "ambiguity_focus": 'naming collision',
    "domain": 'ops runbooks',
    "legacy_index_reference": 'query_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'reviewed',
    "confidence_band": 'low',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Highlights evidence from ops runbooks with single_source trace shape. Current upstream validation state is error_shadow and ambiguity focus is naming collision. Primary risk under review is false certainty; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'emit authoritative mode annotations']
PATH_EXAMPLES = ['reports/annotations/ann_for_012_annotations.json', 'reports_real/annotations/ann_for_012_do_not_write.json', 'reports/registries/ann_for_012_must_not_exist.json']
EVIDENCE_LINES = ['Highlights evidence from ops runbooks with single_source trace shape.', 'Current upstream validation state is error_shadow and ambiguity focus is naming collision.', 'Primary risk under review is false certainty; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for checkout.service_012.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: registry_index is the portable name even when legacy query_index shows up in older notes.', 'Note 2: AI Annotator may summarize conflicts, but cannot resolve ownership boundaries.', 'Note 3: annotation_index is lookup sugar for advice, not a second registry throne.', 'Note 4: installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti.', 'Note 5: advisory prose must remain safely ignorable by canonical writers.']
REVIEW_NOTES = ['registry_index is the portable name even when legacy query_index shows up in older notes', 'AI Annotator may summarize conflicts, but cannot resolve ownership boundaries', 'annotation_index is lookup sugar for advice, not a second registry throne', 'installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti', 'advisory prose must remain safely ignorable by canonical writers']

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
