from __future__ import annotations

import json
import os
from typing import Callable, Dict, List, Tuple

from .bridge_config import BridgeConfig, safe_json_dump
from .bridge_contract import normalize_mode, normalize_policy


class BridgeHistoryStore:
    """Persistence adapter for bridge run history and last payload restore."""

    def __init__(
        self,
        config: BridgeConfig,
        *,
        logger: Callable[[str], None] | None = None,
    ) -> None:
        self.config = config
        self._logger = logger

    def ensure_runtime_ready(self) -> Tuple[bool, str]:
        try:
            os.makedirs(self.config.runtime_root, exist_ok=True)
            return True, "ok"
        except Exception as exc:
            return False, f"Could not create runtime directory {self.config.runtime_root}: {exc}"

    def load_records(self) -> List[Dict[str, object]]:
        ok, detail = self.ensure_runtime_ready()
        if not ok:
            self._log(f"ERROR: {detail}")
            return []

        try:
            if not os.path.isfile(self.config.history_path):
                return []
            with open(self.config.history_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if not isinstance(data, list):
                raise ValueError("History file is not a JSON list.")
            raw_records = [item for item in data if isinstance(item, dict)]
            normalized = self._normalize_records(raw_records)
            if normalized != raw_records[-self.config.max_runs :]:
                self._log("Normalized persisted run history records.")
                self.save_records(normalized)
            return normalized[-self.config.max_runs :]
        except Exception as exc:
            self._log(f"ERROR: Could not load persisted history: {exc}")
            return []

    def save_records(self, records: List[Dict[str, object]]) -> Tuple[bool, str]:
        payload = list(records[-self.config.max_runs :])
        ok, detail = safe_json_dump(self.config.history_path, payload)
        if not ok:
            self._log(f"ERROR: Could not persist history: {detail}")
        return ok, detail

    def append_record(
        self,
        records: List[Dict[str, object]],
        record: Dict[str, object],
    ) -> List[Dict[str, object]]:
        next_records = self._normalize_records(records)
        candidate = self._normalize_record(record)
        candidate_id = self._record_identity(candidate)
        for index in range(len(next_records) - 1, -1, -1):
            current = dict(next_records[index])
            if self._record_identity(current) != candidate_id:
                continue
            next_records[index] = self._prefer_record(current, candidate)
            return self._normalize_records(next_records)
        next_records.append(candidate)
        return self._normalize_records(next_records)

    def extract_last_payload(self, records: List[Dict[str, object]]) -> Dict[str, object]:
        for item in reversed(records):
            request = item.get("request")
            if isinstance(request, dict):
                return dict(request)
        return {}

    def _log(self, message: str) -> None:
        if callable(self._logger):
            try:
                self._logger(message)
            except Exception:
                return

    def _normalize_records(self, records: List[Dict[str, object]]) -> List[Dict[str, object]]:
        cleaned: List[Dict[str, object]] = []
        index_by_identity: Dict[Tuple[str, str, str, str, str, str, str], int] = {}
        for item in records:
            normalized = self._normalize_record(item)
            identity = self._record_identity(normalized)
            existing_index = index_by_identity.get(identity)
            if existing_index is None:
                index_by_identity[identity] = len(cleaned)
                cleaned.append(normalized)
                continue
            cleaned[existing_index] = self._prefer_record(cleaned[existing_index], normalized)
        return cleaned[-self.config.max_runs :]

    def _normalize_record(self, record: Dict[str, object]) -> Dict[str, object]:
        item = dict(record or {})
        mode = normalize_mode(item.get("mode"))
        item["mode"] = mode
        item["policy"] = normalize_policy(item.get("policy"), mode)

        exit_code = item.get("exit_code")
        if exit_code is None:
            item["exit_code"] = "<none>"
        elif isinstance(exit_code, float) and exit_code.is_integer():
            item["exit_code"] = int(exit_code)
        else:
            text_code = str(exit_code).strip()
            item["exit_code"] = text_code if text_code else "<none>"
        contract_detail = str(item.get("contract_detail") or "").strip()
        if item.get("exit_code") == "<none>" and contract_detail == "LaunchFailure":
            item["exit_code"] = "process_error"

        status = str(item.get("status") or item.get("parsed_status") or "unknown").strip().lower()
        item["status"] = status or "unknown"
        if not str(item.get("parsed_status") or "").strip():
            item["parsed_status"] = item["status"]

        request = item.get("request")
        request_payload = dict(request) if isinstance(request, dict) else {}
        request_mode = normalize_mode(request_payload.get("mode"))
        request_payload["mode"] = request_mode
        request_payload["policy"] = normalize_policy(request_payload.get("policy"), request_mode)
        if "project_id" in request_payload:
            request_payload["project_id"] = str(request_payload.get("project_id") or "").strip()
        if "project_name" in request_payload:
            request_payload["project_name"] = str(request_payload.get("project_name") or "").strip()
        if "initiative_type" in request_payload:
            request_payload["initiative_type"] = str(request_payload.get("initiative_type") or "").strip()
        if "intent" in request_payload:
            request_payload["intent"] = str(request_payload.get("intent") or "").strip()
        item["request"] = request_payload
        return item

    def _record_identity(self, record: Dict[str, object]) -> Tuple[str, str, str, str, str, str, str]:
        timestamp = str(record.get("timestamp") or "").strip()
        status = str(record.get("status") or record.get("parsed_status") or "").strip().lower()
        mode = normalize_mode(record.get("mode"))
        policy = normalize_policy(record.get("policy"), mode)
        project_id = str(record.get("project_id") or "").strip()
        session_id = str(record.get("session_id") or "").strip()
        zip_path = str(
            record.get("canonical_zip_path")
            or record.get("handoff_copy_path")
            or record.get("zip_path")
            or ""
        ).strip()
        return (timestamp, status, mode, policy, project_id, session_id, zip_path)

    def _record_score(self, record: Dict[str, object]) -> int:
        score = 0
        for key in (
            "session_id",
            "run_id",
            "round_id",
            "canonical_zip_path",
            "handoff_copy_path",
            "zip_path",
            "project_manifest_path",
            "run_manifest_path",
            "round_manifest_path",
            "lock_path",
            "ledger_path",
        ):
            if str(record.get(key) or "").strip():
                score += 1
        exit_code_text = str(record.get("exit_code") or "").strip().lower()
        if exit_code_text and exit_code_text not in {"<none>", "none", "null"}:
            score += 2
        message_text = str(record.get("message") or "").strip()
        if message_text:
            score += 1
        return score

    def _prefer_record(
        self,
        left: Dict[str, object],
        right: Dict[str, object],
    ) -> Dict[str, object]:
        if self._record_score(right) > self._record_score(left):
            preferred = dict(right)
            fallback = dict(left)
        else:
            preferred = dict(left)
            fallback = dict(right)
        for key, value in fallback.items():
            if key not in preferred or preferred.get(key) in (None, "", "<none>"):
                preferred[key] = value
        return preferred


__all__ = ["BridgeHistoryStore"]
