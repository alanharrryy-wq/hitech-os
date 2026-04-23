
"""Catalog repository advisory case 032.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_adv_032'
FAMILY = 'advisory_cases'
TITLE = 'Catalog repository advisory case 032'
TARGET_MODULE = 'catalog.repository_032'

UPSTREAM_STATE = {
    "module_name": 'catalog.repository_032',
    "module_status": 'canonical',
    "validation_state": 'error_shadow',
    "switch_trace_shape": 'single_source',
    "ambiguity_focus": 'naming collision',
    "domain": 'ops runbooks',
    "legacy_index_reference": 'query_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'medium',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Highlights evidence from ops runbooks with single_source trace shape. Current upstream validation state is error_shadow and ambiguity focus is naming collision. Primary risk under review is false certainty; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json']
PATH_EXAMPLES = ['reports/annotations/ann_adv_032_annotations.json', 'reports_real/annotations/ann_adv_032_do_not_write.json', 'reports/registries/ann_adv_032_must_not_exist.json']
EVIDENCE_LINES = ['Highlights evidence from ops runbooks with single_source trace shape.', 'Current upstream validation state is error_shadow and ambiguity focus is naming collision.', 'Primary risk under review is false certainty; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for catalog.repository_032.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti.', 'Note 2: annotation_index is lookup sugar for advice, not a second registry throne.', 'Note 3: advisory prose must remain safely ignorable by canonical writers.', 'Note 4: registry_index is the portable name even when legacy query_index shows up in older notes.', 'Note 5: switch traces may be cited but never rewritten by annotations.']
REVIEW_NOTES = ['installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti', 'annotation_index is lookup sugar for advice, not a second registry throne', 'advisory prose must remain safely ignorable by canonical writers', 'registry_index is the portable name even when legacy query_index shows up in older notes', 'switch traces may be cited but never rewritten by annotations']

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
