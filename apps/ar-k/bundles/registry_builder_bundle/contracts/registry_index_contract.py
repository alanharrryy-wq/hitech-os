from __future__ import annotations

"""Python-first contract for registry_index.json entries."""

from typing import Iterable

REGISTRY_INDEX_FILE = "registry_index.json"
REQUIRED_FIELDS = (
    "index_id",
    "entity_type",
    "entity_id",
    "lookup_keys",
    "registry_source",
    "snapshot_id",
    "updated_at",
)
OWNER = "registry_builder"
REGISTRY_SOURCES = {"module_registry", "boundary_registry"}


def validate_entry(entry: dict) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"missing:{field}")
    if entry.get("registry_source") not in REGISTRY_SOURCES:
        errors.append("invalid:registry_source")
    lookup_keys = entry.get("lookup_keys", [])
    if not isinstance(lookup_keys, list) or not lookup_keys:
        errors.append("invalid:lookup_keys")
    if not str(entry.get("index_id", "")).startswith("idx_"):
        errors.append("invalid:index_id")
    return errors


def validate_document(entries: Iterable[dict]) -> list[str]:
    findings: list[str] = []
    for idx, entry in enumerate(entries):
        findings.extend(f"entry[{idx}]::{code}" for code in validate_entry(entry))
    return findings
