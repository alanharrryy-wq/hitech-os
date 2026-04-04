from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import Any, Optional

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PySide6.QtWidgets import QWidget

from .appearance import AppearanceProfile, AppearanceSnapshot, EffectsProfile, resolve_appearance_tokens
from .contracts import DEFAULT_THEME_ID
from .skin.backdrop_spec import build_backdrop_spec

try:  # optional, used only when installed
    from perlin_noise import PerlinNoise
except Exception:  # pragma: no cover - optional dependency
    PerlinNoise = None  # type: ignore[assignment]

@dataclass(frozen=True, slots=True)
class _AtmospherePalette:
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


def _clean_token(value: Any, fallback: str = '') -> str:
    token = str(value or '').strip()
    return token or fallback


def _atmosphere_palette(theme_id: str, snapshot: AppearanceSnapshot) -> _AtmospherePalette:
    material = build_backdrop_spec(theme_id, snapshot)
    return _AtmospherePalette(
        canvas_top=material.canvas_top,
        canvas_bottom=material.canvas_bottom,
        wash=material.wash,
        border=material.border,
        line=material.line,
        sheen=material.sheen,
        orb_a=material.orb_a,
        orb_b=material.orb_b,
        orb_c=material.orb_c,
        sparkle=material.sparkle,
        star_soft=material.star_soft,
        star_bright=material.star_bright,
    )


class FrostedGlassBackdrop(QWidget):
    """Atmospheric shell backdrop driven by appearance snapshots.

    The final version does not require the historical Atlas bridge to build
    its palette. It derives atmosphere directly from the theme registry plus
    appearance/effects state.
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        theme_id: str = DEFAULT_THEME_ID,
        variant: str = 'selector',
        motion_enabled: bool = True,
    ) -> None:
        super().__init__(parent)
        self._variant = _clean_token(variant, 'selector').lower() or 'selector'
        self._profile = AppearanceProfile(theme_id=theme_id).normalized()
        self._effects = EffectsProfile.from_appearance(self._profile)
        self._snapshot = AppearanceSnapshot(profile=self._profile, effects=self._effects, source='backdrop_init')
        self._theme_id = self._profile.theme_id
        tokens = resolve_appearance_tokens(self._profile, self._effects)
        self._surface_opacity_scale = float(tokens.surface_opacity_scale)
        self._border_strength_scale = float(tokens.border_strength_scale)
        self._palette = _atmosphere_palette(self._profile.theme_id, self._snapshot)
        self._motion_enabled = bool(motion_enabled)
        self._motion_epoch = time.monotonic()
        self._noise = PerlinNoise(octaves=2, seed=7) if PerlinNoise is not None else None
        self._stars = self._build_stars(seed=42)

        self._motion_timer = QTimer(self)
        self._motion_timer.setInterval(24)
        self._motion_timer.timeout.connect(self._advance_motion)

        self.setObjectName('FrostedGlassBackdrop')
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(False)
        self._sync_motion_timer()

    @property
    def snapshot(self) -> AppearanceSnapshot:
        return self._snapshot

    def set_motion_enabled(self, enabled: bool) -> None:
        self._motion_enabled = bool(enabled)
        self._sync_motion_timer()
        self.update()

    def apply_theme(self, theme_id: str) -> None:
        self.apply_appearance(profile=self._profile.with_updates(theme_id=theme_id), effects=self._effects, source='apply_theme')

    def apply_appearance(
        self,
        snapshot: AppearanceSnapshot | AppearanceProfile | None = None,
        effects: EffectsProfile | None = None,
        *,
        profile: AppearanceProfile | None = None,
        source: str = 'apply_appearance',
    ) -> None:
        if isinstance(snapshot, AppearanceProfile):
            profile = snapshot
            snapshot = None

        if snapshot is None:
            next_profile = (profile or self._profile).normalized()
            next_effects = (effects or self._effects or EffectsProfile.from_appearance(next_profile)).normalized()
            snapshot = AppearanceSnapshot(profile=next_profile, effects=next_effects, source=source)
        self._snapshot = snapshot
        self._profile = snapshot.profile.normalized()
        self._effects = snapshot.effects.normalized()
        tokens = resolve_appearance_tokens(self._profile, self._effects)
        self._theme_id = self._profile.theme_id
        self._surface_opacity_scale = float(tokens.surface_opacity_scale)
        self._border_strength_scale = float(tokens.border_strength_scale)
        self._motion_enabled = bool(tokens.motion_enabled)
        self._palette = _atmosphere_palette(self._profile.theme_id, self._snapshot)
        self._sync_motion_timer()
        self.update()

    def _build_stars(self, *, seed: int) -> list[tuple[float, float, float, bool]]:
        rng = random.Random(seed)
        stars: list[tuple[float, float, float, bool]] = []
        for _ in range(36):
            stars.append((rng.random(), rng.random(), 0.4 + (rng.random() * 1.4), bool(rng.randint(0, 1))))
        return stars

    def _advance_motion(self) -> None:
        if self.isVisible():
            self.update()

    def _sync_motion_timer(self) -> None:
        tokens = resolve_appearance_tokens(self._profile, self._effects)
        should_run = self._motion_enabled and tokens.motion_enabled
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

    def _motion_time(self) -> float:
        return max(0.0, time.monotonic() - self._motion_epoch)

    def _orb_specs(self, rect: QRectF, motion_phase: float) -> list[tuple[QColor, float, float, float]]:
        tokens = resolve_appearance_tokens(self._profile, self._effects)
        wobble = 0.020 + (0.015 * tokens.gaussian_softness)
        base_specs = [
            (self._palette.orb_a, 0.58, 0.18, 0.55, 0.08, 0.06),
            (self._palette.orb_b, 0.18, 0.72, 0.34, 0.12, 0.09),
            (self._palette.orb_c, 0.90, 0.62, 0.36, 0.10, 0.07),
        ]
        specs: list[tuple[QColor, float, float, float]] = []
        for index, (color, x_factor, y_factor, radius_factor, x_speed, y_speed) in enumerate(base_specs, start=1):
            x_wobble = math.sin((motion_phase * x_speed) + (index * 0.9)) * wobble
            y_wobble = math.cos((motion_phase * y_speed) + (index * 1.3)) * (wobble * 1.25)
            radius_wobble = 1.0 + (0.05 * math.sin((motion_phase * 0.08) + (index * 1.7)))
            specs.append((
                color,
                rect.width() * (x_factor + x_wobble),
                rect.height() * (y_factor + y_wobble),
                rect.width() * radius_factor * radius_wobble,
            ))
        return specs

    def _paint_noise(self, painter: QPainter, rect: QRectF) -> None:
        tokens = resolve_appearance_tokens(self._profile, self._effects)
        if tokens.noise_strength <= 0.0:
            return
        painter.save()
        painter.setPen(Qt.NoPen)
        width = max(1, int(rect.width() // 64))
        height = max(1, int(rect.height() // 64))
        for x in range(width):
            for y in range(height):
                sample = 0.0
                if self._noise is not None:
                    sample = float(self._noise([x / max(1, width), y / max(1, height)]))
                alpha = int(round((sample + 1.0) * 0.5 * 36 * tokens.noise_strength))
                if alpha <= 2:
                    continue
                painter.fillRect(
                    int((x / width) * rect.width()),
                    int((y / height) * rect.height()),
                    int(rect.width() / width) + 1,
                    int(rect.height() / height) + 1,
                    QColor(255, 255, 255, alpha),
                )
        painter.restore()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        rect = QRectF(self.rect())
        if rect.width() <= 1 or rect.height() <= 1:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        radius = 22.0
        shell = QPainterPath()
        shell.addRoundedRect(rect.adjusted(1.0, 1.0, -1.0, -1.0), radius, radius)
        painter.setClipPath(shell)

        bg = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        bg.setColorAt(0.0, self._palette.canvas_top)
        bg.setColorAt(1.0, self._palette.canvas_bottom)
        painter.fillPath(shell, bg)

        motion_phase = self._motion_time() if self._motion_timer.isActive() else 0.0
        for color, cx, cy, radius_px in self._orb_specs(rect, motion_phase):
            radial = QRadialGradient(QPointF(cx, cy), radius_px)
            center = QColor(color)
            edge = QColor(color)
            edge.setAlpha(0)
            radial.setColorAt(0.0, center)
            radial.setColorAt(1.0, edge)
            painter.fillRect(rect, radial)

        wash = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        wash.setColorAt(0.0, self._palette.wash)
        tail = QColor(self._palette.wash)
        tail.setAlpha(0)
        wash.setColorAt(1.0, tail)
        painter.fillPath(shell, wash)

        for sx, sy, size, bright in self._stars:
            px = rect.left() + (rect.width() * sx)
            py = rect.top() + (rect.height() * sy)
            color = self._palette.star_bright if bright else self._palette.star_soft
            painter.fillRect(QRectF(px, py, size, size), color)

        self._paint_noise(painter, rect)

        sheen = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.top())
        sheen.setColorAt(0.0, QColor(255, 255, 255, 0))
        sheen.setColorAt(0.5, self._palette.sheen)
        sheen.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setPen(QPen(self._palette.line, 1.0))
        painter.drawLine(int(rect.left()) + 18, int(rect.top()) + 12, int(rect.right()) - 18, int(rect.top()) + 12)
        painter.fillRect(QRectF(rect.left() + 18, rect.top() + 6, rect.width() - 36, 2.0), sheen)

        painter.setClipping(False)
        painter.setPen(QPen(self._palette.border, 1.0))
        painter.drawRoundedRect(rect.adjusted(1.0, 1.0, -1.0, -1.0), radius, radius)
        painter.end()


__all__ = ['FrostedGlassBackdrop']
