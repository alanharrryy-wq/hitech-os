from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .contracts import ContractError, SUPPORT_LEVELS, ensure_no_raw_secret_values, require_nonempty_string, sha256_json


def normalize_evidence_answer(answer: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(answer, Mapping):
        raise ContractError("evidence answer must be an object")
    normalized = deepcopy(dict(answer))
    normalized["claim"] = require_nonempty_string(answer.get("claim"), "claim")
    support = require_nonempty_string(answer.get("supportLevel"), "supportLevel").upper()
    if support not in SUPPORT_LEVELS:
        raise ContractError(f"unsupported supportLevel: {support}")
    normalized["supportLevel"] = support
    refs = answer.get("evidenceReferences", [])
    if not isinstance(refs, list):
        raise ContractError("evidenceReferences must be a list")
    normalized["evidenceReferences"] = refs
    contradictions = answer.get("contradictions", [])
    if not isinstance(contradictions, list):
        raise ContractError("contradictions must be a list")
    normalized["contradictions"] = contradictions
    normalized["doesNotProve"] = answer.get("doesNotProve", [])
    if not isinstance(normalized["doesNotProve"], list):
        raise ContractError("doesNotProve must be a list")

    retrieval_only = bool(answer.get("retrievalOnly", False))
    if support == "SUPPORTED" and (not refs or retrieval_only):
        raise ContractError("SUPPORTED claim requires non-retrieval evidence references")
    if support == "INFERRED" and not answer.get("inference"):
        raise ContractError("INFERRED claim requires explicit inference text")
    if contradictions and support == "SUPPORTED":
        raise ContractError("contradicted claim cannot be marked SUPPORTED without conflict resolution")

    normalized["retrievalIsProof"] = False
    normalized["certifiable"] = False
    normalized["productionCertified"] = False
    ensure_no_raw_secret_values(normalized)
    normalized["answerDigest"] = sha256_json({k: v for k, v in normalized.items() if k != "answerDigest"})
    return normalized
