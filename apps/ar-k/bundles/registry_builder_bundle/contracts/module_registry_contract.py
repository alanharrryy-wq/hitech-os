from __future__ import annotations

"""Python-first contract for module_registry.json entries."""

from typing import Iterable

MODULE_REGISTRY_FILE = "module_registry.json"
REQUIRED_FIELDS = (
    "module_id",
    "name",
    "kind",
    "area",
    "status",
    "source_of_truth",
    "observed_in",
    "declared_by",
    "boundaries",
    "switches",
    "updated_at",
)
ALLOWED_STATUS = {"canonical", "candidate", "superseded"}
OWNER = "registry_builder"


def validate_entry(entry: dict) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"missing:{field}")
    if entry.get("status") not in ALLOWED_STATUS:
        errors.append("invalid:status")
    if entry.get("source_of_truth") != "scanner.signals":
        errors.append("invalid:source_of_truth")
    if entry.get("declared_by") != [OWNER]:
        errors.append("invalid:declared_by")
    observed_in = entry.get("observed_in", [])
    if not isinstance(observed_in, list) or not observed_in:
        errors.append("invalid:observed_in")
    if not str(entry.get("module_id", "")).startswith("mod_"):
        errors.append("invalid:module_id")
    return errors


def validate_document(entries: Iterable[dict]) -> list[str]:
    findings: list[str] = []
    for idx, entry in enumerate(entries):
        findings.extend(f"entry[{idx}]::{code}" for code in validate_entry(entry))
    return findings
