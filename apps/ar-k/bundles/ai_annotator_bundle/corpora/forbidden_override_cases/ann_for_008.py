
"""Catalog repository advisory case 008.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_for_008'
FAMILY = 'forbidden_override_cases'
TITLE = 'Catalog repository advisory case 008'
TARGET_MODULE = 'catalog.repository_008'

UPSTREAM_STATE = {
    "module_name": 'catalog.repository_008',
    "module_status": 'candidate',
    "validation_state": 'gate_hold',
    "switch_trace_shape": 'single_source',
    "ambiguity_focus": 'naming collision',
    "domain": 'identity linking',
    "legacy_index_reference": 'query_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'reviewed',
    "confidence_band": 'low',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Highlights evidence from identity linking with single_source trace shape. Current upstream validation state is gate_hold and ambiguity focus is naming collision. Primary risk under review is false certainty; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'emit authoritative mode annotations']
PATH_EXAMPLES = ['reports/annotations/ann_for_008_annotations.json', 'reports_real/annotations/ann_for_008_do_not_write.json', 'reports/registries/ann_for_008_must_not_exist.json']
EVIDENCE_LINES = ['Highlights evidence from identity linking with single_source trace shape.', 'Current upstream validation state is gate_hold and ambiguity focus is naming collision.', 'Primary risk under review is false certainty; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for catalog.repository_008.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti.', 'Note 2: advisory prose must remain safely ignorable by canonical writers.', 'Note 3: AI Annotator may summarize conflicts, but cannot resolve ownership boundaries.', 'Note 4: registry_index is the portable name even when legacy query_index shows up in older notes.', 'Note 5: bundle verify may emit sample JSON, while shipped corpus stays Python-first.']
REVIEW_NOTES = ['installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti', 'advisory prose must remain safely ignorable by canonical writers', 'AI Annotator may summarize conflicts, but cannot resolve ownership boundaries', 'registry_index is the portable name even when legacy query_index shows up in older notes', 'bundle verify may emit sample JSON, while shipped corpus stays Python-first']

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
