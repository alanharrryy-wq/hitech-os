#!/usr/bin/env python3
from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any

from tools.hos._core.stable_json import load_json, write_json

from .config import SentinelConfig
from .utils import now_utc_iso


def _feedback_path(config: SentinelConfig) -> Path:
    raw = Path(config.false_positive_feedback_path)
    if raw.is_absolute():
        return raw.resolve()
    return (config.repo_root / raw).resolve()


def _normalize_feedback(payload: dict[str, Any]) -> dict[str, Any]:
    fingerprints = sorted({str(item).strip() for item in payload.get("ignoredFingerprints", []) if str(item).strip()})
    kinds = sorted({str(item).strip().lower() for item in payload.get("ignoredKinds", []) if str(item).strip()})
    path_globs = sorted({str(item).replace("\\", "/").strip() for item in payload.get("ignoredPathGlobs", []) if str(item).strip()})
    return {
        "updatedAt": str(payload.get("updatedAt", now_utc_iso())),
        "ignoredFingerprints": fingerprints,
        "ignoredKinds": kinds,
        "ignoredPathGlobs": path_globs,
        "notes": payload.get("notes", []),
    }


def ensure_feedback_template(config: SentinelConfig) -> Path:
    feedback_path = _feedback_path(config)
    if feedback_path.exists():
        return feedback_path
    template = _normalize_feedback(
        {
            "updatedAt": now_utc_iso(),
            "ignoredFingerprints": [],
            "ignoredKinds": [],
            "ignoredPathGlobs": [],
            "notes": [
                "Populate ignoredFingerprints or ignoredPathGlobs to suppress known false positives.",
            ],
        }
    )
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
    normalized = _normalize_feedback(payload)
    normalized["path"] = feedback_path.as_posix()
    return normalized


def _is_suppressed(finding: dict[str, Any], feedback: dict[str, Any]) -> bool:
    fingerprint = str(finding.get("fingerprint", "")).strip()
    kind = str(finding.get("kind", "")).strip().lower()
    path = str(finding.get("path", "")).replace("\\", "/").strip("/")
    if fingerprint and fingerprint in set(feedback.get("ignoredFingerprints", [])):
        return True
    if kind and kind in set(feedback.get("ignoredKinds", [])):
        return True
    for pattern in feedback.get("ignoredPathGlobs", []):
        normalized_pattern = str(pattern).replace("\\", "/").strip("/")
        if normalized_pattern and fnmatch.fnmatch(path, normalized_pattern):
            return True
    return False


def apply_false_positive_feedback(
    findings: list[dict[str, Any]],
    feedback: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    suppressed: list[dict[str, Any]] = []
    for finding in findings:
        if _is_suppressed(finding=finding, feedback=feedback):
            suppressed.append(finding)
            continue
        kept.append(finding)

    raw_count = len(findings)
    suppressed_count = len(suppressed)
    false_positive_rate = 0.0 if raw_count <= 0 else float(suppressed_count) / float(raw_count)

    summary = {
        "rawFindingCount": raw_count,
        "suppressedFindingCount": suppressed_count,
        "findingCount": len(kept),
        "falsePositiveRate": round(false_positive_rate, 4),
        "feedbackPath": str(feedback.get("path", "")),
        "ignoredFingerprintCount": len(feedback.get("ignoredFingerprints", [])),
        "ignoredKindCount": len(feedback.get("ignoredKinds", [])),
        "ignoredPathGlobCount": len(feedback.get("ignoredPathGlobs", [])),
    }
    return kept, suppressed, summary


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
