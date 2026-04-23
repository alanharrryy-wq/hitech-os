
"""Checkout service advisory case 024.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_adv_024'
FAMILY = 'advisory_cases'
TITLE = 'Checkout service advisory case 024'
TARGET_MODULE = 'checkout.service_024'

UPSTREAM_STATE = {
    "module_name": 'checkout.service_024',
    "module_status": 'canonical',
    "validation_state": 'ambiguous',
    "switch_trace_shape": 'single_source',
    "ambiguity_focus": 'naming collision',
    "domain": 'search ranking',
    "legacy_index_reference": 'query_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'medium',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Highlights evidence from search ranking with single_source trace shape. Current upstream validation state is ambiguous and ambiguity focus is naming collision. Primary risk under review is false certainty; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json']
PATH_EXAMPLES = ['reports/annotations/ann_adv_024_annotations.json', 'reports_real/annotations/ann_adv_024_do_not_write.json', 'reports/registries/ann_adv_024_must_not_exist.json']
EVIDENCE_LINES = ['Highlights evidence from search ranking with single_source trace shape.', 'Current upstream validation state is ambiguous and ambiguity focus is naming collision.', 'Primary risk under review is false certainty; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for checkout.service_024.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: upstream gate outcome is evidence, never a thing to overwrite.', 'Note 2: switch traces may be cited but never rewritten by annotations.', 'Note 3: installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti.', 'Note 4: AI Annotator may summarize conflicts, but cannot resolve ownership boundaries.', 'Note 5: annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay.']
REVIEW_NOTES = ['upstream gate outcome is evidence, never a thing to overwrite', 'switch traces may be cited but never rewritten by annotations', 'installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti', 'AI Annotator may summarize conflicts, but cannot resolve ownership boundaries', 'annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay']

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
