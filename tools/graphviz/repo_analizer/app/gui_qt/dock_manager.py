from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from .effects import apply_shadow, fade_in
from .widgets import AccentButton, PanelCard

if TYPE_CHECKING:
    from .main_window import RepoAnalyzerMainWindow
    from .skins import SkinTokens


class DockManager:
    """Manages dock widgets setup and organization."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window

    def build_docks(self, skin_tokens: SkinTokens) -> None:
        """Create and configure all dock widgets."""
        self.main.explorer_dock = self._make_dock('Explorer', Qt.LeftDockWidgetArea)
        self.main.results_dock = self._make_dock('Results', Qt.BottomDockWidgetArea)
        self.main.inspector_dock = self._make_dock('Inspector', Qt.RightDockWidgetArea)
        self.main.bookmarks_dock = self._make_dock('Bookmarks', Qt.RightDockWidgetArea)

        # Build explorer dock (via tree controller)
        tree_filter_box, repo_tree = self.main.tree_controller.build_tree_dock_widget(skin_tokens)
        self.main.tree_filter_box = tree_filter_box
        self.main.repo_tree = repo_tree

        # Build results dock (via search controller)
        self.main.search_controller.build_results_dock_widget(skin_tokens)

        # Build inspector dock
        self._build_inspector_dock(skin_tokens)

        # Build bookmarks dock
        self._build_bookmarks_dock(skin_tokens)

        # Tabify and finalize
        self.main.tabifyDockWidget(self.main.inspector_dock, self.main.bookmarks_dock)
        self.main.inspector_dock.raise_()

        self.main.resizeDocks(
            [self.main.explorer_dock, self.main.inspector_dock],
            [360, 380],
            Qt.Horizontal
        )
        self.main.resizeDocks([self.main.results_dock], [320], Qt.Vertical)

        # Apply effects
        for dock in (self.main.explorer_dock, self.main.results_dock, self.main.inspector_dock, self.main.bookmarks_dock):
            apply_shadow(dock.widget(), skin_tokens.shadow, blur=24.0, y_offset=4.0)
            fade_in(dock.widget())

    def _build_inspector_dock(self, skin_tokens: SkinTokens) -> None:
        """Build inspector dock with search options and file tabs."""
        inspector_card = PanelCard(skin_tokens, accent=False, parent=self.main.inspector_dock)
        inspector_layout = QVBoxLayout(inspector_card)
        inspector_layout.setContentsMargins(14, 14, 14, 14)
        inspector_layout.setSpacing(10)

        from PySide6.QtWidgets import QTabWidget

        self.main.inspector_tabs = QTabWidget(inspector_card)
        inspector_layout.addWidget(self.main.inspector_tabs)

        # Search tab
        search_tab = self.main.search_controller.build_search_inspector_tab(
            self.main.inspector_tabs, skin_tokens
        )

        # File tab
        file_tab = QWidget(self.main.inspector_tabs)
        file_layout = QVBoxLayout(file_tab)
        file_layout.setContentsMargins(8, 8, 8, 8)
        file_layout.setSpacing(8)
        file_header = QLabel('Ficha del archivo', file_tab)
        file_header.setObjectName('heroTitleLabel')
        file_layout.addWidget(file_header)

        self.main.file_summary = QPlainTextEdit(file_tab)
        self.main.file_summary.setReadOnly(True)
        file_layout.addWidget(self.main.file_summary, 1)

        self.main.inspector_tabs.addTab(search_tab, 'Search Ops')
        self.main.inspector_tabs.addTab(file_tab, 'File')

        self.main.inspector_dock.setWidget(inspector_card)
        self.main._panel_cards.append(inspector_card)

    def _build_bookmarks_dock(self, skin_tokens: SkinTokens) -> None:
        """Build bookmarks dock."""
        bookmarks_card = PanelCard(skin_tokens, accent=False, parent=self.main.bookmarks_dock)
        bookmarks_layout = QVBoxLayout(bookmarks_card)
        bookmarks_layout.setContentsMargins(14, 14, 14, 14)
        bookmarks_layout.setSpacing(8)

        self.main.bookmarks_list = QListWidget(bookmarks_card)
        self.main.bookmarks_list.itemDoubleClicked.connect(self.main.open_selected_bookmark)
        bookmarks_layout.addWidget(self.main.bookmarks_list, 1)

        # Buttons
        bm_btn_row = QWidget(bookmarks_card)
        bm_btn_layout = QHBoxLayout(bm_btn_row)
        bm_btn_layout.setContentsMargins(0, 0, 0, 0)
        bm_btn_layout.setSpacing(8)

        self.main.bm_open_btn = AccentButton('Abrir', skin_tokens, bm_btn_row)
        self.main.bm_open_btn.clicked.connect(self.main.open_selected_bookmark)

        self.main.bm_remove_btn = AccentButton('Quitar', skin_tokens, bm_btn_row)
        self.main.bm_remove_btn.clicked.connect(self.main.remove_selected_bookmark)

        for btn in (self.main.bm_open_btn, self.main.bm_remove_btn):
            bm_btn_layout.addWidget(btn)
            self.main._toolbar_buttons.append(btn)

        bookmarks_layout.addWidget(bm_btn_row)
        self.main.bookmarks_dock.setWidget(bookmarks_card)
        self.main._panel_cards.append(bookmarks_card)

    def _make_dock(self, title: str, area) -> QDockWidget:
        """Create a dock widget."""
        dock = QDockWidget(title, self.main)
        dock.setObjectName(f'dock_{title.lower()}')
        dock.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
            | QDockWidget.DockWidgetClosable
        )
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.main.addDockWidget(area, dock)
        return dock
