from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QMainWindow


@dataclass(frozen=True)
class SkinTokens:
    name: str
    display_name: str
    bg: str
    bg_alt: str
    panel: str
    panel_alt: str
    panel_hover: str
    text: str
    text_muted: str
    accent: str
    accent_hover: str
    accent_soft: str
    success: str
    warning: str
    danger: str
    border: str
    border_strong: str
    bevel_light: str
    bevel_shadow: str
    shadow: str
    selection: str
    scrollbar: str
    code_bg: str
    code_text: str
    code_line: str


ORANGE_EMBER = SkinTokens(
    name="orange_ember",
    display_name="Orange Ember",
    bg="#17181d",
    bg_alt="#1b1d24",
    panel="#23262f",
    panel_alt="#2a2e38",
    panel_hover="#313643",
    text="#f3f5f8",
    text_muted="#a2a9b7",
    accent="#ff8f2b",
    accent_hover="#ffad5c",
    accent_soft="#5a3a1d",
    success="#35d07f",
    warning="#ffc857",
    danger="#ff6b6b",
    border="#303643",
    border_strong="#454d5d",
    bevel_light="#ffffff18",
    bevel_shadow="#00000090",
    shadow="#000000aa",
    selection="#2f3d4f",
    scrollbar="#4b5364",
    code_bg="#14161b",
    code_text="#e9edf6",
    code_line="#212734",
)

CYAN_NOIR = SkinTokens(
    name="cyan_noir",
    display_name="Cyan Noir",
    bg="#15181c",
    bg_alt="#191d22",
    panel="#212731",
    panel_alt="#27303c",
    panel_hover="#2e3948",
    text="#eaf6f7",
    text_muted="#9ab0b7",
    accent="#35d0e6",
    accent_hover="#79e6f0",
    accent_soft="#193f46",
    success="#35d07f",
    warning="#ffc857",
    danger="#ff6b6b",
    border="#31404f",
    border_strong="#44586c",
    bevel_light="#ffffff16",
    bevel_shadow="#00000098",
    shadow="#000000aa",
    selection="#2b3d48",
    scrollbar="#506373",
    code_bg="#11161c",
    code_text="#e9f3f8",
    code_line="#1c2630",
)

SKINS: dict[str, SkinTokens] = {
    ORANGE_EMBER.name: ORANGE_EMBER,
    CYAN_NOIR.name: CYAN_NOIR,
}


def list_skins() -> Iterable[SkinTokens]:
    return SKINS.values()


def get_skin(name: str) -> SkinTokens:
    return SKINS.get(name, ORANGE_EMBER)


def _build_stylesheet(tokens: SkinTokens) -> str:
    return f"""
    QWidget {{
        background: {tokens.bg};
        color: {tokens.text};
        selection-background-color: {tokens.selection};
        selection-color: {tokens.text};
        font-family: 'Segoe UI';
        font-size: 10.5pt;
    }}

    QMainWindow, QMenuBar, QMenu, QStatusBar {{
        background: {tokens.bg};
        color: {tokens.text};
    }}

    QMenu::item:selected {{
        background: {tokens.selection};
        border: 1px solid {tokens.accent_soft};
    }}

    QToolBar {{
        background: {tokens.bg_alt};
        border: none;
        spacing: 8px;
        padding: 8px;
    }}

    QToolButton, QPushButton {{
        background: {tokens.panel_alt};
        color: {tokens.text};
        border: 1px solid {tokens.border};
        border-top: 1px solid {tokens.bevel_light};
        border-bottom: 1px solid {tokens.bevel_shadow};
        border-radius: 10px;
        padding: 8px 12px;
    }}

    QToolButton:hover, QPushButton:hover {{
        background: {tokens.panel_hover};
        border: 1px solid {tokens.accent};
    }}

    QToolButton:pressed, QPushButton:pressed {{
        background: {tokens.panel};
        border: 1px solid {tokens.accent_hover};
    }}

    QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QSpinBox {{
        background: {tokens.panel};
        color: {tokens.text};
        border: 1px solid {tokens.border};
        border-top: 1px solid {tokens.bevel_light};
        border-bottom: 1px solid {tokens.bevel_shadow};
        border-radius: 10px;
        padding: 8px 10px;
        selection-background-color: {tokens.selection};
    }}

    QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1px solid {tokens.accent};
    }}

    QHeaderView::section {{
        background: {tokens.panel_alt};
        color: {tokens.text};
        padding: 8px;
        border: none;
        border-bottom: 1px solid {tokens.accent};
        border-right: 1px solid {tokens.border};
        font-weight: 600;
    }}

    QTreeView, QTableView, QListWidget, QTabWidget::pane {{
        background: {tokens.panel};
        alternate-background-color: {tokens.panel_alt};
        border: 1px solid {tokens.border};
        border-top: 1px solid {tokens.bevel_light};
        border-bottom: 1px solid {tokens.bevel_shadow};
        border-radius: 12px;
        outline: 0;
        gridline-color: {tokens.border};
    }}

    QTreeView::item, QTableView::item {{
        padding: 6px;
        border: none;
    }}

    QTreeView::item:selected, QTableView::item:selected, QListWidget::item:selected {{
        background: {tokens.selection};
        border-left: 2px solid {tokens.accent};
    }}

    QDockWidget {{
        color: {tokens.text};
        font-weight: 600;
    }}

    QDockWidget::title {{
        text-align: left;
        background: {tokens.bg_alt};
        color: {tokens.text};
        padding: 8px 12px;
        border-bottom: 1px solid {tokens.accent};
    }}

    QTabBar::tab {{
        background: {tokens.panel_alt};
        color: {tokens.text_muted};
        padding: 8px 12px;
        margin-right: 4px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }}

    QTabBar::tab:selected {{
        background: {tokens.panel};
        color: {tokens.text};
        border-bottom: 1px solid {tokens.accent};
    }}

    QScrollBar:vertical, QScrollBar:horizontal {{
        background: transparent;
        border: none;
        margin: 4px;
    }}
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
        background: {tokens.scrollbar};
        min-height: 30px;
        min-width: 30px;
        border-radius: 6px;
    }}
    QScrollBar::add-line, QScrollBar::sub-line {{
        background: transparent;
        border: none;
        width: 0px;
        height: 0px;
    }}

    QLabel#subtitleLabel {{
        color: {tokens.text_muted};
        font-size: 9.5pt;
    }}

    QFrame#accentBar {{
        background: {tokens.accent};
        border: none;
        border-radius: 3px;
    }}
    """


def apply_skin(app: QApplication, window: QMainWindow, skin_name: str) -> SkinTokens:
    tokens = get_skin(skin_name)
    app.setStyleSheet(_build_stylesheet(tokens))
    window.setProperty("activeSkin", tokens.name)
    app.setProperty("activeSkin", tokens.name)
    return tokens


def rgba(color: str, alpha: int) -> QColor:
    q = QColor(color)
    q.setAlpha(alpha)
    return q
