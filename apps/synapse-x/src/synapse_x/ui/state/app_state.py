
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(slots=True)
class SearchState:
    query: str = ""
    record_type: str | None = None
    days_window: int = 14
    result_count: int = 0
    mode_label: str = "Recent"
    summary: str = "Ready"


@dataclass(slots=True)
class AppState:
    root_path: str = ""
    db_path: str = ""
    chart_visible: bool = True
    current_session_id: str = ""
    busy_task: str = ""
    runtime_status: str = "Ready"
    runtime_tone: str = "good"
    last_refresh_utc: str = ""
    last_error: str = ""
    metrics_payload: dict[str, Any] = field(default_factory=dict)
    results_rows: list[dict[str, Any]] = field(default_factory=list)
    detail_payload: dict[str, Any] = field(default_factory=dict)
    diagnostics: list[str] = field(default_factory=list)
    search: SearchState = field(default_factory=SearchState)

    def mark_busy(self, task_id: str, label: str) -> None:
        self.busy_task = str(task_id or "")
        self.runtime_status = str(label or "Working...")
        self.runtime_tone = "accent"
        self.log(f"BUSY {self.busy_task}: {self.runtime_status}")

    def mark_ready(self, label: str = "Ready") -> None:
        self.busy_task = ""
        self.runtime_status = str(label or "Ready")
        self.runtime_tone = "good"
        self.last_refresh_utc = _utc_now()
        self.log(f"READY: {self.runtime_status}")

    def mark_neutral(self, label: str = "Ready") -> None:
        self.busy_task = ""
        self.runtime_status = str(label or "Ready")
        self.runtime_tone = "neutral"
        self.log(f"NEUTRAL: {self.runtime_status}")

    def mark_error(self, label: str, error: str = "") -> None:
        self.busy_task = ""
        self.runtime_status = str(label or "Error")
        self.runtime_tone = "warn"
        self.last_error = str(error or label)
        self.log(f"ERROR: {self.last_error}")

    def record_metrics(self, payload: dict[str, Any]) -> None:
        self.metrics_payload = dict(payload or {})

    def record_results(
        self,
        rows: list[dict[str, Any]],
        *,
        mode_label: str,
        summary: str,
        query: str = "",
        record_type: str | None = None,
        days_window: int | None = None,
    ) -> None:
        self.results_rows = list(rows)
        self.search.mode_label = str(mode_label or "Results")
        self.search.summary = str(summary or "")
        self.search.query = str(query or "")
        self.search.record_type = record_type
        self.search.result_count = len(self.results_rows)
        if days_window is not None:
            self.search.days_window = int(days_window)

    def record_detail(self, session_id: str, payload: dict[str, Any]) -> None:
        self.current_session_id = str(session_id or "")
        self.detail_payload = dict(payload or {})

    def log(self, line: str) -> None:
        text = str(line or "").strip()
        if not text:
            return
        stamp = _utc_now()
        self.diagnostics.append(f"[{stamp}] {text}")
        if len(self.diagnostics) > 160:
            self.diagnostics = self.diagnostics[-160:]
