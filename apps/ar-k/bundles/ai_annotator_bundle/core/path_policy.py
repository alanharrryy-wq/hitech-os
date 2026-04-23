"""Executable path and exclusion policy for the AI Annotator bundle."""

from __future__ import annotations

from pathlib import Path

from core.bundle_constants import EXCLUDED_RELATIVE_PREFIXES


SAFE_IGNORE_EXAMPLES = [
    "reports_real/registries/module_registry.json",
    "reports_real/annotations/annotations.json",
    "reports/reports/execution_summary.json",
    ".ark_install/ai_annotator_bundle/last_apply.json",
    "build/tmp/generated_annotations.json",
]

ALLOWED_READ_EXAMPLES = [
    "reports/registries/module_registry.json",
    "reports/registries/boundary_registry.json",
    "reports/indices/registry_index.json",
    "reports/decision_trace/switch_decision_trace.json",
    "reports/validation/validation_report.json",
]

ALLOWED_WRITE_EXAMPLES = [
    "reports/annotations/annotations.json",
    "reports/annotations/annotation_index.json",
    "reports/annotations/annotation_summary.json",
]

COUNTEREXAMPLES = [
    "reports/registries/module_registry.json",
    "reports/registries/boundary_registry.json",
    "reports/validation/gate_decisions.json",
    "reports/traces/switch_decision_trace.json",
    "reports_real/annotations/annotation_summary.json",
]


def normalize_rel(path: str | Path) -> str:
    text = str(path).replace("\\", "/").lstrip("./")
    return text


def is_excluded_path(path: str | Path) -> bool:
    rel = normalize_rel(path)
    return any(rel.startswith(prefix) for prefix in EXCLUDED_RELATIVE_PREFIXES)


def path_policy_report() -> dict[str, object]:
    return {
        "excluded_prefixes": EXCLUDED_RELATIVE_PREFIXES[:],
        "safe_ignore_examples": SAFE_IGNORE_EXAMPLES[:],
        "allowed_reads": ALLOWED_READ_EXAMPLES[:],
        "allowed_writes": ALLOWED_WRITE_EXAMPLES[:],
        "counterexamples": COUNTEREXAMPLES[:],
    }
