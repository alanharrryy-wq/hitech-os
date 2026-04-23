
"""Identity client advisory case 019.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_adv_019'
FAMILY = 'advisory_cases'
TITLE = 'Identity client advisory case 019'
TARGET_MODULE = 'identity.client_019'

UPSTREAM_STATE = {
    "module_name": 'identity.client_019',
    "module_status": 'canonical',
    "validation_state": 'ambiguous',
    "switch_trace_shape": 'single_source',
    "ambiguity_focus": 'late validation note',
    "domain": 'search ranking',
    "legacy_index_reference": 'registry_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'medium',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Captures evidence from search ranking with single_source trace shape. Current upstream validation state is ambiguous and ambiguity focus is late validation note. Primary risk under review is legacy alias confusion; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json']
PATH_EXAMPLES = ['reports/annotations/ann_adv_019_annotations.json', 'reports_real/annotations/ann_adv_019_do_not_write.json', 'reports/registries/ann_adv_019_must_not_exist.json']
EVIDENCE_LINES = ['Captures evidence from search ranking with single_source trace shape.', 'Current upstream validation state is ambiguous and ambiguity focus is late validation note.', 'Primary risk under review is legacy alias confusion; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for identity.client_019.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: upstream gate outcome is evidence, never a thing to overwrite.', 'Note 2: reports_real is treated as safe-ignore runtime exhaust, not evidence input.', 'Note 3: annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay.', 'Note 4: annotation_index is lookup sugar for advice, not a second registry throne.', 'Note 5: bundle verify may emit sample JSON, while shipped corpus stays Python-first.']
REVIEW_NOTES = ['upstream gate outcome is evidence, never a thing to overwrite', 'reports_real is treated as safe-ignore runtime exhaust, not evidence input', 'annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay', 'annotation_index is lookup sugar for advice, not a second registry throne', 'bundle verify may emit sample JSON, while shipped corpus stays Python-first']

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
