
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
from typing import Any

from .common import SCHEMA_VERSION, utc_now
from .coordination import (
    canonical_utc,
    load_coordination_configs,
    normalize_message_event,
    parse_utc,
    sanitize_identifier,
    topology_indexes,
)

_DURATION_RE = re.compile(
    r"^P(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?$"
)


def parse_iso8601_duration(value: str) -> timedelta:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("duration must be a non-empty ISO-8601 string")
    match = _DURATION_RE.match(value.strip())
    if not match:
        raise ValueError(f"Unsupported ISO-8601 duration '{value}'")
    parts = {name: int(amount or 0) for name, amount in match.groupdict().items()}
    if all(amount == 0 for amount in parts.values()):
        raise ValueError(f"Duration '{value}' must be greater than zero")
    return timedelta(days=parts["days"], hours=parts["hours"], minutes=parts["minutes"], seconds=parts["seconds"])


def _profile_for_chat(sync_cadence: dict[str, Any], chat_id: str) -> dict[str, Any]:
    for profile in sync_cadence.get("cadence_profiles", []):
        if chat_id in profile.get("applies_to_chat_ids", []):
            return profile
    raise KeyError(f"No cadence profile configured for chat_id '{chat_id}'")


def _state_from_age(age_seconds: int, warn_after: timedelta, escalate_after: timedelta) -> str:
    if age_seconds >= int(escalate_after.total_seconds()):
        return "escalated"
    if age_seconds >= int(warn_after.total_seconds()):
        return "warning"
    return "ok"


def _maybe_parse_clock(clock_value: str | None) -> datetime | None:
    if not clock_value:
        return None
    return parse_utc(clock_value)


def build_heartbeat_message(
    repo_root: Path,
    run_id: str,
    round_id: str,
    chat_id: str,
    status: str,
    status_summary: str,
    current_item_refs: list[str] | None = None,
    next_planned_action: str | None = None,
    tags: list[str] | None = None,
    last_progress_at_utc: str | None = None,
    message_id: str | None = None,
    published_at_utc: str | None = None,
) -> dict[str, Any]:
    configs = load_coordination_configs(repo_root)
    topology = configs["chat_topology"]
    chats = topology_indexes(topology)["chats"]
    if chat_id not in chats:
        raise ValueError(f"Unknown chat_id '{chat_id}'")
    chat = chats[chat_id]
    published = canonical_utc(published_at_utc or utc_now())
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "message_id": message_id or f"heartbeat-{sanitize_identifier(chat_id)}-{parse_utc(published).strftime('%Y%m%dT%H%M%SZ')}",
        "message_type": "chat_heartbeat",
        "run_id": run_id,
        "round_id": round_id,
        "channel_id": "channel.heartbeats",
        "from_chat_id": chat_id,
        "published_at_utc": published,
        "status": status,
        "status_summary": status_summary,
        "current_item_refs": current_item_refs or [],
        "tags": tags or [],
        "history": [],
    }
    owned = chat.get("owns_package_ids", [])
    if len(owned) == 1:
        payload["package_id"] = owned[0]
    if next_planned_action:
        payload["next_planned_action"] = next_planned_action.strip()
    if last_progress_at_utc:
        payload["last_progress_at_utc"] = canonical_utc(last_progress_at_utc)
    return normalize_message_event(payload, repo_root)


def summarize_heartbeats(
    repo_root: Path,
    heartbeat_events: list[dict[str, Any]],
    now_utc: str | None = None,
    initialized_at_utc: str | None = None,
) -> dict[str, Any]:
    configs = load_coordination_configs(repo_root)
    topology = configs["chat_topology"]
    sync_cadence = configs["sync_cadence"]
    indexes = topology_indexes(topology)
    now = parse_utc(now_utc or utc_now())
    initialized_at = _maybe_parse_clock(initialized_at_utc)

    latest_by_chat: dict[str, dict[str, Any]] = {}
    for event in sorted(heartbeat_events, key=lambda item: (item.get("published_at_utc", ""), item.get("message_id", ""))):
        if event.get("message_type") != "chat_heartbeat":
            continue
        latest_by_chat[event["from_chat_id"]] = event

    rows: list[dict[str, Any]] = []
    counts = {"expected": 0, "present": 0, "missing": 0, "ok": 0, "warning": 0, "escalated": 0, "active": 0}
    for chat_id in sorted(indexes["chats"]):
        chat = indexes["chats"][chat_id]
        profile = _profile_for_chat(sync_cadence, chat_id)
        warn_after = parse_iso8601_duration(profile["silence_policy"]["warn_after"])
        escalate_after = parse_iso8601_duration(profile["silence_policy"]["escalate_after"])
        heartbeat_every = parse_iso8601_duration(profile["heartbeat_every"])
        counts["expected"] += 1
        event = latest_by_chat.get(chat_id)
        row: dict[str, Any] = {
            "chat_id": chat_id,
            "chat_kind": chat.get("chat_kind", ""),
            "owned_package_ids": chat.get("owns_package_ids", []),
            "profile_id": profile["profile_id"],
            "heartbeat_every": profile["heartbeat_every"],
            "checkpoint_every": profile["checkpoint_every"],
            "warn_after": profile["silence_policy"]["warn_after"],
            "escalate_after": profile["silence_policy"]["escalate_after"],
            "heartbeat_status": "missing",
            "silence_state": "missing",
            "heartbeat_age_minutes": "",
            "last_progress_at_utc": "",
            "status": "",
            "status_summary": "",
            "current_item_refs": [],
            "next_planned_action": "",
            "risk_flag": "",
        }
        if not event:
            counts["missing"] += 1
            baseline = initialized_at
            if baseline is not None:
                age_seconds = max(0, int((now - baseline).total_seconds()))
                silence_state = _state_from_age(age_seconds, warn_after, escalate_after)
                row["heartbeat_age_minutes"] = age_seconds // 60
                row["silence_state"] = silence_state
                row["risk_flag"] = "missing_heartbeat"
                counts[silence_state] += 1
            rows.append(row)
            continue

        counts["present"] += 1
        counts["active"] += 1
        published = parse_utc(event["published_at_utc"])
        progress_at = parse_utc(event.get("last_progress_at_utc", event["published_at_utc"]))
        age_seconds = max(0, int((now - published).total_seconds()))
        silence_state = _state_from_age(age_seconds, warn_after, escalate_after)
        counts[silence_state] += 1
        row.update({
            "message_id": event.get("message_id", ""),
            "heartbeat_status": event.get("status", ""),
            "status": event.get("status", ""),
            "status_summary": event.get("status_summary", ""),
            "heartbeat_age_minutes": age_seconds // 60,
            "silence_state": silence_state,
            "published_at_utc": event.get("published_at_utc", ""),
            "last_progress_at_utc": progress_at.isoformat().replace("+00:00", "Z"),
            "current_item_refs": event.get("current_item_refs", []),
            "next_planned_action": event.get("next_planned_action", ""),
            "risk_flag": "late_heartbeat" if silence_state in {"warning", "escalated"} else "",
            "heartbeat_interval_minutes": int(heartbeat_every.total_seconds() // 60),
        })
        rows.append(row)

    rows.sort(key=lambda item: ({"escalated": 0, "warning": 1, "ok": 2, "missing": 3}.get(item["silence_state"], 4), item["chat_id"]))
    return {
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "counts": counts,
        "rows": rows,
        "latest_by_chat": latest_by_chat,
    }
