from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Iterable, Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush, QFont, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .contracts import DEFAULT_THEME_ID
from .theme import get_palette

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None  # type: ignore[assignment]

try:
    import pyqtgraph as pg
except Exception:  # pragma: no cover - optional dependency
    pg = None  # type: ignore[assignment]

try:
    import qtawesome as qta
except Exception:  # pragma: no cover - optional dependency
    qta = None  # type: ignore[assignment]

try:
    from superqt import QCollapsible, QLabeledDoubleSlider
except Exception:  # pragma: no cover - optional dependency
    QCollapsible = None  # type: ignore[assignment]
    QLabeledDoubleSlider = None  # type: ignore[assignment]


def _missing_enhanced_chart_dependencies() -> tuple[str, ...]:
    missing: list[str] = []
    if np is None:
        missing.append("numpy")
    if pg is None:
        missing.append("pyqtgraph")
    if qta is None:
        missing.append("qtawesome")
    if QCollapsible is None or QLabeledDoubleSlider is None:
        missing.append("superqt")
    return tuple(missing)


def _require_enhanced_chart_dependencies() -> None:
    missing = _missing_enhanced_chart_dependencies()
    if missing:
        deps = ", ".join(sorted(set(missing)))
        raise RuntimeError(f"Enhanced chart rendering requires optional dependencies: {deps}")


@dataclass(frozen=True, slots=True)
class GlassChartPalette:
    palette_id: str
    title: str
    description: str
    colors: tuple[str, ...]
    order: int = 100
    tags: tuple[str, ...] = ()

    def normalized(self) -> "GlassChartPalette":
        palette_id = str(self.palette_id or "").strip().lower()
        if not palette_id:
            raise ValueError("palette_id is required")
        title = str(self.title or "").strip()
        if not title:
            raise ValueError("title is required")
        colors = tuple(str(item).strip() for item in self.colors if str(item).strip())
        if not colors:
            raise ValueError("colors is required")
        return GlassChartPalette(
            palette_id=palette_id,
            title=title,
            description=str(self.description or "").strip(),
            colors=colors,
            order=max(0, int(self.order)),
            tags=tuple(str(item).strip().lower() for item in self.tags if str(item).strip()),
        )


@dataclass(frozen=True, slots=True)
class GlassChartStyle:
    style_id: str
    title: str
    description: str
    palette_id: str
    default_mode: str = "line"
    supported_modes: tuple[str, ...] = ("line", "area", "bar", "spark")
    show_grid: bool = True
    show_glow: bool = True
    show_markers: bool = False
    smooth: bool = True
    line_width: int = 2
    fill_alpha: int = 26
    order: int = 100
    tags: tuple[str, ...] = ()

    def normalized(self) -> "GlassChartStyle":
        style_id = str(self.style_id or "").strip().lower()
        if not style_id:
            raise ValueError("style_id is required")
        title = str(self.title or "").strip()
        if not title:
            raise ValueError("title is required")
        palette_id = str(self.palette_id or "").strip().lower()
        if not palette_id:
            raise ValueError("palette_id is required")
        default_mode = str(self.default_mode or "line").strip().lower()
        supported_modes = tuple(
            str(item).strip().lower()
            for item in self.supported_modes
            if str(item).strip().lower() in {"line", "area", "bar", "spark"}
        ) or ("line", "area", "bar", "spark")
        if default_mode not in supported_modes:
            default_mode = supported_modes[0]
        return GlassChartStyle(
            style_id=style_id,
            title=title,
            description=str(self.description or "").strip(),
            palette_id=palette_id,
            default_mode=default_mode,
            supported_modes=supported_modes,
            show_grid=bool(self.show_grid),
            show_glow=bool(self.show_glow),
            show_markers=bool(self.show_markers),
            smooth=bool(self.smooth),
            line_width=max(1, min(8, int(self.line_width))),
            fill_alpha=max(0, min(70, int(self.fill_alpha))),
            order=max(0, int(self.order)),
            tags=tuple(str(item).strip().lower() for item in self.tags if str(item).strip()),
        )


@dataclass(frozen=True, slots=True)
class GlassChartSeries:
    name: str
    x: tuple[float, ...]
    y: tuple[float, ...]
    mode: str | None = None
    color_index: int = 0
    width_scale: float = 1.0
    visible: bool = True
    fill_to_zero: bool = False
    symbol: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def normalized(self) -> "GlassChartSeries":
        name = str(self.name or "Series").strip() or "Series"
        x_values = tuple(float(v) for v in self.x)
        y_values = tuple(float(v) for v in self.y)
        if not x_values or not y_values:
            raise ValueError("series requires x and y values")
        if len(x_values) != len(y_values):
            raise ValueError("x and y must have the same length")
        mode = str(self.mode or "").strip().lower() or None
        if mode is not None and mode not in {"line", "area", "bar", "spark"}:
            raise ValueError(f"unsupported series mode '{mode}'")
        symbol = str(self.symbol or "").strip() or None
        return GlassChartSeries(
            name=name,
            x=x_values,
            y=y_values,
            mode=mode,
            color_index=max(0, int(self.color_index)),
            width_scale=max(0.35, float(self.width_scale)),
            visible=bool(self.visible),
            fill_to_zero=bool(self.fill_to_zero),
            symbol=symbol,
            metadata=dict(self.metadata or {}),
        )


@dataclass(frozen=True, slots=True)
class GlassChartTheme:
    style: GlassChartStyle
    palette: GlassChartPalette
    background_top: QColor
    background_bottom: QColor
    grid_major: QColor
    grid_minor: QColor
    text_primary: QColor
    text_muted: QColor
    line_colors: tuple[QColor, ...]
    glow_color: QColor
    bar_brushes: tuple[QBrush, ...]


_PALETTES: dict[str, GlassChartPalette] = {}
_STYLES: dict[str, GlassChartStyle] = {}
_LOCK = RLock()

_STATE_STYLE_PREFERENCES: dict[str, tuple[str, ...]] = {
    "loading": ("graphite_spark", "graphite_clean"),
    "ready": ("silver_line", "silver_area", "ops_health"),
    "empty": ("graphite_clean", "silver_line"),
    "error": ("incident_trace", "warning_watch"),
    "stale": ("warning_watch", "warning_bars", "ops_queue"),
}
_MODE_STYLE_PREFERENCES: dict[str, tuple[str, ...]] = {
    "dashboard": ("ops_health", "silver_area", "obsidian_monitor"),
    "analyst": ("teal_precision", "obsidian_depth", "silver_line"),
    "operator": ("ops_queue", "warning_watch", "incident_trace"),
    "monitoring": ("ops_queue", "warning_watch", "incident_trace"),
    "presentation": ("silver_area", "violet_signal", "sunrise_peak"),
}
_LEVEL_STYLE_PREFERENCES: dict[str, tuple[str, ...]] = {
    "performance": ("graphite_clean", "graphite_spark", "silver_line"),
    "standard": ("silver_line", "silver_area", "ops_health"),
    "premium": ("ops_health", "teal_precision", "obsidian_depth"),
    "showcase": ("violet_signal", "sunrise_peak", "mint_fresh"),
}


def register_chart_palette(palette: GlassChartPalette, *, override: bool = False) -> GlassChartPalette:
    normalized = palette.normalized()
    with _LOCK:
        if normalized.palette_id in _PALETTES and not override:
            raise ValueError(f"chart palette '{normalized.palette_id}' already registered")
        _PALETTES[normalized.palette_id] = normalized
    return normalized


def list_chart_palettes() -> tuple[GlassChartPalette, ...]:
    with _LOCK:
        values = list(_PALETTES.values())
    values.sort(key=lambda item: (item.order, item.title.lower(), item.palette_id))
    return tuple(values)


def get_chart_palette(palette_id: str) -> GlassChartPalette | None:
    key = str(palette_id or "").strip().lower()
    if not key:
        return None
    with _LOCK:
        return _PALETTES.get(key)


def register_chart_style(style: GlassChartStyle, *, override: bool = False) -> GlassChartStyle:
    normalized = style.normalized()
    with _LOCK:
        if normalized.style_id in _STYLES and not override:
            raise ValueError(f"chart style '{normalized.style_id}' already registered")
        if normalized.palette_id not in _PALETTES:
            raise ValueError(f"chart style palette '{normalized.palette_id}' is not registered")
        _STYLES[normalized.style_id] = normalized
    return normalized


def list_chart_styles() -> tuple[GlassChartStyle, ...]:
    with _LOCK:
        values = list(_STYLES.values())
    values.sort(key=lambda item: (item.order, item.title.lower(), item.style_id))
    return tuple(values)


def get_chart_style(style_id: str) -> GlassChartStyle | None:
    key = str(style_id or "").strip().lower()
    if not key:
        return None
    with _LOCK:
        return _STYLES.get(key)


def resolve_chart_style(
    *,
    style_id: str | None = None,
    palette_id: str | None = None,
    data_state: str = "ready",
    experience_mode: str = "default",
    visual_level: str = "standard",
) -> GlassChartStyle:
    if not _STYLES:
        register_builtin_chart_catalog()

    normalized_palette = str(palette_id or "").strip().lower()
    if normalized_palette:
        if get_chart_palette(normalized_palette) is None:
            raise ValueError(f"chart palette '{normalized_palette}' is not registered")

    normalized_state = str(data_state or "ready").strip().lower()
    normalized_mode = str(experience_mode or "default").strip().lower()
    normalized_level = str(visual_level or "standard").strip().lower()

    candidates: list[str] = []
    explicit_style = str(style_id or "").strip().lower()
    if explicit_style:
        candidates.append(explicit_style)
    candidates.extend(_MODE_STYLE_PREFERENCES.get(normalized_mode, ()))
    candidates.extend(_STATE_STYLE_PREFERENCES.get(normalized_state, ()))
    candidates.extend(_LEVEL_STYLE_PREFERENCES.get(normalized_level, ()))
    candidates.extend(("silver_line", "graphite_clean"))

    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate or "").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        style = get_chart_style(key)
        if style is None:
            continue
        if normalized_palette and style.palette_id != normalized_palette:
            if explicit_style:
                raise ValueError(
                    f"chart style '{style.style_id}' uses palette '{style.palette_id}', expected '{normalized_palette}'"
                )
            continue
        return style

    styles = list_chart_styles()
    if not styles:
        raise ValueError("chart style registry is empty")
    fallback = styles[0]
    if normalized_palette and fallback.palette_id != normalized_palette:
        for style in styles:
            if style.palette_id == normalized_palette:
                return style
        raise ValueError(f"no chart style available for palette '{normalized_palette}'")
    return fallback


def resolve_chart_contract(
    *,
    style_id: str | None = None,
    palette_id: str | None = None,
    data_state: str = "ready",
    experience_mode: str = "default",
    visual_level: str = "standard",
) -> tuple[GlassChartStyle, GlassChartPalette]:
    style = resolve_chart_style(
        style_id=style_id,
        palette_id=palette_id,
        data_state=data_state,
        experience_mode=experience_mode,
        visual_level=visual_level,
    )
    palette = get_chart_palette(style.palette_id)
    if palette is None:
        raise ValueError(f"chart style '{style.style_id}' references unknown palette '{style.palette_id}'")
    return style, palette


def _register_defaults(*, force: bool = False) -> None:
    palettes = (
        GlassChartPalette("silver_frost", "Silver Frost", "Neutral silver-frost blend.", ("#e9f3ff", "#8cefff", "#a8b7d1", "#d7e1ff"), order=10, tags=("frost", "silver", "neutral")),
        GlassChartPalette("graphite_mono", "Graphite Mono", "Low-saturation graphite monochrome.", ("#dde4ee", "#bdcad9", "#9eaec0", "#7f8fa4"), order=20, tags=("mono", "graphite")),
        GlassChartPalette("ops_emerald", "Ops Emerald", "Operational healthy-state palette.", ("#bff3d8", "#6ed6a4", "#3ebc82", "#2a8f65"), order=30, tags=("ops", "green")),
        GlassChartPalette("signal_amber", "Signal Amber", "Watch/warning signal palette.", ("#ffe8be", "#f9c86c", "#e9a946", "#b6792d"), order=40, tags=("warning", "amber")),
        GlassChartPalette("incident_crimson", "Incident Crimson", "Incident/critical emphasis palette.", ("#ffd2ce", "#f29690", "#de5a56", "#b83f3d"), order=50, tags=("critical", "red")),
        GlassChartPalette("cool_teal", "Cool Teal", "Cyan-teal tech spectrum.", ("#c8f7ff", "#7defff", "#49c8d9", "#2e96ab"), order=60, tags=("teal", "cool")),
        GlassChartPalette("violet_steel", "Violet Steel", "Muted violet + steel tones.", ("#e8e3ff", "#b9b2e8", "#8f88c8", "#6a6699"), order=70, tags=("violet", "muted")),
        GlassChartPalette("sunrise_heat", "Sunrise Heat", "Warm sunrise performance spectrum.", ("#fff1d4", "#ffcd88", "#ff9f62", "#dd6b5b"), order=80, tags=("warm", "heat")),
        GlassChartPalette("mint_cyan", "Mint Cyan", "Fresh mint-cyan blended palette.", ("#dffcf5", "#a7f1df", "#7adfcc", "#55b8af"), order=90, tags=("mint", "cyan")),
        GlassChartPalette("obsidian_blue", "Obsidian Blue", "Dark-mode friendly blue-gray palette.", ("#d4def4", "#95a8d3", "#667fb5", "#3f5b90"), order=100, tags=("dark", "blue")),
    )
    for palette in palettes:
        try:
            register_chart_palette(palette, override=force)
        except ValueError:
            if force:
                raise

    styles = (
        GlassChartStyle("silver_line", "Silver Line", "Balanced line chart for operational trends.", "silver_frost", default_mode="line", show_grid=True, show_glow=True, show_markers=False, smooth=True, line_width=2, fill_alpha=18, order=10, tags=("line", "default")),
        GlassChartStyle("silver_area", "Silver Area", "Area chart for volume and baseline tracking.", "silver_frost", default_mode="area", show_grid=True, show_glow=True, show_markers=False, smooth=True, line_width=2, fill_alpha=30, order=20, tags=("area", "volume")),
        GlassChartStyle("silver_bar", "Silver Bars", "Bar-style comparison for categorical snapshots.", "silver_frost", default_mode="bar", show_grid=True, show_glow=False, show_markers=False, smooth=False, line_width=2, fill_alpha=35, order=30, tags=("bar", "categorical")),
        GlassChartStyle("graphite_clean", "Graphite Clean", "Minimal monochrome style for dense workspaces.", "graphite_mono", default_mode="line", show_grid=True, show_glow=False, show_markers=False, smooth=True, line_width=2, fill_alpha=16, order=40, tags=("minimal", "mono")),
        GlassChartStyle("graphite_spark", "Graphite Spark", "Compact sparkline-friendly style.", "graphite_mono", default_mode="spark", show_grid=False, show_glow=False, show_markers=False, smooth=True, line_width=2, fill_alpha=0, order=50, tags=("spark", "compact")),
        GlassChartStyle("ops_health", "Ops Health", "Healthy-service monitoring style.", "ops_emerald", default_mode="line", show_grid=True, show_glow=True, show_markers=True, smooth=True, line_width=2, fill_alpha=20, order=60, tags=("ops", "health")),
        GlassChartStyle("ops_queue", "Ops Queue", "Queue depth and throughput monitor style.", "ops_emerald", default_mode="area", show_grid=True, show_glow=True, show_markers=False, smooth=False, line_width=2, fill_alpha=28, order=70, tags=("queue", "ops")),
        GlassChartStyle("warning_watch", "Warning Watch", "Amber watchlist style for degraded trends.", "signal_amber", default_mode="line", show_grid=True, show_glow=True, show_markers=True, smooth=False, line_width=3, fill_alpha=20, order=80, tags=("warning", "watch")),
        GlassChartStyle("warning_bars", "Warning Bars", "Amber bar style for warning counts.", "signal_amber", default_mode="bar", show_grid=True, show_glow=False, show_markers=False, smooth=False, line_width=2, fill_alpha=36, order=90, tags=("warning", "bar")),
        GlassChartStyle("incident_trace", "Incident Trace", "Critical incident escalation style.", "incident_crimson", default_mode="line", show_grid=True, show_glow=True, show_markers=True, smooth=False, line_width=3, fill_alpha=14, order=100, tags=("incident", "critical")),
        GlassChartStyle("incident_area", "Incident Area", "Critical area fill for peaks/spikes.", "incident_crimson", default_mode="area", show_grid=True, show_glow=True, show_markers=False, smooth=False, line_width=2, fill_alpha=26, order=110, tags=("incident", "area")),
        GlassChartStyle("teal_precision", "Teal Precision", "Cool precision line style for latency curves.", "cool_teal", default_mode="line", show_grid=True, show_glow=True, show_markers=False, smooth=True, line_width=2, fill_alpha=12, order=120, tags=("latency", "precision")),
        GlassChartStyle("teal_stream", "Teal Stream", "Streaming-oriented sparkline style.", "cool_teal", default_mode="spark", show_grid=False, show_glow=True, show_markers=False, smooth=True, line_width=2, fill_alpha=0, order=130, tags=("stream", "spark")),
        GlassChartStyle("violet_compare", "Violet Compare", "Muted comparison style for side-by-side series.", "violet_steel", default_mode="bar", show_grid=True, show_glow=False, show_markers=False, smooth=False, line_width=2, fill_alpha=32, order=140, tags=("comparison", "bar")),
        GlassChartStyle("violet_signal", "Violet Signal", "Muted signal style for mixed telemetry.", "violet_steel", default_mode="line", show_grid=True, show_glow=True, show_markers=True, smooth=True, line_width=2, fill_alpha=18, order=150, tags=("telemetry", "signal")),
        GlassChartStyle("sunrise_peak", "Sunrise Peak", "Warm peak detection style.", "sunrise_heat", default_mode="area", show_grid=True, show_glow=True, show_markers=True, smooth=False, line_width=3, fill_alpha=30, order=160, tags=("peak", "heat")),
        GlassChartStyle("sunrise_burst", "Sunrise Burst", "Warm burst style for transient spikes.", "sunrise_heat", default_mode="bar", show_grid=True, show_glow=True, show_markers=False, smooth=False, line_width=2, fill_alpha=38, order=170, tags=("burst", "spike")),
        GlassChartStyle("mint_fresh", "Mint Fresh", "Fresh mint style for positive growth.", "mint_cyan", default_mode="line", show_grid=True, show_glow=True, show_markers=False, smooth=True, line_width=2, fill_alpha=18, order=180, tags=("growth", "fresh")),
        GlassChartStyle("mint_focus", "Mint Focus", "Mint spark style for compact KPI strips.", "mint_cyan", default_mode="spark", show_grid=False, show_glow=False, show_markers=False, smooth=True, line_width=2, fill_alpha=0, order=190, tags=("kpi", "spark")),
        GlassChartStyle("obsidian_depth", "Obsidian Depth", "Blue-gray depth style for dense dark views.", "obsidian_blue", default_mode="line", show_grid=True, show_glow=True, show_markers=False, smooth=True, line_width=2, fill_alpha=22, order=200, tags=("dark", "depth")),
        GlassChartStyle("obsidian_monitor", "Obsidian Monitor", "Dark monitor style for multi-series dashboards.", "obsidian_blue", default_mode="area", show_grid=True, show_glow=True, show_markers=True, smooth=False, line_width=2, fill_alpha=30, order=210, tags=("monitor", "dark")),
    )
    for style in styles:
        try:
            register_chart_style(style, override=force)
        except ValueError:
            if force:
                raise


def register_builtin_chart_catalog(*, force: bool = False) -> tuple[GlassChartStyle, ...]:
    _register_defaults(force=force)
    return list_chart_styles()


def _clear_chart_catalog_for_tests() -> None:
    with _LOCK:
        _PALETTES.clear()
        _STYLES.clear()
if pg is not None:
    try:
        pg.setConfigOptions(antialias=True)
    except Exception:
        pass


def chart_ui_available() -> bool:
    return not _missing_enhanced_chart_dependencies()


def ensure_chart_ui_available() -> None:
    _require_enhanced_chart_dependencies()


def _css_rgba(value: str | QColor, *, alpha: int | float | None = None) -> str:
    color = QColor(value) if not isinstance(value, QColor) else QColor(value)
    if alpha is not None:
        if isinstance(alpha, float) and 0.0 <= alpha <= 1.0:
            color.setAlpha(max(0, min(255, int(round(alpha * 255.0)))))
        else:
            color.setAlpha(max(0, min(255, int(alpha))))
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})"


def resolve_chart_visual_tokens(
    style: GlassChartStyle,
    palette: GlassChartPalette,
    *,
    data_state: str = "ready",
) -> dict[str, str]:
    foundation = get_palette(DEFAULT_THEME_ID)
    colors = tuple(_qcolor(c) for c in palette.colors) or (
        _qcolor(foundation.text_primary),
        _qcolor(foundation.accent),
        _qcolor(foundation.text_muted),
        _qcolor(foundation.tab_text),
    )

    base = colors[0]
    primary = _mix_colors(colors[min(1, len(colors) - 1)], QColor("#ffffff"), 0.12)
    secondary = _mix_colors(colors[min(2, len(colors) - 1)], QColor("#dfe8ff"), 0.10)
    accent = _mix_colors(colors[-1], QColor("#ffffff"), 0.10)
    accent_alt = _mix_colors(primary, QColor("#89f4ff"), 0.28)
    text = _mix_colors(base, QColor("#ffffff"), 0.40)
    muted_text = _mix_colors(secondary, QColor("#c8d4e9"), 0.34)
    grid = _mix_colors(secondary, QColor("#253247"), 0.54)
    axis = _mix_colors(primary, QColor("#f4f8ff"), 0.28)

    state = str(data_state or "ready").strip().lower()
    if state == "error":
        signal = _qcolor("#ff8b93")
        chrome_top = _mix_colors(primary, QColor("#34141b"), 0.50)
        chrome_bottom = _mix_colors(accent, QColor("#12070a"), 0.76)
    elif state == "stale":
        signal = _qcolor("#f9c86c")
        chrome_top = _mix_colors(primary, QColor("#2f2412"), 0.42)
        chrome_bottom = _mix_colors(accent, QColor("#120d07"), 0.74)
    elif state == "loading":
        signal = _qcolor("#8cefff")
        chrome_top = _mix_colors(primary, QColor("#142336"), 0.40)
        chrome_bottom = _mix_colors(accent, QColor("#07111a"), 0.76)
    else:
        signal = _mix_colors(primary, QColor("#91f7ff"), 0.32)
        chrome_top = _mix_colors(primary, QColor("#141f31"), 0.42)
        chrome_bottom = _mix_colors(accent, QColor("#070d16"), 0.78)

    panel_top = _mix_colors(chrome_top, QColor("#ffffff"), 0.05)
    panel_bottom = _mix_colors(chrome_bottom, QColor("#000000"), 0.08)
    chrome_edge = _mix_colors(signal, QColor("#ffffff"), 0.16)
    subtle_border = _mix_colors(secondary, QColor("#ffffff"), 0.10)
    plot_frame = _mix_colors(signal, QColor("#dbe8ff"), 0.22)
    chip_bg = _mix_colors(chrome_top, signal, 0.12)
    chip_hover = _mix_colors(chrome_top, signal, 0.24)
    row_bg = _mix_colors(chrome_top, QColor("#ffffff"), 0.03)
    icon_bg = _mix_colors(signal, QColor("#ffffff"), 0.06)
    shadow = _mix_colors(signal, QColor("#08131f"), 0.56)
    success = _qcolor("#84efb5")
    warning = _qcolor("#f6cb6e")
    danger = _qcolor("#ff8b93")
    info = _qcolor("#8cefff")

    return {
        "primary": primary.name(),
        "secondary": secondary.name(),
        "accent": accent.name(),
        "accent_alt": accent_alt.name(),
        "text": text.name(),
        "muted_text": muted_text.name(),
        "grid": grid.name(),
        "axis": axis.name(),
        "signal": signal.name(),
        "chrome_top": chrome_top.name(),
        "chrome_bottom": chrome_bottom.name(),
        "panel_top": panel_top.name(),
        "panel_bottom": panel_bottom.name(),
        "chrome_edge": chrome_edge.name(),
        "subtle_border": subtle_border.name(),
        "plot_frame": plot_frame.name(),
        "chip_bg": chip_bg.name(),
        "chip_hover": chip_hover.name(),
        "row_bg": row_bg.name(),
        "icon_bg": icon_bg.name(),
        "shadow": shadow.name(),
        "success": success.name(),
        "warning": warning.name(),
        "danger": danger.name(),
        "info": info.name(),
    }


def _make_area_gradient_brush(
    theme: GlassChartTheme,
    *,
    color_index: int = 0,
    opacity_scale: float = 1.0,
) -> QBrush:
    base = QColor(theme.line_colors[color_index % len(theme.line_colors)])
    start_alpha = max(
        18,
        min(255, int(round(theme.style.fill_alpha * 5.2 * max(0.15, float(opacity_scale))))),
    )

    start = QColor(base)
    start.setAlpha(start_alpha)

    mid = QColor(_mix_colors(base, QColor("#ffffff"), 0.12))
    mid.setAlpha(max(10, int(start_alpha * 0.42)))

    end = QColor(base)
    end.setAlpha(max(0, int(start_alpha * 0.05)))

    gradient = QLinearGradient(0.0, 0.0, 0.0, 1.0)
    gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
    gradient.setColorAt(0.0, start)
    gradient.setColorAt(0.58, mid)
    gradient.setColorAt(1.0, end)
    return QBrush(gradient)


def _apply_plot_widget_polish(
    plot_widget: pg.PlotWidget,
    theme: GlassChartTheme,
    *,
    tokens: dict[str, str],
    title: str | None = None,
) -> None:
    _require_enhanced_chart_dependencies()

    plot_widget.setBackground(QColor(0, 0, 0, 0))
    plot_widget.setObjectName("GlassChartPlotWidget")

    plot_item = plot_widget.getPlotItem()
    plot_item.hideButtons()
    plot_item.setMenuEnabled(False)
    plot_item.showGrid(x=theme.style.show_grid, y=theme.style.show_grid, alpha=0.22)

    view_box = plot_item.getViewBox()
    view_box.setBackgroundColor(QColor(0, 0, 0, 0))
    view_box.setBorder(pg.mkPen(_qcolor(tokens["plot_frame"], alpha=96), width=1))
    view_box.setDefaultPadding(0.045)
    view_box.enableAutoRange()

    axis_font = QFont("Segoe UI", 9)
    axis_font.setWeight(QFont.Weight.DemiBold)
    axis_pen = pg.mkPen(_qcolor(tokens["grid"], alpha=118), width=1)
    text_pen = pg.mkPen(_qcolor(tokens["axis"], alpha=228), width=1)

    for axis_name in ("left", "bottom", "right", "top"):
        axis = plot_item.getAxis(axis_name)
        axis.setTextPen(text_pen)
        axis.setTickPen(axis_pen)
        axis.setPen(axis_pen)
        axis.setStyle(
            tickTextOffset=10,
            tickLength=-4,
            autoExpandTextSpace=True,
            showValues=axis_name in {"left", "bottom"},
        )
        try:
            axis.setTickFont(axis_font)
        except Exception:
            pass

    if title:
        safe_title = (
            str(title or "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        plot_item.setTitle(
            (
                f"<span style='color:{tokens['text']}; font-size:12pt; "
                f"font-weight:700; letter-spacing:0.4px;'>{safe_title}</span>"
            )
        )

    legend = getattr(plot_item, "legend", None)
    if legend is not None:
        try:
            legend.setBrush(pg.mkBrush(_qcolor(tokens["panel_bottom"], alpha=176)))
            legend.setPen(pg.mkPen(_qcolor(tokens["subtle_border"], alpha=132), width=1))
            legend.anchor((1, 0), (1, 0), offset=(-10, 10))
        except Exception:
            pass

        for sample, label in getattr(legend, "items", []):
            try:
                label.setAttr("color", tokens["text"])
                label.setAttr("size", "9pt")
            except Exception:
                pass


def build_chart_stylesheet(tokens: dict[str, str]) -> str:
    return f"""
    QWidget {{
        color: {tokens["text"]};
        background: transparent;
        font-family: "Segoe UI";
        selection-background-color: {_css_rgba(tokens["accent"], alpha=112)};
    }}

    QLabel#GlassChartTitle {{
        color: {tokens["text"]};
        font-size: 17px;
        font-weight: 800;
        letter-spacing: 0.25px;
        background: transparent;
    }}

    QLabel#GlassChartSubtitle {{
        color: {_css_rgba(tokens["muted_text"], alpha=228)};
        font-size: 11px;
        line-height: 1.2em;
        background: transparent;
    }}

    QLabel[chartRole="controls_hint"] {{
        color: {_css_rgba(tokens["muted_text"], alpha=208)};
        font-size: 10px;
        padding: 2px 0 6px 2px;
        background: transparent;
    }}

    QFrame#GlassChartControlRow {{
        border: 1px solid {_css_rgba(tokens["subtle_border"], alpha=92)};
        border-radius: 12px;
        background: {_css_rgba(tokens["row_bg"], alpha=108)};
    }}

    QLabel#GlassChartControlIcon {{
        border: 1px solid {_css_rgba(tokens["subtle_border"], alpha=108)};
        border-radius: 12px;
        background: {_css_rgba(tokens["icon_bg"], alpha=112)};
    }}

    QLabel[role="chart_control_label"] {{
        color: {_css_rgba(tokens["muted_text"], alpha=230)};
        font-size: 11px;
        font-weight: 700;
        padding-left: 2px;
    }}

    QLabel[chartMetric="true"] {{
        color: {tokens["text"]};
        background: {_css_rgba(tokens["panel_top"], alpha=116)};
        border: 1px solid {_css_rgba(tokens["subtle_border"], alpha=104)};
        border-radius: 14px;
        padding: 8px 10px;
        min-height: 50px;
    }}

    QPushButton {{
        border: 1px solid {_css_rgba(tokens["chrome_edge"], alpha=146)};
        border-radius: 999px;
        padding: 7px 12px;
        background-color: {_css_rgba(tokens["chip_bg"], alpha=160)};
        color: {tokens["text"]};
        font-weight: 700;
    }}

    QPushButton:hover {{
        background-color: {_css_rgba(tokens["chip_hover"], alpha=194)};
        border-color: {_css_rgba(tokens["accent"], alpha=186)};
    }}

    QPushButton:pressed {{
        background-color: {_css_rgba(tokens["chip_hover"], alpha=224)};
    }}

    QCollapsible > QToolButton {{
        font-weight: 800;
        color: {tokens["text"]};
        background-color: {_css_rgba(tokens["panel_top"], alpha=132)};
        border: 1px solid {_css_rgba(tokens["subtle_border"], alpha=112)};
        border-radius: 12px;
        padding: 8px 12px;
        text-align: left;
    }}

    QCollapsible > QToolButton:hover {{
        background-color: {_css_rgba(tokens["chip_hover"], alpha=156)};
        border-color: {_css_rgba(tokens["accent"], alpha=150)};
    }}

    QSlider::groove:horizontal {{
        height: 8px;
        border-radius: 4px;
        background: {_css_rgba(tokens["panel_bottom"], alpha=214)};
        border: 1px solid {_css_rgba(tokens["subtle_border"], alpha=104)};
    }}

    QSlider::sub-page:horizontal {{
        background: {_css_rgba(tokens["accent_alt"], alpha=212)};
        border-radius: 4px;
    }}

    QSlider::add-page:horizontal {{
        background: {_css_rgba(tokens["panel_top"], alpha=104)};
        border-radius: 4px;
    }}

    QSlider::handle:horizontal {{
        width: 16px;
        margin: -5px 0;
        border-radius: 8px;
        background: {_css_rgba(tokens["signal"], alpha=244)};
        border: 1px solid {_css_rgba(tokens["accent"], alpha=220)};
    }}

    PlotWidget#GlassChartPlotWidget {{
        background: transparent;
        border: 1px solid {_css_rgba(tokens["plot_frame"], alpha=94)};
        border-radius: 18px;
    }}
    """


def _mix_colors(left: QColor, right: QColor, ratio: float) -> QColor:
    blend = min(1.0, max(0.0, float(ratio)))
    inv = 1.0 - blend
    return QColor(
        int(left.red() * inv + right.red() * blend),
        int(left.green() * inv + right.green() * blend),
        int(left.blue() * inv + right.blue() * blend),
        int(left.alpha() * inv + right.alpha() * blend),
    )


def _qcolor(value: str | QColor, *, alpha: int | None = None) -> QColor:
    color = QColor(value) if not isinstance(value, QColor) else QColor(value)
    if alpha is not None:
        color.setAlpha(max(0, min(255, int(alpha))))
    return color


def build_chart_theme(
    *,
    style_id: str | None = None,
    palette_id: str | None = None,
    data_state: str = "ready",
    experience_mode: str = "default",
    visual_level: str = "standard",
) -> GlassChartTheme:
    style, palette = resolve_chart_contract(
        style_id=style_id,
        palette_id=palette_id,
        data_state=data_state,
        experience_mode=experience_mode,
        visual_level=visual_level,
    )
    base = tuple(_qcolor(c) for c in palette.colors)
    bright = _mix_colors(base[0], QColor("#ffffff"), 0.35)
    deep = _mix_colors(base[-1], QColor("#0b1020"), 0.50)
    bg_top = _mix_colors(bright, QColor("#101624"), 0.78)
    bg_bottom = _mix_colors(deep, QColor("#05070e"), 0.88)
    grid_major = _mix_colors(base[1], QColor("#dfe8ff"), 0.40)
    grid_major.setAlpha(80)
    grid_minor = QColor(grid_major)
    grid_minor.setAlpha(28)
    text_primary = _mix_colors(bright, QColor("#ffffff"), 0.55)
    text_muted = _mix_colors(grid_major, QColor("#ffffff"), 0.20)
    glow_color = _mix_colors(base[1], QColor("#ffffff"), 0.12)
    glow_color.setAlpha(112 if style.show_glow else 0)

    line_colors: list[QColor] = []
    bar_brushes: list[QBrush] = []
    for index, color in enumerate(base):
        tone = _mix_colors(color, QColor("#ffffff"), 0.10 if index % 2 == 0 else 0.03)
        tone.setAlpha(255)
        line_colors.append(tone)
        brush_color = QColor(tone)
        brush_color.setAlpha(min(220, max(50, style.fill_alpha * 5)))
        gradient = QLinearGradient(0.0, 0.0, 0.0, 1.0)
        start = QColor(brush_color)
        start.setAlpha(min(255, brush_color.alpha() + 35))
        end = QColor(brush_color)
        end.setAlpha(max(10, int(brush_color.alpha() * 0.25)))
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        gradient.setColorAt(0.0, start)
        gradient.setColorAt(1.0, end)
        bar_brushes.append(QBrush(gradient))

    return GlassChartTheme(
        style=style,
        palette=palette,
        background_top=bg_top,
        background_bottom=bg_bottom,
        grid_major=grid_major,
        grid_minor=grid_minor,
        text_primary=text_primary,
        text_muted=text_muted,
        line_colors=tuple(line_colors),
        glow_color=glow_color,
        bar_brushes=tuple(bar_brushes),
    )


def make_chart_pen(theme: GlassChartTheme, *, color_index: int = 0, width_scale: float = 1.0) -> QPen:
    _require_enhanced_chart_dependencies()
    color = theme.line_colors[color_index % len(theme.line_colors)]
    width = max(1, int(round(theme.style.line_width * max(0.35, float(width_scale)))))
    return pg.mkPen(color=color, width=width)


def make_chart_brush(theme: GlassChartTheme, *, color_index: int = 0, alpha: int | None = None) -> QBrush:
    _require_enhanced_chart_dependencies()
    color = QColor(theme.line_colors[color_index % len(theme.line_colors)])
    color.setAlpha(theme.style.fill_alpha * 4 if alpha is None else max(0, min(255, int(alpha))))
    return pg.mkBrush(color)


def make_chart_icon(theme: GlassChartTheme, *, mode: str | None = None) -> object:
    _require_enhanced_chart_dependencies()
    chart_mode = str(mode or theme.style.default_mode).strip().lower()
    icon_name = {
        "line": "fa6s.chart-line",
        "area": "fa6s.mountain-sun",
        "bar": "fa6s.chart-column",
        "spark": "fa6s.wave-square",
    }.get(chart_mode, "fa6s.chart-line")
    return qta.icon(icon_name, color=theme.text_primary, color_active=theme.line_colors[1 % len(theme.line_colors)])


def configure_plot_widget(plot_widget: pg.PlotWidget, theme: GlassChartTheme, *, title: str | None = None) -> pg.PlotItem:
    _require_enhanced_chart_dependencies()
    plot_widget.setBackground(QColor(0, 0, 0, 0))
    plot_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    plot_item = plot_widget.getPlotItem()
    plot_item.showGrid(x=theme.style.show_grid, y=theme.style.show_grid, alpha=0.26)
    plot_item.hideButtons()
    plot_item.setMenuEnabled(False)
    plot_item.getViewBox().setMouseEnabled(x=False, y=False)
    plot_item.getViewBox().setBorder(pg.mkPen(theme.grid_minor, width=1))
    plot_item.getViewBox().setBackgroundColor(QColor(0, 0, 0, 0))
    plot_item.getViewBox().enableAutoRange()

    axis_font = QFont()
    axis_font.setPointSize(9)
    axis_font.setWeight(QFont.Weight.Medium)
    axis_pen = pg.mkPen(theme.grid_major, width=1)
    for name in ("left", "bottom", "right", "top"):
        axis = plot_item.getAxis(name)
        axis.setTextPen(theme.text_muted)
        axis.setTickPen(axis_pen)
        axis.setPen(axis_pen)
        axis.setStyle(tickTextOffset=10, tickLength=-4, autoExpandTextSpace=True)
        try:
            axis.setTickFont(axis_font)
        except Exception:
            pass
    if title:
        plot_item.setTitle(title, color=theme.text_primary.name(), size="12pt")
    return plot_item


def _make_glow_curve(x: np.ndarray, y: np.ndarray, theme: GlassChartTheme, color_index: int, width_scale: float) -> pg.PlotCurveItem:
    _require_enhanced_chart_dependencies()
    glow = QColor(theme.glow_color)
    glow = _mix_colors(glow, theme.line_colors[color_index % len(theme.line_colors)], 0.45)
    glow.setAlpha(max(0, theme.glow_color.alpha()))
    width = max(4, int(round(theme.style.line_width * max(0.35, float(width_scale)) * 2.6)))
    curve = pg.PlotCurveItem(x, y, pen=pg.mkPen(glow, width=width))
    curve.setZValue(1)
    return curve


def plot_series(
    plot_widget: pg.PlotWidget,
    series: GlassChartSeries | Sequence[GlassChartSeries],
    *,
    style_id: str | None = None,
    palette_id: str | None = None,
    data_state: str = "ready",
    experience_mode: str = "default",
    visual_level: str = "standard",
    title: str | None = None,
) -> GlassChartTheme:
    _require_enhanced_chart_dependencies()
    theme = build_chart_theme(
        style_id=style_id,
        palette_id=palette_id,
        data_state=data_state,
        experience_mode=experience_mode,
        visual_level=visual_level,
    )
    configure_plot_widget(plot_widget, theme, title=title)
    plot_widget.clear()

    normalized_series = series if isinstance(series, Sequence) and not isinstance(series, GlassChartSeries) else [series]  # type: ignore[list-item]

    baseline_cache: dict[int, pg.PlotCurveItem] = {}
    for raw in normalized_series:
        item = raw.normalized() if isinstance(raw, GlassChartSeries) else GlassChartSeries(**raw).normalized()  # type: ignore[arg-type]
        if not item.visible:
            continue
        x = np.asarray(item.x, dtype=float)
        y = np.asarray(item.y, dtype=float)
        mode = item.mode or theme.style.default_mode
        color_index = item.color_index % len(theme.line_colors)

        if mode == "bar":
            width = 0.72 if x.size < 2 else max(0.15, float(np.min(np.diff(np.sort(x)))) * 0.72)
            bars = pg.BarGraphItem(
                x=x,
                height=y,
                width=width,
                brush=theme.bar_brushes[color_index % len(theme.bar_brushes)],
                pen=make_chart_pen(theme, color_index=color_index, width_scale=max(0.8, item.width_scale)),
            )
            bars.setZValue(2)
            plot_widget.addItem(bars)
            continue

        if theme.style.show_glow and mode in {"line", "area", "spark"}:
            plot_widget.addItem(_make_glow_curve(x, y, theme, color_index, item.width_scale))

        symbol = item.symbol
        if symbol is None and theme.style.show_markers and mode != "spark":
            symbol = "o"

        data_item = pg.PlotDataItem(
            x=x,
            y=y,
            pen=make_chart_pen(theme, color_index=color_index, width_scale=item.width_scale),
            symbol=symbol,
            symbolSize=7 if symbol else None,
            symbolBrush=make_chart_brush(theme, color_index=color_index, alpha=220) if symbol else None,
            symbolPen=make_chart_pen(theme, color_index=color_index, width_scale=1.0) if symbol else None,
            antialias=True,
            connect="all",
            skipFiniteCheck=True,
            name=item.name,
        )
        data_item.setZValue(3)
        plot_widget.addItem(data_item)

        if mode == "area" or item.fill_to_zero:
            baseline = baseline_cache.get(color_index)
            if baseline is None:
                baseline = pg.PlotCurveItem(x, np.zeros_like(y), pen=pg.mkPen(QColor(0, 0, 0, 0)))
                baseline_cache[color_index] = baseline
                plot_widget.addItem(baseline)
            fill = pg.FillBetweenItem(data_item, baseline, brush=make_chart_brush(theme, color_index=color_index))
            fill.setZValue(2)
            plot_widget.addItem(fill)

    return theme


class _GlassPlotFrame(QFrame):
    def __init__(self, theme: GlassChartTheme, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme
        self.setObjectName("GlassPlotFrame")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def set_theme(self, theme: GlassChartTheme) -> None:
        self._theme = theme
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = self.rect().adjusted(1, 1, -1, -1)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, self._theme.background_top)
        gradient.setColorAt(1.0, self._theme.background_bottom)

        painter.setPen(QPen(_mix_colors(self._theme.grid_major, QColor("#ffffff"), 0.18), 1))
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(rect, 20, 20)
        super().paintEvent(event)


class GlassChartCard(QWidget):
    themeChanged = Signal(str)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "Telemetry Overview",
        subtitle: str = "Adaptive pyqtgraph showcase powered by the chart contract.",
        style_id: str | None = None,
        palette_id: str | None = None,
        data_state: str = "ready",
        experience_mode: str = "dashboard",
        visual_level: str = "showcase",
        series: Sequence[GlassChartSeries] | None = None,
    ) -> None:
        _require_enhanced_chart_dependencies()
        super().__init__(parent)
        self._title = title
        self._subtitle = subtitle
        self._state = data_state
        self._mode = experience_mode
        self._level = visual_level
        self._style_id = style_id
        self._palette_id = palette_id
        self._series = tuple((series or sample_series()))
        self._theme = build_chart_theme(
            style_id=style_id,
            palette_id=palette_id,
            data_state=data_state,
            experience_mode=experience_mode,
            visual_level=visual_level,
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._surface = _GlassPlotFrame(self._theme, self)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setOffset(0, 14)
        shadow.setColor(_qcolor(self._theme.glow_color, alpha=112 if self._theme.style.show_glow else 52))
        self._surface.setGraphicsEffect(shadow)
        outer.addWidget(self._surface)

        layout = QVBoxLayout(self._surface)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.setSpacing(12)
        layout.addLayout(header)

        self._icon_label = QLabel(self)
        self._icon_label.setFixedSize(36, 36)
        self._icon_label.setScaledContents(True)
        header.addWidget(self._icon_label, 0, Qt.AlignmentFlag.AlignTop)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        header.addLayout(title_box, 1)

        self._title_label = QLabel(title, self)
        self._title_label.setObjectName("GlassChartTitle")
        title_box.addWidget(self._title_label)

        self._subtitle_label = QLabel(subtitle, self)
        self._subtitle_label.setWordWrap(True)
        self._subtitle_label.setObjectName("GlassChartSubtitle")
        title_box.addWidget(self._subtitle_label)

        self._status_chip = QPushButton(self)
        self._status_chip.setFlat(True)
        self._status_chip.setCursor(Qt.CursorShape.PointingHandCursor)
        self._status_chip.clicked.connect(self._cycle_state)
        header.addWidget(self._status_chip, 0, Qt.AlignmentFlag.AlignTop)

        metrics = QGridLayout()
        metrics.setHorizontalSpacing(12)
        metrics.setVerticalSpacing(6)
        layout.addLayout(metrics)
        self._metric_labels: dict[str, QLabel] = {}
        for col, key in enumerate(("Peak", "Latest", "Drift")):
            label = QLabel(self)
            label.setProperty("chartMetric", True)
            metrics.addWidget(label, 0, col)
            self._metric_labels[key] = label

        self.plot_widget = pg.PlotWidget(self)
        self.plot_widget.setObjectName("GlassChartPlotWidget")
        self.plot_widget.setMinimumHeight(260)
        layout.addWidget(self.plot_widget, 1)

        self.controls = QCollapsible("Advanced polish", self)
        self.controls.expand(animate=False)
        layout.addWidget(self.controls)

        self._controls_hint = QLabel(
            "Glow, line, fill, legend and posture tuning. Premium, but calm enough for long sessions.",
            self,
        )
        self._controls_hint.setWordWrap(True)
        self._controls_hint.setProperty("chartRole", "controls_hint")
        self.controls.addWidget(self._controls_hint)

        self._glow_slider = QLabeledDoubleSlider(Qt.Orientation.Horizontal, self)
        self._glow_slider.setRange(0.15, 2.6)
        self._glow_slider.setValue(1.0)
        self._glow_slider.setDecimals(2)
        self._glow_slider.setSingleStep(0.05)
        self._glow_slider.fvalueChanged.connect(self._refresh_plot)
        self.controls.addWidget(
            self._build_control_row(
                "Glow width",
                self._glow_slider,
                "fa6s.wand-magic-sparkles",
            )
        )

        self._line_slider = QLabeledDoubleSlider(Qt.Orientation.Horizontal, self)
        self._line_slider.setRange(0.55, 3.4)
        self._line_slider.setValue(1.0)
        self._line_slider.setDecimals(2)
        self._line_slider.setSingleStep(0.05)
        self._line_slider.fvalueChanged.connect(self._refresh_plot)
        self.controls.addWidget(
            self._build_control_row(
                "Line punch",
                self._line_slider,
                "fa6s.sliders",
            )
        )

        self._fill_slider = QLabeledDoubleSlider(Qt.Orientation.Horizontal, self)
        self._fill_slider.setRange(0.10, 1.85)
        self._fill_slider.setValue(1.0)
        self._fill_slider.setDecimals(2)
        self._fill_slider.setSingleStep(0.05)
        self._fill_slider.fvalueChanged.connect(self._refresh_plot)
        self.controls.addWidget(
            self._build_control_row(
                "Fill density",
                self._fill_slider,
                "fa6s.layer-group",
            )
        )

        self._apply_theme()
        self._refresh_plot()

    def _build_control_row(self, label: str, widget: QWidget, icon_name: str) -> QWidget:
        row = QFrame(self)
        row.setObjectName("GlassChartControlRow")
        row.setFrameShape(QFrame.Shape.NoFrame)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        icon = QLabel(row)
        icon.setObjectName("GlassChartControlIcon")
        icon.setFixedSize(24, 24)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            icon.setPixmap(qta.icon(icon_name, color=self._theme.text_muted).pixmap(14, 14))
        except Exception:
            icon.clear()
        layout.addWidget(icon)

        text = QLabel(label, row)
        text.setMinimumWidth(104)
        text.setProperty("role", "chart_control_label")
        layout.addWidget(text)

        widget.setProperty("chartControl", label.lower().replace(" ", "_"))
        layout.addWidget(widget, 1)
        return row

    def _cycle_state(self) -> None:
        states = ("ready", "stale", "error", "loading")
        current_index = states.index(self._state) if self._state in states else 0
        self._state = states[(current_index + 1) % len(states)]
        self._theme = build_chart_theme(
            style_id=self._style_id,
            palette_id=self._palette_id,
            data_state=self._state,
            experience_mode=self._mode,
            visual_level=self._level,
        )
        self._apply_theme()
        self._refresh_plot()
        self.themeChanged.emit(self._theme.style.style_id)

    def _apply_theme(self) -> None:
        tokens = resolve_chart_visual_tokens(
            self._theme.style,
            self._theme.palette,
            data_state=self._state,
        )

        self._surface.set_theme(self._theme)
        effect = self._surface.graphicsEffect()
        if isinstance(effect, QGraphicsDropShadowEffect):
            effect.setBlurRadius(38 if self._theme.style.show_glow else 26)
            effect.setOffset(0, 14)
            effect.setColor(_qcolor(tokens["shadow"], alpha=124 if self._theme.style.show_glow else 64))

        try:
            self._icon_label.setPixmap(make_chart_icon(self._theme).pixmap(28, 28))
        except Exception:
            self._icon_label.clear()

        chip_icon = qta.icon(
            {
                "ready": "fa6s.circle-check",
                "stale": "fa6s.clock",
                "loading": "fa6s.spinner",
                "error": "fa6s.triangle-exclamation",
                "empty": "fa6s.box-open",
            }.get(self._state, "fa6s.circle-info"),
            color=_qcolor(tokens["signal"]),
        )
        self._status_chip.setIcon(chip_icon)
        self._status_chip.setText(f" {self._state.title()} Â· {self._theme.style.default_mode.upper()}")

        self._title_label.setText(self._title)
        self._subtitle_label.setText(self._subtitle)

        for label in self._metric_labels.values():
            label.setProperty("chartMetric", True)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)



    def _refresh_plot(self) -> None:
        tuned: list[GlassChartSeries] = []
        line_scale = float(self._line_slider.value()) if hasattr(self, "_line_slider") else 1.0
        glow_scale = float(self._glow_slider.value()) if hasattr(self, "_glow_slider") else 1.0
        fill_scale = float(self._fill_slider.value()) if hasattr(self, "_fill_slider") else 1.0

        for index, series in enumerate(self._series):
            item = series.normalized()
            mode = item.mode or self._theme.style.default_mode
            fill = item.fill_to_zero or mode == "area"
            tuned.append(
                GlassChartSeries(
                    name=item.name,
                    x=item.x,
                    y=item.y,
                    mode=mode,
                    color_index=index,
                    width_scale=item.width_scale * line_scale * (1.15 if mode == "spark" else 1.0),
                    visible=item.visible,
                    fill_to_zero=fill,
                    symbol=item.symbol,
                    metadata=item.metadata,
                )
            )

        theme = plot_series(
            self.plot_widget,
            tuned,
            style_id=self._theme.style.style_id,
            palette_id=self._theme.palette.palette_id,
            data_state=self._state,
            experience_mode=self._mode,
            visual_level=self._level,
            title=self._title,
        )

        tokens = resolve_chart_visual_tokens(
            theme.style,
            theme.palette,
            data_state=self._state,
        )
        _apply_plot_widget_polish(
            self.plot_widget,
            theme,
            tokens=tokens,
            title=self._title,
        )

        fill_index = 0
        for item in self.plot_widget.items():
            if isinstance(item, pg.PlotCurveItem) and item.zValue() == 1 and theme.style.show_glow:
                pen = item.opts.get("pen")
                if isinstance(pen, QPen):
                    pen.setWidth(max(1, int(round(pen.width() * glow_scale))))
                    item.setPen(pen)
            elif isinstance(item, pg.FillBetweenItem):
                item.setBrush(
                    _make_area_gradient_brush(
                        theme,
                        color_index=fill_index,
                        opacity_scale=fill_scale,
                    )
                )
                fill_index += 1
            elif isinstance(item, pg.PlotDataItem) and theme.style.show_markers:
                try:
                    item.setSymbolSize(max(6, int(round(7 * max(0.85, line_scale)))))
                except Exception:
                    pass

        self._theme = theme
        self._surface.set_theme(theme)
        self._apply_theme()
        self._update_metrics(tuned)

    def _update_metrics(self, series: Sequence[GlassChartSeries]) -> None:
        if not series:
            return

        primary = series[0].normalized()
        y = np.asarray(primary.y, dtype=float)
        latest = float(y[-1])
        peak = float(np.max(y))
        drift = latest - float(y[0])
        avg = float(np.mean(y))

        tokens = resolve_chart_visual_tokens(
            self._theme.style,
            self._theme.palette,
            data_state=self._state,
        )
        drift_color = tokens["success"] if drift >= 0 else tokens["danger"]
        drift_sign = "+" if drift >= 0 else ""

        self._metric_labels["Peak"].setText(
            (
                f"<div style='font-size:10px; font-weight:700; color:{tokens['muted_text']};'>PEAK</div>"
                f"<div style='font-size:16px; font-weight:800; color:{tokens['accent']};'>{peak:,.2f}</div>"
                f"<div style='font-size:10px; color:{tokens['muted_text']};'>max observed</div>"
            )
        )
        self._metric_labels["Latest"].setText(
            (
                f"<div style='font-size:10px; font-weight:700; color:{tokens['muted_text']};'>LATEST</div>"
                f"<div style='font-size:16px; font-weight:800; color:{tokens['signal']};'>{latest:,.2f}</div>"
                f"<div style='font-size:10px; color:{tokens['muted_text']};'>avg {avg:,.2f}</div>"
            )
        )
        self._metric_labels["Drift"].setText(
            (
                f"<div style='font-size:10px; font-weight:700; color:{tokens['muted_text']};'>DRIFT</div>"
                f"<div style='font-size:16px; font-weight:800; color:{drift_color};'>{drift_sign}{drift:,.2f}</div>"
                f"<div style='font-size:10px; color:{tokens['muted_text']};'>from first sample</div>"
            )
        )

    def set_series(self, series: Sequence[GlassChartSeries]) -> None:
        self._series = tuple(series)
        self._refresh_plot()


def sample_series() -> tuple[GlassChartSeries, ...]:
    x = tuple(range(12))
    base = [28.0, 35.0, 33.0, 42.0, 48.0, 44.0, 53.0, 57.0, 55.0, 62.0, 60.0, 68.0]
    compare = [18.0, 21.0, 25.0, 26.0, 29.0, 31.0, 35.0, 38.0, 40.0, 43.0, 45.0, 47.0]
    latency = [12.0, 11.0, 14.0, 10.0, 9.0, 13.0, 12.0, 10.0, 11.0, 9.0, 8.0, 10.0]
    return (
        GlassChartSeries(name="Requests", x=x, y=tuple(base), mode="area", fill_to_zero=True),
        GlassChartSeries(name="Conversions", x=x, y=tuple(compare), mode="line", symbol="o"),
        GlassChartSeries(name="Latency", x=x, y=tuple(latency), mode="spark"),
    )


def demo_widget(parent: QWidget | None = None) -> GlassChartCard:
    return GlassChartCard(parent=parent, series=sample_series())
def build_chart_card(
    *,
    title: str = "Telemetry Overview",
    subtitle: str = "Registry-driven glass chart surface.",
    style_id: str | None = None,
    palette_id: str | None = None,
    data_state: str = "ready",
    experience_mode: str = "dashboard",
    visual_level: str = "showcase",
    values: Sequence[float] | None = None,
    x_values: Sequence[float] | None = None,
    mode: str | None = None,
    series: Sequence[GlassChartSeries] | None = None,
    parent: QWidget | None = None,
) -> GlassChartCard:
    ensure_chart_ui_available()

    widget = GlassChartCard(
        parent=parent,
        title=title,
        subtitle=subtitle,
        style_id=style_id,
        palette_id=palette_id,
        data_state=data_state,
        experience_mode=experience_mode,
        visual_level=visual_level,
        series=series or sample_series(),
    )

    if series:
        widget.set_series(tuple(item.normalized() for item in series))
    elif values is not None:
        y_payload = tuple(float(value) for value in values)
        if x_values is not None:
            x_payload = tuple(float(value) for value in x_values)
        else:
            x_payload = tuple(float(index) for index in range(len(y_payload)))
        widget.set_series(
            (
                GlassChartSeries(
                    name="Primary",
                    x=x_payload,
                    y=y_payload,
                    mode=mode,
                    color_index=0,
                    fill_to_zero=(mode == "area"),
                ).normalized(),
            )
        )

    return widget


def _demo() -> int:
    _require_enhanced_chart_dependencies()
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    foundation = get_palette(DEFAULT_THEME_ID)
    qta.set_defaults(color=QColor(foundation.text_primary), color_disabled=QColor(foundation.text_muted))
    widget = demo_widget()
    widget.resize(940, 640)
    widget.setWindowTitle("Glass Charts Deluxe")
    widget.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(_demo())
