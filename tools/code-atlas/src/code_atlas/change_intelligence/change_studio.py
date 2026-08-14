from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .contracts import ContractError, SUPPORT_LEVELS, decision_precedence, normalize_repo_path, sha256_json, utc_now_iso

_EVIDENCE_STATES = {"SATISFIED", "PENDING", "MISSING", "UNKNOWN", "CONFLICTED"}


def _normalize_target(item: Mapping[str, Any], field: str) -> dict[str, Any]:
    if not isinstance(item, Mapping):
        raise ContractError(f"{field} target must be an object")
    path = normalize_repo_path(item.get("path"))
    support = str(item.get("supportLevel", "UNKNOWN")).upper()
    if support not in SUPPORT_LEVELS:
        raise ContractError(f"invalid target supportLevel: {support}")
    refs = item.get("evidenceReferences", [])
    if not isinstance(refs, list):
        raise ContractError("target evidenceReferences must be a list")
    if support == "SUPPORTED" and not refs:
        raise ContractError("SUPPORTED target requires evidenceReferences")
    return {
        "path": path,
        "reason": str(item.get("reason", "")).strip(),
        "supportLevel": support,
        "evidenceReferences": deepcopy(refs),
    }


def compose_change_model(
    *,
    normalized_intent: str,
    repository_snapshot: Mapping[str, Any],
    primary_targets: list[Mapping[str, Any]],
    related_targets: list[Mapping[str, Any]] | None = None,
    impact_radius: Mapping[str, Any] | None = None,
    protected_scope: list[str] | None = None,
    authority_references: list[Mapping[str, Any]] | None = None,
    facts: list[Mapping[str, Any]] | None = None,
    inferences: list[Mapping[str, Any]] | None = None,
    unknowns: list[str] | None = None,
    contradictions: list[str] | None = None,
    required_evidence: list[Mapping[str, Any]] | None = None,
    blockers: list[str] | None = None,
    provenance: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    if not isinstance(repository_snapshot, Mapping):
        raise ContractError("repository_snapshot must be an object")
    for key in ("repositoryIdentity", "commitIdentity", "treeIdentity"):
        if not isinstance(repository_snapshot.get(key), str) or not repository_snapshot[key].strip():
            raise ContractError(f"repository_snapshot.{key} is required")
    if not isinstance(normalized_intent, str) or not normalized_intent.strip():
        raise ContractError("normalized_intent is required")
    if not primary_targets:
        raise ContractError("at least one primary target is required")
    if not provenance:
        raise ContractError("change model requires provenance")

    primary = [_normalize_target(item, "primary") for item in primary_targets]
    related = [_normalize_target(item, "related") for item in (related_targets or [])]
    protected = sorted({normalize_repo_path(path) for path in (protected_scope or [])})
    authorities = deepcopy(authority_references or [])
    fact_rows = deepcopy(facts or [])
    inference_rows = deepcopy(inferences or [])
    required = deepcopy(required_evidence or [])
    missing_required: list[str] = []
    for index, item in enumerate(required):
        if not isinstance(item, Mapping):
            raise ContractError(f"required_evidence[{index}] must be an object")
        evidence_id = str(item.get("id", "")).strip()
        if not evidence_id:
            raise ContractError(f"required_evidence[{index}].id is required")
        if item.get("status") not in _EVIDENCE_STATES:
            raise ContractError(f"required_evidence[{index}].status is invalid")
        if item.get("status") in {"MISSING", "CONFLICTED"}:
            missing_required.append(evidence_id)

    unsupported_primary = [row["path"] for row in primary if row["supportLevel"] in {"UNKNOWN", "CONFLICTED"}]
    blocking_items = list(blockers or [])
    if missing_required:
        blocking_items.append("required evidence missing or conflicted")

    uncertain = bool(
        unknowns
        or contradictions
        or unsupported_primary
        or any(item.get("status") == "UNKNOWN" for item in required)
    )
    decision = decision_precedence(
        "BLOCKED" if blocking_items else "PASS",
        "UNKNOWN" if uncertain else "PASS",
    )

    model = {
        "schemaVersion": "code_atlas_change_model.v1",
        "normalizedIntent": normalized_intent.strip(),
        "repositorySnapshot": dict(repository_snapshot),
        "primaryTargets": primary,
        "relatedTargets": related,
        "impactRadius": dict(impact_radius or {}),
        "protectedScope": protected,
        "ownershipAndAuthorityReferences": authorities,
        "facts": fact_rows,
        "inferences": inference_rows,
        "unknowns": list(unknowns or []),
        "contradictions": list(contradictions or []),
        "requiredEvidence": required,
        "missingRequiredEvidence": missing_required,
        "unsupportedPrimaryTargets": unsupported_primary,
        "blockers": blocking_items,
        "decision": decision,
        "provenance": deepcopy(provenance),
        "doesNotProve": [
            "production readiness",
            "runtime correctness beyond supplied evidence",
            "authority outside the repository evidence boundary",
        ],
        "generatedAt": utc_now_iso(),
        "certifiable": False,
        "productionCertified": False,
    }
    model["modelDigest"] = sha256_json(model)
    return model
