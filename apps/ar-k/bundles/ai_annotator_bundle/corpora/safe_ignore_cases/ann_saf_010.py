
"""Routing rule_set advisory case 010.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_saf_010'
FAMILY = 'safe_ignore_cases'
TITLE = 'Routing rule_set advisory case 010'
TARGET_MODULE = 'routing.rule_set_010'

UPSTREAM_STATE = {
    "module_name": 'routing.rule_set_010',
    "module_status": 'candidate',
    "validation_state": 'clean',
    "switch_trace_shape": 'boundary_dense',
    "ambiguity_focus": 'boundary echo',
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
    "summary_seed": 'Captures evidence from checkout toggles with boundary_dense trace shape. Current upstream validation state is clean and ambiguity focus is boundary echo. Primary risk under review is write-scope creep; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'treat reports_real evidence as canonical input']
PATH_EXAMPLES = ['reports/annotations/ann_saf_010_annotations.json', 'reports_real/annotations/ann_saf_010_do_not_write.json', 'reports/registries/ann_saf_010_must_not_exist.json']
EVIDENCE_LINES = ['Captures evidence from checkout toggles with boundary_dense trace shape.', 'Current upstream validation state is clean and ambiguity focus is boundary echo.', 'Primary risk under review is write-scope creep; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for routing.rule_set_010.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: upstream gate outcome is evidence, never a thing to overwrite.', 'Note 2: advisory prose must remain safely ignorable by canonical writers.', 'Note 3: switch traces may be cited but never rewritten by annotations.', 'Note 4: AI Annotator may summarize conflicts, but cannot resolve ownership boundaries.', 'Note 5: bundle verify may emit sample JSON, while shipped corpus stays Python-first.']
REVIEW_NOTES = ['upstream gate outcome is evidence, never a thing to overwrite', 'advisory prose must remain safely ignorable by canonical writers', 'switch traces may be cited but never rewritten by annotations', 'AI Annotator may summarize conflicts, but cannot resolve ownership boundaries', 'bundle verify may emit sample JSON, while shipped corpus stays Python-first']

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
