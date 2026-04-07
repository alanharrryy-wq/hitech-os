
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject

from synapse_x.config import Settings
from synapse_x.engine import SynapseEngine

from ..adapters import (
    build_demo_bundle,
    build_metrics_view_model,
    build_recent_results_model,
    build_search_results_model,
)
from ..state import AppState
from ..workers import EngineTaskRunner, TaskError, TaskOutcome


class AppController(QObject):
    def __init__(
        self,
        window,
        *,
        settings: Settings | None = None,
        engine: SynapseEngine | None = None,
        boot_demo: bool = False,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.settings = settings or Settings()
        self.engine = engine or SynapseEngine(self.settings)
        self.boot_demo = bool(boot_demo)
        self.state = AppState(root_path=str(self.settings.root), db_path=str(self.settings.db_path))
        self.worker = EngineTaskRunner(self, max_threads=2)
        self._task_versions: dict[str, int] = {}
        self._connect_worker()
        self._connect_ui()

    def _connect_worker(self) -> None:
        self.worker.taskStarted.connect(self._on_task_started)
        self.worker.taskResult.connect(self._on_task_result)
        self.worker.taskError.connect(self._on_task_error)
        self.worker.taskFinished.connect(self._on_task_finished)

    def _connect_ui(self) -> None:
        panel = self.window.controls_panel
        panel.searchRequested.connect(self.run_search)
        panel.refreshRequested.connect(self.refresh_dashboard)
        panel.repairRequested.connect(self.repair_storage)
        panel.loadDemoRequested.connect(self.load_demo_state)
        panel.loadRecentRequested.connect(self.load_recent_rows)
        panel.ingestRequested.connect(self.ingest_sample)
        panel.initDbRequested.connect(self.init_storage)
        self.window.results_panel.resultActivated.connect(self.open_result)

    def bootstrap(self) -> None:
        self.window.controls_panel.set_runtime_info(
            root_path=str(self.settings.root),
            db_path=str(self.settings.db_path),
            source_paths=[str(item) for item in self.settings.source_paths],
        )
        self.window.controls_panel.set_scope_text("Live DB")
        try:
            self.engine.init_storage()
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Bootstrap fallback: {exc}", tone="warn")
            self.load_demo_state(reason=str(exc))
            return
        if self.boot_demo:
            self.load_demo_state(reason="Booted in demo mode")
            return
        self.refresh_dashboard()

    def _next_task_id(self, key: str) -> str:
        version = int(self._task_versions.get(key, 0)) + 1
        self._task_versions[key] = version
        return f"{key}:{version}"

    def _is_current(self, task_id: str) -> bool:
        key, _, version_text = str(task_id or "").partition(":")
        if not key:
            return False
        try:
            return int(version_text or 0) == int(self._task_versions.get(key, 0))
        except Exception:
            return False

    def _set_status(self, text: str, *, tone: str = "neutral") -> None:
        self.window.controls_panel.set_state(text, tone=tone)
        self.window._set_footer_state(text, tone)
        if tone == "warn":
            self.state.mark_error(text, text)
        elif tone == "accent":
            self.state.mark_busy(self.state.busy_task or "ui", text)
        elif tone == "good":
            self.state.mark_ready(text)
        else:
            self.state.mark_neutral(text)

    def init_storage(self) -> None:
        try:
            self.engine.init_storage()
            self._set_status("Storage initialized", tone="good")
            self.refresh_dashboard()
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Storage init failed: {exc}", tone="warn")
            self.window.detail_panel.set_error("Storage init failed", str(exc))

    def refresh_dashboard(self) -> None:
        days = self.window.controls_panel.days_window()
        task_id = self._next_task_id("dashboard")
        self.state.mark_busy(task_id, "Refreshing synapse-x deck...")
        self.window.results_panel.set_loading("Refreshing recent records and telemetry...")
        self.window.metrics_panel.set_busy_state("Refreshing metrics and trends...")
        self._set_status("Refreshing synapse-x deck...", tone="accent")
        self.worker.submit(task_id, self._collect_dashboard_payload, days=days)

    def load_recent_rows(self) -> None:
        task_id = self._next_task_id("recent")
        self.state.mark_busy(task_id, "Loading recent rows...")
        self.window.results_panel.set_loading("Loading recent indexed rows...")
        self._set_status("Loading recent rows...", tone="accent")
        self.worker.submit(task_id, self._load_recent_rows_from_db, limit=40)

    def run_search(self, query: str | None = None) -> None:
        text = (query if query is not None else self.window.controls_panel.query_text()).strip()
        if not text:
            self.window.focus_search()
            self._set_status("Search query is empty", tone="warn")
            return
        task_id = self._next_task_id("search")
        record_type = self.window.controls_panel.record_type()
        self.state.mark_busy(task_id, f"Searching for: {text}")
        self.window.results_panel.set_loading(f"Searching indexed memory for '{text}'...")
        self._set_status(f"Searching for: {text}", tone="accent")
        self.worker.submit(
            task_id,
            self.engine.search,
            text,
            record_type=record_type,
            limit=80,
        )

    def repair_storage(self) -> None:
        task_id = self._next_task_id("repair")
        self.state.mark_busy(task_id, "Repairing storage indexes...")
        self.window.detail_panel.set_loading("repair")
        self._set_status("Repairing storage indexes...", tone="accent")
        self.worker.submit(task_id, self.engine.repair)

    def ingest_sample(self) -> None:
        task_id = self._next_task_id("ingest")
        self.state.mark_busy(task_id, "Running incremental ingest against source paths...")
        self.window.detail_panel.set_loading("ingest")
        self._set_status("Running incremental ingest...", tone="accent")
        self.worker.submit(task_id, self._run_incremental_ingest)

    def open_result(self, row: dict[str, Any]) -> None:
        payload = dict(row or {})
        session_id = str(payload.get("session_id") or "").strip()
        self.window.detail_panel.set_result_row(payload)
        if not session_id:
            return
        task_id = self._next_task_id("detail")
        self.state.mark_busy(task_id, f"Hydrating session {session_id}...")
        self.window.detail_panel.set_loading(session_id)
        self._set_status(f"Hydrating session {session_id}...", tone="accent")
        self.worker.submit(task_id, self.engine.get_session_detail, session_id)

    def load_demo_state(self, reason: str | None = None) -> None:
        bundle = build_demo_bundle()
        self.state.record_metrics(bundle["metrics"])
        self.window.metrics_panel.set_metrics_payload(bundle["metrics"])
        results = bundle["results"]
        self.state.record_results(
            list(results["rows"]),
            mode_label=str(results["mode_label"]),
            summary=str(results["summary"]),
            days_window=self.window.controls_panel.days_window(),
        )
        self.window.results_panel.set_results(
            list(results["rows"]),
            summary=str(results["summary"]),
            mode_label=str(results["mode_label"]),
        )
        self.window.detail_panel.set_session_detail(dict(bundle["detail"]))
        label = "Demo state loaded" if not reason else f"Demo state loaded · {reason}"
        self._set_status(label, tone="good")

    def _collect_dashboard_payload(self, *, days: int) -> dict[str, Any]:
        metrics_raw = self.engine.get_metrics(days=days)
        recent_rows = self._load_recent_rows_from_db(limit=30)
        return {
            "days": int(days),
            "metrics": build_metrics_view_model(metrics_raw),
            "recent": build_recent_results_model(recent_rows),
        }

    def _run_incremental_ingest(self) -> dict[str, Any]:
        result = self.engine.ingest(paths=[str(item) for item in self.settings.source_paths], full=False)
        return dict(result or {})

    def _load_recent_rows_from_db(self, limit: int = 30) -> list[dict[str, Any]]:
        db_path = Path(self.settings.db_path)
        if not db_path.exists():
            return []
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                """
                SELECT session_id, timestamp_utc, record_type, source_path,
                       COALESCE(summary, title, record_type) AS text
                FROM records
                ORDER BY timestamp_utc DESC
                LIMIT ?
                """,
                (max(1, int(limit)),),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def _on_task_started(self, task_id: str) -> None:
        if not self._is_current(task_id):
            return
        self.state.log(f"started {task_id}")

    def _on_task_finished(self, task_id: str) -> None:
        if not self._is_current(task_id):
            return
        self.state.log(f"finished {task_id}")

    def _on_task_result(self, outcome: TaskOutcome) -> None:
        task_id = outcome.task_id
        if not self._is_current(task_id):
            return
        key = task_id.split(":", 1)[0]
        payload = outcome.payload

        if key == "dashboard":
            metrics_vm = dict(payload.get("metrics") or {})
            recent_vm = dict(payload.get("recent") or {})
            self.state.record_metrics(metrics_vm)
            self.window.metrics_panel.set_metrics_payload(metrics_vm)
            rows = list(recent_vm.get("rows") or [])
            self.state.record_results(
                rows,
                mode_label=str(recent_vm.get("mode_label") or "Recent"),
                summary=str(recent_vm.get("summary") or ""),
                days_window=int(payload.get("days") or self.window.controls_panel.days_window()),
            )
            self.window.results_panel.set_results(
                rows,
                summary=str(recent_vm.get("summary") or "Recent rows loaded."),
                mode_label=str(recent_vm.get("mode_label") or "Recent"),
            )
            self._set_status("Dashboard refreshed", tone="good")
            return

        if key == "recent":
            vm = build_recent_results_model(payload)
            rows = list(vm.get("rows") or [])
            self.state.record_results(
                rows,
                mode_label=str(vm.get("mode_label") or "Recent"),
                summary=str(vm.get("summary") or ""),
                days_window=self.window.controls_panel.days_window(),
            )
            self.window.results_panel.set_results(rows, summary=str(vm.get("summary") or "Recent rows loaded."), mode_label=str(vm.get("mode_label") or "Recent"))
            self._set_status("Recent rows loaded", tone="good")
            return

        if key == "search":
            query = self.window.controls_panel.query_text()
            record_type = self.window.controls_panel.record_type()
            vm = build_search_results_model(payload, query=query, record_type=record_type)
            rows = list(vm.get("rows") or [])
            self.state.record_results(
                rows,
                mode_label=str(vm.get("mode_label") or "Search"),
                summary=str(vm.get("summary") or ""),
                query=query,
                record_type=record_type,
                days_window=self.window.controls_panel.days_window(),
            )
            self.window.results_panel.set_results(rows, summary=str(vm.get("summary") or "Search complete."), mode_label=str(vm.get("mode_label") or "Search"))
            self._set_status(f"Search complete: {len(rows)} rows", tone="good")
            return

        if key == "repair":
            repair_payload = dict(payload or {})
            self.window.detail_panel.set_payload_title("Repair Result", "Storage integrity and search indexes were refreshed.")
            self.window.detail_panel.set_result_row({
                "session_id": "repair",
                "record_type": "operation",
                "text": f"Repair status: {repair_payload.get('status')}",
                "summary": f"Integrity: {repair_payload.get('integrity_check')} · FTS enabled: {repair_payload.get('fts_enabled')}",
            })
            self.window.detail_panel.set_session_detail({
                "session": {"session_id": "repair", "confidence": repair_payload.get("status")},
                "records": [],
                "errors": [],
                "tools": [],
                "timeline": [],
                "session_insights": {},
                "related_sessions": [],
                "raw": repair_payload,
            })
            self._set_status("Storage repair complete", tone="good")
            return

        if key == "ingest":
            ingest_payload = dict(payload or {})
            self.window.detail_panel.set_result_row({
                "session_id": "ingest",
                "record_type": "operation",
                "text": f"Ingest status: {ingest_payload.get('status')}",
                "summary": f"Processed {ingest_payload.get('files_processed')} / {ingest_payload.get('files_seen')} files",
            })
            self.window.detail_panel.set_session_detail({
                "session": {"session_id": "ingest", "confidence": ingest_payload.get("status")},
                "records": [],
                "errors": [{"error_type": "ingest", "message": item.get("error")} for item in ingest_payload.get("failures") or []],
                "tools": [],
                "timeline": [],
                "session_insights": {"confidence": ingest_payload.get("status")},
                "related_sessions": [],
                "raw": ingest_payload,
            })
            self._set_status("Incremental ingest complete", tone="good")
            self.refresh_dashboard()
            return

        if key == "detail":
            detail_payload = dict(payload or {})
            session = detail_payload.get("session") or {}
            session_id = str(session.get("session_id") or self.window.results_panel.current_session_id() or "detail")
            self.state.record_detail(session_id, detail_payload)
            self.window.detail_panel.set_session_detail(detail_payload)
            self._set_status(f"Session {session_id} hydrated", tone="good")
            return

    def _on_task_error(self, error: TaskError) -> None:
        if not self._is_current(error.task_id):
            return
        key = error.task_id.split(":", 1)[0]
        label = f"{key.title()} failed: {error.message}"
        self.state.mark_error(label, error.traceback_text)
        self.window.detail_panel.set_error(label, error.traceback_text)
        if key in {"search", "recent", "dashboard"}:
            self.window.results_panel.clear_results(summary=label)
        if key == "dashboard":
            self.window.metrics_panel.load_demo_state()
        self.window.controls_panel.push_diagnostic(error.message)
        self.window._set_footer_state(label, "warn")
