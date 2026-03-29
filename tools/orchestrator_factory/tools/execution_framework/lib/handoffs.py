
from __future__ import annotations

from datetime import timedelta
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
    validate_simple_schema,
)

_STATUS_ORDER = {"planned": 0, "in_progress": 1, "blocked": 2, "done": 3}


def _handoff_service_level(policy: dict[str, Any], section_name: str, severity: str) -> timedelta:
    duration = policy.get("service_levels", {}).get(section_name, {}).get(severity)
    if not duration:
        raise KeyError(f"Missing handoff service level '{section_name}' for severity '{severity}'")
    from .heartbeats import parse_iso8601_duration
    return parse_iso8601_duration(duration)


def _normalize_history(values: Any) -> list[dict[str, Any]]:
    if values is None:
        return []
    if not isinstance(values, list):
        raise ValueError("history must be an array")
    entries: list[dict[str, Any]] = []
    for index, entry in enumerate(values):
        if not isinstance(entry, dict):
            raise ValueError(f"history[{index}] must be an object")
        normalized = dict(entry)
        if "at_utc" in normalized:
            normalized["at_utc"] = canonical_utc(str(normalized["at_utc"]))
        entries.append(normalized)
    entries.sort(key=lambda item: item.get("at_utc", ""))
    return entries


def normalize_handoff_ticket(payload: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    configs = load_coordination_configs(repo_root)
    schema = configs["handoff_ticket_schema"]
    topology = configs["chat_topology"]
    policy = configs["handoff_policy"]
    indexes = topology_indexes(topology)
    ticket = dict(payload)
    ticket["schema_version"] = str(ticket.get("schema_version", SCHEMA_VERSION))

    string_fields = [
        "handoff_id",
        "run_id",
        "round_id",
        "from_chat_id",
        "to_chat_id",
        "handoff_kind",
        "package_id",
        "task_ref",
        "handoff_summary",
        "requested_outcome",
        "status",
        "severity",
        "opened_at_utc",
        "response_due_at_utc",
        "ownership_mode",
        "project_id",
        "accepted_at_utc",
        "blocked_at_utc",
        "completed_at_utc",
        "updated_at_utc",
        "completion_summary",
        "rejection_reason",
        "resolved_by_chat_id",
        "next_action_owner",
        "status_summary",
    ]
    for field in string_fields:
        if field in ticket and ticket[field] is not None:
            ticket[field] = str(ticket[field]).strip()
            if not ticket[field]:
                ticket.pop(field, None)

    for field in ["opened_at_utc", "response_due_at_utc", "accepted_at_utc", "blocked_at_utc", "completed_at_utc", "updated_at_utc"]:
        if field in ticket:
            ticket[field] = canonical_utc(ticket[field])

    ticket["scope_refs"] = normalize_repo_relative_refs(ticket.get("scope_refs", []), "scope_refs")
    ticket["acceptance_criteria"] = normalize_string_list(ticket.get("acceptance_criteria", []), "acceptance_criteria", sort_values=False)
    ticket["evidence_refs"] = normalize_repo_relative_refs(ticket.get("evidence_refs", []), "evidence_refs")
    ticket["dependency_refs"] = normalize_string_list(ticket.get("dependency_refs", []), "dependency_refs")
    ticket["related_blocker_ids"] = normalize_string_list(ticket.get("related_blocker_ids", []), "related_blocker_ids")
    ticket["request_revision_fields"] = normalize_string_list(ticket.get("request_revision_fields", []), "request_revision_fields")
    ticket["history"] = _normalize_history(ticket.get("history", []))

    issues = validate_simple_schema(ticket, schema, "handoff_ticket")
    allowed_status = set(schema.get("allowed_status_values", []))
    if "status" in ticket and ticket["status"] not in allowed_status:
        issues.append(Issue("invalid_status", f"Unsupported handoff status '{ticket['status']}'"))
    allowed_kinds = set(schema.get("allowed_handoff_kinds", []))
    if "handoff_kind" in ticket and ticket["handoff_kind"] not in allowed_kinds:
        issues.append(Issue("invalid_handoff_kind", f"Unsupported handoff_kind '{ticket['handoff_kind']}'"))
    allowed_modes = set(schema.get("allowed_ownership_modes", []))
    if "ownership_mode" in ticket and ticket["ownership_mode"] not in allowed_modes:
        issues.append(Issue("invalid_ownership_mode", f"Unsupported ownership_mode '{ticket['ownership_mode']}'"))
    allowed_severity = set(schema.get("allowed_severity_values", []))
    if "severity" in ticket and ticket["severity"] not in allowed_severity:
        issues.append(Issue("invalid_severity", f"Unsupported severity '{ticket['severity']}'"))

    from_chat = indexes["chats"].get(ticket.get("from_chat_id"))
    to_chat = indexes["chats"].get(ticket.get("to_chat_id"))
    if not from_chat:
        issues.append(Issue("unknown_from_chat", f"Unknown from_chat_id '{ticket.get('from_chat_id')}'"))
    if not to_chat:
        issues.append(Issue("unknown_to_chat", f"Unknown to_chat_id '{ticket.get('to_chat_id')}'"))
    if from_chat and to_chat and from_chat["chat_id"] == to_chat["chat_id"]:
        issues.append(Issue("self_handoff", "from_chat_id and to_chat_id must be different"))
    if from_chat and to_chat:
        if from_chat.get("chat_kind") == "package_worker" and to_chat.get("chat_kind") == "package_worker":
            issues.append(Issue("direct_package_handoff_forbidden", "Cross-package handoffs must flow through governance-control"))
    if ticket.get("severity") and ticket.get("response_due_at_utc"):
        opened_at = parse_utc(ticket["opened_at_utc"], "opened_at_utc")
        response_due = parse_utc(ticket["response_due_at_utc"], "response_due_at_utc")
        if response_due < opened_at:
            issues.append(Issue("invalid_due_time", "response_due_at_utc cannot be earlier than opened_at_utc"))
        target_response_due = opened_at + _handoff_service_level(policy, "acknowledgement", ticket["severity"])
        if response_due > target_response_due and ticket.get("status") == "planned":
            issues.append(Issue("sla_due_too_late", "response_due_at_utc exceeds the configured acknowledgement SLA for this severity"))
    if ticket.get("status") == "done":
        if not ticket.get("completion_summary"):
            issues.append(Issue("missing_completion_summary", "Done handoff tickets require completion_summary"))
        if not ticket.get("resolved_by_chat_id"):
            issues.append(Issue("missing_resolved_by", "Done handoff tickets require resolved_by_chat_id"))
        if not ticket.get("evidence_refs"):
            issues.append(Issue("missing_evidence", "Done handoff tickets require evidence_refs"))
    if ticket.get("request_revision_fields") and not ticket.get("rejection_reason"):
        issues.append(Issue("revision_requires_reason", "request_revision_fields require rejection_reason explaining the missing information"))
    if ticket.get("history"):
        ordered = [entry.get("at_utc", "") for entry in ticket["history"] if entry.get("at_utc")]
        if ordered != sorted(ordered):
            issues.append(Issue("non_monotonic_history", "history.at_utc values must be monotonic"))

    if issues:
        raise ValueError("; ".join(issue.message for issue in issues))
    return ticket


def evaluate_handoff_ticket(ticket: dict[str, Any], repo_root: Path, now_utc: str | None = None) -> dict[str, Any]:
    policy = load_coordination_configs(repo_root)["handoff_policy"]
    normalized = normalize_handoff_ticket(ticket, repo_root)
    now = parse_utc(now_utc or utc_now())
    opened_at = parse_utc(normalized["opened_at_utc"])
    response_due = parse_utc(normalized["response_due_at_utc"])
    severity = normalized["severity"]
    ack_target = opened_at + _handoff_service_level(policy, "acknowledgement", severity)
    resolution_due = opened_at + _handoff_service_level(policy, "resolution_target", severity)
    first_checkpoint_due = None
    if normalized.get("accepted_at_utc"):
        first_checkpoint_due = parse_utc(normalized["accepted_at_utc"]) + _handoff_service_level(policy, "first_checkpoint_after_acceptance", severity)

    status = normalized["status"]
    ack_state = "satisfied"
    if status == "planned":
        if now > response_due:
            ack_state = "overdue"
        elif now > ack_target:
            ack_state = "at_risk"
        else:
            ack_state = "pending"

    resolution_state = "complete" if status == "done" else "pending"
    if status != "done":
        if now > resolution_due:
            resolution_state = "overdue"
        elif now > resolution_due - timedelta(minutes=30):
            resolution_state = "at_risk"

    checkpoint_state = "not_applicable"
    if first_checkpoint_due is not None and status in {"in_progress", "blocked"}:
        updated_at = parse_utc(normalized.get("updated_at_utc", normalized.get("accepted_at_utc")))
        checkpoint_state = "on_time"
        if updated_at < first_checkpoint_due and now > first_checkpoint_due:
            checkpoint_state = "overdue"

    return {
        "handoff_id": normalized["handoff_id"],
        "run_id": normalized["run_id"],
        "round_id": normalized["round_id"],
        "package_id": normalized["package_id"],
        "from_chat_id": normalized["from_chat_id"],
        "to_chat_id": normalized["to_chat_id"],
        "status": status,
        "severity": severity,
        "ownership_mode": normalized["ownership_mode"],
        "response_due_at_utc": normalized["response_due_at_utc"],
        "acknowledgement_target_at_utc": ack_target.isoformat().replace("+00:00", "Z"),
        "resolution_due_at_utc": resolution_due.isoformat().replace("+00:00", "Z"),
        "first_checkpoint_due_at_utc": first_checkpoint_due.isoformat().replace("+00:00", "Z") if first_checkpoint_due else "",
        "ack_state": ack_state,
        "resolution_state": resolution_state,
        "checkpoint_state": checkpoint_state,
        "is_overdue": ack_state == "overdue" or resolution_state == "overdue" or checkpoint_state == "overdue",
        "requested_outcome": normalized["requested_outcome"],
        "acceptance_criteria_count": len(normalized["acceptance_criteria"]),
        "evidence_refs_count": len(normalized["evidence_refs"]),
        "status_summary": normalized.get("status_summary", ""),
        "next_action_owner": normalized.get("next_action_owner", ""),
        "ticket": normalized,
    }


def summarize_handoffs(repo_root: Path, tickets: list[dict[str, Any]], now_utc: str | None = None) -> dict[str, Any]:
    evaluations = [evaluate_handoff_ticket(ticket, repo_root, now_utc=now_utc) for ticket in tickets]
    evaluations.sort(key=lambda item: (_STATUS_ORDER.get(item["status"], 9), item["severity"], item["response_due_at_utc"], item["handoff_id"]))
    counts = {
        "total": len(evaluations),
        "open": 0,
        "done": 0,
        "overdue": 0,
        "planned": 0,
        "in_progress": 0,
        "blocked": 0,
        "sev1_open": 0,
        "sev2_open": 0,
    }
    for item in evaluations:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
        if item["status"] == "done":
            counts["done"] += 1
        else:
            counts["open"] += 1
            if item["severity"] == "sev1":
                counts["sev1_open"] += 1
            if item["severity"] == "sev2":
                counts["sev2_open"] += 1
        if item["is_overdue"]:
            counts["overdue"] += 1
    return {
        "generated_at_utc": parse_utc(now_utc or utc_now()).isoformat().replace("+00:00", "Z"),
        "counts": counts,
        "rows": evaluations,
    }
