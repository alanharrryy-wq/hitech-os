
"""System map and homologation decisions for the AI Annotator bundle."""

from __future__ import annotations

SYSTEM_MAP = {
    "stage": "stage_05_ai_annotate",
    "purpose": "Generate advisory-only annotations from already-authoritative evidence.",
    "reads": [
        "module_registry.json",
        "boundary_registry.json",
        "registry_index.json",
        "switch_decision_registry.json",
        "switch_decision_trace.json",
        "validation_report.json",
        "gate_decisions.json",
    ],
    "writes": [
        "annotations.json",
        "annotation_index.json",
        "annotation_summary.json",
    ],
    "forbidden_writes": [
        "module_registry.json",
        "boundary_registry.json",
        "registry_index.json",
        "switch_decision_registry.json",
        "switch_decision_trace.json",
        "validation_report.json",
        "gate_decisions.json",
    ],
    "dependencies": [
        "scanner observations already promoted or rejected upstream",
        "registry_builder canonical registries",
        "switch_engine deterministic decisions and traces",
        "contract_validator report and gate outcomes",
    ],
}

HOMOLOGATION_DECISIONS = [
    {
        "legacy_divergence": "installer roots varied between deliveries, payload roots, and ad-hoc delivery folders",
        "normalized_to": "<root>/bundles/ai_annotator_bundle",
    },
    {
        "legacy_divergence": "installer state files floated between global .ark_install roots and bundle-local scratch paths",
        "normalized_to": "<root>/.ark_install/ai_annotator_bundle/",
    },
    {
        "legacy_divergence": "some deliveries required external payload arguments or separate staging folders",
        "normalized_to": "self-contained unzip-and-run installer with no payload argument",
    },
    {
        "legacy_divergence": "bundle layouts mixed payload/, docs/, and delivery-specific wrappers",
        "normalized_to": "exactly one top-level directory named ark_ai_annotator_bundle/",
    },
    {
        "legacy_divergence": "status wording drifted between READY and other handoff phrases",
        "normalized_to": "READY FOR HANDOFF",
    },
    {
        "legacy_divergence": "legacy query_index naming leaked into bundles without a compatibility fence",
        "normalized_to": "registry_index.json as canon with explicit query_index.json shim only where needed",
    },
    {
        "legacy_divergence": "advisory language was sometimes mixed with authoritative output semantics",
        "normalized_to": "annotation artifacts only, with executable checks preventing promotion and overrides",
    },
]
