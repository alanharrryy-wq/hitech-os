from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from .hashing import canonical_json_bytes, sha256_bytes, sha256_file
from .security import contained_path, validate_tx_id

RECEIPT_SCHEMA = "prisma.visual.application.receipt.v1"
RECEIPT_ROOT = "prisma-html/authority/rifat/visual-application-receipts"


def receipt_path(repo_root: Path, transaction_id: str) -> Path:
    validate_tx_id(transaction_id)
    return contained_path(
        repo_root,
        f"{RECEIPT_ROOT}/{transaction_id}.json",
        field="GVAE receipt",
    )


def _receipt_digest(payload: dict[str, Any]) -> str:
    body = copy.deepcopy(payload)
    body.pop("receiptDigest", None)
    return sha256_bytes(canonical_json_bytes(body))


def build_apply_receipt(
    *,
    repo_root: Path,
    request: dict[str, Any],
    target: dict[str, Any],
    transaction: dict[str, Any],
    receipt_file: Path,
    status: str,
) -> dict[str, Any]:
    source_path = target["canonicalSourcePath"]
    protected = {
        source_path,
        target.get("generatedOutputPath"),
        "prisma-html/authority/rifat/visual-source-manifest.json",
    }
    protected.discard(None)

    files: list[dict[str, Any]] = []
    receipt_rel = receipt_file.relative_to(repo_root).as_posix()
    for row in transaction["files"]:
        if row["path"] == receipt_rel or row["path"] not in protected:
            continue
        path = contained_path(repo_root, row["path"], field="receipt file")
        files.append(
            {
                "path": row["path"],
                "beforeSha256": row["beforeSha256"],
                "afterSha256": sha256_file(path) if path.exists() else None,
            }
        )

    verified = target.get("_authorization") or {}
    supplied = request.get("authorization") or {}
    receipt: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "transactionId": transaction["transactionId"],
        "targetId": target["targetId"],
        "surface": target["surface"],
        "status": status,
        "authorityCommit": request.get("authorityCommit"),
        "requestDigest": sha256_bytes(canonical_json_bytes(request)),
        "sourcePath": source_path,
        "generatedOutputPath": target.get("generatedOutputPath"),
        "files": sorted(files, key=lambda row: row["path"]),
        "authorization": {
            "authorityTaskId": supplied.get("authorityTaskId"),
            "authorityMeshArtifactSha256": supplied.get("authorityMeshArtifactSha256"),
            "authorityMeshRequestDigest": supplied.get("authorityMeshRequestDigest"),
            "mesh": verified.get("mesh"),
            "factoryLedgerDecisionDigest": verified.get("factoryLedgerDecisionDigest"),
            "uiBridge": verified.get("uiBridge"),
            "uiBridgePlanSha256": supplied.get("uiBridgePlanSha256"),
            "uiBridgeSemanticDiffSha256": supplied.get("uiBridgeSemanticDiffSha256"),
        },
        "evidenceClassification": "SOURCE_STATIC_ONLY",
        "runtimeVisualGreen": False,
        "ready": False,
        "doesNotProve": [
            "browser rendering",
            "runtime visual certification",
            "production readiness",
            "all-surface correctness",
            "authorization beyond the exact governed target",
        ],
    }
    receipt["receiptDigest"] = _receipt_digest(receipt)
    return receipt


def validate_receipt_digest(receipt: dict[str, Any]) -> bool:
    value = receipt.get("receiptDigest")
    return isinstance(value, str) and value == _receipt_digest(receipt)
