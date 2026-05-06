
"""Checkout service advisory case 036.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_amb_036'
FAMILY = 'ambiguity_cases'
TITLE = 'Checkout service advisory case 036'
TARGET_MODULE = 'checkout.service_036'

UPSTREAM_STATE = {
    "module_name": 'checkout.service_036',
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
PATH_EXAMPLES = ['reports/annotations/ann_amb_036_annotations.json', 'reports_real/annotations/ann_amb_036_do_not_write.json', 'reports/registries/ann_amb_036_must_not_exist.json']
EVIDENCE_LINES = ['Flags evidence from catalog caching with legacy_alias trace shape.', 'Current upstream validation state is warning and ambiguity focus is late validation note.', 'Primary risk under review is legacy alias confusion; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for checkout.service_036.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti.', 'Note 2: reports_real is treated as safe-ignore runtime exhaust, not evidence input.', 'Note 3: annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay.', 'Note 4: annotation_index is lookup sugar for advice, not a second registry throne.', 'Note 5: advisory prose must remain safely ignorable by canonical writers.']
REVIEW_NOTES = ['installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti', 'reports_real is treated as safe-ignore runtime exhaust, not evidence input', 'annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay', 'annotation_index is lookup sugar for advice, not a second registry throne', 'advisory prose must remain safely ignorable by canonical writers']

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
