# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Payload contract validators."""
from __future__ import annotations
from typing import Any

REQUIRED_ENVELOPE_KEYS = {"ok", "read_only", "mutation_allowed"}


def validate_read_only_envelope(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    for key in REQUIRED_ENVELOPE_KEYS:
        if key not in payload:
            errors.append(f"missing:{key}")
    if payload.get("read_only") is not True:
        errors.append("read_only_must_be_true")
    if payload.get("mutation_allowed") is not False:
        errors.append("mutation_allowed_must_be_false")
    return not errors, errors


def contract_summary() -> dict[str, Any]:
    return {"schema_version": "1.0.0", "required_envelope_keys": sorted(REQUIRED_ENVELOPE_KEYS), "read_only_required": True}
