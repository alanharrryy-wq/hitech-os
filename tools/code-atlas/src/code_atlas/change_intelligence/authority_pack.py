from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .contracts import (
    PACK_SCHEMA,
    ContractError,
    canonical_json,
    ensure_no_raw_secret_values,
    normalize_scope,
    require_nonempty_string,
    require_string_list,
    require_exact_digest,
    sha256_json,
    utc_now_iso,
)

_REQUIRED_FIELDS = {
    "packId", "repositoryIdentity", "commitIdentity", "treeIdentity", "requestDigest",
    "normalizedTask", "allowedScope", "protectedScope", "requiredChecks", "requiredEvidence",
    "forbiddenOperations", "stopConditions", "unknowns", "evidenceReferences", "toolVersion",
    "profileVersion", "schemaVersion", "generatedAt", "checksum",
}


def _checksum_payload(pack: Mapping[str, Any]) -> dict[str, Any]:
    payload = deepcopy(dict(pack))
    payload.pop("checksum", None)
    return payload


def validate_authority_pack(pack: Mapping[str, Any], *, verify_checksum: bool = True) -> dict[str, Any]:
    if not isinstance(pack, Mapping):
        raise ContractError("authority pack must be an object")
    missing = sorted(_REQUIRED_FIELDS - set(pack))
    if missing:
        raise ContractError(f"authority pack missing required fields: {', '.join(missing)}")

    normalized = deepcopy(dict(pack))
    normalized["packId"] = require_nonempty_string(pack["packId"], "packId")
    normalized["repositoryIdentity"] = require_nonempty_string(pack["repositoryIdentity"], "repositoryIdentity")
    normalized["commitIdentity"] = require_nonempty_string(pack["commitIdentity"], "commitIdentity")
    normalized["treeIdentity"] = require_nonempty_string(pack["treeIdentity"], "treeIdentity")
    normalized["requestDigest"] = require_nonempty_string(pack["requestDigest"], "requestDigest")
    normalized["normalizedTask"] = require_nonempty_string(pack["normalizedTask"], "normalizedTask")
    normalized["toolVersion"] = require_nonempty_string(pack["toolVersion"], "toolVersion")
    normalized["profileVersion"] = require_nonempty_string(pack["profileVersion"], "profileVersion")
    normalized["generatedAt"] = require_nonempty_string(pack["generatedAt"], "generatedAt")
    if pack["schemaVersion"] != PACK_SCHEMA:
        raise ContractError(f"unsupported schemaVersion: {pack['schemaVersion']!r}")

    normalized["allowedScope"] = normalize_scope(require_string_list(pack["allowedScope"], "allowedScope", allow_empty=False))
    normalized["protectedScope"] = normalize_scope(require_string_list(pack["protectedScope"], "protectedScope"))
    normalized["requiredChecks"] = sorted(set(require_string_list(pack["requiredChecks"], "requiredChecks")))
    normalized["requiredEvidence"] = sorted(set(require_string_list(pack["requiredEvidence"], "requiredEvidence")))
    normalized["forbiddenOperations"] = sorted(set(require_string_list(pack["forbiddenOperations"], "forbiddenOperations")))
    normalized["stopConditions"] = sorted(set(require_string_list(pack["stopConditions"], "stopConditions")))
    normalized["unknowns"] = require_string_list(pack["unknowns"], "unknowns")
    if not isinstance(pack["evidenceReferences"], list):
        raise ContractError("evidenceReferences must be a list")

    overlap = sorted(set(normalized["allowedScope"]) & set(normalized["protectedScope"]))
    if overlap:
        raise ContractError(f"allowedScope overlaps protectedScope: {overlap}")

    compatibility_locks = pack.get("compatibilityLocks", {})
    if compatibility_locks is not None:
        if not isinstance(compatibility_locks, Mapping):
            raise ContractError("compatibilityLocks must be an object")
        for lock_name in ("authorityDigest", "policyDigest", "evidenceDigest"):
            value = compatibility_locks.get(lock_name)
            if value is not None:
                require_exact_digest(value, f"compatibilityLocks.{lock_name}")

    authority_resolution = pack.get("authorityResolution", {})
    if authority_resolution is not None:
        if not isinstance(authority_resolution, Mapping):
            raise ContractError("authorityResolution must be an object")
        missing_authorities = require_string_list(authority_resolution.get("missing", []), "authorityResolution.missing")
        conflicted_authorities = require_string_list(authority_resolution.get("conflicted", []), "authorityResolution.conflicted")
        if missing_authorities or conflicted_authorities:
            raise ContractError("cannot issue authority pack with unresolved required authorities")

    ensure_no_raw_secret_values(normalized)

    checksum = require_nonempty_string(pack["checksum"], "checksum")
    expected = sha256_json(_checksum_payload(normalized))
    if verify_checksum and checksum != expected:
        raise ContractError("authority pack checksum mismatch")
    normalized["checksum"] = checksum
    return normalized


def build_authority_pack(
    *,
    repository_identity: str,
    commit_identity: str,
    tree_identity: str,
    request_digest: str,
    normalized_task: str,
    allowed_scope: list[str],
    protected_scope: list[str] | None = None,
    required_checks: list[str] | None = None,
    required_evidence: list[str] | None = None,
    forbidden_operations: list[str] | None = None,
    stop_conditions: list[str] | None = None,
    unknowns: list[str] | None = None,
    evidence_references: list[dict[str, Any]] | None = None,
    tool_version: str,
    profile_version: str,
    authority_resolution: Mapping[str, Any] | None = None,
    generated_at: str | None = None,
    authority_digest: str | None = None,
    policy_digest: str | None = None,
    evidence_digest: str | None = None,
) -> dict[str, Any]:
    seed = {
        "repositoryIdentity": require_nonempty_string(repository_identity, "repository_identity"),
        "commitIdentity": require_nonempty_string(commit_identity, "commit_identity"),
        "treeIdentity": require_nonempty_string(tree_identity, "tree_identity"),
        "requestDigest": require_nonempty_string(request_digest, "request_digest"),
        "normalizedTask": require_nonempty_string(normalized_task, "normalized_task"),
        "allowedScope": normalize_scope(allowed_scope),
        "protectedScope": normalize_scope(protected_scope or []),
        "requiredChecks": sorted(set(required_checks or [])),
        "requiredEvidence": sorted(set(required_evidence or [])),
        "forbiddenOperations": sorted(set(forbidden_operations or [])),
        "stopConditions": sorted(set(stop_conditions or [])),
        "unknowns": list(unknowns or []),
        "evidenceReferences": list(evidence_references or []),
        "toolVersion": require_nonempty_string(tool_version, "tool_version"),
        "profileVersion": require_nonempty_string(profile_version, "profile_version"),
        "schemaVersion": PACK_SCHEMA,
        "generatedAt": generated_at or utc_now_iso(),
        "authorityResolution": dict(authority_resolution or {"missing": [], "conflicted": []}),
        "certifiable": False,
        "productionCertified": False,
        "compatibilityLocks": {
            "authorityDigest": require_exact_digest(authority_digest, "authority_digest") if authority_digest else None,
            "policyDigest": require_exact_digest(policy_digest, "policy_digest") if policy_digest else None,
            "evidenceDigest": require_exact_digest(evidence_digest, "evidence_digest") if evidence_digest else None,
        },
    }
    ensure_no_raw_secret_values(seed)
    pack_seed = canonical_json(seed)
    pack_id = "cap." + __import__("hashlib").sha256(pack_seed.encode("utf-8")).hexdigest()[:20]
    pack = {"packId": pack_id, **seed}
    pack["checksum"] = sha256_json(_checksum_payload(pack))
    return validate_authority_pack(pack)
