
from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import Issue, SCHEMA_VERSION, utc_now
from .coordination import (
    canonical_utc,
    load_coordination_configs,
    normalize_repo_relative_refs,
    normalize_string_list,
    parse_utc,
    topology_indexes,
    validate_chat_message,
)

_SEVERITY_RANK = {"sev1": 0, "sev2": 1, "sev3": 2, "sev4": 3}
_INFERENCE_KEYWORDS = {
    "dependency": {"dependency", "handoff", "waiting", "external", "upstream", "deliverable", "approval"},
    "scope": {"scope", "clarify", "ambiguity", "unclear", "contradict", "ownership", "criteria"},
    "infra": {"infra", "runtime", "filesystem", "config", "tool", "path", "environment", "unavailable"},
    "quality": {"quality", "validation", "schema", "evidence", "readiness", "unsafe", "rejected"},
}
_SEVERITY_HINTS = {
    "sev1": {"critical", "immediate", "unsafe", "stop", "stopped"},
    "sev2": {"high", "miss", "risk", "delayed", "blocked"},
    "sev3": {"slow", "waiting", "degraded"},
    "sev4": {"minor", "localized", "low"},
}


def _matrix_lookup(matrix: dict[str, Any], blocker_type: str, severity: str) -> dict[str, Any] | None:
    for row in matrix.get("matrix", []):
        if row.get("blocker_type") == blocker_type and row.get("severity") == severity:
            return row
    return None


def infer_blocker_type(message: dict[str, Any], taxonomy: dict[str, Any]) -> str | None:
    text_fragments: list[str] = []
    for field in ["status_summary", "next_planned_action", "next_action_owner"]:
        if message.get(field):
            text_fragments.append(str(message[field]).lower())
    for tag in message.get("tags", []):
        text_fragments.append(str(tag).lower())
    blob = " ".join(text_fragments)

    best_type = None
    best_score = -1
    valid_types = {item["blocker_type"] for item in taxonomy.get("blocker_types", []) if isinstance(item, dict) and "blocker_type" in item}
    for blocker_type in valid_types:
        keywords = _INFERENCE_KEYWORDS.get(blocker_type, set())
        score = sum(1 for keyword in keywords if keyword in blob)
        if score > best_score:
            best_type = blocker_type
            best_score = score
    return best_type if best_score > 0 else None


def infer_severity(message: dict[str, Any]) -> str:
    text_fragments: list[str] = []
    for field in ["status_summary", "next_planned_action"]:
        if message.get(field):
            text_fragments.append(str(message[field]).lower())
    blob = " ".join(text_fragments)
    for severity in ["sev1", "sev2", "sev4", "sev3"]:
        if any(keyword in blob for keyword in _SEVERITY_HINTS[severity]):
            return severity
    return "sev3"


def normalize_blocker_message(message: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    configs = load_coordination_configs(repo_root)
    topology = configs["chat_topology"]
    taxonomy = configs["blocker_taxonomy"]
    indexes = topology_indexes(topology)
    payload = dict(message)
    payload["schema_version"] = str(payload.get("schema_version", SCHEMA_VERSION))
    payload["message_type"] = "blocker_report"
    if "published_at_utc" in payload:
        payload["published_at_utc"] = canonical_utc(str(payload["published_at_utc"]))
    if "blocked_at_utc" in payload:
        payload["blocked_at_utc"] = canonical_utc(str(payload["blocked_at_utc"]))
    if "current_item_refs" in payload:
        payload["current_item_refs"] = normalize_repo_relative_refs(payload.get("current_item_refs", []), "current_item_refs")
    if "evidence_refs" in payload:
        payload["evidence_refs"] = normalize_repo_relative_refs(payload.get("evidence_refs", []), "evidence_refs")
    if "related_entity_ids" in payload:
        payload["related_entity_ids"] = normalize_string_list(payload.get("related_entity_ids", []), "related_entity_ids")
    if "tags" in payload:
        payload["tags"] = normalize_string_list(payload.get("tags", []), "tags")

    issues = validate_chat_message(payload, repo_root)
    if payload.get("message_type") != "blocker_report":
        issues.append(Issue("invalid_message_type", "blocker messages must use message_type 'blocker_report'"))

    valid_types = {item["blocker_type"] for item in taxonomy.get("blocker_types", []) if isinstance(item, dict) and "blocker_type" in item}
    blocker_type = payload.get("blocker_type") or infer_blocker_type(payload, taxonomy)
    if not blocker_type:
        issues.append(Issue("missing_blocker_type", "blocker_type is required and could not be inferred"))
    elif blocker_type not in valid_types:
        issues.append(Issue("invalid_blocker_type", f"Unsupported blocker_type '{blocker_type}'"))
    else:
        payload["blocker_type"] = blocker_type

    severity = payload.get("severity") or infer_severity(payload)
    matrix = configs["escalation_matrix"]
    valid_severity = {item["severity"] for item in matrix.get("severity_levels", []) if isinstance(item, dict) and "severity" in item}
    if severity not in valid_severity:
        issues.append(Issue("invalid_severity", f"Unsupported severity '{severity}'"))
    else:
        payload["severity"] = severity

    if payload.get("status") != "blocked":
        issues.append(Issue("invalid_blocker_status", "blocker_report events must use status 'blocked'"))
    if not payload.get("next_action_owner"):
        issues.append(Issue("missing_next_action_owner", "blocker_report events must include next_action_owner"))
    chat = indexes["chats"].get(payload.get("from_chat_id"))
    if chat and chat.get("chat_kind") == "package_worker" and payload.get("package_id"):
        owned = chat.get("owns_package_ids", [])
        if owned and payload["package_id"] not in owned:
            issues.append(Issue("package_ownership_mismatch", f"Chat '{chat['chat_id']}' does not own blocker package_id '{payload['package_id']}'"))
    if issues:
        raise ValueError("; ".join(issue.message for issue in issues))
    return payload


def recommend_escalation(message: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    configs = load_coordination_configs(repo_root)
    matrix = configs["escalation_matrix"]
    payload = normalize_blocker_message(message, repo_root)
    row = _matrix_lookup(matrix, payload["blocker_type"], payload["severity"])
    if row is None:
        raise ValueError(f"No escalation rule configured for blocker_type='{payload['blocker_type']}' severity='{payload['severity']}'")
    return {
        "escalate_to": row["escalate_to"],
        "required_action": row["required_action"],
        "resolution_owner": row["resolution_owner"],
        "checkpoint_frequency": row["checkpoint_frequency"],
        "notify_within": next((item["notify_within"] for item in matrix.get("severity_levels", []) if item.get("severity") == payload["severity"]), ""),
    }


def build_blocker_record(message: dict[str, Any], repo_root: Path, now_utc: str | None = None) -> dict[str, Any]:
    payload = normalize_blocker_message(message, repo_root)
    now = parse_utc(now_utc or utc_now())
    opened_at = parse_utc(payload.get("blocked_at_utc", payload["published_at_utc"]))
    age_minutes = max(0, int((now - opened_at).total_seconds() // 60))
    recommendation = recommend_escalation(payload, repo_root)
    return {
        "blocker_id": payload.get("message_id", ""),
        "message_id": payload.get("message_id", ""),
        "run_id": payload["run_id"],
        "round_id": payload["round_id"],
        "package_id": payload.get("package_id", ""),
        "owner_chat_id": payload["from_chat_id"],
        "status": payload["status"],
        "severity": payload["severity"],
        "blocker_type": payload["blocker_type"],
        "status_summary": payload.get("status_summary", ""),
        "next_action_owner": payload.get("next_action_owner", ""),
        "opened_at_utc": opened_at.isoformat().replace("+00:00", "Z"),
        "age_minutes": age_minutes,
        "related_entity_ids": payload.get("related_entity_ids", []),
        "evidence_refs": payload.get("evidence_refs", []),
        "recommendation": recommendation,
        "message": payload,
    }


def summarize_blockers(repo_root: Path, messages: list[dict[str, Any]], now_utc: str | None = None) -> dict[str, Any]:
    rows = [build_blocker_record(message, repo_root, now_utc=now_utc) for message in messages if message.get("message_type") == "blocker_report"]
    rows.sort(key=lambda item: (_SEVERITY_RANK.get(item["severity"], 9), item["opened_at_utc"], item["blocker_id"]))
    counts = {
        "total": len(rows),
        "open": len(rows),
        "sev1_open": 0,
        "sev2_open": 0,
        "dependency": 0,
        "scope": 0,
        "infra": 0,
        "quality": 0,
    }
    for row in rows:
        counts[row["blocker_type"]] = counts.get(row["blocker_type"], 0) + 1
        if row["severity"] == "sev1":
            counts["sev1_open"] += 1
        if row["severity"] == "sev2":
            counts["sev2_open"] += 1
    return {
        "generated_at_utc": parse_utc(now_utc or utc_now()).isoformat().replace("+00:00", "Z"),
        "counts": counts,
        "rows": rows,
    }
