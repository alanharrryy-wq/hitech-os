from __future__ import annotations

import os
import platform
import subprocess
from collections import defaultdict
from pathlib import Path

from PySide6.QtCore import QSettings, Qt, QThread
from PySide6.QtGui import QAction, QFont, QKeySequence, QStandardItem, QStandardItemModel, QTextCursor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QDockWidget,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTableView,
    QTabWidget,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.backend import AnalyzerBackend, PreviewData, SearchResult
from app.config import APP_TITLE, DEFAULT_MAX_RESULTS
from app.helpers import human_size, now_str

from .effects import apply_shadow, fade_in
from .skins import ORANGE_EMBER, SkinTokens, apply_skin, get_skin, list_skins
from .svg_viewer import SvgPreviewWindow
from .widgets import AccentButton, MetricTile, PanelCard, install_hover_raise
from .workers import IndexWorker, SearchWorker

ORG_NAME = 'Hitech'
APP_NAME = 'RepoAnalyzerQt'
STATE_VERSION = 3
ROLE_RELPATH = Qt.UserRole + 1
ROLE_ABSPATH = Qt.UserRole + 2
ROLE_NODE_KIND = Qt.UserRole + 3
ROLE_RESULT_LINE = Qt.UserRole + 4
ROLE_RESULT_MATCHES = Qt.UserRole + 5


class RepoAnalyzerMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings(ORG_NAME, APP_NAME)
        self.backend = AnalyzerBackend()
        self._skin_tokens: SkinTokens = get_skin(self.settings.value('skin_name', ORANGE_EMBER.name))
        self._repo_path = self.backend.settings.get('last_repo', '') or 'F:/repos/hitech-os/tools/graphviz/repo_analizer'
        self.index_data: dict = {
            'root': '',
            'files': {},
            'folder_counts': {},
            'top_level_counts': {},
            'ext_counts': {},
            'dependents': {},
            'stats': {},
        }
        self.search_results: list[SearchResult] = []
        self.current_preview_rel: str | None = None
        self.current_preview_path: str | None = None
        self.quick_filter_map: dict[str, str] = {}
        self.quick_filter_all_label = '(todas las carpetas)'
        self.quick_filter_manual_label = '(filtro manual)'
        self._tree_items_by_relpath: dict[str, QTreeWidgetItem] = {}
        self._tree_selection_guard = False
        self._index_thread: QThread | None = None
        self._search_thread: QThread | None = None
        self._index_worker: IndexWorker | None = None
        self._search_worker: SearchWorker | None = None
        self._toolbar_buttons: list[AccentButton] = []
        self._panel_cards: list[PanelCard] = []
        self._metric_tiles: list[MetricTile] = []
        self._preview_history: list[tuple[str, int]] = []
        self._preview_history_index = -1
        self._history_lock = False
        self._svg_window: SvgPreviewWindow | None = None
        self._restored_preview_once = False

        self.setWindowTitle(f'{APP_TITLE} • Ember Graph Workstation')
        self.resize(1760, 1080)
        self.setDockNestingEnabled(True)
        self.setAnimated(True)
        self.setDockOptions(
            QMainWindow.AllowNestedDocks
            | QMainWindow.AllowTabbedDocks
            | QMainWindow.AnimatedDocks
            | QMainWindow.GroupedDragging
        )
        self.setTabPosition(Qt.AllDockWidgetAreas, QTabWidget.North)
        self.setDocumentMode(True)

        self._build_toolbar()
        self._build_central()
        self._build_docks()
        self._build_status_bar()
        self._build_menu()
        self._restore_ui_state()
        self.apply_selected_skin(self._skin_tokens.name)
        self._update_preview_actions()
        self.log('Listo. Ember Graph Workstation conectado al backend real.')

        if self._repo_path and Path(self._repo_path).exists():
            self.start_indexing(auto=True)

    def _build_toolbar(self) -> None:
        self.workspace_toolbar = QToolBar('WorkspaceToolbar', self)
        self.workspace_toolbar.setObjectName('WorkspaceToolbar')
        self.workspace_toolbar.setMovable(False)
        self.workspace_toolbar.setFloatable(False)
        self.addToolBar(Qt.TopToolBarArea, self.workspace_toolbar)

        title_wrap = QWidget(self)
        title_layout = QVBoxLayout(title_wrap)
        title_layout.setContentsMargins(0, 0, 12, 0)
        title_layout.setSpacing(0)
        title = QLabel('Repo Analyzer', title_wrap)
        title.setObjectName('heroTitleLabel')
        subtitle = QLabel('Ember Graph Workstation • IDE shell premium para uso diario intenso', title_wrap)
        subtitle.setObjectName('subtitleLabel')
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        self.workspace_toolbar.addWidget(title_wrap)

        accent_bar = QFrame(self)
        accent_bar.setObjectName('accentBar')
        accent_bar.setFixedSize(4, 42)
        self.workspace_toolbar.addWidget(accent_bar)

        self.repo_combo = QComboBox(self)
        self.repo_combo.setEditable(True)
        self.repo_combo.setMinimumWidth(520)
        self.repo_combo.addItems(self.backend.settings.get('recent_repos', []))
        self.repo_combo.setCurrentText(self._repo_path)
        self.workspace_toolbar.addWidget(self.repo_combo)

        self.browse_btn = AccentButton('Browse', self._skin_tokens, self)
        self.browse_btn.clicked.connect(self.choose_repo)
        self.workspace_toolbar.addWidget(self.browse_btn)
        self._toolbar_buttons.append(self.browse_btn)

        self.reindex_btn = AccentButton('Reindex', self._skin_tokens, self, strong=True)
        self.reindex_btn.clicked.connect(self.start_indexing)
        self.workspace_toolbar.addWidget(self.reindex_btn)
        self._toolbar_buttons.append(self.reindex_btn)

        self.workspace_toolbar.addSeparator()

        self.back_action = QAction('Back', self)
        self.back_action.setShortcut(QKeySequence('Alt+Left'))
        self.back_action.triggered.connect(self.navigate_back)
        self.workspace_toolbar.addAction(self.back_action)

        self.forward_action = QAction('Forward', self)
        self.forward_action.setShortcut(QKeySequence('Alt+Right'))
        self.forward_action.triggered.connect(self.navigate_forward)
        self.workspace_toolbar.addAction(self.forward_action)

        self.bookmark_action = QAction('Bookmark', self)
        self.bookmark_action.triggered.connect(self.add_current_preview_bookmark)
        self.workspace_toolbar.addAction(self.bookmark_action)

        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.workspace_toolbar.addWidget(spacer)

        self.skin_combo = QComboBox(self)
        for skin in list_skins():
            self.skin_combo.addItem(skin.display_name, skin.name)
        self.skin_combo.currentIndexChanged.connect(self.on_skin_combo_changed)
        self.workspace_toolbar.addWidget(self.skin_combo)

        self.addToolBarBreak(Qt.TopToolBarArea)

        self.command_toolbar = QToolBar('CommandToolbar', self)
        self.command_toolbar.setObjectName('CommandToolbar')
        self.command_toolbar.setMovable(False)
        self.command_toolbar.setFloatable(False)
        self.addToolBar(Qt.TopToolBarArea, self.command_toolbar)

        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText('Search repo, symbols, imports, paths...')
        self.search_box.setMinimumWidth(420)
        self.search_box.returnPressed.connect(self.start_search)
        self.command_toolbar.addWidget(self.search_box)

        self.search_btn = AccentButton('Search', self._skin_tokens, self, strong=True)
        self.search_btn.clicked.connect(self.start_search)
        self.command_toolbar.addWidget(self.search_btn)
        self._toolbar_buttons.append(self.search_btn)

        self.quick_filter_combo = QComboBox(self)
        self.quick_filter_combo.setMinimumWidth(220)
        self.quick_filter_combo.currentIndexChanged.connect(self.on_quick_filter_selected)
        self.command_toolbar.addWidget(self.quick_filter_combo)

        self.ext_combo = QComboBox(self)
        self.ext_combo.setMinimumWidth(150)
        self.ext_combo.currentIndexChanged.connect(self.on_filter_inputs_changed)
        self.command_toolbar.addWidget(self.ext_combo)

        self.sort_combo = QComboBox(self)
        self.sort_combo.addItems(['path', 'modified', 'size', 'ext'])
        self.command_toolbar.addWidget(self.sort_combo)

        self.command_toolbar.addSeparator()

        self.focus_action = QAction('Focus Layout', self)
        self.focus_action.triggered.connect(self.apply_focus_layout)
        self.command_toolbar.addAction(self.focus_action)

        self.default_layout_action = QAction('Ember Layout', self)
        self.default_layout_action.triggered.connect(self.reset_layout)
        self.command_toolbar.addAction(self.default_layout_action)

    def _build_central(self) -> None:
        central = QWidget(self)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        hero_card = PanelCard(self._skin_tokens, accent=True, parent=central)
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(18, 16, 18, 16)
        hero_layout.setSpacing(12)

        hero_top = QHBoxLayout()
        hero_left = QVBoxLayout()
        hero_left.setContentsMargins(0, 0, 0, 0)
        hero_left.setSpacing(2)
        self.hero_repo_label = QLabel('Sin repo indexado', hero_card)
        self.hero_repo_label.setObjectName('heroTitleLabel')
        self.hero_scope_label = QLabel('Selecciona un repo para empezar a mapearlo', hero_card)
        self.hero_scope_label.setObjectName('workspaceMutedLabel')
        hero_left.addWidget(self.hero_repo_label)
        hero_left.addWidget(self.hero_scope_label)
        hero_top.addLayout(hero_left, 1)

        self.hero_mode_pill = QLabel('Workspace listo', hero_card)
        self.hero_mode_pill.setObjectName('heroMetaPill')
        hero_top.addWidget(self.hero_mode_pill, 0, Qt.AlignTop)
        hero_layout.addLayout(hero_top)

        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(10)
        self.metric_repo = MetricTile(self._skin_tokens, 'Repo', hero_card)
        self.metric_files = MetricTile(self._skin_tokens, 'Files', hero_card)
        self.metric_scope = MetricTile(self._skin_tokens, 'Scope', hero_card)
        self.metric_results = MetricTile(self._skin_tokens, 'Results', hero_card)
        for tile in (self.metric_repo, self.metric_files, self.metric_scope, self.metric_results):
            metrics_row.addWidget(tile, 1)
            self._metric_tiles.append(tile)
            self._panel_cards.append(tile)
        hero_layout.addLayout(metrics_row)
        outer.addWidget(hero_card)
        self._panel_cards.append(hero_card)

        self.central_splitter = QSplitter(Qt.Vertical, central)
        outer.addWidget(self.central_splitter, 1)

        preview_card = PanelCard(self._skin_tokens, accent=True, parent=self.central_splitter)
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(18, 16, 18, 16)
        preview_layout.setSpacing(10)

        preview_header = QHBoxLayout()
        preview_title_box = QVBoxLayout()
        preview_title_box.setContentsMargins(0, 0, 0, 0)
        preview_title_box.setSpacing(2)
        self.preview_title_label = QLabel('Sin archivo seleccionado', preview_card)
        self.preview_title_label.setObjectName('heroTitleLabel')
        self.preview_meta_label = QLabel('Selecciona algo del árbol o desde resultados', preview_card)
        self.preview_meta_label.setObjectName('panelMutedLabel')
        preview_title_box.addWidget(self.preview_title_label)
        preview_title_box.addWidget(self.preview_meta_label)
        preview_header.addLayout(preview_title_box, 1)

        self.open_system_btn = AccentButton('Abrir con sistema', self._skin_tokens, preview_card)
        self.open_system_btn.clicked.connect(self.open_current_preview_with_system)
        preview_header.addWidget(self.open_system_btn)
        self._toolbar_buttons.append(self.open_system_btn)

        self.open_svg_btn = AccentButton('SVG Workspace', self._skin_tokens, preview_card)
        self.open_svg_btn.clicked.connect(self.open_svg_workspace)
        preview_header.addWidget(self.open_svg_btn)
        self._toolbar_buttons.append(self.open_svg_btn)

        self.bookmark_btn = AccentButton('Bookmark', self._skin_tokens, preview_card)
        self.bookmark_btn.clicked.connect(self.add_current_preview_bookmark)
        preview_header.addWidget(self.bookmark_btn)
        self._toolbar_buttons.append(self.bookmark_btn)

        preview_layout.addLayout(preview_header)

        self.preview = QPlainTextEdit(preview_card)
        self.preview.setReadOnly(True)
        self.preview.setLineWrapMode(QPlainTextEdit.NoWrap)
        code_font = QFont('Consolas', 10)
        code_font.setStyleHint(QFont.Monospace)
        self.preview.setFont(code_font)
        preview_layout.addWidget(self.preview, 1)

        self.preview_hint_label = QLabel('Doble clic en árbol o resultados para abrir con tu sistema. Alt+Left / Alt+Right para navegar.', preview_card)
        self.preview_hint_label.setObjectName('panelMutedLabel')
        preview_layout.addWidget(self.preview_hint_label)

        insights_card = PanelCard(self._skin_tokens, accent=False, parent=self.central_splitter)
        insights_layout = QVBoxLayout(insights_card)
        insights_layout.setContentsMargins(18, 16, 18, 16)
        insights_layout.setSpacing(10)

        insights_header = QHBoxLayout()
        insights_title = QLabel('Inspector central', insights_card)
        insights_title.setObjectName('heroTitleLabel')
        insights_header.addWidget(insights_title)
        insights_header.addStretch(1)
        self.insights_pill = QLabel('Stats • Imports • Dependents • Log', insights_card)
        self.insights_pill.setObjectName('panelPill')
        insights_header.addWidget(self.insights_pill)
        insights_layout.addLayout(insights_header)

        self.insights_tabs = QTabWidget(insights_card)

        self.stats_text = QPlainTextEdit(insights_card)
        self.stats_text.setReadOnly(True)
        self.log_text = QPlainTextEdit(insights_card)
        self.log_text.setReadOnly(True)

        self.imports_tree = QTreeWidget(insights_card)
        self.imports_tree.setHeaderLabels(['Import', 'Resuelto'])
        self.imports_tree.itemDoubleClicked.connect(self.on_import_double_click)

        self.dependents_tree = QTreeWidget(insights_card)
        self.dependents_tree.setHeaderLabels(['Archivo dependiente'])
        self.dependents_tree.itemDoubleClicked.connect(self.on_dependent_double_click)

        self.insights_tabs.addTab(self.stats_text, 'Stats')
        self.insights_tabs.addTab(self.imports_tree, 'Imports')
        self.insights_tabs.addTab(self.dependents_tree, 'Dependents')
        self.insights_tabs.addTab(self.log_text, 'Log')
        insights_layout.addWidget(self.insights_tabs, 1)

        self.central_splitter.addWidget(preview_card)
        self.central_splitter.addWidget(insights_card)
        self.central_splitter.setSizes([760, 300])

        self._panel_cards.extend([preview_card, insights_card])
        self.setCentralWidget(central)

    def _build_docks(self) -> None:
        self.explorer_dock = self._make_dock('Explorer', Qt.LeftDockWidgetArea)
        self.results_dock = self._make_dock('Results', Qt.BottomDockWidgetArea)
        self.inspector_dock = self._make_dock('Inspector', Qt.RightDockWidgetArea)
        self.bookmarks_dock = self._make_dock('Bookmarks', Qt.RightDockWidgetArea)

        explorer_card = PanelCard(self._skin_tokens, accent=True, parent=self.explorer_dock)
        explorer_layout = QVBoxLayout(explorer_card)
        explorer_layout.setContentsMargins(14, 14, 14, 14)
        explorer_layout.setSpacing(10)
        self.tree_filter_box = QLineEdit(explorer_card)
        self.tree_filter_box.setPlaceholderText('Filtrar árbol por nombre o ruta...')
        self.tree_filter_box.textChanged.connect(self.on_tree_filter_changed)
        explorer_layout.addWidget(self.tree_filter_box)
        self.repo_tree = QTreeWidget(explorer_card)
        self.repo_tree.setHeaderLabels(['Repositorio'])
        self.repo_tree.setAlternatingRowColors(True)
        self.repo_tree.setAnimated(True)
        self.repo_tree.setIndentation(22)
        self.repo_tree.itemSelectionChanged.connect(self.on_tree_selection_changed)
        self.repo_tree.itemDoubleClicked.connect(self.on_tree_double_click)
        explorer_layout.addWidget(self.repo_tree, 1)
        self.explorer_dock.setWidget(explorer_card)
        self._panel_cards.append(explorer_card)

        results_card = PanelCard(self._skin_tokens, accent=True, parent=self.results_dock)
        results_layout = QVBoxLayout(results_card)
        results_layout.setContentsMargins(14, 14, 14, 14)
        results_layout.setSpacing(10)
        self.results_table = QTableView(results_card)
        self.results_model = QStandardItemModel(0, 6, self.results_table)
        self.results_model.setHorizontalHeaderLabels([
            'Ruta',
            'Modificado',
            'Tamaño',
            'Extensión',
            'Hits',
            'Snippet',
        ])
        self.results_table.setModel(self.results_model)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSortingEnabled(False)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.results_table.horizontalHeader().setStretchLastSection(False)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.results_table.clicked.connect(self.on_results_clicked)
        self.results_table.doubleClicked.connect(self.on_results_double_clicked)
        results_layout.addWidget(self.results_table, 1)
        self.results_dock.setWidget(results_card)
        self._panel_cards.append(results_card)

        inspector_card = PanelCard(self._skin_tokens, accent=False, parent=self.inspector_dock)
        inspector_layout = QVBoxLayout(inspector_card)
        inspector_layout.setContentsMargins(14, 14, 14, 14)
        inspector_layout.setSpacing(10)
        self.inspector_tabs = QTabWidget(inspector_card)
        inspector_layout.addWidget(self.inspector_tabs)

        search_tab = QWidget(self.inspector_tabs)
        search_form = QFormLayout(search_tab)
        search_form.setContentsMargins(8, 8, 8, 8)
        search_form.setSpacing(10)

        self.folder_combo = QComboBox(search_tab)
        self.folder_combo.currentIndexChanged.connect(self.on_filter_inputs_changed)
        search_form.addRow('Carpeta', self.folder_combo)

        self.case_check = QCheckBox('Case sensitive', search_tab)
        self.regex_check = QCheckBox('Regex', search_tab)
        self.word_check = QCheckBox('Whole word', search_tab)
        self.names_only_check = QCheckBox('Solo nombres', search_tab)
        self.include_hidden_check = QCheckBox('Incluir ocultos', search_tab)
        self.include_hidden_check.toggled.connect(self.on_include_hidden_changed)

        checks_wrap = QWidget(search_tab)
        checks_layout = QVBoxLayout(checks_wrap)
        checks_layout.setContentsMargins(0, 0, 0, 0)
        checks_layout.setSpacing(6)
        for chk in (self.case_check, self.regex_check, self.word_check, self.names_only_check, self.include_hidden_check):
            checks_layout.addWidget(chk)
        search_form.addRow('Opciones', checks_wrap)

        self.max_results_spin = QSpinBox(search_tab)
        self.max_results_spin.setRange(50, 10000)
        self.max_results_spin.setSingleStep(50)
        self.max_results_spin.setValue(DEFAULT_MAX_RESULTS)
        search_form.addRow('Máx. resultados', self.max_results_spin)

        search_buttons_row = QWidget(search_tab)
        row_layout = QHBoxLayout(search_buttons_row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)
        self.search_now_btn = AccentButton('Buscar', self._skin_tokens, search_buttons_row, strong=True)
        self.search_now_btn.clicked.connect(self.start_search)
        self.clear_search_btn = AccentButton('Limpiar', self._skin_tokens, search_buttons_row)
        self.clear_search_btn.clicked.connect(self.clear_search)
        self.export_btn = AccentButton('Exportar', self._skin_tokens, search_buttons_row)
        self.export_btn.clicked.connect(self.export_results)
        self.open_repo_btn = AccentButton('Abrir carpeta', self._skin_tokens, search_buttons_row)
        self.open_repo_btn.clicked.connect(self.open_current_repo_folder)
        for btn in (self.search_now_btn, self.clear_search_btn, self.export_btn, self.open_repo_btn):
            row_layout.addWidget(btn)
            self._toolbar_buttons.append(btn)
        search_form.addRow(search_buttons_row)

        file_tab = QWidget(self.inspector_tabs)
        file_layout = QVBoxLayout(file_tab)
        file_layout.setContentsMargins(8, 8, 8, 8)
        file_layout.setSpacing(8)
        file_header = QLabel('Ficha del archivo', file_tab)
        file_header.setObjectName('heroTitleLabel')
        file_layout.addWidget(file_header)
        self.file_summary = QPlainTextEdit(file_tab)
        self.file_summary.setReadOnly(True)
        file_layout.addWidget(self.file_summary, 1)

        self.inspector_tabs.addTab(search_tab, 'Search Ops')
        self.inspector_tabs.addTab(file_tab, 'File')
        self.inspector_dock.setWidget(inspector_card)
        self._panel_cards.append(inspector_card)

        bookmarks_card = PanelCard(self._skin_tokens, accent=False, parent=self.bookmarks_dock)
        bookmarks_layout = QVBoxLayout(bookmarks_card)
        bookmarks_layout.setContentsMargins(14, 14, 14, 14)
        bookmarks_layout.setSpacing(8)
        self.bookmarks_list = QListWidget(bookmarks_card)
        self.bookmarks_list.itemDoubleClicked.connect(self.open_selected_bookmark)
        bookmarks_layout.addWidget(self.bookmarks_list, 1)
        bm_btn_row = QWidget(bookmarks_card)
        bm_btn_layout = QHBoxLayout(bm_btn_row)
        bm_btn_layout.setContentsMargins(0, 0, 0, 0)
        bm_btn_layout.setSpacing(8)
        self.bm_open_btn = AccentButton('Abrir', self._skin_tokens, bm_btn_row)
        self.bm_open_btn.clicked.connect(self.open_selected_bookmark)
        self.bm_remove_btn = AccentButton('Quitar', self._skin_tokens, bm_btn_row)
        self.bm_remove_btn.clicked.connect(self.remove_selected_bookmark)
        for btn in (self.bm_open_btn, self.bm_remove_btn):
            bm_btn_layout.addWidget(btn)
            self._toolbar_buttons.append(btn)
        bookmarks_layout.addWidget(bm_btn_row)
        self.bookmarks_dock.setWidget(bookmarks_card)
        self._panel_cards.append(bookmarks_card)

        self.tabifyDockWidget(self.inspector_dock, self.bookmarks_dock)
        self.inspector_dock.raise_()
        self.resizeDocks([self.explorer_dock, self.inspector_dock], [360, 380], Qt.Horizontal)
        self.resizeDocks([self.results_dock], [320], Qt.Vertical)

        for dock in (self.explorer_dock, self.results_dock, self.inspector_dock, self.bookmarks_dock):
            apply_shadow(dock.widget(), self._skin_tokens.shadow, blur=24.0, y_offset=4.0)
            fade_in(dock.widget())

    def _build_status_bar(self) -> None:
        status = QStatusBar(self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedWidth(180)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        status.addPermanentWidget(self.progress_bar)
        self.status_scope_label = QLabel('scope: repo completo', self)
        status.addPermanentWidget(self.status_scope_label)
        self.status_summary = QLabel('0 archivos', self)
        status.addPermanentWidget(self.status_summary)
        status.showMessage('Ready. Ember Graph shell armed and clean.', 2200)
        self.setStatusBar(status)

    def _build_menu(self) -> None:
        menu = self.menuBar()

        file_menu = menu.addMenu('File')
        open_repo_action = QAction('Open Repo...', self)
        open_repo_action.setShortcut(QKeySequence.Open)
        open_repo_action.triggered.connect(self.choose_repo)
        file_menu.addAction(open_repo_action)

        export_action = QAction('Export Results...', self)
        export_action.triggered.connect(self.export_results)
        file_menu.addAction(export_action)
        file_menu.addSeparator()

        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        workspace_menu = menu.addMenu('Workspace')
        save_workspace = QAction('Save Current Layout', self)
        save_workspace.triggered.connect(self.save_current_layout_snapshot)
        workspace_menu.addAction(save_workspace)

        restore_workspace = QAction('Restore Saved Layout', self)
        restore_workspace.triggered.connect(self.restore_saved_layout_snapshot)
        workspace_menu.addAction(restore_workspace)

        reset_layout = QAction('Reset to Ember Layout', self)
        reset_layout.triggered.connect(self.reset_layout)
        workspace_menu.addAction(reset_layout)

        focus_layout = QAction('Apply Focus Layout', self)
        focus_layout.triggered.connect(self.apply_focus_layout)
        workspace_menu.addAction(focus_layout)

        view_menu = menu.addMenu('View')
        skins_menu = view_menu.addMenu('Skins')
        for skin in list_skins():
            action = QAction(skin.display_name, self)
            action.triggered.connect(lambda checked=False, name=skin.name: self.apply_selected_skin(name))
            skins_menu.addAction(action)

        view_menu.addSeparator()
        for dock in (self.explorer_dock, self.results_dock, self.inspector_dock, self.bookmarks_dock):
            view_menu.addAction(dock.toggleViewAction())
        view_menu.addSeparator()
        view_menu.addAction(self.workspace_toolbar.toggleViewAction())
        view_menu.addAction(self.command_toolbar.toggleViewAction())

        navigate_menu = menu.addMenu('Navigate')
        navigate_menu.addAction(self.back_action)
        navigate_menu.addAction(self.forward_action)

        open_svg_action = QAction('Open SVG Workspace', self)
        open_svg_action.triggered.connect(self.open_svg_workspace)
        navigate_menu.addAction(open_svg_action)

    def _restore_ui_state(self) -> None:
        geometry = self.settings.value('geometry')
        state = self.settings.value('window_state_v3')
        if geometry:
            self.restoreGeometry(geometry)
        if state:
            self.restoreState(state, STATE_VERSION)
        else:
            self.reset_layout(save_snapshot=False)

        folder_filter = self.backend.settings.get('last_folder_filter', '(todo)')
        ext_filter = self.backend.settings.get('last_ext_filter', '(todas)')
        self._pending_folder_filter = folder_filter
        self._pending_ext_filter = ext_filter

        skin_name = self._skin_tokens.name
        idx = self.skin_combo.findData(skin_name)
        if idx >= 0:
            self.skin_combo.setCurrentIndex(idx)
        self.repo_combo.setCurrentText(str(self._repo_path))

        self.quick_filter_combo.clear()
        self.quick_filter_combo.addItem(self.quick_filter_all_label)
        self.ext_combo.clear()
        self.ext_combo.addItems(['(todas)', 'TS/JS', '(sin extensión)'])
        self.folder_combo.clear()
        self.folder_combo.addItem('(todo)')
        self.refresh_bookmarks_view()

        splitter_sizes = self.settings.value('central_splitter_sizes')
        if isinstance(splitter_sizes, list) and splitter_sizes:
            try:
                self.central_splitter.setSizes([int(x) for x in splitter_sizes])
            except Exception:
                pass

        self._update_metric_cards_idle()

    def _make_dock(self, title: str, area: Qt.DockWidgetArea) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setObjectName(f'dock_{title.lower()}')
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.addDockWidget(area, dock)
        return dock

    def apply_selected_skin(self, skin_name: str) -> None:
        app = QApplication.instance()
        if app is None:
            return
        self._skin_tokens = apply_skin(app, self, skin_name)
        self.settings.setValue('skin_name', skin_name)
        self._apply_skin_to_widgets()
        if self._svg_window is not None:
            self._svg_window.set_skin(self._skin_tokens)
        self.statusBar().showMessage(f'Skin aplicada: {self._skin_tokens.display_name}', 2400)

    def _apply_skin_to_widgets(self) -> None:
        palette = self._skin_tokens
        for card in self._panel_cards:
            card.set_skin(palette)
        for button in self._toolbar_buttons:
            button.set_skin(palette)
            install_hover_raise(button, 1.5)
        code_qss = (
            f"QPlainTextEdit {{ background: {palette.code_bg}; color: {palette.code_text}; "
            f"selection-background-color: {palette.selection}; border: 1px solid {palette.border}; }}"
        )
        for text_box in (self.preview, self.stats_text, self.log_text, self.file_summary):
            text_box.setStyleSheet(code_qss)
        for dock in (self.explorer_dock, self.results_dock, self.inspector_dock, self.bookmarks_dock):
            apply_shadow(dock.widget(), palette.shadow, blur=24.0, y_offset=4.0)

    def on_skin_combo_changed(self, index: int) -> None:
        skin_name = self.skin_combo.itemData(index)
        if isinstance(skin_name, str):
            self.apply_selected_skin(skin_name)

    def choose_repo(self) -> None:
        start_dir = str(self.repo_combo.currentText() or Path.home())
        folder = QFileDialog.getExistingDirectory(self, 'Selecciona repo', start_dir)
        if folder:
            self.repo_combo.setCurrentText(folder)
            self.backend.remember_repo(folder)
            self.refresh_bookmarks_view()
            self.start_indexing()

    def start_indexing(self, auto: bool = False) -> None:
        repo = self.repo_combo.currentText().strip()
        if not repo:
            if not auto:
                QMessageBox.warning(self, APP_TITLE, 'Primero elige una carpeta de repo.')
            return
        repo_path = Path(repo)
        if not repo_path.exists() or not repo_path.is_dir():
            QMessageBox.critical(self, APP_TITLE, 'La ruta del repo no existe o no es una carpeta.')
            return
        if self._index_thread is not None:
            QMessageBox.information(self, APP_TITLE, 'Ya hay un indexado en progreso.')
            return

        self.backend.remember_repo(repo)
        self.refresh_bookmarks_view()
        self.clear_views_for_reindex()
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)
        self.statusBar().showMessage('Indexando repo…')
        self.hero_repo_label.setText(Path(repo).name or repo)
        self.hero_scope_label.setText(repo)
        self.hero_mode_pill.setText('Indexando workspace')
        self.log(f'Indexando: {repo_path}')

        thread = QThread(self)
        worker = IndexWorker(self.backend, repo, self.include_hidden_check.isChecked())
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self.statusBar().showMessage)
        worker.finished.connect(self.on_index_ready)
        worker.error.connect(self.on_worker_error)
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_index_thread)
        self._index_thread = thread
        self._index_worker = worker
        thread.start()

    def _clear_index_thread(self) -> None:
        self._index_thread = None
        self._index_worker = None

    def clear_views_for_reindex(self) -> None:
        self.repo_tree.clear()
        self.results_model.removeRows(0, self.results_model.rowCount())
        self.imports_tree.clear()
        self.dependents_tree.clear()
        self.preview.clear()
        self.file_summary.clear()
        self.preview_title_label.setText('Sin archivo seleccionado')
        self.preview_meta_label.setText('Selecciona algo del árbol o desde resultados')
        self.current_preview_rel = None
        self.current_preview_path = None
        self.search_results = []
        self._tree_items_by_relpath.clear()
        self.quick_filter_combo.blockSignals(True)
        self.quick_filter_combo.clear()
        self.quick_filter_combo.addItem(self.quick_filter_all_label)
        self.quick_filter_combo.blockSignals(False)
        self._update_preview_actions()
        self._update_metric_cards_idle()

    def on_index_ready(self, payload: object) -> None:
        self.progress_bar.hide()
        self.progress_bar.setRange(0, 1)
        self.index_data = payload if isinstance(payload, dict) else {}
        total_files = len(self.index_data.get('files', {}))
        ext_counts = self.index_data.get('ext_counts', {})
        elapsed = self.index_data.get('stats', {}).get('elapsed_sec', 0)
        self.status_summary.setText(f'{total_files} archivos | {len(ext_counts)} extensiones')
        self.hero_mode_pill.setText('Workspace indexado')
        self.log(f'Index listo: {total_files} archivos en {elapsed}s')
        self.rebuild_repo_tree()
        self.rebuild_filter_values()
        self.rebuild_quick_filters()
        self.refresh_bookmarks_view()
        self.render_stats()
        self._update_metric_cards_after_index()
        self.statusBar().showMessage(f'Repo indexado: {self.index_data.get("root", "")}', 3000)

        last_preview = self.settings.value('last_preview_rel', '')
        if not self._restored_preview_once and isinstance(last_preview, str) and last_preview in self.index_data.get('files', {}):
            self._restored_preview_once = True
            self.show_preview_for_relpath(last_preview, add_history=False)

    def rebuild_repo_tree(self) -> None:
        self.repo_tree.clear()
        self._tree_items_by_relpath.clear()
        repo_root = self.index_data.get('root', '')
        if not repo_root:
            return
        root_label = Path(repo_root).name or repo_root
        root_item = QTreeWidgetItem([root_label])
        root_item.setData(0, ROLE_NODE_KIND, 'root')
        root_item.setExpanded(True)
        self.repo_tree.addTopLevelItem(root_item)

        folder_children: dict[str, set[str]] = defaultdict(set)
        file_children: dict[str, list[str]] = defaultdict(list)

        for rel in self.index_data.get('files', {}).keys():
            parts = rel.split('/')
            if len(parts) == 1:
                file_children[''].append(rel)
                continue
            for depth in range(1, len(parts)):
                folder_rel = '/'.join(parts[:depth])
                parent_rel = '/'.join(parts[:depth - 1]) if depth > 1 else ''
                folder_children[parent_rel].add(folder_rel)
            file_children['/'.join(parts[:-1])].append(rel)

        def insert_branch(parent_item: QTreeWidgetItem, parent_rel: str, depth: int) -> None:
            child_folders = sorted(folder_children.get(parent_rel, set()), key=lambda x: Path(x).name.lower())
            child_files = sorted(file_children.get(parent_rel, []), key=lambda x: Path(x).name.lower())
            for folder_rel in child_folders:
                item = QTreeWidgetItem([Path(folder_rel).name])
                item.setData(0, ROLE_RELPATH, folder_rel)
                item.setData(0, ROLE_NODE_KIND, 'folder')
                item.setExpanded(depth < 1)
                parent_item.addChild(item)
                self._tree_items_by_relpath[folder_rel] = item
                insert_branch(item, folder_rel, depth + 1)
            for file_rel in child_files:
                info = self.index_data['files'][file_rel]
                item = QTreeWidgetItem([Path(file_rel).name])
                item.setData(0, ROLE_RELPATH, file_rel)
                item.setData(0, ROLE_ABSPATH, info['abspath'])
                item.setData(0, ROLE_NODE_KIND, 'file')
                parent_item.addChild(item)
                self._tree_items_by_relpath[file_rel] = item

        insert_branch(root_item, '', 0)
        self.repo_tree.expandItem(root_item)
        self.repo_tree.resizeColumnToContents(0)
        if self.tree_filter_box.text().strip():
            self.on_tree_filter_changed(self.tree_filter_box.text())

    def rebuild_filter_values(self) -> None:
        folders = ['(todo)', *sorted(self.index_data.get('folder_counts', {}).keys())]
        self.folder_combo.blockSignals(True)
        self.folder_combo.clear()
        self.folder_combo.addItems(folders)
        existing = getattr(self, '_pending_folder_filter', self.backend.settings.get('last_folder_filter', '(todo)'))
        self.folder_combo.setCurrentText(existing if existing in folders else '(todo)')
        self.folder_combo.blockSignals(False)

        detected_exts = sorted([ext for ext in self.index_data.get('ext_counts', {}).keys() if ext], key=str.lower)
        exts = ['(todas)', 'TS/JS', '(sin extensión)', *detected_exts]
        self.ext_combo.blockSignals(True)
        self.ext_combo.clear()
        self.ext_combo.addItems(exts)
        current_ext = getattr(self, '_pending_ext_filter', self.backend.settings.get('last_ext_filter', '(todas)'))
        self.ext_combo.setCurrentText(current_ext if current_ext in exts else '(todas)')
        self.ext_combo.blockSignals(False)
        self.on_filter_inputs_changed()

    def rebuild_quick_filters(self) -> None:
        counts = self.index_data.get('top_level_counts', {})
        values = [self.quick_filter_all_label]
        self.quick_filter_map = {self.quick_filter_all_label: '(todo)'}
        for folder, count in list(counts.items())[:30]:
            label = f'{folder} ({count})'
            values.append(label)
            self.quick_filter_map[label] = folder
        self.quick_filter_combo.blockSignals(True)
        self.quick_filter_combo.clear()
        self.quick_filter_combo.addItems(values)
        self.quick_filter_combo.blockSignals(False)
        self.sync_quick_filter_combo()

    def sync_quick_filter_combo(self) -> None:
        current_folder = self.folder_combo.currentText() or '(todo)'
        for label, folder in self.quick_filter_map.items():
            if folder == current_folder:
                self.quick_filter_combo.setCurrentText(label)
                return
        if current_folder not in ('', '(todo)'):
            if self.quick_filter_combo.findText(self.quick_filter_manual_label) < 0:
                self.quick_filter_combo.insertItem(1, self.quick_filter_manual_label)
            self.quick_filter_combo.setCurrentText(self.quick_filter_manual_label)
        else:
            self.quick_filter_combo.setCurrentText(self.quick_filter_all_label)

    def on_quick_filter_selected(self) -> None:
        label = self.quick_filter_combo.currentText().strip() or self.quick_filter_all_label
        folder = self.quick_filter_map.get(label, '(todo)')
        self.folder_combo.setCurrentText(folder)
        self.on_filter_inputs_changed()

    def on_filter_inputs_changed(self) -> None:
        folder = self.folder_combo.currentText() or '(todo)'
        ext = self.ext_combo.currentText() or '(todas)'
        self.backend.update_filter_settings(folder, ext)
        self.sync_quick_filter_combo()
        scope = 'todo el repo' if folder == '(todo)' else folder
        self.status_scope_label.setText(f'scope: {scope}')
        self.metric_scope.set_data(scope, f'ext: {ext}')
        if folder == '(todo)':
            self.statusBar().showMessage('Filtro de carpeta: todo el repo', 1600)
        else:
            self.statusBar().showMessage(f'Filtro de carpeta activo: {folder}', 1600)

    def start_search(self) -> None:
        if not self.index_data.get('files'):
            QMessageBox.warning(self, APP_TITLE, 'Primero indexa un repo.')
            return
        if self._search_thread is not None:
            QMessageBox.information(self, APP_TITLE, 'Ya hay una búsqueda en progreso.')
            return

        query = self.search_box.text().strip()
        folder = self.folder_combo.currentText() or '(todo)'
        ext_filter = self.ext_combo.currentText() or '(todas)'
        sort_mode = self.sort_combo.currentText() or 'path'
        max_results = max(1, int(self.max_results_spin.value() or DEFAULT_MAX_RESULTS))
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)
        self.statusBar().showMessage('Buscando…')
        self.hero_mode_pill.setText('Search pipeline activo')
        self.log(
            f"Buscar: '{query or '(vacío)'}' | folder={folder} | ext={ext_filter} | "
            f"regex={self.regex_check.isChecked()} | names_only={self.names_only_check.isChecked()}"
        )
        self.backend.remember_search(query)
        self.backend.update_filter_settings(folder, ext_filter)

        thread = QThread(self)
        worker = SearchWorker(
            self.backend,
            dict(self.index_data),
            query,
            folder,
            ext_filter,
            sort_mode,
            self.case_check.isChecked(),
            self.regex_check.isChecked(),
            self.word_check.isChecked(),
            self.names_only_check.isChecked(),
            max_results,
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self.statusBar().showMessage)
        worker.finished.connect(self.on_search_ready)
        worker.error.connect(self.on_worker_error)
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_search_thread)
        self._search_thread = thread
        self._search_worker = worker
        thread.start()

    def _clear_search_thread(self) -> None:
        self._search_thread = None
        self._search_worker = None

    def on_search_ready(self, results_obj: object) -> None:
        self.progress_bar.hide()
        self.progress_bar.setRange(0, 1)
        self.search_results = list(results_obj) if isinstance(results_obj, list) else []
        self.results_model.removeRows(0, self.results_model.rowCount())
        for result in self.search_results:
            row_items = [
                QStandardItem(result.display_path),
                QStandardItem(result.modified),
                QStandardItem(human_size(result.size)),
                QStandardItem(result.ext),
                QStandardItem(str(result.matches)),
                QStandardItem(result.snippet or ''),
            ]
            for item in row_items:
                item.setEditable(False)
            row_items[0].setData(result.relpath, ROLE_RELPATH)
            row_items[0].setData(result.abspath, ROLE_ABSPATH)
            row_items[0].setData(result.line, ROLE_RESULT_LINE)
            row_items[0].setData(result.matches, ROLE_RESULT_MATCHES)
            self.results_model.appendRow(row_items)
        self.results_table.resizeRowsToContents()
        count = len(self.search_results)
        self.metric_results.set_data(str(count), self.search_box.text().strip() or 'listado por filtros')
        self.hero_mode_pill.setText('Search lista para inspección')
        if self.search_results:
            self.results_dock.show()
            self.statusBar().showMessage(f'{count} resultados', 2500)
            self.log(f'Búsqueda terminada: {count} resultados')
        else:
            self.statusBar().showMessage('Sin resultados', 2200)
            self.log('Búsqueda sin resultados')

    def show_preview_for_relpath(self, relpath: str, line: int = 0, *, add_history: bool = True) -> None:
        try:
            preview = self.backend.build_preview(self.index_data, relpath, line=line)
        except Exception as e:
            QMessageBox.critical(self, APP_TITLE, f'No se pudo abrir preview:\n{e}')
            return
        self.current_preview_rel = preview.relpath
        self.current_preview_path = preview.abspath
        self.preview_title_label.setText(Path(preview.relpath).name)
        self.preview_meta_label.setText(preview.title)
        self.preview.setPlainText(preview.rendered_text)
        self.populate_imports(preview)
        self.populate_dependents(preview)
        self.populate_file_summary(preview)
        self.select_tree_item_by_relpath(relpath)
        if line > 0:
            self.jump_preview_to_line(line)
        else:
            cursor = self.preview.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self.preview.setTextCursor(cursor)
        self.settings.setValue('last_preview_rel', relpath)
        if add_history:
            self._push_preview_history(relpath, line)
        self._update_preview_actions()

    def populate_imports(self, preview: PreviewData) -> None:
        self.imports_tree.clear()
        for raw, resolved in preview.imports:
            item = QTreeWidgetItem([raw, resolved])
            item.setData(0, ROLE_RELPATH, resolved)
            self.imports_tree.addTopLevelItem(item)
        self.imports_tree.resizeColumnToContents(0)
        self.imports_tree.resizeColumnToContents(1)

    def populate_dependents(self, preview: PreviewData) -> None:
        self.dependents_tree.clear()
        for rel in preview.dependents:
            item = QTreeWidgetItem([rel])
            item.setData(0, ROLE_RELPATH, rel)
            self.dependents_tree.addTopLevelItem(item)
        self.dependents_tree.resizeColumnToContents(0)

    def populate_file_summary(self, preview: PreviewData) -> None:
        path = Path(preview.abspath)
        try:
            size = path.stat().st_size
        except Exception:
            size = 0
        lines = [
            f'Relpath: {preview.relpath}',
            f'Ruta: {preview.abspath}',
            f'Tamaño: {human_size(size)}',
            f'Extensión: {path.suffix.lower() or "(sin extensión)"}',
            f'Imports detectados: {len(preview.imports)}',
            f'Dependents detectados: {len(preview.dependents)}',
        ]
        if preview.line:
            lines.append(f'Línea objetivo: {preview.line}')
        if path.suffix.lower() == '.svg':
            lines.append('Tip: usa SVG Workspace para paneo y zoom fino.')
        self.file_summary.setPlainText('\n'.join(lines))

    def render_stats(self) -> None:
        data = self.index_data
        if not data.get('files'):
            self.stats_text.clear()
            return
        stats = data.get('stats', {})
        lines = [
            f"Repo: {data['root']}",
            f"Archivos indexados: {len(data['files'])}",
            f"Tiempo de indexado: {stats.get('elapsed_sec', 0)} s",
            '',
            'Extensiones:',
        ]
        for ext, count in data.get('ext_counts', {}).items():
            lines.append(f'  {ext:<12} {count}')
        lines.extend(['', 'Top-level folders:'])
        for folder, count in data.get('top_level_counts', {}).items():
            lines.append(f'  {folder:<28} {count}')
        lines.extend(['', 'Archivos más grandes:'])
        for item in stats.get('largest_files', []):
            lines.append(f"  {human_size(item['size']).rjust(8)}   {item['relpath']}")
        self.stats_text.setPlainText('\n'.join(lines))

    def refresh_bookmarks_view(self) -> None:
        self.bookmarks_list.clear()
        repo = self.repo_combo.currentText().strip()
        for rel in self.backend.get_repo_bookmarks(repo):
            self.bookmarks_list.addItem(rel)

    def add_current_preview_bookmark(self) -> None:
        if not self.current_preview_rel:
            return
        self.backend.add_bookmark(self.repo_combo.currentText(), self.current_preview_rel)
        self.refresh_bookmarks_view()
        self.log(f'Bookmark agregado: {self.current_preview_rel}')

    def open_selected_bookmark(self) -> None:
        item = self.bookmarks_list.currentItem()
        if not item:
            return
        self.show_preview_for_relpath(item.text())

    def remove_selected_bookmark(self) -> None:
        item = self.bookmarks_list.currentItem()
        if not item:
            return
        self.backend.remove_bookmark(self.repo_combo.currentText(), item.text())
        self.refresh_bookmarks_view()
        self.log(f'Bookmark removido: {item.text()}')

    def on_tree_selection_changed(self) -> None:
        if self._tree_selection_guard:
            return
        items = self.repo_tree.selectedItems()
        if not items:
            return
        item = items[0]
        if item.data(0, ROLE_NODE_KIND) != 'file':
            return
        relpath = item.data(0, ROLE_RELPATH)
        if isinstance(relpath, str) and relpath:
            self.show_preview_for_relpath(relpath)

    def on_tree_double_click(self, item: QTreeWidgetItem, _column: int) -> None:
        if item.data(0, ROLE_NODE_KIND) == 'file':
            path = item.data(0, ROLE_ABSPATH)
            if isinstance(path, str) and path:
                self.open_with_system(path)

    def on_results_clicked(self, index) -> None:
        if not index.isValid():
            return
        relpath = self.results_model.item(index.row(), 0).data(ROLE_RELPATH)
        line = self.results_model.item(index.row(), 0).data(ROLE_RESULT_LINE) or 0
        if isinstance(relpath, str) and relpath:
            self.show_preview_for_relpath(relpath, int(line))

    def on_results_double_clicked(self, index) -> None:
        if not index.isValid():
            return
        path = self.results_model.item(index.row(), 0).data(ROLE_ABSPATH)
        if isinstance(path, str) and path:
            self.open_with_system(path)

    def on_import_double_click(self, item: QTreeWidgetItem, _column: int) -> None:
        resolved = item.data(0, ROLE_RELPATH)
        if isinstance(resolved, str) and resolved:
            self.show_preview_for_relpath(resolved)

    def on_dependent_double_click(self, item: QTreeWidgetItem, _column: int) -> None:
        relpath = item.data(0, ROLE_RELPATH)
        if isinstance(relpath, str) and relpath:
            self.show_preview_for_relpath(relpath)

    def jump_preview_to_line(self, line: int) -> None:
        cursor = self.preview.textCursor()
        cursor.movePosition(QTextCursor.Start)
        for _ in range(max(0, line - 1)):
            cursor.movePosition(QTextCursor.Down)
        self.preview.setTextCursor(cursor)
        self.preview.centerCursor()

    def select_tree_item_by_relpath(self, relpath: str) -> None:
        item = self._tree_items_by_relpath.get(relpath)
        if item is None:
            return
        self._tree_selection_guard = True
        try:
            self.repo_tree.setCurrentItem(item)
            self.repo_tree.scrollToItem(item)
        finally:
            self._tree_selection_guard = False

    def clear_search(self) -> None:
        self.search_box.clear()
        self.results_model.removeRows(0, self.results_model.rowCount())
        self.search_results = []
        self.metric_results.set_data('0', 'sin resultados cacheados')
        self.statusBar().showMessage('Búsqueda limpia.', 1600)

    def export_results(self) -> None:
        if not self.search_results:
            QMessageBox.information(self, APP_TITLE, 'No hay resultados para exportar.')
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            'Exportar resultados',
            '',
            'CSV (*.csv);;JSON (*.json);;TXT (*.txt);;Todos (*.*)',
        )
        if not path:
            return
        try:
            self.backend.export_results(self.search_results, Path(path))
            self.log(f'Resultados exportados: {path}')
            QMessageBox.information(self, APP_TITLE, f'Exportado correctamente:\n{path}')
        except Exception as e:
            QMessageBox.critical(self, APP_TITLE, f'No se pudo exportar:\n{e}')

    def open_current_preview_with_system(self) -> None:
        if self.current_preview_path:
            self.open_with_system(self.current_preview_path)

    def open_current_repo_folder(self) -> None:
        repo = self.repo_combo.currentText().strip()
        if repo and Path(repo).exists():
            self.open_with_system(repo)

    def open_svg_workspace(self) -> None:
        if not self.current_preview_path:
            QMessageBox.information(self, APP_TITLE, 'Primero selecciona un archivo SVG.')
            return
        if Path(self.current_preview_path).suffix.lower() != '.svg':
            QMessageBox.information(self, APP_TITLE, 'El archivo actual no es .svg.')
            return
        if self._svg_window is None:
            self._svg_window = SvgPreviewWindow(self._skin_tokens, self)
        self._svg_window.set_skin(self._skin_tokens)
        self._svg_window.load_svg(self.current_preview_path, self.current_preview_rel or Path(self.current_preview_path).name)
        self._svg_window.show()
        self._svg_window.raise_()
        self._svg_window.activateWindow()

    def open_with_system(self, path: str) -> None:
        try:
            system = platform.system().lower()
            if system == 'windows':
                os.startfile(path)  # type: ignore[attr-defined]
            elif system == 'darwin':
                subprocess.Popen(['open', path])
            else:
                subprocess.Popen(['xdg-open', path])
        except Exception as e:
            QMessageBox.critical(self, APP_TITLE, f'No se pudo abrir con el sistema:\n{e}')

    def on_include_hidden_changed(self) -> None:
        if self.index_data.get('root'):
            self.statusBar().showMessage('Toggle de ocultos listo. Reindexa para aplicar.', 2200)

    def on_worker_error(self, error_text: str) -> None:
        self.progress_bar.hide()
        self.progress_bar.setRange(0, 1)
        self.hero_mode_pill.setText('Error en pipeline')
        self.log(error_text)
        QMessageBox.critical(self, APP_TITLE, error_text)

    def log(self, msg: str) -> None:
        line = f'[{now_str()}] {msg}'
        self.log_text.appendPlainText(line)
        self.statusBar().showMessage(msg, 2200)

    def reset_layout(self, save_snapshot: bool = True) -> None:
        for dock in (self.explorer_dock, self.results_dock, self.inspector_dock, self.bookmarks_dock):
            self.removeDockWidget(dock)
            dock.show()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.explorer_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.results_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.inspector_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.bookmarks_dock)
        self.tabifyDockWidget(self.inspector_dock, self.bookmarks_dock)
        self.inspector_dock.raise_()
        self.resizeDocks([self.explorer_dock, self.inspector_dock], [340, 380], Qt.Horizontal)
        self.resizeDocks([self.results_dock], [310], Qt.Vertical)
        self.central_splitter.setSizes([760, 300])
        self.statusBar().showMessage('Layout Ember Graph restaurado', 2200)
        if save_snapshot:
            self.save_current_layout_snapshot()

    def apply_focus_layout(self) -> None:
        self.explorer_dock.show()
        self.inspector_dock.show()
        self.results_dock.hide()
        self.bookmarks_dock.hide()
        self.resizeDocks([self.explorer_dock, self.inspector_dock], [280, 320], Qt.Horizontal)
        self.central_splitter.setSizes([880, 220])
        self.statusBar().showMessage('Focus layout aplicado', 2200)

    def save_current_layout_snapshot(self) -> None:
        self.settings.setValue('workspace_snapshot_state_v3', self.saveState(STATE_VERSION))
        self.settings.setValue('workspace_snapshot_splitter', self.central_splitter.sizes())
        self.statusBar().showMessage('Layout actual guardado', 2200)

    def restore_saved_layout_snapshot(self) -> None:
        state = self.settings.value('workspace_snapshot_state_v3')
        splitter_sizes = self.settings.value('workspace_snapshot_splitter')
        if not state:
            self.reset_layout(save_snapshot=False)
            return
        self.restoreState(state, STATE_VERSION)
        if isinstance(splitter_sizes, list) and splitter_sizes:
            try:
                self.central_splitter.setSizes([int(x) for x in splitter_sizes])
            except Exception:
                pass
        self.statusBar().showMessage('Layout guardado restaurado', 2200)

    def navigate_back(self) -> None:
        if self._preview_history_index <= 0:
            return
        self._preview_history_index -= 1
        relpath, line = self._preview_history[self._preview_history_index]
        self._history_lock = True
        try:
            self.show_preview_for_relpath(relpath, line, add_history=False)
        finally:
            self._history_lock = False
        self._update_preview_actions()

    def navigate_forward(self) -> None:
        if self._preview_history_index >= len(self._preview_history) - 1:
            return
        self._preview_history_index += 1
        relpath, line = self._preview_history[self._preview_history_index]
        self._history_lock = True
        try:
            self.show_preview_for_relpath(relpath, line, add_history=False)
        finally:
            self._history_lock = False
        self._update_preview_actions()

    def _push_preview_history(self, relpath: str, line: int) -> None:
        if self._history_lock:
            return
        entry = (relpath, line)
        if self._preview_history and self._preview_history_index >= 0 and self._preview_history[self._preview_history_index] == entry:
            return
        if self._preview_history_index < len(self._preview_history) - 1:
            self._preview_history = self._preview_history[: self._preview_history_index + 1]
        self._preview_history.append(entry)
        if len(self._preview_history) > 100:
            self._preview_history = self._preview_history[-100:]
        self._preview_history_index = len(self._preview_history) - 1
        self._update_preview_actions()

    def _update_preview_actions(self) -> None:
        has_preview = bool(self.current_preview_path)
        is_svg = bool(self.current_preview_path and Path(self.current_preview_path).suffix.lower() == '.svg')
        self.open_system_btn.setEnabled(has_preview)
        self.open_svg_btn.setEnabled(is_svg)
        self.bookmark_btn.setEnabled(has_preview)
        self.back_action.setEnabled(self._preview_history_index > 0)
        self.forward_action.setEnabled(self._preview_history_index < len(self._preview_history) - 1)
        self.bookmark_action.setEnabled(has_preview)

    def _update_metric_cards_idle(self) -> None:
        repo_name = Path(self.repo_combo.currentText().strip() or 'repo').name or 'repo'
        self.metric_repo.set_data(repo_name, 'aún sin indexado')
        self.metric_files.set_data('0', 'archivos en memoria')
        self.metric_scope.set_data('todo el repo', 'scope inicial')
        self.metric_results.set_data('0', 'sin búsqueda')

    def _update_metric_cards_after_index(self) -> None:
        repo_root = self.index_data.get('root', '')
        repo_name = Path(repo_root).name if repo_root else Path(self.repo_combo.currentText().strip() or 'repo').name
        total_files = len(self.index_data.get('files', {}))
        total_ext = len(self.index_data.get('ext_counts', {}))
        elapsed = self.index_data.get('stats', {}).get('elapsed_sec', 0)
        self.metric_repo.set_data(repo_name or 'repo', repo_root or 'ruta sin resolver')
        self.metric_files.set_data(str(total_files), f'{total_ext} extensiones • {elapsed}s')
        scope = self.folder_combo.currentText() or '(todo)'
        self.metric_scope.set_data('todo el repo' if scope == '(todo)' else scope, self.ext_combo.currentText() or '(todas)')
        self.metric_results.set_data(str(len(self.search_results)), self.search_box.text().strip() or 'sin query activa')

    def on_tree_filter_changed(self, text: str) -> None:
        needle = text.strip().lower()
        root = self.repo_tree.invisibleRootItem()
        for i in range(root.childCount()):
            self._filter_tree_item(root.child(i), needle)

    def _filter_tree_item(self, item: QTreeWidgetItem, needle: str) -> bool:
        own_text = item.text(0).lower()
        relpath = item.data(0, ROLE_RELPATH)
        rel_text = relpath.lower() if isinstance(relpath, str) else ''
        match = not needle or needle in own_text or needle in rel_text
        child_match = False
        for idx in range(item.childCount()):
            child_match = self._filter_tree_item(item.child(idx), needle) or child_match
        visible = match or child_match or item.data(0, ROLE_NODE_KIND) == 'root'
        item.setHidden(not visible)
        if child_match and needle:
            item.setExpanded(True)
        return visible

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('window_state_v3', self.saveState(STATE_VERSION))
        self.settings.setValue('central_splitter_sizes', self.central_splitter.sizes())
        self.settings.setValue('last_repo', self.repo_combo.currentText())
        self.settings.setValue('last_preview_rel', self.current_preview_rel or '')
        self.backend.remember_repo(self.repo_combo.currentText())
        self.backend.update_filter_settings(self.folder_combo.currentText() or '(todo)', self.ext_combo.currentText() or '(todas)')
        super().closeEvent(event)
