from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .contracts import ContractError, require_nonempty_string


_ALLOWED_CODES = {
    "CONTRADICTORY_EVIDENCE",
    "DECLARED_UNKNOWN",
    "NEW_UNKNOWN",
    "PACK_UNKNOWN",
    "REQUIRED_EVIDENCE_UNKNOWN",
    "UNSUPPORTED_PRIMARY_TARGET",
}

_DEFAULT_NEXT_EVIDENCE = {
    "CONTRADICTORY_EVIDENCE": "Provide reconciled evidence or an authoritative adjudication that resolves the contradiction.",
    "DECLARED_UNKNOWN": "Provide repository or external evidence that resolves the declared unknown.",
    "NEW_UNKNOWN": "Provide fresh evidence that resolves the newly observed unknown before claiming PASS.",
    "PACK_UNKNOWN": "Resolve the authority-pack unknown with evidence bound to the same repository snapshot before claiming PASS.",
    "REQUIRED_EVIDENCE_UNKNOWN": "Provide the required evidence with a supported or blocking state instead of UNKNOWN.",
    "UNSUPPORTED_PRIMARY_TARGET": "Provide repository evidence references that support the target, or remove it from the proposed primary targets.",
}


def build_unknown_obligation(
    *,
    code: str,
    source: str,
    reason: str,
    subject: str | None = None,
    next_evidence: str | None = None,
) -> dict[str, Any]:
    normalized_code = require_nonempty_string(code, "code").upper()
    if normalized_code not in _ALLOWED_CODES:
        raise ContractError(f"unsupported unknown obligation code: {normalized_code}")
    normalized_source = require_nonempty_string(source, "source")
    normalized_reason = require_nonempty_string(reason, "reason")
    normalized_subject = subject.strip() if isinstance(subject, str) and subject.strip() else None
    normalized_next = (
        next_evidence.strip()
        if isinstance(next_evidence, str) and next_evidence.strip()
        else _DEFAULT_NEXT_EVIDENCE[normalized_code]
    )
    row: dict[str, Any] = {
        "code": normalized_code,
        "source": normalized_source,
        "reason": normalized_reason,
        "nextEvidence": normalized_next,
    }
    if normalized_subject is not None:
        row["subject"] = normalized_subject
    return row


def normalize_unknown_obligations(rows: list[Mapping[str, Any]] | None) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str, str]] = set()
    for index, raw in enumerate(rows or []):
        if not isinstance(raw, Mapping):
            raise ContractError(f"unknown_obligations[{index}] must be an object")
        row = build_unknown_obligation(
            code=str(raw.get("code", "")),
            source=str(raw.get("source", "")),
            reason=str(raw.get("reason", "")),
            subject=raw.get("subject") if isinstance(raw.get("subject"), str) else None,
            next_evidence=raw.get("nextEvidence") if isinstance(raw.get("nextEvidence"), str) else None,
        )
        key = (
            row["code"],
            row["source"],
            str(row.get("subject") or ""),
            row["reason"],
            row["nextEvidence"],
        )
        if key in seen:
            continue
        seen.add(key)
        normalized.append(deepcopy(row))
    return sorted(
        normalized,
        key=lambda row: (
            row["code"],
            row["source"],
            str(row.get("subject") or ""),
            row["reason"],
            row["nextEvidence"],
        ),
    )


__all__ = ["build_unknown_obligation", "normalize_unknown_obligations"]
