from __future__ import annotations

import hashlib
import re
import zipfile
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .evidence_foundation import FreshnessPolicy, assess_audit_completeness, assess_freshness

EVIDENCE_ENTRY_RE = re.compile(r"(manifest|verif|result|smoke|check|report|continuation|evidence)", re.I)


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_runtime_artifact(
    path: str | Path,
    *,
    expected_sha256: str | None = None,
    required_entries: Iterable[str] = (),
) -> dict[str, Any]:
    artifact = Path(path)
    if not artifact.exists() or not artifact.is_file():
        return {
            "artifact": str(artifact),
            "status": "BLOCKED_MISSING_ARTIFACT",
            "verified": False,
            "productionCertified": False,
        }
    try:
        actual_digest = sha256_file(artifact)
    except OSError as exc:
        return {
            "artifact": str(artifact),
            "status": "BLOCKED_ARTIFACT_READ_ERROR",
            "verified": False,
            "error": f"{type(exc).__name__}: {exc}",
            "productionCertified": False,
        }
    if expected_sha256 and actual_digest.lower() != expected_sha256.lower():
        return {
            "artifact": str(artifact),
            "status": "BLOCKED_ARTIFACT_DIGEST_MISMATCH",
            "verified": False,
            "sha256": actual_digest,
            "expectedSha256": expected_sha256.lower(),
            "productionCertified": False,
        }
    try:
        with zipfile.ZipFile(artifact) as bundle:
            names = bundle.namelist()
            bad_member = bundle.testzip()
    except (OSError, zipfile.BadZipFile) as exc:
        return {
            "artifact": str(artifact),
            "status": "BLOCKED_CORRUPT_ARTIFACT",
            "verified": False,
            "sha256": actual_digest,
            "error": f"{type(exc).__name__}: {exc}",
            "productionCertified": False,
        }
    if bad_member:
        return {
            "artifact": str(artifact),
            "status": "BLOCKED_CORRUPT_ARTIFACT_MEMBER",
            "verified": False,
            "sha256": actual_digest,
            "badMember": bad_member,
            "productionCertified": False,
        }
    required = [str(item) for item in required_entries if str(item)]
    missing = [entry for entry in required if entry not in names]
    if missing:
        return {
            "artifact": str(artifact),
            "status": "BLOCKED_REQUIRED_EVIDENCE_ENTRY_MISSING",
            "verified": False,
            "sha256": actual_digest,
            "missingEntries": missing,
            "entryCount": len(names),
            "productionCertified": False,
        }
    interesting = sorted(name for name in names if EVIDENCE_ENTRY_RE.search(name))
    status = "SOURCE_BACKED_ARTIFACT_VERIFIED" if interesting else "BLOCKED_NO_RECOGNIZABLE_EVIDENCE_ENTRIES"
    return {
        "artifact": str(artifact),
        "status": status,
        "verified": status == "SOURCE_BACKED_ARTIFACT_VERIFIED",
        "sha256": actual_digest,
        "entryCount": len(names),
        "evidenceEntries": interesting[:100],
        "productionCertified": False,
        "doesNotProve": ["The semantic truth of evidence entries or production readiness."],
    }


def harden_runtime_evidence_links(rows: Any) -> list[dict[str, Any]]:
    if not isinstance(rows, list) or not rows:
        return [{"status": "BLOCKED_NO_RUNTIME_EVIDENCE_LINKS", "verified": False, "productionCertified": False}]
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            out.append({"status": "BLOCKED_INVALID_RUNTIME_EVIDENCE_ROW", "verified": False, "productionCertified": False})
            continue
        path = row.get("zip") or row.get("artifact") or row.get("path")
        if not path:
            copied = dict(row)
            copied.update({
                "verified": False,
                "productionCertified": False,
                "doesNotProve": ["Artifact integrity without an artifact path and digest."],
            })
            if not str(copied.get("status", "")).startswith("BLOCKED"):
                copied["status"] = "BLOCKED_ARTIFACT_PATH_MISSING"
            out.append(copied)
            continue
        expected = row.get("sha256") or row.get("expectedSha256")
        verified = validate_runtime_artifact(str(path), expected_sha256=str(expected) if expected else None)
        out.append({**dict(row), **verified})
    return out


def build_staleness_rows(
    evidence_records: Sequence[Mapping[str, Any]],
    policies: Mapping[str, FreshnessPolicy],
    *,
    now: Any,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for record in evidence_records:
        source_kind = str(record.get("sourceKind") or "")
        policy = policies.get(source_kind)
        assessment = assess_freshness(record.get("observedAt"), policy, now=now)
        out.append({
            "recordId": record.get("recordId"),
            "capabilityId": record.get("capabilityId"),
            "sourceKind": source_kind,
            **assessment,
            "productionCertified": False,
        })
    return out or [{"status": "BLOCKED_NO_EVIDENCE_RECORDS", "fresh": False, "productionCertified": False}]


def build_audit_completeness(
    required_actions: Iterable[str] | None,
    events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return [assess_audit_completeness(required_actions, events)]
