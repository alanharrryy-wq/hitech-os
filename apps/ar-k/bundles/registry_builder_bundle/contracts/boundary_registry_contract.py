from __future__ import annotations

"""Python-first contract for boundary_registry.json entries."""

from typing import Iterable

BOUNDARY_REGISTRY_FILE = "boundary_registry.json"
REQUIRED_FIELDS = (
    "boundary_id",
    "source_module_id",
    "target_id",
    "target_type",
    "boundary_type",
    "status",
    "source_of_truth",
    "evidence",
    "updated_at",
)
OWNER = "registry_builder"
TARGET_TYPES = {"module", "external"}


def validate_entry(entry: dict) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"missing:{field}")
    if entry.get("target_type") not in TARGET_TYPES:
        errors.append("invalid:target_type")
    if entry.get("status") != "canonical":
        errors.append("invalid:status")
    if entry.get("source_of_truth") != "scanner.signals":
        errors.append("invalid:source_of_truth")
    if not str(entry.get("boundary_id", "")).startswith("bnd_"):
        errors.append("invalid:boundary_id")
    return errors


def validate_document(entries: Iterable[dict]) -> list[str]:
    findings: list[str] = []
    for idx, entry in enumerate(entries):
        findings.extend(f"entry[{idx}]::{code}" for code in validate_entry(entry))
    return findings
