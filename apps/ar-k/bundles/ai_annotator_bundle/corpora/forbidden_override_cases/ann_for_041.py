
"""Routing repository advisory case 041.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_for_041'
FAMILY = 'forbidden_override_cases'
TITLE = 'Routing repository advisory case 041'
TARGET_MODULE = 'routing.repository_041'

UPSTREAM_STATE = {
    "module_name": 'routing.repository_041',
    "module_status": 'candidate',
    "validation_state": 'warning',
    "switch_trace_shape": 'single_source',
    "ambiguity_focus": 'late validation note',
    "domain": 'catalog caching',
    "legacy_index_reference": 'registry_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'reviewed',
    "confidence_band": 'low',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Records evidence from catalog caching with single_source trace shape. Current upstream validation state is warning and ambiguity focus is late validation note. Primary risk under review is legacy alias confusion; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'emit authoritative mode annotations']
PATH_EXAMPLES = ['reports/annotations/ann_for_041_annotations.json', 'reports_real/annotations/ann_for_041_do_not_write.json', 'reports/registries/ann_for_041_must_not_exist.json']
EVIDENCE_LINES = ['Records evidence from catalog caching with single_source trace shape.', 'Current upstream validation state is warning and ambiguity focus is late validation note.', 'Primary risk under review is legacy alias confusion; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for routing.repository_041.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: bundle verify may emit sample JSON, while shipped corpus stays Python-first.', 'Note 2: registry_index is the portable name even when legacy query_index shows up in older notes.', 'Note 3: installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti.', 'Note 4: advisory prose must remain safely ignorable by canonical writers.', 'Note 5: upstream gate outcome is evidence, never a thing to overwrite.']
REVIEW_NOTES = ['bundle verify may emit sample JSON, while shipped corpus stays Python-first', 'registry_index is the portable name even when legacy query_index shows up in older notes', 'installer state is isolated beneath .ark_install/ai_annotator_bundle to avoid cross-tool spaghetti', 'advisory prose must remain safely ignorable by canonical writers', 'upstream gate outcome is evidence, never a thing to overwrite']

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
