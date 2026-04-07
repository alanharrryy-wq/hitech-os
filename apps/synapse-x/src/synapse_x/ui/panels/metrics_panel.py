
from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from visuals.controls.chips import create_chip
from visuals.effects.shadow import apply_shadow
from visuals.widgets.charts import build_chart_card, chart_ui_available, missing_chart_dependencies
from visuals.widgets.charts.engine import GlassChartSeries

from ..widgets.empty_state import EmptyStateCard
from ..widgets.kpi_strip import KPIStrip


class MetricsPanel(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("card", "true")
        apply_shadow(self, blur=16.0, y_offset=6.0, alpha=12)
        self._chart_widget: QWidget | None = None
        self._payload: dict[str, Any] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header = QGridLayout()
        header.setHorizontalSpacing(8)
        header.setVerticalSpacing(6)
        layout.addLayout(header)

        self.title_label = QLabel("Metrics Surface", self)
        self.title_label.setProperty("role", "section")
        header.addWidget(self.title_label, 0, 0)

        self.subtitle_label = QLabel("Storage health, telemetry posture, and charted trends land here.", self)
        self.subtitle_label.setProperty("role", "hint")
        self.subtitle_label.setWordWrap(True)
        header.addWidget(self.subtitle_label, 1, 0)

        self.state_chip = create_chip("Live", tone="good", icon="status", parent=self)
        self.chart_chip = create_chip("Charts ready", tone="accent", icon="chart", parent=self)
        header.addWidget(self.state_chip, 0, 1)
        header.addWidget(self.chart_chip, 1, 1)

        self.kpis = KPIStrip(self, columns=4)
        layout.addWidget(self.kpis)

        self.chart_container = QFrame(self)
        self.chart_container.setProperty("card", "muted")
        self.chart_layout = QVBoxLayout(self.chart_container)
        self.chart_layout.setContentsMargins(0, 0, 0, 0)
        self.chart_layout.setSpacing(0)
        layout.addWidget(self.chart_container, 1)

        lower = QGridLayout()
        lower.setHorizontalSpacing(10)
        lower.setVerticalSpacing(10)
        layout.addLayout(lower)

        self.top_errors = QListWidget(self)
        self.top_tools = QListWidget(self)
        self.sequence_patterns = QListWidget(self)

        lower.addWidget(self._wrap_list("Top Errors", self.top_errors), 0, 0)
        lower.addWidget(self._wrap_list("Top Tools", self.top_tools), 0, 1)
        lower.addWidget(self._wrap_list("Sequence Patterns", self.sequence_patterns), 1, 0, 1, 2)

        self.load_demo_state()

    def _wrap_list(self, title: str, widget: QListWidget) -> QFrame:
        frame = QFrame(self)
        frame.setProperty("card", "muted")
        apply_shadow(frame, blur=14.0, y_offset=5.0, alpha=10)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        heading = QLabel(title, frame)
        heading.setProperty("role", "section")
        layout.addWidget(heading)
        widget.setMinimumHeight(110)
        layout.addWidget(widget, 1)
        return frame

    def _replace_chart_widget(self, widget: QWidget) -> None:
        while self.chart_layout.count():
            item = self.chart_layout.takeAt(0)
            child = item.widget()
            if child is not None:
                child.setParent(None)
                child.deleteLater()
        self._chart_widget = widget
        self.chart_layout.addWidget(widget, 1)

    def _set_list(self, widget: QListWidget, items: list[dict[str, Any]], *, key: str, secondary: str | None = None) -> None:
        widget.clear()
        if not items:
            widget.addItem(QListWidgetItem("No data yet."))
            return
        for item in items[:8]:
            primary = str(item.get(key) or item.get("label") or item.get("name") or item)
            suffix = ""
            if secondary:
                value = item.get(secondary)
                if value not in {None, ""}:
                    suffix = f" · {value}"
            widget.addItem(QListWidgetItem(primary + suffix))

    def _build_series(self, payload: dict[str, Any]) -> tuple[GlassChartSeries, ...]:
        daily = list(reversed(payload.get("daily_activity") or []))
        if not daily:
            return (
                GlassChartSeries(name="Requests", x=tuple(range(6)), y=(10, 12, 15, 14, 18, 20), mode="area", fill_to_zero=True),
                GlassChartSeries(name="Trend", x=tuple(range(6)), y=(9, 11, 13, 13, 15, 17), mode="line", symbol="o"),
                GlassChartSeries(name="Volatility", x=tuple(range(6)), y=(2, 1, 3, 2, 4, 2), mode="spark"),
            )
        counts = [float(item.get("count") or 0.0) for item in daily]
        trend = []
        for idx in range(len(counts)):
            window = counts[max(0, idx - 2): idx + 1]
            trend.append(sum(window) / max(1, len(window)))
        volatility = [abs(counts[idx] - counts[idx - 1]) + 1.0 if idx > 0 else 1.0 for idx in range(len(counts))]
        x_values = tuple(float(idx) for idx in range(len(counts)))
        return (
            GlassChartSeries(name="Records / day", x=x_values, y=tuple(counts), mode="area", fill_to_zero=True),
            GlassChartSeries(name="Trend", x=x_values, y=tuple(round(item, 2) for item in trend), mode="line", symbol="o"),
            GlassChartSeries(name="Volatility", x=x_values, y=tuple(round(item, 2) for item in volatility), mode="spark"),
        )

    def _build_chart_title(self, payload: dict[str, Any]) -> str:
        total_records = int((payload.get("totals") or {}).get("records") or 0)
        total_errors = int((payload.get("totals") or {}).get("errors") or 0)
        return f"Runtime Overview · {total_records} records / {total_errors} errors"

    def _chart_subtitle(self, payload: dict[str, Any]) -> str:
        activity = payload.get("daily_activity") or []
        window = len(activity)
        return f"Daily activity, smoothed trend, and volatility across the latest {window or 6}-day window."

    def set_metrics_payload(self, payload: dict[str, Any]) -> None:
        self._payload = dict(payload or {})
        totals = self._payload.get("totals") or {}
        self.kpis.set_metrics(
            [
                {"label": "Sessions", "value": totals.get("sessions", 0), "detail": "linked session footprints"},
                {"label": "Records", "value": totals.get("records", 0), "detail": "indexed canonical rows"},
                {"label": "Errors", "value": totals.get("errors", 0), "detail": "error events tracked"},
                {"label": "Files", "value": totals.get("files", 0), "detail": "source files fingerprinted"},
            ]
        )

        self._set_list(self.top_errors, list(self._payload.get("top_errors") or []), key="error_type", secondary="count")
        self._set_list(self.top_tools, list(self._payload.get("top_tools") or []), key="tool_name", secondary="count")
        self._set_list(self.sequence_patterns, list(self._payload.get("sequence_patterns") or []), key="pattern", secondary="count")

        self.title_label.setText("Metrics Surface")
        self.subtitle_label.setText(self._chart_subtitle(self._payload))
        self.state_chip.setText("Live")
        if chart_ui_available():
            chart = build_chart_card(
                title=self._build_chart_title(self._payload),
                subtitle=self._chart_subtitle(self._payload),
                experience_mode="dashboard",
                visual_level="showcase",
                data_state="ready" if int(totals.get("errors", 0) or 0) == 0 else "stale",
                series=self._build_series(self._payload),
                parent=self,
            )
            self.chart_chip.setText("Charts ready")
            self._replace_chart_widget(chart)
            return

        missing = missing_chart_dependencies()
        fallback = EmptyStateCard(
            self,
            title="Charts unavailable",
            subtitle="Optional chart extras are missing, so the metrics surface falls back to a rich diagnostic state.",
            icon="warning",
            tone="warn",
            badge_text="Unavailable",
        )
        fallback.set_state(
            "Charts unavailable",
            "Optional chart extras are missing, so the metrics surface falls back to a rich diagnostic state.",
            icon="warning",
            tone="warn",
            badge_text="Unavailable",
            points=tuple(f"Missing optional dependency: {name}" for name in missing) + (
                "Install chart extras to unlock the full pyqtgraph glass surface.",
            ),
        )
        self.chart_chip.setText("Fallback mode")
        self._replace_chart_widget(fallback)

    def load_demo_state(self) -> None:
        self.set_metrics_payload(
            {
                "totals": {"sessions": 12, "records": 184, "events": 96, "errors": 7, "tools": 19, "files": 24},
                "daily_activity": [
                    {"day": "2026-04-01", "count": 18},
                    {"day": "2026-04-02", "count": 22},
                    {"day": "2026-04-03", "count": 24},
                    {"day": "2026-04-04", "count": 17},
                    {"day": "2026-04-05", "count": 28},
                    {"day": "2026-04-06", "count": 31},
                ],
                "top_errors": [
                    {"error_type": "ImportError", "count": 3},
                    {"error_type": "TimeoutError", "count": 2},
                    {"error_type": "RuntimeError", "count": 2},
                ],
                "top_tools": [
                    {"tool_name": "pytest", "count": 7},
                    {"tool_name": "pyside6", "count": 5},
                    {"tool_name": "sqlite", "count": 4},
                ],
                "sequence_patterns": [
                    {"pattern": "start > ingest > failure", "count": 2},
                    {"pattern": "repair > ingest > success", "count": 1},
                ],
            }
        )
