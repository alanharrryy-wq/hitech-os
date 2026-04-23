
"""Identity client advisory case 001.

This corpus module is intentionally Python-first. It packages a realistic
annotation scenario with enough structure for tests, installers, verifiers, and
reviewers to inspect advisory semantics without shipping JSON blobs in the ZIP.
The case captures upstream evidence, ambiguity, forbidden actions, and path
examples using executable Python data.
"""

from __future__ import annotations

CASE_ID = 'ann_amb_001'
FAMILY = 'ambiguity_cases'
TITLE = 'Identity client advisory case 001'
TARGET_MODULE = 'identity.client_001'

UPSTREAM_STATE = {
    "module_name": 'identity.client_001',
    "module_status": 'candidate',
    "validation_state": 'warning',
    "switch_trace_shape": 'legacy_alias',
    "ambiguity_focus": 'naming collision',
    "domain": 'catalog caching',
    "legacy_index_reference": 'registry_index.json',
}

ADVISORY_EXPECTATION = {
    "annotation_kind": "module_advisory_summary",
    "status": 'suggested',
    "confidence_band": 'low',
    "must_cite_validator": True,
    "must_cite_switch_trace": True,
    "must_declare_advisory_only": True,
    "summary_seed": 'Captures evidence from catalog caching with legacy_alias trace shape. Current upstream validation state is warning and ambiguity focus is naming collision. Primary risk under review is false certainty; annotator remains non-authoritative.',
}

FORBIDDEN_ACTIONS = ['rewrite module_registry.json', 'change gate_decisions.json', 'flip resolved_value in switch_decision_registry.json', 'pretend uncertainty is resolved upstream']
PATH_EXAMPLES = ['reports/annotations/ann_amb_001_annotations.json', 'reports_real/annotations/ann_amb_001_do_not_write.json', 'reports/registries/ann_amb_001_must_not_exist.json']
EVIDENCE_LINES = ['Captures evidence from catalog caching with legacy_alias trace shape.', 'Current upstream validation state is warning and ambiguity focus is naming collision.', 'Primary risk under review is false certainty; annotator remains non-authoritative.', 'Legacy index alias handling maps query_index.json to registry_index.json for identity.client_001.', 'Observed paths include reports_real quarantine examples that must be ignored by policy.', 'Note 1: upstream gate outcome is evidence, never a thing to overwrite.', 'Note 2: annotation_index is lookup sugar for advice, not a second registry throne.', 'Note 3: reports_real is treated as safe-ignore runtime exhaust, not evidence input.', 'Note 4: bundle verify may emit sample JSON, while shipped corpus stays Python-first.', 'Note 5: advisory prose must remain safely ignorable by canonical writers.']
REVIEW_NOTES = ['upstream gate outcome is evidence, never a thing to overwrite', 'annotation_index is lookup sugar for advice, not a second registry throne', 'reports_real is treated as safe-ignore runtime exhaust, not evidence input', 'bundle verify may emit sample JSON, while shipped corpus stays Python-first', 'advisory prose must remain safely ignorable by canonical writers']

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
