from __future__ import annotations

from dataclasses import dataclass

from .contracts import DEFAULT_THEME_ID, GLASS_RADIUS


@dataclass(frozen=True, slots=True)
class GlassPalette:
    shell_top: str
    shell_bottom: str
    shell_border: str
    shell_border_hover: str
    chrome_top: str
    chrome_bottom: str
    chrome_border: str
    card_top: str
    card_bottom: str
    card_border: str
    text_primary: str
    text_muted: str
    accent: str
    accent_soft: str
    button_top: str
    button_bottom: str
    button_border: str
    danger_top: str
    danger_bottom: str
    danger_border: str
    input_bg: str
    input_border: str
    input_border_hover: str
    progress_bg: str
    progress_chunk_top: str
    progress_chunk_bottom: str


def get_palette(theme_id: str = DEFAULT_THEME_ID) -> GlassPalette:
    # For now all aliases map to the frozen silver frost cyan theme.
    _ = (theme_id or DEFAULT_THEME_ID).strip().lower()
    return GlassPalette(
        shell_top="rgba(20, 33, 54, 0.92)",
        shell_bottom="rgba(10, 19, 37, 0.95)",
        shell_border="rgba(157, 214, 255, 0.28)",
        shell_border_hover="rgba(181, 233, 255, 0.42)",
        chrome_top="rgba(72, 88, 112, 0.34)",
        chrome_bottom="rgba(38, 48, 68, 0.30)",
        chrome_border="rgba(205, 235, 255, 0.20)",
        card_top="rgba(82, 102, 126, 0.36)",
        card_bottom="rgba(46, 57, 75, 0.34)",
        card_border="rgba(178, 224, 255, 0.22)",
        text_primary="#e7f2fb",
        text_muted="#b7cbdd",
        accent="#8cefff",
        accent_soft="rgba(140, 239, 255, 0.26)",
        button_top="rgba(132, 213, 250, 0.34)",
        button_bottom="rgba(102, 168, 212, 0.26)",
        button_border="rgba(168, 229, 255, 0.36)",
        danger_top="rgba(230, 165, 130, 0.18)",
        danger_bottom="rgba(174, 110, 82, 0.14)",
        danger_border="rgba(238, 177, 145, 0.28)",
        input_bg="rgba(21, 35, 56, 0.72)",
        input_border="rgba(149, 204, 242, 0.24)",
        input_border_hover="rgba(165, 227, 255, 0.40)",
        progress_bg="rgba(19, 34, 52, 0.82)",
        progress_chunk_top="#8cefff",
        progress_chunk_bottom="#78d5f0",
    )


def _gradient(top: str, bottom: str) -> str:
    return f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {top}, stop:1 {bottom})"


def build_stylesheet(theme_id: str = DEFAULT_THEME_ID) -> str:
    p = get_palette(theme_id)
    r = GLASS_RADIUS
    return f"""
QWidget#GlassStage,
QWidget#GlassContent {{
    background: transparent;
}}

QFrame#Shell {{
    background: {_gradient(p.shell_top, p.shell_bottom)};
    border: 1px solid {p.shell_border};
    border-radius: {r.shell}px;
}}
QFrame#Shell:hover {{
    border: 1px solid {p.shell_border_hover};
}}
QFrame#Shell[variant="progress"] {{
    border-radius: {r.shell_progress}px;
}}

QFrame#WindowChrome {{
    background: {_gradient(p.chrome_top, p.chrome_bottom)};
    border: 1px solid {p.chrome_border};
    border-radius: {r.window_chrome}px;
}}

QFrame[card="hero"] {{
    background: {_gradient(p.card_top, p.card_bottom)};
    border: 1px solid {p.card_border};
    border-radius: {r.hero_card}px;
}}

QFrame[card="true"],
QFrame[card="muted"],
QFrame[card="footer"] {{
    background: {_gradient(p.card_top, p.card_bottom)};
    border: 1px solid {p.card_border};
    border-radius: {r.card}px;
}}

QLabel[role="title"] {{
    color: {p.text_primary};
    font-size: 30px;
    font-weight: 760;
}}
QLabel[role="subtitle"],
QLabel[role="hint"],
QLabel[role="value"] {{
    color: {p.text_muted};
    font-size: 12px;
}}
QLabel[role="eyebrow"],
QLabel[role="field"] {{
    color: {p.accent};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}}
QLabel[role="window_title"] {{
    color: {p.text_primary};
    font-size: 12px;
    font-weight: 700;
}}

QLineEdit,
QComboBox,
QTextEdit,
QPlainTextEdit {{
    background: {p.input_bg};
    border: 1px solid {p.input_border};
    border-radius: {r.input}px;
    color: {p.text_primary};
    padding: 8px 10px;
}}
QLineEdit:hover,
QLineEdit:focus,
QComboBox:hover,
QComboBox:focus {{
    border: 1px solid {p.input_border_hover};
}}

QPushButton {{
    background: {_gradient(p.button_top, p.button_bottom)};
    border: 1px solid {p.button_border};
    border-radius: {r.button}px;
    color: {p.text_primary};
    padding: 8px 14px;
    font-weight: 650;
}}
QPushButton:hover {{
    border: 1px solid {p.accent};
}}
QPushButton[variant="danger"] {{
    background: {_gradient(p.danger_top, p.danger_bottom)};
    border: 1px solid {p.danger_border};
}}

QProgressBar {{
    border-radius: {r.progress}px;
    border: 1px solid {p.input_border};
    background: {p.progress_bg};
    text-align: center;
    color: {p.text_primary};
}}
QProgressBar::chunk {{
    border-radius: {r.progress - 1}px;
    background: {_gradient(p.progress_chunk_top, p.progress_chunk_bottom)};
}}
"""

