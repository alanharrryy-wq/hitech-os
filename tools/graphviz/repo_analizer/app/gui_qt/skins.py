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
    bg="#121418",
    bg_alt="#171b20",
    panel="#1d232b",
    panel_alt="#242b35",
    panel_hover="#2b3440",
    text="#edf2f7",
    text_muted="#94a0b2",
    accent="#ff9a3d",
    accent_hover="#ffb86b",
    accent_soft="#4e341f",
    success="#4dd98d",
    warning="#ffc857",
    danger="#ff6d77",
    border="#303947",
    border_strong="#495567",
    bevel_light="#ffffff14",
    bevel_shadow="#0000008c",
    shadow="#000000b8",
    selection="#2b3a49",
    scrollbar="#526073",
    code_bg="#111419",
    code_text="#e8edf5",
    code_line="#1c2430",
)

CYAN_NOIR = SkinTokens(
    name="cyan_noir",
    display_name="Cyan Noir",
    bg="#11161a",
    bg_alt="#161d23",
    panel="#1b242d",
    panel_alt="#21303a",
    panel_hover="#2a3c49",
    text="#e8f5f8",
    text_muted="#95aeb8",
    accent="#38d7ef",
    accent_hover="#7be8f3",
    accent_soft="#1b3f46",
    success="#4dd98d",
    warning="#ffc857",
    danger="#ff6d77",
    border="#2f4250",
    border_strong="#456072",
    bevel_light="#ffffff14",
    bevel_shadow="#00000092",
    shadow="#000000b8",
    selection="#28404b",
    scrollbar="#556c7b",
    code_bg="#0f1419",
    code_text="#e6f2f6",
    code_line="#18222b",
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
        font-size: 10pt;
    }}

    QMainWindow, QMenuBar, QMenu, QStatusBar {{
        background: {tokens.bg};
        color: {tokens.text};
    }}

    QMenuBar {{
        border-bottom: 1px solid {tokens.border};
    }}

    QMenuBar::item {{
        padding: 6px 10px;
        border-radius: 6px;
        background: transparent;
    }}

    QMenuBar::item:selected,
    QMenu::item:selected {{
        background: {tokens.selection};
        color: {tokens.text};
    }}

    QMenu {{
        border: 1px solid {tokens.border};
        padding: 6px;
    }}

    QToolBar {{
        background: {tokens.bg_alt};
        border: none;
        spacing: 8px;
        padding: 8px;
    }}

    QToolBar#WorkspaceToolbar,
    QToolBar#CommandToolbar {{
        border-bottom: 1px solid {tokens.border};
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

    QComboBox::drop-down {{
        border: none;
        width: 24px;
        background: transparent;
    }}

    QHeaderView::section {{
        background: {tokens.panel_alt};
        color: {tokens.text};
        padding: 9px 10px;
        border: none;
        border-bottom: 1px solid {tokens.accent};
        border-right: 1px solid {tokens.border};
        font-weight: 600;
    }}

    QTableCornerButton::section {{
        background: {tokens.panel_alt};
        border: none;
        border-right: 1px solid {tokens.border};
        border-bottom: 1px solid {tokens.accent};
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

    QTreeView::item, QTableView::item, QListWidget::item {{
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
        padding: 10px 14px;
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

    QCheckBox, QRadioButton {{
        spacing: 8px;
    }}

    QCheckBox::indicator, QRadioButton::indicator {{
        width: 16px;
        height: 16px;
    }}

    QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {{
        border: 1px solid {tokens.border_strong};
        background: {tokens.panel_alt};
        border-radius: 4px;
    }}

    QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
        border: 1px solid {tokens.accent};
        background: {tokens.accent_soft};
        border-radius: 4px;
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

    QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
        background: {tokens.accent};
    }}

    QScrollBar::add-line, QScrollBar::sub-line {{
        background: transparent;
        border: none;
        width: 0px;
        height: 0px;
    }}

    QStatusBar {{
        border-top: 1px solid {tokens.border};
    }}

    QLabel#subtitleLabel,
    QLabel#workspaceMutedLabel,
    QLabel#panelMutedLabel,
    QLabel#svgMetaLabel,
    QLabel#svgHintLabel {{
        color: {tokens.text_muted};
        font-size: 9.5pt;
    }}

    QLabel#heroTitleLabel {{
        font-size: 17pt;
        font-weight: 700;
    }}

    QLabel#heroMetaPill,
    QLabel#panelPill {{
        background: {tokens.accent_soft};
        color: {tokens.accent_hover};
        border: 1px solid {tokens.border};
        border-radius: 999px;
        padding: 4px 10px;
        font-size: 9pt;
        font-weight: 600;
    }}

    QLabel#accentValueLabel {{
        color: {tokens.accent_hover};
        font-size: 18pt;
        font-weight: 700;
    }}

    QLabel#metricTitleLabel {{
        color: {tokens.text_muted};
        font-size: 9pt;
        font-weight: 600;
        text-transform: uppercase;
    }}

    QLabel#metricCaptionLabel {{
        color: {tokens.text_muted};
        font-size: 9pt;
    }}

    QFrame#accentBar {{
        background: {tokens.accent};
        border: none;
        border-radius: 3px;
    }}
    """


def apply_skin(app: QApplication, window: QMainWindow, skin_name: str) -> SkinTokens:
    tokens = get_skin(skin_name)
    app.setStyle('Fusion')
    app.setStyleSheet(_build_stylesheet(tokens))
    window.setProperty('activeSkin', tokens.name)
    app.setProperty('activeSkin', tokens.name)
    return tokens


def rgba(color: str, alpha: int) -> QColor:
    q = QColor(color)
    q.setAlpha(alpha)
    return q
