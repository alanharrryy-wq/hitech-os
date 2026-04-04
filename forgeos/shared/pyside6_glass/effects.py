from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import QEasingCurve, Property, QEvent, QObject, Qt, QPropertyAnimation
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget

from .appearance import AppearanceProfile, EffectsProfile, resolve_appearance_tokens
from .skin.shadow_spec import shadow_spec_from_profiles as _material_shadow_spec_from_profiles
from .theme import get_palette


@dataclass(frozen=True, slots=True)
class ShadowSpec:
    blur: float
    x_offset: float
    y_offset: float
    alpha: int
    enabled: bool = True


def shadow_spec_from_profiles(
    profile: AppearanceProfile,
    effects: EffectsProfile | None = None,
) -> ShadowSpec:
    material = _material_shadow_spec_from_profiles(profile, effects, emphasis="normal")
    return ShadowSpec(
        blur=float(material.blur),
        x_offset=float(material.x_offset),
        y_offset=float(material.y_offset),
        alpha=int(material.alpha),
        enabled=bool(material.enabled),
    )


def apply_shadow_profile(
    widget: QWidget,
    profile: AppearanceProfile,
    effects: EffectsProfile | None = None,
    *,
    color: Optional[QColor] = None,
) -> None:
    spec = shadow_spec_from_profiles(profile, effects)
    apply_shadow(
        widget,
        blur=spec.blur,
        x_offset=spec.x_offset,
        y_offset=spec.y_offset,
        alpha=spec.alpha,
        color=color,
        enabled=spec.enabled,
    )


@dataclass(frozen=True, slots=True)
class GlowSpec:
    blur: float
    color: QColor
    enabled: bool = True


def glow_color_from_theme(theme_id: str, *, alpha: int = 96) -> QColor:
    palette = get_palette(theme_id)
    color = QColor(palette.accent)
    if not color.isValid():
        color = QColor(palette.text_primary)
    color.setAlpha(max(0, min(255, int(alpha))))
    return color


def glow_spec_from_profiles(
    profile: AppearanceProfile,
    effects: EffectsProfile | None = None,
) -> GlowSpec:
    tokens = resolve_appearance_tokens(profile, effects)
    enabled = bool(tokens.glow_intensity > 0.0)
    return GlowSpec(
        blur=max(8.0, 8.0 + (tokens.glow_intensity * 18.0)),
        color=glow_color_from_theme(profile.theme_id, alpha=max(18, min(180, int(40 + (tokens.glow_intensity * 120))))),
        enabled=enabled,
    )


class GlowPulseDriver(QObject):
    def __init__(self, widget: QWidget, *, duration_ms: int = 220, parent: QObject | None = None) -> None:
        super().__init__(parent or widget)
        self._widget = widget
        self._value = 0.0
        self._enabled = True
        self._animation = QPropertyAnimation(self, b'glowProgress', self)
        self._animation.setDuration(max(1, int(duration_ms)))
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

    def _get_value(self) -> float:
        return self._value

    def _set_value(self, value: float) -> None:
        self._value = float(value)
        self._widget.setProperty('glowProgress', round(self._value, 4))
        repolish(self._widget, recursive=False)

    glowProgress = Property(float, _get_value, _set_value)  # type: ignore[assignment]

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)
        if not self._enabled:
            self._animation.stop()
            self._set_value(0.0)

    def set_duration_ms(self, duration_ms: int) -> None:
        self._animation.setDuration(max(1, int(duration_ms)))

    def pulse(self) -> None:
        if not self._enabled:
            return
        self._animation.stop()
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.start()


def install_glow_pulse_driver(
    widget: QWidget,
    *,
    duration_ms: int | None = None,
    profile: AppearanceProfile | None = None,
    effects: EffectsProfile | None = None,
) -> GlowPulseDriver:
    resolved_duration = max(1, int(duration_ms if duration_ms is not None else 220))
    motion_enabled = True
    if profile is not None:
        tokens = resolve_appearance_tokens(profile, effects)
        resolved_duration = max(1, int(duration_ms if duration_ms is not None else max(1, tokens.motion_duration_ms)))
        motion_enabled = bool(tokens.motion_enabled)
    driver = getattr(widget, '_glass_glow_pulse_driver', None)
    if isinstance(driver, GlowPulseDriver):
        driver.set_duration_ms(resolved_duration)
        driver.set_enabled(motion_enabled)
        return driver
    driver = GlowPulseDriver(widget, duration_ms=resolved_duration)
    driver.set_enabled(motion_enabled)
    setattr(widget, '_glass_glow_pulse_driver', driver)
    return driver


def apply_shadow(
    widget: QWidget,
    *,
    blur: float = 22.0,
    x_offset: float = 0.0,
    y_offset: float = 6.0,
    alpha: int = 68,
    color: Optional[QColor] = None,
    enabled: bool = True,
) -> None:
    if widget is None:
        return

    if not enabled:
        widget.setGraphicsEffect(None)
        return

    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsDropShadowEffect):
        effect = QGraphicsDropShadowEffect(widget)
        widget.setGraphicsEffect(effect)

    effect.setBlurRadius(max(0.0, float(blur)))
    effect.setOffset(float(x_offset), float(y_offset))
    effect.setColor(color or QColor(0, 0, 0, max(0, min(255, int(alpha)))))


def repolish(widget: QWidget, recursive: bool = False) -> None:
    if widget is None:
        return

    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()

    if recursive:
        for child in widget.findChildren(QWidget):
            child_style = child.style()
            child_style.unpolish(child)
            child_style.polish(child)
            child.update()


class _HoverCardFilter(QObject):
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        if isinstance(watched, QWidget):
            if event.type() in {QEvent.Enter, QEvent.HoverEnter}:
                watched.setProperty("hover", True)
                repolish(watched)
            elif event.type() in {QEvent.Leave, QEvent.HoverLeave}:
                watched.setProperty("hover", False)
                repolish(watched)
        return False


_CARD_HOVER_FILTER: _HoverCardFilter | None = None


def enable_card_hover(widget: QWidget) -> None:
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


__all__ = [
    "GlowPulseDriver",
    "GlowSpec",
    "ShadowSpec",
    "glow_color_from_theme",
    "glow_spec_from_profiles",
    "install_glow_pulse_driver",
    "apply_shadow",
    "apply_shadow_profile",
    "shadow_spec_from_profiles",
    "repolish",
    "enable_card_hover",
]
