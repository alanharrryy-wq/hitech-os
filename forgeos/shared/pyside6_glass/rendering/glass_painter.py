from __future__ import annotations

import math
import re
from dataclasses import dataclass

from PySide6.QtCore import QRectF, QPointF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient

from ..appearance import AppearanceTokens
from ..theme import GlassPalette, get_palette

_RGBA_PATTERN = re.compile(r"^rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*([0-9]*\.?[0-9]+)\s*\)$", re.I)


@dataclass(frozen=True, slots=True)
class GlassSurfaceSpec:
    fill_top: QColor
    fill_bottom: QColor
    border_color: QColor
    glow_color: QColor
    highlight_color: QColor
    radius: float = 18.0
    border_width: float = 1.0
    glow_width: float = 8.0
    glow_opacity: float = 0.0
    highlight_strength: float = 0.15
    neon_intensity: float = 0.0
    noise_strength: float = 0.0
    inset: float = 1.0


def qcolor(value: str | QColor, fallback: QColor | None = None) -> QColor:
    if isinstance(value, QColor):
        return QColor(value)
    text = str(value or '').strip()
    if not text:
        return QColor(fallback or QColor(255, 255, 255, 0))
    match = _RGBA_PATTERN.match(text)
    if match:
        r, g, b = [max(0, min(255, int(match.group(i)))) for i in range(1, 4)]
        alpha = float(match.group(4))
        return QColor(r, g, b, max(0, min(255, int(round(alpha * 255.0)))))
    color = QColor(text)
    if color.isValid():
        return color
    return QColor(fallback or QColor(255, 255, 255, 0))


def with_alpha(color: QColor, alpha_factor: float) -> QColor:
    result = QColor(color)
    result.setAlpha(max(0, min(255, int(round(result.alpha() * max(0.0, alpha_factor))))))
    return result


def blend(a: QColor, b: QColor, factor: float) -> QColor:
    t = max(0.0, min(1.0, float(factor)))
    inv = 1.0 - t
    return QColor(
        int((a.red() * inv) + (b.red() * t)),
        int((a.green() * inv) + (b.green() * t)),
        int((a.blue() * inv) + (b.blue() * t)),
        int((a.alpha() * inv) + (b.alpha() * t)),
    )


def _panel_border_for_role(palette: GlassPalette, role: str) -> QColor:
    mapping = {
        'panel_form': palette.panel_form_border,
        'panel_data': palette.panel_data_border,
        'panel_metrics': palette.panel_metrics_border,
        'panel_detail': palette.panel_detail_border,
        'panel_summary': palette.panel_summary_border,
        'panel_aux': palette.panel_aux_border,
    }
    return qcolor(mapping.get(role, palette.card_border), qcolor(palette.card_border))


def build_surface_spec(
    theme_id: str,
    tokens: AppearanceTokens,
    *,
    role: str = 'panel_workspace',
    variant: str = 'glass',
    emphasis: str = 'normal',
    fx_level: str = 'normal',
) -> GlassSurfaceSpec:
    palette = get_palette(theme_id)
    role_key = str(role or 'panel_workspace').strip().lower()
    variant_key = str(variant or 'glass').strip().lower()
    emphasis_key = str(emphasis or 'normal').strip().lower()
    fx_key = str(fx_level or 'normal').strip().lower()

    base_top = qcolor(palette.card_top)
    base_bottom = qcolor(palette.card_bottom)
    border = qcolor(palette.card_border)

    if role_key == 'shell':
        base_top = qcolor(palette.shell_top)
        base_bottom = qcolor(palette.shell_bottom)
        border = qcolor(palette.shell_border)
    elif role_key == 'hero':
        base_top = blend(qcolor(palette.chrome_top), qcolor(palette.card_top), 0.35)
        base_bottom = blend(qcolor(palette.chrome_bottom), qcolor(palette.card_bottom), 0.25)
        border = qcolor(palette.chrome_border)
    elif role_key.startswith('panel_'):
        border = _panel_border_for_role(palette, role_key)
    elif role_key == 'footer':
        base_top = blend(qcolor(palette.button_top), qcolor(palette.card_top), 0.4)
        base_bottom = blend(qcolor(palette.button_bottom), qcolor(palette.card_bottom), 0.3)
        border = qcolor(palette.button_border)
    elif role_key == 'status':
        base_top = blend(qcolor(palette.accent_soft), qcolor(palette.card_top), 0.5)
        base_bottom = blend(qcolor(palette.tab_bg), qcolor(palette.card_bottom), 0.3)
        border = qcolor(palette.tab_border)

    opacity_boost = max(0.35, min(1.8, tokens.surface_opacity_scale))
    base_top = with_alpha(base_top, opacity_boost)
    base_bottom = with_alpha(base_bottom, opacity_boost * 0.96)
    border = with_alpha(border, max(0.55, tokens.border_strength_scale))

    fx_gain = {
        'off': 0.0,
        'soft': 0.68,
        'normal': 1.0,
        'rich': 1.22,
    }.get(fx_key, 1.0)

    glow_seed = qcolor(palette.accent if variant_key != 'subtle' else palette.text_muted, qcolor('#ffffff'))
    glow_opacity = min(0.92, (0.16 + (tokens.glow_intensity * 0.42)) * fx_gain)
    if emphasis_key == 'high':
        glow_opacity = min(0.95, glow_opacity + 0.14)
    if emphasis_key == 'critical':
        glow_opacity = min(0.98, glow_opacity + 0.2)
    if emphasis_key == 'subtle':
        glow_opacity = max(0.0, glow_opacity - 0.08)
    if fx_key == 'off':
        glow_opacity = 0.0
    glow = with_alpha(glow_seed, glow_opacity)

    highlight = with_alpha(qcolor('#ffffff'), (0.12 + (tokens.highlight_strength * 0.28)) * max(0.25, fx_gain))
    radius = 16.0 * max(0.6, tokens.corner_radius_scale)
    if role_key == 'shell':
        radius = 22.0 * max(0.7, tokens.corner_radius_scale)
    if variant_key == 'panel':
        radius *= 0.9

    return GlassSurfaceSpec(
        fill_top=base_top,
        fill_bottom=base_bottom,
        border_color=border,
        glow_color=glow,
        highlight_color=highlight,
        radius=radius,
        border_width=max(
            1.0,
            1.05 * tokens.border_strength_scale + (0.2 if emphasis_key in {'high', 'critical'} else 0.0),
        ),
        glow_width=5.0 + (tokens.glow_intensity * (7.5 + (3.5 * fx_gain))),
        glow_opacity=glow_opacity,
        highlight_strength=tokens.highlight_strength,
        neon_intensity=0.0 if fx_key == 'off' else (tokens.neon_intensity * fx_gain),
        noise_strength=0.0 if fx_key == 'off' else (tokens.noise_strength * min(1.15, fx_gain)),
        inset=1.0,
    )


def paint_glass_surface(painter: QPainter, rect: QRectF, spec: GlassSurfaceSpec) -> None:
    if rect.isEmpty():
        return
    painter.save()
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

    inset_rect = QRectF(rect)
    inset_rect.adjust(spec.inset, spec.inset, -spec.inset, -spec.inset)
    if inset_rect.width() <= 0 or inset_rect.height() <= 0:
        painter.restore()
        return

    path = QPainterPath()
    path.addRoundedRect(inset_rect, spec.radius, spec.radius)

    fill = QLinearGradient(inset_rect.topLeft(), inset_rect.bottomLeft())
    fill.setColorAt(0.0, spec.fill_top)
    fill.setColorAt(1.0, spec.fill_bottom)
    painter.fillPath(path, fill)

    if spec.glow_opacity > 0.0:
        glow_rect = QRectF(inset_rect)
        glow_rect.adjust(-spec.glow_width, -spec.glow_width, spec.glow_width, spec.glow_width)
        glow = QRadialGradient(glow_rect.center(), max(glow_rect.width(), glow_rect.height()) * 0.55)
        glow.setColorAt(0.0, with_alpha(spec.glow_color, spec.glow_opacity * 0.45))
        glow.setColorAt(0.55, with_alpha(spec.glow_color, spec.glow_opacity * 0.16))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillPath(path, glow)

    highlight_rect = QRectF(inset_rect)
    highlight_rect.setHeight(max(8.0, inset_rect.height() * 0.44))
    highlight = QLinearGradient(highlight_rect.topLeft(), highlight_rect.bottomLeft())
    highlight.setColorAt(0.0, spec.highlight_color)
    highlight.setColorAt(1.0, QColor(255, 255, 255, 0))
    highlight_path = QPainterPath()
    highlight_path.addRoundedRect(highlight_rect, spec.radius, spec.radius)
    painter.fillPath(highlight_path.intersected(path), highlight)

    if spec.noise_strength > 0.001:
        painter.save()
        painter.setClipPath(path)
        painter.setPen(Qt.NoPen)
        noise_alpha = max(2, min(16, int(round(spec.noise_strength * 18))))
        for x_index in range(1, int(max(2.0, inset_rect.width() // 18.0))):
            x = inset_rect.left() + (x_index * 18.0)
            y = inset_rect.top() + (6.0 + ((math.sin(x_index * 12.39) + 1.0) * 0.5 * max(6.0, inset_rect.height() - 12.0)))
            painter.setBrush(QColor(255, 255, 255, noise_alpha))
            painter.drawEllipse(QPointF(x, y), 0.65, 0.65)
        painter.restore()

    pen = QPen(spec.border_color)
    pen.setWidthF(spec.border_width)
    painter.setBrush(Qt.NoBrush)
    painter.setPen(pen)
    painter.drawPath(path)

    if spec.neon_intensity > 0.0:
        neon_pen = QPen(with_alpha(spec.glow_color, min(0.95, 0.38 + (spec.neon_intensity * 0.28))))
        neon_pen.setWidthF(max(spec.border_width, 1.5 + (spec.neon_intensity * 1.2)))
        painter.setPen(neon_pen)
        painter.drawPath(path)

    painter.restore()
