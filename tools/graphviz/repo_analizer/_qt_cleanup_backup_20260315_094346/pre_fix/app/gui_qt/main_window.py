from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path

from PySide6.QtCore import QSettings, Qt, QThread, QUrl
from PySide6.QtGui import QAction, QDesktopServices, QFont, QKeySequence, QStandardItem, QStandardItemModel, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDockWidget,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
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
    QHeaderView,
)

from app.backend import AnalyzerBackend, PreviewData, SearchResult
from app.config import APP_TITLE, DEFAULT_MAX_RESULTS
from app.helpers import human_size, now_str

from .effects import apply_shadow, fade_in
from .skins import ORANGE_EMBER, SkinTokens, apply_skin, get_skin, list_skins
from .widgets import AccentButton, PanelCard, install_hover_raise
from .workers import IndexWorker, SearchWorker

ORG_NAME = 'Hitech'
APP_NAME = 'RepoAnalyzerQt'
ROLE_RELPATH = Qt.UserRole + 1
ROLE_ABSPATH = Qt.UserRole + 2
ROLE_NODE_KIND = Qt.UserRole + 3
ROLE_RESULT_LINE = Qt.UserRole + 4


class RepoAnalyzerMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings(ORG_NAME, APP_NAME)
        self.backend = AnalyzerBackend()
        self._skin_tokens: SkinTokens = get_skin(self.settings.value('skin_name', ORANGE_EMBER.name))
        self._repo_path = self.backend.settings.get('last_repo', '') or 'F:/repos/hitech-os/tools/graphviz/repo_analizer'
        self.index_data: dict = {'root': '', 'files': {}, 'folder_counts': {}, 'top_level_counts': {}, 'ext_counts': {}, 'dependents': {}, 'stats': {}}
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
        self._toolbar_buttons: list[AccentButton] = []
        self._panel_cards: list[PanelCard] = []

        self.setWindowTitle(f'{APP_TITLE} • Qt Edition')
        self.resize(1680, 1020)
        self.setDockNestingEnabled(True)
        self.setAnimated(True)

        self._build_toolbar()
        self._build_central()
        self._build_docks()
        self._build_status_bar()
        self._build_menu()
        self._restore_ui_state()
        self.apply_selected_skin(self._skin_tokens.name)
        self.log('Listo. Qt shell conectado al backend real.')

        if self._repo_path and Path(self._repo_path).exists():
            self.start_indexing(auto=True)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar('MainToolbar', self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        title_wrap = QWidget(self)
        title_layout = QVBoxLayout(title_wrap)
        title_layout.setContentsMargins(0, 0, 12, 0)
        title_layout.setSpacing(0)
        title = QLabel('Repo Analyzer', title_wrap)
        title.setStyleSheet('font-size: 16pt; font-weight: 700;')
        subtitle = QLabel('GitKraken-ish + backend real + skins enchufables', title_wrap)
        subtitle.setObjectName('subtitleLabel')
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        toolbar.addWidget(title_wrap)

        accent_bar = QFrame(self)
        accent_bar.setObjectName('accentBar')
        accent_bar.setFixedSize(4, 40)
        toolbar.addWidget(accent_bar)

        self.repo_combo = QComboBox(self)
        self.repo_combo.setEditable(True)
        self.repo_combo.setMinimumWidth(470)
        self.repo_combo.addItems(self.backend.settings.get('recent_repos', []))
        self.repo_combo.setCurrentText(self._repo_path)
        toolbar.addWidget(self.repo_combo)

        browse_btn = AccentButton('Browse', self._skin_tokens, self)
        browse_btn.clicked.connect(self.choose_repo)
        toolbar.addWidget(browse_btn)
        self._toolbar_buttons.append(browse_btn)

        reindex_btn = AccentButton('Reindex', self._skin_tokens, self)
        reindex_btn.clicked.connect(self.start_indexing)
        toolbar.addWidget(reindex_btn)
        self._toolbar_buttons.append(reindex_btn)

        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText('Search repo, symbols, imports, paths...')
        self.search_box.setMinimumWidth(320)
        self.search_box.returnPressed.connect(self.start_search)
        toolbar.addWidget(self.search_box)

        search_btn = AccentButton('Search', self._skin_tokens, self)
        search_btn.clicked.connect(self.start_search)
        toolbar.addWidget(search_btn)
        self._toolbar_buttons.append(search_btn)

        toolbar.addSeparator()

        self.quick_filter_combo = QComboBox(self)
        self.quick_filter_combo.currentIndexChanged.connect(self.on_quick_filter_selected)
        toolbar.addWidget(self.quick_filter_combo)

        self.ext_combo = QComboBox(self)
        self.ext_combo.currentIndexChanged.connect(self.on_filter_inputs_changed)
        toolbar.addWidget(self.ext_combo)

        self.sort_combo = QComboBox(self)
        self.sort_combo.addItems(['path', 'modified', 'size', 'ext'])
        toolbar.addWidget(self.sort_combo)

        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        self.skin_combo = QComboBox(self)
        for skin in list_skins():
            self.skin_combo.addItem(skin.display_name, skin.name)
        self.skin_combo.currentIndexChanged.connect(self.on_skin_combo_changed)
        toolbar.addWidget(self.skin_combo)

    def _build_central(self) -> None:
        central = QWidget(self)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(10)

        splitter = QSplitter(Qt.Vertical, central)
        outer.addWidget(splitter)

        preview_card = PanelCard(self._skin_tokens, accent=True, parent=splitter)
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(18, 16, 18, 16)
        preview_layout.setSpacing(10)

        preview_header_row = QHBoxLayout()
        self.preview_title_label = QLabel('Sin archivo seleccionado')
        self.preview_title_label.setStyleSheet('font-size: 13pt; font-weight: 700;')
        preview_header_row.addWidget(self.preview_title_label)
        preview_header_row.addStretch(1)

        self.open_system_btn = AccentButton('Abrir con sistema', self._skin_tokens, preview_card)
        self.open_system_btn.clicked.connect(self.open_current_preview_with_system)
        preview_header_row.addWidget(self.open_system_btn)
        self._toolbar_buttons.append(self.open_system_btn)

        self.bookmark_btn = AccentButton('Bookmark', self._skin_tokens, preview_card)
        self.bookmark_btn.clicked.connect(self.add_current_preview_bookmark)
        preview_header_row.addWidget(self.bookmark_btn)
        self._toolbar_buttons.append(self.bookmark_btn)

        preview_layout.addLayout(preview_header_row)

        self.preview = QPlainTextEdit(preview_card)
        self.preview.setReadOnly(True)
        self.preview.setLineWrapMode(QPlainTextEdit.NoWrap)
        code_font = QFont('Consolas', 10)
        code_font.setStyleHint(QFont.Monospace)
        self.preview.setFont(code_font)
        preview_layout.addWidget(self.preview)

        insights_card = PanelCard(self._skin_tokens, accent=False, parent=splitter)
        insights_layout = QVBoxLayout(insights_card)
        insights_layout.setContentsMargins(18, 16, 18, 16)
        insights_layout.setSpacing(12)

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
        self.insights_tabs.addTab(self.log_text, 'Log')
        self.insights_tabs.addTab(self.imports_tree, 'Imports')
        self.insights_tabs.addTab(self.dependents_tree, 'Dependents')
        insights_layout.addWidget(self.insights_tabs)

        splitter.addWidget(preview_card)
        splitter.addWidget(insights_card)
        splitter.setSizes([700, 280])

        self._panel_cards.extend([preview_card, insights_card])
        self.setCentralWidget(central)

    def _build_docks(self) -> None:
        self.explorer_dock = self._make_dock('Explorer', Qt.LeftDockWidgetArea)
        self.results_dock = self._make_dock('Results', Qt.BottomDockWidgetArea)
        self.filters_dock = self._make_dock('Filters', Qt.RightDockWidgetArea)

        explorer_card = PanelCard(self._skin_tokens, accent=True, parent=self.explorer_dock)
        explorer_layout = QVBoxLayout(explorer_card)
        explorer_layout.setContentsMargins(14, 14, 14, 14)
        explorer_layout.setSpacing(10)

        self.repo_tree = QTreeWidget(explorer_card)
        self.repo_tree.setHeaderLabels(['Repositorio'])
        self.repo_tree.setAlternatingRowColors(True)
        self.repo_tree.setAnimated(True)
        self.repo_tree.setIndentation(22)
        self.repo_tree.setUniformRowHeights(False)
        self.repo_tree.itemSelectionChanged.connect(self.on_tree_selection_changed)
        self.repo_tree.itemDoubleClicked.connect(self.on_tree_double_click)
        explorer_layout.addWidget(self.repo_tree)
        self.explorer_dock.setWidget(explorer_card)
        self._panel_cards.append(explorer_card)

        results_card = PanelCard(self._skin_tokens, accent=True, parent=self.results_dock)
        results_layout = QVBoxLayout(results_card)
        results_layout.setContentsMargins(14, 14, 14, 14)
        results_layout.setSpacing(10)
        self.results_table = QTableView(results_card)
        self.results_model = QStandardItemModel(0, 4, self.results_table)
        self.results_model.setHorizontalHeaderLabels([
            'Ruta completa sin extensión',
            'Fecha de modificación',
            'Tamaño',
            'Extensión',
        ])
        self.results_table.setModel(self.results_model)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSortingEnabled(True)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.results_table.clicked.connect(self.on_results_clicked)
        self.results_table.doubleClicked.connect(self.on_results_double_clicked)
        results_layout.addWidget(self.results_table)
        self.results_dock.setWidget(results_card)
        self._panel_cards.append(results_card)

        filters_card = PanelCard(self._skin_tokens, accent=False, parent=self.filters_dock)
        filters_layout = QVBoxLayout(filters_card)
        filters_layout.setContentsMargins(14, 14, 14, 14)
        filters_layout.setSpacing(10)

        filter_tabs = QTabWidget(filters_card)
        filters_layout.addWidget(filter_tabs)

        search_tab = QWidget(filter_tabs)
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
        self.search_now_btn = AccentButton('Buscar', self._skin_tokens, search_buttons_row)
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
        filter_tabs.addTab(search_tab, 'Search')

        bookmarks_tab = QWidget(filter_tabs)
        bookmarks_layout = QVBoxLayout(bookmarks_tab)
        bookmarks_layout.setContentsMargins(8, 8, 8, 8)
        bookmarks_layout.setSpacing(8)
        self.bookmarks_list = QListWidget(bookmarks_tab)
        self.bookmarks_list.itemDoubleClicked.connect(self.open_selected_bookmark)
        bookmarks_layout.addWidget(self.bookmarks_list)
        bm_btn_row = QWidget(bookmarks_tab)
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
        filter_tabs.addTab(bookmarks_tab, 'Bookmarks')

        self.filters_dock.setWidget(filters_card)
        self._panel_cards.append(filters_card)

        for dock in (self.explorer_dock, self.results_dock, self.filters_dock):
            apply_shadow(dock.widget(), self._skin_tokens.shadow, blur=24.0, y_offset=4.0)
            fade_in(dock.widget())

    def _build_status_bar(self) -> None:
        status = QStatusBar(self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedWidth(180)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        status.addPermanentWidget(self.progress_bar)
        self.status_summary = QLabel('0 archivos', self)
        status.addPermanentWidget(self.status_summary)
        status.showMessage('Ready. Daily-driver shell armed and dangerous.')
        self.setStatusBar(status)

    def _build_menu(self) -> None:
        menu = self.menuBar()
        file_menu = menu.addMenu('File')
        open_repo_action = QAction('Open Repo...', self)
        open_repo_action.setShortcut(QKeySequence.Open)
        open_repo_action.triggered.connect(self.choose_repo)
        file_menu.addAction(open_repo_action)
        file_menu.addSeparator()
        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menu.addMenu('View')
        skins_menu = view_menu.addMenu('Skins')
        for skin in list_skins():
            action = QAction(skin.display_name, self)
            action.triggered.connect(lambda checked=False, name=skin.name: self.apply_selected_skin(name))
            skins_menu.addAction(action)

        reset_layout = QAction('Reset Layout', self)
        reset_layout.triggered.connect(self.reset_layout)
        view_menu.addAction(reset_layout)

    def _restore_ui_state(self) -> None:
        geometry = self.settings.value('geometry')
        state = self.settings.value('window_state')
        if geometry:
            self.restoreGeometry(geometry)
        if state:
            self.restoreState(state)

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

    def _make_dock(self, title: str, area: Qt.DockWidgetArea) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setObjectName(f'dock_{title.lower()}')
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)
        self.addDockWidget(area, dock)
        return dock

    def apply_selected_skin(self, skin_name: str) -> None:
        app = QApplication.instance()
        if app is None:
            return
        self._skin_tokens = apply_skin(app, self, skin_name)
        self.settings.setValue('skin_name', skin_name)
        self._apply_skin_to_widgets()
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
        self.preview.setStyleSheet(code_qss)
        for text_box in (self.stats_text, self.log_text):
            text_box.setStyleSheet(code_qss)
        for dock in (self.explorer_dock, self.results_dock, self.filters_dock):
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
        thread.start()

    def _clear_index_thread(self) -> None:
        self._index_thread = None

    def clear_views_for_reindex(self) -> None:
        self.repo_tree.clear()
        self.results_model.removeRows(0, self.results_model.rowCount())
        self.imports_tree.clear()
        self.dependents_tree.clear()
        self.preview.clear()
        self.preview_title_label.setText('Sin archivo seleccionado')
        self.current_preview_rel = None
        self.current_preview_path = None
        self.search_results = []
        self._tree_items_by_relpath.clear()
        self.quick_filter_combo.blockSignals(True)
        self.quick_filter_combo.clear()
        self.quick_filter_combo.addItem(self.quick_filter_all_label)
        self.quick_filter_combo.blockSignals(False)

    def on_index_ready(self, payload: object) -> None:
        self.progress_bar.hide()
        self.progress_bar.setRange(0, 1)
        self.index_data = payload if isinstance(payload, dict) else {}
        total_files = len(self.index_data.get('files', {}))
        ext_counts = self.index_data.get('ext_counts', {})
        elapsed = self.index_data.get('stats', {}).get('elapsed_sec', 0)
        self.status_summary.setText(f'{total_files} archivos | {len(ext_counts)} extensiones')
        self.log(f'Index listo: {total_files} archivos en {elapsed}s')
        self.rebuild_repo_tree()
        self.rebuild_filter_values()
        self.rebuild_quick_filters()
        self.refresh_bookmarks_view()
        self.render_stats()
        self.statusBar().showMessage(f'Repo indexado: {self.index_data.get("root", "")}', 3000)

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

        folder_children: dict[str, set[str]] = {}
        file_children: dict[str, list[str]] = {}
        from collections import defaultdict as _dd
        folder_children = _dd(set)
        file_children = _dd(list)

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
        thread.start()

    def _clear_search_thread(self) -> None:
        self._search_thread = None

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
            ]
            for item in row_items:
                item.setEditable(False)
            row_items[0].setData(result.relpath, ROLE_RELPATH)
            row_items[0].setData(result.abspath, ROLE_ABSPATH)
            row_items[0].setData(result.line, ROLE_RESULT_LINE)
            self.results_model.appendRow(row_items)
        if self.search_results:
            self.statusBar().showMessage(f'{len(self.search_results)} resultados', 2500)
            self.log(f'Búsqueda terminada: {len(self.search_results)} resultados')
        else:
            self.statusBar().showMessage('Sin resultados', 2200)
            self.log('Búsqueda sin resultados')

    def show_preview_for_relpath(self, relpath: str, line: int = 0) -> None:
        try:
            preview = self.backend.build_preview(self.index_data, relpath, line=line)
        except Exception as e:
            QMessageBox.critical(self, APP_TITLE, f'No se pudo abrir preview:\n{e}')
            return
        self.current_preview_rel = preview.relpath
        self.current_preview_path = preview.abspath
        self.preview_title_label.setText(preview.title)
        self.preview.setPlainText(preview.rendered_text)
        self.populate_imports(preview)
        self.populate_dependents(preview)
        self.select_tree_item_by_relpath(relpath)
        if line > 0:
            self.jump_preview_to_line(line)
        else:
            cursor = self.preview.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self.preview.setTextCursor(cursor)

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
            lines.append(f'  {ext:<8} {count}')
        lines.extend(['', 'Top-level folders:'])
        for folder, count in data.get('top_level_counts', {}).items():
            lines.append(f'  {folder:<24} {count}')
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
        self.log(error_text)
        QMessageBox.critical(self, APP_TITLE, error_text)

    def log(self, msg: str) -> None:
        line = f'[{now_str()}] {msg}'
        self.log_text.appendPlainText(line)
        self.statusBar().showMessage(msg, 2200)

    def reset_layout(self) -> None:
        self.removeDockWidget(self.explorer_dock)
        self.removeDockWidget(self.results_dock)
        self.removeDockWidget(self.filters_dock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.explorer_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.results_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.filters_dock)
        self.resize(1680, 1020)
        self.statusBar().showMessage('Layout reseteado', 2200)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('window_state', self.saveState())
        self.settings.setValue('last_repo', self.repo_combo.currentText())
        self.backend.remember_repo(self.repo_combo.currentText())
        self.backend.update_filter_settings(self.folder_combo.currentText() or '(todo)', self.ext_combo.currentText() or '(todas)')
        super().closeEvent(event)
