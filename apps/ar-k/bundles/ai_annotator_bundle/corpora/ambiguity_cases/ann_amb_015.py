
"""Search service advisory case 015.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_amb_015'
FAMILY = 'ambiguity_cases'
TITLE = 'Search service advisory case 015'
TARGET_MODULE = 'search.service_015'

UPSTREAM_STATE = {
    "module_name": 'search.service_015',
    "module_status": 'candidate',
    "validation_state": 'clean',
    "switch_trace_shape": 'legacy_alias',
    "ambiguity_focus": 'naming collision',
    "domain": 'checkout toggles',
    "legacy_index_reference": 'registry_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'low',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Records evidence from checkout toggles with legacy_alias trace shape. Current upstream validation state is clean and ambiguity focus is naming collision. Primary risk under review is false certainty; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'pretend uncertainty is resolved upstream']
PATH_EXAMPLES = ['reports/annotations/ann_amb_015_annotations.json', 'reports_real/annotations/ann_amb_015_do_not_write.json', 'reports/registries/ann_amb_015_must_not_exist.json']
EVIDENCE_LINES = ['Records evidence from checkout toggles with legacy_alias trace shape.', 'Current upstream validation state is clean and ambiguity focus is naming collision.', 'Primary risk under review is false certainty; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for search.service_015.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: upstream gate outcome is evidence, never a thing to overwrite.', 'Note 2: AI Annotator may summarize conflicts, but cannot resolve ownership boundaries.', 'Note 3: registry_index is the portable name even when legacy query_index shows up in older notes.', 'Note 4: advisory prose must remain safely ignorable by canonical writers.', 'Note 5: installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti.']
REVIEW_NOTES = ['upstream gate outcome is evidence, never a thing to overwrite', 'AI Annotator may summarize conflicts, but cannot resolve ownership boundaries', 'registry_index is the portable name even when legacy query_index shows up in older notes', 'advisory prose must remain safely ignorable by canonical writers', 'installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti']

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
