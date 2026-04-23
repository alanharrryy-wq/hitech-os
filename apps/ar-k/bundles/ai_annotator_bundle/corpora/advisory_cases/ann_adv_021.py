
"""Search service advisory case 021.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_adv_021'
FAMILY = 'advisory_cases'
TITLE = 'Search service advisory case 021'
TARGET_MODULE = 'search.service_021'

UPSTREAM_STATE = {
    "module_name": 'search.service_021',
    "module_status": 'canonical',
    "validation_state": 'warning',
    "switch_trace_shape": 'single_source',
    "ambiguity_focus": 'late validation note',
    "domain": 'catalog caching',
    "legacy_index_reference": 'registry_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'medium',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Records evidence from catalog caching with single_source trace shape. Current upstream validation state is warning and ambiguity focus is late validation note. Primary risk under review is legacy alias confusion; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json']
PATH_EXAMPLES = ['reports/annotations/ann_adv_021_annotations.json', 'reports_real/annotations/ann_adv_021_do_not_write.json', 'reports/registries/ann_adv_021_must_not_exist.json']
EVIDENCE_LINES = ['Records evidence from catalog caching with single_source trace shape.', 'Current upstream validation state is warning and ambiguity focus is late validation note.', 'Primary risk under review is legacy alias confusion; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for search.service_021.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: switch traces may be cited but never rewritten by annotations.', 'Note 2: reports_real is treated as safe-ignore runtime exhaust, not evidence input.', 'Note 3: registry_index is the portable name even when legacy query_index shows up in older notes.', 'Note 4: annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay.', 'Note 5: bundle verify may emit sample JSON, while shipped corpus stays Python-first.']
REVIEW_NOTES = ['switch traces may be cited but never rewritten by annotations', 'reports_real is treated as safe-ignore runtime exhaust, not evidence input', 'registry_index is the portable name even when legacy query_index shows up in older notes', 'annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay', 'bundle verify may emit sample JSON, while shipped corpus stays Python-first']

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
