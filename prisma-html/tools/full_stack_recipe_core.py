#!/usr/bin/env python3
"""Core helpers for registry-driven, instruction-only full-stack recipes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ROOT / "authority" / "rifat" / "identity"
CANONICALIZATION = "json-sort-keys-compact-utf8-v1"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def checksum(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def covered_payload(value: dict[str, Any], excluded: tuple[str, ...] = ("integrity",)) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key not in excluded}


def verify_integrity(value: dict[str, Any], excluded: tuple[str, ...] = ("integrity",)) -> list[str]:
    errors: list[str] = []
    integrity = value.get("integrity")
    if not isinstance(integrity, dict):
        return ["integrity block missing"]
    if integrity.get("algorithm") != "SHA-256":
        errors.append("integrity algorithm must be SHA-256")
    if integrity.get("canonicalization") != CANONICALIZATION:
        errors.append("canonicalization mismatch")
    expected = checksum(covered_payload(value, excluded))
    if integrity.get("canonicalPayloadSha256") != expected:
        errors.append(
            "checksum mismatch: "
            f"expected {expected}, got {integrity.get('canonicalPayloadSha256')}"
        )
    return errors


def registry_record(registry: dict[str, Any], recipe_id: str) -> dict[str, Any]:
    matches = [row for row in registry.get("recipes", []) if row.get("recipeId") == recipe_id]
    if len(matches) != 1:
        raise ValueError(f"Recipe registry cardinality for {recipe_id}: {len(matches)}")
    return matches[0]


def recipe_units(recipe: dict[str, Any]) -> dict[str, dict[str, Any]]:
    units = recipe.get("visualStack", {}).get("units", [])
    result: dict[str, dict[str, Any]] = {}
    for unit in units:
        unit_id = unit.get("unitId")
        if not isinstance(unit_id, str) or unit_id in result:
            raise ValueError(f"Invalid or duplicate unitId: {unit_id}")
        result[unit_id] = unit
    return result


def resolved_property_names(unit: dict[str, Any]) -> set[str]:
    values = unit.get("properties") or {}
    return set(values)


def round_trip(value: dict[str, Any]) -> dict[str, Any]:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return json.loads(encoded)
