from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .contracts import ContractError, ensure_no_raw_secret_values, require_nonempty_string, sha256_json
from .customer_lifecycle import (
    build_customer_lifecycle_policy,
    validate_cleanup_evidence,
    validate_customer_lifecycle_policy,
)

RUNNER_MODES = {"LOCAL_ONLY", "PORTABLE_EVIDENCE"}


def _normalize_requested_outputs(requested_outputs: list[str]) -> list[str]:
    if not isinstance(requested_outputs, list) or not all(isinstance(item, str) and item.strip() for item in requested_outputs):
        raise ContractError("requested_outputs must be a list of non-empty strings")
    return sorted(set(item.strip() for item in requested_outputs))


def _normalize_mutations(mutation_permissions: Mapping[str, bool] | None) -> dict[str, bool]:
    mutations = dict(mutation_permissions or {})
    forbidden_enabled = sorted(key for key, enabled in mutations.items() if bool(enabled))
    if forbidden_enabled:
        raise ContractError(f"runner mutation permissions are forbidden: {forbidden_enabled}")
    return {
        "source": False,
        "git": False,
        "database": False,
        "process": False,
        "port": False,
        "deployment": False,
        **{key: False for key in mutations},
    }


def build_runner_plan(
    *,
    repository_identity: str,
    mode: str,
    requested_outputs: list[str],
    customer_controls_egress: bool = True,
    read_only: bool = True,
    source_code_egress: bool = False,
    mutation_permissions: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    """Build the legacy V1 runner plan.

    V1 remains compatible with existing local evidence workflows. External rental
    should use :func:`build_rental_runner_plan`, which requires byte-level artifact
    hygiene plus an explicit data-lifecycle contract.
    """

    mode = require_nonempty_string(mode, "mode").upper()
    if mode not in RUNNER_MODES:
        raise ContractError(f"unsupported runner mode: {mode}")
    if not read_only:
        raise ContractError("customer runner V1 must remain read-only")
    if source_code_egress:
        raise ContractError("source code egress is not allowed by the V1 runner contract")
    plan = {
        "schemaVersion": "code_atlas_customer_runner_plan.v1",
        "repositoryIdentity": require_nonempty_string(repository_identity, "repository_identity"),
        "mode": mode,
        "requestedOutputs": _normalize_requested_outputs(requested_outputs),
        "readOnly": True,
        "sourceCodeEgress": False,
        "customerControlsEvidenceEgress": bool(customer_controls_egress),
        "mutationPermissions": _normalize_mutations(mutation_permissions),
        "leastPrivilege": True,
        "artifactContentSanitizationRequired": False,
        "productionReady": False,
        "certifiable": False,
        "productionCertified": False,
    }
    ensure_no_raw_secret_values(plan)
    plan["planDigest"] = sha256_json(plan)
    return plan


def build_rental_runner_plan(
    *,
    repository_identity: str,
    mode: str = "PORTABLE_EVIDENCE",
    requested_outputs: list[str],
    retention_mode: str = "EPHEMERAL",
    retention_seconds: int = 0,
    customer_controls_egress: bool = True,
    read_only: bool = True,
    source_code_egress: bool = False,
    mutation_permissions: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    """Build the strict V2 runner plan intended for external private repositories."""

    mode = require_nonempty_string(mode, "mode").upper()
    if mode not in RUNNER_MODES:
        raise ContractError(f"unsupported runner mode: {mode}")
    if not read_only:
        raise ContractError("rental runner V2 must remain read-only")
    if source_code_egress:
        raise ContractError("source code egress is forbidden by the rental runner V2 contract")
    repo = require_nonempty_string(repository_identity, "repository_identity")
    lifecycle = build_customer_lifecycle_policy(
        repository_identity=repo,
        retention_mode=retention_mode,
        retention_seconds=retention_seconds,
    )
    plan = {
        "schemaVersion": "code_atlas_customer_runner_plan.v2",
        "repositoryIdentity": repo,
        "mode": mode,
        "requestedOutputs": _normalize_requested_outputs(requested_outputs),
        "readOnly": True,
        "sourceCodeEgress": False,
        "customerControlsEvidenceEgress": bool(customer_controls_egress),
        "mutationPermissions": _normalize_mutations(mutation_permissions),
        "leastPrivilege": True,
        "artifactContentSanitizationRequired": True,
        "allExportedArtifactsMustBeInspected": True,
        "unknownArtifactFormatDecision": "BLOCKED",
        "dataLifecyclePolicy": lifecycle,
        "dataLifecyclePolicyDigest": lifecycle["policyDigest"],
        "cleanupEvidenceRequired": True,
        "failClosed": True,
        "doesNotProve": [
            "Legal, privacy, regulatory, or security certification.",
            "Production or enterprise readiness without separate evidence gates.",
        ],
        "productionReady": False,
        "certifiable": False,
        "productionCertified": False,
    }
    ensure_no_raw_secret_values(plan)
    plan["planDigest"] = sha256_json(plan)
    return plan


def validate_runner_egress(*, runner_plan: Mapping[str, Any], bundle_manifest: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(runner_plan, Mapping):
        raise ContractError("runner plan must be an object")
    schema = runner_plan.get("schemaVersion")
    if schema not in {"code_atlas_customer_runner_plan.v1", "code_atlas_customer_runner_plan.v2"}:
        raise ContractError("unsupported runner plan")
    if not isinstance(bundle_manifest, Mapping):
        raise ContractError("bundle manifest must be an object")

    repo = runner_plan.get("repositoryIdentity")
    bundle_repo = (bundle_manifest.get("repositorySnapshot") or {}).get("repositoryIdentity")
    if repo != bundle_repo:
        raise ContractError("runner egress bundle repository mismatch")
    if bundle_manifest.get("sourceCodeIncluded") is not False:
        raise ContractError("runner egress bundle must not include source code")
    if runner_plan.get("mode") == "LOCAL_ONLY":
        raise ContractError("LOCAL_ONLY runner plan forbids evidence egress")

    if schema == "code_atlas_customer_runner_plan.v1":
        if bundle_manifest.get("schemaVersion") != "code_atlas_portable_evidence_bundle.v1":
            raise ContractError("runner V1 requires portable evidence bundle V1")
        result_schema = "code_atlas_customer_runner_egress.v1"
        cleanup_required = False
    else:
        if bundle_manifest.get("schemaVersion") != "code_atlas_portable_evidence_bundle.v2":
            raise ContractError("rental runner V2 requires hardened portable evidence bundle V2")
        lifecycle = validate_customer_lifecycle_policy(runner_plan.get("dataLifecyclePolicy") or {})
        if runner_plan.get("dataLifecyclePolicyDigest") != lifecycle["policyDigest"]:
            raise ContractError("runner lifecycle digest mismatch")
        if bundle_manifest.get("dataLifecyclePolicyDigest") != lifecycle["policyDigest"]:
            raise ContractError("bundle lifecycle policy does not match runner plan")
        if bundle_manifest.get("artifactContentSanitizationProven") is not True:
            raise ContractError("rental egress requires proven artifact content sanitization")
        if bundle_manifest.get("allArtifactsInspected") is not True:
            raise ContractError("rental egress requires every artifact to be inspected")
        artifacts = bundle_manifest.get("artifacts") or []
        attestations = bundle_manifest.get("sanitizationAttestations") or []
        if not artifacts or len(artifacts) != len(attestations):
            raise ContractError("rental egress requires one sanitization attestation per artifact")
        by_name = {str(row.get("name")): row for row in artifacts if isinstance(row, Mapping)}
        attested_names: set[str] = set()
        for index, attestation in enumerate(attestations):
            if not isinstance(attestation, Mapping):
                raise ContractError(f"sanitizationAttestations[{index}] must be an object")
            name = str(attestation.get("name") or "")
            artifact = by_name.get(name)
            if artifact is None:
                raise ContractError(f"sanitization attestation has no artifact: {name}")
            if attestation.get("decision") not in {"PASS_CLEAN", "PASS_SANITIZED"}:
                raise ContractError(f"sanitization did not pass for artifact: {name}")
            if attestation.get("sanitizedDigest") != artifact.get("digest"):
                raise ContractError(f"sanitization digest mismatch for artifact: {name}")
            if attestation.get("sanitizedSize") != artifact.get("size"):
                raise ContractError(f"sanitization size mismatch for artifact: {name}")
            attested_names.add(name)
        if attested_names != set(by_name):
            raise ContractError("not every artifact has sanitization provenance")
        result_schema = "code_atlas_customer_runner_egress.v2"
        cleanup_required = True

    result = {
        "schemaVersion": result_schema,
        "repositoryIdentity": repo,
        "planDigest": runner_plan.get("planDigest"),
        "bundleDigest": bundle_manifest.get("manifestDigest"),
        "allowed": True,
        "postEgressCleanupRequired": cleanup_required,
        "certifiable": False,
        "productionCertified": False,
    }
    return deepcopy(result)


def validate_runner_cleanup(*, runner_plan: Mapping[str, Any], cleanup_evidence: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(runner_plan, Mapping) or runner_plan.get("schemaVersion") != "code_atlas_customer_runner_plan.v2":
        raise ContractError("cleanup validation requires rental runner V2")
    lifecycle = validate_customer_lifecycle_policy(runner_plan.get("dataLifecyclePolicy") or {})
    evidence = validate_cleanup_evidence(cleanup_evidence=cleanup_evidence, lifecycle_policy=lifecycle)
    return {
        "schemaVersion": "code_atlas_customer_runner_cleanup_validation.v1",
        "repositoryIdentity": runner_plan.get("repositoryIdentity"),
        "planDigest": runner_plan.get("planDigest"),
        "cleanupEvidenceDigest": evidence["cleanupEvidenceDigest"],
        "cleanupVerified": True,
        "remainingPaths": 0,
        "secureEraseGuaranteed": False,
        "certifiable": False,
        "productionCertified": False,
    }


__all__ = [
    "build_rental_runner_plan",
    "build_runner_plan",
    "validate_runner_cleanup",
    "validate_runner_egress",
]
