from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QMainWindow

try:
    from shiboken6 import isValid as qt_object_is_valid
except ImportError:  # pragma: no cover - PySide6 ships shiboken6
    def qt_object_is_valid(obj):
        return obj is not None


@dataclass(frozen=True)
class SkinTokens:
    name: str
    display_name: str

    # Foundation
    bg: str
    bg_alt: str
    bg_elevated: str

    # Surfaces
    panel: str
    panel_alt: str
    panel_hover: str
    panel_active: str

    # Text
    text: str
    text_muted: str
    text_soft: str

    # Accent system
    accent: str
    accent_hover: str
    accent_pressed: str
    accent_soft: str
    accent_glow: str

    # Status
    success: str
    warning: str
    danger: str

    # Structure
    border: str
    border_soft: str
    border_strong: str

    # Light / depth
    bevel_light: str
    bevel_shadow: str
    shadow: str
    selection: str
    focus_ring: str

    # Chrome extras
    toolbar_bg: str
    dock_title_bg: str
    menu_bg: str
    scrollbar: str
    scrollbar_hover: str
    splitter: str

    # Code / graph area
    code_bg: str
    code_text: str
    code_line: str


ORANGE_EMBER = SkinTokens(
    name="orange_ember",
    display_name="Orange Ember",
    bg="#101317",
    bg_alt="#151a20",
    bg_elevated="#1a2028",
    panel="#1c232c",
    panel_alt="#232c37",
    panel_hover="#2a3440",
    panel_active="#313d4b",
    text="#eef3f8",
    text_muted="#96a3b6",
    text_soft="#7d8999",
    accent="#ff9a3d",
    accent_hover="#ffb86b",
    accent_pressed="#ff8a22",
    accent_soft="#4f341f",
    accent_glow="#ff9a3d33",
    success="#4dd98d",
    warning="#ffc857",
    danger="#ff6d77",
    border="#2f3946",
    border_soft="#242d38",
    border_strong="#4f5e72",
    bevel_light="#ffffff16",
    bevel_shadow="#00000094",
    shadow="#000000c4",
    selection="#2e3d4d",
    focus_ring="#ff9a3d55",
    toolbar_bg="#141920",
    dock_title_bg="#18202a",
    menu_bg="#171d24",
    scrollbar="#5a687b",
    scrollbar_hover="#ff9a3d",
    splitter="#364252",
    code_bg="#0f1318",
    code_text="#e8edf5",
    code_line="#1b2330",
)

CYAN_NOIR = SkinTokens(
    name="cyan_noir",
    display_name="Cyan Noir",
    bg="#0f1418",
    bg_alt="#141b21",
    bg_elevated="#182129",
    panel="#1a242c",
    panel_alt="#21303a",
    panel_hover="#2a3c49",
    panel_active="#314654",
    text="#ebf5f8",
    text_muted="#97afba",
    text_soft="#80929b",
    accent="#38d7ef",
    accent_hover="#7be8f3",
    accent_pressed="#21c7df",
    accent_soft="#1a4047",
    accent_glow="#38d7ef33",
    success="#4dd98d",
    warning="#ffc857",
    danger="#ff6d77",
    border="#2e4150",
    border_soft="#23323d",
    border_strong="#486276",
    bevel_light="#ffffff15",
    bevel_shadow="#00000094",
    shadow="#000000c4",
    selection="#29414c",
    focus_ring="#38d7ef50",
    toolbar_bg="#131a20",
    dock_title_bg="#17212a",
    menu_bg="#161d23",
    scrollbar="#5c7180",
    scrollbar_hover="#38d7ef",
    splitter="#35505f",
    code_bg="#0e1318",
    code_text="#e6f2f6",
    code_line="#18222b",
)

SKINS: dict[str, SkinTokens] = {
    ORANGE_EMBER.name: ORANGE_EMBER,
    CYAN_NOIR.name: CYAN_NOIR,
}


def list_skins() -> Iterable[SkinTokens]:
    return SKINS.values()


def _is_live_qt_object(obj: object) -> bool:
    if obj is None:
        return False
    if not hasattr(obj, "metaObject"):
        return False
    try:
        return bool(qt_object_is_valid(obj))
    except Exception:
        return False


def _coerce_skin_tokens(tokens: object) -> SkinTokens:
    if isinstance(tokens, SkinTokens):
        return tokens
    return ORANGE_EMBER


def get_skin(name: Any) -> SkinTokens:
    if isinstance(name, SkinTokens):
        return name if name.name in SKINS else ORANGE_EMBER

    if name is None:
        return ORANGE_EMBER

    try:
        key = str(name).strip().lower()
    except Exception:
        return ORANGE_EMBER

    if not key:
        return ORANGE_EMBER
    return SKINS.get(key, ORANGE_EMBER)


def _build_stylesheet(tokens: SkinTokens) -> str:
    tokens = _coerce_skin_tokens(tokens)
    return f"""
    QWidget {{
        background: {tokens.bg};
        color: {tokens.text};
        selection-background-color: {tokens.selection};
        selection-color: {tokens.text};
        font-family: 'Segoe UI';
        font-size: 10pt;
    }}

    QMainWindow {{
        background: {tokens.bg};
    }}

    QMenuBar, QMenu, QStatusBar {{
        color: {tokens.text};
    }}

    QMenuBar {{
        background: {tokens.bg};
        border: none;
        border-bottom: 1px solid {tokens.border};
        padding: 4px 8px 6px 8px;
    }}

    QMenuBar::item {{
        padding: 7px 12px;
        border-radius: 8px;
        background: transparent;
        color: {tokens.text_muted};
        margin: 0 2px;
    }}

    QMenuBar::item:selected {{
        background: {tokens.bg_elevated};
        color: {tokens.text};
    }}

    QMenuBar::item:pressed {{
        background: {tokens.panel};
        color: {tokens.text};
    }}

    QMenu {{
        background: {tokens.menu_bg};
        border: 1px solid {tokens.border};
        border-radius: 12px;
        padding: 8px;
    }}

    QMenu::item {{
        padding: 8px 12px;
        border-radius: 8px;
        background: transparent;
    }}

    QMenu::item:selected {{
        background: {tokens.selection};
        color: {tokens.text};
    }}

    QMenu::separator {{
        height: 1px;
        background: {tokens.border_soft};
        margin: 6px 4px;
    }}

    QToolBar {{
        background: {tokens.toolbar_bg};
        border: none;
        spacing: 8px;
        padding: 8px 10px;
    }}

    QToolBar#WorkspaceToolbar,
    QToolBar#CommandToolbar {{
        background: {tokens.toolbar_bg};
        border-bottom: 1px solid {tokens.border};
    }}

    QToolBar#SvgToolbar {{
        background: {tokens.bg_alt};
        border-bottom: 1px solid {tokens.accent};
        spacing: 8px;
        padding: 8px 12px;
    }}

    QToolBar::separator {{
        width: 1px;
        margin: 4px 6px;
        background: {tokens.border_soft};
    }}

    QToolButton, QPushButton {{
        background: {tokens.panel_alt};
        color: {tokens.text};
        border: 1px solid {tokens.border};
        border-top: 1px solid {tokens.bevel_light};
        border-bottom: 1px solid {tokens.bevel_shadow};
        border-radius: 11px;
        padding: 8px 12px;
    }}

    QToolButton:hover, QPushButton:hover {{
        background: {tokens.panel_hover};
        border: 1px solid {tokens.accent};
    }}

    QToolButton:pressed, QPushButton:pressed {{
        background: {tokens.panel};
        border: 1px solid {tokens.accent_pressed};
        padding-top: 9px;
        padding-bottom: 7px;
    }}

    QToolButton:checked {{
        background: {tokens.panel_active};
        border: 1px solid {tokens.accent};
        color: {tokens.text};
    }}

    QToolButton:disabled, QPushButton:disabled {{
        background: {tokens.panel};
        color: {tokens.text_soft};
        border: 1px solid {tokens.border_soft};
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

    QLineEdit:hover, QPlainTextEdit:hover, QTextEdit:hover, QComboBox:hover, QSpinBox:hover {{
        border: 1px solid {tokens.border_strong};
        background: {tokens.bg_elevated};
    }}

    QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1px solid {tokens.accent};
        background: {tokens.bg_elevated};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 26px;
        background: transparent;
    }}

    QAbstractItemView {{
        selection-background-color: {tokens.selection};
        selection-color: {tokens.text};
        outline: 0;
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
        margin: 1px 3px;
        border-radius: 7px;
    }}

    QTreeView::item:hover, QTableView::item:hover, QListWidget::item:hover {{
        background: {tokens.bg_elevated};
    }}

    QTreeView::item:selected, QTableView::item:selected, QListWidget::item:selected {{
        background: {tokens.selection};
        border-left: 2px solid {tokens.accent};
        color: {tokens.text};
    }}

    QGraphicsView#svgGraphicsView {{
        background: {tokens.code_bg};
        border: 1px solid {tokens.border};
        border-radius: 12px;
    }}

    QDockWidget {{
        color: {tokens.text};
        font-weight: 600;
    }}

    QDockWidget::title {{
        text-align: left;
        background: {tokens.dock_title_bg};
        color: {tokens.text};
        padding: 10px 14px;
        border-top: 1px solid {tokens.bevel_light};
        border-bottom: 1px solid {tokens.accent};
    }}

    QTabWidget::pane {{
        top: -1px;
    }}

    QTabBar::tab {{
        background: {tokens.panel_alt};
        color: {tokens.text_muted};
        padding: 8px 13px;
        margin-right: 4px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        border: 1px solid {tokens.border};
        border-bottom: none;
    }}

    QTabBar::tab:hover {{
        background: {tokens.panel_hover};
        color: {tokens.text};
    }}

    QTabBar::tab:selected {{
        background: {tokens.panel};
        color: {tokens.text};
        border: 1px solid {tokens.accent};
        border-bottom: 1px solid {tokens.panel};
    }}

    QCheckBox, QRadioButton {{
        spacing: 8px;
        color: {tokens.text};
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

    QScrollBar:vertical {{
        width: 12px;
    }}

    QScrollBar:horizontal {{
        height: 12px;
    }}

    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
        background: {tokens.scrollbar};
        min-height: 30px;
        min-width: 30px;
        border-radius: 6px;
    }}

    QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
        background: {tokens.scrollbar_hover};
    }}

    QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {{
        background: transparent;
        border: none;
        width: 0px;
        height: 0px;
    }}

    QSplitter::handle {{
        background: {tokens.splitter};
        margin: 2px;
    }}

    QSplitter::handle:horizontal {{
        width: 3px;
    }}

    QSplitter::handle:vertical {{
        height: 3px;
    }}

    QStatusBar {{
        background: {tokens.bg};
        border-top: 1px solid {tokens.border};
        color: {tokens.text_muted};
    }}

    QLabel {{
        background: transparent;
    }}

    QLabel#subtitleLabel,
    QLabel#workspaceMutedLabel,
    QLabel#panelMutedLabel,
    QLabel#svgMetaLabel,
    QLabel#svgHintLabel,
    QLabel#secondaryMetaLabel {{
        color: {tokens.text_muted};
        font-size: 9.5pt;
    }}

    QLabel#svgStatusLabel {{
        color: {tokens.accent_hover};
        font-size: 9pt;
        font-weight: 700;
    }}

    QLabel#heroTitleLabel {{
        font-size: 17pt;
        font-weight: 700;
        color: {tokens.text};
    }}

    QLabel#heroMetaPill,
    QLabel#panelPill,
    QLabel#toolbarPill,
    QLabel#statusPill {{
        background: {tokens.accent_soft};
        color: {tokens.accent_hover};
        border: 1px solid {tokens.border};
        border-radius: 999px;
        padding: 4px 10px;
        font-size: 9pt;
        font-weight: 700;
    }}

    QLabel#accentValueLabel {{
        color: {tokens.accent_hover};
        font-size: 18pt;
        font-weight: 700;
    }}

    QLabel#metricTitleLabel {{
        color: {tokens.text_soft};
        font-size: 9pt;
        font-weight: 700;
        text-transform: uppercase;
    }}

    QLabel#metricCaptionLabel {{
        color: {tokens.text_muted};
        font-size: 9pt;
    }}

    QLabel#sectionTitleLabel {{
        color: {tokens.text};
        font-size: 11pt;
        font-weight: 700;
    }}

    QFrame#accentBar {{
        background: {tokens.accent};
        border: none;
        border-radius: 3px;
    }}

    QFrame#surfaceCard,
    QFrame#heroPanel,
    QFrame#metricPanel,
    QFrame#toolbarSurface {{
        background: {tokens.panel};
        border: 1px solid {tokens.border};
        border-top: 1px solid {tokens.bevel_light};
        border-bottom: 1px solid {tokens.bevel_shadow};
        border-radius: 14px;
    }}

    QFrame#surfaceCard:hover,
    QFrame#heroPanel:hover,
    QFrame#metricPanel:hover,
    QFrame#toolbarSurface:hover {{
        background: {tokens.bg_elevated};
        border: 1px solid {tokens.border_strong};
    }}

    QFrame#surfaceCardElevated,
    QFrame#heroPanelElevated {{
        background: {tokens.bg_elevated};
        border: 1px solid {tokens.border_strong};
        border-radius: 14px;
    }}
    """


def apply_skin(
    app: QApplication | None,
    window: QMainWindow | None,
    skin_name: Any,
) -> SkinTokens:
    tokens = get_skin(skin_name)

    if _is_live_qt_object(app) and hasattr(app, "setStyle") and hasattr(app, "setStyleSheet"):
        try:
            app.setStyle("Fusion")
            app.setStyleSheet(_build_stylesheet(tokens))
        except Exception:
            pass

    if _is_live_qt_object(window) and hasattr(window, "setProperty"):
        try:
            window.setProperty("activeSkin", tokens.name)
        except Exception:
            pass

    if _is_live_qt_object(app) and hasattr(app, "setProperty"):
        try:
            app.setProperty("activeSkin", tokens.name)
        except Exception:
            pass

    return tokens


def rgba(color: str, alpha: int) -> QColor:
    try:
        alpha_value = int(alpha)
    except (TypeError, ValueError):
        alpha_value = 0

    alpha_value = max(0, min(255, alpha_value))

    try:
        q = QColor(color)
    except Exception:
        q = QColor()

    if not q.isValid():
        q = QColor(0, 0, 0, 0)

    q.setAlpha(alpha_value)
    return q
