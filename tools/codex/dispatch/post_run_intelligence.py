from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

CODEX_ROOT = Path(__file__).resolve().parents[1]
if str(CODEX_ROOT) not in sys.path:
    sys.path.insert(0, str(CODEX_ROOT))

from factory import common, contracts, schemas  # noqa: E402

REVIEWER = "R_reviewer"
PLANNER = "E_planner"
INTEGRATOR = "Z_aggregator"
LEGACY_INTEGRATOR = "Z_integrator"

SEVERITY_TO_PRIORITY = {
    "critical": "P0",
    "high": "P1",
    "medium": "P2",
    "low": "P3",
}
PRIORITY_TO_NUMERIC = {
    "P0": 95,
    "P1": 85,
    "P2": 75,
    "P3": 65,
}
CATEGORY_TO_TASK_BANK = {
    "hotspot_refactor": "reliability",
    "protected_node_promotion": "reliability",
    "dependency_creep_review": "automation",
    "blast_radius_risk": "reliability",
    "bridge_node_risk": "reliability",
    "layer_violation_review": "reliability",
    "repeated_architecture_risk": "dx",
}
FINDING_ORDER = (
    "hotspot_refactor",
    "protected_node_promotion",
    "dependency_creep_review",
    "blast_radius_risk",
    "bridge_node_risk",
    "layer_violation_review",
    "repeated_architecture_risk",
)
ARTIFACT_FILES = {
    "gravity": "GRAVITY_REPORT.json",
    "impact": "IMPACT_CONE_REPORT.json",
    "dependency": "DEPENDENCY_DIFF.json",
    "dispatch": "DISPATCH_RECOMMENDATIONS.json",
    "protected": "PROTECTED_NODES.json",
}


def _iso_utc(value: dt.datetime) -> str:
    return value.replace(microsecond=0).isoformat()


def _safe_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _fingerprint(*parts: Any) -> str:
    material = json.dumps(parts, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:20]


def _normalize_risk(value: Any) -> str:
    probe = str(value or "").strip().upper()
    if probe in {"CRITICAL", "HIGH", "MEDIUM", "LOW", "NONE"}:
        return probe
    return "LOW"


def _severity_from_risk(value: Any) -> str:
    probe = _normalize_risk(value)
    return {
        "CRITICAL": "critical",
        "HIGH": "high",
        "MEDIUM": "medium",
        "LOW": "low",
        "NONE": "low",
    }[probe]


def _priority_numeric(value: Any) -> int:
    text = str(value or "").strip().upper()
    if text in PRIORITY_TO_NUMERIC:
        return PRIORITY_TO_NUMERIC[text]
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _value_score(severity: str, confidence: float) -> int:
    base = {
        "critical": 95,
        "high": 85,
        "medium": 75,
        "low": 65,
    }.get(str(severity).strip().lower(), 65)
    return max(0, min(100, base + int(round(max(0.0, min(1.0, confidence)) * 5.0))))


def _coerce_confidence(value: Any, default: float = 0.7) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return float(default)


def _z_bundle_dir(run_id: str) -> Path:
    return common.resolve_bundle_dir(run_id, INTEGRATOR, prefer_existing=True)


def _artifact_ref(filename: str) -> str:
    return f"{INTEGRATOR}/{filename}"


def _node_index(gravity_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for item in gravity_payload.get("nodes", []):
        if not isinstance(item, dict):
            continue
        node_id = str(item.get("node_id", "")).strip()
        if node_id:
            index[node_id] = dict(item)
    return index


def _node_meta(node_id: str, node_index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return dict(node_index.get(node_id, {}))


def _allowed_paths_from_meta(meta: dict[str, Any], *, fallback_worker: str) -> list[str]:
    path = str(meta.get("canonical_path", "")).replace("\\", "/").strip()
    if path:
        return [path]
    scope = meta.get("scope", {}) if isinstance(meta.get("scope", {}), dict) else {}
    scope_path = str(scope.get("scope_path", "")).replace("\\", "/").strip()
    if scope_path:
        return [scope_path]
    owner = str(meta.get("owner_worker", fallback_worker)).strip()
    if owner == "B_tooling":
        return ["tools/**"]
    if owner == "C_features":
        return ["apps/**"]
    if owner == "D_validation":
        return ["tests/**"]
    return ["docs/**" if fallback_worker == "D_validation" else "tools/codex/**"]


def _infer_worker_affinity(category: str, meta: dict[str, Any], proposed_owner: str = "") -> list[str]:
    owner = str(proposed_owner or meta.get("owner_worker", "")).strip()
    if owner in {"A_core", "B_tooling", "C_features", "D_validation"}:
        return [owner]
    path = str(meta.get("canonical_path", "")).replace("\\", "/").strip().lower()
    if path.startswith("tools/"):
        return ["B_tooling"]
    if path.startswith("apps/"):
        return ["C_features"]
    if path.startswith("tests/") or "/test" in path:
        return ["D_validation"]
    if category == "dependency_creep_review":
        return ["B_tooling"]
    if category == "blast_radius_risk":
        return ["A_core", "D_validation"]
    if category == "protected_node_promotion":
        return ["A_core", "D_validation"]
    return ["A_core"]


def _acceptance_checks(worker_affinity: list[str]) -> list[str]:
    primary = worker_affinity[0] if worker_affinity else "A_core"
    checks = [
        f"python -m tools.codex.factory bundle-validate --run-id <RUN_ID> --workers {primary},D_validation,Z_aggregator",
        "python -m tools.codex.factory integrate --run-id <RUN_ID> --workers A_core,B_tooling,C_features,D_validation,Z_aggregator",
    ]
    deduped: list[str] = []
    for item in checks:
        if item not in deduped:
            deduped.append(item)
    return deduped


def _estimate_change_size(value_score: int) -> int:
    if value_score >= 90:
        return 2200
    if value_score >= 80:
        return 1600
    if value_score >= 70:
        return 1200
    return 800


def _severity_bucket_counts(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for finding in findings:
        severity = str(finding.get("severity", "low")).lower()
        if severity in counts:
            counts[severity] += 1
    return counts


def _category_counts(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for finding in findings:
        category = str(finding.get("category", "")).strip()
        if not category:
            continue
        counts[category] = counts.get(category, 0) + 1
    return counts


def _dedupe_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_fp: dict[str, dict[str, Any]] = {}
    for finding in findings:
        fingerprint = str(finding.get("fingerprint", "")).strip()
        if not fingerprint:
            continue
        current = by_fp.get(fingerprint)
        if current is None:
            by_fp[fingerprint] = finding
            continue
        current_score = _value_score(str(current.get("severity", "low")), _coerce_confidence(current.get("confidence")))
        new_score = _value_score(str(finding.get("severity", "low")), _coerce_confidence(finding.get("confidence")))
        if new_score > current_score:
            by_fp[fingerprint] = finding
    ordered = sorted(
        by_fp.values(),
        key=lambda item: (
            FINDING_ORDER.index(str(item.get("category", "repeated_architecture_risk")))
            if str(item.get("category", "")) in FINDING_ORDER
            else len(FINDING_ORDER),
            -_priority_numeric(SEVERITY_TO_PRIORITY.get(str(item.get("severity", "low")).lower(), "P3")),
            str(item.get("finding_id", "")),
        ),
    )
    for index, finding in enumerate(ordered, start=1):
        finding["finding_id"] = f"FINDING-{index:03d}-{str(finding.get('fingerprint'))[:8]}"
    return ordered


def _build_finding(
    *,
    category: str,
    title: str,
    description: str,
    severity: str,
    confidence: float,
    source_artifacts: list[str],
    source_refs: list[str],
    key_parts: list[Any],
) -> dict[str, Any]:
    return {
        "finding_id": "",
        "category": category,
        "severity": severity,
        "confidence": _coerce_confidence(confidence),
        "title": title,
        "description": description,
        "source_artifacts": sorted(set(source_artifacts)),
        "source_refs": [item for item in source_refs if str(item).strip()],
        "fingerprint": _fingerprint("finding", category, *key_parts),
    }

def _findings_from_gravity(gravity_payload: dict[str, Any], node_index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    for candidate in gravity_payload.get("refactor_candidates", []):
        if not isinstance(candidate, dict):
            continue
        node_id = str(candidate.get("node_id", "")).strip()
        meta = _node_meta(node_id, node_index)
        title_target = str(meta.get("display_name") or meta.get("canonical_path") or node_id or candidate.get("candidate_id", "hotspot")).strip()
        drivers = candidate.get("centrality_drivers", []) if isinstance(candidate.get("centrality_drivers", []), list) else []
        driver_names = [str(item.get("metric", "")).strip() for item in drivers if isinstance(item, dict) and str(item.get("metric", "")).strip()]
        details = ", ".join(driver_names[:3]) if driver_names else "graph hotspot signals"
        findings.append(
            _build_finding(
                category="hotspot_refactor",
                title=f"Refactor hotspot: {title_target}",
                description=(
                    f"{title_target} was marked for {candidate.get('recommendation_type', 'refactor review')} "
                    f"based on {details}."
                ),
                severity=_severity_from_risk(candidate.get("risk_level")),
                confidence=_coerce_confidence(candidate.get("confidence"), 0.75),
                source_artifacts=[_artifact_ref(ARTIFACT_FILES["gravity"])],
                source_refs=[str(candidate.get("candidate_id", "")), node_id],
                key_parts=[node_id, candidate.get("candidate_id"), candidate.get("recommendation_type")],
            )
        )

    for recommendation in gravity_payload.get("protected_node_recommendations", []):
        if not isinstance(recommendation, dict):
            continue
        node_id = str(recommendation.get("node_id", "")).strip()
        meta = _node_meta(node_id, node_index)
        title_target = str(meta.get("display_name") or meta.get("canonical_path") or node_id or recommendation.get("recommendation_id", "protected-node")).strip()
        findings.append(
            _build_finding(
                category="protected_node_promotion",
                title=f"Protected node review: {title_target}",
                description=(
                    f"{title_target} should be reviewed for protection change "
                    f"{recommendation.get('current_protection_level', 'UNKNOWN')} -> "
                    f"{recommendation.get('recommended_protection_level', 'UNKNOWN')}."
                ),
                severity=_severity_from_risk(recommendation.get("risk_level")),
                confidence=0.8,
                source_artifacts=[_artifact_ref(ARTIFACT_FILES["gravity"]), _artifact_ref(ARTIFACT_FILES["protected"])],
                source_refs=[str(recommendation.get("recommendation_id", "")), node_id],
                key_parts=[node_id, recommendation.get("recommended_protection_level"), recommendation.get("recommendation_type")],
            )
        )

    for flag in gravity_payload.get("architecture_risk_flags", []):
        if not isinstance(flag, dict):
            continue
        flag_type = str(flag.get("flag_type", "")).strip()
        node_ids = [str(item).strip() for item in flag.get("node_ids", []) if str(item).strip()]
        category = {
            "SINGLE_POINT_OF_FAILURE": "bridge_node_risk",
            "COUPLING_HOTSPOT": "dependency_creep_review",
            "DEPENDENCY_DRIFT": "dependency_creep_review",
            "EXTERNAL_BLAST_RADIUS": "blast_radius_risk",
            "CYCLE_CLUSTER": "layer_violation_review",
            "CONTRACT_FRAGILITY": "layer_violation_review",
            "OWNERSHIP_FRAGMENTATION": "layer_violation_review",
            "VALIDATION_GAP_CLUSTER": "layer_violation_review",
        }.get(flag_type, "repeated_architecture_risk")
        title_target = ", ".join(node_ids[:3]) if node_ids else str(flag.get("flag_id", "architecture-risk")).strip()
        findings.append(
            _build_finding(
                category=category,
                title=f"Architecture risk: {flag_type or 'UNCLASSIFIED'}",
                description=(
                    f"{flag_type or 'Architecture risk'} remains {flag.get('status', 'OPEN')} "
                    f"for {title_target}."
                ),
                severity=_severity_from_risk(flag.get("severity")),
                confidence=0.78,
                source_artifacts=[_artifact_ref(ARTIFACT_FILES["gravity"])],
                source_refs=[str(flag.get("flag_id", "")), *node_ids],
                key_parts=[flag_type, *node_ids],
            )
        )

    return findings


def _findings_from_impact(impact_payload: dict[str, Any], node_index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for entity in impact_payload.get("changed_entities", []):
        if not isinstance(entity, dict):
            continue
        risk = _normalize_risk(entity.get("risk_level"))
        radius = entity.get("impact_radius", {}) if isinstance(entity.get("impact_radius", {}), dict) else {}
        radius_category = str(radius.get("category", "")).strip().upper()
        if risk not in {"HIGH", "CRITICAL"} and radius_category not in {"CROSS_WORKER", "REPO_WIDE"}:
            continue
        entity_id = str(entity.get("entity_id", "")).strip()
        meta = _node_meta(entity_id, node_index)
        title_target = str(entity.get("canonical_path") or meta.get("display_name") or entity_id).strip()
        findings.append(
            _build_finding(
                category="blast_radius_risk",
                title=f"High-risk impact cone: {title_target}",
                description=(
                    f"{title_target} has impact radius {radius_category or 'LOCAL'} "
                    f"with risk level {risk}."
                ),
                severity=_severity_from_risk(risk),
                confidence=0.74,
                source_artifacts=[_artifact_ref(ARTIFACT_FILES["impact"])],
                source_refs=[entity_id],
                key_parts=[entity_id, radius_category, risk],
            )
        )
    return findings


def _findings_from_dependency_diff(dependency_payload: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    for change in dependency_payload.get("classification_changes", []):
        if not isinstance(change, dict):
            continue
        node_id = str(change.get("node_id", "")).strip()
        delta = float(change.get("delta", 0.0) or 0.0)
        if abs(delta) < 10 and "HIGH_CHURN" not in {str(code).strip() for code in change.get("reason_codes", [])}:
            continue
        findings.append(
            _build_finding(
                category="dependency_creep_review",
                title=f"Dependency drift review: {node_id or 'unknown-node'}",
                description=(
                    f"{node_id or 'Unknown node'} changed gravity classification with delta {delta:.2f}."
                ),
                severity="high" if abs(delta) >= 25 else "medium",
                confidence=0.72,
                source_artifacts=[_artifact_ref(ARTIFACT_FILES["dependency"])],
                source_refs=[node_id],
                key_parts=[node_id, delta],
            )
        )

    for change in dependency_payload.get("contract_changes", []):
        if not isinstance(change, dict):
            continue
        contract_id = str(change.get("contract_id", "")).strip()
        change_type = str(change.get("change_type", "")).strip().upper()
        if "BREAKING" not in change_type and change_type not in {"OWNER_CHANGED", "CONSUMER_SET_CHANGED", "PRODUCER_SET_CHANGED"}:
            continue
        findings.append(
            _build_finding(
                category="layer_violation_review",
                title=f"Contract fragility review: {contract_id or 'unknown-contract'}",
                description=f"{contract_id or 'Unknown contract'} reported dependency diff change {change_type}.",
                severity="high" if "BREAKING" in change_type else "medium",
                confidence=0.76,
                source_artifacts=[_artifact_ref(ARTIFACT_FILES["dependency"])],
                source_refs=[contract_id],
                key_parts=[contract_id, change_type],
            )
        )

    return findings


def _historical_repeat_counts(run_id: str) -> tuple[int, dict[str, int]]:
    runs_considered = 0
    counts: dict[str, int] = {}
    for run_root in sorted(common.RUNS_DIR.glob("*")):
        if not run_root.is_dir() or run_root.name == run_id:
            continue
        gravity_path = common.resolve_bundle_dir(run_root.name, INTEGRATOR, prefer_existing=True) / ARTIFACT_FILES["gravity"]
        if not gravity_path.exists():
            continue
        gravity_payload = _safe_json(gravity_path, {})
        if not isinstance(gravity_payload, dict):
            continue
        runs_considered += 1
        for item in gravity_payload.get("architecture_risk_flags", []):
            if not isinstance(item, dict):
                continue
            flag_type = str(item.get("flag_type", "")).strip()
            node_ids = [str(node).strip() for node in item.get("node_ids", []) if str(node).strip()]
            key = _fingerprint("repeat", flag_type, *sorted(node_ids))
            counts[key] = counts.get(key, 0) + 1
        for item in gravity_payload.get("refactor_candidates", []):
            if not isinstance(item, dict):
                continue
            key = _fingerprint(
                "repeat",
                str(item.get("node_id", "")).strip(),
                str(item.get("recommendation_type", "")).strip(),
            )
            counts[key] = counts.get(key, 0) + 1
    return runs_considered, counts


def _repeat_findings(
    findings: list[dict[str, Any]],
    historical_counts: dict[str, int],
) -> tuple[list[dict[str, Any]], int]:
    repeated_patterns = 0
    repeated: list[dict[str, Any]] = []
    for finding in findings:
        key = _fingerprint(
            "repeat",
            finding.get("category"),
            *[str(item) for item in finding.get("source_refs", []) if str(item).strip()],
        )
        count = historical_counts.get(key, 0)
        if count <= 0:
            continue
        repeated_patterns += 1
        repeated.append(
            _build_finding(
                category="repeated_architecture_risk",
                title=f"Repeated architecture risk: {finding.get('title')}",
                description=f"{finding.get('title')} has repeated in {count} prior run(s).",
                severity="high" if count >= 2 else "medium",
                confidence=0.82,
                source_artifacts=list(finding.get("source_artifacts", [])),
                source_refs=list(finding.get("source_refs", [])),
                key_parts=[finding.get("fingerprint"), count],
            )
        )
    return repeated, repeated_patterns


def _recommendations_from_findings(findings: list[dict[str, Any]], node_index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    for finding in findings:
        refs = list(finding.get("source_refs", []))
        node_id = refs[1] if len(refs) > 1 else (refs[0] if refs else "")
        meta = _node_meta(node_id, node_index)
        worker_affinity = _infer_worker_affinity(str(finding.get("category", "")), meta)
        allowed_paths = _allowed_paths_from_meta(meta, fallback_worker=worker_affinity[0])
        confidence = _coerce_confidence(finding.get("confidence"), 0.7)
        severity = str(finding.get("severity", "low")).lower()
        priority = SEVERITY_TO_PRIORITY.get(severity, "P3")
        value_score = _value_score(severity, confidence)
        recommendation_id = f"REC-{_fingerprint('recommendation', finding.get('fingerprint'))[:10]}"
        recommendations.append(
            {
                "recommendation_id": recommendation_id,
                "category": str(finding.get("category", "repeated_architecture_risk")),
                "title": str(finding.get("title", recommendation_id)),
                "reason": str(finding.get("description", recommendation_id)),
                "source_finding_ids": [str(finding.get("finding_id", recommendation_id))],
                "worker_affinity": worker_affinity,
                "allowed_paths": allowed_paths,
                "acceptance_checks": _acceptance_checks(worker_affinity),
                "priority": priority,
                "value_score": value_score,
                "confidence": confidence,
                "fingerprint": _fingerprint(
                    "recommendation",
                    finding.get("category"),
                    allowed_paths,
                    worker_affinity,
                    finding.get("fingerprint"),
                ),
            }
        )
    return recommendations

def _task_from_recommendation(
    recommendation: dict[str, Any],
    *,
    now: dt.datetime,
    run_id: str,
) -> dict[str, Any]:
    priority = str(recommendation.get("priority", "P3")).strip().upper()
    value_score = int(recommendation.get("value_score", 0) or 0)
    return {
        "id": f"PLAN-{str(recommendation.get('recommendation_id', 'rec'))[-10:]}",
        "title": str(recommendation.get("title", "")).strip(),
        "description": str(recommendation.get("reason", "")).strip(),
        "category": CATEGORY_TO_TASK_BANK.get(str(recommendation.get("category", "")), "automation"),
        "source": "post_run_planner",
        "owner": PLANNER,
        "priority": PRIORITY_TO_NUMERIC.get(priority, 65),
        "estimated_mloc": _estimate_change_size(value_score),
        "value_score": value_score,
        "active": True,
        "status": "ready" if value_score >= 70 else "backlog",
        "expires_at": (now + dt.timedelta(days=30)).replace(microsecond=0).isoformat(),
        "worker_affinity": list(recommendation.get("worker_affinity", [])),
        "allowed_paths": list(recommendation.get("allowed_paths", [])),
        "acceptance_checks": list(recommendation.get("acceptance_checks", [])),
        "metrics": {
            "impact": max(1, min(10, int(round(value_score / 10.0)))),
            "risk_reduction": max(1, min(10, int(round(value_score / 10.0)))),
            "frequency": max(1, min(10, int(round(_coerce_confidence(recommendation.get("confidence")) * 10.0)))),
            "unblock": 6,
            "confidence": max(1, min(10, int(round(_coerce_confidence(recommendation.get("confidence")) * 10.0)))),
        },
        "created_at_utc": _iso_utc(now),
        "updated_at_utc": _iso_utc(now),
        "fingerprint": str(recommendation.get("fingerprint", "")).strip(),
        "run_origin": run_id,
    }


def _delta_entry(
    *,
    task_id: str,
    fingerprint: str,
    title: str,
    category: str,
    worker_affinity: list[str],
    priority: str,
    value_score: int,
    confidence: float,
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "fingerprint": fingerprint,
        "title": title,
        "category": category,
        "worker_affinity": worker_affinity,
        "priority": priority,
        "value_score": value_score,
        "confidence": _coerce_confidence(confidence),
    }


def _sort_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        tasks,
        key=lambda row: (
            str(row.get("status", "ready")) not in {"ready", "assigned"},
            -int(row.get("value_score", 0) or 0),
            -_priority_numeric(row.get("priority")),
            -int(row.get("estimated_mloc", 0) or 0),
            str(row.get("id", "")),
        ),
    )


def _merge_recommendations(
    *,
    recommendations: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    now: dt.datetime,
    run_id: str,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any]]:
    merged = [dict(item) for item in tasks if isinstance(item, dict)]
    indexed: dict[str, int] = {}
    for idx, task in enumerate(merged):
        fingerprint = str(task.get("fingerprint", "")).strip()
        if not fingerprint:
            fingerprint = _fingerprint("task", task.get("id"), task.get("title"), task.get("source"))
            task["fingerprint"] = fingerprint
        indexed[fingerprint] = idx

    added_delta: list[dict[str, Any]] = []
    updated_delta: list[dict[str, Any]] = []
    skipped_duplicates: list[dict[str, Any]] = []
    accepted_items: list[dict[str, Any]] = []
    rejected_items: list[dict[str, Any]] = []
    planner_recommendations: list[dict[str, Any]] = []

    for recommendation in recommendations:
        fingerprint = str(recommendation.get("fingerprint", "")).strip()
        priority = str(recommendation.get("priority", "P3")).strip().upper()
        value_score = int(recommendation.get("value_score", 0) or 0)
        confidence = _coerce_confidence(recommendation.get("confidence"))
        task = _task_from_recommendation(recommendation, now=now, run_id=run_id)
        planner_recommendations.append(
            {
                "recommendation_id": str(recommendation.get("recommendation_id", "")),
                "fingerprint": fingerprint,
                "title": str(recommendation.get("title", "")),
                "reason": str(recommendation.get("reason", "")),
                "category": str(recommendation.get("category", "")),
                "source_worker": REVIEWER,
                "source_artifact": "REVIEW_RECOMMENDATIONS.json",
                "worker_affinity": list(recommendation.get("worker_affinity", [])),
                "allowed_paths": list(recommendation.get("allowed_paths", [])),
                "acceptance_checks": list(recommendation.get("acceptance_checks", [])),
                "priority": priority,
                "value_score": value_score,
                "confidence": confidence,
                "expires_at": task["expires_at"],
                "run_origin": run_id,
            }
        )

        current_idx = indexed.get(fingerprint)
        delta_item = _delta_entry(
            task_id=str(task.get("id", "")),
            fingerprint=fingerprint,
            title=str(task.get("title", "")),
            category=str(recommendation.get("category", "")),
            worker_affinity=list(recommendation.get("worker_affinity", [])),
            priority=priority,
            value_score=value_score,
            confidence=confidence,
        )
        accepted_item = {
            "recommendation_id": str(recommendation.get("recommendation_id", "")),
            **delta_item,
        }

        if current_idx is None:
            indexed[fingerprint] = len(merged)
            merged.append(task)
            added_delta.append(delta_item)
            accepted_items.append(accepted_item)
            continue

        current = merged[current_idx]
        current_value = int(current.get("value_score", 0) or 0)
        current_priority = _priority_numeric(current.get("priority"))
        next_priority = _priority_numeric(priority)
        if value_score > current_value or next_priority > current_priority:
            task["created_at_utc"] = str(current.get("created_at_utc", task["created_at_utc"]))
            merged[current_idx] = task
            updated_delta.append(delta_item)
            accepted_items.append(accepted_item)
            continue

        duplicate = {
            "fingerprint": fingerprint,
            "task_id": str(current.get("id", "")),
            "reason": "fingerprint already present in task bank",
        }
        skipped_duplicates.append(duplicate)
        rejected_items.append(
            {
                "recommendation_id": str(recommendation.get("recommendation_id", "")),
                "fingerprint": fingerprint,
                "reason": duplicate["reason"],
            }
        )

    merged = _sort_tasks(merged)
    planner_payload = {
        "schema_version": 1,
        "run_id": run_id,
        "worker_id": PLANNER,
        "generated_at_utc": _iso_utc(now),
        "recommendations": planner_recommendations,
        "notes": [],
    }
    delta_payload = {
        "schema_version": 1,
        "run_id": run_id,
        "worker_id": PLANNER,
        "generated_at_utc": _iso_utc(now),
        "status": "PASS",
        "summary": {
            "candidate_count": len(recommendations),
            "added_count": len(added_delta),
            "updated_count": len(updated_delta),
            "duplicate_count": len(skipped_duplicates),
        },
        "added_tasks": added_delta,
        "updated_tasks": updated_delta,
        "skipped_duplicates": skipped_duplicates,
    }
    ingest_payload = {
        "schema_version": 1,
        "run_id": run_id,
        "worker_id": PLANNER,
        "generated_at_utc": _iso_utc(now),
        "status": "PASS" if not rejected_items else "WARN",
        "summary": {
            "source_count": 1,
            "candidate_count": len(recommendations),
            "accepted_count": len(accepted_items),
            "rejected_count": len(rejected_items),
        },
        "sources": [
            {
                "source_id": f"review:{run_id}",
                "source_worker": REVIEWER,
                "source_artifact": "REVIEW_RECOMMENDATIONS.json",
                "candidate_count": len(recommendations),
            }
        ],
        "accepted": accepted_items,
        "rejected": rejected_items,
        "notes": [],
    }
    return merged, delta_payload, ingest_payload, planner_payload


def _markdown_review_summary(review_report: dict[str, Any], findings: list[dict[str, Any]], recommendations: list[dict[str, Any]]) -> str:
    lines = [
        "# Architecture Review Summary",
        "",
        f"- Status: {review_report['status']}",
        f"- Findings: {review_report['summary']['finding_count']}",
        f"- Recommendations: {review_report['summary']['recommendation_count']}",
        "",
        "## Findings",
        "",
    ]
    if not findings:
        lines.append("- No structural review findings were synthesized from current Z_aggregator outputs.")
    else:
        for finding in findings[:8]:
            lines.append(f"- [{finding['severity']}] {finding['title']}")
    lines.extend(["", "## Recommendations", ""])
    if not recommendations:
        lines.append("- No planner-ready recommendations were emitted.")
    else:
        for recommendation in recommendations[:8]:
            lines.append(f"- {recommendation['priority']} {recommendation['title']}")
    return "\n".join(lines) + "\n"


def _markdown_planner_summary(delta_payload: dict[str, Any], planner_payload: dict[str, Any]) -> str:
    summary = delta_payload["summary"]
    lines = [
        "# Planner Summary",
        "",
        f"- Candidate recommendations: {summary['candidate_count']}",
        f"- Added tasks: {summary['added_count']}",
        f"- Updated tasks: {summary['updated_count']}",
        f"- Skipped duplicates: {summary['duplicate_count']}",
        "",
        "## Planner Recommendations",
        "",
    ]
    recommendations = planner_payload.get("recommendations", [])
    if not recommendations:
        lines.append("- No planner recommendations were emitted.")
    else:
        for recommendation in recommendations[:8]:
            lines.append(f"- {recommendation['priority']} {recommendation['title']}")
    return "\n".join(lines) + "\n"


def _validate_generated_payloads(payloads: dict[str, tuple[str, dict[str, Any]]]) -> None:
    errors: list[str] = []
    for label, (schema_name, payload) in payloads.items():
        for issue in schemas.validate_payload(schema_name, payload):
            errors.append(f"{label}: {issue}")
    if errors:
        raise ValueError("post-run intelligence produced invalid payloads:\n" + "\n".join(errors))
