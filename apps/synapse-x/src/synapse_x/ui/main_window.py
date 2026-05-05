from __future__ import annotations

import traceback
from typing import Any, Callable

try:
    from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, QTimer, Signal
    from PySide6.QtWidgets import (
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QSplitter,
        QVBoxLayout,
        QWidget,
    )
except Exception as exc:  # noqa: BLE001
    QObject = None  # type: ignore[assignment]
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

from synapse_x.engine import SynapseEngine
from synapse_x.ui.panels.controls_panel import ControlsPanel
from synapse_x.ui.panels.detail_panel import DetailPanel
from synapse_x.ui.panels.metrics_panel import MetricsPanel
from synapse_x.ui.panels.results_panel import ResultsPanel
from synapse_x.ui.panels.search_panel import SearchPanel
from synapse_x.ui.panels.state_panel import StatePanel


if QObject is not None:

    class WorkerSignals(QObject):
        success = Signal(object)
        error = Signal(str)


    class Worker(QRunnable):
        def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
            super().__init__()
            self.fn = fn
            self.args = args
            self.kwargs = kwargs
            self.signals = WorkerSignals()

        def run(self) -> None:
            try:
                result = self.fn(*self.args, **self.kwargs)
                self.signals.success.emit(result)
            except Exception:  # noqa: BLE001
                self.signals.error.emit(traceback.format_exc())


    class SynapseMainWindow(QMainWindow):
        def __init__(self, engine: SynapseEngine) -> None:
            super().__init__()
            self.engine = engine
            self.thread_pool = QThreadPool.globalInstance()
            self._active_workers = 0
            self._last_selected_session_id: str | None = None

            self.setWindowTitle("SYNAPSE-X Studio")
            self.resize(1400, 900)

            self.state_panel = StatePanel()
            self.controls_panel = ControlsPanel()
            self.search_panel = SearchPanel()
            self.results_panel = ResultsPanel()
            self.detail_panel = DetailPanel()
            self.metrics_panel = MetricsPanel()
            self.footer = QLabel("Ready")
            self.footer.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            root = QWidget()
            root_layout = QVBoxLayout(root)
            root_layout.setContentsMargins(12, 12, 12, 12)
            root_layout.setSpacing(10)
            root_layout.addWidget(self.state_panel)
            root_layout.addWidget(self.controls_panel)
            root_layout.addWidget(self.search_panel)

            split_main = QSplitter(Qt.Horizontal)
            split_right = QSplitter(Qt.Vertical)
            split_main.addWidget(self.results_panel)
            split_main.addWidget(split_right)
            split_right.addWidget(self.detail_panel)
            split_right.addWidget(self.metrics_panel)
            split_main.setStretchFactor(0, 6)
            split_main.setStretchFactor(1, 5)
            split_right.setStretchFactor(0, 7)
            split_right.setStretchFactor(1, 4)

            root_layout.addWidget(split_main)
            root_layout.addWidget(self.footer)
            self.setCentralWidget(root)

            self.watch_timer = QTimer(self)
            self.watch_timer.timeout.connect(self._tick_watch_ingest)
            self.watch_interval_ms = 30_000

            self.controls_panel.ingest_clicked.connect(self._run_ingest)
            self.controls_panel.full_ingest_clicked.connect(self._run_full_ingest)
            self.controls_panel.repair_clicked.connect(self._run_repair)
            self.controls_panel.metrics_clicked.connect(self._refresh_metrics)
            self.controls_panel.status_clicked.connect(self._refresh_status)
            self.controls_panel.watch_toggled.connect(self._toggle_watch)
            self.controls_panel.quick_action_requested.connect(self._run_quick_action)
            self.search_panel.search_requested.connect(self._run_search)
            self.results_panel.session_selected.connect(self._load_session_detail)
            self.detail_panel.export_requested.connect(self._export_session)

            self._refresh_status()
            self._refresh_metrics()

        def _set_busy(self, busy: bool) -> None:
            self.controls_panel.set_busy(busy)
            self.state_panel.set_message("Busy..." if busy else "Ready")

        def _submit(self, action: str, fn: Callable[..., Any], on_success: Callable[[Any], None], *args: Any, **kwargs: Any) -> None:
            self._active_workers += 1
            self._set_busy(True)
            self.footer.setText(action)
            worker = Worker(fn, *args, **kwargs)
            worker.signals.success.connect(lambda result: self._on_success(result, on_success))
            worker.signals.error.connect(self._on_worker_error)
            self.thread_pool.start(worker)

        def _on_success(self, result: Any, callback: Callable[[Any], None]) -> None:
            callback(result)
            self._active_workers = max(0, self._active_workers - 1)
            if self._active_workers == 0:
                self._set_busy(False)
                self.footer.setText("Ready")

        def _on_worker_error(self, error_text: str) -> None:
            self._active_workers = max(0, self._active_workers - 1)
            if self._active_workers == 0:
                self._set_busy(False)
                self.footer.setText("Error")
            self.state_panel.set_message("Error")
            QMessageBox.critical(self, "SYNAPSE-X Error", error_text)

        def _run_ingest(self) -> None:
            self._run_ingest_with_paths(paths=None, full=False)

        def _run_full_ingest(self) -> None:
            self._run_ingest_with_paths(paths=None, full=True)

        def _run_ingest_with_paths(self, *, paths: list[str] | None, full: bool) -> None:
            if full:
                message = "Running full ingest..."
            else:
                message = "Running incremental ingest..."
            if paths:
                message = f"{message} ({len(paths)} path)"
            self._submit(message, self.engine.ingest, self._on_ingest_result, paths, full)

        def _pick_folder(self, title: str) -> str | None:
            selected = QFileDialog.getExistingDirectory(self, title, str(self.engine.settings.root))
            return selected or None

        def _on_ingest_result(self, result: dict) -> None:
            self.footer.setText(
                f"Ingest: status={result.get('status')} seen={result.get('files_seen')} processed={result.get('files_processed')} errors={result.get('errors_count')}"
            )
            self._refresh_status()
            self._refresh_metrics()

        def _run_repair(self) -> None:
            self._submit("Running repair...", self.engine.repair, self._on_repair_result)

        def _on_repair_result(self, result: dict) -> None:
            self.footer.setText(f"Repair: {result.get('status')} integrity={result.get('integrity_check')}")
            self._refresh_status()
            self._refresh_metrics()

        def _refresh_status(self) -> None:
            self._submit("Refreshing status...", self.engine.get_status, self._on_status_result)

        def _on_status_result(self, result: dict) -> None:
            self.state_panel.set_status(result)
            self.state_panel.set_message(result.get("status", "ok"))

        def _refresh_metrics(self) -> None:
            self._submit("Refreshing metrics...", self.engine.get_metrics, self.metrics_panel.set_metrics, 14)

        def _run_search(self, query: str, record_type: str, date_from: str, date_to: str, limit: int) -> None:
            if not query:
                self.footer.setText("Search query is required.")
                return
            self._submit(
                "Searching...",
                self.engine.search,
                self._on_search_result,
                query,
                record_type=record_type or None,
                date_from=date_from or None,
                date_to=date_to or None,
                limit=limit,
            )

        def _on_search_result(self, rows: list[dict]) -> None:
            self.results_panel.set_rows(rows)
            self.footer.setText(f"Search results: {len(rows)}")

        def _load_session_detail(self, session_id: str) -> None:
            self._last_selected_session_id = session_id
            self._submit("Loading session detail...", self.engine.get_session_detail, self.detail_panel.set_detail, session_id)

        def _export_session(self, session_id: str) -> None:
            self._submit("Exporting session report...", self.engine.export_session_report, self._on_export_result, session_id, None)

        def _on_export_result(self, result: dict) -> None:
            self.footer.setText(f"Export: {result.get('status')} -> {result.get('path', '-')}")

        def _export_selected_session(self) -> None:
            session_id = self.detail_panel.current_session_id() or self._last_selected_session_id
            if not session_id:
                QMessageBox.information(
                    self,
                    "SYNAPSE-X",
                    "Primero selecciona una sesion en la tabla de resultados.",
                )
                return
            self._export_session(session_id)

        def _toggle_watch(self, enabled: bool) -> None:
            if enabled:
                self.watch_timer.start(self.watch_interval_ms)
                self.footer.setText("Watch mode enabled")
            else:
                self.watch_timer.stop()
                self.footer.setText("Watch mode disabled")

        def _set_watch_enabled(self, enabled: bool) -> None:
            button = self.controls_panel.watch_button
            if button.isChecked() != enabled:
                button.setChecked(enabled)
            else:
                self._toggle_watch(enabled)

        def _run_quick_action(self, action_code: str) -> None:
            if action_code == "status":
                self._refresh_status()
                return
            if action_code == "ingest_default":
                self._run_ingest_with_paths(paths=None, full=False)
                return
            if action_code == "full_ingest_default":
                self._run_ingest_with_paths(paths=None, full=True)
                return
            if action_code == "ingest_folder":
                folder = self._pick_folder("Selecciona carpeta para ingerir")
                if folder:
                    self._run_ingest_with_paths(paths=[folder], full=False)
                else:
                    self.footer.setText("Accion cancelada.")
                return
            if action_code == "full_ingest_folder":
                folder = self._pick_folder("Selecciona carpeta para full ingest")
                if folder:
                    self._run_ingest_with_paths(paths=[folder], full=True)
                else:
                    self.footer.setText("Accion cancelada.")
                return
            if action_code == "metrics":
                self._refresh_metrics()
                return
            if action_code == "repair":
                self._run_repair()
                return
            if action_code == "watch_on":
                self._set_watch_enabled(True)
                return
            if action_code == "watch_off":
                self._set_watch_enabled(False)
                return
            if action_code == "export_selected_session":
                self._export_selected_session()
                return
            self.footer.setText(f"Accion no reconocida: {action_code}")

        def _tick_watch_ingest(self) -> None:
            if self._active_workers > 0:
                return
            self._run_ingest()
else:

    class SynapseMainWindow:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
            raise RuntimeError("PySide6 is required for SynapseMainWindow") from _IMPORT_ERROR
