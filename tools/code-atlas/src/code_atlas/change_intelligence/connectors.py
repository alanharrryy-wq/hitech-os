from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .contracts import CONNECTOR_SCHEMA, ContractError, ensure_no_raw_secret_values, require_nonempty_string, require_exact_digest, sha256_json

SUPPORTED_CONNECTOR_TYPES = {
    "git-pr-diff",
    "github-actions-style-ci",
    "sarif",
    "junit",
    "coverage-summary",
    "codeowners-style-ownership",
    "generic-command-evidence",
}


def validate_connector_envelope(envelope: Mapping[str, Any], *, expected_repository: str | None = None, expected_commit: str | None = None) -> dict[str, Any]:
    if not isinstance(envelope, Mapping):
        raise ContractError("connector envelope must be an object")
    if envelope.get("schemaVersion") != CONNECTOR_SCHEMA:
        raise ContractError("unsupported connector schemaVersion")
    normalized = deepcopy(dict(envelope))
    connector_type = require_nonempty_string(envelope.get("connectorType"), "connectorType")
    if connector_type not in SUPPORTED_CONNECTOR_TYPES:
        raise ContractError(f"unsupported connectorType: {connector_type}")
    normalized["connectorType"] = connector_type
    normalized["repositoryIdentity"] = require_nonempty_string(envelope.get("repositoryIdentity"), "repositoryIdentity")
    normalized["commitIdentity"] = require_nonempty_string(envelope.get("commitIdentity"), "commitIdentity")
    normalized["observedAt"] = require_nonempty_string(envelope.get("observedAt"), "observedAt")
    normalized["sourceIdentity"] = require_nonempty_string(envelope.get("sourceIdentity"), "sourceIdentity")
    require_exact_digest(envelope.get("payloadDigest"), "payloadDigest")
    payload = envelope.get("payload")
    if not isinstance(payload, (Mapping, list)):
        raise ContractError("payload must be an object or list")
    ensure_no_raw_secret_values(payload)
    if expected_repository is not None and normalized["repositoryIdentity"] != expected_repository:
        raise ContractError("cross-repository connector evidence rejected")
    if expected_commit is not None and normalized["commitIdentity"] != expected_commit:
        raise ContractError("stale connector provenance rejected")
    if envelope["payloadDigest"] != sha256_json(payload):
        raise ContractError("connector payload digest mismatch")
    normalized["automaticAuthority"] = False
    normalized["certifiable"] = False
    normalized["productionCertified"] = False
    return normalized


def build_connector_envelope(*, connector_type: str, repository_identity: str, commit_identity: str, observed_at: str, source_identity: str, payload: Any) -> dict[str, Any]:
    envelope = {
        "schemaVersion": CONNECTOR_SCHEMA,
        "connectorType": connector_type,
        "repositoryIdentity": repository_identity,
        "commitIdentity": commit_identity,
        "observedAt": observed_at,
        "sourceIdentity": source_identity,
        "payload": payload,
        "payloadDigest": sha256_json(payload),
    }
    return validate_connector_envelope(envelope)
