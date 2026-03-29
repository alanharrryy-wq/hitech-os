#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.hos._core.stable_json import load_json, write_json

from .config import SentinelConfig
from .security_scanner import scan_text_security
from .utils import now_utc_iso


def _dataset_path(config: SentinelConfig, dataset_path: str | None = None) -> Path:
    raw = Path(dataset_path or config.security_eval_dataset_path)
    if raw.is_absolute():
        return raw.resolve()
    return (config.repo_root / raw).resolve()


def _normalize_expected_row(row: dict[str, Any]) -> dict[str, Any] | None:
    kind = str(row.get("kind", "")).strip()
    line = int(row.get("line", 0)) if str(row.get("line", "")).strip() else 0
    severity = str(row.get("severity", "")).strip().lower()
    if not kind or line <= 0:
        return None
    normalized = {
        "kind": kind,
        "line": line,
    }
    if severity:
        normalized["severity"] = severity
    return normalized


def _normalize_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    cases = payload.get("cases", [])
    normalized_cases: list[dict[str, Any]] = []
    if isinstance(cases, list):
        for idx, item in enumerate(cases, start=1):
            if not isinstance(item, dict):
                continue
            rel_path = str(item.get("path", f"case_{idx}.txt")).replace("\\", "/").strip()
            content = str(item.get("content", ""))
            expected_raw = item.get("expected", [])
            expected: list[dict[str, Any]] = []
            if isinstance(expected_raw, list):
                for expected_row in expected_raw:
                    if not isinstance(expected_row, dict):
                        continue
                    normalized = _normalize_expected_row(expected_row)
                    if normalized is not None:
                        expected.append(normalized)
            normalized_cases.append(
                {
                    "id": str(item.get("id", f"case-{idx}")).strip() or f"case-{idx}",
                    "path": rel_path,
                    "content": content,
                    "expected": expected,
                }
            )
    return {
        "version": int(payload.get("version", 1)),
        "cases": normalized_cases,
    }


def _finding_signature(path: str, row: dict[str, Any]) -> str:
    return f"{path}::{row.get('kind')}::{int(row.get('line', 0))}"


def _round(value: float) -> float:
    return round(value, 4)


def evaluate_security_dataset(
    config: SentinelConfig,
    dataset_path: str | None = None,
) -> dict[str, Any]:
    resolved_dataset_path = _dataset_path(config=config, dataset_path=dataset_path)
    if not resolved_dataset_path.exists():
        return {
            "timestamp": now_utc_iso(),
            "datasetPath": resolved_dataset_path.as_posix(),
            "status": "skipped",
            "reason": "dataset_not_found",
            "metrics": {
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "tp": 0,
                "fp": 0,
                "fn": 0,
            },
            "thresholds": {
                "minPrecision": float(config.security_eval_min_precision),
                "minRecall": float(config.security_eval_min_recall),
                "minF1": float(config.security_eval_min_f1),
            },
            "passed": False,
            "cases": [],
        }

    raw_payload = load_json(resolved_dataset_path)
    if not isinstance(raw_payload, dict):
        raise ValueError(f"security eval dataset must be an object: {resolved_dataset_path}")
    dataset = _normalize_dataset(raw_payload)

    tp = 0
    fp = 0
    fn = 0
    case_rows: list[dict[str, Any]] = []

    for case in dataset.get("cases", []):
        rel_path = str(case.get("path", "")).replace("\\", "/")
        expected_rows = list(case.get("expected", []))
        findings = scan_text_security(config=config, rel_path=rel_path, text=str(case.get("content", "")))

        expected_signatures = {_finding_signature(rel_path, row) for row in expected_rows}
        actual_signatures = {_finding_signature(rel_path, row) for row in findings}

        case_tp = len(expected_signatures & actual_signatures)
        case_fp = len(actual_signatures - expected_signatures)
        case_fn = len(expected_signatures - actual_signatures)
        tp += case_tp
        fp += case_fp
        fn += case_fn

        case_rows.append(
            {
                "id": str(case.get("id", "")),
                "path": rel_path,
                "expectedCount": len(expected_signatures),
                "actualCount": len(actual_signatures),
                "tp": case_tp,
                "fp": case_fp,
                "fn": case_fn,
            }
        )

    precision = 0.0 if (tp + fp) <= 0 else float(tp) / float(tp + fp)
    recall = 0.0 if (tp + fn) <= 0 else float(tp) / float(tp + fn)
    f1 = 0.0 if (precision + recall) <= 0 else (2.0 * precision * recall) / (precision + recall)

    thresholds = {
        "minPrecision": float(config.security_eval_min_precision),
        "minRecall": float(config.security_eval_min_recall),
        "minF1": float(config.security_eval_min_f1),
    }
    passed = precision >= thresholds["minPrecision"] and recall >= thresholds["minRecall"] and f1 >= thresholds["minF1"]

    return {
        "timestamp": now_utc_iso(),
        "datasetPath": resolved_dataset_path.as_posix(),
        "status": "ok",
        "metrics": {
            "precision": _round(precision),
            "recall": _round(recall),
            "f1": _round(f1),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "caseCount": len(case_rows),
        },
        "thresholds": thresholds,
        "passed": bool(passed),
        "cases": case_rows,
    }


def write_security_eval_files(config: SentinelConfig, payload: dict[str, Any]) -> dict[str, str]:
    config.telemetry_dir.mkdir(parents=True, exist_ok=True)
    timestamp_slug = str(payload.get("timestamp", now_utc_iso())).replace(":", "").replace("-", "")
    latest_path = (config.telemetry_dir / "security_eval_latest.json").resolve()
    snapshot_path = (config.telemetry_dir / f"security_eval_{timestamp_slug}.json").resolve()
    write_json(latest_path, payload, indent=2, sort_keys=True)
    write_json(snapshot_path, payload, indent=2, sort_keys=True)
    return {
        "latest": latest_path.as_posix(),
        "snapshot": snapshot_path.as_posix(),
    }


def load_latest_security_eval(config: SentinelConfig) -> dict[str, Any] | None:
    latest_path = (config.telemetry_dir / "security_eval_latest.json").resolve()
    if not latest_path.exists():
        return None
    payload = load_json(latest_path)
    if isinstance(payload, dict):
        return payload
    return None
