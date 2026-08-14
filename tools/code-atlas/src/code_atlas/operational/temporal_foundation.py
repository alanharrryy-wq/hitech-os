from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from .evidence_foundation import VOLATILE_KEYS, canonical_digest, normalize_timestamp, parse_timestamp

SNAPSHOT_SCHEMA_VERSION = "code_atlas_semantic_snapshot.v1"

DEFAULT_SECTIONS = (
    "clients",
    "licenses",
    "devices",
    "sales",
    "deviceClaimCrosscheck",
    "salesLineage",
    "tenantScopeResolver",
    "schemaDriftGuard",
    "surfaceRoleMatrix",
    "goldenPathComparator",
    "supportResolverSummary",
)


def _row_count(value: Any) -> int:
    if isinstance(value, (list, tuple, set, Mapping)):
        return len(value)
    return 0 if value is None else 1


def make_semantic_snapshot(
    payload: Mapping[str, Any],
    *,
    observed_at: Any,
    source_ref: str,
    sections: Iterable[str] = DEFAULT_SECTIONS,
) -> dict[str, Any]:
    section_digests: dict[str, str] = {}
    metrics: dict[str, int] = {}
    for name in sections:
        if name not in payload:
            continue
        value = payload[name]
        section_digests[name] = canonical_digest(value, drop_keys=VOLATILE_KEYS)
        metrics[f"rows.{name}"] = _row_count(value)
    identity = {
        "schemaVersion": SNAPSHOT_SCHEMA_VERSION,
        "sourceRef": source_ref,
        "sections": section_digests,
    }
    return {
        "schemaVersion": SNAPSHOT_SCHEMA_VERSION,
        "sourceRef": source_ref,
        "observedAt": normalize_timestamp(observed_at),
        "snapshotDigest": canonical_digest(identity),
        "sectionDigests": dict(sorted(section_digests.items())),
        "metrics": dict(sorted(metrics.items())),
        "sectionCount": len(section_digests),
        "certifiable": False,
        "productionCertified": False,
    }


def validate_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    required = {"schemaVersion", "sourceRef", "observedAt", "snapshotDigest", "sectionDigests", "metrics"}
    missing = sorted(required - set(snapshot))
    if missing:
        return {"status": "BLOCKED_INVALID_SNAPSHOT", "missingFields": missing, "valid": False}
    if snapshot.get("schemaVersion") != SNAPSHOT_SCHEMA_VERSION:
        return {"status": "BLOCKED_UNSUPPORTED_SNAPSHOT_SCHEMA", "valid": False}
    if parse_timestamp(snapshot.get("observedAt")) is None:
        return {"status": "BLOCKED_INVALID_SNAPSHOT_TIMESTAMP", "valid": False}
    section_digests = snapshot.get("sectionDigests")
    if not isinstance(section_digests, Mapping):
        return {"status": "BLOCKED_INVALID_SECTION_DIGESTS", "valid": False}
    if any(len(str(value)) != 64 for value in section_digests.values()):
        return {"status": "BLOCKED_INVALID_SECTION_DIGEST", "valid": False}
    identity = {
        "schemaVersion": snapshot["schemaVersion"],
        "sourceRef": snapshot["sourceRef"],
        "sections": dict(section_digests),
    }
    expected = canonical_digest(identity)
    if expected != snapshot.get("snapshotDigest"):
        return {
            "status": "BLOCKED_SNAPSHOT_DIGEST_MISMATCH",
            "valid": False,
            "expectedDigest": expected,
            "actualDigest": snapshot.get("snapshotDigest"),
        }
    return {"status": "PASS_SNAPSHOT_VALID", "valid": True}


def compare_semantic_snapshots(
    base: Mapping[str, Any] | None,
    current: Mapping[str, Any],
) -> dict[str, Any]:
    current_validation = validate_snapshot(current)
    if not current_validation["valid"]:
        return {**current_validation, "comparable": False}
    if base is None:
        return {
            "status": "BLOCKED_MISSING_BASELINE",
            "comparable": False,
            "baseSnapshotDigest": None,
            "currentSnapshotDigest": current["snapshotDigest"],
            "productionCertified": False,
        }
    base_validation = validate_snapshot(base)
    if not base_validation["valid"]:
        return {**base_validation, "comparable": False}
    if base.get("schemaVersion") != current.get("schemaVersion"):
        return {
            "status": "BLOCKED_INCOMPARABLE_SCHEMA",
            "comparable": False,
            "baseSchema": base.get("schemaVersion"),
            "currentSchema": current.get("schemaVersion"),
        }
    left = dict(base.get("sectionDigests") or {})
    right = dict(current.get("sectionDigests") or {})
    added = sorted(set(right) - set(left))
    removed = sorted(set(left) - set(right))
    changed = sorted(key for key in set(left) & set(right) if left[key] != right[key])
    unchanged = sorted(key for key in set(left) & set(right) if left[key] == right[key])
    semantic_change = bool(added or removed or changed)
    return {
        "status": "CHANGE_DETECTED" if semantic_change else "PASS_NO_SEMANTIC_CHANGE",
        "comparable": True,
        "semanticChange": semantic_change,
        "baseSnapshotDigest": base["snapshotDigest"],
        "currentSnapshotDigest": current["snapshotDigest"],
        "addedSections": added,
        "removedSections": removed,
        "changedSections": changed,
        "unchangedSections": unchanged,
        "productionCertified": False,
        "doesNotProve": ["Runtime behavioral equivalence or production readiness."],
    }


def historical_trend(
    snapshots: Sequence[Mapping[str, Any]],
    metric: str,
) -> dict[str, Any]:
    valid = [item for item in snapshots if validate_snapshot(item).get("valid")]
    schemas = {item.get("schemaVersion") for item in valid}
    if len(schemas) > 1:
        return {"status": "BLOCKED_INCOMPARABLE_SCHEMA", "metric": metric, "points": []}
    points = []
    for snapshot in sorted(valid, key=lambda item: str(item.get("observedAt", ""))):
        value = (snapshot.get("metrics") or {}).get(metric)
        if isinstance(value, (int, float)):
            points.append({
                "observedAt": snapshot["observedAt"],
                "snapshotDigest": snapshot["snapshotDigest"],
                "value": value,
            })
    if len(points) < 2:
        return {
            "status": "BLOCKED_INSUFFICIENT_COMPARABLE_RUNS",
            "metric": metric,
            "points": points,
            "productionCertified": False,
        }
    return {
        "status": "TREND_AVAILABLE",
        "metric": metric,
        "points": points,
        "delta": points[-1]["value"] - points[0]["value"],
        "productionCertified": False,
        "doesNotProve": ["Causality or production health from trend direction alone."],
    }


def build_timeline(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    invalid: list[str] = []
    seen: set[str] = set()
    duplicates: list[str] = []
    for record in records:
        record_id = str(record.get("recordId") or "")
        if not record_id:
            invalid.append("missing_record_id")
            continue
        if record_id in seen:
            duplicates.append(record_id)
            continue
        seen.add(record_id)
        observed = parse_timestamp(record.get("observedAt"))
        if observed is None:
            invalid.append(record_id)
            continue
        events.append({
            "eventId": record_id,
            "observedAt": normalize_timestamp(observed),
            "capabilityId": record.get("capabilityId"),
            "sourceKind": record.get("sourceKind"),
            "sourceRef": record.get("sourceRef"),
            "payloadDigest": record.get("payloadDigest"),
            "scope": record.get("scope") or {},
        })
    events.sort(key=lambda item: (item["observedAt"], item["eventId"]))
    status = "TIMELINE_AVAILABLE" if events and not invalid else (
        "BLOCKED_INVALID_TIMELINE_EVIDENCE" if invalid else "BLOCKED_EMPTY_TIMELINE"
    )
    return {
        "status": status,
        "events": events,
        "invalidEvidence": invalid,
        "duplicateEvidenceIds": sorted(set(duplicates)),
        "productionCertified": False,
    }


def _snapshot_entry(names: Sequence[str]) -> Optional[str]:
    candidates = [name for name in names if name.endswith("SEMANTIC_SNAPSHOT.json")]
    if not candidates:
        return None
    return sorted(candidates, key=lambda name: (name.count("/"), len(name), name))[0]


def discover_prior_snapshots(
    result_root: str | Path | None,
    *,
    max_archives: int = 40,
    max_snapshots: int = 10,
) -> list[dict[str, Any]]:
    if not result_root:
        return []
    root = Path(result_root)
    if not root.exists() or not root.is_dir():
        return []
    archives = sorted(
        (path for path in root.glob("*result*.zip") if path.is_file()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )[:max_archives]
    snapshots: list[dict[str, Any]] = []
    seen: set[str] = set()
    for archive in archives:
        try:
            with zipfile.ZipFile(archive) as bundle:
                entry = _snapshot_entry(bundle.namelist())
                if not entry:
                    continue
                info = bundle.getinfo(entry)
                if info.file_size > 2 * 1024 * 1024:
                    continue
                data = json.loads(bundle.read(entry).decode("utf-8"))
        except (OSError, ValueError, KeyError, zipfile.BadZipFile, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict) or not validate_snapshot(data).get("valid"):
            continue
        digest = str(data.get("snapshotDigest"))
        if digest in seen:
            continue
        seen.add(digest)
        data = dict(data)
        data["archiveRef"] = str(archive)
        snapshots.append(data)
        if len(snapshots) >= max_snapshots:
            break
    return list(reversed(snapshots))
