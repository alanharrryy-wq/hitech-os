from __future__ import annotations

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
    background: rgba(12, 21, 32, 0.44);
    border: 1px solid {p.input_border};
}}
QFrame#WindowChrome QPushButton:hover {{
    background: {p.accent_soft};
    border: 1px solid {p.accent};
}}
QFrame#WindowChrome QPushButton:pressed {{
    background: rgba(140, 235, 255, 0.28);
    border: 1px solid rgba(140, 235, 255, 0.82);
}}
QFrame#WindowChrome QPushButton[chrome_kind="close"]:hover {{
    background: rgba(140, 235, 255, 0.18);
    border: 1px solid rgba(140, 235, 255, 0.26);
}}
QFrame[hoverable="true"][hover="true"] {{
    border-color: {p.shell_border_hover};
}}
"""


__all__ = [
    "build_app_stylesheet",
]

