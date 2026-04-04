from __future__ import annotations

from .theme import get_palette


def build_app_stylesheet(theme_id: str) -> str:
    p = get_palette(theme_id)
    return f"""
QFrame#WindowChrome {{
    min-height: 34px;
    max-height: 34px;
    border-radius: 10px;
    border: 1px solid rgba(140, 235, 255, 0.22);
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
    background: rgba(12, 21, 32, 0.20);
    border: 1px solid rgba(140, 235, 255, 0.08);
}}
QFrame#WindowChrome QPushButton:hover {{
    background: rgba(140, 235, 255, 0.12);
    border: 1px solid rgba(140, 235, 255, 0.62);
}}
QFrame#WindowChrome QPushButton:pressed {{
    background: rgba(140, 235, 255, 0.18);
    border: 1px solid rgba(140, 235, 255, 0.86);
}}
QFrame#WindowChrome QPushButton[chrome_kind="close"]:hover {{
    background: rgba(140, 235, 255, 0.13);
    border: 1px solid rgba(140, 235, 255, 0.66);
}}
QFrame[hoverable="true"][hover="true"] {{
    border-color: rgba(140, 235, 255, 0.58);
}}
"""


__all__ = [
    "build_app_stylesheet",
]
