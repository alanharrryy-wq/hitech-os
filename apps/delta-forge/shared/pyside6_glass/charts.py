from __future__ import annotations

from dataclasses import dataclass
from threading import RLock


@dataclass(frozen=True, slots=True)
class GlassChartPalette:
    palette_id: str
    title: str
    description: str
    colors: tuple[str, ...]
    order: int = 100
    tags: tuple[str, ...] = ()

    def normalized(self) -> GlassChartPalette:
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

    def normalized(self) -> GlassChartStyle:
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


_PALETTES: dict[str, GlassChartPalette] = {}
_STYLES: dict[str, GlassChartStyle] = {}
_LOCK = RLock()


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
