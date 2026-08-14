from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .contracts import ContractError, normalize_repo_path, require_exact_digest, require_nonempty_string, sha256_json, utc_now_iso


def build_portable_bundle_manifest(*, repository_snapshot: Mapping[str, Any], artifacts: list[Mapping[str, Any]], purpose: str, pack_id: str | None = None, verification_report_digest: str | None = None) -> dict[str, Any]:
    if not isinstance(repository_snapshot, Mapping):
        raise ContractError("repository_snapshot must be an object")
    for key in ("repositoryIdentity", "commitIdentity", "treeIdentity"):
        require_nonempty_string(repository_snapshot.get(key), f"repository_snapshot.{key}")
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
    manifest = {
        "schemaVersion": "code_atlas_portable_evidence_bundle.v1",
        "purpose": require_nonempty_string(purpose, "purpose"),
        "repositorySnapshot": deepcopy(dict(repository_snapshot)),
        "packId": pack_id,
        "verificationReportDigest": verification_report_digest,
        "artifacts": sorted(normalized_artifacts, key=lambda row: row["name"]),
        "generatedAt": utc_now_iso(),
        "sourceCodeIncluded": False,
        "certifiable": False,
        "productionCertified": False,
    }
    manifest["manifestDigest"] = sha256_json(manifest)
    return manifest
