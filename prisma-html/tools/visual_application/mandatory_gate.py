from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

from .receipts import RECEIPT_ROOT, RECEIPT_SCHEMA, validate_receipt_digest

PRISMA_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PRISMA_ROOT.parent
TARGET_INDEX = PRISMA_ROOT / "authority/rifat/prisma-ui/visual-control/target-index/manifest.json"
RECEIPT_PREFIX = RECEIPT_ROOT + "/"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class MandatoryGateError(RuntimeError):
    pass


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MandatoryGateError(f"{label} invalid: {exc}") from exc
    if not isinstance(value, dict):
        raise MandatoryGateError(f"{label} must be an object")
    return value


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git(repo_root: Path, *args: str) -> bytes:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise MandatoryGateError(
            f"git {' '.join(args)} failed: {proc.stderr.decode('utf-8', 'replace').strip()}"
        )
    return proc.stdout


def changed_paths(repo_root: Path, base: str, head: str) -> set[str]:
    raw = _git(repo_root, "diff", "--name-only", "--diff-filter=ACDMRTUXB", base, head, "--")
    return {line.strip() for line in raw.decode("utf-8").splitlines() if line.strip()}


def git_blob_hash(repo_root: Path, ref: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{ref}:{path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return _sha256(proc.stdout)


def current_file_hash(repo_root: Path, path: str) -> str | None:
    candidate = repo_root / path
    if not candidate.is_file() or candidate.is_symlink():
        return None
    return _sha256(candidate.read_bytes())


def protected_targets(index: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, set[str]]]:
    if index.get("schema") != "prisma.visual.application.target-index.v1":
        raise MandatoryGateError("target index schema invalid")
    if index.get("globalBlockers"):
        raise MandatoryGateError("target index has global blockers")

    by_target: dict[str, dict[str, Any]] = {}
    by_path: dict[str, set[str]] = defaultdict(set)
    for row in index.get("records", []):
        if not isinstance(row, dict):
            raise MandatoryGateError("target index record invalid")
        target_id = row.get("targetId")
        if not isinstance(target_id, str) or not target_id:
            raise MandatoryGateError("target index targetId invalid")
        if target_id in by_target:
            raise MandatoryGateError(f"duplicate targetId: {target_id}")
        by_target[target_id] = row
        if row.get("enforcement") == "DISCOVERY_ONLY":
            continue
        for field in ("canonicalSourcePath", "generatedOutputPath"):
            path = row.get(field)
            if isinstance(path, str) and path:
                by_path[path].add(target_id)
    return by_target, by_path


def _validate_receipt_shape(receipt: dict[str, Any], targets: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if receipt.get("schema") != RECEIPT_SCHEMA:
        return ["RECEIPT_SCHEMA_INVALID"]
    if not validate_receipt_digest(receipt):
        errors.append("RECEIPT_DIGEST_INVALID")
    target_id = receipt.get("targetId")
    target = targets.get(target_id)
    if target is None:
        errors.append(f"RECEIPT_TARGET_UNKNOWN:{target_id}")
        return errors
    if receipt.get("surface") != target.get("surface"):
        errors.append(f"RECEIPT_SURFACE_MISMATCH:{target_id}")
    if receipt.get("sourcePath") != target.get("canonicalSourcePath"):
        errors.append(f"RECEIPT_SOURCE_MISMATCH:{target_id}")
    if receipt.get("generatedOutputPath") != target.get("generatedOutputPath"):
        errors.append(f"RECEIPT_OUTPUT_MISMATCH:{target_id}")
    if receipt.get("evidenceClassification") != "SOURCE_STATIC_ONLY":
        errors.append(f"RECEIPT_CLASSIFICATION_INVALID:{target_id}")
    if receipt.get("runtimeVisualGreen") is not False or receipt.get("ready") is not False:
        errors.append(f"RECEIPT_FAKE_READY:{target_id}")
    if not isinstance(receipt.get("transactionId"), str) or not receipt["transactionId"].startswith("gvae-"):
        errors.append(f"RECEIPT_TRANSACTION_INVALID:{target_id}")
    if not isinstance(receipt.get("authorityCommit"), str) or not HEX40.fullmatch(receipt["authorityCommit"]):
        errors.append(f"RECEIPT_AUTHORITY_COMMIT_INVALID:{target_id}")
    if not isinstance(receipt.get("requestDigest"), str) or not HEX64.fullmatch(receipt["requestDigest"]):
        errors.append(f"RECEIPT_REQUEST_DIGEST_INVALID:{target_id}")

    auth = receipt.get("authorization")
    if not isinstance(auth, dict):
        errors.append(f"RECEIPT_AUTHORIZATION_MISSING:{target_id}")
        return errors
    mesh = auth.get("mesh")
    if not isinstance(mesh, dict):
        errors.append(f"RECEIPT_MESH_MISSING:{target_id}")
    else:
        if mesh.get("status") != "PASS_COMPOSED_AUTHORITY_MESH":
            errors.append(f"RECEIPT_MESH_NOT_PASS:{target_id}")
        if mesh.get("repoHead") != receipt.get("authorityCommit"):
            errors.append(f"RECEIPT_MESH_HEAD_MISMATCH:{target_id}")
        if mesh.get("requiredAuthorityCoveragePct") != 100:
            errors.append(f"RECEIPT_MESH_COVERAGE_INVALID:{target_id}")
        if mesh.get("blockers") != 0 or mesh.get("layerMapPresent") is not True:
            errors.append(f"RECEIPT_MESH_BLOCKED:{target_id}")
        for field in ("requestDigest", "artifactDigest"):
            if not isinstance(mesh.get(field), str) or not HEX64.fullmatch(mesh[field]):
                errors.append(f"RECEIPT_MESH_{field.upper()}_INVALID:{target_id}")
    decision = auth.get("factoryLedgerDecisionDigest")
    if not isinstance(decision, str) or not HEX64.fullmatch(decision):
        errors.append(f"RECEIPT_FACTORY_GATE_INVALID:{target_id}")
    bridge = auth.get("uiBridge")
    if not isinstance(bridge, dict) or not bridge.get("planId") or not isinstance(bridge.get("semanticDiffChecksum"), str):
        errors.append(f"RECEIPT_UI_BRIDGE_INVALID:{target_id}")

    files = receipt.get("files")
    if not isinstance(files, list) or not files:
        errors.append(f"RECEIPT_FILES_INVALID:{target_id}")
    else:
        seen: set[str] = set()
        for row in files:
            if not isinstance(row, dict) or set(row) != {"path", "beforeSha256", "afterSha256"}:
                errors.append(f"RECEIPT_FILE_ROW_INVALID:{target_id}")
                continue
            path = row.get("path")
            if not isinstance(path, str) or not path or path in seen:
                errors.append(f"RECEIPT_FILE_PATH_INVALID:{target_id}")
                continue
            seen.add(path)
            for field in ("beforeSha256", "afterSha256"):
                value = row.get(field)
                if value is not None and (not isinstance(value, str) or not HEX64.fullmatch(value)):
                    errors.append(f"RECEIPT_FILE_HASH_INVALID:{target_id}:{path}:{field}")
    return errors


def evaluate(
    *,
    index: dict[str, Any],
    changed: set[str],
    receipts: list[dict[str, Any]],
    before_hash: Callable[[str], str | None],
    after_hash: Callable[[str], str | None],
) -> dict[str, Any]:
    targets, protected = protected_targets(index)
    changed_protected = sorted(set(protected) & changed)
    if not changed_protected:
        return {
            "status": "PASS_GVAE_MANDATORY_GATE",
            "protectedChanged": [],
            "receiptCount": 0,
            "message": "No registered GVAE target source/projection changed.",
        }

    errors: list[str] = []
    receipt_rows: list[tuple[dict[str, Any], dict[str, Any]]] = []
    seen_receipt_ids: set[tuple[str, str]] = set()
    for receipt in receipts:
        errors.extend(_validate_receipt_shape(receipt, targets))
        target_id = receipt.get("targetId")
        tx_id = receipt.get("transactionId")
        key = (str(target_id), str(tx_id))
        if key in seen_receipt_ids:
            errors.append(f"DUPLICATE_RECEIPT:{target_id}:{tx_id}")
        seen_receipt_ids.add(key)
        if target_id in targets:
            receipt_rows.append((receipt, targets[target_id]))

    covered_receipts: set[tuple[str, str]] = set()
    for path in changed_protected:
        start = before_hash(path)
        finish = after_hash(path)
        if finish is None:
            errors.append(f"PROTECTED_TARGET_DELETION_FORBIDDEN:{path}")
            continue

        edges: list[tuple[str | None, str | None, str, str]] = []
        for receipt, target in receipt_rows:
            if receipt.get("targetId") not in protected[path]:
                continue
            for row in receipt.get("files", []):
                if isinstance(row, dict) and row.get("path") == path:
                    edges.append(
                        (
                            row.get("beforeSha256"),
                            row.get("afterSha256"),
                            str(receipt.get("targetId")),
                            str(receipt.get("transactionId")),
                        )
                    )

        if not edges:
            errors.append(f"GVAE_RECEIPT_REQUIRED:{path}")
            continue

        current = start
        remaining = list(edges)
        used: list[tuple[str | None, str | None, str, str]] = []
        safety = 0
        while current != finish and safety <= len(edges):
            safety += 1
            matches = [edge for edge in remaining if edge[0] == current]
            if len(matches) != 1:
                errors.append(
                    f"RECEIPT_CHAIN_INVALID:{path}:at={current}:matches={len(matches)}"
                )
                break
            edge = matches[0]
            remaining.remove(edge)
            used.append(edge)
            current = edge[1]
            if current is None:
                errors.append(f"RECEIPT_CHAIN_DELETES_TARGET:{path}")
                break

        if current != finish:
            errors.append(f"RECEIPT_CHAIN_FINAL_HASH_MISMATCH:{path}:{current}:{finish}")
        else:
            for _, _, target_id, tx_id in used:
                covered_receipts.add((target_id, tx_id))

    for receipt, _ in receipt_rows:
        key = (str(receipt.get("targetId")), str(receipt.get("transactionId")))
        if key not in covered_receipts:
            errors.append(f"EXTRANEOUS_OR_STALE_RECEIPT:{key[0]}:{key[1]}")

    return {
        "status": "BLOCKED_GVAE_MANDATORY_GATE" if errors else "PASS_GVAE_MANDATORY_GATE",
        "protectedChanged": changed_protected,
        "receiptCount": len(receipts),
        "errors": sorted(set(errors)),
    }


def _load_changed_receipts(repo_root: Path, changed: set[str]) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for path in sorted(changed):
        if not path.startswith(RECEIPT_PREFIX) or not path.endswith(".json"):
            continue
        candidate = repo_root / path
        if not candidate.is_file() or candidate.is_symlink():
            raise MandatoryGateError(f"receipt missing or unsafe: {path}")
        docs.append(_load_json(candidate, path))
    return docs


def run(repo_root: Path, base: str, head: str) -> dict[str, Any]:
    index = _load_json(repo_root / TARGET_INDEX.relative_to(REPO_ROOT), "GVAE target index")
    changed = changed_paths(repo_root, base, head)
    receipts = _load_changed_receipts(repo_root, changed)
    return evaluate(
        index=index,
        changed=changed,
        receipts=receipts,
        before_hash=lambda path: git_blob_hash(repo_root, base, path),
        after_hash=lambda path: current_file_hash(repo_root, path),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail-closed CI gate requiring GVAE receipts for registered visual target mutations."
    )
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    try:
        result = run(Path(args.repo_root).resolve(), args.base, args.head)
    except (MandatoryGateError, OSError, ValueError, KeyError, TypeError) as exc:
        result = {
            "status": "BLOCKED_GVAE_MANDATORY_GATE",
            "protectedChanged": [],
            "receiptCount": 0,
            "errors": [f"GATE_EXECUTION_ERROR:{exc}"],
        }
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("status") == "PASS_GVAE_MANDATORY_GATE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
