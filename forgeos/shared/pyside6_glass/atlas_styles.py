from __future__ import annotations

"""Compatibility shim for historical Atlas-style callers.

This module intentionally stays tiny. The visual system now lives in
`theme.py`, `appearance/`, `effects.py`, `rendering/`, and `backdrop.py`.
Keep this file as a thin API surface only.
"""

from .theme import get_palette


def build_app_stylesheet(theme_id: str) -> str:
    p = get_palette(theme_id)
    return f"""
QFrame#WindowChrome {{
    min-height: 34px;
    max-height: 34px;
    border-radius: 10px;
    border: 1px solid {p.chrome_border};
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 {p.chrome_top},
        stop:1 {p.chrome_bottom}
    );
}}
QFrame#WindowChrome QLabel[role="window_title"] {{
    color: {p.text_primary};
}}
QFrame#WindowChrome QLabel[role="window_icon"] {{
    color: {p.accent};
}}
QFrame#WindowChrome QPushButton {{
    min-width: 30px;
    max-width: 30px;
    min-height: 22px;
    max-height: 22px;
    border-radius: 8px;
    padding: 0px;
    color: {p.text_primary};
    background: {p.button_top};
    border: 1px solid {p.button_border};
}}
QFrame#WindowChrome QPushButton:hover {{
    background: {p.accent_soft};
    border: 1px solid {p.shell_border_hover};
}}
QFrame#WindowChrome QPushButton:pressed {{
    background: {p.button_bottom};
    border: 1px solid {p.shell_border};
}}
QFrame[hoverable="true"][hover="true"] {{
    border-color: {p.shell_border_hover};
}}
"""


__all__ = ['build_app_stylesheet']
