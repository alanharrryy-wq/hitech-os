
"""Ops client advisory case 016.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_for_016'
FAMILY = 'forbidden_override_cases'
TITLE = 'Ops client advisory case 016'
TARGET_MODULE = 'ops.client_016'

UPSTREAM_STATE = {
    "module_name": 'ops.client_016',
    "module_status": 'candidate',
    "validation_state": 'warning',
    "switch_trace_shape": 'single_source',
    "ambiguity_focus": 'naming collision',
    "domain": 'catalog caching',
    "legacy_index_reference": 'query_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'reviewed',
    "confidence_band": 'low',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Highlights evidence from catalog caching with single_source trace shape. Current upstream validation state is warning and ambiguity focus is naming collision. Primary risk under review is false certainty; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'emit authoritative mode annotations']
PATH_EXAMPLES = ['reports/annotations/ann_for_016_annotations.json', 'reports_real/annotations/ann_for_016_do_not_write.json', 'reports/registries/ann_for_016_must_not_exist.json']
EVIDENCE_LINES = ['Highlights evidence from catalog caching with single_source trace shape.', 'Current upstream validation state is warning and ambiguity focus is naming collision.', 'Primary risk under review is false certainty; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for ops.client_016.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: upstream gate outcome is evidence, never a thing to overwrite.', 'Note 2: reports_real is treated as safe-ignore runtime exhaust, not evidence input.', 'Note 3: bundle verify may emit sample JSON, while shipped corpus stays Python-first.', 'Note 4: annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay.', 'Note 5: switch traces may be cited but never rewritten by annotations.']
REVIEW_NOTES = ['upstream gate outcome is evidence, never a thing to overwrite', 'reports_real is treated as safe-ignore runtime exhaust, not evidence input', 'bundle verify may emit sample JSON, while shipped corpus stays Python-first', 'annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay', 'switch traces may be cited but never rewritten by annotations']

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
