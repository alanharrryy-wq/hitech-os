from __future__ import annotations

"""Deterministic graph radar consumer for Aegis Deck.

This module intentionally stays inside the frozen radar contract. It consumes
canonical graph snapshot semantics, keeps compatibility aliases internal, and
never invents upstream graph data.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QFontMetrics, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QFrame, QLabel, QSizePolicy, QVBoxLayout, QWidget

__all__ = ["AegisGraphRadar"]

_DEFAULT_STATUS = "Radar has no data"
_DEFAULT_SUBTITLE = "Awaiting canonical snapshot"
_GOLDEN_ANGLE = 2.399963229728653

_CANONICAL_SNAPSHOT_NODE_KEYS = ("nodes",)
_CANONICAL_SNAPSHOT_EDGE_KEYS = ("edges",)
_CANONICAL_SNAPSHOT_FOCUS_KEYS = ("focus_node_id",)

_COMPAT_SNAPSHOT_NODE_KEYS = ("graph_nodes", "radar_nodes")
_COMPAT_SNAPSHOT_EDGE_KEYS = ("graph_edges", "radar_edges")
_COMPAT_SNAPSHOT_FOCUS_KEYS = ("focus_node", "focused_node_id")

_NODE_ID_KEYS = ("id", "node_id")
_NODE_LABEL_KEYS = ("label", "title")
_EDGE_SOURCE_KEYS = ("source", "from", "src")
_EDGE_TARGET_KEYS = ("target", "to", "dst")
_HOTSPOT_ID_KEYS = ("id",)
_HOTSPOT_LABEL_KEYS = ("label", "title")


@dataclass(frozen=True)
class _ThemeTokens:
    bg: str = "#0b1016"
    panel: str = "#18212d"
    panel_alt: str = "#1f2a37"
    border: str = "#2b3748"
    border_soft: str = "#223040"
    border_strong: str = "#4d6480"
    text: str = "#edf3fb"
    text_muted: str = "#94a5ba"
    accent: str = "#8dc1ff"
    accent_glow: str = "#8dc1ff2e"
    success: str = "#57c68d"
    warning: str = "#d8b15f"
    danger: str = "#dc7f87"
    selection: str = "#263b57"
    focus_ring: str = "#8dc1ff66"
    shadow: str = "#000000aa"


@dataclass(frozen=True)
class _RadarNode:
    node_id: str
    label: str
    x: float
    y: float
    has_explicit_position: bool
    weight: float = 1.0
    severity: str = "neutral"
    active: bool = False
    meta: dict[str, Any] = field(default_factory=dict)
    order: int = 0


@dataclass(frozen=True)
class _RadarEdge:
    source: str
    target: str
    weight: float = 1.0
    active: bool = False
    kind: str = ""
    order: int = 0


@dataclass(frozen=True)
class _RadarHotspot:
    hotspot_id: str
    label: str
    severity: str = "neutral"
    active: bool = False
    meta: dict[str, Any] = field(default_factory=dict)
    order: int = 0


@dataclass(frozen=True)
class _HoverTarget:
    kind: str
    item_id: str
    title: str
    subtitle: str
    severity: str = "neutral"


class _RadarCanvas(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tokens = _ThemeTokens()
        self._nodes: list[_RadarNode] = []
        self._edges: list[_RadarEdge] = []
        self._hotspots: list[_RadarHotspot] = []
        self._focus_node_id = ""
        self._status_text = _DEFAULT_STATUS
        self._subtitle = _DEFAULT_SUBTITLE
        self._sparse_note = ""
        self._fallback_count = 0
        self._phase = 0.0
        self._animation_enabled = True
        self._hover_target: _HoverTarget | None = None

        self._timer = QTimer(self)
        self._timer.setInterval(33)
        self._timer.timeout.connect(self._advance_phase)
        self._timer.start()

        self.setMinimumSize(340, 250)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.setMouseTracking(True)

    def sizeHint(self) -> QSize:  # type: ignore[override]
        return QSize(500, 360)

    def set_model(
        self,
        *,
        nodes: list[_RadarNode],
        edges: list[_RadarEdge],
        hotspots: list[_RadarHotspot],
        focus_node_id: str,
        status_text: str,
        subtitle: str,
        sparse_note: str,
        fallback_count: int,
    ) -> None:
        self._nodes = list(nodes)
        self._edges = list(edges)
        self._hotspots = list(hotspots)
        self._focus_node_id = str(focus_node_id or "")
        self._status_text = str(status_text or _DEFAULT_STATUS)
        self._subtitle = str(subtitle or _DEFAULT_SUBTITLE)
        self._sparse_note = str(sparse_note or "")
        self._fallback_count = max(0, int(fallback_count))
        self._hover_target = self._normalize_hover_target(self._hover_target)
        self.update()

    def set_theme_tokens(self, tokens: _ThemeTokens) -> None:
        self._tokens = tokens
        self.update()

    def set_animation_enabled(self, enabled: bool) -> None:
        self._animation_enabled = bool(enabled)
        if self._animation_enabled:
            if not self._timer.isActive():
                self._timer.start()
        else:
            self._timer.stop()
            self._phase = 0.0
        self.update()

    def clear(self) -> None:
        self.set_model(
            nodes=[],
            edges=[],
            hotspots=[],
            focus_node_id="",
            status_text=_DEFAULT_STATUS,
            subtitle=_DEFAULT_SUBTITLE,
            sparse_note="",
            fallback_count=0,
        )

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        position = event.position() if hasattr(event, "position") else QPointF(event.pos())
        hover = self._pick_hover_target(position)
        if hover != self._hover_target:
            self._hover_target = hover
            self.update()
        self.setCursor(Qt.PointingHandCursor if hover is not None else Qt.ArrowCursor)
        super().mouseMoveEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        if self._hover_target is not None:
            self._hover_target = None
            self.update()
        self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)

    def _advance_phase(self) -> None:
        if not self._animation_enabled:
            return
        self._phase = (self._phase + 0.024) % math.tau
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        outer = self.rect().adjusted(2, 2, -2, -2)
        if outer.width() <= 0 or outer.height() <= 0:
            return

        panel_rect = QRectF(outer)
        panel_path = QPainterPath()
        panel_path.addRoundedRect(panel_rect, 20.0, 20.0)
        self._paint_panel_background(painter, panel_path, panel_rect)

        content = panel_rect.adjusted(18.0, 16.0, -18.0, -16.0)
        header_rect = QRectF(content.left(), content.top(), content.width(), 56.0)
        footer_height = 44.0 if (self._sparse_note or self._hover_target is not None) else 20.0
        graph_rect = QRectF(
            content.left(),
            header_rect.bottom() + 10.0,
            content.width(),
            max(120.0, content.height() - header_rect.height() - footer_height - 12.0),
        )
        footer_rect = QRectF(
            content.left(),
            graph_rect.bottom() + 10.0,
            content.width(),
            max(0.0, content.bottom() - graph_rect.bottom() - 10.0),
        )

        self._paint_status_chrome(painter, header_rect)
        self._paint_grid(painter, graph_rect)
        if self._hotspots:
            self._paint_hotspots(painter, graph_rect)

        if not self._nodes:
            self._paint_empty_state(painter, graph_rect)
        else:
            positions = {node.node_id: self._project_point(node, graph_rect) for node in self._nodes}
            self._paint_edges(painter, positions)
            self._paint_nodes(painter, positions)

        self._paint_footer_chrome(painter, footer_rect)
        if self._hover_target is not None:
            self._paint_hover_panel(painter, content)

    def _paint_panel_background(self, painter: QPainter, path: QPainterPath, rect: QRectF) -> None:
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0.0, QColor(self._tokens.panel_alt))
        gradient.setColorAt(0.48, QColor(self._tokens.panel))
        gradient.setColorAt(1.0, QColor(self._tokens.bg))
        painter.fillPath(path, gradient)

        painter.save()
        painter.setClipPath(path)
        top_glow = QColor(self._tokens.accent_glow)
        top_glow.setAlpha(max(top_glow.alpha(), 26))
        painter.fillRect(QRectF(rect.left(), rect.top(), rect.width(), rect.height() * 0.28), top_glow)

        for index in range(20):
            y = rect.top() + 22.0 + (index * 10.0)
            line_color = QColor(self._tokens.border_soft)
            line_color.setAlpha(16 if index % 2 else 10)
            painter.setPen(QPen(line_color, 1.0))
            painter.drawLine(QPointF(rect.left() + 6.0, y), QPointF(rect.right() - 6.0, y))
        painter.restore()

        border_pen = QPen(QColor(self._tokens.border), 1.2)
        painter.setPen(border_pen)
        painter.drawPath(path)

        accent_pen = QPen(QColor(self._tokens.border_soft), 1.0)
        accent_pen.setCosmetic(True)
        painter.setPen(accent_pen)
        painter.drawRoundedRect(rect.adjusted(1.5, 1.5, -1.5, -1.5), 18.0, 18.0)

    def _paint_status_chrome(self, painter: QPainter, header_rect: QRectF) -> None:
        status_color = self._status_color()
        pill_rect = QRectF(header_rect.left(), header_rect.top() + 2.0, min(250.0, header_rect.width() * 0.52), 52.0)
        pill_fill = QColor(self._tokens.bg)
        pill_fill.setAlpha(178)
        self._draw_rounded_panel(painter, pill_rect, pill_fill, QColor(self._tokens.border_soft), radius=14.0)

        accent_strip = QRectF(pill_rect.left() + 8.0, pill_rect.top() + 8.0, 4.0, pill_rect.height() - 16.0)
        painter.setPen(Qt.NoPen)
        painter.setBrush(status_color)
        painter.drawRoundedRect(accent_strip, 2.0, 2.0)

        title_font = QFont(self.font())
        title_font.setBold(True)
        title_font.setPointSize(max(9, title_font.pointSize()))
        painter.setFont(title_font)
        painter.setPen(QColor(self._tokens.text))
        painter.drawText(pill_rect.adjusted(18.0, 8.0, -12.0, -24.0), Qt.AlignLeft | Qt.AlignVCenter, self._status_text)

        subtitle_font = QFont(self.font())
        subtitle_font.setPointSize(max(7, subtitle_font.pointSize() - 1))
        painter.setFont(subtitle_font)
        painter.setPen(QColor(self._tokens.text_muted))
        painter.drawText(pill_rect.adjusted(18.0, 24.0, -12.0, -7.0), Qt.AlignLeft | Qt.AlignVCenter, self._subtitle)

        chips: list[tuple[str, QColor]] = [
            (f"N {len(self._nodes)}", QColor(self._tokens.text)),
            (f"E {len(self._edges)}", QColor(self._tokens.border_strong)),
            (f"H {len(self._hotspots)}", QColor(self._tokens.warning if self._hotspots else self._tokens.text_muted)),
        ]
        if self._focus_node_id:
            chips.append(("FOCUS", status_color))
        if self._fallback_count:
            chips.append((f"FB {self._fallback_count}", QColor(self._tokens.selection)))

        fm = QFontMetrics(subtitle_font)
        right = header_rect.right()
        y = header_rect.top() + 9.0
        for text, fill in reversed(chips):
            width = max(54.0, fm.horizontalAdvance(text) + 20.0)
            chip_rect = QRectF(right - width, y, width, 24.0)
            right = chip_rect.left() - 8.0
            chip_fill = QColor(fill)
            chip_fill.setAlpha(48 if fill != QColor(self._tokens.text) else 34)
            chip_border = QColor(fill)
            chip_border.setAlpha(126)
            self._draw_pill(
                painter,
                chip_rect,
                text,
                fill=chip_fill,
                border=chip_border,
                text_color=QColor(self._tokens.text),
                font=subtitle_font,
                radius=11.0,
            )

    def _paint_grid(self, painter: QPainter, graph_rect: QRectF) -> None:
        center = graph_rect.center()
        radius = min(graph_rect.width(), graph_rect.height()) * 0.41
        if radius <= 0.0:
            return

        frame_pen = QPen(QColor(self._tokens.border_soft), 1.0)
        frame_pen.setCosmetic(True)
        frame_pen.setStyle(Qt.DashLine)
        painter.setPen(frame_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(graph_rect.adjusted(6.0, 6.0, -6.0, -6.0), 18.0, 18.0)

        ring_color = QColor(self._tokens.border_soft)
        ring_color.setAlpha(162)
        for ratio in (1.0, 0.78, 0.58, 0.38, 0.18):
            pen = QPen(ring_color, 1.0)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.drawEllipse(center, radius * ratio, radius * ratio)

        spoke_color = QColor(self._tokens.border_soft)
        spoke_color.setAlpha(118)
        pen = QPen(spoke_color, 1.0)
        pen.setCosmetic(True)
        painter.setPen(pen)
        for step in range(12):
            angle = math.tau * (step / 12.0)
            dx = math.cos(angle) * radius
            dy = math.sin(angle) * radius
            painter.drawLine(center, QPointF(center.x() + dx, center.y() + dy))

        sweep = QColor(self._tokens.accent_glow)
        sweep.setAlpha(max(24, min(64, sweep.alpha())))
        if self._animation_enabled:
            path = QPainterPath()
            path.moveTo(center)
            path.arcTo(
                QRectF(center.x() - radius, center.y() - radius, radius * 2.0, radius * 2.0),
                -math.degrees(self._phase) - 32.0,
                26.0,
            )
            path.closeSubpath()
            painter.save()
            painter.setClipRect(graph_rect.adjusted(6.0, 6.0, -6.0, -6.0))
            painter.fillPath(path, sweep)
            painter.restore()

        core_glow = QColor(self._tokens.accent_glow)
        core_glow.setAlpha(max(28, core_glow.alpha()))
        core_radius = radius * (0.19 + 0.04 * (1.0 + math.sin(self._phase)) * 0.5) if self._animation_enabled else radius * 0.21
        core_pen = QPen(core_glow, 2.0)
        painter.setPen(core_pen)
        painter.drawEllipse(center, core_radius, core_radius)

    def _paint_hotspots(self, painter: QPainter, graph_rect: QRectF) -> None:
        positions = self._hotspot_positions(graph_rect)
        base_font = QFont(self.font())
        base_font.setPointSize(max(7, base_font.pointSize() - 2))

        for hotspot in self._hotspots:
            point = positions[hotspot.hotspot_id]
            is_hover = self._hover_target is not None and self._hover_target.kind == "hotspot" and self._hover_target.item_id == hotspot.hotspot_id
            size = 7.5 + (1.5 if hotspot.active else 0.0) + (1.5 if is_hover else 0.0)
            fill = self._severity_color(hotspot.severity)
            fill.setAlpha(236 if hotspot.active or is_hover else 198)

            outer = QColor(fill)
            outer.setAlpha(120 if hotspot.active or is_hover else 82)
            painter.setPen(QPen(outer, 4.0))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(point, size + 3.0, size + 3.0)

            painter.setPen(QPen(QColor(self._tokens.bg), 1.2))
            painter.setBrush(fill)
            painter.drawEllipse(point, size, size)

            if hotspot.active or is_hover or len(self._hotspots) <= 4:
                label_rect = QRectF(point.x() - 48.0, point.y() + size + 5.0, 96.0, 16.0)
                painter.setFont(base_font)
                painter.setPen(QColor(self._tokens.text_muted if not is_hover else self._tokens.text))
                painter.drawText(label_rect, Qt.AlignHCenter | Qt.AlignTop, hotspot.label)

    def _paint_empty_state(self, painter: QPainter, graph_rect: QRectF) -> None:
        center = graph_rect.center()
        radius = min(graph_rect.width(), graph_rect.height()) * 0.12

        halo = QColor(self._tokens.accent_glow)
        halo.setAlpha(max(40, halo.alpha()))
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(halo, 5.0))
        painter.drawEllipse(center, radius + 18.0, radius + 18.0)

        painter.setPen(QPen(QColor(self._tokens.border_soft), 1.2))
        painter.drawEllipse(center, radius + 6.0, radius + 6.0)

        dot = QColor(self._tokens.accent)
        dot.setAlpha(224)
        painter.setBrush(dot)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius, radius)

        title_rect = QRectF(graph_rect.left() + 16.0, center.y() + radius + 18.0, graph_rect.width() - 32.0, 30.0)
        subtitle_rect = QRectF(graph_rect.left() + 26.0, title_rect.bottom() + 4.0, graph_rect.width() - 52.0, 48.0)

        title_font = QFont(self.font())
        title_font.setPointSize(max(10, title_font.pointSize() + 1))
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.setPen(QColor(self._tokens.text))
        painter.drawText(title_rect, Qt.AlignCenter, self._status_text)

        subtitle_font = QFont(self.font())
        subtitle_font.setPointSize(max(8, subtitle_font.pointSize() - 1))
        painter.setFont(subtitle_font)
        painter.setPen(QColor(self._tokens.text_muted))
        painter.drawText(subtitle_rect, Qt.AlignCenter | Qt.TextWordWrap, self._subtitle)

        if self._hotspots:
            badge_rect = QRectF(center.x() - 80.0, center.y() - radius - 38.0, 160.0, 22.0)
            self._draw_pill(
                painter,
                badge_rect,
                f"{len(self._hotspots)} hotspots informativos",
                fill=QColor(self._tokens.warning + "33") if len(self._tokens.warning) == 7 else QColor(self._tokens.warning),
                border=QColor(self._tokens.warning),
                text_color=QColor(self._tokens.text),
                font=subtitle_font,
                radius=10.0,
            )

    def _paint_edges(self, painter: QPainter, positions: Mapping[str, QPointF]) -> None:
        for edge in self._edges:
            source = positions.get(edge.source)
            target = positions.get(edge.target)
            if source is None or target is None:
                continue

            is_focus_edge = bool(self._focus_node_id and self._focus_node_id in (edge.source, edge.target))
            base_color = QColor(self._tokens.selection if is_focus_edge else self._tokens.border_strong)
            if edge.active:
                base_color = QColor(self._tokens.accent)
            base_color.setAlpha(224 if is_focus_edge or edge.active else 132)

            glow = QColor(base_color)
            glow.setAlpha(46 if not is_focus_edge else 82)
            path = self._edge_path(source, target, edge.order)

            glow_pen = QPen(glow, 4.5 if is_focus_edge else 2.6)
            glow_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(glow_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)

            width = 1.1 + min(max(edge.weight, 0.2), 3.0) * (0.78 if is_focus_edge else 0.46)
            pen = QPen(base_color, width)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawPath(path)

    def _paint_nodes(self, painter: QPainter, positions: Mapping[str, QPointF]) -> None:
        label_font = QFont(self.font())
        label_font.setPointSize(max(7, label_font.pointSize() - 1))

        hovered_node_id = self._hover_target.item_id if self._hover_target is not None and self._hover_target.kind == "node" else ""
        show_all_labels = len(self._nodes) <= 6

        for node in self._nodes:
            point = positions[node.node_id]
            is_focus = bool(self._focus_node_id and node.node_id == self._focus_node_id)
            is_hover = hovered_node_id == node.node_id
            radius = 7.0 + min(max(node.weight, 0.5), 4.0) * 2.0
            if is_focus:
                radius += 2.2
            elif is_hover:
                radius += 1.4

            fill = self._severity_color(node.severity)
            fill.setAlpha(246 if node.active or is_focus or is_hover else 222)
            ring = QColor(self._tokens.border_strong if node.active or is_hover else self._tokens.border)
            if is_focus:
                ring = QColor(self._tokens.accent)

            if is_focus:
                glow = QColor(self._tokens.focus_ring)
                glow.setAlpha(max(88, glow.alpha()))
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(glow, 5.5))
                halo = radius + 6.0 + (1.4 if self._animation_enabled else 0.0) * ((math.sin(self._phase) + 1.0) * 0.5)
                painter.drawEllipse(point, halo, halo)
            elif is_hover:
                glow = QColor(self._tokens.accent_glow)
                glow.setAlpha(max(72, glow.alpha()))
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(glow, 3.0))
                painter.drawEllipse(point, radius + 4.0, radius + 4.0)

            if not node.has_explicit_position:
                guide = QColor(self._tokens.border_soft)
                guide.setAlpha(150)
                guide_pen = QPen(guide, 1.0)
                guide_pen.setStyle(Qt.DashLine)
                painter.setPen(guide_pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(point, radius + 3.4, radius + 3.4)

            painter.setBrush(fill)
            painter.setPen(QPen(ring, 1.4))
            painter.drawEllipse(point, radius, radius)

            core = QColor(self._tokens.bg)
            core.setAlpha(214)
            painter.setBrush(core)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(point, max(2.0, radius * 0.26), max(2.0, radius * 0.26))

            if show_all_labels or is_focus or node.active or is_hover:
                label_rect = QRectF(point.x() - 74.0, point.y() + radius + 7.0, 148.0, 26.0)
                label_fill = QColor(self._tokens.bg)
                label_fill.setAlpha(150 if is_focus or is_hover else 118)
                label_border = QColor(ring)
                label_border.setAlpha(116 if is_focus or is_hover else 62)
                self._draw_rounded_panel(painter, label_rect, label_fill, label_border, radius=10.0)

                painter.setFont(label_font)
                text_color = QColor(self._tokens.text if is_focus or is_hover else (self._tokens.text if node.active else self._tokens.text_muted))
                painter.setPen(text_color)
                text_rect = label_rect.adjusted(8.0, 4.0, -8.0, -4.0)
                painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, node.label)

    def _paint_footer_chrome(self, painter: QPainter, footer_rect: QRectF) -> None:
        if footer_rect.height() <= 0.0:
            return

        note_font = QFont(self.font())
        note_font.setPointSize(max(7, note_font.pointSize() - 2))
        if self._sparse_note:
            rect = QRectF(footer_rect.left(), footer_rect.top() + 6.0, min(footer_rect.width() * 0.72, 320.0), 24.0)
            self._draw_pill(
                painter,
                rect,
                self._sparse_note,
                fill=QColor(self._tokens.selection),
                border=QColor(self._tokens.border_strong),
                text_color=QColor(self._tokens.text),
                font=note_font,
                radius=11.0,
            )

        hint = "hover: nodes/hotspots · deterministic focus" if (self._nodes or self._hotspots) else "snapshot empty-valid"
        right_rect = QRectF(footer_rect.right() - 190.0, footer_rect.top() + 6.0, 190.0, 24.0)
        self._draw_pill(
            painter,
            right_rect,
            hint,
            fill=QColor(self._tokens.bg),
            border=QColor(self._tokens.border_soft),
            text_color=QColor(self._tokens.text_muted),
            font=note_font,
            radius=11.0,
            align=Qt.AlignCenter,
        )

    def _paint_hover_panel(self, painter: QPainter, content_rect: QRectF) -> None:
        if self._hover_target is None:
            return

        panel_width = min(260.0, content_rect.width() * 0.52)
        panel_rect = QRectF(content_rect.right() - panel_width, content_rect.bottom() - 62.0, panel_width, 54.0)
        fill = QColor(self._tokens.bg)
        fill.setAlpha(204)
        border = self._severity_color(self._hover_target.severity)
        border.setAlpha(120)
        self._draw_rounded_panel(painter, panel_rect, fill, border, radius=12.0)

        title_font = QFont(self.font())
        title_font.setBold(True)
        title_font.setPointSize(max(8, title_font.pointSize() - 1))
        painter.setFont(title_font)
        painter.setPen(QColor(self._tokens.text))
        painter.drawText(panel_rect.adjusted(12.0, 8.0, -12.0, -24.0), Qt.AlignLeft | Qt.AlignVCenter, self._hover_target.title)

        subtitle_font = QFont(self.font())
        subtitle_font.setPointSize(max(7, subtitle_font.pointSize() - 2))
        painter.setFont(subtitle_font)
        painter.setPen(QColor(self._tokens.text_muted))
        painter.drawText(panel_rect.adjusted(12.0, 24.0, -12.0, -8.0), Qt.AlignLeft | Qt.AlignVCenter, self._hover_target.subtitle)

    def _draw_rounded_panel(
        self,
        painter: QPainter,
        rect: QRectF,
        fill: QColor,
        border: QColor,
        *,
        radius: float,
    ) -> None:
        painter.setPen(QPen(border, 1.0))
        painter.setBrush(fill)
        painter.drawRoundedRect(rect, radius, radius)

    def _draw_pill(
        self,
        painter: QPainter,
        rect: QRectF,
        text: str,
        *,
        fill: QColor,
        border: QColor,
        text_color: QColor,
        font: QFont,
        radius: float,
        align: Qt.AlignmentFlag = Qt.AlignCenter,
    ) -> None:
        self._draw_rounded_panel(painter, rect, fill, border, radius=radius)
        painter.setFont(font)
        painter.setPen(text_color)
        painter.drawText(rect.adjusted(8.0, 0.0, -8.0, 0.0), align | Qt.AlignVCenter, text)

    def _project_point(self, node: _RadarNode, graph_rect: QRectF) -> QPointF:
        radius_x = graph_rect.width() * 0.35
        radius_y = graph_rect.height() * 0.35
        cx = graph_rect.center().x() + (max(-1.0, min(1.0, node.x)) * radius_x)
        cy = graph_rect.center().y() + (max(-1.0, min(1.0, node.y)) * radius_y)
        return QPointF(cx, cy)

    def _hotspot_positions(self, graph_rect: QRectF) -> dict[str, QPointF]:
        if not self._hotspots:
            return {}
        center = graph_rect.center()
        radius = min(graph_rect.width(), graph_rect.height()) * 0.46
        positions: dict[str, QPointF] = {}
        total = len(self._hotspots)
        for hotspot in self._hotspots:
            if total == 1:
                angle = -math.pi / 2.0
            else:
                spread = math.pi * 1.35
                angle = (-math.pi / 2.0) - (spread / 2.0) + (spread * (hotspot.order / max(1, total - 1)))
            x = center.x() + (math.cos(angle) * radius)
            y = center.y() + (math.sin(angle) * radius)
            positions[hotspot.hotspot_id] = QPointF(x, y)
        return positions

    def _edge_path(self, source: QPointF, target: QPointF, order: int) -> QPainterPath:
        path = QPainterPath(source)
        dx = target.x() - source.x()
        dy = target.y() - source.y()
        distance = max(1.0, math.hypot(dx, dy))
        normal_x = -dy / distance
        normal_y = dx / distance
        curvature = min(28.0, 10.0 + ((order % 4) * 4.5))
        if order % 2:
            curvature *= -1.0
        midpoint = QPointF(
            (source.x() + target.x()) * 0.5 + (normal_x * curvature),
            (source.y() + target.y()) * 0.5 + (normal_y * curvature),
        )
        path.quadTo(midpoint, target)
        return path

    def _severity_color(self, severity: str) -> QColor:
        if severity == "danger":
            return QColor(self._tokens.danger)
        if severity == "warning":
            return QColor(self._tokens.warning)
        if severity == "success":
            return QColor(self._tokens.success)
        if severity == "accent":
            return QColor(self._tokens.accent)
        return QColor(self._tokens.accent)

    def _status_color(self) -> QColor:
        if any(item.severity == "danger" and item.active for item in self._hotspots):
            return QColor(self._tokens.danger)
        if any(node.severity == "danger" and node.active for node in self._nodes):
            return QColor(self._tokens.danger)
        if self._focus_node_id:
            return QColor(self._tokens.accent)
        if self._nodes:
            return QColor(self._tokens.success)
        if self._hotspots:
            return QColor(self._tokens.warning)
        return QColor(self._tokens.text_muted)

    def _pick_hover_target(self, position: QPointF) -> _HoverTarget | None:
        graph_rect = self._graph_rect()
        node_positions = {node.node_id: self._project_point(node, graph_rect) for node in self._nodes}
        hotspot_positions = self._hotspot_positions(graph_rect)

        best_distance = float("inf")
        chosen: _HoverTarget | None = None
        for node in self._nodes:
            point = node_positions[node.node_id]
            distance = math.hypot(position.x() - point.x(), position.y() - point.y())
            threshold = 18.0 + min(max(node.weight, 0.5), 4.0) * 2.0
            if distance <= threshold and distance < best_distance:
                subtitle_bits = [node.node_id]
                if not node.has_explicit_position:
                    subtitle_bits.append("fallback")
                if node.active:
                    subtitle_bits.append("active")
                chosen = _HoverTarget(
                    kind="node",
                    item_id=node.node_id,
                    title=node.label,
                    subtitle=" · ".join(subtitle_bits),
                    severity=node.severity,
                )
                best_distance = distance

        for hotspot in self._hotspots:
            point = hotspot_positions[hotspot.hotspot_id]
            distance = math.hypot(position.x() - point.x(), position.y() - point.y())
            threshold = 15.0 + (3.0 if hotspot.active else 0.0)
            if distance <= threshold and distance < best_distance:
                subtitle = hotspot.hotspot_id
                if hotspot.active:
                    subtitle += " · active"
                chosen = _HoverTarget(
                    kind="hotspot",
                    item_id=hotspot.hotspot_id,
                    title=hotspot.label,
                    subtitle=subtitle,
                    severity=hotspot.severity,
                )
                best_distance = distance
        return chosen

    def _normalize_hover_target(self, hover: _HoverTarget | None) -> _HoverTarget | None:
        if hover is None:
            return None
        if hover.kind == "node" and any(node.node_id == hover.item_id for node in self._nodes):
            return hover
        if hover.kind == "hotspot" and any(hotspot.hotspot_id == hover.item_id for hotspot in self._hotspots):
            return hover
        return None

    def _graph_rect(self) -> QRectF:
        outer = QRectF(self.rect().adjusted(2, 2, -2, -2))
        content = outer.adjusted(18.0, 16.0, -18.0, -16.0)
        header_height = 56.0
        footer_height = 44.0 if (self._sparse_note or self._hover_target is not None) else 20.0
        return QRectF(
            content.left(),
            content.top() + header_height + 10.0,
            content.width(),
            max(120.0, content.height() - header_height - footer_height - 12.0),
        )


class AegisGraphRadar(QWidget):
    """Compact radar widget that consumes canonical snapshot graph keys.

    Public API is intentionally frozen to the shared contract:
    - set_snapshot(snapshot)
    - set_graph_data(nodes, edges=None, focus_node_id=None)
    - set_focus_node(node_id)
    - set_theme_tokens(tokens)
    - set_animation_enabled(enabled)
    - clear()
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tokens = _ThemeTokens()
        self._nodes: list[_RadarNode] = []
        self._edges: list[_RadarEdge] = []
        self._hotspots: list[_RadarHotspot] = []
        self._focus_node_id = ""
        self._status_text = _DEFAULT_STATUS
        self._subtitle = _DEFAULT_SUBTITLE
        self._animation_enabled = True
        self._fallback_count = 0
        self._sparse_note = ""

        self._frame = QFrame(self)
        self._frame.setObjectName("aegisGraphRadarFrame")

        self._title_label = QLabel("Graph Radar", self._frame)
        self._title_label.setObjectName("aegisGraphRadarTitle")

        self._meta_label = QLabel(_DEFAULT_SUBTITLE, self._frame)
        self._meta_label.setObjectName("aegisGraphRadarMeta")
        self._meta_label.setWordWrap(True)

        self._canvas = _RadarCanvas(self._frame)

        frame_layout = QVBoxLayout(self._frame)
        frame_layout.setContentsMargins(16, 16, 16, 16)
        frame_layout.setSpacing(10)
        frame_layout.addWidget(self._title_label)
        frame_layout.addWidget(self._meta_label)
        frame_layout.addWidget(self._canvas, 1)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._frame)

        self.set_theme_tokens(None)
        self.clear()

    def set_snapshot(self, snapshot: Any) -> None:
        mapping = self._snapshot_mapping(snapshot)
        nodes = self._canonical_then_alias(
            mapping,
            canonical_keys=_CANONICAL_SNAPSHOT_NODE_KEYS,
            alias_keys=_COMPAT_SNAPSHOT_NODE_KEYS,
            default=[],
        )
        edges = self._canonical_then_alias(
            mapping,
            canonical_keys=_CANONICAL_SNAPSHOT_EDGE_KEYS,
            alias_keys=_COMPAT_SNAPSHOT_EDGE_KEYS,
            default=[],
        )
        focus_node_id = self._canonical_then_alias(
            mapping,
            canonical_keys=_CANONICAL_SNAPSHOT_FOCUS_KEYS,
            alias_keys=_COMPAT_SNAPSHOT_FOCUS_KEYS,
            default="",
        )
        hotspots = self._read_value(mapping, "hotspots", default=[])
        self._status_text = self._coerce_text(self._read_value(mapping, "status_text", default=_DEFAULT_STATUS), _DEFAULT_STATUS)
        self._subtitle = self._coerce_text(self._read_value(mapping, "subtitle", default=_DEFAULT_SUBTITLE), _DEFAULT_SUBTITLE)
        self._apply_graph_model(nodes=nodes, edges=edges, hotspots=hotspots, focus_node_id=focus_node_id)

    def set_graph_data(self, nodes: Any, edges: Any = None, focus_node_id: Any = None) -> None:
        self._apply_graph_model(nodes=nodes, edges=edges, hotspots=[], focus_node_id=focus_node_id)

    def set_focus_node(self, node_id: Any) -> None:
        self._focus_node_id = self._resolve_focus_node_id(node_id, self._nodes)
        self._recompute_local_state()
        self._refresh_view()

    def set_theme_tokens(self, tokens: Any) -> None:
        self._tokens = self._coerce_theme_tokens(tokens)
        self._apply_styles()
        self._canvas.set_theme_tokens(self._tokens)
        self._refresh_view()

    def set_skin(self, tokens: Any) -> None:
        self.set_theme_tokens(tokens)

    def set_animation_enabled(self, enabled: Any) -> None:
        self._animation_enabled = bool(enabled)
        self._canvas.set_animation_enabled(self._animation_enabled)

    def clear(self) -> None:
        self._nodes = []
        self._edges = []
        self._hotspots = []
        self._focus_node_id = ""
        self._status_text = _DEFAULT_STATUS
        self._subtitle = _DEFAULT_SUBTITLE
        self._fallback_count = 0
        self._sparse_note = ""
        self._refresh_view()

    def _apply_graph_model(self, *, nodes: Any, edges: Any, hotspots: Any, focus_node_id: Any) -> None:
        normalized_nodes = self._normalize_nodes(nodes)
        normalized_edges = self._normalize_edges(edges, normalized_nodes)
        normalized_hotspots = self._normalize_hotspots(hotspots)
        self._nodes = self._apply_fallback_positions(normalized_nodes)
        self._edges = normalized_edges
        self._hotspots = normalized_hotspots
        self._focus_node_id = self._resolve_focus_node_id(focus_node_id, self._nodes)
        self._recompute_local_state()
        self._refresh_view()

    def _recompute_local_state(self) -> None:
        self._fallback_count = sum(1 for node in self._nodes if not node.has_explicit_position)
        if not self._nodes:
            if self._hotspots:
                self._sparse_note = "no canonical graph; hotspots are shown as informational signals only"
            else:
                self._sparse_note = ""
            return

        focus_label = next((node.label for node in self._nodes if node.node_id == self._focus_node_id), "")
        note_bits: list[str] = []
        if self._fallback_count:
            note_bits.append(f"deterministic fallback on {self._fallback_count} node(s)")
        if len(self._nodes) <= 2:
            note_bits.append("sparse graph")
        if not self._edges:
            note_bits.append("no canonical edges")
        if focus_label:
            note_bits.append(f"focus {focus_label}")
        self._sparse_note = " · ".join(note_bits)

    def _refresh_view(self) -> None:
        self._meta_label.setText(self._build_meta_text())
        self._canvas.set_model(
            nodes=self._nodes,
            edges=self._edges,
            hotspots=self._hotspots,
            focus_node_id=self._focus_node_id,
            status_text=self._status_text,
            subtitle=self._subtitle,
            sparse_note=self._sparse_note,
            fallback_count=self._fallback_count,
        )

    def _build_meta_text(self) -> str:
        parts = [self._status_text or _DEFAULT_STATUS]
        parts.append(f"{len(self._nodes)} nodes")
        parts.append(f"{len(self._edges)} edges")
        if self._hotspots:
            parts.append(f"{len(self._hotspots)} hotspots")
        if self._focus_node_id:
            parts.append(f"focus {self._focus_node_id}")
        if self._fallback_count:
            parts.append(f"fallback {self._fallback_count}")
        if self._subtitle and self._subtitle != _DEFAULT_SUBTITLE:
            parts.append(self._subtitle)
        return " · ".join(parts)

    def _apply_styles(self) -> None:
        self._frame.setStyleSheet(
            f"""
            QFrame#aegisGraphRadarFrame {{
                background: {self._tokens.panel};
                border: 1px solid {self._tokens.border};
                border-radius: 18px;
            }}
            QLabel#aegisGraphRadarTitle {{
                color: {self._tokens.text};
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 0.7px;
                text-transform: uppercase;
            }}
            QLabel#aegisGraphRadarMeta {{
                color: {self._tokens.text_muted};
                font-size: 11px;
                line-height: 1.25em;
            }}
            """
        )

    def _normalize_nodes(self, raw_nodes: Any) -> list[_RadarNode]:
        if not isinstance(raw_nodes, Iterable) or isinstance(raw_nodes, (str, bytes, Mapping)):
            return []

        normalized: list[_RadarNode] = []
        seen_ids: set[str] = set()
        for raw_node in raw_nodes:
            node = self._normalize_node(raw_node, order=len(normalized))
            if node is None:
                continue
            if node.node_id in seen_ids:
                continue
            seen_ids.add(node.node_id)
            normalized.append(node)
        return normalized

    def _normalize_node(self, raw_node: Any, order: int) -> _RadarNode | None:
        mapping = self._item_mapping(raw_node)
        node_id = self._coerce_text(self._first_present(mapping, _NODE_ID_KEYS, default=""), "")
        if not node_id:
            return None

        label = self._coerce_text(self._first_present(mapping, _NODE_LABEL_KEYS, default=node_id), node_id)
        coords = self._normalize_coords(
            self._read_value(mapping, "x"),
            self._read_value(mapping, "y"),
        )
        has_explicit_position = coords is not None
        x, y = coords if coords is not None else (0.0, 0.0)

        weight = self._coerce_float(self._read_value(mapping, "weight"), default=1.0, minimum=0.5, maximum=4.0)
        severity = self._normalize_severity(self._read_value(mapping, "severity"))
        active = bool(self._read_value(mapping, "active", default=False))

        meta_value = self._read_value(mapping, "meta", default={})
        meta = dict(meta_value) if isinstance(meta_value, Mapping) else {}

        return _RadarNode(
            node_id=node_id,
            label=label,
            x=x,
            y=y,
            has_explicit_position=has_explicit_position,
            weight=weight,
            severity=severity,
            active=active,
            meta=meta,
            order=order,
        )

    def _normalize_edges(self, raw_edges: Any, nodes: list[_RadarNode]) -> list[_RadarEdge]:
        if not isinstance(raw_edges, Iterable) or isinstance(raw_edges, (str, bytes, Mapping)):
            return []

        known_ids = {node.node_id for node in nodes}
        normalized: list[_RadarEdge] = []
        for order, raw_edge in enumerate(raw_edges):
            mapping = self._item_mapping(raw_edge)
            source = self._coerce_text(self._first_present(mapping, _EDGE_SOURCE_KEYS, default=""), "")
            target = self._coerce_text(self._first_present(mapping, _EDGE_TARGET_KEYS, default=""), "")
            if not source or not target:
                continue
            if source not in known_ids or target not in known_ids:
                continue
            weight = self._coerce_float(self._read_value(mapping, "weight"), default=1.0, minimum=0.2, maximum=3.0)
            active = bool(self._read_value(mapping, "active", default=False))
            kind = self._coerce_text(self._read_value(mapping, "kind", default=""), "")
            normalized.append(
                _RadarEdge(
                    source=source,
                    target=target,
                    weight=weight,
                    active=active,
                    kind=kind,
                    order=order,
                )
            )
        return normalized

    def _normalize_hotspots(self, raw_hotspots: Any) -> list[_RadarHotspot]:
        if not isinstance(raw_hotspots, Iterable) or isinstance(raw_hotspots, (str, bytes, Mapping)):
            return []

        normalized: list[_RadarHotspot] = []
        seen_ids: set[str] = set()
        for order, raw_hotspot in enumerate(raw_hotspots):
            mapping = self._item_mapping(raw_hotspot)
            explicit_id = self._coerce_text(self._first_present(mapping, _HOTSPOT_ID_KEYS, default=""), "")
            label = self._coerce_text(self._first_present(mapping, _HOTSPOT_LABEL_KEYS, default="hotspot"), "hotspot")
            hotspot_id = explicit_id or f"hotspot-{order + 1}"
            if hotspot_id in seen_ids:
                continue
            seen_ids.add(hotspot_id)
            severity = self._normalize_severity(self._read_value(mapping, "severity"))
            active = bool(self._read_value(mapping, "active", default=False))
            meta_value = self._read_value(mapping, "meta", default={})
            meta = dict(meta_value) if isinstance(meta_value, Mapping) else {}
            normalized.append(
                _RadarHotspot(
                    hotspot_id=hotspot_id,
                    label=label,
                    severity=severity,
                    active=active,
                    meta=meta,
                    order=order,
                )
            )
        return normalized

    def _apply_fallback_positions(self, nodes: list[_RadarNode]) -> list[_RadarNode]:
        if not nodes:
            return []

        total = len(nodes)
        rebuilt: list[_RadarNode] = []
        for node in nodes:
            if node.has_explicit_position:
                rebuilt.append(node)
                continue
            x, y = self._fallback_position(node.order, total)
            rebuilt.append(
                _RadarNode(
                    node_id=node.node_id,
                    label=node.label,
                    x=x,
                    y=y,
                    has_explicit_position=False,
                    weight=node.weight,
                    severity=node.severity,
                    active=node.active,
                    meta=node.meta,
                    order=node.order,
                )
            )
        return rebuilt

    def _resolve_focus_node_id(self, requested: Any, nodes: list[_RadarNode]) -> str:
        requested_id = self._coerce_text(requested, "")
        known_ids = {node.node_id for node in nodes}
        if requested_id and requested_id in known_ids:
            return requested_id
        for node in nodes:
            if node.active:
                return node.node_id
        return nodes[0].node_id if nodes else ""

    def _snapshot_mapping(self, snapshot: Any) -> Mapping[str, Any]:
        if isinstance(snapshot, Mapping):
            return snapshot
        if snapshot is None:
            return {}

        data: dict[str, Any] = {}
        for key in (
            *_CANONICAL_SNAPSHOT_NODE_KEYS,
            *_CANONICAL_SNAPSHOT_EDGE_KEYS,
            *_CANONICAL_SNAPSHOT_FOCUS_KEYS,
            *_COMPAT_SNAPSHOT_NODE_KEYS,
            *_COMPAT_SNAPSHOT_EDGE_KEYS,
            *_COMPAT_SNAPSHOT_FOCUS_KEYS,
            "status_text",
            "subtitle",
            "hotspots",
        ):
            value = getattr(snapshot, key, None)
            if value is not None:
                data[key] = value
        return data

    def _item_mapping(self, item: Any) -> Mapping[str, Any]:
        if isinstance(item, Mapping):
            return item
        if item is None:
            return {}
        data: dict[str, Any] = {}
        for key in (
            *_NODE_ID_KEYS,
            *_NODE_LABEL_KEYS,
            *_HOTSPOT_ID_KEYS,
            *_HOTSPOT_LABEL_KEYS,
            "x",
            "y",
            "weight",
            "severity",
            "active",
            "meta",
            *_EDGE_SOURCE_KEYS,
            *_EDGE_TARGET_KEYS,
            "kind",
        ):
            value = getattr(item, key, None)
            if value is not None:
                data[key] = value
        return data

    def _coerce_theme_tokens(self, tokens: Any) -> _ThemeTokens:
        if tokens is None:
            return _ThemeTokens()
        if isinstance(tokens, _ThemeTokens):
            return tokens

        def pull(name: str, default: str) -> str:
            if isinstance(tokens, Mapping):
                value = tokens.get(name, default)
            else:
                value = getattr(tokens, name, default)
            return self._coerce_color(value, default)

        defaults = _ThemeTokens()
        return _ThemeTokens(
            bg=pull("bg", defaults.bg),
            panel=pull("panel", defaults.panel),
            panel_alt=pull("panel_alt", defaults.panel_alt),
            border=pull("border", defaults.border),
            border_soft=pull("border_soft", defaults.border_soft),
            border_strong=pull("border_strong", defaults.border_strong),
            text=pull("text", defaults.text),
            text_muted=pull("text_muted", defaults.text_muted),
            accent=pull("accent", defaults.accent),
            accent_glow=pull("accent_glow", defaults.accent_glow),
            success=pull("success", defaults.success),
            warning=pull("warning", defaults.warning),
            danger=pull("danger", defaults.danger),
            selection=pull("selection", defaults.selection),
            focus_ring=pull("focus_ring", defaults.focus_ring),
            shadow=pull("shadow", defaults.shadow),
        )

    def _normalize_coords(self, raw_x: Any, raw_y: Any) -> tuple[float, float] | None:
        x = self._coerce_float(raw_x, default=None)
        y = self._coerce_float(raw_y, default=None)
        if x is None or y is None:
            return None
        if 0.0 <= x <= 100.0 and 0.0 <= y <= 100.0:
            x = (x / 50.0) - 1.0
            y = (y / 50.0) - 1.0
        return (max(-1.0, min(1.0, x)), max(-1.0, min(1.0, y)))

    def _fallback_position(self, order: int, total: int) -> tuple[float, float]:
        if total <= 1:
            return (0.0, 0.0)
        ring = order % 3
        radius = 0.3 + (ring * 0.18)
        if total <= 4:
            radius = 0.48
        elif total <= 8:
            radius = 0.4 + (0.18 * (order % 2))
        angle = (order * _GOLDEN_ANGLE) - (math.pi / 2.0)
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        return (max(-0.9, min(0.9, x)), max(-0.9, min(0.9, y)))

    def _normalize_severity(self, value: Any) -> str:
        text = self._coerce_text(value, "neutral").lower()
        if text in {"danger", "warning", "success", "neutral", "accent"}:
            return text
        return "neutral"

    def _canonical_then_alias(
        self,
        mapping: Mapping[str, Any],
        *,
        canonical_keys: Iterable[str],
        alias_keys: Iterable[str],
        default: Any = None,
    ) -> Any:
        value = self._first_present(mapping, canonical_keys, default=None)
        if value is not None:
            return value
        return self._first_present(mapping, alias_keys, default=default)

    def _first_present(self, mapping: Mapping[str, Any], keys: Iterable[str], default: Any = None) -> Any:
        for key in keys:
            if key in mapping:
                return mapping[key]
        return default

    def _read_value(self, mapping: Mapping[str, Any], key: str, default: Any = None) -> Any:
        return mapping[key] if key in mapping else default

    def _coerce_text(self, value: Any, default: str) -> str:
        if value is None:
            return default
        text = str(value).strip()
        return text if text else default

    def _coerce_float(
        self,
        value: Any,
        *,
        default: float | None,
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> float | None:
        if value is None:
            return default
        try:
            result = float(value)
        except (TypeError, ValueError):
            return default
        if minimum is not None:
            result = max(minimum, result)
        if maximum is not None:
            result = min(maximum, result)
        return result

    def _coerce_color(self, value: Any, default: str) -> str:
        text = self._coerce_text(value, default)
        color = QColor(text)
        return text if color.isValid() else default
