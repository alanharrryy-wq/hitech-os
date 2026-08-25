from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .contracts import (
    DECISIONS,
    ContractError,
    ensure_no_raw_secret_values,
    normalize_repo_path,
    require_exact_digest,
    require_nonempty_string,
    require_string_list,
    sha256_json,
    utc_now_iso,
)

REQUIRED_SEMANTIC_EVIDENCE_ROLES = (
    "decision_classification",
    "gaps_unknowns",
    "replay_handoff",
)


def _normalize_artifacts(artifacts: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not artifacts:
        raise ContractError("portable bundle must contain at least one artifact descriptor")
    normalized_artifacts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, Mapping):
            raise ContractError(f"artifacts[{index}] must be an object")
        name = normalize_repo_path(artifact.get("name"))
        if name in seen:
            raise ContractError(f"duplicate bundle artifact name: {name}")
        seen.add(name)
        digest = require_exact_digest(artifact.get("digest"), f"artifacts[{index}].digest")
        size = artifact.get("size")
        if not isinstance(size, int) or size < 0:
            raise ContractError(f"artifacts[{index}].size must be a non-negative integer")
        normalized_artifacts.append({
            "name": name,
            "kind": require_nonempty_string(artifact.get("kind"), f"artifacts[{index}].kind"),
            "digest": digest,
            "size": size,
        })
    return sorted(normalized_artifacts, key=lambda row: row["name"])


def _validate_repository_snapshot(repository_snapshot: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(repository_snapshot, Mapping):
        raise ContractError("repository_snapshot must be an object")
    normalized = deepcopy(dict(repository_snapshot))
    for key in ("repositoryIdentity", "commitIdentity", "treeIdentity"):
        normalized[key] = require_nonempty_string(repository_snapshot.get(key), f"repository_snapshot.{key}")
    ensure_no_raw_secret_values(normalized)
    return normalized


def _normalize_sanitization_attestations(
    attestations: list[Mapping[str, Any]],
    artifacts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(attestations, list) or len(attestations) != len(artifacts):
        raise ContractError("one sanitization attestation is required for every artifact")
    by_artifact = {row["name"]: row for row in artifacts}
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(attestations):
        if not isinstance(raw, Mapping) or raw.get("schemaVersion") != "code_atlas_artifact_sanitization.v1":
            raise ContractError(f"sanitizationAttestations[{index}] uses an unsupported schema")
        name = normalize_repo_path(raw.get("name"))
        if name in seen:
            raise ContractError(f"duplicate sanitization attestation: {name}")
        seen.add(name)
        artifact = by_artifact.get(name)
        if artifact is None:
            raise ContractError(f"sanitization attestation has no matching artifact: {name}")
        kind = require_nonempty_string(raw.get("kind"), f"sanitizationAttestations[{index}].kind")
        if kind != artifact["kind"]:
            raise ContractError(f"sanitization attestation kind mismatch: {name}")
        if raw.get("decision") not in {"PASS_CLEAN", "PASS_SANITIZED"}:
            raise ContractError(f"artifact sanitization is not PASS: {name}")
        if raw.get("contentInspection") != "FULL_UTF8_TEXT":
            raise ContractError(f"artifact was not fully content-inspected: {name}")
        if raw.get("sourceCodeIncluded") is not False:
            raise ContractError(f"source-code egress attestation is not false: {name}")
        sanitized_digest = require_exact_digest(raw.get("sanitizedDigest"), f"sanitizationAttestations[{index}].sanitizedDigest")
        original_digest = require_exact_digest(raw.get("originalDigest"), f"sanitizationAttestations[{index}].originalDigest")
        ruleset_digest = require_exact_digest(raw.get("rulesetDigest"), f"sanitizationAttestations[{index}].rulesetDigest")
        attestation_digest = require_exact_digest(raw.get("attestationDigest"), f"sanitizationAttestations[{index}].attestationDigest")
        sanitized_size = raw.get("sanitizedSize")
        original_size = raw.get("originalSize")
        if not isinstance(sanitized_size, int) or sanitized_size < 0:
            raise ContractError(f"sanitizationAttestations[{index}].sanitizedSize must be non-negative")
        if not isinstance(original_size, int) or original_size < 0:
            raise ContractError(f"sanitizationAttestations[{index}].originalSize must be non-negative")
        if sanitized_digest != artifact["digest"] or sanitized_size != artifact["size"]:
            raise ContractError(f"artifact descriptor does not match sanitized bytes: {name}")
        base = {key: deepcopy(value) for key, value in raw.items() if key != "attestationDigest"}
        if sha256_json(base) != attestation_digest:
            raise ContractError(f"sanitization attestation digest mismatch: {name}")
        normalized.append({
            "schemaVersion": "code_atlas_artifact_sanitization.v1",
            "name": name,
            "kind": kind,
            "scannerId": require_nonempty_string(raw.get("scannerId"), f"sanitizationAttestations[{index}].scannerId"),
            "rulesetDigest": ruleset_digest,
            "contentInspection": "FULL_UTF8_TEXT",
            "originalDigest": original_digest,
            "originalSize": original_size,
            "sanitizedDigest": sanitized_digest,
            "sanitizedSize": sanitized_size,
            "findings": deepcopy(raw.get("findings") or []),
            "decision": raw.get("decision"),
            "sourceCodeIncluded": False,
            "attestationDigest": attestation_digest,
        })
    if seen != set(by_artifact):
        missing = sorted(set(by_artifact) - seen)
        raise ContractError(f"missing sanitization attestations: {missing}")
    ensure_no_raw_secret_values(normalized)
    return sorted(normalized, key=lambda row: row["name"])


def _normalize_semantic_evidence_roles(
    roles: list[Mapping[str, Any]],
    artifacts: list[dict[str, Any]],
    repository_snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(roles, list):
        raise ContractError("semantic_evidence_roles must be a list")
    expected_roles = set(REQUIRED_SEMANTIC_EVIDENCE_ROLES)
    artifacts_by_name = {row["name"]: row for row in artifacts}
    snapshot_digest = sha256_json(repository_snapshot)
    normalized_by_role: dict[str, dict[str, Any]] = {}

    for index, raw in enumerate(roles):
        if not isinstance(raw, Mapping):
            raise ContractError(f"semantic_evidence_roles[{index}] must be an object")
        role = require_nonempty_string(raw.get("role"), f"semantic_evidence_roles[{index}].role")
        if role not in expected_roles:
            raise ContractError(f"unsupported semantic evidence role: {role}")
        if role in normalized_by_role:
            raise ContractError(f"duplicate semantic evidence role: {role}")

        artifact_name = normalize_repo_path(raw.get("artifactName"))
        artifact = artifacts_by_name.get(artifact_name)
        if artifact is None:
            raise ContractError(f"semantic evidence role has no matching artifact: {artifact_name}")
        role_snapshot_digest = require_exact_digest(
            raw.get("snapshotDigest"),
            f"semantic_evidence_roles[{index}].snapshotDigest",
        )
        if role_snapshot_digest != snapshot_digest:
            raise ContractError(f"stale semantic evidence snapshot for role: {role}")
        decision = require_nonempty_string(raw.get("decision"), f"semantic_evidence_roles[{index}].decision").upper()
        if decision not in DECISIONS:
            raise ContractError(f"invalid semantic evidence decision for role {role}: {decision}")

        normalized: dict[str, Any] = {
            "role": role,
            "artifactName": artifact_name,
            "artifactDigest": artifact["digest"],
            "snapshotDigest": snapshot_digest,
            "decision": decision,
        }
        if role == "decision_classification":
            normalized["classification"] = require_nonempty_string(
                raw.get("classification"),
                f"semantic_evidence_roles[{index}].classification",
            )
        elif role == "gaps_unknowns":
            normalized["gaps"] = sorted(set(require_string_list(
                raw.get("gaps"),
                f"semantic_evidence_roles[{index}].gaps",
            )))
            normalized["unknowns"] = sorted(set(require_string_list(
                raw.get("unknowns"),
                f"semantic_evidence_roles[{index}].unknowns",
            )))
        else:
            normalized["replayId"] = require_nonempty_string(
                raw.get("replayId"),
                f"semantic_evidence_roles[{index}].replayId",
            )
            normalized["handoffId"] = require_nonempty_string(
                raw.get("handoffId"),
                f"semantic_evidence_roles[{index}].handoffId",
            )
            normalized["replayDigest"] = require_exact_digest(
                raw.get("replayDigest"),
                f"semantic_evidence_roles[{index}].replayDigest",
            )
            normalized["handoffDigest"] = require_exact_digest(
                raw.get("handoffDigest"),
                f"semantic_evidence_roles[{index}].handoffDigest",
            )
        normalized_by_role[role] = normalized

    missing = [role for role in REQUIRED_SEMANTIC_EVIDENCE_ROLES if role not in normalized_by_role]
    if missing:
        raise ContractError(f"missing required semantic evidence roles: {missing}")
    decisions = {row["decision"] for row in normalized_by_role.values()}
    if len(decisions) != 1:
        raise ContractError("contradictory semantic evidence decisions")

    ordered = [normalized_by_role[role] for role in REQUIRED_SEMANTIC_EVIDENCE_ROLES]
    semantic = {
        "schemaVersion": "code_atlas_evidence_bundle_semantics.v1",
        "snapshotDigest": snapshot_digest,
        "decision": normalized_by_role["decision_classification"]["decision"],
        "requiredRoles": list(REQUIRED_SEMANTIC_EVIDENCE_ROLES),
        "roles": ordered,
        "semanticRoleCoverageComplete": True,
        "proofBearingSemanticPrerequisitesSatisfied": True,
        "decisionPromotionAllowedByPackaging": False,
        "certifiable": False,
        "productionCertified": False,
    }
    ensure_no_raw_secret_values(semantic)
    semantic["semanticDigest"] = sha256_json(semantic)
    return semantic


def build_portable_bundle_manifest(
    *,
    repository_snapshot: Mapping[str, Any],
    artifacts: list[Mapping[str, Any]],
    purpose: str,
    pack_id: str | None = None,
    verification_report_digest: str | None = None,
) -> dict[str, Any]:
    """Build the legacy V1 descriptor-only portable manifest.

    V1 remains for compatibility. It does not prove artifact-byte sanitization and
    therefore is not accepted by the hardened rental runner V2.
    """

    normalized_snapshot = _validate_repository_snapshot(repository_snapshot)
    normalized_artifacts = _normalize_artifacts(artifacts)
    manifest = {
        "schemaVersion": "code_atlas_portable_evidence_bundle.v1",
        "purpose": require_nonempty_string(purpose, "purpose"),
        "repositorySnapshot": normalized_snapshot,
        "packId": pack_id,
        "verificationReportDigest": verification_report_digest,
        "artifacts": normalized_artifacts,
        "generatedAt": utc_now_iso(),
        "sourceCodeIncluded": False,
        "artifactContentSanitizationProven": False,
        "certifiable": False,
        "productionCertified": False,
    }
    ensure_no_raw_secret_values(manifest)
    manifest["manifestDigest"] = sha256_json(manifest)
    return manifest


def build_hardened_portable_bundle_manifest(
    *,
    repository_snapshot: Mapping[str, Any],
    artifacts: list[Mapping[str, Any]],
    sanitization_attestations: list[Mapping[str, Any]],
    lifecycle_policy_digest: str,
    purpose: str,
    pack_id: str | None = None,
    verification_report_digest: str | None = None,
    semantic_evidence_roles: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a V2 manifest only from artifacts with verified byte-scan attestations.

    ``semantic_evidence_roles`` is additive. When supplied, all three required
    semantic categories must bind to current sanitized artifacts and the exact
    repository snapshot. Packaging records the existing decision but can never
    promote it or create certification. Omitting semantic roles preserves the
    legacy V2 manifest shape for compatibility.
    """

    normalized_snapshot = _validate_repository_snapshot(repository_snapshot)
    normalized_artifacts = _normalize_artifacts(artifacts)
    normalized_attestations = _normalize_sanitization_attestations(sanitization_attestations, normalized_artifacts)
    lifecycle_digest = require_exact_digest(lifecycle_policy_digest, "lifecycle_policy_digest")
    semantic_evidence = None
    if semantic_evidence_roles is not None:
        semantic_evidence = _normalize_semantic_evidence_roles(
            semantic_evidence_roles,
            normalized_artifacts,
            normalized_snapshot,
        )
    manifest = {
        "schemaVersion": "code_atlas_portable_evidence_bundle.v2",
        "purpose": require_nonempty_string(purpose, "purpose"),
        "repositorySnapshot": normalized_snapshot,
        "packId": pack_id,
        "verificationReportDigest": verification_report_digest,
        "artifacts": normalized_artifacts,
        "sanitizationAttestations": normalized_attestations,
        "dataLifecyclePolicyDigest": lifecycle_digest,
        "generatedAt": utc_now_iso(),
        "sourceCodeIncluded": False,
        "artifactContentSanitizationProven": True,
        "allArtifactsInspected": True,
        "cleanupEvidenceRequired": True,
        "failClosed": True,
        "certifiable": False,
        "productionCertified": False,
    }
    if semantic_evidence is not None:
        manifest["semanticEvidence"] = semantic_evidence
    ensure_no_raw_secret_values(manifest)
    manifest["manifestDigest"] = sha256_json(manifest)
    return manifest


__all__ = [
    "REQUIRED_SEMANTIC_EVIDENCE_ROLES",
    "build_hardened_portable_bundle_manifest",
    "build_portable_bundle_manifest",
]
