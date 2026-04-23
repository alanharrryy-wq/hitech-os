
"""Checkout service advisory case 048.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_amb_048'
FAMILY = 'ambiguity_cases'
TITLE = 'Checkout service advisory case 048'
TARGET_MODULE = 'checkout.service_048'

UPSTREAM_STATE = {
    "module_name": 'checkout.service_048',
    "module_status": 'candidate',
    "validation_state": 'gate_hold',
    "switch_trace_shape": 'legacy_alias',
    "ambiguity_focus": 'late validation note',
    "domain": 'identity linking',
    "legacy_index_reference": 'query_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'low',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Flags evidence from identity linking with legacy_alias trace shape. Current upstream validation state is gate_hold and ambiguity focus is late validation note. Primary risk under review is legacy alias confusion; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'pretend uncertainty is resolved upstream']
PATH_EXAMPLES = ['reports/annotations/ann_amb_048_annotations.json', 'reports_real/annotations/ann_amb_048_do_not_write.json', 'reports/registries/ann_amb_048_must_not_exist.json']
EVIDENCE_LINES = ['Flags evidence from identity linking with legacy_alias trace shape.', 'Current upstream validation state is gate_hold and ambiguity focus is late validation note.', 'Primary risk under review is legacy alias confusion; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for checkout.service_048.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: bundle verify may emit sample JSON, while shipped corpus stays Python-first.', 'Note 2: AI Annotator may summarize conflicts, but cannot resolve ownership boundaries.', 'Note 3: reports_real is treated as safe-ignore runtime exhaust, not evidence input.', 'Note 4: annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay.', 'Note 5: installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti.']
REVIEW_NOTES = ['bundle verify may emit sample JSON, while shipped corpus stays Python-first', 'AI Annotator may summarize conflicts, but cannot resolve ownership boundaries', 'reports_real is treated as safe-ignore runtime exhaust, not evidence input', 'annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay', 'installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti']

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
