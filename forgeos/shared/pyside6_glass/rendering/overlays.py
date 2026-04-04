from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QRect, Qt
from PySide6.QtWidgets import QWidget

from ..appearance import AppearanceSnapshot, resolve_appearance_tokens
from ..visual_contracts import (
    normalize_visual_emphasis,
    normalize_visual_fx_level,
    normalize_visual_role,
    normalize_visual_variant,
    set_visual_properties,
)
from .glass_painter import GlassSurfaceSpec, build_surface_spec, paint_glass_surface


class GlassSurfaceOverlay(QWidget):
    def __init__(self, target: QWidget) -> None:
        super().__init__(target)
        self._target = target
        self._spec: GlassSurfaceSpec | None = None
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setAutoFillBackground(False)
        self.setObjectName(f"{target.objectName() or target.__class__.__name__}_surface_overlay")
        target.installEventFilter(self)
        self._sync_geometry()
        self.lower()
        self.show()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self._target and event.type() in {
            QEvent.Resize,
            QEvent.Move,
            QEvent.Show,
            QEvent.Hide,
            QEvent.ZOrderChange,
            QEvent.PolishRequest,
        }:
            self._sync_geometry()
            self.update()
        return False

    def _sync_geometry(self) -> None:
        self.setGeometry(QRect(0, 0, max(0, self._target.width()), max(0, self._target.height())))
        self.setVisible(self._target.isVisible())
        self.lower()

    def set_surface_spec(self, spec: GlassSurfaceSpec | None) -> None:
        self._spec = spec
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        if self._spec is None:
            return
        from PySide6.QtGui import QPainter
        painter = QPainter(self)
        paint_glass_surface(painter, self.rect(), self._spec)
        painter.end()


def install_surface_overlay(target: QWidget) -> GlassSurfaceOverlay:
    overlay = getattr(target, '_glass_surface_overlay', None)
    if not isinstance(overlay, GlassSurfaceOverlay):
        overlay = GlassSurfaceOverlay(target)
        setattr(target, '_glass_surface_overlay', overlay)
    overlay._sync_geometry()
    return overlay


def sync_surface_overlay(
    target: QWidget,
    snapshot: AppearanceSnapshot,
    *,
    role: str | None = None,
    variant: str | None = None,
    emphasis: str | None = None,
    fx_level: str | None = None,
) -> GlassSurfaceOverlay:
    overlay = install_surface_overlay(target)
    role_value = normalize_visual_role(role or target.property('visualRole') or 'panel_workspace')
    variant_value = normalize_visual_variant(variant or target.property('visualVariant') or 'glass')
    emphasis_value = normalize_visual_emphasis(emphasis or target.property('visualEmphasis') or 'normal')
    fx_value = normalize_visual_fx_level(fx_level or target.property('visualFxLevel') or 'normal')
    set_visual_properties(
        target,
        role=role_value,
        variant=variant_value,
        emphasis=emphasis_value,
        fx_level=fx_value,
    )
    tokens = resolve_appearance_tokens(snapshot.profile, snapshot.effects)
    spec = build_surface_spec(
        snapshot.profile.theme_id,
        tokens,
        role=role_value,
        variant=variant_value,
        emphasis=emphasis_value,
        fx_level=fx_value,
    )
    overlay.set_surface_spec(spec)
    target.setProperty('visualGlowIntensity', tokens.glow_intensity)
    target.setProperty('visualNeonIntensity', tokens.neon_intensity)
    target.setProperty('visualBlurScale', tokens.blur_intensity_scale)
    target.setProperty('visualCornerRadiusScale', tokens.corner_radius_scale)
    return overlay
