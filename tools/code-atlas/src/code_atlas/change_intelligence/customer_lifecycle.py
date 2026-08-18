from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from .contracts import ContractError, require_nonempty_string, sha256_json, utc_now_iso

LIFECYCLE_MODES = {"EPHEMERAL", "BOUNDED"}
MAX_BOUNDED_RETENTION_SECONDS = 86_400
_SENTINEL = ".code-atlas-customer-workspace.json"
_SESSION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")


def _parse_utc(value: str, field: str) -> datetime:
    text = require_nonempty_string(value, field)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ContractError(f"{field} must include timezone information")
    return parsed.astimezone(timezone.utc)


def build_customer_lifecycle_policy(
    *,
    repository_identity: str,
    retention_mode: str = "EPHEMERAL",
    retention_seconds: int = 0,
) -> dict[str, Any]:
    mode = require_nonempty_string(retention_mode, "retention_mode").upper()
    if mode not in LIFECYCLE_MODES:
        raise ContractError(f"unsupported retention mode: {mode}")
    if not isinstance(retention_seconds, int) or retention_seconds < 0:
        raise ContractError("retention_seconds must be a non-negative integer")
    if mode == "EPHEMERAL" and retention_seconds != 0:
        raise ContractError("EPHEMERAL retention must use retention_seconds=0")
    if mode == "BOUNDED" and not (1 <= retention_seconds <= MAX_BOUNDED_RETENTION_SECONDS):
        raise ContractError(
            f"BOUNDED retention_seconds must be between 1 and {MAX_BOUNDED_RETENTION_SECONDS}"
        )

    policy = {
        "schemaVersion": "code_atlas_customer_data_lifecycle.v1",
        "repositoryIdentity": require_nonempty_string(repository_identity, "repository_identity"),
        "retentionMode": mode,
        "retentionSeconds": retention_seconds,
        "cleanupRequired": True,
        "cleanupAfterSuccess": True,
        "cleanupAfterFailure": True,
        "cleanupEvidenceRequired": True,
        "sourceCodeEgressAllowed": False,
        "artifactContentInspectionRequired": True,
        "failClosedWhenInspectionUnknown": True,
        "secureEraseGuaranteed": False,
        "doesNotProve": [
            "Cryptographic or forensic secure erasure of underlying storage media.",
            "Legal, privacy, regulatory, or security certification.",
        ],
        "certifiable": False,
        "productionCertified": False,
    }
    policy["policyDigest"] = sha256_json(policy)
    return policy


def validate_customer_lifecycle_policy(policy: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(policy, Mapping) or policy.get("schemaVersion") != "code_atlas_customer_data_lifecycle.v1":
        raise ContractError("unsupported customer data lifecycle policy")
    normalized = build_customer_lifecycle_policy(
        repository_identity=require_nonempty_string(policy.get("repositoryIdentity"), "repositoryIdentity"),
        retention_mode=require_nonempty_string(policy.get("retentionMode"), "retentionMode"),
        retention_seconds=policy.get("retentionSeconds"),
    )
    if policy.get("policyDigest") != normalized["policyDigest"]:
        raise ContractError("customer data lifecycle policy digest mismatch")
    return normalized


def create_customer_workspace(
    *,
    base_root: str | Path,
    lifecycle_policy: Mapping[str, Any],
    session_id: str,
    created_at: str | None = None,
) -> dict[str, Any]:
    policy = validate_customer_lifecycle_policy(lifecycle_policy)
    sid = require_nonempty_string(session_id, "session_id")
    if not _SESSION_ID.fullmatch(sid):
        raise ContractError("session_id contains unsafe characters")
    base = Path(base_root).resolve()
    base.mkdir(parents=True, exist_ok=True)
    root = (base / f"code-atlas-{sid}").resolve()
    if base not in root.parents:
        raise ContractError("customer workspace escapes declared base root")
    if root.exists():
        raise ContractError("customer workspace already exists")

    created = _parse_utc(created_at or utc_now_iso(), "created_at")
    expires = created if policy["retentionMode"] == "EPHEMERAL" else created + timedelta(seconds=policy["retentionSeconds"])
    root.mkdir(parents=False)
    sentinel = {
        "schemaVersion": "code_atlas_customer_workspace.v1",
        "workspaceId": sid,
        "repositoryIdentity": policy["repositoryIdentity"],
        "lifecyclePolicyDigest": policy["policyDigest"],
        "createdAt": created.isoformat().replace("+00:00", "Z"),
        "expiresAt": expires.isoformat().replace("+00:00", "Z"),
    }
    sentinel["workspaceDigest"] = sha256_json(sentinel)
    (root / _SENTINEL).write_text(json.dumps(sentinel, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        **sentinel,
        "workspacePath": str(root),
        "cleanupRequired": True,
        "productionCertified": False,
    }


def customer_workspace_expired(workspace: Mapping[str, Any], *, now: str | None = None) -> bool:
    expires = _parse_utc(require_nonempty_string(workspace.get("expiresAt"), "expiresAt"), "expiresAt")
    current = _parse_utc(now or utc_now_iso(), "now")
    return current >= expires


def cleanup_customer_workspace(
    *,
    workspace: Mapping[str, Any],
    lifecycle_policy: Mapping[str, Any],
    reason: str,
    completed_at: str | None = None,
) -> dict[str, Any]:
    policy = validate_customer_lifecycle_policy(lifecycle_policy)
    root = Path(require_nonempty_string(workspace.get("workspacePath"), "workspacePath")).resolve()
    sentinel_path = root / _SENTINEL
    if not root.is_dir() or not sentinel_path.is_file():
        raise ContractError("customer workspace sentinel is missing; cleanup refuses an unowned path")
    try:
        sentinel = json.loads(sentinel_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError("customer workspace sentinel is unreadable") from exc
    expected_digest = sentinel.pop("workspaceDigest", None)
    if expected_digest != sha256_json(sentinel):
        raise ContractError("customer workspace sentinel digest mismatch")
    if sentinel.get("lifecyclePolicyDigest") != policy["policyDigest"]:
        raise ContractError("customer workspace lifecycle policy mismatch")
    if sentinel.get("repositoryIdentity") != policy["repositoryIdentity"]:
        raise ContractError("customer workspace repository identity mismatch")
    if sentinel.get("workspaceId") != workspace.get("workspaceId"):
        raise ContractError("customer workspace identity mismatch")

    files = [path for path in root.rglob("*") if path.is_file()]
    removed_files = len(files)
    removed_bytes = sum(path.stat().st_size for path in files)
    shutil.rmtree(root)
    if root.exists():
        raise ContractError("customer workspace cleanup verification failed")

    evidence = {
        "schemaVersion": "code_atlas_customer_cleanup_evidence.v1",
        "workspaceId": sentinel["workspaceId"],
        "repositoryIdentity": policy["repositoryIdentity"],
        "lifecyclePolicyDigest": policy["policyDigest"],
        "reason": require_nonempty_string(reason, "reason"),
        "completedAt": require_nonempty_string(completed_at or utc_now_iso(), "completedAt"),
        "removedFiles": removed_files,
        "removedBytes": removed_bytes,
        "remainingPaths": 0,
        "cleanupVerified": True,
        "secureEraseGuaranteed": False,
        "certifiable": False,
        "productionCertified": False,
    }
    evidence["cleanupEvidenceDigest"] = sha256_json(evidence)
    return evidence


def validate_cleanup_evidence(
    *,
    cleanup_evidence: Mapping[str, Any],
    lifecycle_policy: Mapping[str, Any],
) -> dict[str, Any]:
    policy = validate_customer_lifecycle_policy(lifecycle_policy)
    if not isinstance(cleanup_evidence, Mapping) or cleanup_evidence.get("schemaVersion") != "code_atlas_customer_cleanup_evidence.v1":
        raise ContractError("unsupported customer cleanup evidence")
    evidence = dict(cleanup_evidence)
    digest = evidence.pop("cleanupEvidenceDigest", None)
    if digest != sha256_json(evidence):
        raise ContractError("cleanup evidence digest mismatch")
    if evidence.get("lifecyclePolicyDigest") != policy["policyDigest"]:
        raise ContractError("cleanup evidence lifecycle policy mismatch")
    if evidence.get("repositoryIdentity") != policy["repositoryIdentity"]:
        raise ContractError("cleanup evidence repository identity mismatch")
    if evidence.get("cleanupVerified") is not True or evidence.get("remainingPaths") != 0:
        raise ContractError("cleanup evidence does not prove logical workspace deletion")
    return {**evidence, "cleanupEvidenceDigest": digest}


__all__ = [
    "MAX_BOUNDED_RETENTION_SECONDS",
    "build_customer_lifecycle_policy",
    "cleanup_customer_workspace",
    "create_customer_workspace",
    "customer_workspace_expired",
    "validate_cleanup_evidence",
    "validate_customer_lifecycle_policy",
]
