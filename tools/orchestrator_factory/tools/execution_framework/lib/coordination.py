
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import re
from typing import Any

from .common import Issue, SCHEMA_VERSION, ensure_dir, is_safe_relative_path, normalize_relpath, read_json, stable_json_dumps
from .config import load_system_config
from .validators import TYPE_MAP, validate_required_fields


CONFIG_PATHS = {
    "chat_topology": "configs/execution_framework/chat_topology.json",
    "chat_capability_matrix": "configs/execution_framework/chat_capability_matrix.json",
    "coordination_protocol": "configs/execution_framework/coordination_protocol.json",
    "handoff_policy": "configs/execution_framework/handoff_policy.json",
    "escalation_matrix": "configs/execution_framework/escalation_matrix.json",
    "blocker_taxonomy": "configs/execution_framework/blocker_taxonomy.json",
    "sync_cadence": "configs/execution_framework/sync_cadence.json",
    "operator_dashboard_views": "configs/execution_framework/operator_dashboard_views.json",
    "chat_message_schema": "schemas/execution_framework/chat_message.schema.json",
    "handoff_ticket_schema": "schemas/execution_framework/handoff_ticket.schema.json",
}

_MESSAGE_ARRAY_FIELDS = {
    "current_item_refs",
    "related_entity_ids",
    "evidence_refs",
    "tags",
    "history",
    "scope_refs",
    "acceptance_criteria",
    "dependency_refs",
    "related_blocker_ids",
    "request_revision_fields",
}
_SAFE_PATH_ARRAY_FIELDS = {"current_item_refs", "evidence_refs", "scope_refs"}
_IDENTIFIER_RE = re.compile(r"[^A-Za-z0-9._-]+")


def parse_utc(value: str, field_name: str = "timestamp") -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty UTC timestamp string")
    raw = value.strip()
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO-8601 timestamp, got '{value}'") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field_name} must include timezone information")
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def canonical_utc(value: str) -> str:
    return parse_utc(value).isoformat().replace("+00:00", "Z")


def sanitize_identifier(value: str) -> str:
    cleaned = _IDENTIFIER_RE.sub("-", str(value).strip()).strip("-")
    return cleaned or "item"


def coordination_round_root(repo_root: Path, run_id: str, round_id: str) -> Path:
    system = load_system_config(repo_root)
    return repo_root / system["runs_root"] / run_id / system["rounds_dir_name"] / round_id


def coordination_plane_root(repo_root: Path, run_id: str, round_id: str) -> Path:
    return coordination_round_root(repo_root, run_id, round_id) / "coordination"


def coordination_channel_root(repo_root: Path, run_id: str, round_id: str) -> Path:
    return coordination_plane_root(repo_root, run_id, round_id) / "channels"


def coordination_channel_dir(repo_root: Path, run_id: str, round_id: str, channel_id: str) -> Path:
    return coordination_channel_root(repo_root, run_id, round_id) / sanitize_identifier(channel_id)


def coordination_snapshots_dir(repo_root: Path, run_id: str, round_id: str) -> Path:
    return coordination_plane_root(repo_root, run_id, round_id) / "snapshots"


def coordination_views_dir(repo_root: Path, run_id: str, round_id: str) -> Path:
    return coordination_plane_root(repo_root, run_id, round_id) / "views"


def ensure_round_context_exists(repo_root: Path, run_id: str, round_id: str) -> Path:
    round_root = coordination_round_root(repo_root, run_id, round_id)
    round_manifest_path = round_root / "round_manifest.json"
    if not round_root.exists():
        raise FileNotFoundError(f"Round root does not exist: {round_root}")
    if not round_manifest_path.exists():
        raise FileNotFoundError(f"Round manifest does not exist: {round_manifest_path}")
    return round_root


def load_coordination_configs(repo_root: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, rel_path in CONFIG_PATHS.items():
        payload[key] = read_json(repo_root / rel_path)
    return payload


def _schema_type_issues(data: dict[str, Any], schema: dict[str, Any], label: str) -> list[Issue]:
    issues: list[Issue] = []
    optional = schema.get("optional_fields", {})
    for key, type_name in optional.items():
        if key not in data:
            continue
        expected = TYPE_MAP.get(type_name)
        if expected is None:
            issues.append(Issue("unknown_schema_type", f"{label}: unsupported schema type '{type_name}' for '{key}'"))
            continue
        if not isinstance(data[key], expected):
            issues.append(Issue("wrong_type", f"{label}: field '{key}' must be {type_name}"))
    return issues


def validate_simple_schema(data: dict[str, Any], schema: dict[str, Any], label: str) -> list[Issue]:
    issues = validate_required_fields(data, schema.get("required_fields", {}), label)
    issues.extend(_schema_type_issues(data, schema, label))
    return issues


def _normalize_string(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Expected string value")
    normalized = value.strip()
    if not normalized:
        raise ValueError("String value cannot be empty")
    return normalized


def normalize_string_list(values: Any, field_name: str, sort_values: bool = True) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list):
        raise ValueError(f"{field_name} must be an array")
    normalized: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(values):
        if not isinstance(item, str):
            raise ValueError(f"{field_name}[{index}] must be a string")
        text = item.strip()
        if not text:
            raise ValueError(f"{field_name}[{index}] cannot be empty")
        if text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    if sort_values:
        normalized.sort()
    return normalized


def normalize_repo_relative_refs(values: Any, field_name: str) -> list[str]:
    refs = normalize_string_list(values, field_name)
    normalized_refs: list[str] = []
    for ref in refs:
        normalized = normalize_relpath(ref)
        if not is_safe_relative_path(normalized):
            raise ValueError(f"{field_name} contains unsafe repo-relative path '{ref}'")
        normalized_refs.append(normalized)
    return normalized_refs


def normalize_history_entries(values: Any) -> list[dict[str, Any]]:
    if values is None:
        return []
    if not isinstance(values, list):
        raise ValueError("history must be an array")
    entries: list[dict[str, Any]] = []
    for index, item in enumerate(values):
        if not isinstance(item, dict):
            raise ValueError(f"history[{index}] must be an object")
        entry = dict(item)
        if "at_utc" in entry:
            entry["at_utc"] = canonical_utc(str(entry["at_utc"]))
        if "action" in entry and isinstance(entry["action"], str):
            entry["action"] = entry["action"].strip()
        entries.append(entry)
    entries.sort(key=lambda item: item.get("at_utc", ""))
    return entries


def topology_indexes(topology: dict[str, Any]) -> dict[str, dict[str, Any]]:
    chats = {item["chat_id"]: item for item in topology.get("chats", []) if isinstance(item, dict) and "chat_id" in item}
    channels = {item["channel_id"]: item for item in topology.get("channels", []) if isinstance(item, dict) and "channel_id" in item}
    routes = {item["message_type"]: item for item in topology.get("routing_table", []) if isinstance(item, dict) and "message_type" in item}
    return {"chats": chats, "channels": channels, "routes": routes}


def validate_chat_message(payload: dict[str, Any], repo_root: Path) -> list[Issue]:
    configs = load_coordination_configs(repo_root)
    schema = configs["chat_message_schema"]
    topology = configs["chat_topology"]
    indexes = topology_indexes(topology)
    issues = validate_simple_schema(payload, schema, "chat_message")

    allowed_types = set(schema.get("allowed_message_types", []))
    allowed_status = set(schema.get("allowed_status_values", []))
    if "message_type" in payload and payload["message_type"] not in allowed_types:
        issues.append(Issue("invalid_message_type", f"Unsupported message_type '{payload['message_type']}'"))
    if "status" in payload and payload["status"] not in allowed_status:
        issues.append(Issue("invalid_status", f"Unsupported status '{payload['status']}'"))

    for timestamp_field in ["published_at_utc", "last_progress_at_utc"]:
        if timestamp_field in payload:
            try:
                parse_utc(str(payload[timestamp_field]), timestamp_field)
            except ValueError as exc:
                issues.append(Issue("invalid_timestamp", str(exc)))

    for field_name in _SAFE_PATH_ARRAY_FIELDS.intersection(payload.keys()):
        try:
            normalize_repo_relative_refs(payload[field_name], field_name)
        except ValueError as exc:
            issues.append(Issue("invalid_path", str(exc)))

    if "history" in payload:
        try:
            normalize_history_entries(payload["history"])
        except ValueError as exc:
            issues.append(Issue("invalid_history", str(exc)))

    chat = indexes["chats"].get(payload.get("from_chat_id"))
    if not chat:
        issues.append(Issue("unknown_chat", f"Unknown from_chat_id '{payload.get('from_chat_id')}'"))
    channel = indexes["channels"].get(payload.get("channel_id"))
    if not channel:
        issues.append(Issue("unknown_channel", f"Unknown channel_id '{payload.get('channel_id')}'"))

    route = indexes["routes"].get(payload.get("message_type"))
    if route:
        expected_channel = route.get("required_channel_id")
        if expected_channel and payload.get("channel_id") != expected_channel:
            issues.append(Issue("route_channel_mismatch", f"message_type '{payload.get('message_type')}' must publish to '{expected_channel}'"))
        if chat and chat.get("chat_kind") not in route.get("source_chat_kinds", []):
            issues.append(Issue("route_source_mismatch", f"chat_kind '{chat.get('chat_kind')}' cannot publish '{payload.get('message_type')}'"))
    if chat and channel:
        if payload.get("channel_id") not in chat.get("may_publish_to_channels", []):
            issues.append(Issue("publish_not_allowed", f"Chat '{chat['chat_id']}' may not publish to '{payload.get('channel_id')}'"))
        if chat["chat_id"] not in channel.get("publishers", []):
            issues.append(Issue("publisher_not_registered", f"Channel '{payload.get('channel_id')}' does not list '{chat['chat_id']}' as publisher"))
    to_chat_id = payload.get("to_chat_id")
    if to_chat_id and to_chat_id not in indexes["chats"]:
        issues.append(Issue("unknown_to_chat", f"Unknown to_chat_id '{to_chat_id}'"))

    package_id = payload.get("package_id")
    if package_id and chat and chat.get("chat_kind") == "package_worker":
        owned = chat.get("owns_package_ids", [])
        if owned and package_id not in owned:
            issues.append(Issue("package_ownership_mismatch", f"Chat '{chat['chat_id']}' does not own package_id '{package_id}'"))

    return issues


def normalize_message_event(payload: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    normalized = dict(payload)
    normalized["schema_version"] = str(normalized.get("schema_version", SCHEMA_VERSION))
    string_fields = [
        "message_id",
        "message_type",
        "run_id",
        "round_id",
        "channel_id",
        "from_chat_id",
        "published_at_utc",
        "status",
        "status_summary",
        "project_id",
        "package_id",
        "to_chat_id",
        "severity",
        "blocker_type",
        "next_action_owner",
        "next_planned_action",
        "payload_ref",
        "last_progress_at_utc",
    ]
    for field in string_fields:
        if field in normalized and normalized[field] is not None:
            normalized[field] = str(normalized[field]).strip()
            if not normalized[field]:
                normalized.pop(field, None)

    if "published_at_utc" in normalized:
        normalized["published_at_utc"] = canonical_utc(normalized["published_at_utc"])
    if "last_progress_at_utc" in normalized:
        normalized["last_progress_at_utc"] = canonical_utc(normalized["last_progress_at_utc"])

    for field in _MESSAGE_ARRAY_FIELDS.intersection(normalized.keys()):
        if field == "history":
            normalized[field] = normalize_history_entries(normalized[field])
        elif field in _SAFE_PATH_ARRAY_FIELDS:
            normalized[field] = normalize_repo_relative_refs(normalized[field], field)
        else:
            normalized[field] = normalize_string_list(normalized[field], field)

    if "message_id" not in normalized:
        if "message_type" not in normalized or "from_chat_id" not in normalized or "published_at_utc" not in normalized:
            raise ValueError("message_id is missing and cannot be derived without message_type, from_chat_id, and published_at_utc")
        stamp = parse_utc(normalized["published_at_utc"]).strftime("%Y%m%dT%H%M%SZ")
        normalized["message_id"] = f"{sanitize_identifier(normalized['message_type'])}-{sanitize_identifier(normalized['from_chat_id'])}-{stamp}"

    issues = validate_chat_message(normalized, repo_root)
    if issues:
        joined = "; ".join(issue.message for issue in issues)
        raise ValueError(joined)
    return normalized


def write_coordination_event(repo_root: Path, run_id: str, round_id: str, payload: dict[str, Any]) -> Path:
    normalized = normalize_message_event(payload, repo_root)
    channel_dir = ensure_dir(coordination_channel_dir(repo_root, run_id, round_id, normalized["channel_id"]))
    target = channel_dir / f"{sanitize_identifier(normalized['message_id'])}.json"
    if target.exists():
        existing = read_json(target)
        if existing != normalized:
            raise FileExistsError(f"Coordination event already exists with different content: {target}")
        return target
    target.write_text(stable_json_dumps(normalized), encoding="utf-8")
    return target


def load_channel_events(repo_root: Path, run_id: str, round_id: str, channel_id: str) -> tuple[list[dict[str, Any]], list[Issue]]:
    channel_dir = coordination_channel_dir(repo_root, run_id, round_id, channel_id)
    if not channel_dir.exists():
        return [], []
    events: list[dict[str, Any]] = []
    issues: list[Issue] = []
    for path in sorted(channel_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(Issue("invalid_json", f"Failed to decode '{path.name}': {exc.msg}", path=path.name))
            continue
        try:
            events.append(normalize_message_event(payload, repo_root))
        except ValueError as exc:
            issues.append(Issue("invalid_event", str(exc), path=path.name))
    events.sort(key=lambda item: (item.get("published_at_utc", ""), item.get("message_id", "")))
    return events, issues


def latest_message_by_chat(events: list[dict[str, Any]], message_type: str | None = None) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for event in sorted(events, key=lambda item: (item.get("published_at_utc", ""), item.get("message_id", ""))):
        if message_type and event.get("message_type") != message_type:
            continue
        from_chat = event.get("from_chat_id")
        if not from_chat:
            continue
        latest[from_chat] = event
    return latest


def compute_global_status(
    heartbeat_summary: dict[str, Any],
    checkpoint_summary: dict[str, Any],
    handoff_summary: dict[str, Any],
    blocker_summary: dict[str, Any],
) -> dict[str, Any]:
    reasons: list[str] = []
    state = "planned"
    if heartbeat_summary.get("counts", {}).get("escalated", 0) > 0:
        state = "blocked"
        reasons.append("one or more chats exceeded the escalation silence threshold")
    if blocker_summary.get("counts", {}).get("sev1_open", 0) > 0:
        state = "blocked"
        reasons.append("at least one sev1 blocker is still open")
    if handoff_summary.get("counts", {}).get("overdue", 0) > 0 and state != "blocked":
        state = "in_progress"
        reasons.append("there are overdue handoffs awaiting attention")
    if checkpoint_summary.get("counts", {}).get("blocked", 0) > 0 and state != "blocked":
        state = "in_progress"
        reasons.append("one or more package checkpoints are blocked")
    if heartbeat_summary.get("counts", {}).get("active", 0) > 0 and state == "planned":
        state = "in_progress"
        reasons.append("active heartbeat traffic exists")
    expected = heartbeat_summary.get("counts", {}).get("expected", 0)
    done = checkpoint_summary.get("counts", {}).get("done", 0)
    open_blockers = blocker_summary.get("counts", {}).get("open", 0)
    open_handoffs = handoff_summary.get("counts", {}).get("open", 0)
    if expected > 0 and done >= expected and open_blockers == 0 and open_handoffs == 0:
        state = "done"
        reasons = ["all expected chats report done checkpoints and no open blockers or handoffs remain"]
    return {
        "status": state,
        "reasons": reasons,
    }


def render_markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._\n"
    header = "| " + " | ".join(columns) + " |\n"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |\n"
    body_lines = []
    for row in rows:
        values = []
        for column in columns:
            value = row.get(column, "")
            if isinstance(value, list):
                value = ", ".join(str(item) for item in value)
            elif isinstance(value, dict):
                value = stable_json_dumps(value).strip()
            values.append(str(value))
        body_lines.append("| " + " | ".join(values) + " |")
    return header + separator + "\n".join(body_lines) + "\n"


def summarize_checkpoint_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    latest = latest_message_by_chat(events, message_type="sync_checkpoint")
    rows: list[dict[str, Any]] = []
    counts = {"planned": 0, "in_progress": 0, "blocked": 0, "done": 0}
    for chat_id in sorted(latest):
        event = latest[chat_id]
        status = event.get("status", "planned")
        counts[status] = counts.get(status, 0) + 1
        rows.append({
            "chat_id": chat_id,
            "status": status,
            "status_summary": event.get("status_summary", ""),
            "package_id": event.get("package_id", ""),
            "published_at_utc": event.get("published_at_utc", ""),
            "next_planned_action": event.get("next_planned_action", ""),
        })
    return {"counts": counts, "rows": rows, "latest_by_chat": latest}
