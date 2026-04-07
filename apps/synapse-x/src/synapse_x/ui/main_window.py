
from __future__ import annotations

import sqlite3
import traceback
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QFrame, QSplitter, QVBoxLayout, QWidget

from synapse_x.config import Settings
from synapse_x.engine import SynapseEngine
from visuals.common.types import ActionSpec, ChipSpec, TemplateConsoleConfig
from visuals.screens.template_console import TemplateConsoleWindow

from .panels import ControlsPanel, DetailPanel, MetricsPanel, ResultsPanel


def _build_config() -> TemplateConsoleConfig:
    return TemplateConsoleConfig(
        window_title="synapse-x Operations Deck",
        theme_id="silver_frost_cyan",
        ui_scale="100",
        hero_eyebrow="Operational Memory",
        hero_title="synapse-x Operations Deck",
        hero_subtitle=(
            "Live glass host for recent records, indexed search, detail inspection, "
            "metrics telemetry, and graceful chart fallback."
        ),
        hero_icon="workspace",
        hero_chips=[
            ChipSpec("synapse-x", tone="accent", icon="spark"),
            ChipSpec("Operations Deck", tone="neutral", icon="overview"),
            ChipSpec("Indexed Memory", tone="neutral", icon="search"),
        ],
        toolbar_title="Command Rail",
        toolbar_actions=[
            ActionSpec("refresh", "Refresh", icon="refresh", variant="secondary"),
            ActionSpec("focus_search", "Search", icon="search", variant="secondary"),
            ActionSpec("load_demo", "Demo", icon="spark", variant="secondary"),
            ActionSpec("repair_storage", "Repair", icon="settings", variant="secondary"),
            ActionSpec("open_selector", "Workspace", icon="workspace", variant="secondary"),
            ActionSpec("toggle_sidebar", "Sidebar", icon="panel", variant="secondary"),
            ActionSpec("toggle_charts", "Charts", icon="overview", variant="secondary", checkable=True, checked=True),
        ],
        panel_order=("sidebar", "main", "aux"),
        show_sidebar=True,
        show_aux=True,
        sidebar_title="Controls",
        main_title="Results + Detail",
        aux_title="Live Metrics",
        show_sidebar_builtin_controls=False,
        sidebar_hint="Search, refresh, repair, demo load, and runtime context live here.",
        main_hint="Recent and searched records stay on top, while the detail inspector hydrates beneath them.",
        aux_hint="Live telemetry and charted trends render here when optional chart extras are available.",
        footer_hint="run_ui.py is now the real UI entrypoint. starter.py remains a shell/demo launcher.",
    )


class SynapseXMainWindow(TemplateConsoleWindow):
    def __init__(self, *, settings: Settings | None = None, engine: SynapseEngine | None = None) -> None:
        self.settings = settings or Settings()
        self.engine = engine or SynapseEngine(self.settings)
        self._shortcuts: list[QShortcut] = []
        self._busy = False
        super().__init__(config=_build_config())

        self.controls_panel = ControlsPanel(self)
        self.results_panel = ResultsPanel(self)
        self.detail_panel = DetailPanel(self)
        self.metrics_panel = MetricsPanel(self)

        self._mount_product_surfaces()
        self._wire_signals()
        self._install_shortcuts()
        self._bootstrap_runtime()

    def _mount_product_surfaces(self) -> None:
        self.set_slot_widget("sidebar", self.controls_panel)

        main_surface = QWidget(self)
        main_layout = QVBoxLayout(main_surface)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Vertical, main_surface)
        splitter.addWidget(self.results_panel)
        splitter.addWidget(self.detail_panel)
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)
        splitter.setSizes([420, 280])
        main_layout.addWidget(splitter, 1)

        self.set_slot_widget("main", main_surface)
        self.set_chart_widget(self.metrics_panel)

    def _wire_signals(self) -> None:
        self.controls_panel.searchRequested.connect(self.run_search)
        self.controls_panel.refreshRequested.connect(self.refresh_dashboard)
        self.controls_panel.repairRequested.connect(self.repair_storage)
        self.controls_panel.loadDemoRequested.connect(self.load_demo_state)
        self.controls_panel.loadRecentRequested.connect(self.load_recent_rows)
        self.results_panel.resultActivated.connect(self._on_result_selected)

    def _install_shortcuts(self) -> None:
        bindings = {
            "Ctrl+R": self.refresh_dashboard,
            "Ctrl+L": self.focus_search,
            "Ctrl+Shift+C": self.toggle_chart_visibility,
            "Ctrl+E": self.repair_storage,
            "Ctrl+D": self.load_demo_state,
        }
        for sequence, callback in bindings.items():
            shortcut = QShortcut(QKeySequence(sequence), self)
            shortcut.activated.connect(callback)
            self._shortcuts.append(shortcut)

    def _bootstrap_runtime(self) -> None:
        self.controls_panel.set_runtime_info(
            root_path=str(self.settings.root),
            db_path=str(self.settings.db_path),
        )
        try:
            self.engine.init_storage()
            self.refresh_dashboard()
        except Exception as exc:  # noqa: BLE001
            self.load_demo_state()
            self.detail_panel.set_result_row({"session_id": "bootstrap", "record_type": "error", "text": str(exc)})
            self._set_footer_state(f"Bootstrap fallback: {exc}", "warn")

    def focus_search(self) -> None:
        self.controls_panel.focus_query()
        self._set_footer_state("Search focused", "accent")

    def _set_busy(self, active: bool, label: str) -> None:
        self._busy = bool(active)
        self.controls_panel.set_state(label, tone="accent" if active else "good")
        self._set_footer_state(label, "accent" if active else "good")

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
        except Exception:
            return []
        finally:
            conn.close()

    def refresh_dashboard(self) -> None:
        self._set_busy(True, "Refreshing synapse-x deck...")
        try:
            metrics = self.engine.get_metrics(days=self.controls_panel.days_window())
            self.metrics_panel.set_metrics_payload(metrics)
            recent = self._load_recent_rows_from_db(limit=30)
            if recent:
                self.results_panel.set_results(
                    recent,
                    summary="Latest indexed records from the operational memory store.",
                    mode_label="Recent",
                )
            else:
                self.results_panel.clear_results(summary="Storage is live, but there are no recent records yet.")
            self._set_footer_state("Dashboard refreshed", "good")
        except Exception as exc:  # noqa: BLE001
            self._set_footer_state(f"Refresh failed: {exc}", "warn")
            self.detail_panel.set_result_row(
                {
                    "session_id": "refresh-error",
                    "record_type": "error",
                    "text": traceback.format_exc(limit=6),
                }
            )
        finally:
            self._set_busy(False, "Ready")

    def load_recent_rows(self) -> None:
        rows = self._load_recent_rows_from_db(limit=40)
        if rows:
            self.results_panel.set_results(
                rows,
                summary="Recent indexed records from SQLite storage.",
                mode_label="Recent",
            )
            self._set_footer_state("Recent rows loaded", "good")
            return
        self.results_panel.clear_results(summary="No indexed records available yet.")
        self._set_footer_state("No recent rows available", "neutral")

    def run_search(self, query: str | None = None) -> None:
        text = (query if query is not None else self.controls_panel.query_text()).strip()
        if not text:
            self.focus_search()
            self._set_footer_state("Search query is empty", "warn")
            return

        self._set_busy(True, f"Searching for: {text}")
        try:
            rows = self.engine.search(
                text,
                record_type=self.controls_panel.record_type(),
                limit=80,
            )
            self.results_panel.set_results(
                rows,
                summary=f"Search returned {len(rows)} indexed rows for '{text}'.",
                mode_label="Search",
            )
            self._set_footer_state(f"Search complete: {len(rows)} rows", "good")
        except Exception as exc:  # noqa: BLE001
            self.results_panel.clear_results(summary=f"Search failed: {exc}")
            self._set_footer_state(f"Search failed: {exc}", "warn")
        finally:
            self._set_busy(False, "Ready")

    def load_demo_state(self) -> None:
        self.metrics_panel.load_demo_state()
        demo_rows = [
            {
                "session_id": "demo-2026-04-06-a",
                "timestamp_utc": "2026-04-06T09:14:00Z",
                "record_type": "log",
                "source_path": "sample_inputs/demo_a.log",
                "text": "Queued ingest completed with 31 records and a minor timeout spike.",
            },
            {
                "session_id": "demo-2026-04-06-b",
                "timestamp_utc": "2026-04-06T10:22:00Z",
                "record_type": "report",
                "source_path": "sample_inputs/demo_b.md",
                "text": "Repair normalized index consistency and cleared a stale FTS fragment.",
            },
        ]
        self.results_panel.set_results(
            demo_rows,
            summary="Demo rows loaded so the deck stays useful even before real data arrives.",
            mode_label="Demo",
        )
        self.detail_panel.set_result_row(demo_rows[0])
        self._set_footer_state("Demo state loaded", "accent")

    def repair_storage(self) -> None:
        self._set_busy(True, "Repairing storage...")
        try:
            result = self.engine.repair()
            self.detail_panel.set_session_detail({"session": {"session_id": "repair"}, "session_insights": result})
            self._set_footer_state(f"Repair complete: {result.get('status', 'ok')}", "good")
            self.refresh_dashboard()
        except Exception as exc:  # noqa: BLE001
            self._set_footer_state(f"Repair failed: {exc}", "warn")
            self.detail_panel.set_result_row(
                {
                    "session_id": "repair-error",
                    "record_type": "error",
                    "text": traceback.format_exc(limit=6),
                }
            )
        finally:
            self._set_busy(False, "Ready")

    def _on_result_selected(self, row: dict[str, Any]) -> None:
        self.detail_panel.set_result_row(row)
        session_id = str(row.get("session_id") or "").strip()
        if not session_id:
            return
        try:
            payload = self.engine.get_session_detail(session_id)
            self.detail_panel.set_session_detail(payload)
            self._set_footer_state(f"Detail hydrated: {session_id}", "good")
        except Exception as exc:  # noqa: BLE001
            self._set_footer_state(f"Detail load failed: {exc}", "warn")

    def _on_toolbar_action(self, action_id: str) -> None:
        if action_id == "refresh":
            self.refresh_dashboard()
            return
        if action_id == "focus_search":
            self.focus_search()
            return
        if action_id == "load_demo":
            self.load_demo_state()
            return
        if action_id == "repair_storage":
            self.repair_storage()
            return
        super()._on_toolbar_action(action_id)
