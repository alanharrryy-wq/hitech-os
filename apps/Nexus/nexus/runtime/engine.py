from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any


NEXUS_STAGE_SEQUENCE: tuple[str, ...] = (
    "intake",
    "quote",
    "follow_up",
    "operations",
    "closed",
)
NEXUS_APPROVAL_STATES: tuple[str, ...] = ("pending", "approved", "rejected", "hold")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class NexusRuntimeEngine:
    """
    Nexus runtime/business engine.

    Keeps business/runtime behavior independent from UI widgets.
    """

    workspace_id: str = "nexus-main"
    _records: dict[str, dict[str, Any]] = field(default_factory=dict, init=False)
    _approvals: dict[str, dict[str, Any]] = field(default_factory=dict, init=False)
    _timeline: list[dict[str, Any]] = field(default_factory=list, init=False)
    _sequence: int = field(default=0, init=False)
    _lock: RLock = field(default_factory=RLock, init=False)

    def __post_init__(self) -> None:
        self._seed_defaults()

    def upsert_record(self, record_id: str, record: dict[str, Any], *, actor: str) -> dict[str, Any]:
        normalized_id = str(record_id or "").strip()
        if not normalized_id:
            raise ValueError("record_id is required")
        if not isinstance(record, dict):
            raise ValueError("record payload must be a mapping")

        stage = str(record.get("stage") or "intake").strip().lower()
        if stage not in NEXUS_STAGE_SEQUENCE:
            raise ValueError(f"unsupported stage '{stage}'")

        now = _utc_iso()
        with self._lock:
            current = dict(self._records.get(normalized_id) or {})
            current.update(
                {
                    "record_id": normalized_id,
                    "title": str(record.get("title") or current.get("title") or normalized_id),
                    "owner": str(record.get("owner") or current.get("owner") or "unassigned"),
                    "stage": stage,
                    "status": str(record.get("status") or current.get("status") or "active").strip().lower(),
                    "tags": self._normalize_tags(record.get("tags") or current.get("tags") or []),
                    "metadata": dict(record.get("metadata") or current.get("metadata") or {}),
                    "updated_at": now,
                }
            )
            if "created_at" not in current:
                current["created_at"] = now
            self._records[normalized_id] = current
            self._ensure_approval_record(normalized_id, actor=actor)
            self._append_timeline(
                event="nexus.runtime.record.upserted",
                actor=actor,
                message=f"record '{normalized_id}' upserted",
                payload={"record_id": normalized_id, "stage": stage},
            )
            return dict(current)

    def set_record_stage(self, record_id: str, stage: str, *, actor: str, note: str = "") -> dict[str, Any]:
        normalized_id = str(record_id or "").strip()
        target_stage = str(stage or "").strip().lower()
        if not normalized_id:
            raise ValueError("record_id is required")
        if target_stage not in NEXUS_STAGE_SEQUENCE:
            raise ValueError(f"unsupported stage '{target_stage}'")

        now = _utc_iso()
        with self._lock:
            current = self._records.get(normalized_id)
            if current is None:
                raise ValueError(f"record '{normalized_id}' was not found")
            current["stage"] = target_stage
            current["updated_at"] = now
            if note:
                current.setdefault("metadata", {})
                current["metadata"]["last_stage_note"] = str(note)
            self._append_timeline(
                event="nexus.runtime.record.stage_changed",
                actor=actor,
                message=f"record '{normalized_id}' moved to stage '{target_stage}'",
                payload={"record_id": normalized_id, "stage": target_stage, "note": str(note)},
            )
            return dict(current)

    def set_approval_state(
        self,
        record_id: str,
        state: str,
        *,
        actor: str,
        note: str = "",
    ) -> dict[str, Any]:
        normalized_id = str(record_id or "").strip()
        normalized_state = str(state or "").strip().lower()
        if not normalized_id:
            raise ValueError("record_id is required")
        if normalized_state not in NEXUS_APPROVAL_STATES:
            raise ValueError(f"unsupported approval state '{normalized_state}'")

        now = _utc_iso()
        with self._lock:
            self._ensure_approval_record(normalized_id, actor=actor)
            approval = self._approvals[normalized_id]
            approval["state"] = normalized_state
            approval["updated_at"] = now
            approval["last_actor"] = actor
            if note:
                approval["note"] = str(note)
            self._append_timeline(
                event="nexus.runtime.approval.state_changed",
                actor=actor,
                message=f"approval for '{normalized_id}' set to '{normalized_state}'",
                payload={"record_id": normalized_id, "state": normalized_state, "note": str(note)},
            )
            return dict(approval)

    def append_note(self, record_id: str, note: str, *, actor: str) -> dict[str, Any]:
        normalized_id = str(record_id or "").strip()
        message = str(note or "").strip()
        if not normalized_id:
            raise ValueError("record_id is required")
        if not message:
            raise ValueError("note is required")

        now = _utc_iso()
        with self._lock:
            current = self._records.get(normalized_id)
            if current is None:
                raise ValueError(f"record '{normalized_id}' was not found")
            notes = list(current.get("notes") or [])
            notes.append({"text": message, "actor": actor, "created_at": now})
            current["notes"] = notes
            current["updated_at"] = now
            self._append_timeline(
                event="nexus.runtime.note.appended",
                actor=actor,
                message=f"note appended to '{normalized_id}'",
                payload={"record_id": normalized_id, "note": message},
            )
            return {"record_id": normalized_id, "notes": list(notes)}

    def summary(self) -> dict[str, Any]:
        with self._lock:
            stage_counts = {stage: 0 for stage in NEXUS_STAGE_SEQUENCE}
            for record in self._records.values():
                stage = str(record.get("stage") or "intake")
                stage_counts[stage] = stage_counts.get(stage, 0) + 1

            approval_counts = {state: 0 for state in NEXUS_APPROVAL_STATES}
            for approval in self._approvals.values():
                state = str(approval.get("state") or "pending")
                approval_counts[state] = approval_counts.get(state, 0) + 1

            return {
                "workspace_id": self.workspace_id,
                "record_count": len(self._records),
                "approval_count": len(self._approvals),
                "stage_counts": stage_counts,
                "approval_counts": approval_counts,
                "latest_event_sequence": self._sequence,
            }

    def list_records(self) -> list[dict[str, Any]]:
        with self._lock:
            rows = [dict(item) for item in self._records.values()]
        rows.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)
        return rows

    def get_record(self, record_id: str) -> dict[str, Any] | None:
        normalized_id = str(record_id or "").strip()
        if not normalized_id:
            return None
        with self._lock:
            value = self._records.get(normalized_id)
            return dict(value) if value is not None else None

    def list_approvals(self) -> list[dict[str, Any]]:
        with self._lock:
            rows = [dict(item) for item in self._approvals.values()]
        rows.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)
        return rows

    def workspace_snapshot(self) -> dict[str, Any]:
        return {
            "workspace": {
                "summary": self.summary(),
                "records": self.list_records(),
                "approvals": self.list_approvals(),
            }
        }

    def timeline_snapshot(self, *, limit: int = 60) -> dict[str, Any]:
        max_items = max(1, int(limit))
        with self._lock:
            items = list(self._timeline[-max_items:])
            cursor = self._sequence
        return {
            "timeline": {
                "cursor": cursor,
                "count": len(items),
                "entries": items,
            }
        }

    def health_snapshot(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            "health": {
                "module_status": "healthy",
                "workspace_id": self.workspace_id,
                "record_count": summary["record_count"],
                "pending_approvals": summary["approval_counts"].get("pending", 0),
                "timeline_depth": summary["latest_event_sequence"],
                "integration_mode": "in_process_preferred",
            }
        }

    def _normalize_tags(self, value: Any) -> list[str]:
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        if isinstance(value, (list, tuple, set)):
            tags = [str(item).strip() for item in value if str(item).strip()]
            return tags
        return []

    def _ensure_approval_record(self, record_id: str, *, actor: str) -> None:
        if record_id in self._approvals:
            return
        now = _utc_iso()
        self._approvals[record_id] = {
            "record_id": record_id,
            "state": "pending",
            "assignee": "ops-review",
            "note": "",
            "updated_at": now,
            "last_actor": actor,
        }

    def _append_timeline(
        self,
        *,
        event: str,
        actor: str,
        message: str,
        payload: dict[str, Any],
    ) -> None:
        self._sequence += 1
        self._timeline.append(
            {
                "sequence": self._sequence,
                "event": str(event),
                "actor": str(actor or "system"),
                "message": str(message),
                "timestamp_utc": _utc_iso(),
                "payload": dict(payload),
            }
        )

    def _seed_defaults(self) -> None:
        seed_records = [
            {
                "record_id": "nx-1001",
                "record": {
                    "title": "Northbound intake",
                    "owner": "agent.intake",
                    "stage": "intake",
                    "status": "active",
                    "tags": ["intake", "new"],
                },
            },
            {
                "record_id": "nx-1002",
                "record": {
                    "title": "Regional quote review",
                    "owner": "agent.quote",
                    "stage": "quote",
                    "status": "active",
                    "tags": ["quote", "pricing"],
                },
            },
            {
                "record_id": "nx-1003",
                "record": {
                    "title": "Ops follow-up queue",
                    "owner": "agent.ops",
                    "stage": "follow_up",
                    "status": "active",
                    "tags": ["follow_up", "ops"],
                },
            },
        ]
        for item in seed_records:
            self.upsert_record(item["record_id"], item["record"], actor="seed")

