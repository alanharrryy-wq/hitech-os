
"""Catalog repository advisory case 050.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_adv_050'
FAMILY = 'advisory_cases'
TITLE = 'Catalog repository advisory case 050'
TARGET_MODULE = 'catalog.repository_050'

UPSTREAM_STATE = {
    "module_name": 'catalog.repository_050',
    "module_status": 'canonical',
    "validation_state": 'clean',
    "switch_trace_shape": 'single_source',
    "ambiguity_focus": 'naming collision',
    "domain": 'checkout toggles',
    "legacy_index_reference": 'registry_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'medium',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Flags evidence from checkout toggles with single_source trace shape. Current upstream validation state is clean and ambiguity focus is naming collision. Primary risk under review is false certainty; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json']
PATH_EXAMPLES = ['reports/annotations/ann_adv_050_annotations.json', 'reports_real/annotations/ann_adv_050_do_not_write.json', 'reports/registries/ann_adv_050_must_not_exist.json']
EVIDENCE_LINES = ['Flags evidence from checkout toggles with single_source trace shape.', 'Current upstream validation state is clean and ambiguity focus is naming collision.', 'Primary risk under review is false certainty; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for catalog.repository_050.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti.', 'Note 2: bundle verify may emit sample JSON, while shipped corpus stays Python-first.', 'Note 3: switch traces may be cited but never rewritten by annotations.', 'Note 4: reports_real is treated as safe-ignore runtime exhaust, not evidence input.', 'Note 5: upstream gate outcome is evidence, never a thing to overwrite.']
REVIEW_NOTES = ['installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti', 'bundle verify may emit sample JSON, while shipped corpus stays Python-first', 'switch traces may be cited but never rewritten by annotations', 'reports_real is treated as safe-ignore runtime exhaust, not evidence input', 'upstream gate outcome is evidence, never a thing to overwrite']

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
