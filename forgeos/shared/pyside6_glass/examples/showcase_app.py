from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..config import GlassRegionConfig, GlassTemplateConfig, GlassThemeConfig, GlassTypographyConfig, GlassTabConfig
from ..template import GlassPanelTemplate

try:
    import qtawesome as qta  # type: ignore
except Exception:  # pragma: no cover
    qta = None


_QTA_NAMES: dict[str, str] = {
    "home": "fa6s.house",
    "clock": "fa6s.clock",
    "diamond": "fa6s.gem",
    "power": "fa6s.power-off",
    "terminal": "fa6s.terminal",
    "camera": "fa6s.camera",
    "hammer": "fa6s.gavel",
}


@dataclass(slots=True)
class MetricSpec:
    title: str
    value: str
    detail: str
    badge: str = ""
    badge_kind: str = "neutral"


class RailButton(QToolButton):
    def __init__(self, icon_key: str, tooltip: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DeckRailButton")
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(tooltip)
        self.setText("•")
        self.setAutoRaise(True)
        if qta is not None:
            icon_name = _QTA_NAMES.get(icon_key)
            if icon_name:
                try:
                    self.setIcon(qta.icon(icon_name, color="#d9e3ef"))
                except Exception:
                    pass


class ToneBadge(QLabel):
    def __init__(self, text: str, kind: str = "neutral", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setObjectName("ToneBadge")
        self.setProperty("tone", kind)
        self.setAlignment(Qt.AlignCenter)


class MetricCell(QWidget):
    def __init__(self, spec: MetricSpec, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("MetricCell")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(8)

        title = QLabel(spec.title, self)
        title.setObjectName("MetricTitle")
        title_row.addWidget(title, 1)
        if spec.badge:
            title_row.addWidget(ToneBadge(spec.badge, spec.badge_kind, self), 0, Qt.AlignRight)
        layout.addLayout(title_row)

        value = QLabel(spec.value, self)
        value.setObjectName("MetricValue")
        layout.addWidget(value)

        detail = QLabel(spec.detail, self)
        detail.setObjectName("MetricDetail")
        detail.setWordWrap(True)
        layout.addWidget(detail)
        layout.addStretch(1)


class MetricsMatrix(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("MetricsMatrix")
        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)

        metrics = (
            MetricSpec("Relax component", "98.4%", "Smooth pivot and semantic checks aligned."),
            MetricSpec("Active incidents", "03", "Operator status codes tell the story cleanly.", "WARNING", "warning"),
            MetricSpec("GIS pressure", "27", "Operator status codes tell the story cleanly.", "SUCCESS", "success"),
            MetricSpec("Vulner debt", "12", "Known partial backlogs and structural failures.", "PENDING", "pending"),
        )
        for index, spec in enumerate(metrics):
            cell = MetricCell(spec, self)
            if index % 2 == 0:
                cell.setProperty("vcut", True)
            if index < 2:
                cell.setProperty("hcut", True)
            cell.style().unpolish(cell)
            cell.style().polish(cell)
            grid.addWidget(cell, index // 2, index % 2)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(216, 224, 234, 34), 1)
        painter.setPen(pen)
        mid_x = self.width() / 2
        mid_y = self.height() / 2
        painter.drawLine(int(mid_x), 0, int(mid_x), self.height())
        painter.drawLine(0, int(mid_y), self.width(), int(mid_y))


class StreamTable(QTableWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(5, 4, parent)
        self.setObjectName("DeckStreamTable")
        self.setHorizontalHeaderLabels(("Service", "State", "Latency", "Notes"))
        rows = (
            ("joyce", "SAFE", "81ms", "Blazing deployment"),
            ("joerynn", "SAFE", "81ms", "Running smooth"),
            ("living", "WARNING", "58ms", "Blazing deployment"),
            ("creatily", "SUCCESS", "49ms", "Running timing"),
            ("restore_panel", "N/A", "n/a", "Issue pending"),
        )
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                if column_index == 1:
                    item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row_index, column_index, item)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setMinimumSectionSize(72)
        self.setAlternatingRowColors(False)
        self.setSelectionMode(self.SelectionMode.NoSelection)
        self.setEditTriggers(self.EditTrigger.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setShowGrid(True)
        self.setMinimumHeight(250)


class DeckSurface(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CommandDeckSurface")
        self.setAttribute(Qt.WA_StyledBackground, True)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(14)

        rail = QFrame(self)
        rail.setObjectName("DeckRail")
        rail.setFixedWidth(46)
        rail_layout = QVBoxLayout(rail)
        rail_layout.setContentsMargins(0, 82, 0, 18)
        rail_layout.setSpacing(14)
        for icon_key, tooltip in (
            ("home", "Overview"),
            ("clock", "Recent"),
            ("diamond", "Quality"),
            ("power", "Gate"),
        ):
            rail_layout.addWidget(RailButton(icon_key, tooltip, rail), 0, Qt.AlignCenter)
        rail_layout.addStretch(1)
        outer.addWidget(rail)

        content = QWidget(self)
        content.setObjectName("DeckContent")
        outer.addWidget(content, 1)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget(content)
        header.setObjectName("DeckHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(22, 18, 22, 16)
        header_layout.setSpacing(8)

        eyebrow = QLabel("WORKSPACE", header)
        eyebrow.setObjectName("DeckEyebrow")
        header_layout.addWidget(eyebrow)

        title = QLabel("ForgeOS Command Center", header)
        title.setObjectName("DeckTitle")
        header_layout.addWidget(title)

        subtitle = QLabel("code-atlas operator console", header)
        subtitle.setObjectName("DeckSubtitle")
        header_layout.addWidget(subtitle)

        body = QLabel(
            "A premium operator suite that actually tells the orchestrator story. "
            "The visual quick stats, cams, and advanced tools for the ecosystem.",
            header,
        )
        body.setObjectName("DeckBody")
        body.setWordWrap(True)
        header_layout.addWidget(body)

        strip = QHBoxLayout()
        strip.setContentsMargins(0, 10, 0, 0)
        strip.setSpacing(10)
        strip.addWidget(self._meta_token("Throughput"), 0)
        strip.addWidget(self._meta_token("86/s"), 0)
        strip.addWidget(self._meta_token("Latency"), 0)
        strip.addStretch(1)
        header_layout.addLayout(strip)
        layout.addWidget(header)

        divider_1 = self._divider(content)
        layout.addWidget(divider_1)

        metrics = MetricsMatrix(content)
        layout.addWidget(metrics)

        divider_2 = self._divider(content)
        layout.addWidget(divider_2)

        stream = QWidget(content)
        stream_layout = QVBoxLayout(stream)
        stream_layout.setContentsMargins(22, 18, 22, 18)
        stream_layout.setSpacing(12)
        stream_title = QLabel("LIVE COMMAND STREAM", stream)
        stream_title.setObjectName("SectionTitle")
        stream_layout.addWidget(stream_title)
        stream_layout.addWidget(StreamTable(stream), 1)
        layout.addWidget(stream, 1)

        footer_divider = self._divider(content)
        layout.addWidget(footer_divider)

        footer = QWidget(content)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(22, 14, 22, 14)
        footer_layout.setSpacing(10)
        footer_layout.addWidget(self._action_button("Notebook", quiet=True), 0)
        footer_layout.addWidget(self._action_button("Apps Metrics", quiet=True), 0)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self._action_button("Snapshot", icon_key="camera"), 0)
        footer_layout.addWidget(self._action_button("Force Ops", icon_key="hammer", accent=True), 0)
        layout.addWidget(footer)

    def _meta_token(self, text: str) -> QLabel:
        label = QLabel(text, self)
        label.setObjectName("MetaToken")
        return label

    def _divider(self, parent: QWidget) -> QWidget:
        line = QWidget(parent)
        line.setObjectName("DeckDivider")
        line.setFixedHeight(1)
        return line

    def _action_button(self, text: str, *, icon_key: str | None = None, quiet: bool = False, accent: bool = False) -> QPushButton:
        button = QPushButton(text, self)
        button.setObjectName("DeckActionButton")
        if quiet:
            button.setProperty("quiet", True)
        if accent:
            button.setProperty("accent", True)
        button.setCursor(Qt.PointingHandCursor)
        if qta is not None and icon_key:
            icon_name = _QTA_NAMES.get(icon_key)
            if icon_name:
                try:
                    button.setIcon(qta.icon(icon_name, color="#dfe8f1" if not accent else "#f2e7da"))
                except Exception:
                    pass
        button.style().unpolish(button)
        button.style().polish(button)
        return button

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)

        path = QPainterPath()
        path.addRoundedRect(rect, 24, 24)
        painter.setClipPath(path)

        base = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        base.setColorAt(0.0, QColor(20, 24, 31, 244))
        base.setColorAt(0.45, QColor(14, 18, 24, 248))
        base.setColorAt(1.0, QColor(10, 12, 17, 250))
        painter.fillPath(path, base)

        top_glow = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.top() + 160)
        top_glow.setColorAt(0.0, QColor(232, 239, 245, 42))
        top_glow.setColorAt(0.32, QColor(180, 192, 206, 18))
        top_glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(rect, top_glow)

        for y in range(rect.top(), rect.bottom(), 4):
            alpha = 7 if y % 16 == 0 else 4
            painter.setPen(QPen(QColor(255, 255, 255, alpha), 1))
            painter.drawLine(rect.left(), y, rect.right(), y)

        painter.setClipping(False)
        painter.setPen(QPen(QColor(222, 230, 238, 52), 1.2))
        painter.drawRoundedRect(rect, 24, 24)
        painter.setPen(QPen(QColor(240, 246, 252, 24), 1))
        painter.drawLine(rect.left() + 18, rect.top() + 18, rect.right() - 18, rect.top() + 18)
        super().paintEvent(event)



def _showcase_overrides() -> str:
    return """
QFrame#WindowChrome {
    min-height: 34px;
    max-height: 34px;
    border-radius: 10px;
    border: 1px solid rgba(230, 236, 242, 0.10);
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.04),
        stop:1 rgba(160, 171, 183, 0.02));
}
QFrame#Shell {
    background: rgba(8, 10, 14, 0.36);
    border: 1px solid rgba(228, 235, 242, 0.16);
    border-radius: 30px;
}
QFrame#Shell:hover {
    border: 1px solid rgba(236, 241, 246, 0.18);
}
QWidget#DeckContent,
QWidget#DeckHeader,
QWidget#DeckDivider,
QWidget#MetricCell,
QWidget#MetricsMatrix,
QWidget#DeckStreamSection,
QTableWidget#DeckStreamTable,
QWidget#DeckFooter,
QLabel,
QPushButton,
QToolButton {
    background: transparent;
}
QFrame#DeckRail {
    border-right: 1px solid rgba(226, 233, 240, 0.07);
}
QToolButton#DeckRailButton {
    min-width: 28px;
    max-width: 28px;
    min-height: 28px;
    max-height: 28px;
    border: none;
    color: #dce5ef;
}
QToolButton#DeckRailButton:hover {
    color: #ffffff;
}
QLabel#DeckEyebrow {
    color: #80a4c7;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
}
QLabel#DeckTitle {
    color: #eef3f8;
    font-size: 28px;
    font-weight: 760;
}
QLabel#DeckSubtitle {
    color: #e2e7ee;
    font-size: 17px;
    font-weight: 520;
}
QLabel#DeckBody {
    color: rgba(224, 230, 237, 0.78);
    font-size: 13px;
    line-height: 1.4em;
}
QLabel#MetaToken {
    color: rgba(222, 230, 237, 0.82);
    font-size: 12px;
    padding: 2px 8px 2px 0px;
}
QWidget#DeckDivider {
    background: rgba(230, 236, 242, 0.10);
}
QLabel#MetricTitle {
    color: #c8d3de;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}
QLabel#MetricValue {
    color: #edf3f7;
    font-size: 28px;
    font-weight: 760;
}
QLabel#MetricDetail {
    color: rgba(225, 231, 238, 0.78);
    font-size: 13px;
}
QLabel#ToneBadge {
    min-height: 26px;
    max-height: 26px;
    padding: 0px 12px;
    border-radius: 13px;
    font-size: 11px;
    font-weight: 760;
    letter-spacing: 1px;
}
QLabel#ToneBadge[tone="warning"] {
    color: #f4c07c;
    background: rgba(128, 83, 32, 0.16);
    border: 1px solid rgba(244, 192, 124, 0.18);
}
QLabel#ToneBadge[tone="success"] {
    color: #d8e0b2;
    background: rgba(88, 95, 44, 0.18);
    border: 1px solid rgba(216, 224, 178, 0.18);
}
QLabel#ToneBadge[tone="pending"] {
    color: #efb173;
    background: rgba(122, 71, 24, 0.16);
    border: 1px solid rgba(239, 177, 115, 0.18);
}
QLabel#SectionTitle {
    color: #dfe7ef;
    font-size: 13px;
    font-weight: 760;
    letter-spacing: 2px;
}
QTableWidget#DeckStreamTable {
    color: #ecf1f6;
    gridline-color: rgba(225, 232, 239, 0.08);
    border: none;
    outline: none;
    font-size: 12px;
    selection-background-color: transparent;
    alternate-background-color: transparent;
}
QTableWidget#DeckStreamTable::item {
    padding: 7px 10px;
    border: none;
}
QHeaderView::section {
    background: transparent;
    color: #dbe4ec;
    border: none;
    border-bottom: 1px solid rgba(225, 232, 239, 0.12);
    padding: 8px 10px;
    font-size: 12px;
    font-weight: 700;
}
QPushButton#DeckActionButton {
    min-height: 34px;
    padding: 0px 16px;
    border-radius: 10px;
    color: #e7eef5;
    border: 1px solid rgba(228, 235, 242, 0.12);
    background: rgba(255, 255, 255, 0.03);
}
QPushButton#DeckActionButton[quiet="true"] {
    color: #cfd8e2;
    background: rgba(255, 255, 255, 0.02);
}
QPushButton#DeckActionButton[accent="true"] {
    color: #f3e8db;
    border: 1px solid rgba(237, 190, 135, 0.16);
    background: rgba(118, 70, 22, 0.12);
}
QPushButton#DeckActionButton:hover {
    border: 1px solid rgba(236, 242, 247, 0.22);
    background: rgba(255, 255, 255, 0.05);
}
QPushButton#DeckActionButton[accent="true"]:hover {
    border: 1px solid rgba(237, 190, 135, 0.24);
    background: rgba(118, 70, 22, 0.16);
}
QPlainTextEdit,
QTextEdit {
    background: transparent;
    border: none;
}
"""



def build_command_center_example(parent: QWidget | None = None) -> GlassPanelTemplate:
    config = GlassTemplateConfig(
        title="ForgeOS Command Center",
        subtitle="Professional operator workspace",
        eyebrow="WORKSPACE",
        theme=GlassThemeConfig(
            theme_id="obsidian_ice",
            density="compact",
            experience_mode="operator",
            typography=GlassTypographyConfig(scale="lg"),
        ),
        regions=GlassRegionConfig(show_side=False, show_footer=False, show_status=False),
        tabs=GlassTabConfig(enabled=False, density="compact"),
    )
    template = GlassPanelTemplate(
        parent,
        config=config,
        theme_id="obsidian_ice",
        density="compact",
        typography_scale="lg",
    )
    template.setStyleSheet(f"{template.styleSheet()}\n{_showcase_overrides()}")
    surface = DeckSurface(template)
    template.slots.main_slot.addWidget(surface, 1)
    template.set_status_text("Command center ready")
    return template
