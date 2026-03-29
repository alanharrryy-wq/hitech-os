#!/usr/bin/env python3
from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from tools.hos._core.stable_json import load_json, write_json

from .config import SentinelConfig
from .utils import now_utc_iso


@dataclass(frozen=True)
class ActiveSuppression:
    suppression_id: str
    match_type: str
    value: str
    owner: str
    reason: str
    expires_at: str


def _feedback_path(config: SentinelConfig) -> Path:
    raw = Path(config.false_positive_feedback_path)
    if raw.is_absolute():
        return raw.resolve()
    return (config.repo_root / raw).resolve()


def _audit_path(config: SentinelConfig) -> Path:
    raw = Path(config.false_positive_audit_path)
    if raw.is_absolute():
        return raw.resolve()
    return (config.repo_root / raw).resolve()


def _parse_iso(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def _default_expiry(days: int) -> str:
    delta_days = max(1, int(days))
    return (datetime.now(UTC) + timedelta(days=delta_days)).replace(microsecond=0).isoformat()


def _suppression_from_legacy(
    match_type: str,
    values: list[str],
    ttl_days: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, value in enumerate(sorted(set(values)), start=1):
        clean_value = str(value).strip()
        if not clean_value:
            continue
        rows.append(
            {
                "id": f"legacy-{match_type}-{idx}",
                "match": {
                    "type": match_type,
                    "value": clean_value,
                },
                "owner": "legacy",
                "reason": "migrated from legacy ignore list",
                "createdAt": now_utc_iso(),
                "expiresAt": _default_expiry(ttl_days),
                "active": True,
            }
        )
    return rows


def _normalize_feedback(payload: dict[str, Any], config: SentinelConfig) -> dict[str, Any]:
    ttl_days = int(payload.get("defaultTtlDays", config.false_positive_default_ttl_days))
    legacy_fingerprints = [str(item).strip() for item in payload.get("ignoredFingerprints", []) if str(item).strip()]
    legacy_kinds = [str(item).strip().lower() for item in payload.get("ignoredKinds", []) if str(item).strip()]
    legacy_path_globs = [str(item).replace("\\", "/").strip() for item in payload.get("ignoredPathGlobs", []) if str(item).strip()]

    suppressions = payload.get("suppressions", [])
    normalized_suppressions: list[dict[str, Any]] = []
    if isinstance(suppressions, list):
        for idx, item in enumerate(suppressions, start=1):
            if not isinstance(item, dict):
                continue
            match = item.get("match", {})
            if not isinstance(match, dict):
                continue
            match_type = str(match.get("type", "")).strip().lower()
            value = str(match.get("value", "")).replace("\\", "/").strip()
            if match_type not in {"fingerprint", "kind", "path_glob"} or not value:
                continue
            normalized_suppressions.append(
                {
                    "id": str(item.get("id", f"suppression-{idx}")).strip() or f"suppression-{idx}",
                    "match": {
                        "type": match_type,
                        "value": value,
                    },
                    "owner": str(item.get("owner", "unknown")).strip() or "unknown",
                    "reason": str(item.get("reason", "unspecified")).strip() or "unspecified",
                    "createdAt": str(item.get("createdAt", now_utc_iso())),
                    "expiresAt": str(item.get("expiresAt", _default_expiry(ttl_days))),
                    "active": bool(item.get("active", True)),
                }
            )

    normalized_suppressions.extend(_suppression_from_legacy("fingerprint", legacy_fingerprints, ttl_days))
    normalized_suppressions.extend(_suppression_from_legacy("kind", legacy_kinds, ttl_days))
    normalized_suppressions.extend(_suppression_from_legacy("path_glob", legacy_path_globs, ttl_days))

    deduped: dict[str, dict[str, Any]] = {}
    for item in normalized_suppressions:
        match = item.get("match", {})
        key = f"{match.get('type')}::{match.get('value')}"
        deduped[key] = item

    return {
        "version": 2,
        "updatedAt": str(payload.get("updatedAt", now_utc_iso())),
        "defaultTtlDays": ttl_days,
        "suppressions": sorted(deduped.values(), key=lambda row: str(row.get("id", ""))),
        "notes": payload.get(
            "notes",
            [
                "Each suppression must include owner, reason and expiresAt.",
                "Expired suppressions are ignored automatically and tracked in the audit log.",
            ],
        ),
    }


def ensure_feedback_template(config: SentinelConfig) -> Path:
    feedback_path = _feedback_path(config)
    if feedback_path.exists():
        return feedback_path
    template = _normalize_feedback({}, config=config)
    write_json(feedback_path, template, indent=2, sort_keys=True)
    return feedback_path


def load_feedback(config: SentinelConfig) -> dict[str, Any]:
    feedback_path = ensure_feedback_template(config)
    payload: dict[str, Any] = {}
    try:
        loaded = load_json(feedback_path)
        if isinstance(loaded, dict):
            payload = loaded
    except (OSError, ValueError):
        payload = {}
    normalized = _normalize_feedback(payload, config=config)
    normalized["path"] = feedback_path.as_posix()
    return normalized


def _active_suppressions(feedback: dict[str, Any]) -> tuple[list[ActiveSuppression], list[dict[str, Any]]]:
    now = datetime.now(UTC)
    active: list[ActiveSuppression] = []
    expired: list[dict[str, Any]] = []
    for item in feedback.get("suppressions", []):
        if not isinstance(item, dict):
            continue
        if not bool(item.get("active", True)):
            continue
        match = item.get("match", {})
        if not isinstance(match, dict):
            continue
        suppression_id = str(item.get("id", "")).strip()
        match_type = str(match.get("type", "")).strip().lower()
        value = str(match.get("value", "")).replace("\\", "/").strip()
        owner = str(item.get("owner", "unknown")).strip() or "unknown"
        reason = str(item.get("reason", "unspecified")).strip() or "unspecified"
        expires_at = str(item.get("expiresAt", "")).strip()
        expires_ts = _parse_iso(expires_at)
        if match_type not in {"fingerprint", "kind", "path_glob"} or not value or not suppression_id:
            continue
        if expires_ts is not None and expires_ts < now:
            expired.append(
                {
                    "id": suppression_id,
                    "matchType": match_type,
                    "value": value,
                    "owner": owner,
                    "reason": reason,
                    "expiresAt": expires_at,
                }
            )
            continue
        active.append(
            ActiveSuppression(
                suppression_id=suppression_id,
                match_type=match_type,
                value=value,
                owner=owner,
                reason=reason,
                expires_at=expires_at,
            )
        )
    return active, expired


def _suppression_match(finding: dict[str, Any], suppression: ActiveSuppression) -> bool:
    fingerprint = str(finding.get("fingerprint", "")).strip()
    kind = str(finding.get("kind", "")).strip().lower()
    path = str(finding.get("path", "")).replace("\\", "/").strip("/")
    if suppression.match_type == "fingerprint":
        return bool(fingerprint and fingerprint == suppression.value)
    if suppression.match_type == "kind":
        return bool(kind and kind == suppression.value)
    if suppression.match_type == "path_glob":
        pattern = suppression.value.replace("\\", "/").strip("/")
        return bool(pattern and fnmatch.fnmatch(path, pattern))
    return False


def apply_false_positive_feedback(
    findings: list[dict[str, Any]],
    feedback: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    active_suppressions, expired_suppressions = _active_suppressions(feedback=feedback)

    kept: list[dict[str, Any]] = []
    suppressed: list[dict[str, Any]] = []
    suppression_hits: dict[str, int] = {}

    for finding in findings:
        matched: ActiveSuppression | None = None
        for suppression in active_suppressions:
            if _suppression_match(finding=finding, suppression=suppression):
                matched = suppression
                break
        if matched is None:
            kept.append(finding)
            continue
        enriched = {
            **finding,
            "suppressedBy": {
                "id": matched.suppression_id,
                "matchType": matched.match_type,
                "owner": matched.owner,
                "reason": matched.reason,
                "expiresAt": matched.expires_at,
            },
        }
        suppressed.append(enriched)
        suppression_hits[matched.suppression_id] = suppression_hits.get(matched.suppression_id, 0) + 1

    raw_count = len(findings)
    suppressed_count = len(suppressed)
    false_positive_rate = 0.0 if raw_count <= 0 else float(suppressed_count) / float(raw_count)

    summary = {
        "rawFindingCount": raw_count,
        "suppressedFindingCount": suppressed_count,
        "findingCount": len(kept),
        "falsePositiveRate": round(false_positive_rate, 4),
        "feedbackPath": str(feedback.get("path", "")),
        "suppressionCount": len(active_suppressions),
        "expiredSuppressionCount": len(expired_suppressions),
    }
    audit_payload = {
        "timestamp": now_utc_iso(),
        "feedbackPath": str(feedback.get("path", "")),
        "activeSuppressionCount": len(active_suppressions),
        "expiredSuppressions": expired_suppressions,
        "suppressionHits": dict(sorted(suppression_hits.items())),
        "suppressedFindingCount": suppressed_count,
        "rawFindingCount": raw_count,
    }
    return kept, suppressed, summary, audit_payload


def write_false_positive_audit(config: SentinelConfig, payload: dict[str, Any]) -> str:
    audit_path = _audit_path(config)
    write_json(audit_path, payload, indent=2, sort_keys=True)
    return audit_path.as_posix()


def write_false_positive_metrics(
    config: SentinelConfig,
    summary: dict[str, Any],
    timestamp: str,
) -> dict[str, str]:
    telemetry_dir = config.telemetry_dir.resolve()
    telemetry_dir.mkdir(parents=True, exist_ok=True)
    slug = timestamp.replace(":", "").replace("-", "")
    payload = {
        "timestamp": timestamp,
        "summary": summary,
    }
    latest_path = (telemetry_dir / "false_positive_metrics_latest.json").resolve()
    snapshot_path = (telemetry_dir / f"false_positive_metrics_{slug}.json").resolve()
    write_json(latest_path, payload, indent=2, sort_keys=True)
    write_json(snapshot_path, payload, indent=2, sort_keys=True)
    return {
        "latest": latest_path.as_posix(),
        "snapshot": snapshot_path.as_posix(),
    }
