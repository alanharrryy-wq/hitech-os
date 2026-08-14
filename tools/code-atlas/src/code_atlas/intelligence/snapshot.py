from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .common import digest_json, git_identity, sha256_file

SCANNER_VERSION = "code_atlas_universal_intelligence.v1"
MATERIAL_CLASSES = {"authority", "schema", "ci"}

def build_snapshot(
    repo_root: str | Path,
    inventory: dict[str, Any],
    authorities: dict[str, Any],
    *,
    profile_id: str,
    profile_version: str | None,
    request_digest: str,
) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    authority_hashes = {
        str(row.get("path")): row.get("contentSha256")
        for row in authorities.get("candidates") or []
        if row.get("state") in {"SUPPORTED", "AUTHORITATIVE", "CONFLICTED"} and row.get("contentSha256")
    }
    material: dict[str, str | None] = {}
    for rel in inventory.get("databaseFiles") or []:
        path = repo / rel
        material[f"schema:{rel}"] = sha256_file(path) if path.is_file() else None
    for rel in inventory.get("ciFiles") or []:
        path = repo / rel
        material[f"ci:{rel}"] = sha256_file(path) if path.is_file() else None
    for rel, digest in authority_hashes.items():
        material[f"authority:{rel}"] = digest
    identity = git_identity(repo)
    payload = {
        "schemaVersion": "code_atlas_portable_snapshot.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "repository": {
            "remote": identity.get("remote"),
            "head": identity.get("head"),
            "tree": identity.get("tree"),
            "branch": identity.get("branch"),
            "dirty": identity.get("dirty"),
        },
        "profile": {"id": profile_id, "version": profile_version},
        "scannerVersion": SCANNER_VERSION,
        "requestDigest": request_digest,
        "authorityHashes": authority_hashes,
        "materialHashes": material,
        "inventoryDigest": digest_json({
            "fileCount": inventory.get("fileCount"),
            "paths": [row.get("path") for row in inventory.get("files") or []],
        }),
        "authorityDigest": digest_json(authority_hashes),
        "portable": True,
        "derivedIndexesAuthoritative": False,
        "productionCertified": False,
    }
    payload["snapshotDigest"] = digest_json(payload)
    return payload

def _current_material_hashes(repo: Path, previous: dict[str, Any]) -> dict[str, str | None]:
    current: dict[str, str | None] = {}
    for key in (previous.get("materialHashes") or {}):
        _, rel = key.split(":", 1)
        path = repo / rel
        current[key] = sha256_file(path) if path.is_file() else None
    return current

def assess_snapshot_freshness(snapshot: dict[str, Any], repo_root: str | Path) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    current = git_identity(repo)
    previous_repo = snapshot.get("repository") or {}
    current_material = _current_material_hashes(repo, snapshot)
    previous_material = snapshot.get("materialHashes") or {}
    changed = sorted(
        key for key in set(current_material) | set(previous_material)
        if current_material.get(key) != previous_material.get(key)
    )
    if changed:
        return {
            "status": "STALE_RESCAN_REQUIRED",
            "materialDrift": changed,
            "headChanged": current.get("head") != previous_repo.get("head"),
            "worktreeDirty": current.get("dirty"),
            "rescanRequired": True,
        }
    if current.get("dirty"):
        return {
            "status": "STALE_WORKTREE_DIRTY_RESCAN_REQUIRED",
            "materialDrift": [],
            "headChanged": current.get("head") != previous_repo.get("head"),
            "worktreeDirty": True,
            "rescanRequired": True,
        }
    if current.get("head") and current.get("head") == previous_repo.get("head"):
        return {
            "status": "REUSABLE_SAME_HEAD",
            "materialDrift": [],
            "headChanged": False,
            "worktreeDirty": False,
            "rescanRequired": False,
        }
    return {
        "status": "INCREMENTAL_REFRESH_ELIGIBLE",
        "materialDrift": [],
        "headChanged": True,
        "worktreeDirty": False,
        "rescanRequired": False,
    }
