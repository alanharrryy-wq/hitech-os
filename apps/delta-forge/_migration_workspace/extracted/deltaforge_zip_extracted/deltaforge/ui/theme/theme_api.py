from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Mapping

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QWidget


@dataclass(frozen=True)
class ThemeSpec:
    name: str
    tokens: Mapping[str, str]
    roles: Mapping[str, str]


_THEME_ALIASES = {
    'default': 'dark',
    'system': 'dark',
}


_THEME_SPECS: dict[str, ThemeSpec] = {
    'dark': ThemeSpec(
        name='dark',
        tokens={
            'canvas_bg': '#0f131a',
            'panel_bg': '#171c26',
            'panel_bg_elevated': '#1d2430',
            'stroke': '#2b3444',
            'fg': '#edf2ff',
            'muted_text': '#94a0b8',
            'focus': '#6e94ff',
            'input_bg': '#0d1219',
        },
        roles={
            'window_bg': '#0f131a',
            'surface_bg': '#171c26',
            'surface_elevated': '#1d2430',
            'border_default': '#2b3444',
            'text_primary': '#edf2ff',
            'text_muted': '#94a0b8',
            'accent': '#6e94ff',
            'accent_text': '#08111f',
            'warning': '#f4cb77',
            'danger': '#ff8c8c',
            'success': '#74d4ab',
            'input_bg': '#0d1219',
        },
    ),
}


@lru_cache(maxsize=8)
def resolve_theme(theme_name: str = 'dark') -> ThemeSpec:
    normalized = (theme_name or 'dark').strip().lower()
    normalized = _THEME_ALIASES.get(normalized, normalized)
    return _THEME_SPECS.get(normalized, _THEME_SPECS['dark'])


def _qcolor(value: str) -> QColor:
    color = QColor(value)
    if color.isValid():
        return color
    return QColor('#000000')


def _build_palette(theme: ThemeSpec) -> QPalette:
    roles = theme.roles
    palette = QPalette()
    window = _qcolor(roles['window_bg'])
    surface = _qcolor(roles['surface_bg'])
    base = _qcolor(roles['input_bg'])
    text = _qcolor(roles['text_primary'])
    muted = _qcolor(roles['text_muted'])
    accent = _qcolor(roles['accent'])
    accent_text = _qcolor(roles['accent_text'])

    palette.setColor(QPalette.Window, window)
    palette.setColor(QPalette.WindowText, text)
    palette.setColor(QPalette.Base, base)
    palette.setColor(QPalette.AlternateBase, surface)
    palette.setColor(QPalette.Text, text)
    palette.setColor(QPalette.Button, surface)
    palette.setColor(QPalette.ButtonText, text)
    palette.setColor(QPalette.ToolTipBase, surface)
    palette.setColor(QPalette.ToolTipText, text)
    palette.setColor(QPalette.PlaceholderText, muted)
    palette.setColor(QPalette.Highlight, accent)
    palette.setColor(QPalette.HighlightedText, accent_text)
    palette.setColor(QPalette.BrightText, _qcolor(roles['danger']))
    return palette


def apply_theme(
    app: QApplication,
    root: QWidget | None = None,
    theme_name: str = 'dark',
) -> ThemeSpec:
    from .stylesheet import build_stylesheet

    theme = resolve_theme(theme_name)
    app.setPalette(_build_palette(theme))
    app.setStyleSheet(build_stylesheet(theme.name))
    if root is not None:
        root.setProperty('theme', theme.name)
        root.style().polish(root)
    return theme
