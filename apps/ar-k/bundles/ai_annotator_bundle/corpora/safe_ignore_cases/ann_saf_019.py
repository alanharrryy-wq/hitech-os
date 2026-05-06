
"""Catalog rule_set advisory case 019.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_saf_019'
FAMILY = 'safe_ignore_cases'
TITLE = 'Catalog rule_set advisory case 019'
TARGET_MODULE = 'catalog.rule_set_019'

UPSTREAM_STATE = {
    "module_name": 'catalog.rule_set_019',
    "module_status": 'candidate',
    "validation_state": 'ambiguous',
    "switch_trace_shape": 'boundary_dense',
    "ambiguity_focus": 'shadow import',
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
    "summary_seed": 'Highlights evidence from search ranking with boundary_dense trace shape. Current upstream validation state is ambiguous and ambiguity focus is shadow import. Primary risk under review is gate override temptation; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'treat reports_real evidence as canonical input']
PATH_EXAMPLES = ['reports/annotations/ann_saf_019_annotations.json', 'reports_real/annotations/ann_saf_019_do_not_write.json', 'reports/registries/ann_saf_019_must_not_exist.json']
EVIDENCE_LINES = ['Highlights evidence from search ranking with boundary_dense trace shape.', 'Current upstream validation state is ambiguous and ambiguity focus is shadow import.', 'Primary risk under review is gate override temptation; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for catalog.rule_set_019.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: upstream gate outcome is evidence, never a thing to overwrite.', 'Note 2: switch traces may be cited but never rewritten by annotations.', 'Note 3: annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay.', 'Note 4: reports_real is treated as safe-ignore runtime exhaust, not evidence input.', 'Note 5: bundle verify may emit sample JSON, while shipped corpus stays Python-first.']
REVIEW_NOTES = ['upstream gate outcome is evidence, never a thing to overwrite', 'switch traces may be cited but never rewritten by annotations', 'annotation confidence must reflect uncertainty instead of performing bureaucratic cosplay', 'reports_real is treated as safe-ignore runtime exhaust, not evidence input', 'bundle verify may emit sample JSON, while shipped corpus stays Python-first']

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
