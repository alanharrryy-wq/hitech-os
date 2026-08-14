from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .contracts import ContractError, ensure_no_raw_secret_values, require_nonempty_string, sha256_json

RUNNER_MODES = {"LOCAL_ONLY", "PORTABLE_EVIDENCE"}


def build_runner_plan(*, repository_identity: str, mode: str, requested_outputs: list[str], customer_controls_egress: bool = True, read_only: bool = True, source_code_egress: bool = False, mutation_permissions: Mapping[str, bool] | None = None) -> dict[str, Any]:
    mode = require_nonempty_string(mode, "mode").upper()
    if mode not in RUNNER_MODES:
        raise ContractError(f"unsupported runner mode: {mode}")
    if not read_only:
        raise ContractError("customer runner V1 must remain read-only")
    if source_code_egress:
        raise ContractError("source code egress is not allowed by the V1 runner contract")
    if not isinstance(requested_outputs, list) or not all(isinstance(item, str) and item.strip() for item in requested_outputs):
        raise ContractError("requested_outputs must be a list of non-empty strings")
    mutations = dict(mutation_permissions or {})
    forbidden_enabled = sorted(key for key, enabled in mutations.items() if bool(enabled))
    if forbidden_enabled:
        raise ContractError(f"runner mutation permissions are forbidden: {forbidden_enabled}")
    plan = {
        "schemaVersion": "code_atlas_customer_runner_plan.v1",
        "repositoryIdentity": require_nonempty_string(repository_identity, "repository_identity"),
        "mode": mode,
        "requestedOutputs": sorted(set(item.strip() for item in requested_outputs)),
        "readOnly": True,
        "sourceCodeEgress": False,
        "customerControlsEvidenceEgress": bool(customer_controls_egress),
        "mutationPermissions": {"source": False, "git": False, "database": False, "process": False, "port": False, "deployment": False, **{key: False for key in mutations}},
        "leastPrivilege": True,
        "productionReady": False,
        "certifiable": False,
        "productionCertified": False,
    }
    ensure_no_raw_secret_values(plan)
    plan["planDigest"] = sha256_json(plan)
    return plan


def validate_runner_egress(*, runner_plan: Mapping[str, Any], bundle_manifest: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(runner_plan, Mapping) or runner_plan.get("schemaVersion") != "code_atlas_customer_runner_plan.v1":
        raise ContractError("unsupported runner plan")
    if not isinstance(bundle_manifest, Mapping) or bundle_manifest.get("schemaVersion") != "code_atlas_portable_evidence_bundle.v1":
        raise ContractError("unsupported bundle manifest")
    repo = runner_plan.get("repositoryIdentity")
    bundle_repo = (bundle_manifest.get("repositorySnapshot") or {}).get("repositoryIdentity")
    if repo != bundle_repo:
        raise ContractError("runner egress bundle repository mismatch")
    if bundle_manifest.get("sourceCodeIncluded") is not False:
        raise ContractError("runner egress bundle must not include source code")
    if runner_plan.get("mode") == "LOCAL_ONLY":
        raise ContractError("LOCAL_ONLY runner plan forbids evidence egress")
    result = {
        "schemaVersion": "code_atlas_customer_runner_egress.v1",
        "repositoryIdentity": repo,
        "planDigest": runner_plan.get("planDigest"),
        "bundleDigest": bundle_manifest.get("manifestDigest"),
        "allowed": True,
        "certifiable": False,
        "productionCertified": False,
    }
    return deepcopy(result)
