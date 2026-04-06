from __future__ import annotations

from collections import deque
import math
import time
from dataclasses import dataclass
from typing import Any, Optional

from PySide6.QtCore import QEvent, QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QRadialGradient
from PySide6.QtWidgets import QWidget

from ..common.color import mix_hex
from ..common.constants import DEFAULT_THEME_ID
from ..common.helpers import clean_text
from ..themes.catalog import normalize_theme, resolve_theme


@dataclass(frozen=True, slots=True)
class _GlassPalette:
    canvas_top: QColor
    canvas_bottom: QColor
    wash: QColor
    border: QColor
    line: QColor
    sheen: QColor
    orb_a: QColor
    orb_b: QColor
    orb_c: QColor
    sparkle: QColor
    star_soft: QColor
    star_bright: QColor


def _qcolor_from_value(value: Any, alpha: float = 1.0) -> QColor:
    cleaned = clean_text(str(value or ""))
    color = QColor(cleaned or "#808080")
    if not color.isValid():
        color = QColor("#808080")
    color.setAlphaF(max(0.0, min(1.0, float(alpha))))
    return color


def _is_silver_theme_id(theme_id: str) -> bool:
    lowered = clean_text(theme_id).lower()
    return any(tag in lowered for tag in ("silver", "frost", "argent", "mercury"))


def _glass_palette(theme_id: str, variant: str = "selector") -> _GlassPalette:
    render = resolve_theme(theme_id)
    t = render.tokens
    dark = render.is_dark
    silver_theme = _is_silver_theme_id(theme_id)
    selector_variant = clean_text(variant).lower() != "progress"

    if silver_theme:
        canvas_top = _qcolor_from_value("#04070d", 1.0)
        canvas_bottom = _qcolor_from_value("#0f1824", 1.0)
        wash = _qcolor_from_value("#eef6ff", 0.016 if selector_variant else 0.020)
        border = _qcolor_from_value("#e8f6ff", 0.16 if selector_variant else 0.13)
        line = _qcolor_from_value("#8cefff", 0.05)
        sheen = _qcolor_from_value("#ffffff", 0.08)
        orb_a = _qcolor_from_value("#eff7ff", 0.18 if selector_variant else 0.14)
        orb_b = _qcolor_from_value("#8cefff", 0.15 if selector_variant else 0.12)
        orb_c = _qcolor_from_value("#d7e1ff", 0.10 if selector_variant else 0.08)
        sparkle = _qcolor_from_value("#ffffff", 0.88)
        star_soft = _qcolor_from_value("#eef6ff", 0.18)
        star_bright = _qcolor_from_value("#ffffff", 0.62)
        return _GlassPalette(
            canvas_top=canvas_top,
            canvas_bottom=canvas_bottom,
            wash=wash,
            border=border,
            line=line,
            sheen=sheen,
            orb_a=orb_a,
            orb_b=orb_b,
            orb_c=orb_c,
            sparkle=sparkle,
            star_soft=star_soft,
            star_bright=star_bright,
        )

    canvas_top = _qcolor_from_value(mix_hex(t["canvas_bg"], t["header_fill"], 0.18 if dark else 0.05), 1.0)
    canvas_bottom = _qcolor_from_value(mix_hex(t["canvas_bg"], t["legend_fill"], 0.32 if dark else 0.10), 1.0)
    wash = _qcolor_from_value(mix_hex(t["header_fill"], t["legend_fill"], 0.50 if dark else 0.20), 0.22 if dark else 0.58)
    border = _qcolor_from_value(mix_hex(t["focus"], t["legend_stroke"], 0.26 if dark else 0.12), 0.20 if dark else 0.30)
    line = _qcolor_from_value(t["header_stroke"], 0.10 if dark else 0.18)
    sheen = _qcolor_from_value("#ffffff", 0.09 if dark else 0.16)
    orb_a = _qcolor_from_value(t["halo_a"], 0.22 if selector_variant and dark else 0.16 if selector_variant else 0.18 if dark else 0.12)
    orb_b = _qcolor_from_value(t["halo_b"], 0.16 if selector_variant and dark else 0.11 if selector_variant else 0.14 if dark else 0.10)
    orb_c = _qcolor_from_value(t["focus"], 0.14 if dark else 0.09)
    sparkle = _qcolor_from_value("#ffffff", 0.34 if dark else 0.42)
    star_soft = _qcolor_from_value("#ffffff", 0.12 if dark else 0.18)
    star_bright = _qcolor_from_value("#ffffff", 0.28 if dark else 0.34)
    return _GlassPalette(
        canvas_top=canvas_top,
        canvas_bottom=canvas_bottom,
        wash=wash,
        border=border,
        line=line,
        sheen=sheen,
        orb_a=orb_a,
        orb_b=orb_b,
        orb_c=orb_c,
        sparkle=sparkle,
        star_soft=star_soft,
        star_bright=star_bright,
    )


class FrostedGlassBackdrop(QWidget):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        theme_id: str = DEFAULT_THEME_ID,
        variant: str = "selector",
        motion_enabled: bool = True,
    ) -> None:
        super().__init__(parent)
        self._variant = clean_text(variant).lower() or "selector"
        self._theme_id = normalize_theme(theme_id)
        self._palette = _glass_palette(self._theme_id, self._variant)
        self._motion_enabled = bool(motion_enabled)
        self._motion_epoch = time.monotonic()
        self._motion_timer = QTimer(self)
        self._motion_timer.setInterval(24)
        self._motion_timer.timeout.connect(self._advance_motion)
        self._star_seed_cache: dict[tuple[float, int], list[tuple[float, ...]]] = {}
        self._star_runtime_cache: dict[tuple[float, int, float, float, float, float, float, float], list[tuple[float, ...]]] = {}
        self._lens_spec_cache: dict[str, list[tuple[float, ...]]] = {}
        self._static_cache_key: tuple[str, str, int, int] | None = None
        self._static_cache: QPixmap | None = None
        self._star_layer_cache: dict[tuple[float, int, float, float, float, float, float, float, float, float], list[tuple[float, ...]]] = {}
        self._lens_seed_cache: dict[str, list[tuple[float, ...]]] = {}
        self._perf_paint_samples = deque(maxlen=90)
        self._perf_paint_stamps = deque(maxlen=180)
        self._clip_cache_key: tuple[int, int] | None = None
        self._clip_path_cache: QPainterPath | None = None
        self._last_motion_interval_ms: int | None = None
        self.setObjectName("FrostedGlassBackdrop")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(False)
        self._sync_motion_timer()

    def set_motion_enabled(self, enabled: bool) -> None:
        self._motion_enabled = bool(enabled)
        self._sync_motion_timer()

    def _advance_motion(self) -> None:
        if not self.isVisible():
            return
        self._sync_motion_timer()
        self.update()

    def _motion_time(self) -> float:
        return max(0.0, time.monotonic() - self._motion_epoch)

    def _invalidate_render_cache(self) -> None:
        self._static_cache_key = None
        self._static_cache = None

    def _invalidate_clip_cache(self) -> None:
        self._clip_cache_key = None
        self._clip_path_cache = None

    def _resolve_motion_interval_ms(self) -> int:
        window = self.window()
        is_active = True
        if window is not None:
            try:
                is_active = bool(window.isActiveWindow())
            except RuntimeError:
                is_active = True
        return 24 if is_active else 48

    def _sync_motion_timer(self) -> None:
        should_run = self._motion_enabled and _is_silver_theme_id(self._theme_id) and self.isVisible()
        if not should_run:
            self._last_motion_interval_ms = None
            if self._motion_timer.isActive():
                self._motion_timer.stop()
            return

        interval_ms = self._resolve_motion_interval_ms()
        if self._last_motion_interval_ms != interval_ms:
            self._motion_timer.setInterval(interval_ms)
            self._last_motion_interval_ms = interval_ms

        if not self._motion_timer.isActive():
            self._motion_timer.start()

    def showEvent(self, event) -> None:  # type: ignore[override]
        self._sync_motion_timer()
        super().showEvent(event)

    def hideEvent(self, event) -> None:  # type: ignore[override]
        if self._motion_timer.isActive():
            self._motion_timer.stop()
        super().hideEvent(event)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        self._invalidate_render_cache()
        self._invalidate_clip_cache()
        super().resizeEvent(event)

    def changeEvent(self, event) -> None:  # type: ignore[override]
        event_type = event.type()
        if event_type in {QEvent.Type.ActivationChange, QEvent.Type.WindowStateChange}:
            self._sync_motion_timer()
        super().changeEvent(event)

    def apply_theme(self, theme_id: str) -> None:
        resolved = normalize_theme(theme_id or DEFAULT_THEME_ID)
        if resolved == self._theme_id:
            return
        self._theme_id = resolved
        self._palette = _glass_palette(self._theme_id, self._variant)
        self._invalidate_render_cache()
        self._sync_motion_timer()
        self.update()

    def _record_paint_metrics(self, started_at: float) -> None:
        finished_at = time.perf_counter()
        elapsed_ms = max(0.0, (finished_at - started_at) * 1000.0)
        self._perf_paint_samples.append(elapsed_ms)
        self._perf_paint_stamps.append(finished_at)

    def performance_snapshot(self) -> dict[str, float | bool]:
        now = time.perf_counter()
        recent = [stamp for stamp in self._perf_paint_stamps if (now - stamp) <= 1.0]
        fps = float(len(recent))
        paint_ms = 0.0
        if self._perf_paint_samples:
            paint_ms = sum(self._perf_paint_samples) / float(len(self._perf_paint_samples))
        motion_interval_ms = float(self._motion_timer.interval()) if self._motion_timer.isActive() else 0.0
        return {
            "fps": fps,
            "paint_ms": paint_ms,
            "motion_interval_ms": motion_interval_ms,
            "active": bool(self.isVisible() and self._motion_timer.isActive()),
        }

    def _orb_specs(self, rect: QRectF, *, motion_phase: float = 0.0) -> list[tuple[QColor, float, float, float]]:
        if self._variant == "progress":
            base_specs = [
                (self._palette.orb_a, 0.76, 0.18, 0.46, 0.10, 0.08),
                (self._palette.orb_b, 0.16, 0.82, 0.30, 0.12, 0.10),
                (self._palette.orb_c, 0.50, 0.58, 0.24, 0.14, 0.09),
            ]
        else:
            base_specs = [
                (self._palette.orb_a, 0.58, 0.16, 0.54, 0.08, 0.06),
                (self._palette.orb_b, 0.18, 0.72, 0.34, 0.12, 0.09),
                (self._palette.orb_c, 0.90, 0.62, 0.38, 0.10, 0.07),
            ]
        specs: list[tuple[QColor, float, float, float]] = []
        for index, (color, x_factor, y_factor, radius_factor, x_speed, y_speed) in enumerate(base_specs, start=1):
            x_wobble = math.sin((motion_phase * x_speed) + (index * 0.9)) * 0.026
            y_wobble = math.cos((motion_phase * y_speed) + (index * 1.3)) * 0.033
            radius_wobble = 1.0 + (0.055 * math.sin((motion_phase * 0.08) + (index * 1.7)))
            specs.append(
                (
                    color,
                    rect.width() * (x_factor + x_wobble),
                    rect.height() * (y_factor + y_wobble),
                    rect.width() * radius_factor * radius_wobble,
                )
            )
        return specs

    def _noise01(self, seed: float) -> float:
        value = math.sin((seed * 12.9898) + 78.233) * 43758.5453123
        return value - math.floor(value)

    def _flash_interval_seconds(self, event_index: int) -> float:
        # random-blink-patch: 5s to 10s interval per burst, seeded per runtime.
        seed_base = float(getattr(self, "_flash_random_seed", 0.0))
        seed = 7000.0 + seed_base + (event_index * 1.731)
        return 5.0 + (self._noise01(seed) * 5.0)

    def _ensure_flash_events(self, until_time: float) -> None:
        if not hasattr(self, "_flash_events"):
            self._flash_events: list[dict[str, float]] = []
            self._flash_schedule_cursor = 0.0
            self._flash_schedule_index = 0
            self._flash_random_seed = time.perf_counter() * 1000.0
        while self._flash_schedule_cursor <= until_time:
            event_index = int(self._flash_schedule_index)
            self._flash_schedule_cursor += self._flash_interval_seconds(event_index)

            seed_base = float(getattr(self, "_flash_random_seed", 0.0))
            burst_seed = 8000.0 + seed_base + (event_index * 3.17)
            burst_count = 1 + int(self._noise01(burst_seed) * 3.0)
            burst_count = max(1, min(3, burst_count))
            burst_spacing = 0.18 + (self._noise01(burst_seed + 0.77) * 0.82)

            for burst_index in range(burst_count):
                seed = 9100.0 + seed_base + (event_index * 13.0) + (burst_index * 5.7)
                start_offset = 0.0
                if burst_index > 0:
                    start_offset = (burst_index * burst_spacing) + (self._noise01(seed + 3.2) * 0.22)

                start = self._flash_schedule_cursor + start_offset
                duration = 0.45 + (self._noise01(seed + 4.8) * 0.95)
                intensity = 0.55 + (self._noise01(seed + 5.6) * 0.90)
                strength = 0.28 + (self._noise01(seed + 14.9) * 0.72)

                self._flash_events.append(
                    {
                        "start": start,
                        "end": start + duration,
                        "x_factor": 0.08 + (self._noise01(seed + 7.1) * 0.84),
                        "y_factor": 0.10 + (self._noise01(seed + 9.4) * 0.72),
                        "radius": (7.0 + (self._noise01(seed + 12.7) * 15.0)) * (0.82 + (intensity * 0.42)),
                        "strength": strength,
                        "cross": (2.2 + (self._noise01(seed + 17.3) * 4.2)) * (0.84 + (intensity * 0.32)),
                        "intensity": intensity,
                        "glow_alpha": 0.72 + (self._noise01(seed + 19.1) * 0.70),
                        "core_alpha": 0.78 + (self._noise01(seed + 21.6) * 0.85),
                        "cross_alpha": 0.60 + (self._noise01(seed + 23.4) * 0.90),
                    }
                )
            self._flash_schedule_index += 1

        prune_before = max(0.0, until_time - 48.0)
        self._flash_events = [event for event in self._flash_events if event["end"] >= prune_before]

    def _active_flash_events(self, at_time: float) -> list[dict[str, float]]:
        self._ensure_flash_events(at_time + 45.0)
        return [event for event in getattr(self, "_flash_events", []) if event["start"] <= at_time <= event["end"]]

    def _paint_spark_flashes(self, painter: QPainter, rect: QRectF, *, motion_phase: float = 0.0) -> None:
        for event in self._active_flash_events(motion_phase):
            duration = max(0.01, event["end"] - event["start"])
            progress = max(0.0, min(1.0, (motion_phase - event["start"]) / duration))
            if progress < 0.24:
                envelope = progress / 0.24
            elif progress > 0.72:
                envelope = max(0.0, 1.0 - ((progress - 0.72) / 0.28))
            else:
                envelope = 1.0

            intensity = event.get("intensity", 1.0)
            shimmer = 0.68 + (0.32 * math.sin((progress * math.tau * 2.0) + (event["x_factor"] * (7.0 + (5.0 * intensity)))))
            strength = max(0.0, envelope * shimmer * event["strength"] * intensity)
            if strength <= 0.02:
                continue

            x = rect.width() * event["x_factor"]
            y = rect.height() * event["y_factor"]
            radius = event["radius"] * (0.78 + (0.52 * strength))

            glow = QRadialGradient(x, y, radius)
            glow_color = QColor(self._palette.star_bright)
            glow_color.setAlpha(max(0, min(255, int(104 * strength * event.get("glow_alpha", 1.0)))))
            mid = QColor(self._palette.star_soft)
            mid.setAlpha(max(0, min(255, int(48 * strength * event.get("glow_alpha", 1.0)))))
            edge = QColor(glow_color)
            edge.setAlpha(0)
            glow.setColorAt(0.0, glow_color)
            glow.setColorAt(0.34, mid)
            glow.setColorAt(1.0, edge)
            painter.setBrush(glow)
            painter.drawEllipse(QRectF(x - radius, y - radius, radius * 2.0, radius * 2.0))

            core_size = (1.2 + (2.6 * strength)) * (0.92 + (0.42 * intensity))
            painter.setBrush(QColor(255, 255, 255, max(0, min(255, int(198 * strength * event.get("core_alpha", 1.0))))))
            painter.drawEllipse(QRectF(x - (core_size / 2.0), y - (core_size / 2.0), core_size, core_size))

            painter.setPen(QPen(QColor(255, 255, 255, max(0, min(255, int(94 * strength * event.get("cross_alpha", 1.0))))), 1.0))
            cross = event["cross"] * (0.60 + (0.48 * strength * intensity))
            painter.drawLine(QPointF(x - cross, y), QPointF(x + cross, y))
            painter.drawLine(QPointF(x, y - cross), QPointF(x, y + cross))
            painter.setPen(Qt.NoPen)

    def _paint_depth_haze(self, painter: QPainter, rect: QRectF, *, motion_phase: float = 0.0) -> None:
        haze_specs = (
            (0.22, 0.24, 0.56, 0.030, 0.024),
            (0.74, 0.62, 0.50, 0.022, 0.018),
            (0.50, 0.80, 0.42, 0.020, 0.015),
        )
        for index, (x_factor, y_factor, radius_factor, alpha_core, alpha_mid) in enumerate(haze_specs):
            wobble_x = 0.02 * math.sin((motion_phase * (0.11 + (index * 0.03))) + (index * 1.1))
            wobble_y = 0.02 * math.cos((motion_phase * (0.09 + (index * 0.04))) + (index * 1.6))
            cx = rect.width() * (x_factor + wobble_x)
            cy = rect.height() * (y_factor + wobble_y)
            radius = rect.width() * radius_factor
            haze = QRadialGradient(cx, cy, radius)
            core = QColor(255, 255, 255)
            core.setAlphaF(alpha_core)
            mid = QColor(180, 224, 255)
            mid.setAlphaF(alpha_mid)
            edge = QColor(mid)
            edge.setAlpha(0)
            haze.setColorAt(0.0, core)
            haze.setColorAt(0.50, mid)
            haze.setColorAt(1.0, edge)
            painter.setBrush(haze)
            painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2.0, radius * 2.0))

    def _star_runtime_rows(
        self,
        *,
        layer_seed: float,
        total: int,
        drift_min: float,
        drift_span: float,
        wave_min: float,
        wave_span: float,
        sway_min: float,
        sway_span: float,
    ) -> list[tuple[float, ...]]:
        cache_key = (
            float(layer_seed),
            int(total),
            float(drift_min),
            float(drift_span),
            float(wave_min),
            float(wave_span),
            float(sway_min),
            float(sway_span),
        )
        cached = self._star_runtime_cache.get(cache_key)
        if cached is not None:
            return cached

        rows: list[tuple[float, ...]] = []
        for (
            seed_a,
            seed_b,
            seed_c,
            seed_d,
            seed_e,
            seed_f,
            seed_g,
            seed_h,
            seed_i,
            seed_j,
            seed_k,
            seed_l,
            seed_m,
            seed_n,
        ) in self._star_seed_rows(layer_seed, total):
            parallax = 0.70 + (seed_c * 1.45)
            rows.append(
                (
                    seed_a,
                    seed_b,
                    seed_j,
                    seed_k,
                    seed_l,
                    seed_m,
                    seed_n,
                    parallax,
                    (drift_min + (seed_d * drift_span)) * parallax,
                    wave_min + (seed_e * wave_span),
                    0.0020 + (seed_f * 0.0080),
                    seed_g * math.tau * 2.0,
                    sway_min + (seed_h * sway_span),
                    0.34 + (seed_i * 0.96),
                )
            )
        self._star_runtime_cache[cache_key] = rows
        return rows

    def _lens_specs(self) -> list[tuple[float, ...]]:
        cache_key = self._variant
        cached = self._lens_spec_cache.get(cache_key)
        if cached is not None:
            return cached

        lens_count = 5 if self._variant == "selector" else 3
        rows: list[tuple[float, ...]] = []
        for index in range(lens_count):
            seed = 6200.0 + (index * 9.0)
            rows.append(
                (
                    0.16 + (self._noise01(seed) * 0.68),
                    0.20 + (self._noise01(seed + 1.9) * 0.64),
                    0.06 + (self._noise01(seed + 2.8) * 0.05),
                    0.07 + (self._noise01(seed + 3.4) * 0.06),
                    1.2 + (0.9 * self._noise01(seed + 7.2)),
                    float(index),
                )
            )
        self._lens_spec_cache[cache_key] = rows
        return rows

    def _paint_refractive_lenses(self, painter: QPainter, rect: QRectF, *, motion_phase: float = 0.0) -> None:
        # perf-safe-margin-patch: lens rows cached, frame work reduced to position-only math.
        width = rect.width()
        height = rect.height()
        selector_variant = self._variant == "selector"

        for x_factor, y_factor, rx_factor, ry_factor, dot, index_value in self._lens_seed_rows():
            index = int(index_value)
            cx = width * (x_factor + (0.012 * math.sin((motion_phase * 0.21) + index)))
            cy = height * (y_factor + (0.010 * math.cos((motion_phase * 0.18) + (index * 0.7))))
            rx = width * rx_factor
            ry = height * ry_factor

            lens = QRadialGradient(cx, cy, max(rx, ry))
            core = QColor(255, 255, 255, 14 if selector_variant else 10)
            mid = QColor(255, 255, 255, 6 if selector_variant else 4)
            edge = QColor(255, 255, 255, 0)
            lens.setColorAt(0.0, core)
            lens.setColorAt(0.42, mid)
            lens.setColorAt(1.0, edge)
            painter.setBrush(lens)
            painter.drawEllipse(QRectF(cx - rx, cy - ry, rx * 2.0, ry * 2.0))
            painter.setBrush(QColor(255, 255, 255, 36 if selector_variant else 24))
            painter.drawEllipse(QRectF(cx - (dot * 0.4), cy - (dot * 0.4), dot, dot))

    def _lens_seed_rows(self) -> list[tuple[float, ...]]:
        # perf-safe-margin-patch: cache lens seeds so each frame only applies motion offsets.
        cache_key = self._variant
        cached = self._lens_seed_cache.get(cache_key)
        if cached is not None:
            return cached

        lens_count = 5 if self._variant == "selector" else 3
        rows: list[tuple[float, ...]] = []
        for index in range(lens_count):
            seed = 6200.0 + (index * 9.0)
            rows.append(
                (
                    0.16 + (self._noise01(seed) * 0.68),
                    0.20 + (self._noise01(seed + 1.9) * 0.64),
                    0.06 + (self._noise01(seed + 2.8) * 0.05),
                    0.07 + (self._noise01(seed + 3.4) * 0.06),
                    1.2 + (0.9 * self._noise01(seed + 7.2)),
                    float(index),
                )
            )
        self._lens_seed_cache[cache_key] = rows
        return rows

    def _star_layer_rows(
        self,
        layer_seed: float,
        total: int,
        *,
        size_base: float,
        size_span: float,
        drift_min: float,
        drift_span: float,
        wave_min: float,
        wave_span: float,
        sway_min: float,
        sway_span: float,
    ) -> list[tuple[float, ...]]:
        # perf-safe-margin-patch: cache star-layer math derived from immutable seeds.
        cache_key = (
            float(layer_seed),
            int(total),
            float(size_base),
            float(size_span),
            float(drift_min),
            float(drift_span),
            float(wave_min),
            float(wave_span),
            float(sway_min),
            float(sway_span),
        )
        cached = self._star_layer_cache.get(cache_key)
        if cached is not None:
            return cached

        rows: list[tuple[float, ...]] = []
        for (
            seed_a,
            seed_b,
            seed_c,
            seed_d,
            seed_e,
            seed_f,
            seed_g,
            seed_h,
            seed_i,
            seed_j,
            seed_k,
            seed_l,
            seed_m,
            seed_n,
        ) in self._star_seed_rows(layer_seed, total):
            parallax = 0.70 + (seed_c * 1.45)
            wave_offset = seed_g * math.tau * 2.0
            rows.append(
                (
                    seed_a,
                    seed_b,
                    seed_j,
                    parallax,
                    (drift_min + (seed_d * drift_span)) * parallax,
                    wave_min + (seed_e * wave_span),
                    0.0020 + (seed_f * 0.0080),
                    wave_offset,
                    sway_min + (seed_h * sway_span),
                    0.34 + (seed_i * 0.96),
                    size_base + (seed_j * size_span) + (0.32 if seed_k > 0.90 else 0.0),
                    1.0 if seed_l > 0.80 else 0.0,
                    0.72 + (seed_m * 1.84),
                    seed_n * math.tau * 2.0,
                )
            )
        self._star_layer_cache[cache_key] = rows
        return rows
    def _star_seed_rows(self, layer_seed: float, total: int) -> list[tuple[float, ...]]:
        cache_key = (float(layer_seed), int(total))
        cached = self._star_seed_cache.get(cache_key)
        if cached is not None:
            return cached

        rows: list[tuple[float, ...]] = []
        for index in range(total):
            seed = layer_seed + float(index)
            rows.append(
                (
                    self._noise01((seed * 1.173) + 0.31),
                    self._noise01((seed * 2.417) + 1.17),
                    self._noise01((seed * 3.191) + 2.29),
                    self._noise01((seed * 4.883) + 0.73),
                    self._noise01((seed * 5.731) + 1.91),
                    self._noise01((seed * 6.419) + 3.07),
                    self._noise01((seed * 7.117) + 0.43),
                    self._noise01((seed * 8.411) + 2.61),
                    self._noise01((seed * 9.067) + 1.33),
                    self._noise01((seed * 10.233) + 0.57),
                    self._noise01((seed * 11.521) + 4.11),
                    self._noise01((seed * 12.019) + 2.03),
                    self._noise01((seed * 13.337) + 5.37),
                    self._noise01((seed * 14.907) + 6.73),
                )
            )
        self._star_seed_cache[cache_key] = rows
        return rows

    def _paint_star_layer(
        self,
        painter: QPainter,
        rect: QRectF,
        *,
        layer_seed: float,
        total: int,
        size_base: float,
        size_span: float,
        alpha_scale: float,
        drift_min: float,
        drift_span: float,
        wave_min: float,
        wave_span: float,
        sway_min: float,
        sway_span: float,
        motion_phase: float = 0.0,
        band_bias: float = 0.0,
    ) -> None:
        # perf-safe-margin-patch: cached per-layer star coefficients, per-frame math stays minimal.
        width = rect.width()
        height = rect.height()
        band_scale = band_bias * 0.34

        for (
            seed_a,
            seed_b,
            band_seed,
            parallax,
            drift_x,
            wave_speed,
            wave_amp,
            wave_offset,
            sway_amp,
            sway_speed,
            size,
            bright_flag,
            twinkle_speed,
            twinkle_offset,
        ) in self._star_layer_rows(
            layer_seed,
            total,
            size_base=size_base,
            size_span=size_span,
            drift_min=drift_min,
            drift_span=drift_span,
            wave_min=wave_min,
            wave_span=wave_span,
            sway_min=sway_min,
            sway_span=sway_span,
        ):
            x = width * ((seed_a + (motion_phase * drift_x)) % 1.0)
            y_center = seed_b + (band_scale * (band_seed - 0.5))
            y_offset = math.sin((motion_phase * wave_speed) + wave_offset) * wave_amp
            x_sway = math.cos((motion_phase * sway_speed) + (wave_offset * 0.68)) * sway_amp
            y = height * ((y_center + y_offset) % 1.0)
            x += width * x_sway

            color = QColor(self._palette.star_bright if bright_flag > 0.5 else self._palette.star_soft)
            twinkle_phase = (motion_phase * twinkle_speed) + twinkle_offset
            twinkle = 0.64 + (0.38 * (0.5 + (0.5 * math.sin(twinkle_phase))))
            shimmer = 0.86 + (0.16 * math.sin((motion_phase * 0.38 * parallax) + wave_offset))
            alpha = int(color.alpha() * twinkle * shimmer * alpha_scale)
            color.setAlpha(max(0, min(255, alpha)))
            painter.setBrush(color)
            painter.drawEllipse(QRectF(x, y, size, size))

    def _paint_stars(self, painter: QPainter, rect: QRectF, *, motion_phase: float = 0.0) -> None:
        if self._variant == "progress":
            back_total, mid_total, front_total = 120, 88, 54
        else:
            back_total, mid_total, front_total = 212, 146, 88

        self._paint_star_layer(
            painter,
            rect,
            layer_seed=1400.0,
            total=back_total,
            size_base=0.42,
            size_span=0.78,
            alpha_scale=0.70,
            drift_min=0.00044,
            drift_span=0.00092,
            wave_min=0.22,
            wave_span=0.40,
            sway_min=0.0004,
            sway_span=0.0012,
            motion_phase=motion_phase,
            band_bias=0.10,
        )
        self._paint_star_layer(
            painter,
            rect,
            layer_seed=3200.0,
            total=mid_total,
            size_base=0.58,
            size_span=1.06,
            alpha_scale=0.92,
            drift_min=0.00090,
            drift_span=0.00155,
            wave_min=0.34,
            wave_span=0.62,
            sway_min=0.0008,
            sway_span=0.0018,
            motion_phase=motion_phase,
            band_bias=0.16,
        )
        self._paint_star_layer(
            painter,
            rect,
            layer_seed=5100.0,
            total=front_total,
            size_base=0.76,
            size_span=1.34,
            alpha_scale=1.14,
            drift_min=0.00126,
            drift_span=0.00210,
            wave_min=0.48,
            wave_span=0.82,
            sway_min=0.0011,
            sway_span=0.0028,
            motion_phase=motion_phase,
            band_bias=0.20,
        )

    def _paint_silver_dynamic(self, painter: QPainter, rect: QRectF, *, motion_phase: float = 0.0) -> None:
        self._paint_depth_haze(painter, rect, motion_phase=motion_phase)

        for color, cx, cy, radius in self._orb_specs(rect, motion_phase=motion_phase):
            orb = QRadialGradient(cx, cy, radius)
            edge = QColor(color)
            edge.setAlpha(0)
            mid = QColor(color)
            mid.setAlpha(max(0, int(color.alpha() * 0.42)))
            orb.setColorAt(0.0, color)
            orb.setColorAt(0.40, mid)
            orb.setColorAt(1.0, edge)
            painter.setBrush(orb)
            painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2.0, radius * 2.0))

        self._paint_stars(painter, rect, motion_phase=motion_phase)
        self._paint_spark_flashes(painter, rect, motion_phase=motion_phase)
        self._paint_refractive_lenses(painter, rect, motion_phase=motion_phase)

        painter.setBrush(self._palette.sparkle)
        painter.setPen(Qt.NoPen)
        sparkle_size = 8.0 if self._variant == "progress" else 10.0
        sparkle_x = rect.width() * ((0.88 if self._variant == "selector" else 0.74) + (0.014 * math.sin(motion_phase * 0.54)))
        sparkle_y = rect.height() * (0.12 + (0.016 * math.cos(motion_phase * 0.46)))
        painter.drawEllipse(QRectF(sparkle_x, sparkle_y, sparkle_size, sparkle_size))

    def _paint_standard_dynamic(self, painter: QPainter, rect: QRectF, *, motion_phase: float = 0.0) -> None:
        for color, cx, cy, radius in self._orb_specs(rect, motion_phase=motion_phase):
            orb = QRadialGradient(cx, cy, radius)
            edge = QColor(color)
            edge.setAlpha(0)
            orb.setColorAt(0.0, color)
            orb.setColorAt(0.48, QColor(color.red(), color.green(), color.blue(), max(0, int(color.alpha() * 0.46))))
            orb.setColorAt(1.0, edge)
            painter.setBrush(orb)
            painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2.0, radius * 2.0))

        self._paint_stars(painter, rect, motion_phase=motion_phase)
        self._paint_refractive_lenses(painter, rect, motion_phase=motion_phase)

    def _ensure_clip_path(self, rect: QRectF) -> QPainterPath:
        width = max(1, int(rect.width()))
        height = max(1, int(rect.height()))
        cache_key = (width, height)
        if self._clip_path_cache is not None and self._clip_cache_key == cache_key:
            return self._clip_path_cache

        clip_path = QPainterPath()
        clip_path.addRoundedRect(rect.adjusted(0.75, 0.75, -0.75, -0.75), 30.0, 30.0)
        self._clip_cache_key = cache_key
        self._clip_path_cache = clip_path
        return clip_path

    def _ensure_static_cache(self, rect: QRectF) -> QPixmap:
        width = max(1, int(rect.width()))
        height = max(1, int(rect.height()))
        cache_key = (self._theme_id, self._variant, width, height)
        if self._static_cache is not None and self._static_cache_key == cache_key:
            return self._static_cache

        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        static_rect = QRectF(0.0, 0.0, float(width), float(height))
        bg_gradient = QLinearGradient(static_rect.left(), static_rect.top(), static_rect.left(), static_rect.bottom())
        bg_gradient.setColorAt(0.0, self._palette.canvas_top)
        bg_gradient.setColorAt(1.0, self._palette.canvas_bottom)
        painter.fillRect(static_rect, bg_gradient)

        if _is_silver_theme_id(self._theme_id):
            top_wash = QLinearGradient(static_rect.left(), static_rect.top(), static_rect.right(), static_rect.bottom())
            top_wash.setColorAt(0.0, QColor(255, 255, 255, 18))
            top_wash.setColorAt(0.38, QColor(156, 224, 255, 8))
            top_wash.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.fillRect(static_rect, top_wash)

            vignette = QRadialGradient(static_rect.center(), max(static_rect.width(), static_rect.height()) * 0.78)
            vignette.setColorAt(0.0, QColor(0, 0, 0, 0))
            vignette.setColorAt(0.78, QColor(0, 0, 0, 0))
            vignette.setColorAt(1.0, QColor(0, 0, 0, 76 if self._variant == "selector" else 58))
            painter.setBrush(vignette)
            painter.drawRect(static_rect)

            frame_path = QPainterPath()
            frame_path.addRoundedRect(static_rect.adjusted(1.5, 1.5, -1.5, -1.5), 30.0, 30.0)
            painter.fillPath(frame_path, self._palette.wash)
            painter.setPen(QPen(self._palette.border, 1.15))
            painter.drawPath(frame_path)

            sheen_path = QPainterPath()
            sheen_path.moveTo(static_rect.width() * 0.08, static_rect.height() * 0.10)
            sheen_path.cubicTo(
                static_rect.width() * 0.28,
                static_rect.height() * 0.04,
                static_rect.width() * 0.56,
                static_rect.height() * 0.12,
                static_rect.width() * 0.84,
                static_rect.height() * 0.06,
            )
            painter.setPen(QPen(self._palette.sheen, 1.1))
            painter.drawPath(sheen_path)
        else:
            glass_path = QPainterPath()
            glass_path.addRoundedRect(static_rect.adjusted(1.5, 1.5, -1.5, -1.5), 30.0, 30.0)
            painter.fillPath(glass_path, self._palette.wash)
            painter.setPen(QPen(self._palette.border, 1.2))
            painter.drawPath(glass_path)

        painter.end()
        self._static_cache_key = cache_key
        self._static_cache = pixmap
        return pixmap

    def paintEvent(self, event) -> None:  # type: ignore[override]
        rect = QRectF(self.rect())
        if rect.width() <= 1.0 or rect.height() <= 1.0:
            return

        paint_started = time.perf_counter()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.save()
        painter.setClipPath(self._ensure_clip_path(rect))

        painter.drawPixmap(0, 0, self._ensure_static_cache(rect))

        motion_phase = self._motion_time()
        if _is_silver_theme_id(self._theme_id):
            self._paint_silver_dynamic(painter, rect, motion_phase=motion_phase)
        else:
            self._paint_standard_dynamic(painter, rect, motion_phase=motion_phase)

        painter.restore()
        painter.end()
        self._record_paint_metrics(paint_started)
