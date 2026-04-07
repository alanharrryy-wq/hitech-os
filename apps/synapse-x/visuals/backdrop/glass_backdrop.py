from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Optional

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
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
        self.setObjectName("FrostedGlassBackdrop")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(False)
        self._sync_motion_timer()

    def set_motion_enabled(self, enabled: bool) -> None:
        self._motion_enabled = bool(enabled)
        self._sync_motion_timer()

    def _advance_motion(self) -> None:
        if self.isVisible():
            self.update()

    def _motion_time(self) -> float:
        return max(0.0, time.monotonic() - self._motion_epoch)

    def _sync_motion_timer(self) -> None:
        should_run = self._motion_enabled and _is_silver_theme_id(self._theme_id)
        if should_run and not self._motion_timer.isActive():
            self._motion_timer.start()
        elif not should_run and self._motion_timer.isActive():
            self._motion_timer.stop()

    def showEvent(self, event) -> None:  # type: ignore[override]
        self._sync_motion_timer()
        super().showEvent(event)

    def hideEvent(self, event) -> None:  # type: ignore[override]
        if self._motion_timer.isActive():
            self._motion_timer.stop()
        super().hideEvent(event)

    def apply_theme(self, theme_id: str) -> None:
        resolved = normalize_theme(theme_id or DEFAULT_THEME_ID)
        if resolved == self._theme_id:
            return
        self._theme_id = resolved
        self._palette = _glass_palette(self._theme_id, self._variant)
        self._sync_motion_timer()
        self.update()

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
        step = event_index % 3
        if step == 0:
            return 10.0
        if step == 1:
            return 15.0
        return 30.0

    def _ensure_flash_events(self, until_time: float) -> None:
        if not hasattr(self, "_flash_events"):
            self._flash_events: list[dict[str, float]] = []
            self._flash_schedule_cursor = 0.0
            self._flash_schedule_index = 0
        while self._flash_schedule_cursor <= until_time:
            event_index = int(self._flash_schedule_index)
            self._flash_schedule_cursor += self._flash_interval_seconds(event_index)
            pair_count = 1 if self._noise01(8000.0 + (event_index * 1.91)) < 0.78 else 2
            for pair_index in range(pair_count):
                seed = 9100.0 + (event_index * 13.0) + (pair_index * 2.7)
                start = self._flash_schedule_cursor + (0.0 if pair_index == 0 else (0.55 + (self._noise01(seed + 3.2) * 1.05)))
                duration = 0.65 + (self._noise01(seed + 4.8) * 0.75)
                self._flash_events.append(
                    {
                        "start": start,
                        "end": start + duration,
                        "x_factor": 0.08 + (self._noise01(seed + 7.1) * 0.84),
                        "y_factor": 0.10 + (self._noise01(seed + 9.4) * 0.72),
                        "radius": 8.0 + (self._noise01(seed + 12.7) * 12.0),
                        "strength": 0.40 + (self._noise01(seed + 14.9) * 0.25),
                        "cross": 2.8 + (self._noise01(seed + 17.3) * 3.4),
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
            shimmer = 0.74 + (0.26 * math.sin((progress * math.tau * 2.0) + (event["x_factor"] * 8.0)))
            strength = max(0.0, envelope * shimmer * event["strength"])
            if strength <= 0.02:
                continue
            x = rect.width() * event["x_factor"]
            y = rect.height() * event["y_factor"]
            radius = event["radius"] * (0.84 + (0.44 * strength))

            glow = QRadialGradient(x, y, radius)
            glow_color = QColor(self._palette.star_bright)
            glow_color.setAlpha(max(0, min(255, int(98 * strength))))
            mid = QColor(self._palette.star_soft)
            mid.setAlpha(max(0, min(255, int(42 * strength))))
            edge = QColor(glow_color)
            edge.setAlpha(0)
            glow.setColorAt(0.0, glow_color)
            glow.setColorAt(0.34, mid)
            glow.setColorAt(1.0, edge)
            painter.setBrush(glow)
            painter.drawEllipse(QRectF(x - radius, y - radius, radius * 2.0, radius * 2.0))

            core_size = 1.4 + (2.2 * strength)
            painter.setBrush(QColor(255, 255, 255, max(0, min(255, int(188 * strength)))))
            painter.drawEllipse(QRectF(x - (core_size / 2.0), y - (core_size / 2.0), core_size, core_size))
            painter.setPen(QPen(QColor(255, 255, 255, max(0, min(255, int(84 * strength)))), 1.0))
            cross = event["cross"] * (0.68 + (0.36 * strength))
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

    def _paint_refractive_lenses(self, painter: QPainter, rect: QRectF, *, motion_phase: float = 0.0) -> None:
        lens_count = 5 if self._variant == "selector" else 3
        for index in range(lens_count):
            seed = 6200.0 + (index * 9.0)
            cx = rect.width() * ((0.16 + (self._noise01(seed) * 0.68)) + (0.012 * math.sin((motion_phase * 0.21) + index)))
            cy = rect.height() * ((0.20 + (self._noise01(seed + 1.9) * 0.64)) + (0.010 * math.cos((motion_phase * 0.18) + (index * 0.7))))
            rx = rect.width() * (0.06 + (self._noise01(seed + 2.8) * 0.05))
            ry = rect.height() * (0.07 + (self._noise01(seed + 3.4) * 0.06))

            lens = QRadialGradient(cx, cy, max(rx, ry))
            core = QColor(255, 255, 255, 14 if self._variant == "selector" else 10)
            mid = QColor(255, 255, 255, 6 if self._variant == "selector" else 4)
            edge = QColor(255, 255, 255, 0)
            lens.setColorAt(0.0, core)
            lens.setColorAt(0.42, mid)
            lens.setColorAt(1.0, edge)
            painter.setBrush(lens)
            painter.drawEllipse(QRectF(cx - rx, cy - ry, rx * 2.0, ry * 2.0))
            painter.setBrush(QColor(255, 255, 255, 36 if self._variant == "selector" else 24))
            dot = 1.2 + (0.9 * self._noise01(seed + 7.2))
            painter.drawEllipse(QRectF(cx - (dot * 0.4), cy - (dot * 0.4), dot, dot))

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
        for index in range(total):
            seed = layer_seed + float(index)
            seed_a = self._noise01((seed * 1.173) + 0.31)
            seed_b = self._noise01((seed * 2.417) + 1.17)
            seed_c = self._noise01((seed * 3.191) + 2.29)
            seed_d = self._noise01((seed * 4.883) + 0.73)
            seed_e = self._noise01((seed * 5.731) + 1.91)
            seed_f = self._noise01((seed * 6.419) + 3.07)
            seed_g = self._noise01((seed * 7.117) + 0.43)
            seed_h = self._noise01((seed * 8.411) + 2.61)
            seed_i = self._noise01((seed * 9.067) + 1.33)
            seed_j = self._noise01((seed * 10.233) + 0.57)
            seed_k = self._noise01((seed * 11.521) + 4.11)
            seed_l = self._noise01((seed * 12.019) + 2.03)
            seed_m = self._noise01((seed * 13.337) + 5.37)
            seed_n = self._noise01((seed * 14.907) + 6.73)

            parallax = 0.70 + (seed_c * 1.45)
            drift_x = (drift_min + (seed_d * drift_span)) * parallax
            wave_speed = wave_min + (seed_e * wave_span)
            wave_amp = 0.0020 + (seed_f * 0.0080)
            wave_offset = seed_g * math.tau * 2.0
            sway_amp = sway_min + (seed_h * sway_span)
            sway_speed = 0.34 + (seed_i * 0.96)

            x = rect.width() * ((seed_a + (motion_phase * drift_x)) % 1.0)
            y_center = seed_b + ((band_bias * 0.34) * (seed_j - 0.5))
            y_offset = math.sin((motion_phase * wave_speed) + wave_offset) * wave_amp
            x_sway = math.cos((motion_phase * sway_speed) + (wave_offset * 0.68)) * sway_amp
            y = rect.height() * ((y_center + y_offset) % 1.0)
            x += rect.width() * x_sway

            size = size_base + (seed_j * size_span)
            if seed_k > 0.90:
                size += 0.32
            color = QColor(self._palette.star_bright if seed_l > 0.80 else self._palette.star_soft)
            twinkle_phase = (motion_phase * (0.72 + (seed_m * 1.84))) + (seed_n * math.tau * 2.0)
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

    def _paint_silver_field(self, painter: QPainter, rect: QRectF) -> None:
        motion_phase = self._motion_time()
        bg_gradient = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
        bg_gradient.setColorAt(0.0, self._palette.canvas_top)
        bg_gradient.setColorAt(1.0, self._palette.canvas_bottom)
        painter.fillRect(rect, bg_gradient)

        top_wash = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.bottom())
        top_wash.setColorAt(0.0, QColor(255, 255, 255, 18))
        top_wash.setColorAt(0.38, QColor(156, 224, 255, 8))
        top_wash.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(rect, top_wash)
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

        vignette = QRadialGradient(rect.center(), max(rect.width(), rect.height()) * 0.78)
        vignette.setColorAt(0.0, QColor(0, 0, 0, 0))
        vignette.setColorAt(0.78, QColor(0, 0, 0, 0))
        vignette.setColorAt(1.0, QColor(0, 0, 0, 76 if self._variant == "selector" else 58))
        painter.setBrush(vignette)
        painter.drawRect(rect)

        frame_path = QPainterPath()
        frame_path.addRoundedRect(rect.adjusted(1.5, 1.5, -1.5, -1.5), 30.0, 30.0)
        painter.fillPath(frame_path, self._palette.wash)
        painter.setPen(QPen(self._palette.border, 1.15))
        painter.drawPath(frame_path)

        sheen_path = QPainterPath()
        sheen_path.moveTo(rect.width() * 0.08, rect.height() * 0.10)
        sheen_path.cubicTo(
            rect.width() * 0.28,
            rect.height() * 0.04,
            rect.width() * 0.56,
            rect.height() * 0.12,
            rect.width() * 0.84,
            rect.height() * 0.06,
        )
        painter.setPen(QPen(self._palette.sheen, 1.1))
        painter.drawPath(sheen_path)

        painter.setBrush(self._palette.sparkle)
        painter.setPen(Qt.NoPen)
        sparkle_size = 8.0 if self._variant == "progress" else 10.0
        sparkle_x = rect.width() * ((0.88 if self._variant == "selector" else 0.74) + (0.014 * math.sin(motion_phase * 0.54)))
        sparkle_y = rect.height() * (0.12 + (0.016 * math.cos(motion_phase * 0.46)))
        painter.drawEllipse(QRectF(sparkle_x, sparkle_y, sparkle_size, sparkle_size))

    def paintEvent(self, event) -> None:  # type: ignore[override]
        rect = QRectF(self.rect())
        if rect.width() <= 1.0 or rect.height() <= 1.0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        clip_path = QPainterPath()
        clip_path.addRoundedRect(rect.adjusted(0.75, 0.75, -0.75, -0.75), 30.0, 30.0)
        painter.save()
        painter.setClipPath(clip_path)

        if _is_silver_theme_id(self._theme_id):
            self._paint_silver_field(painter, rect)
            painter.restore()
            painter.end()
            return

        motion_phase = self._motion_time()
        bg_gradient = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
        bg_gradient.setColorAt(0.0, self._palette.canvas_top)
        bg_gradient.setColorAt(1.0, self._palette.canvas_bottom)
        painter.fillRect(rect, bg_gradient)

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
        glass_path = QPainterPath()
        glass_path.addRoundedRect(rect.adjusted(1.5, 1.5, -1.5, -1.5), 30.0, 30.0)
        painter.fillPath(glass_path, self._palette.wash)
        painter.setPen(QPen(self._palette.border, 1.2))
        painter.drawPath(glass_path)
        painter.restore()
        painter.end()
