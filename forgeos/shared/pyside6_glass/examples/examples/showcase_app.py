from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Any

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QProgressBar,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..assets import CompactToolbar, ControlCard, GlassSegmentedControl, HeroPanel, MiniLegend, ParameterPanel, SearchCommandBar, StatPill, StatusPill
from ..config import GlassTemplateConfig, GlassThemeConfig, GlassTypographyConfig, GlassRegionConfig, GlassTabConfig
from ..controls import create_button
from ..template import GlassPanelTemplate

try:
    import pyqtgraph as pg  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pg = None

try:
    import qtawesome as qta  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    qta = None


_QTA_FALLBACKS: dict[str, str] = {
    "refresh": "fa6s.arrows-rotate",
    "rocket": "fa6s.rocket",
    "play": "fa6s.play",
    "shield": "fa6s.shield-halved",
    "terminal": "fa6s.terminal",
    "chart": "fa6s.chart-line",
    "database": "fa6s.database",
    "network": "fa6s.network-wired",
    "sparkles": "fa6s.wand-magic-sparkles",
    "settings": "fa6s.sliders",
    "workflow": "fa6s.diagram-project",
}


@dataclass(slots=True)
class _Metric:
    label: str
    value: str
    detail: str
    kind: str = "neutral"


class MetricCard(QFrame):
    def __init__(self, metric: _Metric, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("assetRole", "control_card")
        self.setProperty("card", "true")
        self.setObjectName("ShowcaseMetricCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        label = QLabel(metric.label, self)
        label.setProperty("role", "panel_title")
        top.addWidget(label, 1)
        top.addWidget(StatusPill(metric.kind.upper(), kind=metric.kind, parent=self), 0, Qt.AlignRight)
        layout.addLayout(top)

        value = QLabel(metric.value, self)
        value.setProperty("role", "title")
        layout.addWidget(value)

        detail = QLabel(metric.detail, self)
        detail.setProperty("role", "caption")
        detail.setWordWrap(True)
        layout.addWidget(detail)


class CommandConsoleCard(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("card", "true")
        self.setProperty("assetRole", "control_card")
        self.setObjectName("GlassCommandConsoleCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        title_box = QVBoxLayout()
        title_box.setContentsMargins(0, 0, 0, 0)
        title_box.setSpacing(2)
        title = QLabel("Live command stream", self)
        title.setProperty("role", "panel_title")
        title_box.addWidget(title)
        subtitle = QLabel("Synthetic operator feed wired for visual polish, not bash cosplay.", self)
        subtitle.setProperty("role", "panel_subtitle")
        subtitle.setWordWrap(True)
        title_box.addWidget(subtitle)
        header.addLayout(title_box, 1)

        legend = MiniLegend(self)
        legend.add_status("LIVE", "success")
        legend.add_status("GATED", "info")
        legend.add_status("SAFE", "pending")
        header.addWidget(legend, 0, Qt.AlignRight)
        layout.addLayout(header)

        self.console = QPlainTextEdit(self)
        self.console.setReadOnly(True)
        self.console.setObjectName("GlassCommandConsole")
        self.console.setMinimumHeight(280)
        mono = QFont("Cascadia Code")
        mono.setStyleHint(QFont.Monospace)
        mono.setPointSize(10)
        self.console.setFont(mono)
        layout.addWidget(self.console, 1)

        self._lines = [
            "[12:40:18] coordinator :: preset resolved -> compact_operator",
            "[12:40:19] renderer    :: shell.surface = shell / glass / elevated",
            "[12:40:21] telemetry   :: pipeline lag stable at 134ms",
            "[12:40:23] release     :: no regressions detected in current viewport",
            "[12:40:27] workflow    :: incident triage board synced",
            "[12:40:31] services    :: billing=healthy jobs=warning gateway=healthy",
        ]
        self.console.setPlainText("\n".join(self._lines))

        self._pulse_lines = [
            "[12:41:02] runtime     :: visibility policy reapplied for operator role",
            "[12:41:07] visuals     :: blur envelope stepped down for dense mode",
            "[12:41:13] charts      :: telemetry palette refreshed from coordinator snapshot",
            "[12:41:17] data        :: alerts feed probe returned 3 active items",
            "[12:41:22] diagnostics :: adapter handshake stable, 0 broken bindings",
            "[12:41:26] backlog     :: queue drift back inside threshold",
        ]
        self._pulse_index = 0
        self._timer = QTimer(self)
        self._timer.setInterval(1800)
        self._timer.timeout.connect(self._append_pulse)
        self._timer.start()

    def _append_pulse(self) -> None:
        self._lines.append(self._pulse_lines[self._pulse_index % len(self._pulse_lines)])
        self._pulse_index += 1
        self._lines = self._lines[-14:]
        self.console.setPlainText("\n".join(self._lines))
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class TelemetryPlotCard(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("card", "true")
        self.setProperty("assetRole", "control_card")
        self.setObjectName("GlassTelemetryPlotCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        title_box = QVBoxLayout()
        title_box.setContentsMargins(0, 0, 0, 0)
        title_box.setSpacing(2)
        title = QLabel("Live telemetry", self)
        title.setProperty("role", "panel_title")
        title_box.addWidget(title)
        subtitle = QLabel("Uses pyqtgraph when available, otherwise degrades gracefully.", self)
        subtitle.setProperty("role", "panel_subtitle")
        title_box.addWidget(subtitle)
        header.addLayout(title_box, 1)
        self.status = StatusPill("PYQTGRAPH" if pg is not None else "FALLBACK", kind="info", parent=self)
        header.addWidget(self.status, 0, Qt.AlignRight)
        layout.addLayout(header)

        self._phase = 0.0
        self._data = [0.58 + (math.sin(i / 3.8) * 0.16) for i in range(28)]

        if pg is None:
            fallback = QLabel(
                "pyqtgraph no esta instalado aqui, pero en tu maquina si esta.\n"
                "El card queda listo para dibujar la grafica apenas extraigas los archivos.",
                self,
            )
            fallback.setProperty("role", "caption")
            fallback.setWordWrap(True)
            fallback.setMinimumHeight(200)
            fallback.setAlignment(Qt.AlignCenter)
            layout.addWidget(fallback, 1)
            self._timer = None
            return

        plot = pg.PlotWidget(self)
        plot.setBackground((0, 0, 0, 0))
        plot.showGrid(x=True, y=True, alpha=0.10)
        plot.hideButtons()
        plot.setMouseEnabled(x=False, y=False)
        plot.setMenuEnabled(False)
        plot.getPlotItem().hideAxis("bottom")
        plot.getPlotItem().hideAxis("left")
        plot.setYRange(0.12, 1.05)
        plot.setMinimumHeight(220)

        pen = pg.mkPen(color=(236, 240, 245, 220), width=2)
        brush = pg.mkBrush(120, 196, 255, 40)
        self._curve = plot.plot(self._data, pen=pen)
        self._fill = pg.FillBetweenItem(self._curve, pg.PlotCurveItem([0.22] * len(self._data), pen=None), brush=brush)
        plot.addItem(self._fill)
        layout.addWidget(plot, 1)

        self._timer = QTimer(self)
        self._timer.setInterval(1200)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self) -> None:
        if pg is None:
            return
        self._phase += 0.35
        tail = 0.58 + (math.sin(self._phase) * 0.18) + random.uniform(-0.025, 0.025)
        self._data.append(max(0.18, min(0.96, tail)))
        self._data = self._data[-28:]
        self._curve.setData(self._data)


class ServiceRailCard(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("assetRole", "control_card")
        self.setProperty("card", "true")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        title = QLabel("Service rail", self)
        title.setProperty("role", "panel_title")
        layout.addWidget(title)

        items = [
            ("API Gateway", "stable", "success"),
            ("Jobs / Workers", "drift detected", "warning"),
            ("Billing", "healthy", "success"),
            ("Release gate", "armed", "info"),
            ("Catalog registry", "ready", "pending"),
        ]
        for name, detail, kind in items:
            row = QFrame(self)
            row.setProperty("card", "muted")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 8, 10, 8)
            row_layout.setSpacing(8)
            text_box = QVBoxLayout()
            text_box.setContentsMargins(0, 0, 0, 0)
            text_box.setSpacing(2)
            label = QLabel(name, row)
            label.setProperty("role", "label")
            text_box.addWidget(label)
            subtitle = QLabel(detail, row)
            subtitle.setProperty("role", "caption")
            text_box.addWidget(subtitle)
            row_layout.addLayout(text_box, 1)
            row_layout.addWidget(StatusPill(kind.upper(), kind=kind, parent=row), 0, Qt.AlignRight)
            layout.addWidget(row)
        layout.addStretch(1)


class ActivityFeedCard(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("assetRole", "control_card")
        self.setProperty("card", "true")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        title = QLabel("Operator queue", self)
        title.setProperty("role", "panel_title")
        layout.addWidget(title)

        self.listing = QListWidget(self)
        self.listing.setObjectName("GlassActivityFeed")
        self.listing.setMinimumHeight(180)
        for text in (
            "Resolve stale dashboard snapshot in review workspace",
            "Promote compact_operator preset to nightly smoke",
            "Refresh icon pack aliases before release proof",
            "Inspect metrics drift on jobs pipeline",
            "Snapshot current theme overrides for golden session",
        ):
            item = QListWidgetItem(text)
            self.listing.addItem(item)
        layout.addWidget(self.listing, 1)


class OrchestrationSummaryCard(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("assetRole", "control_card")
        self.setProperty("card", "true")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        title = QLabel("System path", self)
        title.setProperty("role", "panel_title")
        layout.addWidget(title)

        summary = QTextEdit(self)
        summary.setReadOnly(True)
        summary.setMinimumHeight(160)
        summary.setPlainText(
            "runtime context\n"
            "  -> visual intelligence\n"
            "  -> appearance coordinator\n"
            "  -> profiles / effects\n"
            "  -> token resolution\n"
            "  -> runtime + template + renderer\n"
            "  -> governed final UI\n\n"
            "This showcase leans into the actual system story instead of pretending to be a random sci-fi dashboard."
        )
        layout.addWidget(summary, 1)


class MetricsBoard(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        metrics_grid = QWidget(self)
        grid = QGridLayout(metrics_grid)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        for index, metric in enumerate(
            (
                _Metric("Release confidence", "98.4%", "Smoke, proof and semantic checks aligned.", "success"),
                _Metric("Active incidents", "03", "One warning-grade cluster, zero red regressions.", "warning"),
                _Metric("Queue pressure", "27", "Operator queue stable with low retry churn.", "info"),
                _Metric("Visual debt", "12", "Known polish backlog, not structural failure.", "pending"),
            )
        ):
            grid.addWidget(MetricCard(metric, metrics_grid), index // 2, index % 2)
        layout.addWidget(metrics_grid)

        table_card = QFrame(self)
        table_card.setProperty("assetRole", "control_card")
        table_card.setProperty("card", "true")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(14, 12, 14, 12)
        table_layout.setSpacing(8)

        table_title = QLabel("Service health matrix", table_card)
        table_title.setProperty("role", "panel_title")
        table_layout.addWidget(table_title)

        table = QTableWidget(5, 4, table_card)
        table.setHorizontalHeaderLabels(("Service", "State", "Latency", "Notes"))
        rows = (
            ("gateway", "healthy", "84ms", "Traffic normal"),
            ("jobs", "warning", "211ms", "Backpressure visible"),
            ("billing", "healthy", "96ms", "No drift"),
            ("catalog", "healthy", "38ms", "Registry ready"),
            ("release_gate", "armed", "n/a", "Awaiting proof run"),
        )
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                table.setItem(row_index, column_index, QTableWidgetItem(str(value)))
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(False)
        table_layout.addWidget(table, 1)
        layout.addWidget(table_card, 1)


class RunbookBoard(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        card = QFrame(self)
        card.setProperty("assetRole", "control_card")
        card.setProperty("card", "true")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(8)
        title = QLabel("Polish runbook", card)
        title.setProperty("role", "panel_title")
        card_layout.addWidget(title)
        notes = QTextEdit(card)
        notes.setReadOnly(True)
        notes.setPlainText(
            "1. tighten packaging\n"
            "2. keep release gate portable\n"
            "3. split template responsibilities\n"
            "4. keep examples aspirational but grounded\n"
            "5. show the orchestrator story on screen\n"
        )
        card_layout.addWidget(notes, 1)
        layout.addWidget(card, 1)

        progress_card = QFrame(self)
        progress_card.setProperty("assetRole", "control_card")
        progress_card.setProperty("card", "true")
        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setContentsMargins(14, 12, 14, 12)
        progress_layout.setSpacing(10)
        progress_title = QLabel("Release gate readiness", progress_card)
        progress_title.setProperty("role", "panel_title")
        progress_layout.addWidget(progress_title)
        for text, value in (("Contracts", 96), ("Visual proof", 78), ("Examples", 82), ("Docs", 91)):
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(8)
            label = QLabel(text, progress_card)
            label.setProperty("role", "label")
            bar = QProgressBar(progress_card)
            bar.setRange(0, 100)
            bar.setValue(value)
            row.addWidget(label, 0)
            row.addWidget(bar, 1)
            progress_layout.addLayout(row)
        layout.addWidget(progress_card)


def _set_qta_icon(button: Any, icon_key: str, *, color: str = "#eef3f9") -> None:
    if qta is None:
        return
    icon_name = _QTA_FALLBACKS.get(icon_key, icon_key)
    try:
        button.setIcon(qta.icon(icon_name, color=color))
    except Exception:
        return


def _showcase_overrides() -> str:
    return """
QFrame#WindowChrome {
    min-height: 36px;
    max-height: 36px;
    border-radius: 12px;
    border: 1px solid rgba(231, 238, 246, 0.10);
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.06),
        stop:1 rgba(160, 177, 200, 0.03));
}
QFrame#Shell {
    border: 1px solid rgba(236, 242, 248, 0.20);
}
QFrame#ShowcaseMetricCard:hover,
QFrame#GlassCommandConsoleCard:hover,
QFrame#GlassTelemetryPlotCard:hover {
    border: 1px solid rgba(244, 248, 252, 0.24);
}
QPlainTextEdit#GlassCommandConsole {
    background: rgba(12, 16, 22, 0.80);
    border: 1px solid rgba(239, 244, 248, 0.12);
    border-radius: 18px;
    selection-background-color: rgba(180, 206, 236, 0.26);
    padding: 10px 12px;
}
QListWidget#GlassActivityFeed {
    border-radius: 16px;
    padding: 6px;
}
QListWidget#GlassActivityFeed::item {
    padding: 10px 10px;
    margin: 2px 0px;
    border-radius: 12px;
    border: 1px solid rgba(245, 248, 252, 0.06);
    background: rgba(255, 255, 255, 0.03);
}
QListWidget#GlassActivityFeed::item:selected {
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(245, 248, 252, 0.16);
}
"""


def build_command_center_example(parent: QWidget | None = None) -> GlassPanelTemplate:
    config = GlassTemplateConfig(
        title="ForgeOS Command Center",
        subtitle="A premium operator shell that actually tells the orchestrator story.",
        eyebrow="LIVE CONTROL ROOM",
        theme=GlassThemeConfig(
            density="compact",
            experience_mode="operator",
            typography=GlassTypographyConfig(scale="lg"),
        ),
        regions=GlassRegionConfig(show_side=True, show_footer=True, show_status=True, main_side_sizes=(900, 360)),
        tabs=GlassTabConfig(
            enabled=True,
            movable=True,
            closable=False,
            pinnable=True,
            default_tab_id="overview",
            default_tab_title="Overview",
            density="compact",
        ),
    )
    template = GlassPanelTemplate(
        parent,
        config=config,
        theme_id="silver_frost_cyan",
        density="compact",
        typography_scale="lg",
    )
    template.setStyleSheet(f"{template.styleSheet()}\n{_showcase_overrides()}")

    hero = HeroPanel(
        "PySide6 Glass operator console",
        subtitle=(
            "Uses the real shell, tabs, cards, status lanes, and optional local libs like pyqtgraph / QtAwesome "
            "to make the example feel flagship instead of tutorial leftovers."
        ),
        eyebrow="SHOWCASE",
        parent=template,
    )
    template.slots.hero_slot.addWidget(hero)

    hero_row = QWidget(template)
    hero_layout = QHBoxLayout(hero_row)
    hero_layout.setContentsMargins(0, 0, 0, 0)
    hero_layout.setSpacing(8)
    for label, value, trend in (
        ("Throughput", "92/s", "+6%"),
        ("Latency", "134 ms", "-12 ms"),
        ("Alerts", "3", "triage"),
        ("Gate", "armed", "proof"),
    ):
        hero_layout.addWidget(StatPill(label, value, trend=trend, parent=hero_row), 1)
    template.slots.hero_slot.addWidget(hero_row)

    tools = CompactToolbar("Workspace actions", parent=template)
    connect_button = tools.add_action("Reconnect", icon_name="refresh-cw", variant="secondary")
    deploy_button = tools.add_action("Promote", icon_name="sparkles", variant="primary")
    gate_button = tools.add_action("Run Gate", icon_name="shield", variant="ghost")
    tools.add_icon_action(icon_name="settings", tooltip="Workspace settings")
    _set_qta_icon(connect_button, "refresh")
    _set_qta_icon(deploy_button, "rocket")
    _set_qta_icon(gate_button, "shield")

    search = SearchCommandBar(placeholder="Search entries, services, or commands", parent=template)
    mode_switch = GlassSegmentedControl(
        (("ops", "Ops"), ("metrics", "Metrics"), ("proof", "Proof")),
        selected="ops",
        parent=template,
    )

    tool_row = QWidget(template)
    tool_row_layout = QHBoxLayout(tool_row)
    tool_row_layout.setContentsMargins(0, 0, 0, 0)
    tool_row_layout.setSpacing(8)
    tool_row_layout.addWidget(search, 1)
    tool_row_layout.addWidget(mode_switch, 0)

    template.slots.main_slot.addWidget(tools)
    template.slots.main_slot.addWidget(tool_row)

    content_split = QSplitter(Qt.Horizontal, template)
    content_split.setChildrenCollapsible(False)
    content_split.setHandleWidth(8)
    console_card = CommandConsoleCard(content_split)

    right_stack = QWidget(content_split)
    right_layout = QVBoxLayout(right_stack)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(10)
    plot_card = TelemetryPlotCard(right_stack)
    feed_card = ActivityFeedCard(right_stack)
    right_layout.addWidget(plot_card, 1)
    right_layout.addWidget(feed_card, 1)

    content_split.addWidget(console_card)
    content_split.addWidget(right_stack)
    content_split.setSizes([640, 340])
    template.slots.main_slot.addWidget(content_split, 1)

    parameter_panel = ParameterPanel("Visual envelope", parent=template)
    blur_slider = parameter_panel.add_slider("Blur budget", minimum=0, maximum=100, value=64)
    glow_slider = parameter_panel.add_slider("Glow restraint", minimum=0, maximum=100, value=36)
    parameter_panel.add_toggle("Motion policy", checked=True)
    parameter_panel.add_toggle("Dense ops mode", checked=True)
    template.slots.side_slot.addWidget(parameter_panel)
    template.slots.side_slot.addWidget(ServiceRailCard(template), 1)
    template.slots.side_slot.addWidget(OrchestrationSummaryCard(template))

    metrics_tab = MetricsBoard(template)
    runbook_tab = RunbookBoard(template)
    template.add_workspace_tab(tab_id="metrics", title="Metrics", widget=metrics_tab, icon_name="activity")
    template.add_workspace_tab(tab_id="runbooks", title="Runbooks", widget=runbook_tab, icon_name="file-text")

    def _emit_status(text: str) -> None:
        template.set_status_text(text)
        console_card.console.appendPlainText(text)

    connect_button.clicked.connect(lambda: _emit_status("[ui] reconnect requested -> simulated adapter handshake complete"))
    deploy_button.clicked.connect(lambda: _emit_status("[ui] promote requested -> release candidate staged"))
    gate_button.clicked.connect(lambda: _emit_status("[ui] release gate requested -> smoke/proof queued"))
    blur_slider.value_changed.connect(lambda value: template.set_status_text(f"Blur budget -> {value}"))
    glow_slider.value_changed.connect(lambda value: template.set_status_text(f"Glow restraint -> {value}"))
    mode_switch.value_changed.connect(lambda value: template.set_status_text(f"Workspace mode switched -> {value}"))
    search.search_changed.connect(lambda text: template.set_status_text(f"Search filter -> {text or 'all'}"))

    template.add_footer_action("Open Metrics", "secondary", align="left", icon_name="activity", on_click=lambda: template.set_active_workspace_tab("metrics"))
    template.add_footer_action("Runbooks", "ghost", align="left", icon_name="file-text", on_click=lambda: template.set_active_workspace_tab("runbooks"))
    template.add_footer_action("Snapshot", "secondary", icon_name="download", on_click=lambda: _emit_status("[ui] workspace snapshot exported to tools/_local (simulated)"))
    template.add_footer_action("Focus Ops", "primary", icon_name="terminal", on_click=lambda: template.set_active_workspace_tab("overview"))
    template.set_status_text("Command center ready. pyqtgraph={} qtawesome={}".format("on" if pg is not None else "off", "on" if qta is not None else "off"))
    return template
