from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..widgets import AccentButton, PanelCard

if TYPE_CHECKING:
    from ..main_window import RepoAnalyzerMainWindow
    from ..skins import SkinTokens


class DockSectionFactory:
    """Build built-in dock content sections for the shell."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window

    def build_inspector_section(
        self,
        skin_tokens: SkinTokens,
        *,
        parent: QWidget | None = None,
    ) -> PanelCard:
        surface_parent = parent or self.main.inspector_dock
        inspector_card = PanelCard(skin_tokens, accent=False, parent=surface_parent)
        inspector_layout = QVBoxLayout(inspector_card)
        inspector_layout.setContentsMargins(14, 14, 14, 14)
        inspector_layout.setSpacing(10)

        from PySide6.QtWidgets import QTabWidget

        self.main.inspector_tabs = QTabWidget(inspector_card)
        self.main.inspector_tabs.setObjectName('inspectorTabsSurface')
        self.main.inspector_tabs.setProperty('visualRole', 'panel-surface')
        self.main.inspector_tabs.setProperty('visualTier', 'themed')
        inspector_layout.addWidget(self.main.inspector_tabs)

        search_tab = self.main.search_controller.build_search_inspector_tab(
            self.main.inspector_tabs,
            skin_tokens,
        )

        file_tab = QWidget(self.main.inspector_tabs)
        file_tab.setObjectName('fileInspectorSurface')
        file_tab.setProperty('visualRole', 'panel-surface')
        file_tab.setProperty('visualTier', 'themed')
        file_layout = QVBoxLayout(file_tab)
        file_layout.setContentsMargins(8, 8, 8, 8)
        file_layout.setSpacing(8)
        file_header = QLabel("Ficha del archivo", file_tab)
        file_header.setObjectName("heroTitleLabel")
        file_layout.addWidget(file_header)

        self.main.file_summary = QPlainTextEdit(file_tab)
        self.main.file_summary.setObjectName('fileSummarySurface')
        self.main.file_summary.setProperty('visualRole', 'summary-surface')
        self.main.file_summary.setProperty('codeSurface', True)
        self.main.file_summary.setReadOnly(True)
        file_layout.addWidget(self.main.file_summary, 1)

        self.main.inspector_tabs.addTab(search_tab, "Search Ops")
        self.main.inspector_tabs.addTab(file_tab, "File")
        return inspector_card

    def build_bookmarks_section(
        self,
        skin_tokens: SkinTokens,
        *,
        parent: QWidget | None = None,
    ) -> PanelCard:
        surface_parent = parent or self.main.bookmarks_dock
        bookmarks_card = PanelCard(skin_tokens, accent=False, parent=surface_parent)
        bookmarks_layout = QVBoxLayout(bookmarks_card)
        bookmarks_layout.setContentsMargins(14, 14, 14, 14)
        bookmarks_layout.setSpacing(8)

        self.main.bookmarks_list = QListWidget(bookmarks_card)
        self.main.bookmarks_list.setObjectName('bookmarksListSurface')
        self.main.bookmarks_list.setProperty('visualRole', 'summary-surface')
        self.main.bookmarks_list.setProperty('visualTier', 'themed')
        self.main.bookmarks_list.itemDoubleClicked.connect(self.main.open_selected_bookmark)
        bookmarks_layout.addWidget(self.main.bookmarks_list, 1)

        button_row = QWidget(bookmarks_card)
        button_row.setObjectName('bookmarksActionsSurface')
        button_row.setProperty('visualRole', 'panel-surface')
        button_row.setProperty('visualTier', 'themed')
        button_row_layout = QHBoxLayout(button_row)
        button_row_layout.setContentsMargins(0, 0, 0, 0)
        button_row_layout.setSpacing(8)

        self.main.bm_open_btn = AccentButton("Abrir", skin_tokens, button_row)
        self.main.bm_open_btn.clicked.connect(self.main.open_selected_bookmark)
        self.main.bm_remove_btn = AccentButton("Quitar", skin_tokens, button_row)
        self.main.bm_remove_btn.clicked.connect(self.main.remove_selected_bookmark)

        for button in (self.main.bm_open_btn, self.main.bm_remove_btn):
            button_row_layout.addWidget(button)

        bookmarks_layout.addWidget(button_row)
        return bookmarks_card
