from __future__ import annotations

import datetime as dt
import json
from copy import deepcopy
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import QEvent, QObject, QPoint, QPointF, QRect, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QBrush, QKeySequence, QLinearGradient, QPainter, QPainterPath, QPen, QShortcut
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..catalog import (
    GlassCatalogEntry,
    get_catalog_entry,
    list_catalog_categories,
    list_catalog_entries,
    list_catalog_tags,
    register_builtin_catalog_entries,
)
from ..charts import (
    GlassChartPalette,
    GlassChartStyle,
    get_chart_palette,
    get_chart_style,
    list_chart_palettes,
    list_chart_styles,
    register_builtin_chart_catalog,
)
from ..config import GlassRegionConfig, GlassTabConfig, GlassTemplateConfig, get_template_preset
from ..data import DataQuery, describe_data_provider, execute_data_query, list_data_providers
from ..data_providers import register_builtin_data_providers
from ..icons import apply_icon, get_icon
from ..integration import InProcessIntegrationAdapter, create_reference_workspace_service
from ..template import GlassPanelFrame, GlassPanelTemplate
from ..workbench_editor_support import (
    behavior_summary,
    default_behavior_binding,
    default_widget_props,
    normalize_behavior_binding,
    normalize_widget_props,
    parse_behavior_payload,
)
from .catalog_dashboard_entries import DashboardCatalogEntrySpec, iter_dashboard_catalog_specs


def _clear_layout(layout: QVBoxLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget is not None:
            widget.setParent(None)
            continue
        if child_layout is not None:
            while child_layout.count():
                child_item = child_layout.takeAt(0)
                child_widget = child_item.widget()
                if child_widget is not None:
                    child_widget.setParent(None)


def _apply_shadow(
    widget: QWidget,
    *,
    blur: float = 16.0,
    y_offset: float = 4.0,
    alpha: int = 22,
) -> None:
    if widget is None:
        return
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsDropShadowEffect):
        effect = QGraphicsDropShadowEffect(widget)
        widget.setGraphicsEffect(effect)
    effect.setBlurRadius(max(0.0, float(blur)))
    effect.setOffset(0.0, float(y_offset))
    effect.setColor(QColor(4, 10, 18, max(0, min(255, int(alpha)))))


def _repolish(widget: QWidget) -> None:
    if widget is None:
        return
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


class _HoverCardFilter(QObject):
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        if isinstance(watched, QWidget):
            if event.type() in {QEvent.Enter, QEvent.HoverEnter}:
                watched.setProperty("hover", True)
                _repolish(watched)
            elif event.type() in {QEvent.Leave, QEvent.HoverLeave}:
                watched.setProperty("hover", False)
                _repolish(watched)
        return False


_CARD_HOVER_FILTER: _HoverCardFilter | None = None


def _enable_card_hover(widget: QWidget) -> None:
    global _CARD_HOVER_FILTER
    if widget is None:
        return
    if _CARD_HOVER_FILTER is None:
        _CARD_HOVER_FILTER = _HoverCardFilter()
    widget.setAttribute(Qt.WA_Hover, True)
    widget.setMouseTracking(True)
    widget.setProperty("hoverable", True)
    widget.setProperty("hover", False)
    widget.installEventFilter(_CARD_HOVER_FILTER)


@dataclass(slots=True)
class WorkbenchPanelType:
    panel_type: str
    title: str
    icon_name: str
    default_role: str
    description: str
    default_subtitle: str
    default_text: str
    category: str = "content"
    object_kind: str = "content"
    allowed_slots: tuple[str, ...] = ("main", "side", "status")
    max_per_slot: int | None = None
    heavy: bool = False


@dataclass(slots=True)
class WorkbenchPanelState:
    panel_id: str
    panel_type: str
    title: str
    subtitle: str
    target_slot: str
    role: str
    state: str
    visible: bool
    text: str
    icon_name: str
    variant: str = "default"
    density: str = "compact"
    width_policy: str = "stretch"
    padding: str = "normal"
    data_provider_id: str = ""
    data_query_id: str = ""
    chart_mode: str = "line"
    chart_style_id: str = "silver_line"
    chart_palette_id: str = "auto"
    chart_show_grid: bool = True
    chart_show_glow: bool = True
    chart_show_markers: bool = False
    chart_smooth: bool = True
    chart_line_width: int = 2
    chart_fill_alpha: int = 26
    height_policy: str = "auto"
    panel_height: int = 0
    list_options: tuple[str, ...] = ()
    widget_props: dict[str, Any] = field(default_factory=dict)
    behavior: dict[str, Any] = field(default_factory=default_behavior_binding)
    dynamic: bool = True


@dataclass(slots=True)
class WorkbenchEditorSession:
    context_id: str
    source_kind: str
    source_ref: str
    entry_id: str
    core_baseline: dict[str, dict[str, Any]]
    core_working: dict[str, dict[str, Any]]
    dynamic_baseline: list[WorkbenchPanelState]
    dynamic_working: list[WorkbenchPanelState]
    split_baseline: tuple[int, int]
    split_working: tuple[int, int]
    panel_counter: int = 0
    selected_panel_id: str | None = None
    dirty: bool = False

    def clone_payload(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "source_kind": self.source_kind,
            "source_ref": self.source_ref,
            "entry_id": self.entry_id,
            "core": deepcopy(self.core_working),
            "dynamic": [
                {
                    "panel_id": item.panel_id,
                    "panel_type": item.panel_type,
                    "title": item.title,
                    "subtitle": item.subtitle,
                    "target_slot": item.target_slot,
                    "role": item.role,
                    "state": item.state,
                    "visible": bool(item.visible),
                    "text": item.text,
                    "icon_name": item.icon_name,
                    "variant": item.variant,
                    "density": item.density,
                    "width_policy": item.width_policy,
                    "padding": item.padding,
                    "data_provider_id": item.data_provider_id,
                    "data_query_id": item.data_query_id,
                    "chart_mode": item.chart_mode,
                    "chart_style_id": item.chart_style_id,
                    "chart_palette_id": item.chart_palette_id,
                    "chart_show_grid": bool(item.chart_show_grid),
                    "chart_show_glow": bool(item.chart_show_glow),
                    "chart_show_markers": bool(item.chart_show_markers),
                    "chart_smooth": bool(item.chart_smooth),
                    "chart_line_width": int(item.chart_line_width),
                    "chart_fill_alpha": int(item.chart_fill_alpha),
                    "height_policy": item.height_policy,
                    "panel_height": int(item.panel_height),
                    "list_options": list(item.list_options),
                    "widget_props": normalize_widget_props(item.panel_type, item.widget_props),
                    "behavior": normalize_behavior_binding(item.behavior),
                    "dynamic": bool(item.dynamic),
                }
                for item in self.dynamic_working
            ],
            "split": {
                "main": int(self.split_working[0]),
                "side": int(self.split_working[1]),
            },
            "saved_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        }


class _LazyMountHost(QFrame):
    """Mounts heavy preview content only while active to keep tab budget bounded."""

    def __init__(self, title: str, factory, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._factory = factory
        self._mounted: QWidget | None = None
        self._title = str(title or "Workspace")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)
        self._placeholder = QLabel(
            "Inactive workspace tab.\nSelect this tab to mount live content.",
            self,
        )
        self._placeholder.setProperty("role", "panel_subtitle")
        self._placeholder.setWordWrap(True)
        self._layout.addWidget(self._placeholder)

    def is_mounted(self) -> bool:
        return self._mounted is not None

    def set_active(self, active: bool) -> None:
        if bool(active):
            self._mount_if_needed()
            return
        self._unmount()

    def _mount_if_needed(self) -> None:
        if self._mounted is not None:
            return
        widget = self._factory()
        if widget is None:
            return
        widget.setParent(self)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._layout.addWidget(widget, 1)
        self._mounted = widget
        self._placeholder.hide()

    def _unmount(self) -> None:
        if self._mounted is None:
            return
        mounted = self._mounted
        self._mounted = None
        self._layout.removeWidget(mounted)
        mounted.setParent(None)
        mounted.deleteLater()
        self._placeholder.show()

    def replace_factory(self, title: str, factory, *, remount_if_active: bool = True) -> None:
        self._title = str(title or self._title)
        self._factory = factory
        was_active = bool(self._mounted is not None)
        self._unmount()
        if remount_if_active and was_active:
            self._mount_if_needed()


@dataclass(slots=True)
class _PanelDragSession:
    context_id: str
    panel_id: str
    origin: QPoint
    active: bool = False
    last_target: tuple[str, int] | None = None


@dataclass(slots=True)
class _PanelResizeSession:
    context_id: str
    panel_id: str
    origin_y: int
    start_height: int
    min_height: int
    max_height: int
    active: bool = False


class _WindowEdgeGrip(QFrame):
    def __init__(self, host: QWidget, *, edges: Qt.Edge, cursor: Qt.CursorShape, parent: QWidget | None = None) -> None:
        super().__init__(parent or host)
        self._host = host
        self._edges = edges
        self._press_pos = QPoint(0, 0)
        self._press_geometry = QRect()
        self.setCursor(cursor)
        self.setMouseTracking(True)
        self.setStyleSheet("background: transparent;")

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton and not self._host.isMaximized():
            self._press_pos = event.globalPosition().toPoint()
            self._press_geometry = QRect(self._host.geometry())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if bool(event.buttons() & Qt.LeftButton) and not self._host.isMaximized():
            self._resize_from_delta(event.globalPosition().toPoint() - self._press_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def _resize_from_delta(self, delta: QPoint) -> None:
        rect = QRect(self._press_geometry)
        minimum = self._host.minimumSize()
        if bool(self._edges & Qt.LeftEdge):
            target = rect.left() + int(delta.x())
            max_left = rect.right() - minimum.width() + 1
            rect.setLeft(min(target, max_left))
        if bool(self._edges & Qt.RightEdge):
            target = rect.right() + int(delta.x())
            min_right = rect.left() + minimum.width() - 1
            rect.setRight(max(target, min_right))
        if bool(self._edges & Qt.TopEdge):
            target = rect.top() + int(delta.y())
            max_top = rect.bottom() - minimum.height() + 1
            rect.setTop(min(target, max_top))
        if bool(self._edges & Qt.BottomEdge):
            target = rect.bottom() + int(delta.y())
            min_bottom = rect.top() + minimum.height() - 1
            rect.setBottom(max(target, min_bottom))
        self._host.setGeometry(rect)


class _PendingCandidateOverlay(QFrame):
    """Ephemeral floating candidate with confirm/cancel actions."""

    def __init__(
        self,
        parent: QWidget,
        *,
        title: str,
        summary: str,
        on_confirm: Callable[[], None],
        on_cancel: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel
        self._dragging = False
        self._drag_offset = QPoint(0, 0)
        self.setObjectName("WorkbenchPendingCandidate")
        self.setProperty("card", "clear")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFrameShape(QFrame.NoFrame)
        self.setMouseTracking(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(4)

        heading = QLabel(str(title or "Pending Candidate"), self)
        heading.setProperty("role", "panel_title")
        heading.setWordWrap(True)
        root.addWidget(heading)

        detail = QLabel(str(summary or ""), self)
        detail.setProperty("role", "caption")
        detail.setWordWrap(True)
        root.addWidget(detail)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(6)
        confirm = QPushButton("Confirm", self)
        confirm.setProperty("variant", "primary")
        confirm.clicked.connect(self._on_confirm)
        cancel = QPushButton("Cancel", self)
        cancel.setProperty("variant", "subtle")
        cancel.clicked.connect(self._on_cancel)
        actions.addWidget(confirm)
        actions.addWidget(cancel)
        actions.addStretch(1)
        root.addLayout(actions)

    def _interactive_child(self, local_pos: QPoint) -> bool:
        child = self.childAt(local_pos)
        return isinstance(
            child,
            (QPushButton, QLineEdit, QTextEdit, QComboBox, QSlider, QCheckBox, QListWidget, QTabWidget, QTableWidget),
        )

    def _clamp_top_left(self, candidate: QPoint) -> QPoint:
        parent = self.parentWidget()
        if parent is None:
            return candidate
        bounds = parent.contentsRect().adjusted(2, 2, -2, -2)
        if bounds.width() <= 0 or bounds.height() <= 0:
            return candidate
        x = max(bounds.left(), min(bounds.right() - self.width() + 1, candidate.x()))
        y = max(bounds.top(), min(bounds.bottom() - self.height() + 1, candidate.y()))
        return QPoint(int(x), int(y))

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton and not self._interactive_child(event.position().toPoint()):
            self._dragging = True
            self._drag_offset = event.position().toPoint()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._dragging and bool(event.buttons() & Qt.LeftButton):
            top_left = self.mapToParent(event.position().toPoint() - self._drag_offset)
            self.move(self._clamp_top_left(top_left))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        self._dragging = False
        super().mouseReleaseEvent(event)


class _ChartPreviewCanvas(QWidget):
    """Lightweight chart painter for workbench composition previews."""

    def __init__(
        self,
        *,
        values: list[float],
        mode: str,
        style: GlassChartStyle,
        palette: GlassChartPalette,
        show_grid: bool,
        show_glow: bool,
        show_markers: bool,
        smooth: bool,
        line_width: int,
        fill_alpha: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._values = list(values)
        self._mode = str(mode or "line").strip().lower() or "line"
        self._style = style
        self._palette = palette
        self._show_grid = bool(show_grid)
        self._show_glow = bool(show_glow)
        self._show_markers = bool(show_markers)
        self._smooth = bool(smooth)
        self._line_width = max(1, min(8, int(line_width)))
        self._fill_alpha = max(0, min(70, int(fill_alpha)))
        self.setMinimumHeight(164)
        self.setObjectName("WorkbenchChartCanvas")

    def paintEvent(self, event) -> None:  # type: ignore[override]
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        panel_rect = QRectF(self.rect()).adjusted(6, 6, -6, -6)
        if panel_rect.width() < 20 or panel_rect.height() < 20:
            return

        colors = [QColor(token) for token in self._palette.colors if QColor(token).isValid()]
        if not colors:
            colors = [QColor("#e8edf4"), QColor("#cfd7e2"), QColor("#a9b4c3")]
        base = QColor(colors[0])
        base.setAlpha(38)
        bg_gradient = QLinearGradient(panel_rect.topLeft(), panel_rect.bottomLeft())
        top = QColor(base)
        top.setAlpha(max(12, int(base.alpha() * 0.76)))
        bottom = QColor(base)
        bottom.setAlpha(max(10, int(base.alpha() * 0.48)))
        bg_gradient.setColorAt(0.0, top)
        bg_gradient.setColorAt(1.0, bottom)
        painter.setPen(QPen(QColor(220, 233, 247, 42), 1.0))
        painter.setBrush(QBrush(bg_gradient))
        painter.drawRoundedRect(panel_rect, 12, 12)

        content_rect = QRectF(panel_rect).adjusted(12, 10, -12, -12)
        if content_rect.width() < 12 or content_rect.height() < 12:
            return
        if self._show_grid and self._mode != "spark":
            grid_pen = QPen(QColor(222, 236, 248, 28), 1.0)
            painter.setPen(grid_pen)
            for row in range(1, 4):
                y = content_rect.top() + (content_rect.height() * row / 4.0)
                painter.drawLine(QPointF(content_rect.left(), y), QPointF(content_rect.right(), y))

        values = self._values or [10, 13, 11, 15, 14, 18, 16, 19]
        v_min = min(values)
        v_max = max(values)
        spread = max(1.0, float(v_max - v_min))
        points: list[QPointF] = []
        if len(values) == 1:
            points.append(QPointF(content_rect.center().x(), content_rect.bottom()))
        else:
            for idx, value in enumerate(values):
                x_ratio = idx / max(1, len(values) - 1)
                y_ratio = (float(value) - float(v_min)) / spread
                x = content_rect.left() + x_ratio * content_rect.width()
                y = content_rect.bottom() - y_ratio * content_rect.height()
                points.append(QPointF(x, y))
        if not points:
            return

        line_color = QColor(colors[1] if len(colors) > 1 else colors[0])
        if not line_color.isValid():
            line_color = QColor("#d3dbe7")
        line_color.setAlpha(216)
        glow_color = QColor(line_color)
        glow_color.setAlpha(72)

        if self._mode == "bar":
            width = max(6.0, content_rect.width() / max(4, len(points) * 1.8))
            for idx, point in enumerate(points):
                bar_color = QColor(colors[idx % len(colors)])
                bar_color.setAlpha(180)
                rect = QRectF(
                    point.x() - width / 2.0,
                    point.y(),
                    width,
                    content_rect.bottom() - point.y(),
                )
                painter.setPen(Qt.NoPen)
                painter.setBrush(bar_color)
                painter.drawRoundedRect(rect, 4, 4)
            return

        path = QPainterPath(points[0])
        if self._smooth and len(points) > 2:
            for idx in range(1, len(points)):
                prev = points[idx - 1]
                curr = points[idx]
                mid_x = (prev.x() + curr.x()) / 2.0
                path.cubicTo(QPointF(mid_x, prev.y()), QPointF(mid_x, curr.y()), curr)
        else:
            for point in points[1:]:
                path.lineTo(point)

        if self._show_glow:
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(glow_color, float(self._line_width + 3)))
            painter.drawPath(path)

        if self._mode in {"area"}:
            area_path = QPainterPath(path)
            area_path.lineTo(QPointF(points[-1].x(), content_rect.bottom()))
            area_path.lineTo(QPointF(points[0].x(), content_rect.bottom()))
            area_path.closeSubpath()
            fill = QColor(line_color)
            fill.setAlpha(self._fill_alpha * 4)
            painter.setPen(Qt.NoPen)
            painter.setBrush(fill)
            painter.drawPath(area_path)

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(line_color, float(self._line_width)))
        painter.drawPath(path)

        if self._show_markers and self._mode != "spark":
            marker = QColor(colors[2] if len(colors) > 2 else line_color)
            marker.setAlpha(220)
            painter.setBrush(marker)
            painter.setPen(QPen(QColor(255, 255, 255, 140), 1.0))
            for point in points:
                painter.drawEllipse(point, 3.1, 3.1)


class GlassCatalogShell(QWidget):
    """
    Interactive framework workbench for pyside6_glass capabilities.

    The workbench keeps catalog browsing, live preview, data/provider inspection and
    runtime/integration diagnostics in one reusable examples-layer surface.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("GlassCatalogShell")
        register_builtin_catalog_entries()
        register_builtin_data_providers()
        register_builtin_chart_catalog()
        self._selected_entry_id: str | None = None
        self._entry_order: list[str] = []
        self._preview_instance_counter = 0
        self._workspace_counter = 0
        self._workspace_hosts: dict[str, _LazyMountHost] = {}
        self._workspace_active_budget = 1
        self._catalog_panel_visible = False
        self._inspector_panel_visible = False
        self._catalog_initialized = False
        self._inspector_initialized = False
        self._responsive_bucket = ""
        self._panel_click_map: dict[int, tuple[str, str]] = {}
        self._editor_sessions: dict[str, WorkbenchEditorSession] = {}
        self._editor_templates: dict[str, GlassPanelTemplate] = {}
        self._category_counts: dict[str, int] = {}
        self._category_tags: dict[str, tuple[str, ...]] = {}
        self._dashboard_specs_by_id: dict[str, DashboardCatalogEntrySpec] = {
            spec.entry_id: spec for spec in iter_dashboard_catalog_specs()
        }
        self._integration_contracts_cache: dict[str, Any] | None = None
        self._panel_type_registry = self._build_panel_type_registry()
        self._palette_recent: list[str] = []
        self._editor_policy = {
            "heavy_panels_per_tab": 3,
            "live_data_widgets_per_tab": 4,
            "max_panels_per_slot": {"main": 14, "side": 10, "status": 8},
        }
        self._editor_policy_messages: list[str] = []
        self._panel_drag_session: _PanelDragSession | None = None
        self._panel_resize_session: _PanelResizeSession | None = None
        self._picker_target_tab_id: str | None = None
        self._action_trace: list[dict[str, str]] = []
        self._action_trace_limit = 220
        self._status_autoclear_timer = QTimer(self)
        self._status_autoclear_timer.setSingleShot(True)
        self._status_autoclear_timer.timeout.connect(self._clear_status_feedback)
        base_size = self.font().pointSizeF()
        if base_size <= 0:
            base_size = float(max(9, self.font().pointSize() or 10))
        self._base_font_point_size = float(base_size)
        self._window_dragging = False
        self._window_drag_offset = QPoint(0, 0)
        self._window_resize_grips: list[_WindowEdgeGrip] = []
        self._window_resize_host: QWidget | None = None
        self._window_resize_grip_size = 8
        self._pending_candidate_overlay: _PendingCandidateOverlay | None = None
        self._pending_candidate_commit: Callable[[], bool] | None = None
        self._pending_candidate_context_id: str | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        base_config = get_template_preset("tabbed_workspace")
        tuned_config = replace(
            base_config,
            theme=replace(
                base_config.theme,
                theme_id="silver_frost_cyan",
                density="compact",
                visual_scale=replace(
                    base_config.theme.visual_scale,
                    border_strength_scale=0.78,
                    surface_opacity_scale=0.74,
                ),
                typography=replace(
                    base_config.theme.typography,
                    scale="lg",
                ),
            ),
            tabs=replace(base_config.tabs, density="compact", variant="segmented", icon_mode="icon_text"),
        )
        self._text_size = "lg"

        self.catalog = GlassPanelTemplate(
            self,
            config=tuned_config,
            title="Glass Workbench",
            subtitle=(
                "Interactive framework inspection workbench for catalog entries, "
                "providers, runtime and integration boundaries."
            ),
            eyebrow="WORKBENCH",
            include_default_actions=False,
            show_side=False,
            show_footer=False,
            show_status=True,
            with_chrome=False,
        )
        self._raw_catalog_set_status_text = self.catalog.set_status_text
        self.catalog.set_status_text = self._status_proxy  # type: ignore[method-assign]
        root.addWidget(self.catalog, 1)
        self.catalog.set_tab_density("compact")
        self.catalog.set_hide_single_tab_bar(False)
        self.catalog.set_split_proportions(main=100, side=0)
        self.catalog.set_panel_visible("side", False)
        self.catalog.set_status_text("Initializing workbench...")
        self._tune_template_density()
        self._build_catalog_ui()
        self._wire()
        self._on_scale_changed(self.scale_combo.currentIndex())
        self._set_catalog_panel_visible(False, initialize=False)
        self._set_inspector_panel_visible(False, initialize=False)
        self._set_preview_collapsed(True)
        self._enforce_workspace_budget()
        self._refresh_editor_contexts()
        self._set_status(
            "Blank workspace ready. Use Add / Browse or Ctrl+K to populate tabs."
        )
        self._refresh_action_trace_view()
        QTimer.singleShot(0, self._install_window_shell_interactions)

    def _infer_status_level(self, message: str) -> str:
        normalized = str(message or "").strip().lower()
        if not normalized:
            return "info"
        if any(token in normalized for token in ("failed", "error", "exception", "cannot", "invalid")):
            return "error"
        if any(token in normalized for token in ("warning", "stale", "deferred", "budget", "limit")):
            return "warning"
        if any(token in normalized for token in ("saved", "opened", "loaded", "created", "applied", "refreshed")):
            return "success"
        return "info"

    def _append_action_trace(
        self,
        *,
        action: str,
        level: str = "info",
        context: str = "workbench",
    ) -> None:
        timestamp = dt.datetime.now().strftime("%H:%M:%S")
        event = {
            "at": timestamp,
            "action": str(action or "").strip(),
            "level": str(level or "info").strip().lower() or "info",
            "context": str(context or "workbench").strip().lower() or "workbench",
        }
        self._action_trace.append(event)
        if len(self._action_trace) > int(self._action_trace_limit):
            self._action_trace = self._action_trace[-int(self._action_trace_limit) :]
        self._refresh_action_trace_view()

    def _refresh_action_trace_view(self) -> None:
        trace_box = getattr(self, "runtime_action_trace_text", None)
        if trace_box is None:
            return
        lines = [
            f"[{event.get('at', '?')}] {event.get('level', 'info').upper()} "
            f"[{event.get('context', 'workbench')}]: {event.get('action', '')}"
            for event in self._action_trace[-80:]
        ]
        trace_box.setPlainText("\n".join(lines) if lines else "No action trace events yet.")

    def _clear_status_feedback(self) -> None:
        self._raw_catalog_set_status_text("")

    def _set_status(
        self,
        text: str | None,
        *,
        level: str | None = None,
        context: str = "workbench",
        auto_clear_ms: int | None = None,
    ) -> None:
        message = str(text or "").strip()
        if not message:
            self._status_autoclear_timer.stop()
            self._raw_catalog_set_status_text("")
            return
        resolved_level = str(level or self._infer_status_level(message)).strip().lower() or "info"
        self._raw_catalog_set_status_text(message)
        self._append_action_trace(action=message, level=resolved_level, context=context)
        if resolved_level in {"error", "warning"}:
            self._status_autoclear_timer.stop()
            return
        ttl = int(auto_clear_ms) if auto_clear_ms is not None else (5200 if resolved_level == "success" else 3600)
        self._status_autoclear_timer.start(max(1200, ttl))

    def _status_proxy(self, text: str | None) -> None:
        self._set_status(text, context="catalog")

    def _build_catalog_ui(self) -> None:
        self.catalog.clear_slot("main")
        self.catalog.clear_slot("side")
        tools_bar = QFrame(self.catalog)
        tools_bar.setObjectName("WorkbenchToolbarCard")
        tools_bar.setProperty("card", "clear")
        tools_layout = QHBoxLayout(tools_bar)
        tools_layout.setContentsMargins(0, 0, 0, 0)
        tools_layout.setSpacing(2)
        self.tools_bar = tools_bar
        self.tools_layout = tools_layout

        self.btn_toggle_catalog = QPushButton("Catalog", tools_bar)
        self.btn_toggle_catalog.setCheckable(True)
        self.btn_toggle_inspector = QPushButton("Inspector", tools_bar)
        self.btn_toggle_inspector.setCheckable(True)
        self.btn_preview = QPushButton("Preview", tools_bar)
        self.btn_workspace = QPushButton("Open Tab", tools_bar)
        self.btn_new_workspace = QPushButton("New Tab", tools_bar)
        self.btn_close_workspace = QPushButton("Close Tab", tools_bar)
        self.btn_clear_preview = QPushButton("Clear Preview", tools_bar)
        self.btn_clear_filters = QPushButton("Clear Filters", tools_bar)
        self.btn_toggle_motion = QPushButton("Motion", tools_bar)
        self.btn_browse_content = QPushButton("Add / Browse", tools_bar)
        self.btn_new_tab_primary = QPushButton("New Tab", tools_bar)
        self.btn_tools = QPushButton("Tools", tools_bar)
        self.btn_close_tab_primary = QPushButton("Close Tab", tools_bar)
        self.btn_quick_search = QPushButton("Quick Search", tools_bar)

        self.btn_toggle_catalog.setProperty("commandRole", "toggle")
        self.btn_toggle_inspector.setProperty("commandRole", "toggle")
        self.btn_preview.setProperty("commandRole", "primary")
        self.btn_workspace.setProperty("commandRole", "primary")
        self.btn_new_workspace.setProperty("commandRole", "primary")
        self.btn_close_workspace.setProperty("commandRole", "secondary")
        self.btn_clear_preview.setProperty("commandRole", "secondary")
        self.btn_clear_filters.setProperty("commandRole", "secondary")
        self.btn_toggle_motion.setProperty("commandRole", "secondary")
        self.btn_preview.setProperty("variant", "primary")
        self.btn_workspace.setProperty("variant", "primary")
        self.btn_new_workspace.setProperty("variant", "secondary")
        self.btn_close_workspace.setProperty("variant", "subtle")
        self.btn_clear_preview.setProperty("variant", "subtle")
        self.btn_clear_filters.setProperty("variant", "subtle")
        self.btn_toggle_motion.setProperty("variant", "ghost")
        self.btn_browse_content.setProperty("variant", "primary")
        self.btn_new_tab_primary.setProperty("variant", "secondary")
        self.btn_tools.setProperty("variant", "ghost")
        self.btn_close_tab_primary.setProperty("variant", "subtle")
        self.btn_quick_search.setProperty("variant", "ghost")

        self.scale_combo = QComboBox(tools_bar)
        self.scale_combo.addItem("SM", "sm")
        self.scale_combo.addItem("MD", "md")
        self.scale_combo.addItem("LG", "lg")
        self.scale_combo.addItem("XL", "xl")
        self.scale_combo.setCurrentIndex(2)
        self.scale_combo.setToolTip("Text Size")

        def _separator() -> QFrame:
            line = QFrame(tools_bar)
            line.setFrameShape(QFrame.VLine)
            line.setProperty("workbenchSep", True)
            line.setFixedWidth(1)
            return line

        self.btn_toggle_catalog.hide()
        self.btn_toggle_inspector.hide()
        self.btn_preview.hide()
        self.btn_workspace.hide()
        self.btn_new_workspace.hide()
        self.btn_close_workspace.hide()
        self.btn_clear_preview.hide()
        self.btn_clear_filters.hide()
        self.btn_toggle_motion.hide()

        tools_layout.addWidget(self.btn_browse_content)
        tools_layout.addWidget(self.btn_new_tab_primary)
        tools_layout.addWidget(self.btn_close_tab_primary)
        tools_layout.addWidget(_separator())
        tools_layout.addWidget(self.btn_quick_search)
        tools_layout.addWidget(self.btn_tools)
        tools_layout.addStretch(1)
        scale_label = QLabel("Text Size", tools_bar)
        scale_label.setProperty("role", "caption")
        self.scale_label = scale_label
        tools_layout.addWidget(scale_label)
        tools_layout.addWidget(self.scale_combo)
        shell_layout = self.catalog.cards.shell.layout()
        if isinstance(shell_layout, QVBoxLayout):
            shell_layout.insertWidget(1, tools_bar)

        split = QSplitter(Qt.Horizontal, self.catalog)
        split.setObjectName("WorkbenchMainSplitter")
        split.setChildrenCollapsible(False)
        split.setHandleWidth(3)
        split.setStretchFactor(0, 2)
        split.setStretchFactor(1, 6)
        split.setStretchFactor(2, 3)

        left = QFrame(split)
        left.setObjectName("WorkbenchNavRail")
        left.setProperty("card", "clear")
        self.catalog_browser_frame = left
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(2)

        self.search_input = QLineEdit(left)
        self.search_input.setPlaceholderText("Search by title, tags, preset, theme, keyword...")
        self.search_input.setClearButtonEnabled(True)
        left_layout.addWidget(self.search_input)
        self.tags_input = QLineEdit(left)
        self.tags_input.setPlaceholderText("Tag filter: dashboard,provider")
        self.tags_input.setClearButtonEnabled(True)
        left_layout.addWidget(self.tags_input)

        category_label = QLabel("Categories", left)
        category_label.setProperty("role", "panel_title")
        left_layout.addWidget(category_label)
        self.category_list = QListWidget(left)
        self.category_list.setObjectName("GlassCatalogCategories")
        left_layout.addWidget(self.category_list, 1)

        entries_label = QLabel("Entries", left)
        entries_label.setProperty("role", "panel_title")
        left_layout.addWidget(entries_label)
        self.entry_list = QListWidget(left)
        self.entry_list.setObjectName("GlassCatalogEntries")
        left_layout.addWidget(self.entry_list, 3)

        center = QFrame(split)
        center.setObjectName("WorkbenchCenterSurface")
        center.setProperty("card", "clear")
        self.workspace_center_frame = center
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(2)

        self.preview_title = QLabel("Blank Editor Workspace", center)
        self.preview_title.setProperty("role", "section")
        self.preview_subtitle = QLabel(
            "Blank by design. Add content only when needed.",
            center,
        )
        self.preview_subtitle.setProperty("role", "caption")
        self.preview_subtitle.setWordWrap(True)
        center_layout.addWidget(self.preview_title)
        center_layout.addWidget(self.preview_subtitle)

        self.blank_workspace_hint = QLabel(
            "Use Add / Browse (Ctrl+K) to start.",
            center,
        )
        self.blank_workspace_hint.setProperty("role", "panel_subtitle")
        self.blank_workspace_hint.setWordWrap(True)
        center_layout.addWidget(self.blank_workspace_hint)

        self.blank_workspace_actions = QWidget(center)
        blank_actions_layout = QHBoxLayout(self.blank_workspace_actions)
        blank_actions_layout.setContentsMargins(0, 0, 0, 0)
        blank_actions_layout.setSpacing(6)
        self.btn_blank_add = QPushButton("Add Content", self.blank_workspace_actions)
        self.btn_blank_add.setProperty("variant", "primary")
        self.btn_blank_new_tab = QPushButton("New Workspace Tab", self.blank_workspace_actions)
        self.btn_blank_new_tab.setProperty("variant", "secondary")
        self.btn_blank_tools = QPushButton("Open Tools", self.blank_workspace_actions)
        self.btn_blank_tools.setProperty("variant", "ghost")
        blank_actions_layout.addWidget(self.btn_blank_add)
        blank_actions_layout.addWidget(self.btn_blank_new_tab)
        blank_actions_layout.addWidget(self.btn_blank_tools)
        blank_actions_layout.addStretch(1)
        center_layout.addWidget(self.blank_workspace_actions)

        self.preview_scroll = QScrollArea(center)
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setObjectName("WorkbenchPreviewScroll")
        self.preview_host = QFrame(self.preview_scroll)
        self.preview_host.setObjectName("WorkbenchPreviewHost")
        self.preview_host.setProperty("card", "clear")
        self.preview_layout = QVBoxLayout(self.preview_host)
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_layout.setSpacing(4)
        self.preview_placeholder = QLabel(
            "Preview is idle. Select content in the picker to preview and add it.",
            self.preview_host,
        )
        self.preview_placeholder.setProperty("role", "panel_subtitle")
        self.preview_placeholder.setWordWrap(True)
        self.preview_layout.addWidget(self.preview_placeholder)
        self.preview_scroll.setWidget(self.preview_host)
        center_layout.addWidget(self.preview_scroll, 1)
        self.preview_scroll.hide()

        inspector = QFrame(split)
        inspector.setObjectName("WorkbenchInspectorSurface")
        inspector.setProperty("card", "clear")
        self.inspector_frame = inspector
        inspector_layout = QVBoxLayout(inspector)
        inspector_layout.setContentsMargins(0, 0, 0, 0)
        inspector_layout.setSpacing(2)
        self.side_tabs = QTabWidget(inspector)
        self.side_tabs.setObjectName("WorkbenchInspectorTabs")
        inspector_layout.addWidget(self.side_tabs, 1)

        entry_tab = QWidget(self.side_tabs)
        entry_layout = QVBoxLayout(entry_tab)
        entry_layout.setContentsMargins(0, 0, 0, 0)
        entry_layout.setSpacing(8)

        self.meta_title = QLabel("Entry Details", entry_tab)
        self.meta_title.setProperty("role", "panel_title")
        entry_layout.addWidget(self.meta_title)
        self.meta_summary = QLabel("No entry selected.", entry_tab)
        self.meta_summary.setProperty("role", "panel_subtitle")
        self.meta_summary.setWordWrap(True)
        entry_layout.addWidget(self.meta_summary)

        self.entry_summary_card = QFrame(entry_tab)
        self.entry_summary_card.setObjectName("WorkbenchEntrySummaryCard")
        self.entry_summary_card.setProperty("card", "clear")
        summary_layout = QFormLayout(self.entry_summary_card)
        summary_layout.setContentsMargins(8, 8, 8, 8)
        summary_layout.setHorizontalSpacing(10)
        summary_layout.setVerticalSpacing(6)
        self.meta_kind_value = QLabel("-", self.entry_summary_card)
        self.meta_origin_value = QLabel("-", self.entry_summary_card)
        self.meta_layer_value = QLabel("-", self.entry_summary_card)
        self.meta_builder_value = QLabel("-", self.entry_summary_card)
        self.meta_builder_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.meta_hint_value = QLabel("-", self.entry_summary_card)
        self.meta_cap_value = QLabel("-", self.entry_summary_card)
        self.meta_best_for_value = QLabel("-", self.entry_summary_card)
        self.meta_best_for_value.setWordWrap(True)
        summary_layout.addRow("Kind", self.meta_kind_value)
        summary_layout.addRow("Origin", self.meta_origin_value)
        summary_layout.addRow("Layer", self.meta_layer_value)
        summary_layout.addRow("Builder", self.meta_builder_value)
        summary_layout.addRow("Preset/Theme", self.meta_hint_value)
        summary_layout.addRow("Capabilities", self.meta_cap_value)
        summary_layout.addRow("Best For", self.meta_best_for_value)
        entry_layout.addWidget(self.entry_summary_card)

        self.meta_use_when = QLabel("", entry_tab)
        self.meta_use_when.setProperty("role", "caption")
        self.meta_use_when.setWordWrap(True)
        self.meta_use_when.setVisible(False)
        entry_layout.addWidget(self.meta_use_when)
        self.meta_tags = QLabel("", entry_tab)
        self.meta_tags.setProperty("role", "caption")
        self.meta_tags.setWordWrap(True)
        self.meta_tags.setVisible(False)
        entry_layout.addWidget(self.meta_tags)

        self.related_title = QLabel("See Also", entry_tab)
        self.related_title.setProperty("role", "panel_title")
        entry_layout.addWidget(self.related_title)
        self.related_list = QListWidget(entry_tab)
        self.related_list.setObjectName("GlassCatalogRelated")
        entry_layout.addWidget(self.related_list, 1)

        self.btn_toggle_entry_json = QPushButton("Toggle Raw Metadata", entry_tab)
        entry_layout.addWidget(self.btn_toggle_entry_json)
        self.meta_text = QTextEdit(entry_tab)
        self.meta_text.setReadOnly(True)
        self.meta_text.setPlaceholderText("Structured metadata debug view.")
        self.meta_text.setVisible(False)
        entry_layout.addWidget(self.meta_text, 1)
        self.side_tabs.addTab(entry_tab, "Entry")

        data_tab = QWidget(self.side_tabs)
        data_layout = QVBoxLayout(data_tab)
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.setSpacing(8)
        data_title = QLabel("Data & Provider Inspection", data_tab)
        data_title.setProperty("role", "panel_title")
        data_layout.addWidget(data_title)
        self.data_binding_summary = QLabel("Select a provider-backed entry for query/provider diagnostics.", data_tab)
        self.data_binding_summary.setProperty("role", "panel_subtitle")
        self.data_binding_summary.setWordWrap(True)
        data_layout.addWidget(self.data_binding_summary)

        data_actions = QHBoxLayout()
        data_actions.setContentsMargins(0, 0, 0, 0)
        data_actions.setSpacing(8)
        self.btn_probe_query = QPushButton("Probe Selected Query", data_tab)
        self.btn_refresh_providers = QPushButton("Refresh Providers", data_tab)
        self.btn_toggle_data_json = QPushButton("Toggle Raw Data", data_tab)
        data_actions.addWidget(self.btn_probe_query)
        data_actions.addWidget(self.btn_refresh_providers)
        data_actions.addWidget(self.btn_toggle_data_json)
        data_layout.addLayout(data_actions)

        self.selected_data_binding = QTextEdit(data_tab)
        self.selected_data_binding.setReadOnly(True)
        self.selected_data_binding.setPlaceholderText("Provider/query binding details.")
        self.selected_data_binding.setVisible(False)
        data_layout.addWidget(self.selected_data_binding, 1)

        self.query_probe_text = QTextEdit(data_tab)
        self.query_probe_text.setReadOnly(True)
        self.query_probe_text.setPlaceholderText("Query probe output and data state summary.")
        self.query_probe_text.setVisible(False)
        data_layout.addWidget(self.query_probe_text, 1)

        providers_label = QLabel("Registered Providers", data_tab)
        providers_label.setProperty("role", "panel_title")
        data_layout.addWidget(providers_label)
        self.provider_list = QListWidget(data_tab)
        self.provider_list.setObjectName("GlassCatalogProviders")
        data_layout.addWidget(self.provider_list, 1)
        self.provider_summary = QLabel("Select a provider to inspect metadata.", data_tab)
        self.provider_summary.setProperty("role", "panel_subtitle")
        self.provider_summary.setWordWrap(True)
        data_layout.addWidget(self.provider_summary)
        self.provider_details = QTextEdit(data_tab)
        self.provider_details.setReadOnly(True)
        self.provider_details.setPlaceholderText("Raw provider metadata and diagnostics.")
        self.provider_details.setVisible(False)
        data_layout.addWidget(self.provider_details, 1)
        self.side_tabs.addTab(data_tab, "Data")

        runtime_tab = QWidget(self.side_tabs)
        runtime_layout = QVBoxLayout(runtime_tab)
        runtime_layout.setContentsMargins(0, 0, 0, 0)
        runtime_layout.setSpacing(8)
        runtime_title = QLabel("Architecture & Runtime Inspection", runtime_tab)
        runtime_title.setProperty("role", "panel_title")
        runtime_layout.addWidget(runtime_title)

        self.architecture_boundaries_text = QTextEdit(runtime_tab)
        self.architecture_boundaries_text.setReadOnly(True)
        self.architecture_boundaries_text.setPlainText(self._architecture_boundaries_note())
        runtime_layout.addWidget(self.architecture_boundaries_text)

        runtime_actions = QHBoxLayout()
        runtime_actions.setContentsMargins(0, 0, 0, 0)
        runtime_actions.setSpacing(8)
        self.btn_refresh_runtime = QPushButton("Refresh Runtime Diagnostics", runtime_tab)
        self.btn_toggle_runtime_json = QPushButton("Toggle Raw Runtime", runtime_tab)
        self.btn_toggle_action_trace = QPushButton("Toggle Action Trace", runtime_tab)
        runtime_actions.addWidget(self.btn_refresh_runtime)
        runtime_actions.addWidget(self.btn_toggle_runtime_json)
        runtime_actions.addWidget(self.btn_toggle_action_trace)
        runtime_layout.addLayout(runtime_actions)

        self.runtime_summary = QLabel("Runtime diagnostics are available for the selected entry.", runtime_tab)
        self.runtime_summary.setProperty("role", "panel_subtitle")
        self.runtime_summary.setWordWrap(True)
        runtime_layout.addWidget(self.runtime_summary)
        self.runtime_action_trace_text = QTextEdit(runtime_tab)
        self.runtime_action_trace_text.setReadOnly(True)
        self.runtime_action_trace_text.setPlaceholderText("Recent action timeline (status, edits, probes, tab events).")
        self.runtime_action_trace_text.setVisible(False)
        self.runtime_action_trace_text.setMaximumHeight(160)
        runtime_layout.addWidget(self.runtime_action_trace_text)
        self.runtime_diagnostics_text = QTextEdit(runtime_tab)
        self.runtime_diagnostics_text.setReadOnly(True)
        self.runtime_diagnostics_text.setPlaceholderText(
            "Catalog/workbench summary, provider diagnostics, integration endpoints."
        )
        self.runtime_diagnostics_text.setVisible(False)
        runtime_layout.addWidget(self.runtime_diagnostics_text, 1)
        self.side_tabs.addTab(runtime_tab, "Runtime")

        compose_tab = QWidget(self.side_tabs)
        compose_layout = QVBoxLayout(compose_tab)
        compose_layout.setContentsMargins(0, 0, 0, 0)
        compose_layout.setSpacing(8)
        compose_title = QLabel("Interactive Layout Composer", compose_tab)
        compose_title.setProperty("role", "panel_title")
        compose_layout.addWidget(compose_title)

        self.editor_status = QLabel(
            "Open a preview to start interactive editing. Original examples remain pristine until Save Clone.",
            compose_tab,
        )
        self.editor_status.setProperty("role", "panel_subtitle")
        self.editor_status.setWordWrap(True)
        compose_layout.addWidget(self.editor_status)

        context_form = QFormLayout()
        context_form.setContentsMargins(0, 0, 0, 0)
        context_form.setHorizontalSpacing(10)
        context_form.setVerticalSpacing(6)
        self.editor_context_combo = QComboBox(compose_tab)
        self.editor_context_combo.setToolTip("Editable context (preview or active workspace tab)")
        self.editor_source_value = QLabel("(none)", compose_tab)
        self.editor_source_value.setProperty("role", "caption")
        self.editor_dirty_value = QLabel("clean", compose_tab)
        self.editor_dirty_value.setProperty("role", "caption")
        context_form.addRow("Context", self.editor_context_combo)
        context_form.addRow("Source", self.editor_source_value)
        context_form.addRow("State", self.editor_dirty_value)
        compose_layout.addLayout(context_form)

        self.editor_panel_combo = QComboBox(compose_tab)
        self.editor_panel_combo.setToolTip("Selected panel")
        self.editor_panel_type_combo = QComboBox(compose_tab)
        self.editor_slot_combo = QComboBox(compose_tab)
        self.editor_slot_combo.addItems(["main", "side", "status"])
        self.editor_role_combo = QComboBox(compose_tab)
        self.editor_role_combo.addItems(["workspace", "detail", "form", "data", "metrics", "inspector", "aux"])
        self.editor_state_combo = QComboBox(compose_tab)
        self.editor_state_combo.addItems(["visible", "hold", "background", "disabled", "hidden"])
        self.editor_visible_check = QCheckBox("Visible", compose_tab)
        self.editor_visible_check.setChecked(True)
        self.editor_title_input = QLineEdit(compose_tab)
        self.editor_subtitle_input = QLineEdit(compose_tab)
        self.editor_icon_input = QLineEdit(compose_tab)
        self.editor_icon_input.setPlaceholderText("icon name (e.g. layers)")
        self.editor_text_input = QTextEdit(compose_tab)
        self.editor_text_input.setPlaceholderText("Panel text/content seed")
        self.editor_text_input.setMaximumHeight(88)
        self.editor_variant_combo = QComboBox(compose_tab)
        self.editor_variant_combo.addItems(["default", "muted", "accent", "warning", "success"])
        self.editor_density_combo = QComboBox(compose_tab)
        self.editor_density_combo.addItems(["compact", "cozy", "comfortable"])
        self.editor_width_policy_combo = QComboBox(compose_tab)
        self.editor_width_policy_combo.addItems(["stretch", "fit", "fixed"])
        self.editor_padding_combo = QComboBox(compose_tab)
        self.editor_padding_combo.addItems(["none", "tight", "normal", "relaxed"])
        self.editor_height_policy_combo = QComboBox(compose_tab)
        self.editor_height_policy_combo.addItems(["auto", "fixed"])
        self.editor_height_slider = QSlider(Qt.Horizontal, compose_tab)
        self.editor_height_slider.setRange(96, 760)
        self.editor_height_slider.setValue(240)
        self.editor_chart_mode_combo = QComboBox(compose_tab)
        self.editor_chart_mode_combo.addItems(["line", "bar", "area", "spark"])
        self.editor_chart_style_combo = QComboBox(compose_tab)
        self.editor_chart_palette_combo = QComboBox(compose_tab)
        self.editor_chart_grid_check = QCheckBox("Grid", compose_tab)
        self.editor_chart_grid_check.setChecked(True)
        self.editor_chart_glow_check = QCheckBox("Glow", compose_tab)
        self.editor_chart_glow_check.setChecked(True)
        self.editor_chart_markers_check = QCheckBox("Markers", compose_tab)
        self.editor_chart_smooth_check = QCheckBox("Smooth", compose_tab)
        self.editor_chart_smooth_check.setChecked(True)
        self.editor_chart_line_slider = QSlider(Qt.Horizontal, compose_tab)
        self.editor_chart_line_slider.setRange(1, 6)
        self.editor_chart_line_slider.setValue(2)
        self.editor_chart_fill_slider = QSlider(Qt.Horizontal, compose_tab)
        self.editor_chart_fill_slider.setRange(0, 60)
        self.editor_chart_fill_slider.setValue(26)
        self.editor_provider_combo = QComboBox(compose_tab)
        self.editor_query_input = QLineEdit(compose_tab)
        self.editor_query_input.setPlaceholderText("query id (optional)")
        self.editor_options_input = QLineEdit(compose_tab)
        self.editor_options_input.setPlaceholderText("options csv (list/dropdown/chips)")
        self.editor_widget_object_name_input = QLineEdit(compose_tab)
        self.editor_widget_object_name_input.setPlaceholderText("button_object_name")
        self.editor_widget_tooltip_input = QLineEdit(compose_tab)
        self.editor_widget_tooltip_input.setPlaceholderText("Tooltip")
        self.editor_widget_enabled_check = QCheckBox("Enabled", compose_tab)
        self.editor_widget_enabled_check.setChecked(True)
        self.editor_button_text_input = QLineEdit(compose_tab)
        self.editor_button_text_input.setPlaceholderText("Button label")
        self.editor_button_icon_input = QLineEdit(compose_tab)
        self.editor_button_icon_input.setPlaceholderText("icon name")
        self.editor_button_checkable_check = QCheckBox("Checkable", compose_tab)
        self.editor_button_checked_check = QCheckBox("Checked", compose_tab)
        self.editor_button_style_variant_combo = QComboBox(compose_tab)
        self.editor_button_style_variant_combo.addItems(["default", "primary", "secondary", "subtle", "ghost", "danger"])
        self.editor_behavior_action_type_combo = QComboBox(compose_tab)
        self.editor_behavior_action_type_combo.addItems(["none", "command", "open_panel", "task", "navigate", "custom"])
        self.editor_behavior_command_id_input = QLineEdit(compose_tab)
        self.editor_behavior_command_id_input.setPlaceholderText("refresh.metrics")
        self.editor_behavior_target_panel_input = QLineEdit(compose_tab)
        self.editor_behavior_target_panel_input.setPlaceholderText("dyn_001")
        self.editor_behavior_task_ref_input = QLineEdit(compose_tab)
        self.editor_behavior_task_ref_input.setPlaceholderText("task://ops/check")
        self.editor_behavior_payload_input = QTextEdit(compose_tab)
        self.editor_behavior_payload_input.setPlaceholderText("{\"arg\": \"value\"}")
        self.editor_behavior_payload_input.setMaximumHeight(74)

        height_row = QWidget(compose_tab)
        height_row_layout = QHBoxLayout(height_row)
        height_row_layout.setContentsMargins(0, 0, 0, 0)
        height_row_layout.setSpacing(6)
        height_row_layout.addWidget(self.editor_height_policy_combo)
        height_row_layout.addWidget(self.editor_height_slider, 1)

        chart_style_row = QWidget(compose_tab)
        chart_style_layout = QHBoxLayout(chart_style_row)
        chart_style_layout.setContentsMargins(0, 0, 0, 0)
        chart_style_layout.setSpacing(6)
        chart_style_layout.addWidget(self.editor_chart_style_combo, 2)
        chart_style_layout.addWidget(self.editor_chart_palette_combo, 1)

        chart_effect_row = QWidget(compose_tab)
        chart_effect_layout = QHBoxLayout(chart_effect_row)
        chart_effect_layout.setContentsMargins(0, 0, 0, 0)
        chart_effect_layout.setSpacing(6)
        chart_effect_layout.addWidget(self.editor_chart_grid_check)
        chart_effect_layout.addWidget(self.editor_chart_glow_check)
        chart_effect_layout.addWidget(self.editor_chart_markers_check)
        chart_effect_layout.addWidget(self.editor_chart_smooth_check)
        chart_effect_layout.addStretch(1)

        chart_tune_row = QWidget(compose_tab)
        chart_tune_layout = QHBoxLayout(chart_tune_row)
        chart_tune_layout.setContentsMargins(0, 0, 0, 0)
        chart_tune_layout.setSpacing(6)
        chart_tune_layout.addWidget(QLabel("Stroke", compose_tab))
        chart_tune_layout.addWidget(self.editor_chart_line_slider, 1)
        chart_tune_layout.addWidget(QLabel("Fill", compose_tab))
        chart_tune_layout.addWidget(self.editor_chart_fill_slider, 1)

        panel_form = QFormLayout()
        panel_form.setContentsMargins(0, 0, 0, 0)
        panel_form.setHorizontalSpacing(10)
        panel_form.setVerticalSpacing(6)
        panel_form.addRow("Panel", self.editor_panel_combo)
        panel_form.addRow("Type", self.editor_panel_type_combo)
        panel_form.addRow("Slot", self.editor_slot_combo)
        panel_form.addRow("Role", self.editor_role_combo)
        panel_form.addRow("State", self.editor_state_combo)
        panel_form.addRow("Title", self.editor_title_input)
        panel_form.addRow("Subtitle", self.editor_subtitle_input)
        panel_form.addRow("Icon", self.editor_icon_input)
        panel_form.addRow("Variant", self.editor_variant_combo)
        panel_form.addRow("Density", self.editor_density_combo)
        panel_form.addRow("Width", self.editor_width_policy_combo)
        panel_form.addRow("Padding", self.editor_padding_combo)
        panel_form.addRow("Height", height_row)
        panel_form.addRow("Chart", self.editor_chart_mode_combo)
        panel_form.addRow("Chart Style", chart_style_row)
        panel_form.addRow("Chart Effects", chart_effect_row)
        panel_form.addRow("Chart Tune", chart_tune_row)
        panel_form.addRow("Provider", self.editor_provider_combo)
        panel_form.addRow("Query", self.editor_query_input)
        panel_form.addRow("Options", self.editor_options_input)
        panel_form.addRow("Widget Name", self.editor_widget_object_name_input)
        panel_form.addRow("Widget Tooltip", self.editor_widget_tooltip_input)
        panel_form.addRow("Widget Enabled", self.editor_widget_enabled_check)
        panel_form.addRow("Button Text", self.editor_button_text_input)
        panel_form.addRow("Button Icon", self.editor_button_icon_input)
        panel_form.addRow("Button Checkable", self.editor_button_checkable_check)
        panel_form.addRow("Button Checked", self.editor_button_checked_check)
        panel_form.addRow("Button Style", self.editor_button_style_variant_combo)
        panel_form.addRow("Behavior Action", self.editor_behavior_action_type_combo)
        panel_form.addRow("Behavior Command", self.editor_behavior_command_id_input)
        panel_form.addRow("Behavior Target", self.editor_behavior_target_panel_input)
        panel_form.addRow("Behavior Task Ref", self.editor_behavior_task_ref_input)
        panel_form.addRow("Behavior Payload", self.editor_behavior_payload_input)
        panel_form.addRow("Visible", self.editor_visible_check)
        panel_form.addRow("Content", self.editor_text_input)
        compose_layout.addLayout(panel_form)

        split_row = QHBoxLayout()
        split_row.setContentsMargins(0, 0, 0, 0)
        split_row.setSpacing(8)
        self.editor_main_slider = QSlider(Qt.Horizontal, compose_tab)
        self.editor_main_slider.setRange(20, 80)
        self.editor_main_slider.setValue(68)
        self.editor_side_slider = QSlider(Qt.Horizontal, compose_tab)
        self.editor_side_slider.setRange(20, 80)
        self.editor_side_slider.setValue(32)
        self.editor_apply_split = QPushButton("Apply Split", compose_tab)
        split_row.addWidget(QLabel("Main", compose_tab))
        split_row.addWidget(self.editor_main_slider, 1)
        split_row.addWidget(QLabel("Side", compose_tab))
        split_row.addWidget(self.editor_side_slider, 1)
        split_row.addWidget(self.editor_apply_split)
        compose_layout.addLayout(split_row)

        palette_card = QFrame(compose_tab)
        palette_card.setProperty("card", "clear")
        palette_layout = QVBoxLayout(palette_card)
        palette_layout.setContentsMargins(2, 2, 2, 2)
        palette_layout.setSpacing(4)
        palette_title = QLabel("Insert Palette", palette_card)
        palette_title.setProperty("role", "panel_title")
        palette_layout.addWidget(palette_title)

        palette_filter_row = QHBoxLayout()
        palette_filter_row.setContentsMargins(0, 0, 0, 0)
        palette_filter_row.setSpacing(6)
        self.editor_palette_search = QLineEdit(palette_card)
        self.editor_palette_search.setPlaceholderText("Search object type, category, tags...")
        self.editor_palette_category_combo = QComboBox(palette_card)
        self.editor_palette_category_combo.addItem("all", "all")
        palette_filter_row.addWidget(self.editor_palette_search, 1)
        palette_filter_row.addWidget(self.editor_palette_category_combo)
        palette_layout.addLayout(palette_filter_row)

        self.editor_palette_list = QListWidget(palette_card)
        self.editor_palette_list.setObjectName("WorkbenchInsertPalette")
        palette_layout.addWidget(self.editor_palette_list, 1)

        self.editor_palette_summary = QLabel("Select an object type to inspect insertion hints.", palette_card)
        self.editor_palette_summary.setProperty("role", "caption")
        self.editor_palette_summary.setWordWrap(True)
        palette_layout.addWidget(self.editor_palette_summary)

        insert_row = QHBoxLayout()
        insert_row.setContentsMargins(0, 0, 0, 0)
        insert_row.setSpacing(6)
        self.editor_insert_target_combo = QComboBox(palette_card)
        self.editor_insert_target_combo.addItems(["main", "side", "status", "auto"])
        self.editor_insert_position_combo = QComboBox(palette_card)
        self.editor_insert_position_combo.addItems(["append", "before selected", "after selected"])
        self.editor_add_type_combo = QComboBox(palette_card)
        self.editor_add_slot_combo = QComboBox(palette_card)
        self.editor_add_slot_combo.addItems(["main", "side", "status"])
        self.editor_add_button = QPushButton("Insert Object", palette_card)
        insert_row.addWidget(self.editor_insert_target_combo)
        insert_row.addWidget(self.editor_insert_position_combo)
        insert_row.addWidget(self.editor_add_type_combo, 1)
        insert_row.addWidget(self.editor_add_slot_combo)
        insert_row.addWidget(self.editor_add_button)
        palette_layout.addLayout(insert_row)
        compose_layout.addWidget(palette_card, 1)

        actions_row = QHBoxLayout()
        actions_row.setContentsMargins(0, 0, 0, 0)
        actions_row.setSpacing(8)
        self.editor_apply_button = QPushButton("Apply Properties", compose_tab)
        self.editor_move_up_button = QPushButton("Move Up", compose_tab)
        self.editor_move_down_button = QPushButton("Move Down", compose_tab)
        self.editor_move_left_button = QPushButton("Move Left", compose_tab)
        self.editor_move_right_button = QPushButton("Move Right", compose_tab)
        self.editor_duplicate_button = QPushButton("Duplicate", compose_tab)
        self.editor_hide_button = QPushButton("Hide Panel", compose_tab)
        self.editor_reopen_button = QPushButton("Reopen Hidden", compose_tab)
        self.editor_remove_button = QPushButton("Remove Panel", compose_tab)
        self.editor_apply_button.setProperty("variant", "primary")
        self.editor_duplicate_button.setProperty("variant", "secondary")
        self.editor_hide_button.setProperty("variant", "subtle")
        self.editor_reopen_button.setProperty("variant", "ghost")
        self.editor_remove_button.setProperty("variant", "danger")
        self.editor_remove_button.setProperty("editorAction", "danger")
        actions_row.addWidget(self.editor_apply_button)
        actions_row.addWidget(self.editor_move_up_button)
        actions_row.addWidget(self.editor_move_down_button)
        actions_row.addWidget(self.editor_move_left_button)
        actions_row.addWidget(self.editor_move_right_button)
        actions_row.addWidget(self.editor_duplicate_button)
        actions_row.addWidget(self.editor_hide_button)
        actions_row.addWidget(self.editor_reopen_button)
        actions_row.addWidget(self.editor_remove_button)
        compose_layout.addLayout(actions_row)

        self.editor_policy_label = QLabel(
            "Policies: active tab only, heavy budget per tab, inactive heavy widgets deferred/paused.",
            compose_tab,
        )
        self.editor_policy_label.setProperty("role", "caption")
        self.editor_policy_label.setWordWrap(True)
        compose_layout.addWidget(self.editor_policy_label)
        self.editor_interaction_hint = QLabel(
            "Direct manipulation: drag panel from top band, resize from bottom edge (cursor changes to vertical resize).",
            compose_tab,
        )
        self.editor_interaction_hint.setProperty("role", "caption")
        self.editor_interaction_hint.setWordWrap(True)
        compose_layout.addWidget(self.editor_interaction_hint)

        self.editor_hidden_summary = QLabel("Hidden panels: 0", compose_tab)
        self.editor_hidden_summary.setProperty("role", "caption")
        self.editor_hidden_summary.setWordWrap(True)
        compose_layout.addWidget(self.editor_hidden_summary)

        persistence_row = QHBoxLayout()
        persistence_row.setContentsMargins(0, 0, 0, 0)
        persistence_row.setSpacing(8)
        self.editor_clone_to_tab_button = QPushButton("Clone To New Tab", compose_tab)
        self.editor_reset_button = QPushButton("Reset Changes", compose_tab)
        self.editor_save_clone_button = QPushButton("Save Clone", compose_tab)
        self.editor_open_clone_button = QPushButton("Open Clone", compose_tab)
        self.editor_clone_to_tab_button.setProperty("variant", "secondary")
        self.editor_reset_button.setProperty("variant", "warning")
        self.editor_save_clone_button.setProperty("variant", "primary")
        self.editor_open_clone_button.setProperty("variant", "ghost")
        persistence_row.addWidget(self.editor_clone_to_tab_button)
        persistence_row.addWidget(self.editor_reset_button)
        persistence_row.addWidget(self.editor_save_clone_button)
        persistence_row.addWidget(self.editor_open_clone_button)
        compose_layout.addLayout(persistence_row)

        self.editor_note = QLabel(
            "Close without Save Clone discards session edits. Save Clone writes a separate file and keeps originals unchanged.",
            compose_tab,
        )
        self.editor_note.setProperty("role", "caption")
        self.editor_note.setWordWrap(True)
        compose_layout.addWidget(self.editor_note)

        self.side_tabs.addTab(compose_tab, "Compose")
        self._build_entry_picker_dialog()

        split.addWidget(left)
        split.addWidget(center)
        split.addWidget(inspector)
        split.setSizes([0, 1, 0])
        self.main_split = split
        self.catalog.slots.main_slot.addWidget(split, 1)
        self.catalog.cards.hero.hide()
        self.catalog.cards.footer.hide()

        main_panel = self.catalog.panel("main")
        side_panel = self.catalog.panel("side")
        for panel in (main_panel, side_panel):
            if panel is None:
                continue
            panel.setProperty("card", "clear")
            panel.layout().setContentsMargins(0, 0, 0, 0)
            panel.layout().setSpacing(0)
            _repolish(panel)

        self._populate_editor_type_controls()
        self._apply_workbench_icons()
        self._apply_workbench_styles()

    def _wire(self) -> None:
        self.shortcut_open_picker = QShortcut(QKeySequence("Ctrl+K"), self)
        self.shortcut_open_picker.activated.connect(lambda: self._open_entry_picker())
        self.shortcut_open_picker_meta = QShortcut(QKeySequence("Meta+K"), self)
        self.shortcut_open_picker_meta.activated.connect(lambda: self._open_entry_picker())

        self.btn_toggle_catalog.toggled.connect(self._set_catalog_panel_visible)
        self.btn_toggle_inspector.toggled.connect(self._set_inspector_panel_visible)
        self.search_input.textChanged.connect(lambda _text: self._refresh_entries())
        self.tags_input.textChanged.connect(lambda _text: self._refresh_entries())
        self.category_list.currentItemChanged.connect(lambda _curr, _prev: self._refresh_entries())
        self.entry_list.currentItemChanged.connect(self._on_entry_selected)
        self.entry_list.itemDoubleClicked.connect(lambda _item: self._open_selected_preview())
        self.btn_preview.clicked.connect(self._open_selected_preview)
        self.btn_workspace.clicked.connect(self._open_selected_in_workspace)
        self.btn_new_workspace.clicked.connect(self._open_empty_workspace_tab)
        self.btn_close_workspace.clicked.connect(self._close_active_workspace_tab)
        self.btn_clear_filters.clicked.connect(self._clear_filters)
        self.btn_clear_preview.clicked.connect(self._clear_preview)
        self.btn_toggle_motion.clicked.connect(self._toggle_motion)
        self.scale_combo.currentIndexChanged.connect(self._on_scale_changed)
        self.btn_browse_content.clicked.connect(lambda: self._open_entry_picker())
        self.btn_quick_search.clicked.connect(lambda: self._open_entry_picker())
        self.btn_new_tab_primary.clicked.connect(self._open_empty_workspace_tab)
        self.btn_close_tab_primary.clicked.connect(self._close_active_workspace_tab)
        self.btn_tools.clicked.connect(lambda: self._set_inspector_panel_visible(not self._inspector_panel_visible))
        self.btn_blank_add.clicked.connect(lambda: self._open_entry_picker())
        self.btn_blank_new_tab.clicked.connect(self._open_empty_workspace_tab)
        self.btn_blank_tools.clicked.connect(lambda: self._set_inspector_panel_visible(True))
        self.related_list.itemDoubleClicked.connect(self._open_related_item)
        self.provider_list.currentItemChanged.connect(self._on_provider_selected)
        self.btn_probe_query.clicked.connect(self._probe_selected_query)
        self.btn_refresh_providers.clicked.connect(self._refresh_provider_list)
        self.btn_toggle_entry_json.clicked.connect(lambda: self.meta_text.setVisible(not self.meta_text.isVisible()))
        self.btn_toggle_data_json.clicked.connect(self._toggle_data_debug)
        self.btn_refresh_runtime.clicked.connect(self._refresh_runtime_button)
        self.btn_toggle_runtime_json.clicked.connect(
            lambda: self.runtime_diagnostics_text.setVisible(not self.runtime_diagnostics_text.isVisible())
        )
        self.btn_toggle_action_trace.clicked.connect(
            lambda: self.runtime_action_trace_text.setVisible(not self.runtime_action_trace_text.isVisible())
        )
        self.editor_context_combo.currentIndexChanged.connect(self._on_editor_context_changed)
        self.editor_panel_combo.currentIndexChanged.connect(self._on_editor_panel_changed)
        self.editor_palette_search.textChanged.connect(lambda _text: self._refresh_insert_palette())
        self.editor_palette_category_combo.currentIndexChanged.connect(lambda _idx: self._refresh_insert_palette())
        self.editor_palette_list.currentItemChanged.connect(self._on_palette_selected)
        self.editor_palette_list.itemDoubleClicked.connect(lambda _item: self._add_editor_panel())
        self.editor_apply_button.clicked.connect(self._apply_editor_properties)
        self.editor_add_button.clicked.connect(self._add_editor_panel)
        self.editor_remove_button.clicked.connect(self._remove_editor_panel)
        self.editor_move_up_button.clicked.connect(lambda: self._move_editor_panel(-1))
        self.editor_move_down_button.clicked.connect(lambda: self._move_editor_panel(1))
        self.editor_move_left_button.clicked.connect(lambda: self._move_editor_panel_across_slot(-1))
        self.editor_move_right_button.clicked.connect(lambda: self._move_editor_panel_across_slot(1))
        self.editor_duplicate_button.clicked.connect(self._duplicate_editor_panel)
        self.editor_hide_button.clicked.connect(self._hide_editor_panel)
        self.editor_reopen_button.clicked.connect(self._reopen_hidden_panel)
        self.editor_clone_to_tab_button.clicked.connect(self._clone_context_into_new_tab)
        self.editor_reset_button.clicked.connect(self._reset_editor_session)
        self.editor_save_clone_button.clicked.connect(self._save_clone)
        self.editor_open_clone_button.clicked.connect(self._open_clone)
        self.editor_apply_split.clicked.connect(self._apply_editor_split)
        if self.catalog.workspace_tabs is not None:
            self.catalog.workspace_tabs.currentChanged.connect(lambda _idx: self._on_workspace_tab_changed())

    def _is_host_frameless(self, host: QWidget | None) -> bool:
        if host is None:
            return False
        return bool(host.windowFlags() & Qt.FramelessWindowHint)

    def _install_window_shell_interactions(self) -> None:
        host = self.window() if isinstance(self.window(), QWidget) else None
        if host is None:
            return
        self.tools_bar.installEventFilter(self)
        host.installEventFilter(self)
        if not self._is_host_frameless(host):
            return
        existing_grips = getattr(host, "_resize_grips", None)
        if isinstance(existing_grips, list) and existing_grips:
            return
        self._window_resize_host = host
        if self._window_resize_grips:
            self._layout_window_resize_grips()
            return
        grip_specs = [
            (Qt.LeftEdge, Qt.SizeHorCursor),
            (Qt.RightEdge, Qt.SizeHorCursor),
            (Qt.TopEdge, Qt.SizeVerCursor),
            (Qt.BottomEdge, Qt.SizeVerCursor),
            (Qt.LeftEdge | Qt.TopEdge, Qt.SizeFDiagCursor),
            (Qt.RightEdge | Qt.TopEdge, Qt.SizeBDiagCursor),
            (Qt.LeftEdge | Qt.BottomEdge, Qt.SizeBDiagCursor),
            (Qt.RightEdge | Qt.BottomEdge, Qt.SizeFDiagCursor),
        ]
        for edges, cursor in grip_specs:
            grip = _WindowEdgeGrip(host, edges=edges, cursor=cursor, parent=host)
            grip.raise_()
            grip.show()
            self._window_resize_grips.append(grip)
        self._layout_window_resize_grips()

    def _layout_window_resize_grips(self) -> None:
        host = self._window_resize_host
        if host is None or not self._window_resize_grips:
            return
        if host.isMaximized() or not self._is_host_frameless(host):
            for grip in self._window_resize_grips:
                grip.hide()
            return
        for grip in self._window_resize_grips:
            grip.show()
            grip.raise_()
        grip = int(self._window_resize_grip_size)
        width = int(host.width())
        height = int(host.height())
        left, right, top, bottom, tl, tr, bl, br = self._window_resize_grips
        left.setGeometry(0, grip, grip, max(0, height - (grip * 2)))
        right.setGeometry(width - grip, grip, grip, max(0, height - (grip * 2)))
        top.setGeometry(grip, 0, max(0, width - (grip * 2)), grip)
        bottom.setGeometry(grip, height - grip, max(0, width - (grip * 2)), grip)
        tl.setGeometry(0, 0, grip, grip)
        tr.setGeometry(width - grip, 0, grip, grip)
        bl.setGeometry(0, height - grip, grip, grip)
        br.setGeometry(width - grip, height - grip, grip, grip)

    def _can_begin_window_drag(self, event: QEvent) -> bool:
        if not self._event_has_left_button(event):
            return False
        if self._event_modifiers(event) not in {Qt.NoModifier, Qt.AltModifier}:
            return False
        pos = self._event_local_point(event)
        if pos.y() > max(42, int(self.tools_bar.height()) + 4):
            return False
        child = self.tools_bar.childAt(pos)
        if isinstance(child, (QPushButton, QComboBox, QLineEdit, QTextEdit, QSlider, QCheckBox, QListWidget, QTabWidget)):
            return False
        return True

    def _handle_window_drag_event(self, watched: QObject, event: QEvent) -> bool:
        if watched is not self.tools_bar:
            return False
        host = self.window() if isinstance(self.window(), QWidget) else None
        if host is None or not self._is_host_frameless(host) or host.isMaximized():
            return False
        event_type = event.type()
        if event_type == QEvent.Type.MouseButtonPress:
            if not self._can_begin_window_drag(event):
                return False
            self._window_dragging = True
            self._window_drag_offset = self._event_global_point(event) - host.frameGeometry().topLeft()
            return True
        if event_type == QEvent.Type.MouseMove:
            if not self._window_dragging or not self._event_has_left_button(event):
                return False
            host.move(self._event_global_point(event) - self._window_drag_offset)
            return True
        if event_type in {QEvent.Type.MouseButtonRelease, QEvent.Type.Leave}:
            if self._window_dragging:
                self._window_dragging = False
                return True
        return False

    def _tune_template_density(self) -> None:
        shell_layout = self.catalog.cards.shell.layout()
        if isinstance(shell_layout, QVBoxLayout):
            shell_layout.setContentsMargins(1, 1, 1, 1)
            shell_layout.setSpacing(2)
        hero_layout = self.catalog.cards.hero.layout()
        if isinstance(hero_layout, QVBoxLayout):
            hero_layout.setContentsMargins(1, 1, 1, 1)
            hero_layout.setSpacing(1)
        body_layout = self.catalog.cards.body.layout()
        if isinstance(body_layout, QVBoxLayout):
            body_layout.setSpacing(2)

    def _set_preview_collapsed(self, collapsed: bool) -> None:
        self.preview_scroll.setVisible(not bool(collapsed))
        self.blank_workspace_hint.setVisible(bool(collapsed))
        self.blank_workspace_actions.setVisible(bool(collapsed))
        self.main_split.setMaximumHeight(16777215)
        self.main_split.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        main_panel = self.catalog.panel("main")
        if main_panel is not None:
            main_panel.setMaximumHeight(16777215)
        if collapsed:
            self.preview_title.setText("Blank Editor Workspace")
            self.preview_subtitle.setText("Blank by design. Add content only when needed.")

    def _set_catalog_panel_visible(self, visible: bool, *, initialize: bool = True) -> None:
        self._catalog_panel_visible = bool(visible)
        self.catalog_browser_frame.setVisible(self._catalog_panel_visible)
        self.btn_toggle_catalog.blockSignals(True)
        self.btn_toggle_catalog.setChecked(False)
        self.btn_toggle_catalog.blockSignals(False)
        if initialize and not self._catalog_initialized:
            self._refresh_categories()
            self._refresh_entries()
            self._catalog_initialized = True
        if self._catalog_panel_visible:
            self._open_entry_picker()
        self._apply_main_split_visibility()

    def _set_inspector_panel_visible(self, visible: bool, *, initialize: bool = True) -> None:
        self._inspector_panel_visible = bool(visible)
        self.inspector_frame.setVisible(self._inspector_panel_visible)
        self.btn_toggle_inspector.blockSignals(True)
        self.btn_toggle_inspector.setChecked(self._inspector_panel_visible)
        self.btn_toggle_inspector.blockSignals(False)
        if self._inspector_panel_visible and initialize and not self._inspector_initialized:
            self._refresh_provider_list()
            self._refresh_runtime_inspector(self._current_entry())
            self._inspector_initialized = True
        self._apply_main_split_visibility()

    def _apply_main_split_visibility(self) -> None:
        if not hasattr(self, "main_split"):
            return
        sizes = self.main_split.sizes()
        total = sum(sizes) if sum(sizes) > 0 else max(1200, int(self.width()))
        nav = max(220, int(total * 0.20)) if self._catalog_panel_visible else 0
        inspect = max(280, int(total * 0.24)) if self._inspector_panel_visible else 0
        center = max(620, total - nav - inspect)
        self.main_split.setSizes([nav, center, inspect])

    def _apply_workbench_icons(self) -> None:
        icon_map = {
            self.btn_toggle_catalog: "layers",
            self.btn_toggle_inspector: "search",
            self.btn_preview: "play",
            self.btn_workspace: "arrow-right",
            self.btn_new_workspace: "plus",
            self.btn_close_workspace: "x-circle",
            self.btn_clear_preview: "minus",
            self.btn_clear_filters: "filter",
            self.btn_toggle_motion: "sparkles",
            self.btn_probe_query: "search",
            self.btn_refresh_providers: "refresh-cw",
            self.btn_toggle_entry_json: "code",
            self.btn_toggle_data_json: "database",
            self.btn_refresh_runtime: "activity",
            self.btn_toggle_runtime_json: "terminal",
            self.btn_toggle_action_trace: "clock",
            self.btn_browse_content: "plus",
            self.btn_new_tab_primary: "plus-square",
            self.btn_close_tab_primary: "x-circle",
            self.btn_quick_search: "search",
            self.btn_tools: "sliders-horizontal",
            self.btn_blank_add: "plus",
            self.btn_blank_new_tab: "plus-square",
            self.btn_blank_tools: "sliders-horizontal",
            self.editor_apply_button: "check",
            self.editor_add_button: "plus",
            self.editor_remove_button: "x-circle",
            self.editor_move_up_button: "chevron-up",
            self.editor_move_down_button: "chevron-down",
            self.editor_move_left_button: "chevron-left",
            self.editor_move_right_button: "chevron-right",
            self.editor_duplicate_button: "copy",
            self.editor_hide_button: "minus",
            self.editor_reopen_button: "folder-open",
            self.editor_clone_to_tab_button: "copy-plus",
            self.editor_reset_button: "refresh-cw",
            self.editor_save_clone_button: "save",
            self.editor_open_clone_button: "folder-open",
            self.editor_apply_split: "layout-dashboard",
        }
        for button, icon_name in icon_map.items():
            apply_icon(button, icon_name, size="small", tooltip=button.text())

        tab_icon_map = ("file-text", "database", "cpu", "sliders-horizontal")
        for index, icon_name in enumerate(tab_icon_map):
            icon = get_icon(icon_name)
            if not icon.isNull():
                self.side_tabs.setTabIcon(index, icon)

    def _apply_workbench_styles(self) -> None:
        self.setStyleSheet(
            """
QWidget#GlassCatalogShell QFrame#WorkbenchToolbarCard {
    background: transparent;
    border: none;
    border-radius: 0px;
}
QWidget#GlassCatalogShell QFrame#WorkbenchToolbarCard QFrame[workbenchSep="true"] {
    background: rgba(140, 235, 255, 0.14);
}
QWidget#GlassCatalogShell QFrame#WorkbenchToolbarCard QPushButton {
    min-height: 22px;
    max-height: 22px;
    padding-top: 1px;
    padding-bottom: 1px;
    border-radius: 9px;
    border: none;
    background: rgba(255, 255, 255, 0.01);
    color: rgba(244, 247, 252, 0.95);
}
QWidget#GlassCatalogShell QFrame#WorkbenchToolbarCard QComboBox {
    min-height: 22px;
    max-height: 22px;
    padding-top: 1px;
    padding-bottom: 1px;
}
QWidget#GlassCatalogShell QFrame#WorkbenchToolbarCard QPushButton:checked {
    border: 1px solid rgba(140, 235, 255, 0.58);
    background: rgba(140, 235, 255, 0.10);
}
QWidget#GlassCatalogShell QFrame#WorkbenchToolbarCard QPushButton[commandRole="primary"] {
    background: rgba(140, 235, 255, 0.07);
    border: none;
}
QWidget#GlassCatalogShell QFrame#WorkbenchToolbarCard QPushButton[commandRole="toggle"] {
    border: none;
}
QWidget#GlassCatalogShell QFrame#WorkbenchToolbarCard QPushButton[commandRole="secondary"] {
    background: rgba(255, 255, 255, 0.01);
}
QWidget#GlassCatalogShell QFrame#WorkbenchToolbarCard QPushButton:hover {
    border: 1px solid rgba(140, 235, 255, 0.54);
    background: rgba(140, 235, 255, 0.09);
}
QWidget#GlassCatalogShell QFrame#WorkbenchNavRail,
QWidget#GlassCatalogShell QFrame#WorkbenchInspectorSurface {
    background: rgba(255, 255, 255, 0.028);
    border: 1px solid rgba(140, 235, 255, 0.14);
    border-radius: 12px;
}
QWidget#GlassCatalogShell QFrame#WorkbenchCenterSurface {
    background: transparent;
    border: none;
    border-radius: 10px;
}
QWidget#GlassCatalogShell QFrame#WorkbenchPreviewHost {
    background: transparent;
    border: none;
    border-radius: 10px;
}
QWidget#GlassCatalogShell QFrame#WorkbenchEntrySummaryCard {
    background: transparent;
    border: none;
    border-radius: 0px;
}
QWidget#GlassCatalogShell QSplitter#WorkbenchMainSplitter::handle {
    background: rgba(255, 255, 255, 0.045);
    border-radius: 3px;
}
QWidget#GlassCatalogShell QSplitter#WorkbenchMainSplitter::handle:hover {
    background: rgba(255, 255, 255, 0.11);
}
QWidget#GlassCatalogShell QScrollArea#WorkbenchPreviewScroll {
    border: none;
    background: transparent;
}
QWidget#GlassCatalogShell QLineEdit,
QWidget#GlassCatalogShell QComboBox,
QWidget#GlassCatalogShell QTextEdit,
QWidget#GlassCatalogShell QListWidget,
QWidget#GlassCatalogShell QTableWidget {
    background: rgba(255, 255, 255, 0.048);
    border: 1px solid rgba(140, 235, 255, 0.16);
    border-radius: 8px;
}
QWidget#GlassCatalogShell QLineEdit:hover,
QWidget#GlassCatalogShell QLineEdit:focus,
QWidget#GlassCatalogShell QComboBox:hover,
QWidget#GlassCatalogShell QComboBox:focus,
QWidget#GlassCatalogShell QTextEdit:hover,
QWidget#GlassCatalogShell QTextEdit:focus {
    border-color: rgba(140, 235, 255, 0.58);
}
QWidget#GlassCatalogShell QListWidget {
    padding: 2px;
    outline: none;
}
QWidget#GlassCatalogShell QListWidget::item {
    padding: 4px 6px;
    border-radius: 8px;
}
QWidget#GlassCatalogShell QListWidget::item:hover {
    background: rgba(255, 255, 255, 0.065);
}
QWidget#GlassCatalogShell QListWidget::item:selected {
    background: rgba(140, 235, 255, 0.12);
    border: 1px solid rgba(140, 235, 255, 0.62);
}
QWidget#GlassCatalogShell QTabWidget#WorkbenchInspectorTabs::pane {
    border: none;
    border-radius: 10px;
}
QWidget#GlassCatalogShell QTabWidget#WorkbenchInspectorTabs QTabBar::tab {
    padding: 3px 9px;
    margin-right: 3px;
}
QWidget#GlassCatalogShell QFrame[hoverable="true"][hover="true"] {
    border-color: rgba(140, 235, 255, 0.56);
}
QWidget#GlassCatalogShell QFrame[editorSelected="true"] {
    border: 1px solid rgba(140, 235, 255, 0.78);
}
QWidget#GlassCatalogShell QListWidget#WorkbenchInsertPalette::item:selected {
    background: rgba(140, 235, 255, 0.12);
    border: 1px solid rgba(140, 235, 255, 0.64);
}
QWidget#GlassCatalogShell QFrame[editorVariant="accent"] {
    border: 1px solid rgba(140, 235, 255, 0.62);
}
QWidget#GlassCatalogShell QFrame[editorVariant="warning"] {
    border: 1px solid rgba(140, 235, 255, 0.42);
}
QWidget#GlassCatalogShell QFrame[editorVariant="success"] {
    border: 1px solid rgba(140, 235, 255, 0.46);
}
QWidget#GlassCatalogShell QPushButton[variant="subtle"] {
    padding-left: 8px;
    padding-right: 8px;
}
QWidget#GlassCatalogShell QPushButton[editorAction="danger"] {
    border-color: rgba(140, 235, 255, 0.64);
}
QWidget#GlassCatalogShell QLabel#MetricChip {
    background: rgba(140, 235, 255, 0.08);
    border: 1px solid rgba(140, 235, 255, 0.22);
    border-radius: 10px;
    padding: 1px 7px;
    color: rgba(243, 247, 252, 0.92);
}
QWidget#GlassCatalogShell QWidget#WorkbenchChartCanvas {
    background: transparent;
    border: none;
}
QWidget#GlassCatalogShell QFrame[panelInteraction="dragging"] {
    border-color: rgba(140, 235, 255, 0.84);
}
QWidget#GlassCatalogShell QFrame[panelInteraction="resizing"] {
    border-color: rgba(140, 235, 255, 0.74);
}
QWidget#GlassCatalogShell QFrame[resizeAffordance="true"] {
    border-bottom-width: 1px;
    border-bottom-style: solid;
    border-bottom-color: rgba(140, 235, 255, 0.14);
}
QWidget#GlassCatalogShell QFrame[resizeAffordance="true"]:hover {
    border-bottom-color: rgba(140, 235, 255, 0.42);
}
QWidget#GlassCatalogShell QFrame#WorkbenchCenterSurface {
    border: none;
    background: transparent;
}
QWidget#GlassCatalogShell QFrame#WorkbenchNavRail,
QWidget#GlassCatalogShell QFrame#WorkbenchInspectorSurface {
    border-radius: 12px;
}
QDialog#WorkbenchEntryPicker {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.11),
        stop:1 rgba(255, 255, 255, 0.05));
    border: 1px solid rgba(140, 235, 255, 0.24);
    border-radius: 14px;
}
QDialog#WorkbenchEntryPicker QListWidget {
    border: 1px solid rgba(140, 235, 255, 0.18);
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.06);
}
QDialog#WorkbenchEntryPicker QListWidget::item {
    padding: 6px 8px;
    border-radius: 8px;
}
QDialog#WorkbenchEntryPicker QListWidget::item:selected {
    background: rgba(140, 235, 255, 0.14);
    border: 1px solid rgba(140, 235, 255, 0.64);
}
QDialog#WorkbenchEntryPicker QLineEdit,
QDialog#WorkbenchEntryPicker QComboBox,
QDialog#WorkbenchEntryPicker QTextEdit {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(140, 235, 255, 0.18);
    border-radius: 8px;
}
QDialog#WorkbenchEntryPicker QPushButton {
    border-radius: 9px;
    border: none;
    background: rgba(255, 255, 255, 0.01);
}
QDialog#WorkbenchEntryPicker QPushButton {
    min-height: 24px;
}
QDialog#WorkbenchEntryPicker QPushButton:hover {
    border: 1px solid rgba(140, 235, 255, 0.56);
    background: rgba(140, 235, 255, 0.09);
}
QWidget#GlassCatalogShell QFrame#WorkbenchPendingCandidate {
    background: rgba(255, 255, 255, 0.042);
    border: 1px solid rgba(140, 235, 255, 0.28);
    border-radius: 10px;
}
"""
        )

    def _build_entry_picker_dialog(self) -> None:
        dialog = QDialog(self, Qt.Dialog)
        dialog.setModal(False)
        dialog.setWindowTitle("Browse Content")
        dialog.resize(960, 640)
        dialog.setObjectName("WorkbenchEntryPicker")
        dialog.setAttribute(Qt.WA_TranslucentBackground, True)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        title = QLabel("Content Picker", dialog)
        title.setProperty("role", "panel_title")
        subtitle = QLabel(
            "Search and filter catalog entries, then Add to Current Tab or Open in New Tab.",
            dialog,
        )
        subtitle.setProperty("role", "panel_subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        filters = QHBoxLayout()
        filters.setContentsMargins(0, 0, 0, 0)
        filters.setSpacing(6)
        self.picker_search_input = QLineEdit(dialog)
        self.picker_search_input.setPlaceholderText("Search entries, tags, keywords...")
        self.picker_category_combo = QComboBox(dialog)
        self.picker_category_combo.addItem("All", "All")
        filters.addWidget(self.picker_search_input, 1)
        filters.addWidget(self.picker_category_combo)
        layout.addLayout(filters)

        body_split = QSplitter(Qt.Horizontal, dialog)
        body_split.setChildrenCollapsible(False)
        body_split.setHandleWidth(4)
        list_host = QFrame(body_split)
        list_host.setProperty("card", "clear")
        list_layout = QVBoxLayout(list_host)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(6)
        self.picker_entry_list = QListWidget(list_host)
        list_layout.addWidget(self.picker_entry_list, 1)

        detail_host = QFrame(body_split)
        detail_host.setProperty("card", "clear")
        detail_layout = QVBoxLayout(detail_host)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        detail_layout.setSpacing(6)
        self.picker_entry_title = QLabel("No selection", detail_host)
        self.picker_entry_title.setProperty("role", "section")
        self.picker_entry_summary = QLabel("Select an entry to preview and add it into workspace tabs.", detail_host)
        self.picker_entry_summary.setProperty("role", "panel_subtitle")
        self.picker_entry_summary.setWordWrap(True)
        self.picker_entry_meta = QLabel("", detail_host)
        self.picker_entry_meta.setProperty("role", "caption")
        self.picker_entry_meta.setWordWrap(True)
        self.picker_entry_meta.setVisible(False)
        detail_layout.addWidget(self.picker_entry_title)
        detail_layout.addWidget(self.picker_entry_summary)
        detail_layout.addWidget(self.picker_entry_meta)
        detail_layout.addStretch(1)

        body_split.addWidget(list_host)
        body_split.addWidget(detail_host)
        body_split.setSizes([560, 420])
        layout.addWidget(body_split, 1)

        buttons = QDialogButtonBox(dialog)
        self.picker_preview_button = buttons.addButton("Preview", QDialogButtonBox.ActionRole)
        self.picker_add_current_button = buttons.addButton("Add to Current Tab", QDialogButtonBox.AcceptRole)
        self.picker_add_new_tab_button = buttons.addButton("Open in New Tab", QDialogButtonBox.ActionRole)
        self.picker_close_button = buttons.addButton("Close", QDialogButtonBox.RejectRole)
        self.picker_add_current_button.setDefault(True)
        layout.addWidget(buttons)

        self.entry_picker_dialog = dialog
        dialog.finished.connect(lambda _code: self._on_picker_closed())

        self.picker_search_input.textChanged.connect(lambda _text: self._refresh_picker_entries())
        self.picker_category_combo.currentIndexChanged.connect(lambda _idx: self._refresh_picker_entries())
        self.picker_entry_list.currentItemChanged.connect(lambda _curr, _prev: self._on_picker_selection_changed())
        self.picker_entry_list.itemDoubleClicked.connect(lambda _item: self._picker_add_to_current_tab())
        self.picker_preview_button.clicked.connect(self._picker_preview_selected)
        self.picker_add_current_button.clicked.connect(self._picker_add_to_current_tab)
        self.picker_add_new_tab_button.clicked.connect(self._picker_open_in_new_tab)
        self.picker_close_button.clicked.connect(dialog.close)

    def _on_picker_closed(self) -> None:
        self._catalog_panel_visible = False

    def _open_entry_picker(self, *, target_tab_id: str | None = None) -> None:
        if not hasattr(self, "entry_picker_dialog"):
            return
        self._picker_target_tab_id = str(target_tab_id or "").strip() or None
        self._refresh_picker_categories()
        self._refresh_picker_entries()
        current_id = str(self._selected_entry_id or "").strip().lower()
        if current_id:
            for index in range(self.picker_entry_list.count()):
                item = self.picker_entry_list.item(index)
                if str(item.data(Qt.UserRole) or "").strip().lower() == current_id:
                    self.picker_entry_list.setCurrentRow(index)
                    break
        self.entry_picker_dialog.show()
        self.entry_picker_dialog.raise_()
        self.entry_picker_dialog.activateWindow()
        self.picker_search_input.setFocus()

    def _refresh_picker_categories(self) -> None:
        self.picker_category_combo.blockSignals(True)
        current = str(self.picker_category_combo.currentData() or "All")
        self.picker_category_combo.clear()
        self.picker_category_combo.addItem("All", "All")
        for category in list_catalog_categories():
            self.picker_category_combo.addItem(category, category)
        self.picker_category_combo.blockSignals(False)
        for idx in range(self.picker_category_combo.count()):
            if str(self.picker_category_combo.itemData(idx) or "") == current:
                self.picker_category_combo.setCurrentIndex(idx)
                break

    def _refresh_picker_entries(self) -> None:
        query = str(self.picker_search_input.text() or "").strip()
        category = str(self.picker_category_combo.currentData() or "All")
        entries = list_catalog_entries(
            category=None if str(category).strip().lower() == "all" else category,
            search=query,
            tags=(),
        )
        self.picker_entry_list.blockSignals(True)
        self.picker_entry_list.clear()
        for entry in entries:
            label = f"{entry.title}\n{entry.subtitle or entry.description or ''}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, entry.entry_id)
            icon = get_icon(entry.icon_name or "layers")
            if not icon.isNull():
                item.setIcon(icon)
            self.picker_entry_list.addItem(item)
        self.picker_entry_list.blockSignals(False)
        if self.picker_entry_list.count() > 0:
            self.picker_entry_list.setCurrentRow(0)
        else:
            self.picker_entry_title.setText("No matching entries")
            self.picker_entry_summary.setText("Adjust search/category filters to find available content.")
            self.picker_entry_meta.setVisible(False)

    def _picker_selected_entry_id(self) -> str:
        item = self.picker_entry_list.currentItem()
        if item is None:
            return ""
        return str(item.data(Qt.UserRole) or "").strip()

    def _on_picker_selection_changed(self) -> None:
        entry_id = self._picker_selected_entry_id()
        entry = get_catalog_entry(entry_id) if entry_id else None
        if entry is None:
            self.picker_entry_title.setText("No selection")
            self.picker_entry_summary.setText("Select an entry to preview and add it into workspace tabs.")
            self.picker_entry_meta.setVisible(False)
            return
        self._selected_entry_id = entry.entry_id
        self.picker_entry_title.setText(entry.title)
        self.picker_entry_summary.setText(entry.description or entry.subtitle or "No summary.")
        self.picker_entry_meta.setText(
            f"{entry.category} · {entry.status.upper()} · tags: {', '.join(entry.tags) if entry.tags else '(none)'}"
        )
        self.picker_entry_meta.setVisible(True)
        self._show_entry_detail(entry)
        self._open_selected_preview()

    def _picker_preview_selected(self) -> None:
        if not self._picker_selected_entry_id():
            return
        self._open_selected_preview()

    def _resolve_target_workspace_tab(self) -> str:
        tabs = self.catalog.workspace_tabs
        if tabs is None:
            return ""
        if self._picker_target_tab_id and self._picker_target_tab_id in self._workspace_hosts:
            return self._picker_target_tab_id
        active = tabs.active_tab_id() or ""
        if active in self._workspace_hosts:
            return active
        self._open_empty_workspace_tab()
        tabs = self.catalog.workspace_tabs
        if tabs is None:
            return ""
        active = tabs.active_tab_id() or ""
        if active in self._workspace_hosts:
            return active
        return ""

    def _replace_workspace_host_with_entry(self, *, tab_id: str, entry: GlassCatalogEntry) -> bool:
        host = self._workspace_hosts.get(tab_id)
        tabs = self.catalog.workspace_tabs
        if host is None or tabs is None:
            return False
        context_id = f"workspace:{tab_id}"
        host.replace_factory(
            entry.title,
            factory=lambda: self._build_workspace_widget(entry, context_id=context_id),
            remount_if_active=True,
        )
        index = tabs.index_of(tab_id)
        if index >= 0:
            tabs.setTabText(index, entry.title)
            tabs.setTabToolTip(index, entry.description or entry.subtitle or entry.title)
        tabs.set_tab_badge(tab_id, "live" if host.is_mounted() else "lazy")
        self._enforce_workspace_budget()
        self._refresh_editor_contexts(select_context=context_id)
        self.catalog.set_status_text(f"Added '{entry.title}' to current tab.")
        return True

    def _pending_candidate_host(self, context_id: str) -> QWidget:
        normalized = str(context_id or "").strip().lower()
        template = self._editor_templates.get(normalized)
        if isinstance(template, GlassPanelTemplate):
            return template.cards.body
        if normalized.startswith("workspace:"):
            tab_id = normalized.split(":", 1)[1]
            host = self._workspace_hosts.get(tab_id)
            if host is not None:
                host.set_active(True)
                mounted = getattr(host, "_mounted", None)
                if isinstance(mounted, GlassPanelTemplate):
                    self._editor_templates[normalized] = mounted
                    return mounted.cards.body
        return self.catalog.cards.body

    def _stage_pending_panel_candidate(
        self,
        *,
        context_id: str,
        title: str,
        summary: str,
        commit: Callable[[], bool],
    ) -> None:
        self._discard_pending_panel_candidate(announce=False)
        host = self._pending_candidate_host(context_id)
        overlay = _PendingCandidateOverlay(
            host,
            title=title,
            summary=summary,
            on_confirm=self._commit_pending_panel_candidate,
            on_cancel=self._discard_pending_panel_candidate,
        )
        width = max(300, min(460, int(max(1, host.width()) * 0.42)))
        overlay.resize(width, 114)
        host_rect = host.contentsRect()
        initial = QPoint(
            host_rect.left() + max(0, (host_rect.width() - overlay.width()) // 2),
            host_rect.top() + max(2, int(host_rect.height() * 0.14)),
        )
        overlay.move(overlay._clamp_top_left(initial))
        overlay.show()
        overlay.raise_()
        self._pending_candidate_overlay = overlay
        self._pending_candidate_commit = commit
        self._pending_candidate_context_id = str(context_id or "").strip().lower()
        self.catalog.set_status_text("Candidate staged. Confirm or cancel.")

    def _commit_pending_panel_candidate(self) -> None:
        overlay = self._pending_candidate_overlay
        commit = self._pending_candidate_commit
        if commit is None:
            return
        if overlay is not None:
            try:
                overlay.parentWidget()
            except RuntimeError:
                overlay = None
                self._pending_candidate_overlay = None
        if overlay is None:
            return
        try:
            committed = bool(commit())
        except Exception as exc:  # noqa: BLE001
            self.catalog.set_status_text(f"Candidate commit failed: {exc}")
            return
        if not committed:
            self.catalog.set_status_text("Candidate commit did not complete.")
            return
        self._discard_pending_panel_candidate(announce=False)

    def _discard_pending_panel_candidate(self, *, announce: bool = True) -> None:
        overlay = self._pending_candidate_overlay
        self._pending_candidate_overlay = None
        self._pending_candidate_commit = None
        self._pending_candidate_context_id = None
        if overlay is not None:
            try:
                overlay.setParent(None)
                overlay.deleteLater()
            except RuntimeError:
                pass
        if announce:
            self.catalog.set_status_text("Candidate discarded.")

    def _picker_add_to_current_tab(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        target_tab_id = self._resolve_target_workspace_tab()
        if not target_tab_id:
            self._open_empty_workspace_tab()
            target_tab_id = self._resolve_target_workspace_tab()
            if not target_tab_id:
                self.catalog.set_status_text("No workspace tab available to stage candidate.")
                return
        context_id = f"workspace:{target_tab_id}"
        self._stage_pending_panel_candidate(
            context_id=context_id,
            title=f"Stage '{entry.title}'",
            summary="Drag within workspace bounds, then Confirm to apply or Cancel to discard.",
            commit=lambda: self._replace_workspace_host_with_entry(tab_id=target_tab_id, entry=entry),
        )
        self.entry_picker_dialog.close()

    def _picker_open_in_new_tab(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        self._open_empty_workspace_tab()
        tabs = self.catalog.workspace_tabs
        target_tab_id = tabs.active_tab_id() if tabs is not None else ""
        if not target_tab_id:
            return
        context_id = f"workspace:{target_tab_id}"
        self._stage_pending_panel_candidate(
            context_id=context_id,
            title=f"Stage '{entry.title}' in new tab",
            summary="Confirm to commit into the new workspace tab or Cancel to keep it blank.",
            commit=lambda: self._replace_workspace_host_with_entry(tab_id=target_tab_id, entry=entry),
        )
        self.entry_picker_dialog.close()

    def _build_panel_type_registry(self) -> dict[str, WorkbenchPanelType]:
        specs = [
            WorkbenchPanelType(
                "empty_panel",
                "Clean Empty Panel",
                "square",
                "workspace",
                "Blank shell for custom composition.",
                "Empty panel",
                "",
                category="layout",
                object_kind="layout_container",
            ),
            WorkbenchPanelType(
                "text_block",
                "Text Block",
                "file-text",
                "workspace",
                "Simple paragraph text content.",
                "Text block",
                "Write panel notes here.",
                category="content",
                object_kind="content_panel",
            ),
            WorkbenchPanelType(
                "title_subtitle_block",
                "Title/Subtitle Block",
                "type",
                "workspace",
                "Header style content for section intros.",
                "Header block",
                "Title and subtitle",
                category="content",
                object_kind="content_panel",
            ),
            WorkbenchPanelType(
                "text_markdown",
                "Markdown/Content Block",
                "file-code",
                "workspace",
                "Narrative markdown-like content block.",
                "Markdown panel",
                "## Heading\nDetails and notes.",
                category="content",
                object_kind="content_panel",
            ),
            WorkbenchPanelType(
                "form_input",
                "Form / Input",
                "edit",
                "form",
                "Input-oriented controls and capture flow.",
                "Input capture",
                "Name, email, notes.",
                category="input",
                object_kind="input_control",
            ),
            WorkbenchPanelType(
                "form_section",
                "Form Section",
                "list-checks",
                "form",
                "Labeled form section with grouped fields.",
                "Form section",
                "Group of editable fields",
                category="input",
                object_kind="input_control",
            ),
            WorkbenchPanelType(
                "button_control",
                "Button",
                "mouse-pointer-click",
                "workspace",
                "Single action button control.",
                "Button control",
                "Run action",
                category="action",
                object_kind="action_control",
            ),
            WorkbenchPanelType(
                "action_buttons",
                "Button / Actions",
                "zap",
                "workspace",
                "Action-oriented command buttons.",
                "Action strip",
                "Primary / secondary actions.",
                category="action",
                object_kind="action_control",
            ),
            WorkbenchPanelType(
                "toolbar_controls",
                "Toolbar",
                "rows-3",
                "workspace",
                "Compact toolbar with action affordances.",
                "Toolbar",
                "Search · Refresh · Export",
                category="action",
                object_kind="chrome_utility",
            ),
            WorkbenchPanelType(
                "search_filter_bar",
                "Search/Filter Bar",
                "search",
                "workspace",
                "Search and filter controls for dense screens.",
                "Search + filters",
                "query / status / owner",
                category="input",
                object_kind="input_control",
            ),
            WorkbenchPanelType(
                "selector_list",
                "Dropdown / Selector",
                "filter",
                "detail",
                "Selection controls and option lists.",
                "Selector panel",
                "Option A, Option B, Option C",
                category="input",
                object_kind="input_control",
            ),
            WorkbenchPanelType(
                "list_view",
                "List View",
                "list",
                "detail",
                "Scrollable list surface for entities/items.",
                "List view",
                "Item A, Item B, Item C",
                category="content",
                object_kind="content_panel",
            ),
            WorkbenchPanelType(
                "table_grid",
                "Table / Grid",
                "menu",
                "data",
                "Structured row/column overview.",
                "Table view",
                "Rows and columns",
                category="data",
                object_kind="data_widget",
                heavy=True,
            ),
            WorkbenchPanelType(
                "property_grid",
                "Property Grid",
                "sliders-horizontal",
                "inspector",
                "Name/value property table for object inspection.",
                "Property grid",
                "key=value pairs",
                category="diagnostic",
                object_kind="diagnostic_surface",
                heavy=True,
            ),
            WorkbenchPanelType(
                "chart_graph",
                "Chart / Graph",
                "activity",
                "metrics",
                "Provider-backed chart surface with style/palette catalog.",
                "Chart surface",
                "Trend / distribution · style catalog",
                category="data",
                object_kind="data_widget",
                heavy=True,
            ),
            WorkbenchPanelType(
                "metrics_kpi",
                "Metrics / KPI",
                "cpu",
                "metrics",
                "Compact KPI cards.",
                "KPI row",
                "Latency, errors, throughput",
                category="data",
                object_kind="data_widget",
            ),
            WorkbenchPanelType(
                "metric_card",
                "KPI / Metric Card",
                "gauge",
                "metrics",
                "Single-value KPI card for dashboard summaries.",
                "Metric card",
                "p95 latency 42ms",
                category="data",
                object_kind="data_widget",
            ),
            WorkbenchPanelType(
                "feed_log",
                "Feed / Events",
                "clock",
                "activity",
                "Event stream style feed.",
                "Activity feed",
                "event.created / event.updated / event.closed",
                category="data",
                object_kind="data_widget",
                heavy=True,
            ),
            WorkbenchPanelType(
                "timeline_activity",
                "Timeline / Activity",
                "history",
                "activity",
                "Timeline style ordered activity panel.",
                "Timeline",
                "09:40 queued · 09:42 running · 09:45 done",
                category="data",
                object_kind="data_widget",
                heavy=True,
            ),
            WorkbenchPanelType(
                "inspector_panel",
                "Inspector Panel",
                "inspect",
                "inspector",
                "Structured inspector-focused panel.",
                "Inspector",
                "Selected object diagnostics",
                category="diagnostic",
                object_kind="diagnostic_surface",
                heavy=True,
            ),
            WorkbenchPanelType(
                "image_svg",
                "Image / SVG",
                "component",
                "detail",
                "Icon/image placeholder panel.",
                "Visual preview",
                "SVG/icon preview",
                category="content",
                object_kind="content_panel",
            ),
            WorkbenchPanelType(
                "json_diag",
                "JSON / Diagnostics",
                "terminal",
                "inspector",
                "Raw diagnostics panel.",
                "Diagnostics",
                "{\"status\":\"ok\"}",
                category="diagnostic",
                object_kind="diagnostic_surface",
                heavy=True,
            ),
            WorkbenchPanelType(
                "code_panel",
                "Code / JSON Panel",
                "code",
                "inspector",
                "Code-like payload/JSON inspection surface.",
                "Code panel",
                "{\"payload\":\"...\"}",
                category="diagnostic",
                object_kind="diagnostic_surface",
                heavy=True,
            ),
            WorkbenchPanelType(
                "dashboard_widget",
                "Dashboard Widget",
                "layout-panel-top",
                "metrics",
                "Reusable dashboard widget shell with chrome.",
                "Widget shell",
                "Widget title + body + status",
                category="data",
                object_kind="data_widget",
                heavy=True,
            ),
            WorkbenchPanelType(
                "status_badge_group",
                "Status/Badge/Chip Group",
                "badge-check",
                "summary",
                "Compact status chip and badge group.",
                "Status chips",
                "ready · warning · pending",
                category="utility",
                object_kind="chrome_utility",
            ),
            WorkbenchPanelType(
                "split_container",
                "Split Container",
                "layout-dashboard",
                "workspace",
                "Two-pane split surface.",
                "Split container",
                "Left / right context",
                category="layout",
                object_kind="layout_container",
                max_per_slot=3,
            ),
            WorkbenchPanelType(
                "tabbed_container",
                "Tabbed Container",
                "layers",
                "workspace",
                "Tabbed panel container.",
                "Tabbed panel",
                "Tab A / Tab B",
                category="layout",
                object_kind="layout_container",
                max_per_slot=3,
            ),
            WorkbenchPanelType(
                "stacked_container",
                "Stacked Container",
                "panel-top",
                "workspace",
                "Vertical stacked layout container.",
                "Stacked container",
                "Top / middle / bottom blocks",
                category="layout",
                object_kind="layout_container",
                max_per_slot=4,
            ),
            WorkbenchPanelType(
                "header_section",
                "Header / Section",
                "sparkles",
                "workspace",
                "Hero/header utility panel.",
                "Section header",
                "Headline and supporting text",
                category="utility",
                object_kind="chrome_utility",
            ),
            WorkbenchPanelType(
                "section_shell",
                "Section Shell",
                "rectangle-ellipsis",
                "workspace",
                "Framed section shell for grouped content.",
                "Section shell",
                "Grouped block",
                category="layout",
                object_kind="layout_container",
            ),
            WorkbenchPanelType(
                "empty_state_shell",
                "Empty-State Shell",
                "inbox",
                "detail",
                "Reusable empty-state message shell.",
                "No results",
                "No items found. Adjust filters.",
                category="state",
                object_kind="state_surface",
            ),
            WorkbenchPanelType(
                "loading_state_shell",
                "Loading-State Shell",
                "loader",
                "detail",
                "Reusable loading-state shell.",
                "Loading",
                "Fetching latest data...",
                category="state",
                object_kind="state_surface",
            ),
            WorkbenchPanelType(
                "error_state_shell",
                "Error-State Shell",
                "alert-triangle",
                "detail",
                "Reusable error-state shell with retry affordance.",
                "Error",
                "Request failed. Try again.",
                category="state",
                object_kind="state_surface",
            ),
            WorkbenchPanelType(
                "divider_utility",
                "Divider / Utility",
                "separator-horizontal",
                "aux",
                "Divider utility for layout rhythm.",
                "Divider",
                "-----",
                category="utility",
                object_kind="chrome_utility",
            ),
            WorkbenchPanelType(
                "spacer_utility",
                "Spacer / Utility",
                "minus",
                "aux",
                "Spacing and separator utility.",
                "Spacer",
                "Utility space",
                category="utility",
                object_kind="chrome_utility",
            ),
        ]
        return {item.panel_type: item for item in specs}

    def _populate_editor_type_controls(self) -> None:
        self.editor_panel_type_combo.clear()
        self.editor_add_type_combo.clear()
        categories: set[str] = {"all"}
        for panel_type in self._panel_type_registry.values():
            self.editor_panel_type_combo.addItem(panel_type.title, panel_type.panel_type)
            self.editor_add_type_combo.addItem(panel_type.title, panel_type.panel_type)
            categories.add(panel_type.category)
        self.editor_palette_category_combo.blockSignals(True)
        self.editor_palette_category_combo.clear()
        self.editor_palette_category_combo.addItem("all", "all")
        for category in sorted(item for item in categories if item != "all"):
            self.editor_palette_category_combo.addItem(category.replace("_", " "), category)
        self.editor_palette_category_combo.setCurrentIndex(0)
        self.editor_palette_category_combo.blockSignals(False)
        self.editor_provider_combo.clear()
        self.editor_provider_combo.addItem("(none)", "")
        for provider in list_data_providers():
            self.editor_provider_combo.addItem(provider.provider_id, provider.provider_id)
        self.editor_chart_style_combo.clear()
        for style in list_chart_styles():
            label = f"{style.title} ({style.style_id})"
            self.editor_chart_style_combo.addItem(label, style.style_id)
        self.editor_chart_palette_combo.clear()
        self.editor_chart_palette_combo.addItem("Auto (from style)", "auto")
        for palette in list_chart_palettes():
            label = f"{palette.title} ({palette.palette_id})"
            self.editor_chart_palette_combo.addItem(label, palette.palette_id)
        self._refresh_insert_palette()

    def _refresh_editor_provider_combo(self) -> None:
        current = str(self.editor_provider_combo.currentData() or "")
        self.editor_provider_combo.blockSignals(True)
        self.editor_provider_combo.clear()
        self.editor_provider_combo.addItem("(none)", "")
        for provider in list_data_providers():
            self.editor_provider_combo.addItem(provider.provider_id, provider.provider_id)
        self.editor_provider_combo.blockSignals(False)
        if current:
            self._set_combo_data(self.editor_provider_combo, current)

    def _refresh_insert_palette(self) -> None:
        query = str(self.editor_palette_search.text() or "").strip().lower()
        category = str(self.editor_palette_category_combo.currentData() or "all").strip().lower()
        current_panel_type = self._selected_palette_panel_type() or str(self.editor_add_type_combo.currentData() or "")
        self.editor_palette_list.blockSignals(True)
        self.editor_palette_list.clear()
        matched = 0
        for panel_type in self._panel_type_registry.values():
            haystack = " ".join(
                [
                    panel_type.panel_type,
                    panel_type.title,
                    panel_type.description,
                    panel_type.category,
                    panel_type.object_kind,
                ]
            ).lower()
            if query and query not in haystack:
                continue
            if category != "all" and panel_type.category.lower() != category:
                continue
            recent_mark = "★ " if panel_type.panel_type in self._palette_recent[:5] else ""
            label = f"{recent_mark}{panel_type.title} · {panel_type.category.replace('_', ' ')}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, panel_type.panel_type)
            item.setToolTip(panel_type.description)
            icon = get_icon(panel_type.icon_name or "component")
            if not icon.isNull():
                item.setIcon(icon)
            self.editor_palette_list.addItem(item)
            matched += 1
        self.editor_palette_list.blockSignals(False)

        if matched == 0:
            self.editor_palette_summary.setText("No insertable objects match current palette filters.")
            self.editor_add_type_combo.setCurrentIndex(0 if self.editor_add_type_combo.count() else -1)
            return

        target_panel_type = current_panel_type
        selected_row = 0
        for row in range(self.editor_palette_list.count()):
            item = self.editor_palette_list.item(row)
            panel_type = str(item.data(Qt.UserRole) or "")
            if panel_type == target_panel_type:
                selected_row = row
                break
        self.editor_palette_list.setCurrentRow(selected_row)
        selected_item = self.editor_palette_list.item(selected_row)
        if selected_item is not None:
            self._on_palette_selected(selected_item, None)

    def _on_palette_selected(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        if current is None:
            return
        panel_type = str(current.data(Qt.UserRole) or "").strip().lower()
        if not panel_type:
            return
        spec = self._panel_type_registry.get(panel_type)
        if spec is None:
            return
        self._set_combo_data(self.editor_add_type_combo, panel_type)
        if spec.allowed_slots:
            self._set_combo_data(self.editor_add_slot_combo, spec.allowed_slots[0])
        allowed_slots = ", ".join(spec.allowed_slots) if spec.allowed_slots else "main/side/status"
        heavy = "heavy" if spec.heavy else "light"
        self.editor_palette_summary.setText(
            f"{spec.title} · kind={spec.object_kind} · slots={allowed_slots} · {heavy}\n{spec.description}"
        )

    def _selected_palette_panel_type(self) -> str:
        item = self.editor_palette_list.currentItem()
        if item is None:
            return ""
        return str(item.data(Qt.UserRole) or "").strip().lower()

    def _refresh_editor_contexts(self, *, select_context: str | None = None) -> None:
        current = select_context or str(self.editor_context_combo.currentData() or "")
        self.editor_context_combo.blockSignals(True)
        self.editor_context_combo.clear()
        live_contexts = sorted(self._editor_templates.keys())
        for context_id in live_contexts:
            session = self._editor_sessions.get(context_id)
            if session is None:
                continue
            active = sum(1 for item in session.dynamic_working if item.visible and item.state == "visible")
            label = f"{context_id} · {session.source_kind} · active:{active}"
            self.editor_context_combo.addItem(label, context_id)
        self.editor_context_combo.blockSignals(False)
        if self.editor_context_combo.count() == 0:
            self._set_editor_controls_enabled(False)
            self.editor_source_value.setText("(none)")
            self.editor_dirty_value.setText("clean")
            return
        self._set_editor_controls_enabled(True)
        selected_index = 0
        if current:
            for index in range(self.editor_context_combo.count()):
                if str(self.editor_context_combo.itemData(index) or "") == current:
                    selected_index = index
                    break
        self.editor_context_combo.setCurrentIndex(selected_index)
        self._load_editor_for_current_context()

    def _set_editor_controls_enabled(self, enabled: bool) -> None:
        controls = [
            self.editor_panel_combo,
            self.editor_panel_type_combo,
            self.editor_slot_combo,
            self.editor_role_combo,
            self.editor_state_combo,
            self.editor_visible_check,
            self.editor_title_input,
            self.editor_subtitle_input,
            self.editor_icon_input,
            self.editor_variant_combo,
            self.editor_density_combo,
            self.editor_width_policy_combo,
            self.editor_padding_combo,
            self.editor_height_policy_combo,
            self.editor_height_slider,
            self.editor_chart_mode_combo,
            self.editor_chart_style_combo,
            self.editor_chart_palette_combo,
            self.editor_chart_grid_check,
            self.editor_chart_glow_check,
            self.editor_chart_markers_check,
            self.editor_chart_smooth_check,
            self.editor_chart_line_slider,
            self.editor_chart_fill_slider,
            self.editor_provider_combo,
            self.editor_query_input,
            self.editor_options_input,
            self.editor_widget_object_name_input,
            self.editor_widget_tooltip_input,
            self.editor_widget_enabled_check,
            self.editor_button_text_input,
            self.editor_button_icon_input,
            self.editor_button_checkable_check,
            self.editor_button_checked_check,
            self.editor_button_style_variant_combo,
            self.editor_behavior_action_type_combo,
            self.editor_behavior_command_id_input,
            self.editor_behavior_target_panel_input,
            self.editor_behavior_task_ref_input,
            self.editor_behavior_payload_input,
            self.editor_text_input,
            self.editor_main_slider,
            self.editor_side_slider,
            self.editor_apply_split,
            self.editor_palette_search,
            self.editor_palette_category_combo,
            self.editor_palette_list,
            self.editor_insert_target_combo,
            self.editor_insert_position_combo,
            self.editor_add_type_combo,
            self.editor_add_slot_combo,
            self.editor_add_button,
            self.editor_apply_button,
            self.editor_move_up_button,
            self.editor_move_down_button,
            self.editor_move_left_button,
            self.editor_move_right_button,
            self.editor_duplicate_button,
            self.editor_hide_button,
            self.editor_reopen_button,
            self.editor_clone_to_tab_button,
            self.editor_remove_button,
            self.editor_reset_button,
            self.editor_save_clone_button,
            self.editor_open_clone_button,
        ]
        for control in controls:
            control.setEnabled(bool(enabled))
        if not enabled:
            self._set_slot_shell_edit_lock(False)

    def _set_slot_shell_edit_lock(self, locked: bool) -> None:
        mutable_controls = [
            self.editor_panel_type_combo,
            self.editor_slot_combo,
            self.editor_state_combo,
            self.editor_visible_check,
            self.editor_move_up_button,
            self.editor_move_down_button,
            self.editor_move_left_button,
            self.editor_move_right_button,
            self.editor_hide_button,
            self.editor_remove_button,
            self.editor_duplicate_button,
        ]
        for control in mutable_controls:
            control.setEnabled(not bool(locked))

    def _on_editor_context_changed(self, _index: int) -> None:
        self._load_editor_for_current_context()

    def _on_editor_panel_changed(self, _index: int) -> None:
        session = self._current_editor_session()
        if session is None:
            return
        panel_id = str(self.editor_panel_combo.currentData() or "")
        if panel_id:
            self._set_selected_editor_panel(session, panel_id)

    def _load_editor_for_current_context(self) -> None:
        session = self._current_editor_session()
        template = self._current_editor_template()
        if session is None or template is None:
            self.editor_status.setText("Open a preview to start interactive editing.")
            self.editor_source_value.setText("(none)")
            self.editor_dirty_value.setText("clean")
            self.editor_hidden_summary.setText("Hidden panels: 0")
            self.editor_panel_combo.clear()
            self._set_slot_shell_edit_lock(False)
            return
        self.editor_main_slider.setValue(int(session.split_working[0]))
        self.editor_side_slider.setValue(int(session.split_working[1]))
        self._refresh_editor_provider_combo()
        self._refresh_insert_palette()
        self._refresh_editor_panel_combo(session, template)
        if not session.selected_panel_id and self.editor_panel_combo.count() > 0:
            session.selected_panel_id = str(self.editor_panel_combo.itemData(0) or "")
        if session.selected_panel_id:
            self._set_selected_editor_panel(session, session.selected_panel_id)
        else:
            self._set_slot_shell_edit_lock(False)
        self._sync_editor_status(session)

    def _current_editor_context_id(self) -> str:
        return str(self.editor_context_combo.currentData() or "").strip()

    def _current_editor_session(self) -> WorkbenchEditorSession | None:
        context_id = self._current_editor_context_id()
        if not context_id:
            return None
        return self._editor_sessions.get(context_id)

    def _current_editor_template(self) -> GlassPanelTemplate | None:
        context_id = self._current_editor_context_id()
        if not context_id:
            return None
        return self._editor_templates.get(context_id)

    def _refresh_editor_panel_combo(self, session: WorkbenchEditorSession, template: GlassPanelTemplate) -> None:
        self.editor_panel_combo.blockSignals(True)
        self.editor_panel_combo.clear()
        for panel_id in template.panel_ids():
            panel = template.panel(panel_id)
            if panel is None:
                continue
            slot = self._panel_slot(template, panel_id)
            panel_state = self._panel_state_for_session(session, panel_id) or {}
            panel_type = str(panel_state.get("panel_type") or "unknown")
            state = str(panel_state.get("state") or "visible")
            visible = bool(panel_state.get("visible", True))
            visibility = "hidden" if not visible else state
            shell_tag = " · shell" if self._is_structural_slot_shell(template, panel_id) else ""
            label = f"{panel_id} · {slot} · {panel_type} · {visibility}{shell_tag}"
            self.editor_panel_combo.addItem(label, panel_id)
        self.editor_panel_combo.blockSignals(False)
        if self.editor_panel_combo.count() == 0:
            return
        target = session.selected_panel_id or str(self.editor_panel_combo.itemData(0) or "")
        for index in range(self.editor_panel_combo.count()):
            if str(self.editor_panel_combo.itemData(index) or "") == target:
                self.editor_panel_combo.setCurrentIndex(index)
                return
        self.editor_panel_combo.setCurrentIndex(0)

    def _panel_slot(self, template: GlassPanelTemplate, panel_id: str) -> str:
        panel = template.panel(panel_id)
        if panel is None:
            return "main"
        if self._is_structural_slot_shell(template, panel_id):
            normalized = str(panel_id or "").strip().lower()
            if normalized == "side":
                return "side"
            return "main"
        for slot_name, layout in (
            ("main", template.slots.main_slot),
            ("side", template.slots.side_slot),
            ("status", template.slots.status_slot),
        ):
            for index in range(layout.count()):
                if layout.itemAt(index).widget() is panel:
                    return slot_name
        return "main"

    def _is_structural_slot_shell(self, template: GlassPanelTemplate, panel_id: str) -> bool:
        return bool(getattr(template, "panel_is_slot_shell", lambda _panel_id: False)(panel_id))

    def _slot_panel_ids(self, template: GlassPanelTemplate, slot: str) -> list[str]:
        layout = {
            "main": template.slots.main_slot,
            "side": template.slots.side_slot,
            "status": template.slots.status_slot,
        }.get(slot, template.slots.main_slot)
        values: list[str] = []
        for index in range(layout.count()):
            widget = layout.itemAt(index).widget()
            if isinstance(widget, GlassPanelFrame):
                values.append(widget.panel_id)
        return values

    def _core_panel_state(self, template: GlassPanelTemplate) -> dict[str, dict[str, Any]]:
        payload: dict[str, dict[str, Any]] = {}
        index_map: dict[str, int] = {}
        for slot_name in ("main", "side", "status"):
            for index, panel_id in enumerate(self._slot_panel_ids(template, slot_name)):
                index_map[panel_id] = index
        for panel_id in template.panel_ids():
            panel = template.panel(panel_id)
            if panel is None:
                continue
            role = str(panel.property("panelRole") or "workspace")
            panel_type = "text_markdown"
            if role == "metrics":
                panel_type = "metrics_kpi"
            elif role in {"detail", "inspector"}:
                panel_type = "json_diag"
            elif role == "data":
                panel_type = "table_grid"
            slot_shell = bool(
                getattr(template, "panel_is_slot_shell", lambda _panel_id: False)(panel_id)
            )
            state_value = str(panel.property("panelState") or "visible")
            visible_value = bool(panel.isVisible())
            if slot_shell:
                state_value = "visible"
                visible_value = True
            widget_props = default_widget_props(
                panel_type,
                title=self._panel_title(panel),
                text=self._panel_subtitle(panel),
            )
            payload[panel_id] = {
                "title": self._panel_title(panel),
                "subtitle": self._panel_subtitle(panel),
                "slot": self._panel_slot(template, panel_id),
                "index": int(index_map.get(panel_id, 0)),
                "role": role,
                "state": state_value,
                "visible": visible_value,
                "panel_type": panel_type,
                "icon_name": "",
                "text": self._panel_subtitle(panel),
                "variant": "default",
                "density": "compact",
                "width_policy": "stretch",
                "padding": "normal",
                "data_provider_id": "",
                "data_query_id": "",
                "chart_mode": "line",
                "chart_style_id": "silver_line",
                "chart_palette_id": "auto",
                "chart_show_grid": True,
                "chart_show_glow": True,
                "chart_show_markers": False,
                "chart_smooth": True,
                "chart_line_width": 2,
                "chart_fill_alpha": 26,
                "height_policy": "auto",
                "panel_height": 0,
                "list_options": (),
                "widget_props": normalize_widget_props(panel_type, widget_props),
                "behavior": default_behavior_binding(),
                "slot_shell": slot_shell,
                "user_hidden": False,
                "content_override": False,
                "dynamic": False,
            }
        return payload

    def _split_state(self, template: GlassPanelTemplate) -> tuple[int, int]:
        splitter = template.layout_controller.splitters.get("main_side")
        if splitter is None:
            return (70, 30)
        sizes = splitter.sizes()
        if len(sizes) < 2:
            return (70, 30)
        total = max(1, sizes[0] + sizes[1])
        return (int((sizes[0] * 100) / total), int((sizes[1] * 100) / total))

    def _panel_title(self, panel: GlassPanelFrame) -> str:
        labels = panel.findChildren(QLabel)
        for label in labels:
            name = str(label.accessibleName() or "")
            if "glass_panel_title_" in name:
                return label.text()
        return panel.panel_id

    def _panel_subtitle(self, panel: GlassPanelFrame) -> str:
        labels = panel.findChildren(QLabel)
        for label in labels:
            name = str(label.accessibleName() or "")
            if "glass_panel_subtitle_" in name:
                return label.text()
        return ""

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._layout_window_resize_grips()
        width = self.width()
        if not hasattr(self, "main_split"):
            return
        sizes = self.main_split.sizes()
        bucket = "wide"
        if width < 1120:
            bucket = "narrow"
        elif width < 1360:
            bucket = "medium"
        if not self._catalog_panel_visible and not self._inspector_panel_visible:
            if sum(sizes) <= 0:
                self.main_split.setSizes([0, 1, 0])
            else:
                self.main_split.setSizes([0, max(1, int(sizes[1] if len(sizes) > 1 else 1)), 0])
            self._responsive_bucket = bucket
            return

        if bucket == self._responsive_bucket:
            return
        self._responsive_bucket = bucket

        if bucket == "narrow":
            default_nav, default_inspect = 180, 250
        elif bucket == "medium":
            default_nav, default_inspect = 200, 280
        else:
            default_nav, default_inspect = 220, 320

        total = sum(sizes) if sum(sizes) > 0 else max(1, width)
        nav = int(sizes[0]) if self._catalog_panel_visible and len(sizes) > 0 else 0
        inspect = int(sizes[2]) if self._inspector_panel_visible and len(sizes) > 2 else 0
        if self._catalog_panel_visible and nav <= 0:
            nav = default_nav
        if self._inspector_panel_visible and inspect <= 0:
            inspect = default_inspect
        center = max(620, total - nav - inspect)
        self.main_split.setSizes([nav if self._catalog_panel_visible else 0, center, inspect if self._inspector_panel_visible else 0])

    def _refresh_categories(self) -> None:
        selected = self._selected_category()
        self.category_list.blockSignals(True)
        self.category_list.clear()
        all_entries = list_catalog_entries(search=None)
        self._category_counts = {}
        for entry in all_entries:
            self._category_counts[entry.category] = int(self._category_counts.get(entry.category, 0)) + 1
        self._category_tags = {
            category: list_catalog_tags(category=category)
            for category in list_catalog_categories()
        }
        total_count = len(all_entries)

        categories = ("All",) + list_catalog_categories()
        category_icons = {
            "all": "layers",
            "compositions": "layout-dashboard",
            "controls & assets": "component",
            "data dashboards": "database",
            "presets": "sliders-horizontal",
            "primitives": "box",
            "runtime & integration": "cpu",
            "themes": "sparkles",
        }
        for category in categories:
            if category == "All":
                display = f"All ({total_count})"
            else:
                display = f"{category} ({self._category_counts.get(category, 0)})"
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, category)
            icon = get_icon(category_icons.get(category.strip().lower(), "layers"))
            if not icon.isNull():
                item.setIcon(icon)
            self.category_list.addItem(item)
        self.category_list.blockSignals(False)
        self._select_category(selected if selected else "All")

    def _refresh_entries(self) -> None:
        selected_entry = self._selected_entry_id
        category = self._selected_category()
        query = self.search_input.text().strip()
        tags = self._selected_tags()
        entries = list_catalog_entries(
            category=None if category.lower() == "all" else category,
            search=query,
            tags=tags,
        )

        self._entry_order = [entry.entry_id for entry in entries]
        self.entry_list.blockSignals(True)
        self.entry_list.clear()
        if not entries:
            selected_tags_text = ", ".join(tags) if tags else "(none)"
            empty = QListWidgetItem(
                f"No entries for category '{category}' with query '{query or '(none)'}' and tags '{selected_tags_text}'."
            )
            empty.setFlags(Qt.NoItemFlags)
            self.entry_list.addItem(empty)
            self.entry_list.blockSignals(False)
            self._selected_entry_id = None
            self._show_entry_detail(None)
            self.catalog.set_status_text("No entries found for current filter. Try clearing query/tags.")
            return

        for entry in entries:
            item = QListWidgetItem(self._entry_text(entry))
            item.setData(Qt.UserRole, entry.entry_id)
            item.setToolTip(entry.description or entry.subtitle or entry.title)
            icon = get_icon(entry.icon_name or "layers")
            if not icon.isNull():
                item.setIcon(icon)
            self.entry_list.addItem(item)
        self.entry_list.blockSignals(False)

        if selected_entry and selected_entry in self._entry_order:
            self._select_entry(selected_entry)
        else:
            first = entries[0]
            self._select_entry(first.entry_id)

        self.catalog.set_status_text(
            f"{len(entries)} entries available in '{category}'"
            + (f" filtered by query='{query}'." if query else "")
            + (f" tags={','.join(tags)}." if tags else ".")
        )

    def _on_entry_selected(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        entry_id = current.data(Qt.UserRole) if current is not None else None
        if not entry_id:
            self._selected_entry_id = None
            self._show_entry_detail(None)
            return
        self._selected_entry_id = str(entry_id)
        entry = get_catalog_entry(self._selected_entry_id)
        self._show_entry_detail(entry)

    def _show_entry_detail(self, entry: GlassCatalogEntry | None) -> None:
        if entry is None:
            self.preview_title.setText("No catalog entry selected.")
            self.preview_subtitle.setText("Choose an entry from the left rail, or clear active query/tag filters.")
            self.meta_title.setText("Entry Details")
            self.meta_summary.setText("No entry selected.")
            self.meta_kind_value.setText("-")
            self.meta_origin_value.setText("-")
            self.meta_layer_value.setText("-")
            self.meta_builder_value.setText("-")
            self.meta_hint_value.setText("-")
            self.meta_cap_value.setText("-")
            self.meta_best_for_value.setText("-")
            self.meta_use_when.setText("")
            self.meta_use_when.setVisible(False)
            self.meta_tags.setText("")
            self.meta_tags.setVisible(False)
            self.meta_text.setPlainText("")
            self.related_list.clear()
            self.selected_data_binding.setPlainText("")
            self.query_probe_text.setPlainText("")
            self._refresh_runtime_inspector(None)
            return

        self.preview_title.setText(entry.title)
        self.preview_subtitle.setText(entry.subtitle or entry.description or "No subtitle.")
        category_count = self._category_counts.get(entry.category, 0)
        self.meta_title.setText(f"{entry.category} ({category_count}) · {entry.status.upper()}")
        hint_parts = []
        if entry.preset_hint:
            hint_parts.append(f"Preset: {entry.preset_hint}")
        if entry.theme_hint:
            hint_parts.append(f"Theme: {entry.theme_hint}")
        if entry.required_capabilities:
            hint_parts.append(f"Capabilities: {', '.join(entry.required_capabilities)}")
        if entry.icon_name:
            hint_parts.append(f"Icon: {entry.icon_name}")
        self.meta_summary.setText(" | ".join(hint_parts) if hint_parts else "No capability hints.")
        self.meta_kind_value.setText(self._entry_kind(entry))
        self.meta_origin_value.setText(self._entry_origin(entry))
        self.meta_layer_value.setText(self._layer_boundary_for_entry(entry))
        self.meta_builder_value.setText(self._builder_ref(entry))
        self.meta_hint_value.setText(", ".join(hint_parts) if hint_parts else "(none)")
        self.meta_cap_value.setText(", ".join(entry.required_capabilities) if entry.required_capabilities else "(none)")
        self.meta_best_for_value.setText(self._best_for_note(entry))
        use_when = self._use_when_note(entry)
        self.meta_use_when.setText(f"Use when: {use_when}")
        self.meta_use_when.setVisible(True)
        if entry.tags:
            self.meta_tags.setText(f"Tags: {', '.join(entry.tags)}")
        else:
            category_tags = self._category_tags.get(entry.category, ())
            self.meta_tags.setText(f"Category tags: {', '.join(category_tags[:8])}" if category_tags else "Tags: (none)")
        self.meta_tags.setVisible(True)
        self.meta_text.setPlainText(
            json.dumps(
                {
                    "id": entry.entry_id,
                    "title": entry.title,
                    "subtitle": entry.subtitle,
                    "description": entry.description,
                    "category": entry.category,
                    "status": entry.status,
                    "tags": list(entry.tags),
                    "keywords": list(entry.keywords),
                    "preset_hint": entry.preset_hint,
                    "theme_hint": entry.theme_hint,
                    "required_capabilities": list(entry.required_capabilities),
                    "best_for": self._best_for_note(entry),
                    "use_when": use_when,
                    "category_tag_suggestions": list(self._category_tags.get(entry.category, ())),
                    "sort_order": entry.sort_order,
                    "metadata": entry.metadata,
                    "builder_ref": self._builder_ref(entry),
                    "layer_boundary": self._layer_boundary_for_entry(entry),
                    "entry_kind": self._entry_kind(entry),
                    "entry_origin": self._entry_origin(entry),
                },
                indent=2,
                ensure_ascii=True,
            )
        )
        self._refresh_related(entry)
        self._refresh_data_inspector(entry)
        self._refresh_runtime_inspector(entry)

    def _builder_ref(self, entry: GlassCatalogEntry) -> str:
        if entry.builder is None:
            return "(no builder)"
        module = getattr(entry.builder, "__module__", "")
        qualname = getattr(entry.builder, "__qualname__", getattr(entry.builder, "__name__", "callable"))
        if module:
            return f"{module}.{qualname}"
        return str(qualname)

    def _entry_kind(self, entry: GlassCatalogEntry) -> str:
        category = str(entry.category or "").lower()
        if category == "data dashboards":
            return "provider-backed dashboard"
        if category == "runtime & integration":
            return "runtime/integration showcase"
        if category == "controls & assets":
            return "asset/control gallery item"
        if category == "primitives":
            return "primitive showcase"
        if category == "presets":
            return "preset profile"
        if category == "themes":
            return "theme profile"
        if category == "compositions":
            return "composition example"
        return "catalog entry"

    def _entry_origin(self, entry: GlassCatalogEntry) -> str:
        entry_id = str(entry.entry_id or "").strip().lower()
        if entry_id.startswith(("example.", "preset.", "theme.", "primitive.", "runtime.", "integration.", "data.", "asset.")):
            return "built-in catalog"
        return "registered extension"

    def _layer_boundary_for_entry(self, entry: GlassCatalogEntry) -> str:
        category = str(entry.category or "").strip().lower()
        if category in {"controls & assets", "primitives", "presets", "themes"}:
            return "framework core"
        if category in {"data dashboards"}:
            return "data/provider layer"
        if category in {"runtime & integration"}:
            return "runtime + integration boundary"
        if category in {"compositions"}:
            return "example/composition layer"
        return "framework example layer"

    def _architecture_boundaries_note(self) -> str:
        return (
            "Architecture boundaries (workbench scope):\n"
            "- Framework Core: reusable primitives, controls, themes, config, shell template.\n"
            "- Example/Workbench Layer: catalog/workbench exploration, preview and inspection only.\n"
            "- Data/Provider Layer: DataQuery/DataResult + provider registry; no app-domain coupling.\n"
            "- Runtime Layer: workspace orchestration and visibility/persistence controls.\n"
            "- Integration Boundary: neutral command/query/snapshot/event contracts + adapters.\n\n"
            "Guardrails:\n"
            "- Workbench does not modify integration runtime bridge responsibilities.\n"
            "- Workbench does not own persistence schemas or transport concerns.\n"
            "- Workbench consumes existing APIs and surfaces discoverability/diagnostics."
        )

    def _dashboard_spec_for_entry(self, entry_id: str | None) -> DashboardCatalogEntrySpec | None:
        if not entry_id:
            return None
        return self._dashboard_specs_by_id.get(str(entry_id).strip().lower())

    def _result_age_seconds(self, refreshed_at_utc: str | None) -> float | None:
        value = str(refreshed_at_utc or "").strip()
        if not value:
            return None
        try:
            refreshed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
            age = (dt.datetime.now(dt.timezone.utc) - refreshed.astimezone(dt.timezone.utc)).total_seconds()
            return max(0.0, float(age))
        except Exception:  # noqa: BLE001
            return None

    def _refresh_data_inspector(self, entry: GlassCatalogEntry | None) -> None:
        if entry is None:
            self.data_binding_summary.setText("No entry selected.")
            self.selected_data_binding.setPlainText("No entry selected.")
            return
        spec = self._dashboard_spec_for_entry(entry.entry_id)
        payload: dict[str, Any] = {
            "entry_id": entry.entry_id,
            "entry_kind": self._entry_kind(entry),
            "layer_boundary": self._layer_boundary_for_entry(entry),
            "builder_ref": self._builder_ref(entry),
            "entry_origin": self._entry_origin(entry),
        }
        if spec is not None:
            provider_info = describe_data_provider(spec.provider_id)
            diagnostics = provider_info.get("diagnostics", {})
            payload.update(
                {
                    "provider_id": spec.provider_id,
                    "query_id": spec.query_id,
                    "query_params": dict(spec.query_params),
                    "query_context": dict(spec.query_context),
                    "provider_meta": provider_info.get("meta", {}),
                    "provider_diagnostics": provider_info.get("diagnostics", {}),
                    "refresh_behavior": "provider policy-defined (manual or polling)",
                    "states_supported": ["loading", "ready", "empty", "error", "stale"],
                    "freshness_contract": "Use Probe Selected Query for stale/fresh certainty.",
                }
            )
            self.data_binding_summary.setText(
                "Provider-backed entry.\n"
                f"provider={spec.provider_id} | query={spec.query_id} | "
                f"status={diagnostics.get('status', 'unknown')} | "
                f"latency={diagnostics.get('last_latency_ms', '?')}ms | freshness=probe-required"
            )
        else:
            payload["note"] = "Selected entry is not a provider-backed data dashboard."
            self.data_binding_summary.setText(
                "This entry is not provider-backed. Probe actions are available for Data Dashboards."
            )
        self.selected_data_binding.setPlainText(json.dumps(payload, indent=2, ensure_ascii=True))

    def _refresh_provider_list(self) -> None:
        if not self._inspector_panel_visible and not self._inspector_initialized:
            return
        register_builtin_data_providers()
        self._refresh_editor_provider_combo()
        providers = list_data_providers()
        current_provider_id = self._current_provider_id()
        self.provider_list.blockSignals(True)
        self.provider_list.clear()
        if not providers:
            empty = QListWidgetItem("No providers registered.")
            empty.setFlags(Qt.NoItemFlags)
            self.provider_list.addItem(empty)
            self.provider_list.blockSignals(False)
            self.provider_summary.setText("No provider metadata available.")
            self.provider_details.setPlainText("No provider metadata available.")
            return
        for provider in providers:
            label = (
                f"{provider.title}\n"
                f"{provider.provider_id} · {provider.source_kind} · {provider.status}"
            )
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, provider.provider_id)
            icon_name = "database" if provider.status == "ready" else ("alert-triangle" if provider.status == "error" else "clock")
            icon = get_icon(icon_name)
            if not icon.isNull():
                item.setIcon(icon)
            self.provider_list.addItem(item)
        self.provider_list.blockSignals(False)
        if current_provider_id:
            self._select_provider(current_provider_id)
        elif self.provider_list.count() > 0:
            self.provider_list.setCurrentRow(0)

    def _on_provider_selected(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        provider_id = str(current.data(Qt.UserRole) or "").strip() if current is not None else ""
        if not provider_id:
            self.provider_summary.setText("Select a provider to inspect metadata/diagnostics.")
            self.provider_details.setPlainText("Select a provider to inspect metadata/diagnostics.")
            return
        payload = describe_data_provider(provider_id)
        meta = payload.get("meta", {})
        diagnostics = payload.get("diagnostics", {})
        self.provider_summary.setText(
            f"id={provider_id} | source={meta.get('source_kind', '?')} | "
            f"status={diagnostics.get('status', '?')} | latency={diagnostics.get('last_latency_ms', '?')}ms"
        )
        self.provider_details.setPlainText(json.dumps(payload, indent=2, ensure_ascii=True))

    def _current_provider_id(self) -> str:
        item = self.provider_list.currentItem()
        if item is None:
            return ""
        return str(item.data(Qt.UserRole) or "").strip().lower()

    def _select_provider(self, provider_id: str) -> None:
        target = str(provider_id or "").strip().lower()
        for index in range(self.provider_list.count()):
            item = self.provider_list.item(index)
            current = str(item.data(Qt.UserRole) or "").strip().lower()
            if current == target:
                self.provider_list.setCurrentRow(index)
                return

    def _probe_selected_query(self) -> None:
        if not self._inspector_panel_visible:
            self._set_inspector_panel_visible(True)
        entry = self._current_entry()
        spec = self._dashboard_spec_for_entry(entry.entry_id if entry else None)
        if spec is None:
            self.query_probe_text.setPlainText(
                "Selected entry is not provider-backed. Choose a 'Data Dashboards' entry to probe."
            )
            self.catalog.set_status_text("Probe query is only available for provider-backed dashboard entries.")
            return
        result = execute_data_query(
            DataQuery.create(
                spec.provider_id,
                query_id=spec.query_id,
                params=dict(spec.query_params),
                context=dict(spec.query_context),
            )
        )
        age_seconds = self._result_age_seconds(result.refreshed_at_utc)
        stale = result.is_stale()
        payload = {
            "provider_id": result.provider_id,
            "query_id": result.query_id,
            "state": result.normalized_state(),
            "is_stale": stale,
            "refresh_policy": result.refresh_policy.to_payload(),
            "counts": {
                "metrics": len(result.metrics),
                "rows": len(result.rows),
                "feed": len(result.feed),
            },
            "latency_ms": result.latency_ms,
            "refreshed_at_utc": result.refreshed_at_utc,
            "age_seconds": age_seconds,
            "summary": dict(result.summary),
            "error": result.error.to_payload() if result.error else None,
            "diagnostics": dict(result.diagnostics),
        }
        self.query_probe_text.setPlainText(json.dumps(payload, indent=2, ensure_ascii=True))
        stale_label = "STALE WARNING" if stale else "fresh"
        self.data_binding_summary.setText(
            f"Probe result: provider={result.provider_id} | query={result.query_id} | "
            f"state={result.normalized_state()} | stale={stale} ({stale_label}) | "
            f"age={age_seconds if age_seconds is not None else '?'}s | latency={result.latency_ms}ms"
        )
        self._set_status(
            f"Probed {spec.provider_id}:{spec.query_id} -> {result.normalized_state()} "
            f"(stale={stale}, age={age_seconds if age_seconds is not None else '?' }s).",
            level="warning" if stale else "success",
            context="data_probe",
        )
        self._refresh_provider_list()
        self._refresh_runtime_inspector(entry)

    def _refresh_runtime_button(self) -> None:
        if not self._inspector_panel_visible:
            self._set_inspector_panel_visible(True)
        self._integration_contracts_cache = None
        self._refresh_runtime_inspector(self._current_entry())
        self.catalog.set_status_text("Runtime diagnostics refreshed.")

    def _integration_contracts_summary(self) -> dict[str, Any]:
        if self._integration_contracts_cache is not None:
            return self._integration_contracts_cache
        service, _ = create_reference_workspace_service(debug=False, namespace="workspace")
        adapter = InProcessIntegrationAdapter(service)
        contracts = adapter.contracts()
        self._integration_contracts_cache = contracts
        return contracts

    def _refresh_runtime_inspector(self, entry: GlassCatalogEntry | None) -> None:
        if not self._inspector_panel_visible and not self._inspector_initialized:
            return
        contracts = self._integration_contracts_summary()
        providers = list_data_providers()
        selected_dashboard = self._dashboard_spec_for_entry(entry.entry_id if entry else None)
        payload = {
            "workbench": {
                "selected_entry_id": entry.entry_id if entry else None,
                "selected_entry_kind": self._entry_kind(entry) if entry else None,
                "selected_layer_boundary": self._layer_boundary_for_entry(entry) if entry else None,
                "selected_entry_origin": self._entry_origin(entry) if entry else None,
                "preview_instances_opened": self._preview_instance_counter,
                "workspace_active_budget": self._workspace_active_budget,
                "active_filters": {
                    "category": self._selected_category(),
                    "search": self.search_input.text().strip(),
                    "tags": list(self._selected_tags()),
                },
            },
            "catalog": {
                "total_entries_visible": len(self._entry_order),
                "category_counts": dict(self._category_counts),
                "categories_visible": sorted(set(item.category for item in list_catalog_entries(search=None))),
            },
            "providers": {
                "count": len(providers),
                "ids": [item.provider_id for item in providers],
                "source_kinds": sorted({item.source_kind for item in providers}),
            },
            "selected_dashboard_binding": {
                "provider_id": selected_dashboard.provider_id if selected_dashboard else None,
                "query_id": selected_dashboard.query_id if selected_dashboard else None,
            },
            "integration_boundary": {
                "protocol_version": contracts.get("diagnostics", {}).get("supported_protocol_versions", []),
                "command_count": len(contracts.get("endpoints", {}).get("commands", [])),
                "query_count": len(contracts.get("endpoints", {}).get("queries", [])),
                "snapshot_count": len(contracts.get("endpoints", {}).get("snapshots", [])),
                "diagnostics": contracts.get("diagnostics", {}),
                "sample_commands": [
                    item.get("endpoint")
                    for item in contracts.get("endpoints", {}).get("commands", [])[:5]
                ],
                "sample_queries": [
                    item.get("endpoint")
                    for item in contracts.get("endpoints", {}).get("queries", [])[:5]
                ],
                "sample_snapshots": [
                    item.get("endpoint")
                    for item in contracts.get("endpoints", {}).get("snapshots", [])[:5]
                ],
            },
            "action_trace": {
                "total_events": len(self._action_trace),
                "recent": list(self._action_trace[-30:]),
            },
        }
        protocol_versions = [str(item) for item in payload["integration_boundary"]["protocol_version"]]
        self.runtime_summary.setText(
            f"contracts v{','.join(protocol_versions) or '?'} | "
            f"commands={payload['integration_boundary']['command_count']} | "
            f"queries={payload['integration_boundary']['query_count']} | "
            f"snapshots={payload['integration_boundary']['snapshot_count']} | "
            f"providers={payload['providers']['count']} | trace={payload['action_trace']['total_events']}"
        )
        self.runtime_diagnostics_text.setPlainText(json.dumps(payload, indent=2, ensure_ascii=True))
        self._refresh_action_trace_view()

    def _best_for_note(self, entry: GlassCatalogEntry) -> str:
        if entry.best_for:
            return str(entry.best_for)
        category = str(entry.category or "").lower()
        if "data" in category:
            return "Operational monitoring, KPI review, and diagnostics-driven dashboards."
        if "controls" in category or "assets" in category:
            return "Composing reusable workstation controls and dense interaction surfaces."
        if "primitive" in category:
            return "Building reusable UI building blocks across multiple screens."
        if "runtime" in category:
            return "Testing orchestration, persistence, and integration boundary behaviors."
        return "General framework composition and visual exploration."

    def _use_when_note(self, entry: GlassCatalogEntry) -> str:
        if entry.use_when:
            return str(entry.use_when)
        if entry.metadata.get("use_when"):
            return str(entry.metadata.get("use_when"))
        if entry.keywords:
            return f"you need {', '.join(entry.keywords[:3])}."
        if entry.tags:
            return f"you are building {', '.join(entry.tags[:3])} surfaces."
        return "you need a reusable baseline composition."

    def _open_selected_preview(self) -> None:
        entry = self._ensure_entry_for_command()
        if entry is None:
            self.catalog.set_status_text("No catalog entries available to preview.")
            return
        tabs = self.catalog.workspace_tabs
        default_tab_id = self._default_workspace_tab_id()
        if tabs is not None and default_tab_id:
            tabs.set_active_tab(default_tab_id)
        if entry.builder is None:
            self.catalog.set_status_text(f"Entry '{entry.entry_id}' has no preview builder.")
            return
        try:
            widget = entry.builder(self.preview_host)
            if widget is None:
                raise RuntimeError("builder returned None")
        except Exception as exc:  # noqa: BLE001
            self.catalog.set_status_text(f"Preview failed for '{entry.entry_id}': {exc}")
            return
        self._configure_preview_widget(widget, for_workspace=False)
        self._render_preview_widget(widget, entry)
        self._set_preview_collapsed(False)
        if isinstance(widget, GlassPanelTemplate):
            self._ensure_editor_session(
                context_id="preview",
                template=widget,
                source_kind="catalog_entry",
                source_ref=entry.entry_id,
                entry_id=entry.entry_id,
                force_reset=True,
            )
            self._refresh_editor_contexts(select_context="preview")
        self.catalog.set_status_text(f"Preview opened for '{entry.title}'.")

    def _open_selected_in_workspace(self) -> None:
        entry = self._ensure_entry_for_command()
        if entry is None:
            self.catalog.set_status_text("No catalog entries available to open in workspace.")
            return
        if entry.builder is None:
            self.catalog.set_status_text(f"Entry '{entry.entry_id}' has no builder.")
            return
        if self.catalog.workspace_tabs is None:
            self._open_selected_preview()
            return

        try:
            self._preview_instance_counter += 1
            tab_id = f"catalog_{entry.entry_id}_{self._preview_instance_counter}"
            context_id = f"workspace:{tab_id}"
            host = _LazyMountHost(
                entry.title,
                factory=lambda: self._build_workspace_widget(entry, context_id=context_id),
                parent=self.catalog,
            )
            self._workspace_hosts[tab_id] = host
            self.catalog.add_workspace_tab(
                tab_id=tab_id,
                title=entry.title,
                widget=host,
                state="visible",
                icon_name=entry.icon_name or "layers",
                tooltip=entry.description,
                make_current=True,
                metadata={"catalog_entry_id": entry.entry_id},
            )
            self._enforce_workspace_budget()
            self._refresh_editor_contexts(select_context=context_id)
            self.catalog.set_status_text(f"'{entry.title}' added to workspace tabs.")
        except Exception as exc:  # noqa: BLE001
            self.catalog.set_status_text(f"Failed to add '{entry.title}' to workspace: {exc}")

    def _open_empty_workspace_tab(self) -> None:
        if self.catalog.workspace_tabs is None:
            self.catalog.set_status_text("Workspace tabs are disabled for this preset.")
            return
        self._workspace_counter += 1
        tab_id = f"scratch_{self._workspace_counter}"
        host = _LazyMountHost(
            "Scratch Workspace",
            factory=lambda: self._build_scratch_workspace_widget(tab_id),
            parent=self.catalog,
        )
        self._workspace_hosts[tab_id] = host
        self.catalog.add_workspace_tab(
            tab_id=tab_id,
            title=f"Workspace {self._workspace_counter}",
            widget=host,
            state="visible",
            icon_name="layers",
            tooltip="Empty workspace tab for quick experiments.",
            make_current=True,
            metadata={"catalog_entry_id": ""},
        )
        self._enforce_workspace_budget()
        self.catalog.set_status_text("Created new workspace tab. Use Add Content (Ctrl+K) to populate it.")

    def _close_active_workspace_tab(self) -> None:
        tabs = self.catalog.workspace_tabs
        if tabs is None:
            return
        tab_id = tabs.active_tab_id()
        if not tab_id:
            return
        if tab_id == self._default_workspace_tab_id():
            self.catalog.set_status_text("Default workspace tab cannot be closed.")
            return
        if self.catalog.remove_workspace_tab(tab_id):
            self._workspace_hosts.pop(tab_id, None)
            context_id = f"workspace:{tab_id}"
            if str(self._pending_candidate_context_id or "") == context_id:
                self._discard_pending_panel_candidate(announce=False)
            self._editor_sessions.pop(context_id, None)
            self._editor_templates.pop(context_id, None)
            self._enforce_workspace_budget()
            self._refresh_editor_contexts()
            self.catalog.set_status_text(f"Closed workspace tab '{tab_id}'.")

    def _default_workspace_tab_id(self) -> str:
        tabs = self.catalog.workspace_tabs
        if tabs is None:
            return ""
        tab_ids = tabs.tab_ids()
        return tab_ids[0] if tab_ids else ""

    def _build_workspace_widget(self, entry: GlassCatalogEntry, *, context_id: str) -> QWidget:
        if entry.builder is None:
            placeholder = QLabel(f"Entry '{entry.entry_id}' has no builder.", self.catalog)
            placeholder.setWordWrap(True)
            return placeholder
        try:
            widget = entry.builder(self.catalog)
        except Exception as exc:  # noqa: BLE001
            placeholder = QLabel(f"Failed to build '{entry.entry_id}': {exc}", self.catalog)
            placeholder.setWordWrap(True)
            return placeholder
        if widget is None:
            placeholder = QLabel(f"Entry '{entry.entry_id}' returned no widget.", self.catalog)
            placeholder.setWordWrap(True)
            return placeholder
        self._configure_preview_widget(widget, for_workspace=True)
        if isinstance(widget, GlassPanelTemplate):
            self._ensure_editor_session(
                context_id=context_id,
                template=widget,
                source_kind="workspace_tab",
                source_ref=context_id,
                entry_id=entry.entry_id,
                force_reset=False,
            )
            session = self._editor_sessions.get(context_id)
            if session is not None:
                self._apply_session_to_template(widget, session)
                self._bind_editor_click_targets(widget, context_id)
        return widget

    def _ensure_entry_for_command(self) -> GlassCatalogEntry | None:
        current = self._current_entry()
        if current is not None:
            return current
        if not self._catalog_initialized:
            self._set_catalog_panel_visible(True)
        current = self._current_entry()
        if current is not None:
            return current
        if self._entry_order:
            self._select_entry(self._entry_order[0])
            return self._current_entry()
        return None

    def _build_scratch_workspace_widget(self, tab_id: str) -> QWidget:
        config = GlassTemplateConfig(
            title="Blank Workspace",
            subtitle="Minimal editable workspace. Insert panels when needed.",
            eyebrow="WORKSPACE",
            with_chrome=False,
            regions=GlassRegionConfig(show_side=False, show_footer=False, show_status=False, main_side_sizes=(1000, 0)),
            tabs=GlassTabConfig(enabled=False),
        )
        template = GlassPanelTemplate(
            self.catalog,
            config=config,
            include_default_actions=False,
            show_side=False,
            show_footer=False,
            show_status=False,
            with_chrome=False,
            density="compact",
            typography_scale="lg",
        )
        template.cards.hero.hide()
        shell_layout = template.cards.shell.layout()
        if isinstance(shell_layout, QVBoxLayout):
            shell_layout.setContentsMargins(4, 4, 4, 4)
            shell_layout.setSpacing(4)
        template.clear_slot("main")
        template.clear_slot("side")
        template.clear_slot("status")
        hero = QWidget(template)
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(2, 2, 2, 2)
        hero_layout.setSpacing(6)
        title = QLabel("Blank Editor Workspace", hero)
        title.setProperty("role", "section")
        hint = QLabel(
            "This tab starts clean. Add content when you need it.",
            hero,
        )
        hint.setProperty("role", "panel_subtitle")
        hint.setWordWrap(True)
        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(6)
        add_button = QPushButton("Add Content", hero)
        add_button.setProperty("variant", "primary")
        add_button.clicked.connect(lambda: self._open_entry_picker(target_tab_id=tab_id))
        tools_button = QPushButton("Open Tools", hero)
        tools_button.setProperty("variant", "ghost")
        tools_button.clicked.connect(lambda: self._set_inspector_panel_visible(True))
        action_row.addWidget(add_button)
        action_row.addWidget(tools_button)
        action_row.addStretch(1)
        hero_layout.addWidget(title)
        hero_layout.addWidget(hint)
        hero_layout.addLayout(action_row)
        template.slots.main_slot.addWidget(hero)
        template.slots.main_slot.addStretch(1)

        context_id = f"workspace:{tab_id}"
        self._ensure_editor_session(
            context_id=context_id,
            template=template,
            source_kind="workspace_tab",
            source_ref=context_id,
            entry_id="",
            force_reset=False,
        )
        session = self._editor_sessions.get(context_id)
        if session is not None:
            self._apply_session_to_template(template, session)
            self._bind_editor_click_targets(template, context_id)
        return template

    def _configure_preview_widget(self, widget: QWidget, *, for_workspace: bool) -> None:
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        if isinstance(widget, GlassPanelTemplate):
            widget.set_density("compact")
            widget.set_typography_scale(self._text_size)
            widget.set_hide_single_tab_bar(True)
            if not for_workspace:
                widget.set_footer_visible(False)
                widget.set_status_visible(False)
            chrome = widget.findChild(QFrame, "WindowChrome")
            if chrome is not None:
                chrome.hide()
            widget.set_split_proportions(main=84, side=16)

    def _render_preview_widget(self, widget: QWidget, entry: GlassCatalogEntry) -> None:
        _clear_layout(self.preview_layout)
        widget.setParent(self.preview_host)
        self.preview_layout.addWidget(widget, 1)
        badge = QLabel(
            f"{entry.category} · {entry.status.upper()} · tags: {', '.join(entry.tags) if entry.tags else '(none)'}",
            self.preview_host,
        )
        badge.setProperty("role", "caption")
        badge.setWordWrap(True)
        self.preview_layout.addWidget(badge)

    def _clear_preview(self) -> None:
        _clear_layout(self.preview_layout)
        placeholder = QLabel(
            "Preview is idle.\nUse Add / Browse (Ctrl+K) to select and preview catalog content.",
            self.preview_host,
        )
        placeholder.setProperty("role", "panel_subtitle")
        placeholder.setWordWrap(True)
        self.preview_layout.addWidget(placeholder)
        self._editor_templates.pop("preview", None)
        self._editor_sessions.pop("preview", None)
        self._refresh_editor_contexts()
        self._set_preview_collapsed(True)
        self.catalog.set_status_text("Preview cleared.")

    def _enforce_workspace_budget(self) -> None:
        tabs = self.catalog.workspace_tabs
        if tabs is None:
            return
        active_tab = tabs.active_tab_id()
        existing = set(tabs.tab_ids())
        for stale_id in [key for key in self._workspace_hosts.keys() if key not in existing]:
            self._workspace_hosts.pop(stale_id, None)
        active_hosts = 0
        for tab_id, host in self._workspace_hosts.items():
            is_active = bool(tab_id == active_tab and active_hosts < self._workspace_active_budget)
            host.set_active(is_active)
            tabs.set_tab_state(tab_id, "visible" if is_active else "pending")
            tabs.set_tab_badge(tab_id, "live" if host.is_mounted() else "lazy")
            context_id = f"workspace:{tab_id}"
            mounted_widget = host._mounted if hasattr(host, "_mounted") else None
            if not isinstance(mounted_widget, GlassPanelTemplate):
                self._editor_templates.pop(context_id, None)
            else:
                self._editor_templates[context_id] = mounted_widget
            if is_active:
                active_hosts += 1

    def _toggle_motion(self) -> None:
        backdrop = getattr(self.catalog, "_glass_backdrop", None)
        if backdrop is None:
            return
        enabled = bool(getattr(backdrop, "_motion_enabled", True))
        set_motion_enabled = getattr(backdrop, "set_motion_enabled", None)
        if callable(set_motion_enabled):
            set_motion_enabled(not enabled)
            self.btn_toggle_motion.setText("Motion Off" if enabled else "Motion On")
            self.catalog.set_status_text("Backdrop motion disabled." if enabled else "Backdrop motion enabled.")

    def _on_scale_changed(self, _index: int) -> None:
        scale = str(self.scale_combo.currentData() or "lg").strip().lower() or "lg"
        factor_map = {
            "sm": 0.92,
            "md": 1.00,
            "lg": 1.12,
            "xl": 1.24,
        }
        self._text_size = scale if scale in factor_map else "lg"
        factor = float(factor_map.get(self._text_size, 1.12))
        if self._text_size in {"sm", "md"}:
            self.catalog.set_density("compact")
            self.catalog.set_tab_density("compact")
        else:
            self.catalog.set_density("cozy")
            self.catalog.set_tab_density("comfortable")
        self.catalog.set_typography_scale(self._text_size)
        self._apply_runtime_font_scale(factor)
        self._tune_template_density()
        self.catalog.set_status_text(f"Text Size set to {self._text_size.upper()}.")

    def _apply_runtime_font_scale(self, factor: float) -> None:
        clamped = max(0.86, min(1.36, float(factor)))
        target_size = max(9.0, min(15.5, self._base_font_point_size * clamped))
        font = self.font()
        font.setPointSizeF(target_size)
        self.setFont(font)
        self.catalog.setFont(font)
        dialog = getattr(self, "entry_picker_dialog", None)
        if isinstance(dialog, QDialog):
            dialog.setFont(font)

    def _toggle_data_debug(self) -> None:
        if not self._inspector_panel_visible:
            self._set_inspector_panel_visible(True)
        target = not self.selected_data_binding.isVisible()
        self.selected_data_binding.setVisible(target)
        self.query_probe_text.setVisible(target)
        self.provider_details.setVisible(target)

    def _clear_filters(self) -> None:
        self._set_catalog_panel_visible(False)
        self.search_input.clear()
        self.tags_input.clear()
        self._select_category("All")
        self._refresh_entries()
        if hasattr(self, "picker_search_input"):
            self.picker_search_input.clear()
            self.picker_category_combo.setCurrentIndex(0)
            self._refresh_picker_entries()
        self.catalog.set_status_text("Catalog filters cleared.")

    def _refresh_related(self, entry: GlassCatalogEntry) -> None:
        self.related_list.clear()
        related = self._related_entries(entry, limit=8)
        if not related:
            item = QListWidgetItem("No related entries found.")
            item.setFlags(Qt.NoItemFlags)
            self.related_list.addItem(item)
            return
        for related_entry in related:
            item = QListWidgetItem(f"{related_entry.title} · {related_entry.category}")
            item.setToolTip(related_entry.subtitle or related_entry.description)
            item.setData(Qt.UserRole, related_entry.entry_id)
            icon = get_icon(related_entry.icon_name or "layers")
            if not icon.isNull():
                item.setIcon(icon)
            self.related_list.addItem(item)

    def _related_entries(self, entry: GlassCatalogEntry, *, limit: int = 8) -> list[GlassCatalogEntry]:
        candidates = list_catalog_entries(search=None)
        target_tags = set(entry.tags)
        target_keywords = set(entry.keywords)
        scored: list[tuple[int, GlassCatalogEntry]] = []
        for item in candidates:
            if item.entry_id == entry.entry_id:
                continue
            score = 0
            if item.category == entry.category:
                score += 3
            score += len(target_tags.intersection(item.tags)) * 2
            score += len(target_keywords.intersection(item.keywords))
            if score <= 0:
                continue
            scored.append((score, item))
        scored.sort(key=lambda pair: (-pair[0], pair[1].sort_order, pair[1].title.lower()))
        return [item for _, item in scored[: max(1, int(limit))]]

    def _open_related_item(self, item: QListWidgetItem) -> None:
        entry_id = str(item.data(Qt.UserRole) or "").strip()
        if not entry_id:
            return
        self._select_entry(entry_id)

    def _entry_text(self, entry: GlassCatalogEntry) -> str:
        tags = ", ".join(entry.tags[:3]) if entry.tags else "no tags"
        subtitle = entry.subtitle or entry.description or ""
        return (
            f"{entry.title}\n"
            f"{subtitle}\n"
            f"{entry.category} · {entry.status.upper()} · {tags}"
        )

    def _selected_category(self) -> str:
        item = self.category_list.currentItem()
        if item is None:
            return "All"
        value = str(item.data(Qt.UserRole) or item.text() or "All").strip()
        return value or "All"

    def _selected_tags(self) -> tuple[str, ...]:
        raw = self.tags_input.text().strip()
        if not raw:
            return ()
        values: list[str] = []
        for item in raw.split(","):
            normalized = str(item or "").strip().lower()
            if normalized:
                values.append(normalized)
        return tuple(values)

    def _select_category(self, category: str) -> None:
        target = str(category or "All").strip().lower()
        for index in range(self.category_list.count()):
            item = self.category_list.item(index)
            value = str(item.data(Qt.UserRole) or item.text()).strip().lower()
            if value == target:
                self.category_list.setCurrentRow(index)
                return
        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)

    def _select_entry(self, entry_id: str) -> None:
        target = str(entry_id or "").strip().lower()
        for index in range(self.entry_list.count()):
            item = self.entry_list.item(index)
            if str(item.data(Qt.UserRole) or "").strip().lower() == target:
                self.entry_list.setCurrentRow(index)
                return

    def _current_entry(self) -> GlassCatalogEntry | None:
        if not self._selected_entry_id:
            return None
        return get_catalog_entry(self._selected_entry_id)

    def _ensure_editor_session(
        self,
        *,
        context_id: str,
        template: GlassPanelTemplate,
        source_kind: str,
        source_ref: str,
        entry_id: str,
        force_reset: bool,
    ) -> WorkbenchEditorSession:
        normalized_context = str(context_id or "").strip().lower()
        existing = self._editor_sessions.get(normalized_context)
        if existing is not None and not force_reset:
            self._editor_templates[normalized_context] = template
            self._bind_editor_click_targets(template, normalized_context)
            return existing

        core_state = self._core_panel_state(template)
        split_state = self._split_state(template)
        session = WorkbenchEditorSession(
            context_id=normalized_context,
            source_kind=str(source_kind or "catalog_entry").strip().lower(),
            source_ref=str(source_ref or "").strip(),
            entry_id=str(entry_id or "").strip(),
            core_baseline=deepcopy(core_state),
            core_working=deepcopy(core_state),
            dynamic_baseline=[],
            dynamic_working=[],
            split_baseline=tuple(split_state),
            split_working=tuple(split_state),
            panel_counter=0,
            selected_panel_id=None,
            dirty=False,
        )
        self._editor_sessions[normalized_context] = session
        self._editor_templates[normalized_context] = template
        self._bind_editor_click_targets(template, normalized_context)
        return session

    def _bind_editor_click_targets(self, template: GlassPanelTemplate, context_id: str) -> None:
        normalized = str(context_id or "").strip().lower()
        self._panel_click_map = {
            key: value for key, value in self._panel_click_map.items() if value[0] != normalized
        }
        for panel_id in template.panel_ids():
            panel = template.panel(panel_id)
            if panel is None:
                continue
            panel.setAttribute(Qt.WA_AcceptTouchEvents, True)
            self._panel_click_map[id(panel)] = (normalized, panel_id)
            panel.installEventFilter(self)
            for child in panel.findChildren(QWidget):
                child.setAttribute(Qt.WA_AcceptTouchEvents, True)
                self._panel_click_map[id(child)] = (normalized, panel_id)
                child.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        if self._handle_window_drag_event(watched, event):
            return True
        host = self._window_resize_host
        if host is not None and watched is host and event.type() in {
            QEvent.Type.Resize,
            QEvent.Type.WindowStateChange,
            QEvent.Type.Show,
        }:
            self._layout_window_resize_grips()
        mapped = self._panel_click_map.get(id(watched))
        event_type = event.type()
        touch_begin = getattr(QEvent.Type, "TouchBegin", QEvent.Type.User)
        touch_update = getattr(QEvent.Type, "TouchUpdate", QEvent.Type.User)
        touch_end = getattr(QEvent.Type, "TouchEnd", QEvent.Type.User)
        touch_cancel = getattr(QEvent.Type, "TouchCancel", QEvent.Type.User)

        if event_type in {QEvent.Type.MouseButtonPress, touch_begin}:
            if mapped is not None:
                context_id, panel_id = mapped
                self._select_editor_context(context_id, panel_id=panel_id)
                panel = self._mapped_panel_widget(context_id, panel_id)
                local_point = self._event_local_point(event)
                if panel is not None:
                    panel_local = panel.mapFromGlobal(self._event_global_point(event))
                    local_point = panel_local
                if self._can_start_panel_resize(watched=watched, panel=panel, local_point=local_point, event=event):
                    self._start_panel_resize(context_id=context_id, panel_id=panel_id, panel=panel)
                    return True
                if self._can_start_panel_drag(watched=watched, panel=panel, local_point=local_point, event=event):
                    self._start_panel_drag(context_id=context_id, panel_id=panel_id, event=event)
                    return True
        elif event_type in {QEvent.Type.MouseMove, touch_update}:
            if self._panel_resize_session is not None:
                self._apply_panel_resize(event)
                return True
            if self._panel_drag_session is not None:
                self._apply_panel_drag(event)
                return True
            if mapped is not None:
                context_id, panel_id = mapped
                panel = self._mapped_panel_widget(context_id, panel_id)
                if panel is not None:
                    point = panel.mapFromGlobal(self._event_global_point(event))
                    if self._is_resize_hotzone(panel, point):
                        panel.setCursor(Qt.SizeVerCursor)
                    else:
                        panel.unsetCursor()
        elif event_type in {QEvent.Type.MouseButtonRelease, touch_end, touch_cancel, QEvent.Type.Leave}:
            if self._panel_resize_session is not None:
                self._finish_panel_resize()
                return True
            if self._panel_drag_session is not None:
                self._finish_panel_drag()
                return True
        return super().eventFilter(watched, event)

    def _mapped_panel_widget(self, context_id: str, panel_id: str) -> GlassPanelFrame | None:
        template = self._editor_templates.get(str(context_id or "").strip().lower())
        if template is None:
            return None
        return template.panel(panel_id)

    def _event_global_point(self, event: QEvent) -> QPoint:
        touch_point = self._touch_primary_global_point(event)
        if touch_point is not None:
            return touch_point
        global_position = getattr(event, "globalPosition", None)
        if callable(global_position):
            try:
                return global_position().toPoint()
            except Exception:  # noqa: BLE001
                pass
        global_pos = getattr(event, "globalPos", None)
        if callable(global_pos):
            try:
                return global_pos()
            except Exception:  # noqa: BLE001
                pass
        return QPoint()

    def _event_local_point(self, event: QEvent) -> QPoint:
        touch_point = self._touch_primary_local_point(event)
        if touch_point is not None:
            return touch_point
        position = getattr(event, "position", None)
        if callable(position):
            try:
                return position().toPoint()
            except Exception:  # noqa: BLE001
                pass
        pos = getattr(event, "pos", None)
        if callable(pos):
            try:
                return pos()
            except Exception:  # noqa: BLE001
                pass
        return QPoint()

    def _touch_primary_global_point(self, event: QEvent) -> QPoint | None:
        points_getter = getattr(event, "points", None)
        if not callable(points_getter):
            return None
        try:
            points = points_getter()
        except Exception:  # noqa: BLE001
            return None
        if not points:
            return None
        first = points[0]
        global_position = getattr(first, "globalPosition", None)
        if callable(global_position):
            try:
                return global_position().toPoint()
            except Exception:  # noqa: BLE001
                return None
        return None

    def _touch_primary_local_point(self, event: QEvent) -> QPoint | None:
        points_getter = getattr(event, "points", None)
        if not callable(points_getter):
            return None
        try:
            points = points_getter()
        except Exception:  # noqa: BLE001
            return None
        if not points:
            return None
        first = points[0]
        local_position = getattr(first, "position", None)
        if callable(local_position):
            try:
                return local_position().toPoint()
            except Exception:  # noqa: BLE001
                return None
        return None

    def _event_has_left_button(self, event: QEvent) -> bool:
        button = getattr(event, "button", None)
        if callable(button):
            try:
                if button() != Qt.LeftButton:
                    return False
            except Exception:  # noqa: BLE001
                return False
        buttons = getattr(event, "buttons", None)
        if callable(buttons):
            try:
                return bool(buttons() & Qt.LeftButton)
            except Exception:  # noqa: BLE001
                return False
        return True

    def _event_modifiers(self, event: QEvent) -> Qt.KeyboardModifiers:
        modifiers = getattr(event, "modifiers", None)
        if callable(modifiers):
            try:
                return modifiers()
            except Exception:  # noqa: BLE001
                return Qt.NoModifier
        return Qt.NoModifier

    def _is_resize_hotzone(self, panel: GlassPanelFrame, local_point: QPoint) -> bool:
        return bool(local_point.y() >= max(0, panel.height() - 10))

    def _can_start_panel_resize(
        self,
        *,
        watched: QObject,
        panel: GlassPanelFrame | None,
        local_point: QPoint,
        event: QEvent,
    ) -> bool:
        if panel is None:
            return False
        if watched is not panel:
            return False
        if not self._event_has_left_button(event):
            return False
        if self._event_modifiers(event) not in {Qt.NoModifier, Qt.ShiftModifier}:
            return False
        return self._is_resize_hotzone(panel, local_point)

    def _can_start_panel_drag(
        self,
        *,
        watched: QObject,
        panel: GlassPanelFrame | None,
        local_point: QPoint,
        event: QEvent,
    ) -> bool:
        if panel is None:
            return False
        if bool(panel.property("slotShell")):
            return False
        if not self._event_has_left_button(event):
            return False
        if self._event_modifiers(event) not in {Qt.NoModifier, Qt.AltModifier}:
            return False
        blocked_types = (QLineEdit, QTextEdit, QComboBox, QSlider, QTableWidget, QListWidget, QPushButton, QCheckBox)
        if isinstance(watched, blocked_types):
            return False
        return bool(local_point.y() <= 56)

    def _start_panel_drag(self, *, context_id: str, panel_id: str, event: QEvent) -> None:
        self._panel_drag_session = _PanelDragSession(
            context_id=str(context_id or "").strip().lower(),
            panel_id=str(panel_id or "").strip(),
            origin=self._event_global_point(event),
            active=False,
            last_target=None,
        )
        panel = self._mapped_panel_widget(context_id, panel_id)
        if panel is not None:
            panel.setProperty("panelInteraction", "dragging")
            _repolish(panel)

    def _finish_panel_drag(self) -> None:
        if self._panel_drag_session is None:
            return
        panel = self._mapped_panel_widget(self._panel_drag_session.context_id, self._panel_drag_session.panel_id)
        self._panel_drag_session = None
        if panel is not None:
            panel.setProperty("panelInteraction", "")
            panel.unsetCursor()
            _repolish(panel)

    def _start_panel_resize(self, *, context_id: str, panel_id: str, panel: GlassPanelFrame | None) -> None:
        if panel is None:
            return
        template = self._editor_templates.get(str(context_id or "").strip().lower())
        if template is None:
            return
        slot = self._panel_slot(template, panel_id)
        slot_widget = self._slot_widget(template, slot)
        available_height = 0
        if slot_widget is not None:
            try:
                available_height = int(slot_widget.contentsRect().height())
            except Exception:  # noqa: BLE001
                available_height = int(slot_widget.height())
        if available_height <= 0:
            parent = panel.parentWidget()
            if parent is not None:
                try:
                    available_height = int(parent.contentsRect().height())
                except Exception:  # noqa: BLE001
                    available_height = int(parent.height())
        if available_height <= 0:
            available_height = int(panel.height() * 2)
        max_height = max(150, int(available_height - 4))
        start_height = max(panel.height(), panel.minimumHeight(), 96)
        self._panel_resize_session = _PanelResizeSession(
            context_id=str(context_id or "").strip().lower(),
            panel_id=str(panel_id or "").strip(),
            origin_y=panel.mapToGlobal(QPoint(0, 0)).y() + panel.height(),
            start_height=start_height,
            min_height=96,
            max_height=max_height,
            active=False,
        )
        panel.setProperty("panelInteraction", "resizing")
        panel.setCursor(Qt.SizeVerCursor)
        _repolish(panel)

    def _finish_panel_resize(self) -> None:
        if self._panel_resize_session is None:
            return
        panel = self._mapped_panel_widget(self._panel_resize_session.context_id, self._panel_resize_session.panel_id)
        self._panel_resize_session = None
        if panel is not None:
            panel.setProperty("panelInteraction", "")
            panel.unsetCursor()
            _repolish(panel)

    def _slot_widget(self, template: GlassPanelTemplate, slot: str) -> QWidget | None:
        layout = {
            "main": template.slots.main_slot,
            "side": template.slots.side_slot,
            "status": template.slots.status_slot,
        }.get(str(slot or "main").strip().lower(), template.slots.main_slot)
        return layout.parentWidget()

    def _workspace_bounds(self, template: GlassPanelTemplate) -> QRect:
        target = template.cards.body if hasattr(template, "cards") else template
        top_left = target.mapToGlobal(QPoint(0, 0))
        return QRect(top_left, target.size()).adjusted(2, 2, -2, -2)

    def _clamped_workspace_point(self, template: GlassPanelTemplate, global_point: QPoint) -> QPoint:
        rect = self._workspace_bounds(template)
        if rect.width() <= 2 or rect.height() <= 2:
            return global_point
        x = max(rect.left(), min(rect.right(), global_point.x()))
        y = max(rect.top(), min(rect.bottom(), global_point.y()))
        return QPoint(int(x), int(y))

    def _drop_target_for_point(
        self,
        *,
        template: GlassPanelTemplate,
        panel_id: str,
        global_point: QPoint,
    ) -> tuple[str, int]:
        fallback_slot = self._panel_slot(template, panel_id)
        fallback_ids = self._slot_panel_ids(template, fallback_slot)
        fallback_index = fallback_ids.index(panel_id) if panel_id in fallback_ids else max(0, len(fallback_ids))
        for slot in ("main", "side", "status"):
            container = self._slot_widget(template, slot)
            if container is None:
                continue
            rect = QRect(container.mapToGlobal(QPoint(0, 0)), container.size())
            if not rect.contains(global_point):
                continue
            slot_ids = self._slot_panel_ids(template, slot)
            if panel_id in slot_ids:
                slot_ids.remove(panel_id)
            target_index = len(slot_ids)
            for idx, candidate_id in enumerate(slot_ids):
                candidate = template.panel(candidate_id)
                if candidate is None:
                    continue
                center = candidate.mapToGlobal(QPoint(0, max(1, candidate.height() // 2))).y()
                if global_point.y() < center:
                    target_index = idx
                    break
            return slot, max(0, target_index)
        return fallback_slot, fallback_index

    def _apply_panel_drag(self, event: QEvent) -> None:
        drag = self._panel_drag_session
        if drag is None:
            return
        template = self._editor_templates.get(drag.context_id)
        session = self._editor_sessions.get(drag.context_id)
        if template is None or session is None:
            return
        if self._is_structural_slot_shell(template, drag.panel_id):
            self._finish_panel_drag()
            return
        if not self._event_has_left_button(event):
            self._finish_panel_drag()
            return
        point = self._event_global_point(event)
        if not drag.active:
            if (point - drag.origin).manhattanLength() < 8:
                return
            drag.active = True
        clamped = self._clamped_workspace_point(template, point)
        target_slot, target_index = self._drop_target_for_point(
            template=template,
            panel_id=drag.panel_id,
            global_point=clamped,
        )
        panel_state = self._panel_state_for_session(session, drag.panel_id) or {}
        panel_type = str(panel_state.get("panel_type") or "text_markdown")
        spec = self._panel_type_registry.get(panel_type)
        if spec is not None and target_slot not in spec.allowed_slots:
            return
        if not self._can_add_panel_to_slot(
            template=template,
            slot=target_slot,
            spec=spec or next(iter(self._panel_type_registry.values())),
            session=session,
            moving_panel_id=drag.panel_id,
        ):
            return
        if drag.last_target == (target_slot, target_index):
            return
        drag.last_target = (target_slot, target_index)
        moved = template.move_panel(drag.panel_id, target_slot=target_slot, index=target_index)
        if not moved:
            return
        if drag.panel_id in session.core_working:
            session.core_working[drag.panel_id]["slot"] = target_slot
        else:
            for item in session.dynamic_working:
                if item.panel_id == drag.panel_id:
                    item.target_slot = target_slot
                    break
        self._refresh_core_indices(session, template)
        self._sync_dynamic_order_from_template(session, template)
        self._refresh_editor_panel_combo(session, template)
        self._set_selected_editor_panel(session, drag.panel_id)
        self._mark_session_dirty(session)

    def _apply_panel_resize(self, event: QEvent) -> None:
        resize = self._panel_resize_session
        if resize is None:
            return
        template = self._editor_templates.get(resize.context_id)
        session = self._editor_sessions.get(resize.context_id)
        if template is None or session is None:
            return
        panel = template.panel(resize.panel_id)
        if panel is None:
            return
        point = self._event_global_point(event)
        if not resize.active:
            if abs(point.y() - resize.origin_y) < 3:
                return
            resize.active = True
        delta = int(point.y() - resize.origin_y)
        next_height = max(resize.min_height, min(resize.max_height, resize.start_height + delta))
        panel.setMinimumHeight(next_height)
        panel.setMaximumHeight(next_height)
        if resize.panel_id in session.core_working:
            session.core_working[resize.panel_id]["height_policy"] = "fixed"
            session.core_working[resize.panel_id]["panel_height"] = next_height
        else:
            for item in session.dynamic_working:
                if item.panel_id == resize.panel_id:
                    item.height_policy = "fixed"
                    item.panel_height = next_height
                    break
        self._set_combo_data(self.editor_height_policy_combo, "fixed")
        self.editor_height_slider.setValue(max(96, min(760, next_height)))
        self._mark_session_dirty(session)

    def _select_editor_context(self, context_id: str, *, panel_id: str | None = None) -> None:
        target = str(context_id or "").strip().lower()
        if not target:
            return
        for index in range(self.editor_context_combo.count()):
            value = str(self.editor_context_combo.itemData(index) or "").strip().lower()
            if value == target:
                self.editor_context_combo.setCurrentIndex(index)
                break
        session = self._editor_sessions.get(target)
        if session is None:
            return
        if panel_id:
            session.selected_panel_id = str(panel_id)
        self._load_editor_for_current_context()

    def _set_selected_editor_panel(self, session: WorkbenchEditorSession, panel_id: str) -> None:
        selected = str(panel_id or "").strip()
        if not selected:
            return
        session.selected_panel_id = selected
        self._activate_selected_dynamic_panel(session, selected)
        self._set_combo_data(self.editor_panel_combo, selected)
        template = self._current_editor_template()
        if template is not None:
            for current_panel_id in template.panel_ids():
                panel = template.panel(current_panel_id)
                if panel is None:
                    continue
                panel.setProperty("editorSelected", "true" if current_panel_id == selected else "false")
                panel.style().unpolish(panel)
                panel.style().polish(panel)
                panel.update()
        self._load_selected_panel_fields(session)

    def _activate_selected_dynamic_panel(self, session: WorkbenchEditorSession, panel_id: str) -> None:
        template = self._current_editor_template()
        if template is None:
            return
        for item in session.dynamic_working:
            if item.panel_id != panel_id:
                continue
            should_wake = item.state in {"deferred", "hold", "background"} or (
                (not item.visible) and item.state not in {"hidden", "collapsed"}
            )
            if should_wake:
                item.state = "visible"
                item.visible = True
                panel = template.panel(panel_id)
                if panel is not None:
                    panel.set_panel_state("visible")
                    panel.setVisible(True)
                    self._render_dynamic_panel_content(panel, item)
                self._enforce_tab_panel_budget(template, session, emit_warnings=True)
            return

    def _panel_state_for_session(self, session: WorkbenchEditorSession, panel_id: str) -> dict[str, Any] | None:
        panel = session.core_working.get(panel_id)
        if panel is not None:
            return panel
        for dynamic in session.dynamic_working:
            if dynamic.panel_id == panel_id:
                return {
                    "panel_id": dynamic.panel_id,
                    "panel_type": dynamic.panel_type,
                    "title": dynamic.title,
                    "subtitle": dynamic.subtitle,
                    "slot": dynamic.target_slot,
                    "role": dynamic.role,
                    "state": dynamic.state,
                    "visible": bool(dynamic.visible),
                    "text": dynamic.text,
                    "icon_name": dynamic.icon_name,
                    "variant": dynamic.variant,
                    "density": dynamic.density,
                    "width_policy": dynamic.width_policy,
                    "padding": dynamic.padding,
                    "data_provider_id": dynamic.data_provider_id,
                    "data_query_id": dynamic.data_query_id,
                    "chart_mode": dynamic.chart_mode,
                    "chart_style_id": dynamic.chart_style_id,
                    "chart_palette_id": dynamic.chart_palette_id,
                    "chart_show_grid": bool(dynamic.chart_show_grid),
                    "chart_show_glow": bool(dynamic.chart_show_glow),
                    "chart_show_markers": bool(dynamic.chart_show_markers),
                    "chart_smooth": bool(dynamic.chart_smooth),
                    "chart_line_width": int(dynamic.chart_line_width),
                    "chart_fill_alpha": int(dynamic.chart_fill_alpha),
                    "height_policy": dynamic.height_policy,
                    "panel_height": int(dynamic.panel_height),
                    "list_options": list(dynamic.list_options),
                    "widget_props": normalize_widget_props(dynamic.panel_type, dynamic.widget_props),
                    "behavior": normalize_behavior_binding(dynamic.behavior),
                    "dynamic": True,
                }
        return None

    def _load_selected_panel_fields(self, session: WorkbenchEditorSession) -> None:
        panel_id = str(session.selected_panel_id or "").strip()
        if not panel_id:
            return
        state = self._panel_state_for_session(session, panel_id)
        if state is None:
            return
        self._set_combo_data(self.editor_panel_type_combo, str(state.get("panel_type") or "text_markdown"))
        self._set_combo_data(self.editor_slot_combo, str(state.get("slot") or "main"))
        self._set_combo_data(self.editor_role_combo, str(state.get("role") or "workspace"))
        self._set_combo_data(self.editor_state_combo, str(state.get("state") or "visible"))
        self.editor_visible_check.setChecked(bool(state.get("visible", True)))
        self.editor_title_input.setText(str(state.get("title") or ""))
        self.editor_subtitle_input.setText(str(state.get("subtitle") or ""))
        self.editor_icon_input.setText(str(state.get("icon_name") or ""))
        self._set_combo_data(self.editor_variant_combo, str(state.get("variant") or "default"))
        self._set_combo_data(self.editor_density_combo, str(state.get("density") or "compact"))
        self._set_combo_data(self.editor_width_policy_combo, str(state.get("width_policy") or "stretch"))
        self._set_combo_data(self.editor_padding_combo, str(state.get("padding") or "normal"))
        self._set_combo_data(self.editor_height_policy_combo, str(state.get("height_policy") or "auto"))
        self.editor_height_slider.setValue(max(96, min(760, int(state.get("panel_height") or 240))))
        self._set_combo_data(self.editor_chart_mode_combo, str(state.get("chart_mode") or "line"))
        self._set_combo_data(self.editor_chart_style_combo, str(state.get("chart_style_id") or "silver_line"))
        self._set_combo_data(self.editor_chart_palette_combo, str(state.get("chart_palette_id") or "auto"))
        self.editor_chart_grid_check.setChecked(bool(state.get("chart_show_grid", True)))
        self.editor_chart_glow_check.setChecked(bool(state.get("chart_show_glow", True)))
        self.editor_chart_markers_check.setChecked(bool(state.get("chart_show_markers", False)))
        self.editor_chart_smooth_check.setChecked(bool(state.get("chart_smooth", True)))
        self.editor_chart_line_slider.setValue(max(1, min(6, int(state.get("chart_line_width") or 2))))
        self.editor_chart_fill_slider.setValue(max(0, min(60, int(state.get("chart_fill_alpha") or 26))))
        self._set_combo_data(self.editor_provider_combo, str(state.get("data_provider_id") or ""))
        self.editor_query_input.setText(str(state.get("data_query_id") or ""))
        list_options = state.get("list_options", ())
        if isinstance(list_options, (tuple, list)):
            self.editor_options_input.setText(", ".join(str(item) for item in list_options))
        else:
            self.editor_options_input.setText(str(list_options or ""))
        panel_type = str(state.get("panel_type") or "text_markdown")
        widget_props = normalize_widget_props(panel_type, state.get("widget_props"))
        behavior = normalize_behavior_binding(state.get("behavior"))
        self.editor_widget_object_name_input.setText(str(widget_props.get("object_name") or ""))
        self.editor_widget_tooltip_input.setText(str(widget_props.get("tooltip") or ""))
        self.editor_widget_enabled_check.setChecked(bool(widget_props.get("enabled", True)))
        self.editor_button_text_input.setText(str(widget_props.get("text") or state.get("text") or ""))
        self.editor_button_icon_input.setText(str(widget_props.get("icon_name") or ""))
        self.editor_button_checkable_check.setChecked(bool(widget_props.get("checkable", False)))
        self.editor_button_checked_check.setChecked(bool(widget_props.get("checked", False)))
        self._set_combo_data(self.editor_button_style_variant_combo, str(widget_props.get("style_variant") or "default"))
        self._set_combo_data(self.editor_behavior_action_type_combo, str(behavior.get("action_type") or "none"))
        self.editor_behavior_command_id_input.setText(str(behavior.get("command_id") or ""))
        self.editor_behavior_target_panel_input.setText(str(behavior.get("target_panel_id") or ""))
        self.editor_behavior_task_ref_input.setText(str(behavior.get("task_ref") or ""))
        payload_text = json.dumps(behavior.get("payload") or {}, indent=2, ensure_ascii=True)
        self.editor_behavior_payload_input.setPlainText(payload_text if payload_text != "{}" else "")
        self.editor_text_input.setPlainText(str(state.get("text") or widget_props.get("text") or ""))
        template = self._current_editor_template()
        locked = bool(template is not None and self._is_structural_slot_shell(template, panel_id))
        self._set_slot_shell_edit_lock(locked)

    def _set_combo_data(self, combo: QComboBox, value: str) -> None:
        target = str(value or "").strip().lower()
        if not target:
            if combo.count() > 0:
                combo.setCurrentIndex(0)
            return
        for index in range(combo.count()):
            item_value = str(combo.itemData(index) or combo.itemText(index) or "").strip().lower()
            if item_value == target:
                combo.setCurrentIndex(index)
                return

    def _mark_session_dirty(self, session: WorkbenchEditorSession) -> None:
        session.dirty = True
        self._sync_editor_status(session)

    def _sync_editor_status(self, session: WorkbenchEditorSession) -> None:
        source_mode = "preview" if session.context_id == "preview" else ("saved clone" if session.source_kind == "clone" else "source")
        self.editor_source_value.setText(
            f"{source_mode} - {session.source_kind} - {session.source_ref or '(unspecified)'}"
        )
        self.editor_dirty_value.setText("dirty - unsaved" if session.dirty else "clean - synced")
        panel_count = len(session.core_working) + len(session.dynamic_working)
        active_dynamic = sum(1 for item in session.dynamic_working if item.visible and item.state == "visible")
        deferred_dynamic = sum(
            1 for item in session.dynamic_working if item.state in {"deferred", "hold", "background"} or not item.visible
        )
        hidden_dynamic = sum(
            1 for item in session.dynamic_working if (not item.visible) or item.state in {"hidden", "collapsed"}
        )
        hidden_core = sum(
            1
            for payload in session.core_working.values()
            if (not bool(payload.get("visible", True)))
            or str(payload.get("state") or "visible").lower() in {"hidden", "collapsed"}
        )
        self.editor_status.setText(
            f"Context '{session.context_id}' - panels={panel_count} - "
            f"split={session.split_working[0]}/{session.split_working[1]} - "
            f"active={active_dynamic} deferred={deferred_dynamic} - "
            f"{'Unsaved edits in current working state.' if session.dirty else 'Working state matches saved/baseline state.'}"
        )
        self.editor_hidden_summary.setText(
            f"Hidden panels: {hidden_dynamic + hidden_core} "
            f"(dynamic={hidden_dynamic}, core={hidden_core}). "
            "Use Reopen Hidden to reactivate."
        )

    def _new_panel_state(self, *, panel_type: str, slot: str, session: WorkbenchEditorSession) -> WorkbenchPanelState:
        normalized_type = str(panel_type or "").strip().lower()
        spec = self._panel_type_registry.get(normalized_type) or next(iter(self._panel_type_registry.values()))
        heavy_visible = sum(
            1
            for item in session.dynamic_working
            if item.visible and item.state == "visible" and self._panel_type_registry.get(item.panel_type, spec).heavy
        )
        should_defer = bool(spec.heavy and heavy_visible >= int(self._editor_policy["heavy_panels_per_tab"]))
        session.panel_counter += 1
        panel_id = f"dyn_{session.panel_counter:03d}"
        return WorkbenchPanelState(
            panel_id=panel_id,
            panel_type=spec.panel_type,
            title=f"{spec.title} {session.panel_counter}",
            subtitle=spec.default_subtitle,
            target_slot=str(slot or "main").strip().lower() or "main",
            role=spec.default_role,
            state="deferred" if should_defer else "visible",
            visible=not should_defer,
            text=spec.default_text,
            icon_name=spec.icon_name,
            variant="default",
            density="compact",
            width_policy="stretch",
            padding="normal",
            data_provider_id="",
            data_query_id="",
            chart_mode="line",
            chart_style_id="silver_line",
            chart_palette_id="auto",
            chart_show_grid=True,
            chart_show_glow=True,
            chart_show_markers=False,
            chart_smooth=True,
            chart_line_width=2,
            chart_fill_alpha=26,
            height_policy="auto",
            panel_height=0,
            list_options=tuple(item.strip() for item in spec.default_text.split(",") if item.strip())[:8],
            widget_props=default_widget_props(spec.panel_type, title=spec.title, text=spec.default_text),
            behavior=default_behavior_binding(),
            dynamic=True,
        )

    def _add_editor_panel(self) -> None:
        session = self._current_editor_session()
        template = self._current_editor_template()
        if session is None or template is None:
            return
        panel_type = (
            str(self.editor_add_type_combo.currentData() or "").strip().lower()
            or self._selected_palette_panel_type()
            or "text_markdown"
        )
        spec = self._panel_type_registry.get(panel_type)
        if spec is None:
            return
        slot = self._resolve_insert_slot(session=session, template=template, spec=spec)
        if slot not in spec.allowed_slots:
            slot = spec.allowed_slots[0] if spec.allowed_slots else "main"
        if not self._can_add_panel_to_slot(template=template, slot=slot, spec=spec, session=session):
            self.catalog.set_status_text(f"Cannot insert '{spec.title}' into '{slot}' due to slot policy/budget.")
            return

        state = self._new_panel_state(panel_type=panel_type, slot=slot, session=session)
        state.variant = str(self.editor_variant_combo.currentData() or self.editor_variant_combo.currentText() or "default")
        state.density = str(self.editor_density_combo.currentData() or self.editor_density_combo.currentText() or "compact")
        state.width_policy = str(
            self.editor_width_policy_combo.currentData() or self.editor_width_policy_combo.currentText() or "stretch"
        )
        state.padding = str(self.editor_padding_combo.currentData() or self.editor_padding_combo.currentText() or "normal")
        state.data_provider_id = str(self.editor_provider_combo.currentData() or "")
        state.data_query_id = self.editor_query_input.text().strip()
        state.text = self.editor_text_input.toPlainText().strip() or state.text
        state.chart_mode = str(self.editor_chart_mode_combo.currentData() or self.editor_chart_mode_combo.currentText() or "line")
        state.chart_style_id = str(
            self.editor_chart_style_combo.currentData() or self.editor_chart_style_combo.currentText() or "silver_line"
        ).strip().lower()
        state.chart_palette_id = str(
            self.editor_chart_palette_combo.currentData() or self.editor_chart_palette_combo.currentText() or "auto"
        ).strip().lower() or "auto"
        state.chart_show_grid = bool(self.editor_chart_grid_check.isChecked())
        state.chart_show_glow = bool(self.editor_chart_glow_check.isChecked())
        state.chart_show_markers = bool(self.editor_chart_markers_check.isChecked())
        state.chart_smooth = bool(self.editor_chart_smooth_check.isChecked())
        state.chart_line_width = int(self.editor_chart_line_slider.value())
        state.chart_fill_alpha = int(self.editor_chart_fill_slider.value())
        state.height_policy = str(
            self.editor_height_policy_combo.currentData() or self.editor_height_policy_combo.currentText() or "auto"
        ).strip().lower() or "auto"
        state.panel_height = int(self.editor_height_slider.value()) if state.height_policy == "fixed" else 0
        option_values = [item.strip() for item in self.editor_options_input.text().split(",") if item.strip()]
        if option_values:
            state.list_options = tuple(option_values[:12])
        behavior_payload: dict[str, Any]
        try:
            behavior_payload = parse_behavior_payload(self.editor_behavior_payload_input.toPlainText())
        except Exception:
            behavior_payload = {}
        state.widget_props = normalize_widget_props(
            state.panel_type,
            {
                "text": self.editor_button_text_input.text().strip() or state.text or state.title,
                "tooltip": self.editor_widget_tooltip_input.text().strip(),
                "object_name": self.editor_widget_object_name_input.text().strip(),
                "enabled": bool(self.editor_widget_enabled_check.isChecked()),
                "visible": bool(state.visible),
                "checkable": bool(self.editor_button_checkable_check.isChecked()),
                "checked": bool(self.editor_button_checked_check.isChecked()),
                "icon_name": self.editor_button_icon_input.text().strip(),
                "style_variant": str(
                    self.editor_button_style_variant_combo.currentData()
                    or self.editor_button_style_variant_combo.currentText()
                    or "default"
                ),
            },
        )
        state.behavior = normalize_behavior_binding(
            {
                "event": "clicked",
                "action_type": str(
                    self.editor_behavior_action_type_combo.currentData()
                    or self.editor_behavior_action_type_combo.currentText()
                    or "none"
                ),
                "command_id": self.editor_behavior_command_id_input.text().strip(),
                "target_panel_id": self.editor_behavior_target_panel_input.text().strip(),
                "task_ref": self.editor_behavior_task_ref_input.text().strip(),
                "payload": behavior_payload,
            }
        )

        insert_index = self._insert_index_for_slot(session=session, template=template, slot=slot)
        state_snapshot = deepcopy(state)
        context_id = session.context_id

        def _commit_insert() -> bool:
            current_session = self._editor_sessions.get(context_id)
            current_template = self._editor_templates.get(context_id)
            if current_session is None or current_template is None:
                return False
            spec_now = self._panel_type_registry.get(state_snapshot.panel_type)
            if spec_now is None:
                return False
            if not self._can_add_panel_to_slot(
                template=current_template,
                slot=state_snapshot.target_slot,
                spec=spec_now,
                session=current_session,
            ):
                self.catalog.set_status_text(
                    f"Cannot insert '{state_snapshot.title}' into '{state_snapshot.target_slot}' due to slot policy/budget."
                )
                return False
            if current_template.panel(state_snapshot.panel_id) is not None:
                return False
            panel = current_template.create_panel(
                panel_id=state_snapshot.panel_id,
                title=state_snapshot.title,
                subtitle=state_snapshot.subtitle,
                target_slot=state_snapshot.target_slot,
                role=state_snapshot.role,
                state=state_snapshot.state,
                icon_name=state_snapshot.icon_name or None,
                card_kind="muted",
            )
            if insert_index is not None:
                current_template.move_panel(state_snapshot.panel_id, target_slot=state_snapshot.target_slot, index=insert_index)
            self._render_dynamic_panel_content(panel, state_snapshot)
            current_session.dynamic_working.append(deepcopy(state_snapshot))
            self._record_palette_recent(state_snapshot.panel_type)
            self._bind_editor_click_targets(current_template, current_session.context_id)
            self._refresh_editor_panel_combo(current_session, current_template)
            self._set_selected_editor_panel(current_session, state_snapshot.panel_id)
            self._enforce_tab_panel_budget(current_template, current_session, emit_warnings=True)
            self._mark_session_dirty(current_session)
            self.catalog.set_status_text(
                f"Inserted '{state_snapshot.title}' ({state_snapshot.panel_type}) into '{state_snapshot.target_slot}'"
                + (f" @ index {insert_index}" if insert_index is not None else "")
                + "."
            )
            return True

        self._stage_pending_panel_candidate(
            context_id=context_id,
            title=f"Stage '{state.title}'",
            summary=(
                "Candidate panel staged in workspace. Drag to reposition, then Confirm to commit "
                "or Cancel to discard."
            ),
            commit=_commit_insert,
        )

    def _apply_editor_properties(self) -> None:
        session = self._current_editor_session()
        template = self._current_editor_template()
        if session is None or template is None:
            return
        panel_id = str(self.editor_panel_combo.currentData() or "").strip()
        if not panel_id:
            return
        panel = template.panel(panel_id)
        if panel is None:
            return
        is_slot_shell = bool(getattr(template, "panel_is_slot_shell", lambda _panel_id: False)(panel_id))

        panel_type = str(self.editor_panel_type_combo.currentData() or "text_markdown").strip().lower()
        slot = str(self.editor_slot_combo.currentData() or self.editor_slot_combo.currentText() or "main").strip().lower()
        role = str(self.editor_role_combo.currentData() or self.editor_role_combo.currentText() or "workspace").strip().lower()
        state_value = str(self.editor_state_combo.currentData() or self.editor_state_combo.currentText() or "visible").strip().lower()
        title = self.editor_title_input.text().strip() or panel_id
        subtitle = self.editor_subtitle_input.text().strip()
        icon_name = self.editor_icon_input.text().strip()
        text = self.editor_text_input.toPlainText().strip()
        visible = bool(self.editor_visible_check.isChecked())
        variant = str(self.editor_variant_combo.currentData() or self.editor_variant_combo.currentText() or "default")
        density = str(self.editor_density_combo.currentData() or self.editor_density_combo.currentText() or "compact")
        width_policy = str(
            self.editor_width_policy_combo.currentData() or self.editor_width_policy_combo.currentText() or "stretch"
        )
        padding = str(self.editor_padding_combo.currentData() or self.editor_padding_combo.currentText() or "normal")
        height_policy = str(
            self.editor_height_policy_combo.currentData() or self.editor_height_policy_combo.currentText() or "auto"
        ).strip().lower()
        panel_height = int(self.editor_height_slider.value()) if height_policy == "fixed" else 0
        data_provider_id = str(self.editor_provider_combo.currentData() or "")
        data_query_id = self.editor_query_input.text().strip()
        chart_mode = str(self.editor_chart_mode_combo.currentData() or self.editor_chart_mode_combo.currentText() or "line")
        chart_style_id = str(
            self.editor_chart_style_combo.currentData() or self.editor_chart_style_combo.currentText() or "silver_line"
        ).strip().lower()
        chart_palette_id = str(
            self.editor_chart_palette_combo.currentData() or self.editor_chart_palette_combo.currentText() or "auto"
        ).strip().lower() or "auto"
        chart_show_grid = bool(self.editor_chart_grid_check.isChecked())
        chart_show_glow = bool(self.editor_chart_glow_check.isChecked())
        chart_show_markers = bool(self.editor_chart_markers_check.isChecked())
        chart_smooth = bool(self.editor_chart_smooth_check.isChecked())
        chart_line_width = int(self.editor_chart_line_slider.value())
        chart_fill_alpha = int(self.editor_chart_fill_slider.value())
        list_options = tuple(item.strip() for item in self.editor_options_input.text().split(",") if item.strip())
        raw_behavior_payload = self.editor_behavior_payload_input.toPlainText()
        try:
            behavior_payload = parse_behavior_payload(raw_behavior_payload)
        except Exception as exc:  # noqa: BLE001
            self.catalog.set_status_text(f"Invalid behavior payload JSON: {exc}")
            return
        widget_props = normalize_widget_props(
            panel_type,
            {
                "text": self.editor_button_text_input.text().strip() or text,
                "tooltip": self.editor_widget_tooltip_input.text().strip(),
                "object_name": self.editor_widget_object_name_input.text().strip(),
                "enabled": bool(self.editor_widget_enabled_check.isChecked()),
                "visible": visible,
                "checkable": bool(self.editor_button_checkable_check.isChecked()),
                "checked": bool(self.editor_button_checked_check.isChecked()),
                "icon_name": self.editor_button_icon_input.text().strip(),
                "style_variant": str(
                    self.editor_button_style_variant_combo.currentData()
                    or self.editor_button_style_variant_combo.currentText()
                    or "default"
                ),
            },
        )
        if panel_type == "button_control":
            text = str(widget_props.get("text") or text)
        behavior = normalize_behavior_binding(
            {
                "event": "clicked",
                "action_type": str(
                    self.editor_behavior_action_type_combo.currentData()
                    or self.editor_behavior_action_type_combo.currentText()
                    or "none"
                ),
                "command_id": self.editor_behavior_command_id_input.text().strip(),
                "target_panel_id": self.editor_behavior_target_panel_input.text().strip(),
                "task_ref": self.editor_behavior_task_ref_input.text().strip(),
                "payload": behavior_payload,
            }
        )

        if is_slot_shell:
            panel_state = self._panel_state_for_session(session, panel_id) or {}
            panel_type = str(panel_state.get("panel_type") or panel_type)
            slot = self._panel_slot(template, panel_id)
            role = str(panel_state.get("role") or role)
            state_value = "visible"
            visible = True
            self.catalog.set_status_text(f"'{panel_id}' is a structural slot shell; movement/hide/type change blocked.")

        spec = self._panel_type_registry.get(panel_type)
        if spec is not None and slot not in spec.allowed_slots:
            slot = spec.allowed_slots[0] if spec.allowed_slots else "main"
        if (not is_slot_shell) and slot != self._panel_slot(template, panel_id) and not self._can_add_panel_to_slot(
            template=template,
            slot=slot,
            spec=spec or next(iter(self._panel_type_registry.values())),
            session=session,
            moving_panel_id=panel_id,
        ):
            self.catalog.set_status_text(f"Cannot move '{panel_id}' into slot '{slot}' due to slot policy/budget.")
            return

        panel.set_panel_title(title)
        panel.set_panel_subtitle(subtitle)
        panel.set_panel_role(role)
        panel.set_panel_state(state_value)
        panel.setVisible(visible)
        if slot != self._panel_slot(template, panel_id):
            target_index = None
            existing_ids = self._slot_panel_ids(template, slot)
            if panel_id in existing_ids:
                target_index = existing_ids.index(panel_id)
            if not template.move_panel(panel_id, target_slot=slot, index=target_index):
                self.catalog.set_status_text(f"Move rejected for panel '{panel_id}'.")
                return

        if panel_id in session.core_working:
            core = session.core_working[panel_id]
            core["title"] = title
            core["subtitle"] = subtitle
            core["slot"] = slot
            core["role"] = role
            core["state"] = state_value
            core["visible"] = visible
            core["panel_type"] = panel_type
            core["icon_name"] = icon_name
            core["text"] = text
            core["variant"] = variant
            core["density"] = density
            core["width_policy"] = width_policy
            core["padding"] = padding
            core["height_policy"] = height_policy
            core["panel_height"] = panel_height
            core["data_provider_id"] = data_provider_id
            core["data_query_id"] = data_query_id
            core["chart_mode"] = chart_mode
            core["chart_style_id"] = chart_style_id
            core["chart_palette_id"] = chart_palette_id
            core["chart_show_grid"] = chart_show_grid
            core["chart_show_glow"] = chart_show_glow
            core["chart_show_markers"] = chart_show_markers
            core["chart_smooth"] = chart_smooth
            core["chart_line_width"] = chart_line_width
            core["chart_fill_alpha"] = chart_fill_alpha
            core["list_options"] = list_options
            core["widget_props"] = normalize_widget_props(panel_type, widget_props)
            core["behavior"] = normalize_behavior_binding(behavior)
            core["slot_shell"] = is_slot_shell
            core["user_hidden"] = bool((not visible) or state_value in {"hidden", "collapsed"})
            core["content_override"] = False if is_slot_shell else True
            self._apply_panel_visual_policy(panel, core)
            if not is_slot_shell:
                core_state = WorkbenchPanelState(
                    panel_id=panel_id,
                    panel_type=panel_type,
                    title=title,
                    subtitle=subtitle,
                    target_slot=slot,
                    role=role,
                    state=state_value,
                    visible=visible,
                    text=text,
                    icon_name=icon_name,
                    variant=variant,
                    density=density,
                    width_policy=width_policy,
                    padding=padding,
                    data_provider_id=data_provider_id,
                    data_query_id=data_query_id,
                    chart_mode=chart_mode,
                    chart_style_id=chart_style_id,
                    chart_palette_id=chart_palette_id,
                    chart_show_grid=chart_show_grid,
                    chart_show_glow=chart_show_glow,
                    chart_show_markers=chart_show_markers,
                    chart_smooth=chart_smooth,
                    chart_line_width=chart_line_width,
                    chart_fill_alpha=chart_fill_alpha,
                    height_policy=height_policy,
                    panel_height=panel_height,
                    list_options=list_options,
                    widget_props=normalize_widget_props(panel_type, widget_props),
                    behavior=normalize_behavior_binding(behavior),
                    dynamic=False,
                )
                self._render_dynamic_panel_content(panel, core_state)
        else:
            for item in session.dynamic_working:
                if item.panel_id != panel_id:
                    continue
                item.panel_type = panel_type
                item.title = title
                item.subtitle = subtitle
                item.target_slot = slot
                item.role = role
                item.state = state_value
                item.visible = visible
                item.icon_name = icon_name
                item.text = text
                item.variant = variant
                item.density = density
                item.width_policy = width_policy
                item.padding = padding
                item.height_policy = height_policy
                item.panel_height = panel_height
                item.data_provider_id = data_provider_id
                item.data_query_id = data_query_id
                item.chart_mode = chart_mode
                item.chart_style_id = chart_style_id
                item.chart_palette_id = chart_palette_id
                item.chart_show_grid = chart_show_grid
                item.chart_show_glow = chart_show_glow
                item.chart_show_markers = chart_show_markers
                item.chart_smooth = chart_smooth
                item.chart_line_width = chart_line_width
                item.chart_fill_alpha = chart_fill_alpha
                item.list_options = list_options
                item.widget_props = normalize_widget_props(panel_type, widget_props)
                item.behavior = normalize_behavior_binding(behavior)
                self._apply_panel_visual_policy(panel, item)
                self._render_dynamic_panel_content(panel, item)
                break

        self._refresh_core_indices(session, template)
        self._sync_dynamic_order_from_template(session, template)
        self._bind_editor_click_targets(template, session.context_id)
        self._enforce_tab_panel_budget(template, session, emit_warnings=True)
        self._mark_session_dirty(session)
        self.catalog.set_status_text(f"Applied properties for panel '{panel_id}'.")

    def _remove_editor_panel(self) -> None:
        session = self._current_editor_session()
        template = self._current_editor_template()
        if session is None or template is None:
            return
        panel_id = str(self.editor_panel_combo.currentData() or "").strip()
        if not panel_id:
            return
        if panel_id in session.core_working:
            self.catalog.set_status_text("Core panels cannot be removed. Add dynamic panels for custom layout.")
            return
        panel = template.panel(panel_id)
        if panel is not None:
            parent_layout = panel.parentWidget().layout() if panel.parentWidget() else None
            if isinstance(parent_layout, QVBoxLayout):
                parent_layout.removeWidget(panel)
            panel.setParent(None)
            panel.deleteLater()
        if hasattr(template, "_panels"):
            template._panels.pop(panel_id, None)  # type: ignore[attr-defined]
        session.dynamic_working = [item for item in session.dynamic_working if item.panel_id != panel_id]
        session.selected_panel_id = None
        self._sync_dynamic_order_from_template(session, template)
        self._bind_editor_click_targets(template, session.context_id)
        self._refresh_editor_panel_combo(session, template)
        if self.editor_panel_combo.count() > 0:
            session.selected_panel_id = str(self.editor_panel_combo.itemData(0) or "")
            self._set_selected_editor_panel(session, session.selected_panel_id)
        self._mark_session_dirty(session)
        self.catalog.set_status_text(f"Removed dynamic panel '{panel_id}'.")

    def _hidden_panel_candidates(self, session: WorkbenchEditorSession) -> list[tuple[str, str, str, str, bool]]:
        values: list[tuple[str, str, str, str, bool]] = []
        for panel_id, payload in session.core_working.items():
            state = str(payload.get("state") or "visible").strip().lower()
            user_hidden = bool(payload.get("user_hidden", False))
            if not user_hidden and state not in {"hidden", "collapsed", "hold", "background", "deferred"}:
                continue
            values.append(
                (
                    panel_id,
                    str(payload.get("title") or panel_id),
                    str(payload.get("slot") or "main"),
                    state or "hidden",
                    False,
                )
            )
        for item in session.dynamic_working:
            state = str(item.state or "visible").strip().lower()
            visible = bool(item.visible)
            if visible and state not in {"hidden", "collapsed", "hold", "background", "deferred"}:
                continue
            values.append((item.panel_id, item.title, item.target_slot, state or "hidden", True))
        values.sort(key=lambda row: (row[2], row[1].lower(), row[0]))
        return values

    def _hide_editor_panel(self) -> None:
        session = self._current_editor_session()
        template = self._current_editor_template()
        if session is None or template is None:
            return
        panel_id = str(self.editor_panel_combo.currentData() or "").strip()
        if not panel_id:
            return
        if self._is_structural_slot_shell(template, panel_id):
            self.catalog.set_status_text("Structural slot shells cannot be hidden.")
            return
        panel = template.panel(panel_id)
        if panel is None:
            return
        panel.set_panel_state("hidden")
        panel.setVisible(False)
        if panel_id in session.core_working:
            session.core_working[panel_id]["state"] = "hidden"
            session.core_working[panel_id]["visible"] = False
            session.core_working[panel_id]["user_hidden"] = True
        else:
            for item in session.dynamic_working:
                if item.panel_id == panel_id:
                    item.state = "hidden"
                    item.visible = False
                    break
        self._refresh_editor_panel_combo(session, template)
        self._mark_session_dirty(session)
        self.catalog.set_status_text(f"Panel '{panel_id}' hidden. Use Reopen Hidden to restore it.")

    def _reopen_hidden_panel(self) -> None:
        session = self._current_editor_session()
        template = self._current_editor_template()
        if session is None or template is None:
            return
        hidden_items = self._hidden_panel_candidates(session)
        if not hidden_items:
            self.catalog.set_status_text("No hidden/deferred panels available to reopen.")
            return
        labels: list[str] = []
        mapping: dict[str, str] = {}
        for panel_id, title, slot, state, is_dynamic in hidden_items:
            scope = "dynamic" if is_dynamic else "core"
            label = f"{title} · {panel_id} · {slot} · {state} · {scope}"
            labels.append(label)
            mapping[label] = panel_id
        selected, ok = QInputDialog.getItem(
            self,
            "Reopen Hidden Panel",
            "Select panel to reactivate:",
            labels,
            editable=False,
        )
        if not ok or not selected:
            return
        panel_id = mapping.get(str(selected), "")
        if not panel_id:
            return
        panel = template.panel(panel_id)
        if panel is None:
            self.catalog.set_status_text(f"Panel '{panel_id}' is unavailable in current context.")
            return
        panel.set_panel_state("visible")
        panel.setVisible(True)
        if panel_id in session.core_working:
            session.core_working[panel_id]["state"] = "visible"
            session.core_working[panel_id]["visible"] = True
            session.core_working[panel_id]["user_hidden"] = False
        else:
            for item in session.dynamic_working:
                if item.panel_id != panel_id:
                    continue
                item.state = "visible"
                item.visible = True
                self._render_dynamic_panel_content(panel, item)
                break
        self._refresh_editor_panel_combo(session, template)
        self._set_selected_editor_panel(session, panel_id)
        self._enforce_tab_panel_budget(template, session, emit_warnings=True)
        self._mark_session_dirty(session)
        self.catalog.set_status_text(f"Reopened panel '{panel_id}'.")

    def _move_editor_panel(self, delta: int) -> None:
        session = self._current_editor_session()
        template = self._current_editor_template()
        if session is None or template is None:
            return
        panel_id = str(self.editor_panel_combo.currentData() or "").strip()
        if not panel_id:
            return
        if self._is_structural_slot_shell(template, panel_id):
            self.catalog.set_status_text("Structural slot shells cannot be reordered.")
            return
        slot = self._panel_slot(template, panel_id)
        slot_panel_ids = self._slot_panel_ids(template, slot)
        if panel_id not in slot_panel_ids:
            return
        current_index = slot_panel_ids.index(panel_id)
        target_index = max(0, min(len(slot_panel_ids) - 1, current_index + int(delta)))
        if target_index == current_index:
            return
        if not template.move_panel(panel_id, target_slot=slot, index=target_index):
            self.catalog.set_status_text(f"Move rejected for panel '{panel_id}'.")
            return
        self._refresh_core_indices(session, template)
        self._sync_dynamic_order_from_template(session, template)
        self._bind_editor_click_targets(template, session.context_id)
        self._refresh_editor_panel_combo(session, template)
        self._set_selected_editor_panel(session, panel_id)
        self._mark_session_dirty(session)

    def _move_editor_panel_across_slot(self, direction: int) -> None:
        session = self._current_editor_session()
        template = self._current_editor_template()
        if session is None or template is None:
            return
        panel_id = str(self.editor_panel_combo.currentData() or "").strip()
        if not panel_id:
            return
        if self._is_structural_slot_shell(template, panel_id):
            self.catalog.set_status_text("Structural slot shells cannot move across slots.")
            return
        slot_order = ("main", "side", "status")
        current_slot = self._panel_slot(template, panel_id)
        if current_slot not in slot_order:
            return
        current_index = slot_order.index(current_slot)
        target_slot = slot_order[max(0, min(len(slot_order) - 1, current_index + int(direction)))]
        panel_state = self._panel_state_for_session(session, panel_id) or {}
        panel_type = str(panel_state.get("panel_type") or "text_markdown")
        spec = self._panel_type_registry.get(panel_type)
        if spec is not None and target_slot not in spec.allowed_slots:
            self.catalog.set_status_text(f"'{spec.title}' cannot be moved into slot '{target_slot}'.")
            return
        if not self._can_add_panel_to_slot(
            template=template,
            slot=target_slot,
            spec=spec or next(iter(self._panel_type_registry.values())),
            session=session,
            moving_panel_id=panel_id,
        ):
            self.catalog.set_status_text(f"Slot '{target_slot}' is at capacity; move blocked.")
            return
        if not template.move_panel(panel_id, target_slot=target_slot):
            self.catalog.set_status_text(f"Move rejected for panel '{panel_id}'.")
            return
        if panel_id in session.core_working:
            session.core_working[panel_id]["slot"] = target_slot
        else:
            for item in session.dynamic_working:
                if item.panel_id == panel_id:
                    item.target_slot = target_slot
                    break
        self._refresh_core_indices(session, template)
        self._sync_dynamic_order_from_template(session, template)
        self._bind_editor_click_targets(template, session.context_id)
        self._refresh_editor_panel_combo(session, template)
        self._set_selected_editor_panel(session, panel_id)
        self._mark_session_dirty(session)

    def _duplicate_editor_panel(self) -> None:
        session = self._current_editor_session()
        template = self._current_editor_template()
        if session is None or template is None:
            return
        panel_id = str(self.editor_panel_combo.currentData() or "").strip()
        if not panel_id:
            return
        if self._is_structural_slot_shell(template, panel_id):
            self.catalog.set_status_text("Structural slot shells cannot be duplicated.")
            return
        source_state = self._panel_state_for_session(session, panel_id)
        if source_state is None:
            return
        panel_type = str(source_state.get("panel_type") or "text_markdown")
        spec = self._panel_type_registry.get(panel_type) or next(iter(self._panel_type_registry.values()))
        slot = str(source_state.get("slot") or "main")
        if not self._can_add_panel_to_slot(template=template, slot=slot, spec=spec, session=session):
            self.catalog.set_status_text(f"Cannot duplicate panel into '{slot}' due to slot policy.")
            return
        state = self._new_panel_state(panel_type=panel_type, slot=slot, session=session)
        state.title = f"{str(source_state.get('title') or state.title)} Copy"
        state.subtitle = str(source_state.get("subtitle") or "")
        state.role = str(source_state.get("role") or state.role)
        state.state = str(source_state.get("state") or state.state)
        state.visible = bool(source_state.get("visible", True))
        state.text = str(source_state.get("text") or "")
        state.icon_name = str(source_state.get("icon_name") or state.icon_name)
        state.variant = str(source_state.get("variant") or "default")
        state.density = str(source_state.get("density") or "compact")
        state.width_policy = str(source_state.get("width_policy") or "stretch")
        state.padding = str(source_state.get("padding") or "normal")
        state.data_provider_id = str(source_state.get("data_provider_id") or "")
        state.data_query_id = str(source_state.get("data_query_id") or "")
        state.chart_mode = str(source_state.get("chart_mode") or "line")
        state.chart_style_id = str(source_state.get("chart_style_id") or "silver_line")
        state.chart_palette_id = str(source_state.get("chart_palette_id") or "auto")
        state.chart_show_grid = bool(source_state.get("chart_show_grid", True))
        state.chart_show_glow = bool(source_state.get("chart_show_glow", True))
        state.chart_show_markers = bool(source_state.get("chart_show_markers", False))
        state.chart_smooth = bool(source_state.get("chart_smooth", True))
        state.chart_line_width = int(source_state.get("chart_line_width") or 2)
        state.chart_fill_alpha = int(source_state.get("chart_fill_alpha") or 26)
        state.height_policy = str(source_state.get("height_policy") or "auto")
        state.panel_height = int(source_state.get("panel_height") or 0)
        list_options = source_state.get("list_options", ())
        if isinstance(list_options, (tuple, list)):
            state.list_options = tuple(str(item) for item in list_options)
        state.widget_props = normalize_widget_props(
            panel_type,
            source_state.get("widget_props") or default_widget_props(panel_type, title=state.title, text=state.text),
        )
        state.behavior = normalize_behavior_binding(source_state.get("behavior"))

        panel = template.create_panel(
            panel_id=state.panel_id,
            title=state.title,
            subtitle=state.subtitle,
            target_slot=state.target_slot,
            role=state.role,
            state=state.state,
            icon_name=state.icon_name or None,
            card_kind="muted",
        )
        after_index = None
        slot_ids = self._slot_panel_ids(template, slot)
        if panel_id in slot_ids:
            after_index = slot_ids.index(panel_id) + 1
        if after_index is not None:
            template.move_panel(state.panel_id, target_slot=slot, index=after_index)
        self._render_dynamic_panel_content(panel, state)
        session.dynamic_working.append(state)
        self._record_palette_recent(state.panel_type)
        self._sync_dynamic_order_from_template(session, template)
        self._bind_editor_click_targets(template, session.context_id)
        self._refresh_editor_panel_combo(session, template)
        self._set_selected_editor_panel(session, state.panel_id)
        self._enforce_tab_panel_budget(template, session, emit_warnings=True)
        self._mark_session_dirty(session)
        self.catalog.set_status_text(f"Duplicated panel '{panel_id}' as '{state.panel_id}'.")

    def _clone_context_into_new_tab(self) -> None:
        session = self._current_editor_session()
        if session is None:
            return
        entry = get_catalog_entry(session.entry_id) if session.entry_id else None
        if entry is None:
            self.catalog.set_status_text("Current editor context has no catalog entry to clone into a new tab.")
            return
        previous_selected = self._selected_entry_id
        self._selected_entry_id = entry.entry_id
        self._open_selected_in_workspace()
        tabs = self.catalog.workspace_tabs
        if tabs is None:
            self._selected_entry_id = previous_selected
            return
        active_tab = tabs.active_tab_id()
        if not active_tab:
            self._selected_entry_id = previous_selected
            return
        context_id = f"workspace:{active_tab}"
        target_session = self._editor_sessions.get(context_id)
        target_template = self._editor_templates.get(context_id)
        if target_session is None or target_template is None:
            self._selected_entry_id = previous_selected
            return
        target_session.core_working = deepcopy(session.core_working)
        target_session.dynamic_working = deepcopy(session.dynamic_working)
        target_session.split_working = tuple(session.split_working)
        target_session.core_baseline = deepcopy(session.core_baseline)
        target_session.dynamic_baseline = deepcopy(session.dynamic_baseline)
        target_session.split_baseline = tuple(session.split_baseline)
        target_session.dirty = session.dirty
        target_session.source_kind = session.source_kind
        target_session.source_ref = session.source_ref
        target_session.entry_id = session.entry_id
        self._apply_session_to_template(target_template, target_session)
        self._refresh_editor_contexts(select_context=context_id)
        self._selected_entry_id = previous_selected
        self.catalog.set_status_text(f"Cloned context '{session.context_id}' into new workspace tab '{active_tab}'.")

    def _resolve_insert_slot(
        self,
        *,
        session: WorkbenchEditorSession,
        template: GlassPanelTemplate,
        spec: WorkbenchPanelType,
    ) -> str:
        preferred = str(self.editor_insert_target_combo.currentData() or self.editor_insert_target_combo.currentText() or "auto")
        preferred = preferred.strip().lower()
        if preferred == "auto":
            selected = str(session.selected_panel_id or "").strip()
            if selected:
                selected_slot = self._panel_slot(template, selected)
                if selected_slot in spec.allowed_slots:
                    return selected_slot
            if "main" in spec.allowed_slots:
                return "main"
            return spec.allowed_slots[0] if spec.allowed_slots else "main"
        return preferred

    def _insert_index_for_slot(
        self,
        *,
        session: WorkbenchEditorSession,
        template: GlassPanelTemplate,
        slot: str,
    ) -> int | None:
        mode = str(self.editor_insert_position_combo.currentData() or self.editor_insert_position_combo.currentText() or "append")
        normalized = mode.strip().lower()
        if normalized == "append":
            return None
        selected = str(session.selected_panel_id or "").strip()
        if not selected:
            return None
        selected_slot = self._panel_slot(template, selected)
        if selected_slot != slot:
            return None
        slot_ids = self._slot_panel_ids(template, slot)
        if selected not in slot_ids:
            return None
        index = slot_ids.index(selected)
        if normalized == "before selected":
            return index
        if normalized == "after selected":
            return index + 1
        return None

    def _can_add_panel_to_slot(
        self,
        *,
        template: GlassPanelTemplate,
        slot: str,
        spec: WorkbenchPanelType,
        session: WorkbenchEditorSession | None = None,
        moving_panel_id: str | None = None,
    ) -> bool:
        capacity = int(self._editor_policy["max_panels_per_slot"].get(slot, 12))
        slot_ids = self._slot_panel_ids(template, slot)
        effective_count = len(slot_ids)
        if moving_panel_id and moving_panel_id in slot_ids:
            return True
        if effective_count >= capacity:
            return False
        if spec.max_per_slot is not None:
            active_session = session or self._current_editor_session()
            type_count = sum(
                1
                for panel_id in slot_ids
                if str((self._panel_state_for_session(active_session, panel_id) if active_session else {}).get("panel_type") or "")
                == spec.panel_type
            )
            if type_count >= int(spec.max_per_slot):
                return False
        return True

    def _record_palette_recent(self, panel_type: str) -> None:
        normalized = str(panel_type or "").strip().lower()
        if not normalized:
            return
        self._palette_recent = [normalized] + [item for item in self._palette_recent if item != normalized]
        self._palette_recent = self._palette_recent[:12]
        self._refresh_insert_palette()
    def _apply_editor_split(self) -> None:
        session = self._current_editor_session()
        template = self._current_editor_template()
        if session is None or template is None:
            return
        main = int(self.editor_main_slider.value())
        side = int(self.editor_side_slider.value())
        if main + side <= 0:
            main, side = 70, 30
        template.set_split_proportions(main=main, side=side)
        session.split_working = (main, side)
        self._mark_session_dirty(session)

    def _refresh_core_indices(self, session: WorkbenchEditorSession, template: GlassPanelTemplate) -> None:
        for slot_name in ("main", "side", "status"):
            ordered = self._slot_panel_ids(template, slot_name)
            for index, panel_id in enumerate(ordered):
                core = session.core_working.get(panel_id)
                if core is not None:
                    core["index"] = index
                    core["slot"] = slot_name

    def _sync_dynamic_order_from_template(self, session: WorkbenchEditorSession, template: GlassPanelTemplate) -> None:
        dynamic_by_id = {item.panel_id: item for item in session.dynamic_working}
        ordered: list[WorkbenchPanelState] = []
        for slot in ("main", "side", "status"):
            for panel_id in self._slot_panel_ids(template, slot):
                panel_state = dynamic_by_id.get(panel_id)
                if panel_state is None:
                    continue
                panel_state.target_slot = slot
                ordered.append(panel_state)
        for panel_state in session.dynamic_working:
            if panel_state not in ordered:
                ordered.append(panel_state)
        session.dynamic_working = ordered

    def _render_dynamic_panel_content(self, panel: GlassPanelFrame, state: WorkbenchPanelState) -> None:
        self._apply_panel_visual_policy(panel, state)
        panel.clear_content()
        content = self._build_panel_content_widget(state, panel)
        if content is not None:
            panel.set_content_widget(content)

    def _apply_panel_visual_policy(self, panel: GlassPanelFrame, state: WorkbenchPanelState | dict[str, Any]) -> None:
        width_policy = str(state.get("width_policy") if isinstance(state, dict) else state.width_policy or "stretch")
        padding = str(state.get("padding") if isinstance(state, dict) else state.padding or "normal")
        density = str(state.get("density") if isinstance(state, dict) else state.density or "compact")
        variant = str(state.get("variant") if isinstance(state, dict) else state.variant or "default")
        height_policy = str(state.get("height_policy") if isinstance(state, dict) else state.height_policy or "auto")
        panel_height = int(state.get("panel_height") if isinstance(state, dict) else state.panel_height or 0)
        slot_shell = bool(state.get("slot_shell", False)) if isinstance(state, dict) else False
        if width_policy == "fit":
            panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        elif width_policy == "fixed":
            panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            panel.setMinimumWidth(220)
        else:
            panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            panel.setMinimumWidth(0)
        margin_map = {
            "none": 0,
            "tight": 2,
            "normal": 4,
            "relaxed": 8,
        }
        margin = margin_map.get(padding, 4)
        if slot_shell:
            margin = 0
        panel.content_layout.setContentsMargins(margin, margin, margin, margin)
        if height_policy == "fixed" and panel_height > 0:
            clamped_height = max(96, min(760, int(panel_height)))
            panel.setMinimumHeight(clamped_height)
            panel.setMaximumHeight(clamped_height)
        else:
            panel.setMinimumHeight(0)
            panel.setMaximumHeight(16777215)
        panel.setProperty("editorVariant", variant)
        panel.setProperty("editorDensity", density)
        panel.setProperty("resizeAffordance", "false" if slot_shell else "true")
        panel.setToolTip("" if slot_shell else "Drag top band to move panel. Drag bottom edge to resize.")
        panel.style().unpolish(panel)
        panel.style().polish(panel)

    def _build_panel_content_widget(self, state: WorkbenchPanelState, parent: QWidget) -> QWidget:
        panel_type = str(state.panel_type or "text_markdown").strip().lower()
        options = list(state.list_options) if state.list_options else [item.strip() for item in state.text.split(",") if item.strip()]

        if panel_type == "empty_panel":
            host = QFrame(parent)
            host.setProperty("card", "clear")
            host_layout = QVBoxLayout(host)
            host_layout.setContentsMargins(4, 4, 4, 4)
            host_layout.setSpacing(4)
            label = QLabel("Empty panel shell", host)
            label.setProperty("role", "panel_subtitle")
            host_layout.addWidget(label)
            return host
        if panel_type in {"text_block", "text_markdown"}:
            label = QLabel(state.text or "Text/markdown panel", parent)
            label.setWordWrap(True)
            label.setProperty("role", "panel_subtitle")
            return label
        if panel_type == "title_subtitle_block":
            host = QFrame(parent)
            host_layout = QVBoxLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(4)
            title = QLabel(state.title or "Title", host)
            title.setProperty("role", "title")
            subtitle = QLabel(state.subtitle or state.text or "Subtitle", host)
            subtitle.setProperty("role", "panel_subtitle")
            subtitle.setWordWrap(True)
            host_layout.addWidget(title)
            host_layout.addWidget(subtitle)
            return host
        if panel_type == "form_input":
            host = QFrame(parent)
            host_layout = QVBoxLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(6)
            for placeholder in ("Name", "Email", "Notes"):
                field = QLineEdit(host)
                field.setPlaceholderText(placeholder)
                host_layout.addWidget(field)
            return host
        if panel_type == "form_section":
            host = QFrame(parent)
            host_layout = QFormLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(6)
            host_layout.addRow("Name", QLineEdit(host))
            host_layout.addRow("Owner", QLineEdit(host))
            host_layout.addRow("Status", QComboBox(host))
            return host
        if panel_type == "button_control":
            props = normalize_widget_props(panel_type, state.widget_props)
            binding = normalize_behavior_binding(state.behavior)
            host = QFrame(parent)
            host.setProperty("card", "clear")
            host_layout = QVBoxLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(2)
            button = QPushButton(props.get("text") or state.text or "Execute", host)
            object_name = str(props.get("object_name") or "").strip()
            if object_name:
                button.setObjectName(object_name)
            button.setToolTip(str(props.get("tooltip") or ""))
            button.setEnabled(bool(props.get("enabled", True)))
            button.setVisible(bool(props.get("visible", True)))
            button.setCheckable(bool(props.get("checkable", False)))
            button.setChecked(bool(props.get("checked", False) and button.isCheckable()))
            button.setProperty("variant", str(props.get("style_variant") or "default"))
            icon_name = str(props.get("icon_name") or "").strip()
            if icon_name:
                apply_icon(button, icon_name, size="small", tooltip=button.toolTip() or button.text())
            host_layout.addWidget(button, 0, Qt.AlignLeft)
            summary = QLabel(behavior_summary(binding), host)
            summary.setProperty("role", "microcopy")
            summary.setWordWrap(True)
            host_layout.addWidget(summary)
            return host
        if panel_type == "action_buttons":
            host = QFrame(parent)
            host_layout = QHBoxLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(6)
            for label in ("Run", "Pause", "Apply"):
                host_layout.addWidget(QPushButton(label, host))
            host_layout.addStretch(1)
            return host
        if panel_type == "toolbar_controls":
            host = QFrame(parent)
            host_layout = QHBoxLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(6)
            for label in ("Search", "Refresh", "Export", "Actions"):
                chip = QPushButton(label, host)
                host_layout.addWidget(chip)
            host_layout.addStretch(1)
            return host
        if panel_type == "search_filter_bar":
            host = QFrame(parent)
            host_layout = QHBoxLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(6)
            q = QLineEdit(host)
            q.setPlaceholderText("Search…")
            owner = QComboBox(host)
            owner.addItems(["all owners", "ops", "qa", "platform"])
            state_filter = QComboBox(host)
            state_filter.addItems(["all states", "ready", "warning", "error"])
            host_layout.addWidget(q, 2)
            host_layout.addWidget(owner, 1)
            host_layout.addWidget(state_filter, 1)
            return host
        if panel_type == "selector_list":
            host = QFrame(parent)
            host_layout = QVBoxLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(6)
            combo = QComboBox(host)
            combo.addItems(options or ["Option A", "Option B", "Option C"])
            host_layout.addWidget(combo)
            list_widget = QListWidget(host)
            list_widget.addItems(options or ["Alpha", "Beta", "Gamma"])
            host_layout.addWidget(list_widget, 1)
            return host
        if panel_type == "list_view":
            list_widget = QListWidget(parent)
            list_widget.addItems(options or ["Item 1", "Item 2", "Item 3"])
            return list_widget
        if panel_type == "table_grid":
            table = QTableWidget(4, 3, parent)
            table.setHorizontalHeaderLabels(["Name", "State", "Latency"])
            rows = [("api", "ready", "43ms"), ("queue", "warning", "210ms"), ("db", "ready", "18ms"), ("cache", "ready", "11ms")]
            for row, values in enumerate(rows):
                for col, value in enumerate(values):
                    table.setItem(row, col, QTableWidgetItem(value))
            return table
        if panel_type == "property_grid":
            table = QTableWidget(5, 2, parent)
            table.setHorizontalHeaderLabels(["Property", "Value"])
            pairs = [
                ("title", state.title),
                ("variant", state.variant),
                ("density", state.density),
                ("provider", state.data_provider_id or "-"),
                ("query", state.data_query_id or "-"),
            ]
            for row, (k, v) in enumerate(pairs):
                table.setItem(row, 0, QTableWidgetItem(str(k)))
                table.setItem(row, 1, QTableWidgetItem(str(v)))
            return table
        if panel_type == "chart_graph":
            return self._build_chart_panel_content(state, parent)
        if panel_type == "metrics_kpi":
            host = QFrame(parent)
            host_layout = QHBoxLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(8)
            for metric in ("p95 42ms", "err 0.8%", "throughput 320/s"):
                chip = QLabel(metric, host)
                chip.setProperty("role", "caption")
                chip.setObjectName("MetricChip")
                host_layout.addWidget(chip)
            host_layout.addStretch(1)
            return host
        if panel_type == "metric_card":
            host = QFrame(parent)
            host_layout = QVBoxLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(4)
            value = QLabel("42", host)
            value.setProperty("role", "title")
            caption = QLabel(state.text or "metric value", host)
            caption.setProperty("role", "caption")
            host_layout.addWidget(value)
            host_layout.addWidget(caption)
            return host
        if panel_type == "feed_log":
            feed = QListWidget(parent)
            feed.addItems(
                [
                    "12:40 event.created workspace.main",
                    "12:42 command.executed refresh.metrics",
                    "12:44 snapshot.updated workspace.summary",
                ]
            )
            return feed
        if panel_type == "timeline_activity":
            feed = QListWidget(parent)
            feed.addItems(
                [
                    "09:40 queued",
                    "09:42 running",
                    "09:45 completed",
                    "09:47 verified",
                ]
            )
            return feed
        if panel_type == "inspector_panel":
            host = QFrame(parent)
            host_layout = QVBoxLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(6)
            for row in (
                f"id: {state.panel_id}",
                f"type: {state.panel_type}",
                f"slot: {state.target_slot}",
                f"state: {state.state}",
                f"provider: {state.data_provider_id or '-'}",
            ):
                label = QLabel(row, host)
                label.setProperty("role", "caption")
                host_layout.addWidget(label)
            return host
        if panel_type == "image_svg":
            host = QFrame(parent)
            host_layout = QVBoxLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(6)
            icon_label = QLabel(host)
            icon = get_icon(state.icon_name or "component")
            icon_label.setPixmap(icon.pixmap(48, 48))
            icon_label.setAlignment(Qt.AlignCenter)
            text_label = QLabel(state.text or "Visual panel", host)
            text_label.setAlignment(Qt.AlignCenter)
            host_layout.addWidget(icon_label)
            host_layout.addWidget(text_label)
            return host
        if panel_type in {"json_diag", "code_panel"}:
            text = QTextEdit(parent)
            text.setReadOnly(True)
            text.setPlainText(
                json.dumps(
                    {
                        "panel_id": state.panel_id,
                        "state": state.state,
                        "slot": state.target_slot,
                        "role": state.role,
                        "visible": state.visible,
                        "variant": state.variant,
                        "density": state.density,
                        "provider_id": state.data_provider_id,
                        "query_id": state.data_query_id,
                    },
                    indent=2,
                    ensure_ascii=True,
                )
            )
            return text
        if panel_type == "dashboard_widget":
            host = QFrame(parent)
            host.setProperty("card", "clear")
            host_layout = QVBoxLayout(host)
            host_layout.setContentsMargins(4, 4, 4, 4)
            host_layout.setSpacing(4)
            title = QLabel(state.title or "Dashboard Widget", host)
            title.setProperty("role", "panel_title")
            body = QLabel(state.text or "Widget body", host)
            body.setWordWrap(True)
            status = QLabel("status: ready", host)
            status.setProperty("role", "caption")
            host_layout.addWidget(title)
            host_layout.addWidget(body)
            host_layout.addWidget(status)
            return host
        if panel_type == "status_badge_group":
            host = QFrame(parent)
            host_layout = QHBoxLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(6)
            for badge in (options or ["ready", "warning", "pending"]):
                label = QLabel(str(badge), host)
                label.setProperty("role", "caption")
                host_layout.addWidget(label)
            host_layout.addStretch(1)
            return host
        if panel_type == "split_container":
            splitter = QSplitter(Qt.Horizontal, parent)
            splitter.addWidget(QLabel("Left pane", splitter))
            splitter.addWidget(QLabel("Right pane", splitter))
            splitter.setSizes([2, 1])
            return splitter
        if panel_type == "tabbed_container":
            tabs = QTabWidget(parent)
            tab_a = QLabel("Tab A content", tabs)
            tab_a.setAlignment(Qt.AlignCenter)
            tab_b = QLabel("Tab B content", tabs)
            tab_b.setAlignment(Qt.AlignCenter)
            tabs.addTab(tab_a, "A")
            tabs.addTab(tab_b, "B")
            return tabs
        if panel_type == "stacked_container":
            host = QFrame(parent)
            host_layout = QVBoxLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(6)
            host_layout.addWidget(QLabel("Stack item 1", host))
            host_layout.addWidget(QLabel("Stack item 2", host))
            host_layout.addWidget(QLabel("Stack item 3", host))
            return host
        if panel_type == "header_section":
            host = QFrame(parent)
            host_layout = QVBoxLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(4)
            title = QLabel(state.title, host)
            title.setProperty("role", "title")
            subtitle = QLabel(state.subtitle or state.text or "", host)
            subtitle.setProperty("role", "panel_subtitle")
            subtitle.setWordWrap(True)
            host_layout.addWidget(title)
            host_layout.addWidget(subtitle)
            return host
        if panel_type == "section_shell":
            host = QFrame(parent)
            host.setProperty("card", "clear")
            host_layout = QVBoxLayout(host)
            host_layout.setContentsMargins(4, 4, 4, 4)
            host_layout.setSpacing(4)
            host_layout.addWidget(QLabel(state.title or "Section", host))
            subtitle = QLabel(state.subtitle or state.text or "", host)
            subtitle.setWordWrap(True)
            host_layout.addWidget(subtitle)
            return host
        if panel_type in {"empty_state_shell", "loading_state_shell", "error_state_shell"}:
            host = QFrame(parent)
            host.setProperty("card", "clear")
            host_layout = QVBoxLayout(host)
            host_layout.setContentsMargins(4, 4, 4, 4)
            host_layout.setSpacing(4)
            title = QLabel(state.title or panel_type.replace("_", " ").title(), host)
            title.setProperty("role", "panel_title")
            body = QLabel(state.text or "state message", host)
            body.setWordWrap(True)
            host_layout.addWidget(title)
            host_layout.addWidget(body)
            if panel_type == "error_state_shell":
                host_layout.addWidget(QPushButton("Retry", host))
            return host
        if panel_type == "divider_utility":
            divider = QLabel("────────────", parent)
            divider.setProperty("role", "caption")
            divider.setAlignment(Qt.AlignCenter)
            return divider
        spacer = QLabel(state.text or "Spacer / utility panel", parent)
        spacer.setProperty("role", "panel_subtitle")
        spacer.setWordWrap(True)
        return spacer

    def _resolve_chart_style(self, style_id: str) -> GlassChartStyle:
        fallback = list_chart_styles()
        if not fallback:
            register_builtin_chart_catalog(force=True)
            fallback = list_chart_styles()
        resolved = get_chart_style(style_id) if style_id else None
        return resolved or fallback[0]

    def _resolve_chart_palette(self, palette_id: str, *, style: GlassChartStyle) -> GlassChartPalette:
        fallback = list_chart_palettes()
        if not fallback:
            register_builtin_chart_catalog(force=True)
            fallback = list_chart_palettes()
        resolved = None
        normalized = str(palette_id or "").strip().lower()
        if normalized and normalized != "auto":
            resolved = get_chart_palette(normalized)
        if resolved is None:
            resolved = get_chart_palette(style.palette_id)
        return resolved or fallback[0]

    def _chart_values_from_result(self, state: WorkbenchPanelState) -> tuple[list[float], dict[str, Any]]:
        values: list[float] = []
        details: dict[str, Any] = {
            "state": "ready",
            "source": "fallback",
            "provider_id": state.data_provider_id or "",
            "query_id": state.data_query_id or "",
            "summary": {},
            "diagnostics": {},
            "error": None,
            "latency_ms": None,
            "refresh_policy": {},
        }
        provider_id = str(state.data_provider_id or "").strip().lower()
        query_id = str(state.data_query_id or "").strip().lower() or "time_series_placeholder"
        if provider_id:
            try:
                result = execute_data_query(DataQuery.create(provider_id, query_id=query_id))
                details["state"] = result.normalized_state()
                details["source"] = "provider"
                details["provider_id"] = result.provider_id
                details["query_id"] = result.query_id
                details["summary"] = dict(result.summary)
                details["diagnostics"] = dict(result.diagnostics)
                details["error"] = result.error.to_payload() if result.error else None
                details["latency_ms"] = result.latency_ms
                details["refresh_policy"] = result.refresh_policy.to_payload()
                raw_series = result.payload.get("series")
                if isinstance(raw_series, (list, tuple)):
                    for item in raw_series:
                        if isinstance(item, dict):
                            for key in ("value", "y", "v"):
                                if key in item:
                                    try:
                                        values.append(float(item[key]))
                                    except Exception:  # noqa: BLE001
                                        pass
                                    break
                        else:
                            try:
                                values.append(float(item))
                            except Exception:  # noqa: BLE001
                                continue
                if not values and result.metrics:
                    for value in result.metrics.values():
                        try:
                            values.append(float(value))
                        except Exception:  # noqa: BLE001
                            continue
                if not values and result.rows:
                    for row in result.rows:
                        if isinstance(row, dict):
                            for key in ("value", "latency_ms", "metric_value", "count", "age_s", "attempts"):
                                if key in row:
                                    try:
                                        values.append(float(row[key]))
                                    except Exception:  # noqa: BLE001
                                        pass
                                    break
            except Exception as exc:  # noqa: BLE001
                details["state"] = "error"
                details["source"] = "provider_error"
                details["error"] = {"message": str(exc)}
        if not values:
            parsed = [item.strip() for item in str(state.text or "").replace(";", ",").split(",") if item.strip()]
            for item in parsed:
                try:
                    values.append(float(item))
                except Exception:  # noqa: BLE001
                    continue
        if not values:
            values = [72, 74, 73, 79, 81, 80, 84, 87, 83, 85, 89, 91]
            details["source"] = "seed"
        return values, details

    def _build_chart_panel_content(self, state: WorkbenchPanelState, parent: QWidget) -> QWidget:
        style = self._resolve_chart_style(state.chart_style_id)
        palette = self._resolve_chart_palette(state.chart_palette_id, style=style)
        values, details = self._chart_values_from_result(state)

        host = QFrame(parent)
        host_layout = QVBoxLayout(host)
        host_layout.setContentsMargins(0, 0, 0, 0)
        host_layout.setSpacing(6)

        badges = QHBoxLayout()
        badges.setContentsMargins(0, 0, 0, 0)
        badges.setSpacing(6)
        mode_chip = QLabel(f"mode:{state.chart_mode}", host)
        mode_chip.setObjectName("MetricChip")
        style_chip = QLabel(f"style:{style.style_id}", host)
        style_chip.setObjectName("MetricChip")
        palette_chip = QLabel(f"palette:{palette.palette_id}", host)
        palette_chip.setObjectName("MetricChip")
        state_chip = QLabel(f"state:{details.get('state', 'ready')}", host)
        state_chip.setObjectName("MetricChip")
        badges.addWidget(mode_chip)
        badges.addWidget(style_chip)
        badges.addWidget(palette_chip)
        badges.addWidget(state_chip)
        badges.addStretch(1)
        host_layout.addLayout(badges)

        chart = _ChartPreviewCanvas(
            values=values,
            mode=state.chart_mode or style.default_mode,
            style=style,
            palette=palette,
            show_grid=bool(state.chart_show_grid),
            show_glow=bool(state.chart_show_glow),
            show_markers=bool(state.chart_show_markers),
            smooth=bool(state.chart_smooth),
            line_width=int(state.chart_line_width or style.line_width),
            fill_alpha=int(state.chart_fill_alpha or style.fill_alpha),
            parent=host,
        )
        host_layout.addWidget(chart, 1)

        source = str(details.get("source") or "seed")
        provider = str(details.get("provider_id") or state.data_provider_id or "(none)")
        query = str(details.get("query_id") or state.data_query_id or "(none)")
        latency = details.get("latency_ms")
        latency_text = f"{latency:.2f}ms" if isinstance(latency, (float, int)) else "n/a"
        summary = QLabel(
            f"source={source} · provider={provider} · query={query} · points={len(values)} · latency={latency_text}",
            host,
        )
        summary.setProperty("role", "caption")
        summary.setWordWrap(True)
        host_layout.addWidget(summary)
        return host

    def _apply_session_to_template(self, template: GlassPanelTemplate, session: WorkbenchEditorSession) -> None:
        for panel_id, payload in session.core_working.items():
            panel = template.panel(panel_id)
            if panel is None:
                continue
            panel.set_panel_title(str(payload.get("title") or panel_id))
            panel.set_panel_subtitle(str(payload.get("subtitle") or ""))
            panel.set_panel_role(str(payload.get("role") or "workspace"))
            panel.set_panel_state(str(payload.get("state") or "visible"))
            panel.setVisible(bool(payload.get("visible", True)))
            self._apply_panel_visual_policy(panel, payload)
            if bool(payload.get("content_override", False)) and not self._is_structural_slot_shell(template, panel_id):
                panel_state = WorkbenchPanelState(
                    panel_id=panel_id,
                    panel_type=str(payload.get("panel_type") or "text_markdown"),
                    title=str(payload.get("title") or panel_id),
                    subtitle=str(payload.get("subtitle") or ""),
                    target_slot=str(payload.get("slot") or "main"),
                    role=str(payload.get("role") or "workspace"),
                    state=str(payload.get("state") or "visible"),
                    visible=bool(payload.get("visible", True)),
                    text=str(payload.get("text") or ""),
                    icon_name=str(payload.get("icon_name") or ""),
                    variant=str(payload.get("variant") or "default"),
                    density=str(payload.get("density") or "compact"),
                    width_policy=str(payload.get("width_policy") or "stretch"),
                    padding=str(payload.get("padding") or "normal"),
                    data_provider_id=str(payload.get("data_provider_id") or ""),
                    data_query_id=str(payload.get("data_query_id") or ""),
                    chart_mode=str(payload.get("chart_mode") or "line"),
                    chart_style_id=str(payload.get("chart_style_id") or "silver_line"),
                    chart_palette_id=str(payload.get("chart_palette_id") or "auto"),
                    chart_show_grid=bool(payload.get("chart_show_grid", True)),
                    chart_show_glow=bool(payload.get("chart_show_glow", True)),
                    chart_show_markers=bool(payload.get("chart_show_markers", False)),
                    chart_smooth=bool(payload.get("chart_smooth", True)),
                    chart_line_width=int(payload.get("chart_line_width") or 2),
                    chart_fill_alpha=int(payload.get("chart_fill_alpha") or 26),
                    height_policy=str(payload.get("height_policy") or "auto"),
                    panel_height=int(payload.get("panel_height") or 0),
                    list_options=tuple(payload.get("list_options") or ()),
                    widget_props=normalize_widget_props(
                        str(payload.get("panel_type") or "text_markdown"),
                        payload.get("widget_props"),
                    ),
                    behavior=normalize_behavior_binding(payload.get("behavior")),
                    dynamic=bool(payload.get("dynamic", False)),
                )
                self._render_dynamic_panel_content(panel, panel_state)
            template.move_panel(
                panel_id,
                target_slot=str(payload.get("slot") or "main"),
                index=int(payload.get("index", 0)),
            )

        for panel_id in list(template.panel_ids()):
            if panel_id in session.core_working:
                continue
            panel = template.panel(panel_id)
            if panel is None:
                continue
            parent_layout = panel.parentWidget().layout() if panel.parentWidget() else None
            if isinstance(parent_layout, QVBoxLayout):
                parent_layout.removeWidget(panel)
            panel.setParent(None)
            panel.deleteLater()
            if hasattr(template, "_panels"):
                template._panels.pop(panel_id, None)  # type: ignore[attr-defined]

        for panel_state in session.dynamic_working:
            panel = template.panel(panel_state.panel_id)
            if panel is None:
                panel = template.create_panel(
                    panel_id=panel_state.panel_id,
                    title=panel_state.title,
                    subtitle=panel_state.subtitle,
                    target_slot=panel_state.target_slot,
                    role=panel_state.role,
                    state=panel_state.state,
                    icon_name=panel_state.icon_name or None,
                    card_kind="muted",
                )
            panel.set_panel_title(panel_state.title)
            panel.set_panel_subtitle(panel_state.subtitle)
            panel.set_panel_role(panel_state.role)
            panel.set_panel_state(panel_state.state)
            panel.setVisible(bool(panel_state.visible))
            self._apply_panel_visual_policy(panel, panel_state)
            template.move_panel(panel_state.panel_id, target_slot=panel_state.target_slot)
            self._render_dynamic_panel_content(panel, panel_state)

        template.set_split_proportions(main=session.split_working[0], side=session.split_working[1])
        self._refresh_core_indices(session, template)
        self._sync_dynamic_order_from_template(session, template)
        self._bind_editor_click_targets(template, session.context_id)
        self._enforce_tab_panel_budget(template, session)

    def _reset_editor_session(self) -> None:
        session = self._current_editor_session()
        template = self._current_editor_template()
        if session is None or template is None:
            return
        session.core_working = deepcopy(session.core_baseline)
        session.dynamic_working = deepcopy(session.dynamic_baseline)
        session.split_working = tuple(session.split_baseline)
        session.dirty = False
        session.selected_panel_id = None
        self._apply_session_to_template(template, session)
        self._refresh_editor_panel_combo(session, template)
        if self.editor_panel_combo.count() > 0:
            session.selected_panel_id = str(self.editor_panel_combo.itemData(0) or "")
            self._set_selected_editor_panel(session, session.selected_panel_id)
        self._sync_editor_status(session)
        self.catalog.set_status_text(f"Editor context '{session.context_id}' reset to pristine baseline.")

    def _clone_root_path(self) -> Path:
        root = Path(__file__).resolve().parents[4] / "tools" / "_local" / "pyside6_glass" / "workbench_clones"
        root.mkdir(parents=True, exist_ok=True)
        return root

    def _save_clone(self) -> None:
        session = self._current_editor_session()
        if session is None:
            return
        response = QMessageBox.question(
            self,
            "Save Clone",
            "Clone current edited configuration?\n\nYes: save to clone folder and continue on clone.\nNo: keep editing without saving.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if response != QMessageBox.Yes:
            return
        default_name = f"{session.entry_id or session.context_id}_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        clone_name, ok = QInputDialog.getText(self, "Clone Name", "Clone file name:", text=default_name)
        if not ok:
            return
        safe_name = "".join(ch for ch in clone_name if ch.isalnum() or ch in ("-", "_")).strip("_-")
        if not safe_name:
            safe_name = default_name.replace(":", "_")
        clone_path = self._clone_root_path() / f"{safe_name}.json"
        payload = session.clone_payload()
        payload["schema"] = "glass_workbench_clone_v1"
        payload["clone_name"] = safe_name
        payload["saved_at_local"] = dt.datetime.now().isoformat()
        clone_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")

        session.source_kind = "clone"
        session.source_ref = str(clone_path)
        session.core_baseline = deepcopy(session.core_working)
        session.dynamic_baseline = deepcopy(session.dynamic_working)
        session.split_baseline = tuple(session.split_working)
        session.dirty = False
        self._sync_editor_status(session)
        self.catalog.set_status_text(f"Clone saved: {clone_path}")

    def _open_clone(self) -> None:
        session = self._current_editor_session()
        template = self._current_editor_template()
        if session is None or template is None:
            return
        root = self._clone_root_path()
        clones = sorted(root.glob("*.json"))
        if not clones:
            self.catalog.set_status_text("No clones available yet. Use Save Clone first.")
            return
        labels = [path.name for path in clones]
        selected, ok = QInputDialog.getItem(self, "Open Clone", "Select clone:", labels, editable=False)
        if not ok or not selected:
            return
        clone_path = root / str(selected)
        try:
            payload = json.loads(clone_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            self.catalog.set_status_text(f"Failed to load clone '{selected}': {exc}")
            return

        core_payload = payload.get("core", {})
        dynamic_payload = payload.get("dynamic", [])
        split_payload = payload.get("split", {})
        dynamic_items: list[WorkbenchPanelState] = []
        for item in dynamic_payload:
            dynamic_items.append(
                WorkbenchPanelState(
                    panel_id=str(item.get("panel_id") or ""),
                    panel_type=str(item.get("panel_type") or "text_markdown"),
                    title=str(item.get("title") or "Panel"),
                    subtitle=str(item.get("subtitle") or ""),
                    target_slot=str(item.get("target_slot") or "main"),
                    role=str(item.get("role") or "workspace"),
                    state=str(item.get("state") or "visible"),
                    visible=bool(item.get("visible", True)),
                    text=str(item.get("text") or ""),
                    icon_name=str(item.get("icon_name") or ""),
                    variant=str(item.get("variant") or "default"),
                    density=str(item.get("density") or "compact"),
                    width_policy=str(item.get("width_policy") or "stretch"),
                    padding=str(item.get("padding") or "normal"),
                    data_provider_id=str(item.get("data_provider_id") or ""),
                    data_query_id=str(item.get("data_query_id") or ""),
                    chart_mode=str(item.get("chart_mode") or "line"),
                    chart_style_id=str(item.get("chart_style_id") or "silver_line"),
                    chart_palette_id=str(item.get("chart_palette_id") or "auto"),
                    chart_show_grid=bool(item.get("chart_show_grid", True)),
                    chart_show_glow=bool(item.get("chart_show_glow", True)),
                    chart_show_markers=bool(item.get("chart_show_markers", False)),
                    chart_smooth=bool(item.get("chart_smooth", True)),
                    chart_line_width=int(item.get("chart_line_width") or 2),
                    chart_fill_alpha=int(item.get("chart_fill_alpha") or 26),
                    height_policy=str(item.get("height_policy") or "auto"),
                    panel_height=int(item.get("panel_height") or 0),
                    list_options=tuple(item.get("list_options") or ()),
                    widget_props=normalize_widget_props(
                        str(item.get("panel_type") or "text_markdown"),
                        item.get("widget_props"),
                    ),
                    behavior=normalize_behavior_binding(item.get("behavior")),
                    dynamic=True,
                )
            )
        split = (
            int(split_payload.get("main", session.split_working[0])),
            int(split_payload.get("side", session.split_working[1])),
        )

        session.source_kind = "clone"
        session.source_ref = str(clone_path)
        session.core_baseline = deepcopy(core_payload) if isinstance(core_payload, dict) else deepcopy(session.core_baseline)
        session.core_working = deepcopy(session.core_baseline)
        session.dynamic_baseline = deepcopy(dynamic_items)
        session.dynamic_working = deepcopy(dynamic_items)
        session.split_baseline = tuple(split)
        session.split_working = tuple(split)
        session.panel_counter = max([session.panel_counter] + [int(item.panel_id.split("_")[-1]) for item in dynamic_items if item.panel_id.startswith("dyn_") and item.panel_id.split("_")[-1].isdigit()])
        session.selected_panel_id = None
        session.dirty = False

        self._apply_session_to_template(template, session)
        self._refresh_editor_panel_combo(session, template)
        if self.editor_panel_combo.count() > 0:
            session.selected_panel_id = str(self.editor_panel_combo.itemData(0) or "")
            self._set_selected_editor_panel(session, session.selected_panel_id)
        self._sync_editor_status(session)
        self.catalog.set_status_text(f"Clone loaded: {clone_path}")

    def _enforce_tab_panel_budget(
        self,
        template: GlassPanelTemplate,
        session: WorkbenchEditorSession,
        *,
        heavy_budget: int | None = None,
        emit_warnings: bool = False,
    ) -> None:
        resolved_heavy_budget = int(heavy_budget if heavy_budget is not None else self._editor_policy["heavy_panels_per_tab"])
        live_data_budget = int(self._editor_policy["live_data_widgets_per_tab"])
        policy_messages: list[str] = []
        heavy_ids = [
            item.panel_id
            for item in session.dynamic_working
            if item.visible and self._panel_type_registry.get(item.panel_type, WorkbenchPanelType("", "", "", "", "", "", "")).heavy
        ]
        for index, panel_id in enumerate(heavy_ids):
            if index < resolved_heavy_budget:
                continue
            panel = template.panel(panel_id)
            if panel is None:
                continue
            panel.set_panel_state("hold")
            panel.setVisible(False)
            for item in session.dynamic_working:
                if item.panel_id == panel_id:
                    item.state = "hold"
                    item.visible = False
                    policy_messages.append(
                        f"Heavy budget exceeded ({resolved_heavy_budget}). '{item.title}' set to hold/off."
                    )
                    break

        live_data_types = {"chart_graph", "feed_log", "table_grid", "json_diag", "dashboard_widget", "timeline_activity"}
        active_live = [
            item
            for item in session.dynamic_working
            if item.visible and item.state == "visible" and item.panel_type in live_data_types
        ]
        for index, item in enumerate(active_live):
            if index < live_data_budget:
                continue
            panel = template.panel(item.panel_id)
            if panel is None:
                continue
            panel.set_panel_state("background")
            panel.setVisible(False)
            item.state = "background"
            item.visible = False
            policy_messages.append(
                f"Live data widget budget exceeded ({live_data_budget}). '{item.title}' moved to background."
            )

        if policy_messages:
            self._editor_policy_messages = policy_messages
            self.editor_policy_label.setText("Policies: " + " | ".join(policy_messages[:3]))
            if emit_warnings:
                self.catalog.set_status_text(policy_messages[0])
        else:
            self._editor_policy_messages = []
            self.editor_policy_label.setText(
                "Policies: active tab only, heavy<=3 per tab, live-data<=4 per tab, inactive tabs lazy."
            )

    def _on_workspace_tab_changed(self) -> None:
        self._enforce_workspace_budget()
        tabs = self.catalog.workspace_tabs
        if tabs is None:
            return
        active_tab = tabs.active_tab_id()
        if not active_tab:
            self._discard_pending_panel_candidate(announce=False)
            self._refresh_editor_contexts()
            return
        context_id = f"workspace:{active_tab}"
        pending_context = str(self._pending_candidate_context_id or "")
        if pending_context and pending_context != context_id:
            self._discard_pending_panel_candidate(announce=False)
        self._refresh_editor_contexts(select_context=context_id)

    def _safe_json_parse(self, raw: str) -> dict[str, Any]:
        text = str(raw or "").strip()
        if not text:
            return {}
        try:
            parsed = json.loads(text)
        except Exception:  # noqa: BLE001
            return {"raw": text}
        if isinstance(parsed, dict):
            return parsed
        return {"value": parsed}

    def _rect_payload(self, rect: QRect) -> dict[str, int]:
        return {
            "x": int(rect.x()),
            "y": int(rect.y()),
            "width": int(rect.width()),
            "height": int(rect.height()),
        }

    def _active_editor_geometry_payload(self) -> dict[str, dict[str, int]]:
        template = self._current_editor_template()
        if template is None:
            return {}
        payload: dict[str, dict[str, int]] = {}
        for panel_id in template.panel_ids():
            panel = template.panel(panel_id)
            if panel is None:
                continue
            global_rect = QRect(panel.mapToGlobal(QPoint(0, 0)), panel.size())
            payload[panel_id] = {
                "x": int(global_rect.x()),
                "y": int(global_rect.y()),
                "width": int(global_rect.width()),
                "height": int(global_rect.height()),
            }
        return payload

    def semantic_checkpoint_snapshot(self, *, checkpoint_id: str = "") -> dict[str, Any]:
        tabs = self.catalog.workspace_tabs
        tab_ids = tabs.tab_ids() if tabs is not None else []
        visible_tab_ids = tabs.visible_tab_ids() if tabs is not None else []
        active_tab_id = tabs.active_tab_id() if tabs is not None else ""
        active_context = self._current_editor_context_id()
        session = self._current_editor_session()
        template = self._current_editor_template()

        mounted_panel_ids: list[str] = []
        hidden_panel_ids: list[str] = []
        slot_assignments: dict[str, str] = {}
        if template is not None:
            mounted_panel_ids = list(template.panel_ids())
            for panel_id in mounted_panel_ids:
                slot_assignments[panel_id] = self._panel_slot(template, panel_id)
        if session is not None:
            for panel_id, item in session.core_working.items():
                if (not bool(item.get("visible", True))) or str(item.get("state") or "visible").lower() in {"hidden", "collapsed"}:
                    hidden_panel_ids.append(panel_id)
            for item in session.dynamic_working:
                if (not bool(item.visible)) or str(item.state).lower() in {"hidden", "collapsed"}:
                    hidden_panel_ids.append(item.panel_id)

        status_event = self._action_trace[-1] if self._action_trace else {}
        window_rect = self.window().geometry() if isinstance(self.window(), QWidget) else self.geometry()
        workspace_bounds = self._workspace_bounds(template) if template is not None else QRect()
        lazy_mount_state = {
            tab_id: {
                "mounted": bool(host.is_mounted()),
                "title": str(getattr(host, "_title", tab_id)),
            }
            for tab_id, host in self._workspace_hosts.items()
        }

        snapshot = {
            "checkpoint_id": str(checkpoint_id or "").strip(),
            "captured_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "active_workspace_id": active_tab_id or self._default_workspace_tab_id(),
            "active_tab_id": active_tab_id,
            "workspace_tab_ids": list(tab_ids),
            "visible_tab_ids": list(visible_tab_ids),
            "mounted_panel_ids": mounted_panel_ids,
            "hidden_panel_ids": sorted(set(hidden_panel_ids)),
            "slot_assignments": slot_assignments,
            "panel_geometries": self._active_editor_geometry_payload(),
            "window_geometry": self._rect_payload(window_rect),
            "workspace_bounds": self._rect_payload(workspace_bounds),
            "selected_entry_id": str(self._selected_entry_id or ""),
            "picker_open": bool(getattr(self, "entry_picker_dialog", None) and self.entry_picker_dialog.isVisible()),
            "catalog_visible": bool(self._catalog_panel_visible),
            "inspector_visible": bool(self._inspector_panel_visible),
            "runtime_state": self._safe_json_parse(self.runtime_diagnostics_text.toPlainText() if hasattr(self, "runtime_diagnostics_text") else ""),
            "data_state": self._safe_json_parse(self.query_probe_text.toPlainText() if hasattr(self, "query_probe_text") else ""),
            "clone_state": {
                "source_kind": str(session.source_kind if session is not None else ""),
                "source_ref": str(session.source_ref if session is not None else ""),
            },
            "dirty_state": {
                "context_id": active_context,
                "is_dirty": bool(session.dirty) if session is not None else False,
            },
            "lazy_mount_state": lazy_mount_state,
            "budget_counters": {
                "workspace_active_budget": int(self._workspace_active_budget),
                "heavy_panels_per_tab": int(self._editor_policy.get("heavy_panels_per_tab", 0)),
                "live_data_widgets_per_tab": int(self._editor_policy.get("live_data_widgets_per_tab", 0)),
                "policy_messages": list(self._editor_policy_messages),
            },
            "current_status": {
                "text": str(status_event.get("action", "")),
                "severity": str(status_event.get("level", "info")),
            },
            "recent_action_trace": list(self._action_trace[-20:]),
        }
        return snapshot

    def capture_semantic_checkpoint(self, checkpoint_id: str) -> dict[str, Any]:
        return self.semantic_checkpoint_snapshot(checkpoint_id=checkpoint_id)

    def capture_checkpoint_screenshot(self, path: Path) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            pixmap = self.grab()
            if pixmap.isNull():
                return False
            return bool(pixmap.save(str(path)))
        except Exception:  # noqa: BLE001
            return False
