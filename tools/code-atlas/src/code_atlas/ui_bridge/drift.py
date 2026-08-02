from __future__ import annotations
from pathlib import Path
from typing import Any

from .canonical import file_sha256


def _hash_entries(component: dict[str, Any]) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    hashes = component.get("sourceHashes", {})
    if isinstance(hashes, dict):
        for path, digest in hashes.items():
            resolved_path = component.get(path) if path in {"ownerFile", "renderSourceFile"} else path
            if not resolved_path:
                continue
            if isinstance(digest, str): result.append((str(resolved_path), digest.lower()))
            elif isinstance(digest, dict) and digest.get("sha256"): result.append((str(resolved_path), str(digest["sha256"]).lower()))
    elif isinstance(hashes, list):
        for item in hashes:
            if isinstance(item, dict):
                path = item.get("path") or item.get("file")
                digest = item.get("sha256") or item.get("sourceHash")
                if path and digest: result.append((str(path), str(digest).lower()))
    for target in component.get("visualTargets", []) if isinstance(component.get("visualTargets"), list) else []:
        if not isinstance(target, dict): continue
        path = target.get("styleSourceFile")
        digest = target.get("sourceHash")
        if path and digest: result.append((str(path), str(digest).lower()))
    return sorted(set(result))


def verify_component_drift(component: dict[str, Any], product_root: str | Path, governor_root: str | Path | None = None) -> dict[str, Any]:
    product = Path(product_root)
    governor = Path(governor_root) if governor_root else None
    entries = _hash_entries(component)
    checks: list[dict[str, Any]] = []
    for raw, expected in entries:
        rel = Path(raw.replace("\\", "/"))
        candidates = [product / rel]
        if governor: candidates.append(governor / rel)
        existing = next((p for p in candidates if p.is_file()), None)
        if existing is None:
            checks.append({"path": raw, "status": "MISSING_SOURCE", "expectedSha256": expected, "actualSha256": None})
            continue
        actual = file_sha256(existing).lower()
        checks.append({"path": raw, "status": "MATCH" if actual == expected else "DRIFT", "expectedSha256": expected, "actualSha256": actual})
    ok = bool(entries) and all(c["status"] == "MATCH" for c in checks)
    return {"schema": "prisma.ui.bridge.drift.v1", "ok": ok, "status": "PASS_NO_DRIFT" if ok else "BLOCKED_BY_DRIFT_OR_MISSING_SOURCE", "checks": checks}
