from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Iterable

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QMainWindow

_REPO_ROOT = Path(__file__).resolve().parents[5]
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)

from forgeos.shared.pyside6_glass.theme import (
    build_stylesheet as build_shared_glass_stylesheet,
)

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
    bg="#0f1318",
    bg_alt="#141a22",
    bg_elevated="#1a212c",
    panel="#1d2531",
    panel_alt="#232d3a",
    panel_hover="#2b3747",
    panel_active="#314258",
    text="#edf2f8",
    text_muted="#9aa8bc",
    text_soft="#7c8a9e",
    accent="#d9a168",
    accent_hover="#e4b582",
    accent_pressed="#c8925a",
    accent_soft="#36281a",
    accent_glow="#d9a1682c",
    success="#5fc794",
    warning="#d8b36d",
    danger="#d58086",
    border="#2d3848",
    border_soft="#263140",
    border_strong="#3f5067",
    bevel_light="#ffffff12",
    bevel_shadow="#00000073",
    shadow="#0000009f",
    selection="#2f4058",
    focus_ring="#d9a1686b",
    toolbar_bg="#111821",
    dock_title_bg="#151f2b",
    menu_bg="#151e28",
    scrollbar="#4f5d70",
    scrollbar_hover="#d9a168",
    splitter="#2f3c4e",
    code_bg="#0b1118",
    code_text="#e8eef6",
    code_line="#15202d",
)

CYAN_NOIR = SkinTokens(
    name="cyan_noir",
    display_name="Cyan Noir",
    bg="#0f1318",
    bg_alt="#141b22",
    bg_elevated="#19222b",
    panel="#1d2732",
    panel_alt="#23303d",
    panel_hover="#2a3949",
    panel_active="#304356",
    text="#ebf3f7",
    text_muted="#98aeb8",
    text_soft="#7f949f",
    accent="#7fb8c1",
    accent_hover="#98c8cf",
    accent_pressed="#6ea8b2",
    accent_soft="#1f363a",
    accent_glow="#7fb8c12b",
    success="#60c797",
    warning="#d8b570",
    danger="#d27f88",
    border="#2d3d4d",
    border_soft="#253241",
    border_strong="#3e556a",
    bevel_light="#ffffff11",
    bevel_shadow="#00000073",
    shadow="#0000009f",
    selection="#2d4458",
    focus_ring="#7fb8c167",
    toolbar_bg="#111921",
    dock_title_bg="#15212a",
    menu_bg="#142028",
    scrollbar="#4d6270",
    scrollbar_hover="#7fb8c1",
    splitter="#2f4353",
    code_bg="#0b1118",
    code_text="#e6eff4",
    code_line="#14212c",
)

GRAPHITE_LUXE = SkinTokens(
    name="graphite_luxe",
    display_name="Graphite Luxe",
    bg="#0d1117",
    bg_alt="#11161d",
    bg_elevated="#161d26",
    panel="#1a222d",
    panel_alt="#202a37",
    panel_hover="#273447",
    panel_active="#2e3f56",
    text="#e9eef6",
    text_muted="#9caabc",
    text_soft="#78879b",
    accent="#88addc",
    accent_hover="#a4c0e6",
    accent_pressed="#729bce",
    accent_soft="#1f3048",
    accent_glow="#88addc2d",
    success="#5fc794",
    warning="#d7b36b",
    danger="#d37b84",
    border="#2b3748",
    border_soft="#243041",
    border_strong="#3b4c64",
    bevel_light="#ffffff12",
    bevel_shadow="#00000076",
    shadow="#000000a3",
    selection="#2d415a",
    focus_ring="#88addc69",
    toolbar_bg="#101721",
    dock_title_bg="#151f2c",
    menu_bg="#141e2a",
    scrollbar="#4e5c70",
    scrollbar_hover="#6b87ad",
    splitter="#2e3b4c",
    code_bg="#0a1018",
    code_text="#e5ebf3",
    code_line="#141d2a",
)

ALABASTER_GLASS = SkinTokens(
    name="alabaster_glass",
    display_name="Alabaster Glass",
    bg="#f1f4f8",
    bg_alt="#e8eef5",
    bg_elevated="#fcfeff",
    panel="#f9fcff",
    panel_alt="#eef4fb",
    panel_hover="#e4edf8",
    panel_active="#dbe7f4",
    text="#182433",
    text_muted="#465a72",
    text_soft="#6c8098",
    accent="#536f90",
    accent_hover="#617fa3",
    accent_pressed="#446181",
    accent_soft="#d5e1ef",
    accent_glow="#536f9026",
    success="#2f8b67",
    warning="#9a6f2b",
    danger="#af4d58",
    border="#c7d3e3",
    border_soft="#d8e0ec",
    border_strong="#adbed4",
    bevel_light="#ffffffe6",
    bevel_shadow="#8da0b53d",
    shadow="#1b2b3a1f",
    selection="#d7e4f3",
    focus_ring="#536f9056",
    toolbar_bg="#f3f7fc",
    dock_title_bg="#e9f0f8",
    menu_bg="#fbfdff",
    scrollbar="#a5b6ca",
    scrollbar_hover="#6d87a5",
    splitter="#c0cedf",
    code_bg="#e5edf7",
    code_text="#1f2f43",
    code_line="#d0dceb",
)

SKINS: dict[str, SkinTokens] = {
    ALABASTER_GLASS.name: ALABASTER_GLASS,
    GRAPHITE_LUXE.name: GRAPHITE_LUXE,
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


def _hex_rgba(color_hex: str, alpha: int) -> str:
    try:
        color = QColor(color_hex)
    except Exception:
        color = QColor()

    if not color.isValid():
        color = QColor(0, 0, 0)

    alpha = max(0, min(255, int(alpha)))
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {alpha})"


def _build_stylesheet(tokens: SkinTokens) -> str:
    tokens = _coerce_skin_tokens(tokens)
    soft_border = _hex_rgba(tokens.border, 176)
    soft_accent = _hex_rgba(tokens.accent, 44)
    panel_hover_soft = _hex_rgba(tokens.panel_hover, 215)
    splitter_soft = _hex_rgba(tokens.splitter, 220)
    menu_bg = _hex_rgba(tokens.menu_bg, 244)
    chrome_border = _hex_rgba(tokens.border, 198)
    accent_line = _hex_rgba(tokens.accent, 78)
    glass_bg = _hex_rgba(tokens.bg_elevated, 242)
    muted_panel = _hex_rgba(tokens.panel_alt, 232)
    tree_hover = _hex_rgba(tokens.panel_hover, 230)
    tree_selection = _hex_rgba(tokens.selection, 242)
    header_bg = _hex_rgba(tokens.panel_alt, 246)
    local_styles = f"""
    QWidget {{
        background: {tokens.bg};
        color: {tokens.text};
        selection-background-color: {tokens.selection};
        selection-color: {tokens.text};
        font-family: 'Segoe UI Variable Text', 'Segoe UI', sans-serif;
        font-size: 11pt;
    }}

    QMainWindow {{
        background: {tokens.bg};
    }}

    QWidget#workspaceCanvasRootSurface,
    QWidget#workspaceCanvasSurface {{
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 {tokens.bg_alt},
            stop:1 {tokens.bg}
        );
        border: none;
    }}

    QMenuBar {{
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 {tokens.toolbar_bg},
            stop:0.62 {tokens.bg_alt},
            stop:1 {tokens.bg}
        );
        border: none;
        border-bottom: 1px solid {chrome_border};
        padding: 4px 10px 5px 10px;
        spacing: 4px;
    }}

    QMenuBar::item {{
        padding: 5px 11px;
        margin: 0 2px;
        border: 1px solid transparent;
        border-radius: 9px;
        background: transparent;
        color: {tokens.text_muted};
    }}

    QMenuBar::item:selected {{
        background: {glass_bg};
        border: 1px solid {tokens.border_soft};
        color: {tokens.text};
    }}

    QMenuBar::item:pressed {{
        background: {tokens.panel_active};
        border: 1px solid {accent_line};
        color: {tokens.text};
    }}

    QMenu {{
        background: {menu_bg};
        color: {tokens.text};
        border: 1px solid {tokens.border};
        border-radius: 10px;
        padding: 7px;
    }}

    QMenu::item {{
        padding: 7px 10px;
        margin: 1px 0;
        border-radius: 7px;
        background: transparent;
    }}

    QMenu::item:selected {{
        background: {tokens.selection};
        color: {tokens.text};
    }}

    QMenu::separator {{
        height: 1px;
        margin: 6px 4px;
        background: {tokens.border_soft};
    }}

    QToolBar {{
        border: none;
        spacing: 10px;
    }}

    QToolBar#WorkspaceToolbar {{
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 {tokens.toolbar_bg},
            stop:0.58 {tokens.bg_alt},
            stop:1 {tokens.bg}
        );
        border-top: 1px solid {tokens.bevel_light};
        border-bottom: 1px solid {chrome_border};
        padding: 9px 12px 8px 12px;
    }}

    QToolBar#CommandToolbar {{
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 {tokens.bg_alt},
            stop:0.52 {tokens.bg},
            stop:1 {tokens.bg}
        );
        border-bottom: 1px solid {chrome_border};
        padding: 7px 12px 9px 12px;
    }}

    QToolBar#SvgToolbar {{
        background: {tokens.toolbar_bg};
        border-bottom: 1px solid {tokens.border};
        padding: 8px 10px;
        spacing: 8px;
    }}

    QToolBar::separator {{
        width: 1px;
        margin: 7px 9px;
        background: {tokens.border_soft};
    }}

    QFrame#panelCard,
    QFrame#workspaceHeroSurface,
    QFrame#workspaceRepoSurface,
    QFrame#workspaceNavSurface,
    QFrame#workspaceSkinSurface,
    QFrame#commandDeckSurface,
    QFrame#commandFiltersSurface,
    QFrame#commandLayoutSurface,
    QFrame#searchOptionsSurface,
    QFrame#searchActionsSurface,
    QFrame#bookmarksActionsSurface,
    QWidget#searchInspectorSurface,
    QWidget#fileInspectorSurface {{
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 {glass_bg},
            stop:0.48 {tokens.panel},
            stop:1 {tokens.panel_alt}
        );
        border: 1px solid {chrome_border};
        border-top: 1px solid {tokens.bevel_light};
        border-radius: 13px;
    }}

    QFrame#workspaceHeroSurface,
    QFrame#commandDeckSurface {{
        border: 1px solid {tokens.border_strong};
    }}

    QFrame#panelCard:hover,
    QFrame#workspaceHeroSurface:hover,
    QFrame#workspaceRepoSurface:hover,
    QFrame#workspaceNavSurface:hover,
    QFrame#workspaceSkinSurface:hover,
    QFrame#commandDeckSurface:hover,
    QFrame#commandFiltersSurface:hover,
    QFrame#commandLayoutSurface:hover {{
        border: 1px solid {tokens.border_strong};
    }}

    QFrame#metricTile {{
        background: {tokens.panel_alt};
        border: 1px solid {tokens.border_soft};
        border-radius: 12px;
    }}

    QFrame#metricTile:hover {{
        background: {tokens.panel_hover};
        border: 1px solid {tokens.border_strong};
    }}

    QLineEdit,
    QPlainTextEdit,
    QTextEdit,
    QComboBox,
    QSpinBox {{
        background: {tokens.panel};
        color: {tokens.text};
        border: 1px solid {tokens.border};
        border-radius: 10px;
        padding: 8px 11px;
        min-height: 20px;
    }}

    QLineEdit:hover,
    QPlainTextEdit:hover,
    QTextEdit:hover,
    QComboBox:hover,
    QSpinBox:hover {{
        border: 1px solid {tokens.border_strong};
        background: {tokens.panel_alt};
    }}

    QLineEdit:focus,
    QPlainTextEdit:focus,
    QTextEdit:focus,
    QComboBox:focus,
    QSpinBox:focus {{
        border: 1px solid {tokens.accent};
        background: {tokens.bg_elevated};
    }}

    QLineEdit#heroSearchBox {{
        border-radius: 12px;
        border: 1px solid {tokens.border_strong};
        padding: 10px 14px;
        background: {tokens.bg_elevated};
        font-size: 10.2pt;
    }}

    QLineEdit#heroSearchBox:focus {{
        border: 1px solid {tokens.accent};
        background: {tokens.panel};
    }}

    QLineEdit#treeFilterSurface {{
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 {glass_bg},
            stop:1 {tokens.panel}
        );
        border: 1px solid {tokens.border};
        border-radius: 11px;
        padding: 7px 11px;
    }}

    QLineEdit#treeFilterSurface:hover {{
        border: 1px solid {tokens.border_strong};
    }}

    QLineEdit#treeFilterSurface:focus {{
        border: 1px solid {tokens.accent};
        background: {tokens.bg_elevated};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 24px;
        background: transparent;
    }}

    QComboBox#repoComboBox,
    QComboBox#skinComboBox,
    QComboBox#quickFilterComboBox,
    QComboBox#extComboBox,
    QComboBox#sortComboBox {{
        background: {tokens.bg_elevated};
    }}

    QPushButton,
    QToolButton {{
        background: {tokens.panel_alt};
        color: {tokens.text};
        border: 1px solid {tokens.border};
        border-radius: 9px;
        padding: 7px 11px;
    }}

    QPushButton:hover,
    QToolButton:hover {{
        background: {tokens.panel_hover};
        border: 1px solid {tokens.border_strong};
    }}

    QPushButton:pressed,
    QToolButton:pressed {{
        background: {tokens.panel_active};
        border: 1px solid {tokens.accent_pressed};
        padding-top: 8px;
        padding-bottom: 6px;
    }}

    QPushButton:checked,
    QToolButton:checked {{
        background: {tokens.selection};
        border: 1px solid {tokens.accent};
    }}

    QPushButton:disabled,
    QToolButton:disabled {{
        background: {tokens.panel};
        border: 1px solid {tokens.border_soft};
        color: {tokens.text_soft};
    }}

    QTreeView,
    QTableView,
    QListWidget,
    QTabWidget::pane {{
        background: {tokens.panel};
        alternate-background-color: {tokens.panel_alt};
        border: 1px solid {tokens.border};
        border-radius: 11px;
        outline: 0;
        gridline-color: {tokens.border_soft};
    }}

    QTreeView#repoTreeSurface,
    QTreeView#importsTreeSurface,
    QTreeView#dependentsTreeSurface,
    QListWidget#bookmarksListSurface,
    QTableView#resultsTableSurface {{
        background: {tokens.panel};
        border: 1px solid {tokens.border};
        border-radius: 11px;
    }}

    QTreeView#repoTreeSurface {{
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 {glass_bg},
            stop:1 {tokens.panel_alt}
        );
        alternate-background-color: {muted_panel};
        border: 1px solid {tokens.border_strong};
        border-radius: 12px;
        padding: 4px 3px 4px 3px;
        outline: 0;
    }}

    QTreeView#repoTreeSurface::item {{
        padding: 7px 8px;
        margin: 1px 4px;
        border-radius: 7px;
    }}

    QTreeView#repoTreeSurface::item:hover {{
        background: {tree_hover};
    }}

    QTreeView#repoTreeSurface::item:selected {{
        background: {tree_selection};
        color: {tokens.text};
        border-left: 3px solid {tokens.accent};
        border-right: 1px solid {soft_border};
    }}

    QTreeView::item,
    QTableView::item,
    QListWidget::item {{
        padding: 6px;
        margin: 1px 3px;
        border-radius: 6px;
    }}

    QTreeView::item:hover,
    QTableView::item:hover,
    QListWidget::item:hover {{
        background: {tokens.panel_hover};
    }}

    QTreeView::item:selected,
    QTableView::item:selected,
    QListWidget::item:selected {{
        background: {tokens.selection};
        color: {tokens.text};
        border-left: 2px solid {tokens.accent};
    }}

    QHeaderView::section {{
        background: {header_bg};
        color: {tokens.text_muted};
        border: none;
        border-bottom: 1px solid {tokens.border_soft};
        border-right: 1px solid {tokens.border_soft};
        padding: 8px 10px;
        font-weight: 600;
    }}

    QHeaderView#repoTreeHeaderSurface::section {{
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 {glass_bg},
            stop:1 {tokens.panel_alt}
        );
        color: {tokens.text_soft};
        border: none;
        border-bottom: 1px solid {tokens.border_soft};
        padding: 8px 10px 8px 10px;
        font-size: 8.6pt;
        font-weight: 700;
    }}

    QTableCornerButton::section {{
        background: {tokens.panel_alt};
        border: none;
        border-right: 1px solid {tokens.border_soft};
        border-bottom: 1px solid {tokens.border_soft};
    }}

    QTabWidget::pane {{
        top: -1px;
    }}

    QTabBar::tab {{
        background: {tokens.panel_alt};
        color: {tokens.text_muted};
        border: 1px solid {tokens.border_soft};
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 7px 12px;
        margin-right: 3px;
    }}

    QTabBar::tab:hover {{
        color: {tokens.text};
        background: {panel_hover_soft};
        border: 1px solid {tokens.border};
        border-bottom: none;
    }}

    QTabBar::tab:selected {{
        color: {tokens.text};
        background: {tokens.panel};
        border: 1px solid {tokens.border};
        border-bottom: 1px solid {tokens.panel};
    }}

    QPlainTextEdit#previewCodeSurface,
    QPlainTextEdit#statsTextSurface,
    QPlainTextEdit#logTextSurface,
    QPlainTextEdit#fileSummarySurface {{
        background: {tokens.code_bg};
        color: {tokens.code_text};
        border: 1px solid {tokens.border};
        border-radius: 11px;
        selection-background-color: {tokens.selection};
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
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 {tokens.dock_title_bg},
            stop:1 {tokens.toolbar_bg}
        );
        color: {tokens.text};
        border-top: 1px solid {tokens.bevel_light};
        border-bottom: 1px solid {chrome_border};
        padding: 8px 12px;
    }}

    QDockWidget::close-button,
    QDockWidget::float-button {{
        border: 1px solid transparent;
        border-radius: 6px;
        background: transparent;
    }}

    QDockWidget::close-button:hover,
    QDockWidget::float-button:hover {{
        background: {tokens.panel_hover};
        border: 1px solid {tokens.border_soft};
    }}

    QStatusBar {{
        background: {tokens.toolbar_bg};
        color: {tokens.text_muted};
        border-top: 1px solid {tokens.border};
        padding: 3px 4px;
    }}

    QLabel#statusActivitySurface,
    QLabel#statusToolSurface,
    QLabel#statusRepoSurface,
    QLabel#statusScopeSurface,
    QLabel#statusSummarySurface {{
        color: {tokens.text_soft};
        padding: 1px 6px;
    }}

    QProgressBar#statusProgressSurface {{
        background: {tokens.panel};
        border: 1px solid {tokens.border_soft};
        border-radius: 8px;
        min-height: 9px;
        max-height: 9px;
        text-align: center;
    }}

    QProgressBar#statusProgressSurface::chunk {{
        background: {tokens.accent};
        border-radius: 7px;
    }}

    QScrollBar:vertical,
    QScrollBar:horizontal {{
        background: transparent;
        border: none;
        margin: 1px;
    }}

    QScrollBar:vertical {{
        width: 10px;
    }}

    QScrollBar:horizontal {{
        height: 10px;
    }}

    QScrollBar::handle:vertical,
    QScrollBar::handle:horizontal {{
        background: {tokens.scrollbar};
        border-radius: 4px;
        border: 1px solid {soft_border};
        min-width: 24px;
        min-height: 24px;
    }}

    QScrollBar::handle:vertical:hover,
    QScrollBar::handle:horizontal:hover {{
        background: {tokens.scrollbar_hover};
    }}

    QScrollBar::add-line,
    QScrollBar::sub-line,
    QScrollBar::add-page,
    QScrollBar::sub-page {{
        background: transparent;
        border: none;
        width: 0;
        height: 0;
    }}

    QSplitter::handle {{
        background: {splitter_soft};
        margin: 2px;
    }}

    QSplitter::handle:horizontal {{
        width: 3px;
    }}

    QSplitter::handle:vertical {{
        height: 3px;
    }}

    QTreeView#repoTreeSurface QScrollBar:vertical {{
        margin: 5px 2px 5px 0;
    }}

    QTreeView#repoTreeSurface QScrollBar::handle:vertical {{
        background: {tokens.scrollbar};
        border: 1px solid {tokens.border_soft};
        border-radius: 4px;
        min-height: 22px;
    }}

    QTreeView#repoTreeSurface QScrollBar::handle:vertical:hover {{
        background: {tokens.scrollbar_hover};
        border: 1px solid {accent_line};
    }}

    QLabel#heroTitleLabel {{
        color: {tokens.text};
        font-size: 14.8pt;
        font-weight: 700;
    }}

    QLabel#subtitleLabel,
    QLabel#workspaceMutedLabel,
    QLabel#panelMutedLabel,
    QLabel#svgMetaLabel,
    QLabel#svgHintLabel,
    QLabel#secondaryMetaLabel {{
        color: {tokens.text_muted};
        font-size: 10pt;
    }}

    QLabel#toolbarSectionCaption {{
        color: {tokens.text_soft};
        font-size: 9pt;
        font-weight: 700;
        letter-spacing: 1.0px;
        padding-left: 2px;
    }}

    QLabel#heroMetaPill,
    QLabel#panelPill,
    QLabel#toolbarPill,
    QLabel#statusPill {{
        background: {soft_accent};
        color: {tokens.accent_hover};
        border: 1px solid {tokens.border_strong};
        border-radius: 999px;
        padding: 2px 9px;
        font-size: 10pt;
        font-weight: 700;
    }}

    QLabel#svgStatusLabel {{
        color: {tokens.accent_hover};
        font-size: 10pt;
        font-weight: 600;
    }}

    QLabel#accentValueLabel {{
        color: {tokens.accent_hover};
        font-size: 16pt;
        font-weight: 700;
    }}

    QLabel#metricTitleLabel {{
        color: {tokens.text_soft};
        font-size: 9.5pt;
        font-weight: 700;
    }}

    QLabel#metricCaptionLabel {{
        color: {tokens.text_muted};
        font-size: 9.5pt;
    }}

    QLabel#sectionTitleLabel {{
        color: {tokens.text};
        font-size: 11pt;
        font-weight: 700;
    }}

    QFrame#accentBar {{
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 {accent_line},
            stop:0.6 {tokens.accent},
            stop:1 {tokens.accent_hover}
        );
        border: none;
        border-radius: 2px;
    }}
    """
    # Shared glass base first; repo-analyzer-specific skin rules remain as top-level overrides.
    return f"{build_shared_glass_stylesheet('silver_frost_cyan')}\n{local_styles}"


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
