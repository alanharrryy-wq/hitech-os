
from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from visuals.controls.chips import create_chip
from visuals.effects.shadow import apply_shadow
from visuals.widgets.charts import build_chart_card, chart_ui_available, missing_chart_dependencies

from ..adapters import build_metrics_view_model
from ..widgets.empty_state import EmptyStateCard
from ..widgets.kpi_strip import KPIStrip
from ..widgets.log_console import LogConsole


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
        self.notes_console = LogConsole(self, title="Operational notes")

        lower.addWidget(self._wrap_list("Top Errors", self.top_errors), 0, 0)
        lower.addWidget(self._wrap_list("Top Tools", self.top_tools), 0, 1)
        lower.addWidget(self._wrap_list("Sequence Patterns", self.sequence_patterns), 1, 0)
        lower.addWidget(self.notes_console, 1, 1)

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

    def set_busy_state(self, message: str) -> None:
        self.state_chip.setText("Busy")
        self.chart_chip.setText("Hydrating")
        self.subtitle_label.setText(message)
        self.notes_console.set_lines([message])

    def set_metrics_payload(self, payload: dict[str, Any]) -> None:
        view_model = dict(payload or {})
        if "chart" not in view_model or "kpis" not in view_model:
            view_model = build_metrics_view_model(view_model)
        self._payload = view_model

        self.kpis.set_metrics(list(view_model.get("kpis") or []))
        self._set_list(self.top_errors, list(view_model.get("top_errors") or []), key="error_type", secondary="count")
        self._set_list(self.top_tools, list(view_model.get("top_tools") or []), key="tool_name", secondary="count")
        self._set_list(self.sequence_patterns, list(view_model.get("sequence_patterns") or []), key="pattern", secondary="count")
        self.notes_console.set_lines(list(view_model.get("notes") or []))

        chart_model = dict(view_model.get("chart") or {})
        status = dict(view_model.get("status") or {})
        self.title_label.setText("Metrics Surface")
        self.subtitle_label.setText(str(chart_model.get("subtitle") or "Telemetry view model ready."))
        self.state_chip.setText(str(status.get("label") or "Live"))
        self.state_chip.setProperty("tone", str(status.get("tone") or "good"))

        if chart_ui_available():
            chart = build_chart_card(
                title=str(chart_model.get("title") or "Runtime Overview"),
                subtitle=str(chart_model.get("subtitle") or "Telemetry trend surface."),
                experience_mode="dashboard",
                visual_level="showcase",
                data_state=str(chart_model.get("data_state") or "ready"),
                series=tuple(chart_model.get("series") or ()),
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
        self.set_metrics_payload(build_metrics_view_model({}))
