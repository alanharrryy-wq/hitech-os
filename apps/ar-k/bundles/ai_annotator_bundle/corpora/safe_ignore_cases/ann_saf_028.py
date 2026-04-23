
"""Routing rule_set advisory case 028.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_saf_028'
FAMILY = 'safe_ignore_cases'
TITLE = 'Routing rule_set advisory case 028'
TARGET_MODULE = 'routing.rule_set_028'

UPSTREAM_STATE = {
    "module_name": 'routing.rule_set_028',
    "module_status": 'candidate',
    "validation_state": 'gate_hold',
    "switch_trace_shape": 'boundary_dense',
    "ambiguity_focus": 'boundary echo',
    "domain": 'identity linking',
    "legacy_index_reference": 'query_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'medium',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Records evidence from identity linking with boundary_dense trace shape. Current upstream validation state is gate_hold and ambiguity focus is boundary echo. Primary risk under review is write-scope creep; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'treat reports_real evidence as canonical input']
PATH_EXAMPLES = ['reports/annotations/ann_saf_028_annotations.json', 'reports_real/annotations/ann_saf_028_do_not_write.json', 'reports/registries/ann_saf_028_must_not_exist.json']
EVIDENCE_LINES = ['Records evidence from identity linking with boundary_dense trace shape.', 'Current upstream validation state is gate_hold and ambiguity focus is boundary echo.', 'Primary risk under review is write-scope creep; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for routing.rule_set_028.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: registry_index is the portable name even when legacy query_index shows up in older notes.', 'Note 2: installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti.', 'Note 3: advisory prose must remain safely ignorable by canonical writers.', 'Note 4: annotation_index is lookup sugar for advice, not a second registry throne.', 'Note 5: reports_real is treated as safe-ignore runtime exhaust, not evidence input.']
REVIEW_NOTES = ['registry_index is the portable name even when legacy query_index shows up in older notes', 'installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti', 'advisory prose must remain safely ignorable by canonical writers', 'annotation_index is lookup sugar for advice, not a second registry throne', 'reports_real is treated as safe-ignore runtime exhaust, not evidence input']

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
