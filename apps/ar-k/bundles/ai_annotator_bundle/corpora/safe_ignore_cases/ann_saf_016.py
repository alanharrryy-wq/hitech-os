
"""Routing rule_set advisory case 016.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_saf_016'
FAMILY = 'safe_ignore_cases'
TITLE = 'Routing rule_set advisory case 016'
TARGET_MODULE = 'routing.rule_set_016'

UPSTREAM_STATE = {
    "module_name": 'routing.rule_set_016',
    "module_status": 'candidate',
    "validation_state": 'warning',
    "switch_trace_shape": 'boundary_dense',
    "ambiguity_focus": 'boundary echo',
    "domain": 'catalog caching',
    "legacy_index_reference": 'query_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'medium',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Records evidence from catalog caching with boundary_dense trace shape. Current upstream validation state is warning and ambiguity focus is boundary echo. Primary risk under review is write-scope creep; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'treat reports_real evidence as canonical input']
PATH_EXAMPLES = ['reports/annotations/ann_saf_016_annotations.json', 'reports_real/annotations/ann_saf_016_do_not_write.json', 'reports/registries/ann_saf_016_must_not_exist.json']
EVIDENCE_LINES = ['Records evidence from catalog caching with boundary_dense trace shape.', 'Current upstream validation state is warning and ambiguity focus is boundary echo.', 'Primary risk under review is write-scope creep; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for routing.rule_set_016.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: switch traces may be cited but never rewritten by annotations.', 'Note 2: bundle verify may emit sample JSON, while shipped corpus stays Python-first.', 'Note 3: installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti.', 'Note 4: annotation_index is lookup sugar for advice, not a second registry throne.', 'Note 5: upstream gate outcome is evidence, never a thing to overwrite.']
REVIEW_NOTES = ['switch traces may be cited but never rewritten by annotations', 'bundle verify may emit sample JSON, while shipped corpus stays Python-first', 'installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti', 'annotation_index is lookup sugar for advice, not a second registry throne', 'upstream gate outcome is evidence, never a thing to overwrite']

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
