from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QSettings, Qt, QThread
from PySide6.QtGui import QAction, QFont, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

try:
    from shiboken6 import isValid as qt_object_is_valid
except ImportError:  # pragma: no cover - PySide6 ships shiboken6
    def qt_object_is_valid(obj):
        return obj is not None

from app.backend import AnalyzerBackend
from app.config import APP_TITLE
from app.helpers import now_str

from .command_dispatcher import CommandDispatcher
from .commands import (
    AddBookmarkCommand,
    ExecuteSearchCommand,
    ExportResultsCommand,
    NavigateBackCommand,
    NavigateForwardCommand,
    OpenFileCommand,
    RemoveBookmarkCommand,
)
from .dock_manager import DockManager
from .event_bus import EventBus, Events
from .layout_manager import LayoutManager
from .navigation_controller import NavigationController
from .preview_controller import PreviewController
from .plugins import PluginManager
from .search_controller import SearchController
from .services import ServiceContainer
from .skins import ORANGE_EMBER, SkinTokens, apply_skin, get_skin, list_skins
from .svg_viewer import SvgPreviewWindow
from .toolbar_controller import ToolbarController
from .tree_controller import TreeController
from .ui_contribution_registry import UIContributionRegistry
from .widgets import MetricTile, PanelCard
from .workers import IndexWorker

ORG_NAME = 'Hitech'
APP_NAME = 'RepoAnalyzerQt'
STATE_VERSION = 3


class RepoAnalyzerMainWindow(QMainWindow):
    """Main window orchestrator using modular controllers."""

    def __init__(self) -> None:
        super().__init__()
        
        # Core setup
        self.settings = QSettings(ORG_NAME, APP_NAME)
        self.backend = AnalyzerBackend()
        self._skin_tokens: SkinTokens = get_skin(
            self.settings.value('skin_name', ORANGE_EMBER.name)
        )
        self.STATE_VERSION = STATE_VERSION
        
        # Repository state
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
        self.search_results: list = []
        
        # Preview and navigation state
        self.current_preview_rel: str | None = None
        self.current_preview_path: str | None = None
        
        # Quick filter state
        self.quick_filter_map: dict[str, str] = {}
        self.quick_filter_all_label = '(todas las carpetas)'
        self.quick_filter_manual_label = '(filtro manual)'
        
        # Threading
        self._index_thread: QThread | None = None
        self._index_worker: IndexWorker | None = None
        
        # UI collections
        self._toolbar_buttons: list = []
        self._panel_cards: list[PanelCard] = []
        self._metric_tiles: list[MetricTile] = []
        
        # UI state
        self._svg_window: SvgPreviewWindow | None = None
        self._restored_preview_once = False
        self._pending_folder_filter = '(todo)'
        self._pending_ext_filter = '(todas)'
        self._plugin_ui_applied = False
        self._menu_path_cache: dict[str, QMenu] = {}
        self._plugin_menu_actions: list[QAction] = []
        
        # Initialize controllers
        self.toolbar_controller = ToolbarController(self)
        self.tree_controller = TreeController(self)
        self.search_controller = SearchController(self)
        self.preview_controller = PreviewController(self)
        self.navigation_controller = NavigationController(self)
        self.dock_manager = DockManager(self)
        self.layout_manager = LayoutManager(self)
        
        # Initialize extensibility infrastructure
        self._initialize_extensibility()
        
        # Build UI
        self._setup_window()
        self._build_ui()
        self._finalize_setup()

    def _setup_window(self) -> None:
        """Configure main window properties."""
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

    def _build_ui(self) -> None:
        """Build all UI components."""
        self.toolbar_controller.build_toolbar()
        self._build_central()
        self.dock_manager.build_docks(self._skin_tokens)
        self._build_status_bar()
        self._build_menu()
        self._apply_plugin_ui_contributions()

    def _finalize_setup(self) -> None:
        """Finalize setup and restore state."""
        self.layout_manager.restore_ui_state()
        self.apply_selected_skin(self._skin_tokens.name)
        self._update_preview_actions()
        self.log('Listo. Ember Graph Workstation conectado al backend real.')

        if self._repo_path and Path(self._repo_path).exists():
            self.start_indexing(auto=True)

    def _initialize_extensibility(self) -> None:
        """
        Initialize extensibility infrastructure.
        
        Sets up:
        - Event Bus for loose coupling
        - Command Dispatcher for action encapsulation
        - Service Container for dependency injection
        - Plugin Manager for dynamic extensibility
        - Registers built-in commands
        """
        # Create core infrastructure
        self.event_bus = EventBus()
        self.command_dispatcher = CommandDispatcher()
        self.service_container = ServiceContainer()
        self.ui_contribution_registry = UIContributionRegistry()
        
        # Register services in container
        self.service_container.register('event_bus', self.event_bus)
        self.service_container.register('command_dispatcher', self.command_dispatcher)
        self.service_container.register('backend', self.backend)
        self.service_container.register('ui_contribution_registry', self.ui_contribution_registry)
        self.service_container.register('settings', self.settings)
        self.service_container.register('main_window', self)
        
        # Register controllers as services
        self.service_container.register('toolbar_controller', self.toolbar_controller)
        self.service_container.register('tree_controller', self.tree_controller)
        self.service_container.register('search_controller', self.search_controller)
        self.service_container.register('preview_controller', self.preview_controller)
        self.service_container.register('navigation_controller', self.navigation_controller)
        self.service_container.register('dock_manager', self.dock_manager)
        self.service_container.register('layout_manager', self.layout_manager)
        
        # Register built-in commands
        self._register_built_in_commands()
        
        # Initialize plugin manager
        self.plugin_manager = PluginManager(
            self.event_bus,
            self.command_dispatcher,
            self.service_container,
        )
        
        # Load plugins from plugins directory
        plugins_dir = Path(__file__).parent / 'plugins'
        if plugins_dir.exists():
            self.plugin_manager.load_plugins_from_directory(str(plugins_dir))
            self.plugin_manager.initialize_all()
    
    def _register_built_in_commands(self) -> None:
        """Register built-in commands for core functionality."""
        # File operations
        self.command_dispatcher.register(
            'open_file',
            OpenFileCommand(self.preview_controller),
        )
        
        # Search operations
        self.command_dispatcher.register(
            'execute_search',
            ExecuteSearchCommand(self.search_controller),
        )
        self.command_dispatcher.register(
            'export_results',
            ExportResultsCommand(self.search_controller),
        )
        
        # Navigation operations
        self.command_dispatcher.register(
            'navigate_back',
            NavigateBackCommand(self.navigation_controller),
        )
        self.command_dispatcher.register(
            'navigate_forward',
            NavigateForwardCommand(self.navigation_controller),
        )
        
        # Bookmark operations
        self.command_dispatcher.register(
            'add_bookmark',
            AddBookmarkCommand(self),
        )
        self.command_dispatcher.register(
            'remove_bookmark',
            RemoveBookmarkCommand(self),
        )

    def _apply_plugin_ui_contributions(self) -> None:
        """Apply declarative UI contributions registered by plugins."""
        if self._plugin_ui_applied:
            return

        registry = self.service_container.get('ui_contribution_registry')
        if registry is None:
            return

        for contribution in registry.get_dock_contributions():
            self.dock_manager.add_plugin_dock(contribution, self._skin_tokens)

        for contribution in registry.get_toolbar_contributions():
            self.toolbar_controller.add_plugin_action(contribution)

        self._plugin_menu_actions.clear()
        for contribution in registry.get_menu_contributions():
            menu = self._find_or_create_menu_path(contribution.menu_path)
            if menu is None or not self._is_menu_alive(menu):
                raise RuntimeError(
                    f"Could not resolve live menu path for plugin contribution '{contribution.contribution_id}'"
                )

            action = QAction(contribution.text, menu)
            action.setObjectName(
                f"plugin_menu_action_{self._sanitize_plugin_ui_name(contribution.contribution_id)}"
            )
            if contribution.shortcut:
                action.setShortcut(QKeySequence(contribution.shortcut))
            if contribution.tooltip:
                action.setToolTip(contribution.tooltip)
                action.setStatusTip(contribution.tooltip)
            action.triggered.connect(
                lambda checked=False, callback=contribution.callback: callback()
            )
            menu.addAction(action)
            self._plugin_menu_actions.append(action)

        self.menuBar().update()
        self._plugin_ui_applied = True

    def _reset_menu_runtime_state(self) -> None:
        """Reset runtime caches used to build and extend menus safely."""
        self._menu_path_cache.clear()
        self._plugin_menu_actions.clear()

    def _menu_cache_key(self, menu_path: str) -> str:
        parts = [part.strip() for part in menu_path.split('/') if part.strip()]
        return '/'.join(self._normalize_menu_text(part) for part in parts)

    def _remember_menu_path(self, menu_path: str, menu: QMenu) -> QMenu:
        """Store a strong reference to a menu path when the Qt object is alive."""
        key = self._menu_cache_key(menu_path)
        if key and self._is_menu_alive(menu):
            self._menu_path_cache[key] = menu
        return menu

    def _get_cached_menu(self, menu_path: str) -> QMenu | None:
        """Return a cached menu only if its underlying Qt object is still valid."""
        key = self._menu_cache_key(menu_path)
        if not key:
            return None

        menu = self._menu_path_cache.get(key)
        if self._is_menu_alive(menu):
            return menu

        self._menu_path_cache.pop(key, None)
        return None

    def _is_menu_alive(self, menu: QMenu | None) -> bool:
        """Check whether a QMenu wrapper still points to a live Qt object."""
        if menu is None:
            return False

        try:
            return bool(qt_object_is_valid(menu))
        except RuntimeError:
            return False

    def _find_or_create_menu_path(self, menu_path: str):
        """Find or create a nested menu path such as 'Tools/My Plugin'."""
        parts = [part.strip() for part in menu_path.split('/') if part.strip()]
        if not parts:
            raise ValueError('menu_path cannot be empty')

        current_menu = None
        current_path: list[str] = []

        for index, part in enumerate(parts):
            current_path.append(part)
            path_str = '/'.join(current_path)

            cached_menu = self._get_cached_menu(path_str)
            if cached_menu is not None:
                current_menu = cached_menu
                continue

            if index == 0:
                current_menu = self._find_or_create_top_level_menu(part)
            else:
                if current_menu is None or not self._is_menu_alive(current_menu):
                    raise RuntimeError(f"Parent menu became invalid while resolving '{menu_path}'")
                current_menu = self._find_or_create_sub_menu(current_menu, part)

            self._remember_menu_path(path_str, current_menu)

        if current_menu is None or not self._is_menu_alive(current_menu):
            raise RuntimeError(f"Menu path '{menu_path}' resolved to an invalid QMenu")

        return current_menu

    def _find_or_create_top_level_menu(self, title: str):
        """Find an existing top-level menu or create it."""
        normalized = self._normalize_menu_text(title)
        for action in self.menuBar().actions():
            menu = action.menu()
            if not self._is_menu_alive(menu):
                continue
            if self._normalize_menu_text(menu.title()) == normalized:
                return menu

        menu = QMenu(title, self.menuBar())
        self.menuBar().addMenu(menu)
        return menu

    def _find_or_create_sub_menu(self, parent_menu, title: str):
        """Find an existing submenu or create it under the given menu."""
        normalized = self._normalize_menu_text(title)
        for action in parent_menu.actions():
            menu = action.menu()
            if not self._is_menu_alive(menu):
                continue
            if self._normalize_menu_text(menu.title()) == normalized:
                return menu

        menu = QMenu(title, parent_menu)
        parent_menu.addMenu(menu)
        return menu

    def _normalize_menu_text(self, value: str) -> str:
        """Normalize menu titles for comparison."""
        return value.replace('&', '').strip().lower()

    def _sanitize_plugin_ui_name(self, value: str) -> str:
        """Create a safe object name fragment for plugin UI actions."""
        sanitized = ''.join(ch if ch.isalnum() else '_' for ch in value.strip().lower())
        return sanitized.strip('_') or 'plugin'

    def _build_central(self) -> None:
        """Build central widget with preview and inspector panels."""
        central = QWidget(self)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        # Hero card
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

        # Metrics
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

        # Central splitter with preview and inspector
        self.central_splitter = QSplitter(Qt.Vertical, central)
        outer.addWidget(self.central_splitter, 1)

        preview_card = self.preview_controller.build_preview_panel(self._skin_tokens, self.central_splitter)
        inspector_card = self.preview_controller.build_inspector_panel(self._skin_tokens, self.central_splitter)

        self.central_splitter.addWidget(preview_card)
        self.central_splitter.addWidget(inspector_card)
        self.central_splitter.setSizes([760, 300])

        self.setCentralWidget(central)

    def _build_status_bar(self) -> None:
        """Build status bar with progress indicator."""
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
        """Build application menu bar."""
        menu = self.menuBar()
        self._reset_menu_runtime_state()

        # File menu
        file_menu = menu.addMenu('File')
        self._remember_menu_path('File', file_menu)
        
        open_repo_action = file_menu.addAction('Open Repo...')
        open_repo_action.triggered.connect(self.choose_repo)

        export_action = file_menu.addAction('Export Results...')
        export_action.triggered.connect(self.search_controller.export_results)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)

        # Workspace menu
        workspace_menu = menu.addMenu('Workspace')
        self._remember_menu_path('Workspace', workspace_menu)
        
        save_workspace = workspace_menu.addAction('Save Current Layout')
        save_workspace.triggered.connect(self.layout_manager.save_current_layout_snapshot)

        restore_workspace = workspace_menu.addAction('Restore Saved Layout')
        restore_workspace.triggered.connect(self.layout_manager.restore_saved_layout_snapshot)

        reset_layout = workspace_menu.addAction('Reset to Ember Layout')
        reset_layout.triggered.connect(self.reset_layout)

        focus_layout = workspace_menu.addAction('Apply Focus Layout')
        focus_layout.triggered.connect(self.apply_focus_layout)

        # View menu
        view_menu = menu.addMenu('View')
        self._remember_menu_path('View', view_menu)
        skins_menu = view_menu.addMenu('Skins')
        self._remember_menu_path('View/Skins', skins_menu)
        for skin in list_skins():
            action = skins_menu.addAction(skin.display_name)
            action.triggered.connect(lambda checked=False, name=skin.name: self.apply_selected_skin(name))

        view_menu.addSeparator()
        for dock in (self.explorer_dock, self.results_dock, self.inspector_dock, self.bookmarks_dock):
            view_menu.addAction(dock.toggleViewAction())
        view_menu.addSeparator()
        view_menu.addAction(self.workspace_toolbar.toggleViewAction())
        view_menu.addAction(self.command_toolbar.toggleViewAction())

        # Navigate menu
        navigate_menu = menu.addMenu('Navigate')
        self._remember_menu_path('Navigate', navigate_menu)
        navigate_menu.addAction(self.back_action)
        navigate_menu.addAction(self.forward_action)

        open_svg_action = navigate_menu.addAction('Open SVG Workspace')
        open_svg_action.triggered.connect(self.preview_controller.open_svg_workspace)

    # ========== Index Operations ==========

    def choose_repo(self) -> None:
        """Open dialog to choose repository."""
        start_dir = str(self.repo_combo.currentText() or Path.home())
        folder = QFileDialog.getExistingDirectory(self, 'Selecciona repo', start_dir)
        if folder:
            self.repo_combo.setCurrentText(folder)
            self.backend.remember_repo(folder)
            self.refresh_bookmarks_view()
            self.start_indexing()

    def start_indexing(self, auto: bool = False) -> None:
        """Start repository indexing."""
        repo = self.repo_combo.currentText().strip()
        if not repo:
            if not auto:
                QMessageBox.warning(self, APP_TITLE, 'Ingresa una ruta de repo.')
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
        """Clear index thread reference."""
        self._index_thread = None
        self._index_worker = None

    def on_index_ready(self, payload: object) -> None:
        """Handle index completion."""
        self.progress_bar.hide()
        self.progress_bar.setRange(0, 1)
        self.index_data = payload if isinstance(payload, dict) else {}

        total_files = len(self.index_data.get('files', {}))
        ext_counts = self.index_data.get('ext_counts', {})
        elapsed = self.index_data.get('stats', {}).get('elapsed_sec', 0)

        self.status_summary.setText(f'{total_files} archivos | {len(ext_counts)} extensiones')
        self.hero_mode_pill.setText('Workspace indexado')
        self.log(f'Index listo: {total_files} archivos en {elapsed}s')

        self.tree_controller.rebuild_repo_tree()
        self.rebuild_filter_values()
        self.rebuild_quick_filters()
        self.refresh_bookmarks_view()
        self.render_stats()
        self._update_metric_cards_after_index()

        # Publish event for extensibility
        self.event_bus.publish(
            Events.INDEX_COMPLETED,
            {
                'root': self.index_data.get('root', ''),
                'file_count': total_files,
                'ext_count': len(ext_counts),
                'elapsed_sec': elapsed
            }
        )

        self.statusBar().showMessage(f'Repo indexado: {self.index_data.get("root", "")}', 3000)

        last_preview = self.settings.value('last_preview_rel', '')
        if (
            not self._restored_preview_once
            and isinstance(last_preview, str)
            and last_preview in self.index_data.get('files', {})
        ):
            self._restored_preview_once = True
            self.preview_controller.show_preview_for_relpath(last_preview, add_history=False)

    def clear_views_for_reindex(self) -> None:
        """Clear all views before reindexing."""
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
        self.tree_controller._tree_items_by_relpath.clear()

        self.quick_filter_combo.blockSignals(True)
        self.quick_filter_combo.clear()
        self.quick_filter_combo.addItem(self.quick_filter_all_label)
        self.quick_filter_combo.blockSignals(False)

        self._update_preview_actions()
        self._update_metric_cards_idle()

    # ========== Filter Operations ==========

    def rebuild_filter_values(self) -> None:
        """Rebuild folder and extension filter values."""
        folders = ['(todo)', *sorted(self.index_data.get('folder_counts', {}).keys())]
        self.folder_combo.blockSignals(True)
        self.folder_combo.clear()
        self.folder_combo.addItems(folders)
        existing = getattr(
            self, '_pending_folder_filter', 
            self.backend.settings.get('last_folder_filter', '(todo)')
        )
        self.folder_combo.setCurrentText(existing if existing in folders else '(todo)')
        self.folder_combo.blockSignals(False)

        detected_exts = sorted(
            [ext for ext in self.index_data.get('ext_counts', {}).keys() if ext],
            key=str.lower
        )
        exts = ['(todas)', 'TS/JS', '(sin extensión)', *detected_exts]
        self.ext_combo.blockSignals(True)
        self.ext_combo.clear()
        self.ext_combo.addItems(exts)
        current_ext = getattr(
            self, '_pending_ext_filter',
            self.backend.settings.get('last_ext_filter', '(todas)')
        )
        self.ext_combo.setCurrentText(current_ext if current_ext in exts else '(todas)')
        self.ext_combo.blockSignals(False)

        self.on_filter_inputs_changed()

    def rebuild_quick_filters(self) -> None:
        """Rebuild quick filter combo."""
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
        """Sync quick filter with folder filter."""
        current_folder = self.folder_combo.currentText() or '(todo)'
        for label, folder in self.quick_filter_map.items():
            if folder == current_folder:
                self.quick_filter_combo.setCurrentText(label)
                return

        if current_folder not in ('', '(todo)'):
            if self.quick_filter_combo.findText(self.quick_filter_manual_label) < 0:
                self.quick_filter_combo.addItem(self.quick_filter_manual_label)
            self.quick_filter_combo.setCurrentText(self.quick_filter_manual_label)
        else:
            self.quick_filter_combo.setCurrentText(self.quick_filter_all_label)

    def on_quick_filter_selected(self) -> None:
        """Handle quick filter selection."""
        label = self.quick_filter_combo.currentText().strip() or self.quick_filter_all_label
        folder = self.quick_filter_map.get(label, '(todo)')
        self.folder_combo.setCurrentText(folder)
        self.on_filter_inputs_changed()

    def on_filter_inputs_changed(self) -> None:
        """Handle filter input changes."""
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

    def on_include_hidden_changed(self) -> None:
        """Handle hidden files checkbox."""
        if self.index_data.get('root'):
            pass  # Could reindex if needed

    # ========== Search Operations ==========

    def start_search(self) -> None:
        """Start search with current parameters."""
        self.search_controller.start_search()

    # ========== Skin Management ==========

    def on_skin_combo_changed(self, index: int) -> None:
        """Handle skin combo change."""
        skin_name = self.skin_combo.itemData(index)
        if isinstance(skin_name, str):
            self.apply_selected_skin(skin_name)

    def apply_selected_skin(self, skin_name: str) -> None:
        """Apply skin to entire application."""
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
        """Apply skin tokens to all widgets."""
        palette = self._skin_tokens

        for card in self._panel_cards:
            card.set_skin(palette)

        self.toolbar_controller.apply_skin_to_buttons(palette)

        code_qss = (
            f"QPlainTextEdit {{ background: {palette.code_bg}; color: {palette.code_text}; "
            f"selection-background-color: {palette.selection}; border: 1px solid {palette.border}; }}"
        )
        for text_box in (self.preview, self.stats_text, self.log_text, self.file_summary):
            text_box.setStyleSheet(code_qss)

        from .effects import apply_shadow

        for dock in (self.explorer_dock, self.results_dock, self.inspector_dock, self.bookmarks_dock):
            apply_shadow(dock.widget(), palette.shadow, blur=24.0, y_offset=4.0)

    # ========== Preview and Navigation ==========

    def show_preview_for_relpath(self, relpath: str, line: int = 0, *, add_history: bool = True) -> None:
        """Show preview for a file (delegated to preview controller)."""
        self.preview_controller.show_preview_for_relpath(relpath, line, add_history=add_history)

    def navigate_back(self) -> None:
        """Navigate to previous preview."""
        self.navigation_controller.navigate_back()

    def navigate_forward(self) -> None:
        """Navigate to next preview."""
        self.navigation_controller.navigate_forward()

    def open_with_system(self, path: str) -> None:
        """Open path with system app."""
        self.preview_controller.open_with_system(path)

    def open_current_preview_with_system(self) -> None:
        """Open current preview with system app."""
        self.preview_controller.open_current_preview_with_system()

    def open_current_repo_folder(self) -> None:
        """Open current repo folder."""
        self.preview_controller.open_current_repo_folder()

    def open_svg_workspace(self) -> None:
        """Open SVG workspace."""
        self.preview_controller.open_svg_workspace()

    def open_selected_bookmark(self) -> None:
        """Open selected bookmark."""
        item = self.bookmarks_list.currentItem()
        if not item:
            return
        self.show_preview_for_relpath(item.text())

    def remove_selected_bookmark(self) -> None:
        """Remove selected bookmark."""
        item = self.bookmarks_list.currentItem()
        if not item:
            return
        self.backend.remove_bookmark(self.repo_combo.currentText(), item.text())
        self.refresh_bookmarks_view()
        self.log(f'Bookmark removido: {item.text()}')

    # ========== Bookmark Operations ==========

    def add_current_preview_bookmark(self) -> None:
        """Add current preview as bookmark."""
        if not self.current_preview_rel:
            return
        self.backend.add_bookmark(self.repo_combo.currentText(), self.current_preview_rel)
        self.refresh_bookmarks_view()
        self.log(f'Bookmark agregado: {self.current_preview_rel}')

    def refresh_bookmarks_view(self) -> None:
        """Refresh bookmarks list."""
        self.bookmarks_list.clear()
        repo = self.repo_combo.currentText().strip()
        for rel in self.backend.get_repo_bookmarks(repo):
            self.bookmarks_list.addItem(rel)

    # ========== Layout Operations ==========

    def reset_layout(self, save_snapshot: bool = True) -> None:
        """Reset to default layout."""
        self.layout_manager.reset_layout(save_snapshot)

    def apply_focus_layout(self) -> None:
        """Apply focus layout."""
        self.layout_manager.apply_focus_layout()

    # ========== UI Actions ==========

    def on_tree_selection_changed(self) -> None:
        """Delegated to tree controller."""
        self.tree_controller.on_tree_selection_changed()

    def on_tree_double_click(self, item, column: int) -> None:
        """Delegated to tree controller."""
        self.tree_controller.on_tree_double_click(item, column)

    def on_tree_filter_changed(self, text: str) -> None:
        """Delegated to tree controller."""
        self.tree_controller.on_tree_filter_changed(text)

    def on_results_clicked(self, index) -> None:
        """Delegated to search controller."""
        self.search_controller.on_results_clicked(index)

    def on_results_double_clicked(self, index) -> None:
        """Delegated to search controller."""
        self.search_controller.on_results_double_clicked(index)

    def on_import_double_click(self, item, column: int) -> None:
        """Delegated to preview controller."""
        self.preview_controller.on_import_double_click(item, column)

    def on_dependent_double_click(self, item, column: int) -> None:
        """Delegated to preview controller."""
        self.preview_controller.on_dependent_double_click(item, column)

    # ========== Worker Callbacks ==========

    def on_worker_error(self, error_text: str) -> None:
        """Handle worker error."""
        self.progress_bar.hide()
        self.progress_bar.setRange(0, 1)
        self.hero_mode_pill.setText('Error en pipeline')
        self.log(error_text)
        QMessageBox.critical(self, APP_TITLE, error_text)

    # ========== Stats and Rendering ==========

    def render_stats(self) -> None:
        """Render stats in stats panel."""
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

        from app.helpers import human_size

        for ext, count in data.get('ext_counts', {}).items():
            lines.append(f'  {ext:<12} {count}')

        lines.extend(['', 'Top-level folders:'])
        for folder, count in data.get('top_level_counts', {}).items():
            lines.append(f'  {folder:<28} {count}')

        lines.extend(['', 'Archivos más grandes:'])
        for item in stats.get('largest_files', []):
            lines.append(f"  {human_size(item['size']).rjust(8)}   {item['relpath']}")

        self.stats_text.setPlainText('\n'.join(lines))

    def _update_metric_cards_idle(self) -> None:
        """Update metric cards in idle state."""
        repo_name = Path(self.repo_combo.currentText().strip() or 'repo').name or 'repo'
        self.metric_repo.set_data(repo_name, 'aún sin indexado')
        self.metric_files.set_data('0', 'archivos en memoria')
        self.metric_scope.set_data('todo el repo', 'scope inicial')
        self.metric_results.set_data('0', 'sin búsqueda')

    def _update_metric_cards_after_index(self) -> None:
        """Update metric cards after indexing."""
        repo_root = self.index_data.get('root', '')
        repo_name = (
            Path(repo_root).name 
            if repo_root 
            else Path(self.repo_combo.currentText().strip() or 'repo').name
        )
        total_files = len(self.index_data.get('files', {}))
        total_ext = len(self.index_data.get('ext_counts', {}))
        elapsed = self.index_data.get('stats', {}).get('elapsed_sec', 0)

        self.metric_repo.set_data(repo_name or 'repo', repo_root or 'ruta sin resolver')
        self.metric_files.set_data(str(total_files), f'{total_ext} extensiones • {elapsed}s')
        scope = self.folder_combo.currentText() or '(todo)'
        self.metric_scope.set_data(
            'todo el repo' if scope == '(todo)' else scope,
            self.ext_combo.currentText() or '(todas)'
        )
        self.metric_results.set_data(
            str(len(self.search_results)),
            self.search_box.text().strip() or 'sin query activa'
        )

    def _update_preview_actions(self) -> None:
        """Update preview action states."""
        has_preview = bool(self.current_preview_path)
        is_svg = bool(
            self.current_preview_path 
            and Path(self.current_preview_path).suffix.lower() == '.svg'
        )

        self.open_system_btn.setEnabled(has_preview)
        self.open_svg_btn.setEnabled(is_svg)
        self.bookmark_btn.setEnabled(has_preview)
        self.back_action.setEnabled(self.navigation_controller._preview_history_index > 0)
        self.forward_action.setEnabled(
            self.navigation_controller._preview_history_index 
            < len(self.navigation_controller._preview_history) - 1
        )
        self.bookmark_action.setEnabled(has_preview)

    # ========== Logging ==========

    def log(self, msg: str) -> None:
        """Log message to log text widget."""
        line = f'[{now_str()}] {msg}'
        self.log_text.appendPlainText(line)
        self.statusBar().showMessage(msg, 2200)

    # ========== Window Events ==========

    def closeEvent(self, event) -> None:
        """Save state before closing."""
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('window_state_v3', self.saveState(STATE_VERSION))
        self.settings.setValue('central_splitter_sizes', self.central_splitter.sizes())
        self.settings.setValue('last_repo', self.repo_combo.currentText())
        self.settings.setValue('last_preview_rel', self.current_preview_rel or '')
        self.backend.remember_repo(self.repo_combo.currentText())
        self.backend.update_filter_settings(
            self.folder_combo.currentText() or '(todo)',
            self.ext_combo.currentText() or '(todas)'
        )
        super().closeEvent(event)
