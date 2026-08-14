from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .contracts import POLICY_SCHEMA, ContractError, ensure_no_raw_secret_values, normalize_scope, require_nonempty_string, require_string_list, sha256_json


def validate_policy_pack(policy: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(policy, Mapping):
        raise ContractError("policy pack must be an object")
    if policy.get("schemaVersion") != POLICY_SCHEMA:
        raise ContractError("unsupported policy schemaVersion")
    normalized = deepcopy(dict(policy))
    normalized["policyId"] = require_nonempty_string(policy.get("policyId"), "policyId")
    normalized["version"] = require_nonempty_string(policy.get("version"), "version")
    normalized["protectedPaths"] = normalize_scope(require_string_list(policy.get("protectedPaths", []), "protectedPaths"))
    for field in ("requiredAuthorities", "requiredTests", "requiredReviews", "forbiddenOperations", "domainEvidenceRequirements"):
        normalized[field] = sorted(set(require_string_list(policy.get(field, []), field)))
    thresholds = policy.get("impactThresholds", {})
    if not isinstance(thresholds, Mapping):
        raise ContractError("impactThresholds must be an object")
    normalized["impactThresholds"] = dict(thresholds)
    normalized["configurationIsEvidence"] = False
    normalized["certifiable"] = False
    normalized["productionCertified"] = False
    ensure_no_raw_secret_values(normalized)
    normalized["policyDigest"] = sha256_json({k: v for k, v in normalized.items() if k != "policyDigest"})
    return normalized
