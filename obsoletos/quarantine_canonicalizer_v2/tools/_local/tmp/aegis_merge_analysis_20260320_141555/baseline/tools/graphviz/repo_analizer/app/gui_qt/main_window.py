from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import QSettings, Qt, QThread
from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
)

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
from .dev_diagnostics import RuntimeDiagnostics
from .dock_manager import DockManager
from .event_bus import EventBus
from .layout_manager import LayoutManager
from .navigation_controller import NavigationController
from .preview_controller import PreviewController
from .plugins import PluginManager
from .search_controller import SearchController
from .services import ServiceContainer
from .shell import (
    BookmarkRuntimeCoordinator,
    CentralWorkspaceBuilder,
    ShellContributionBridge,
    ShellMenuBuilder,
    SkinRuntimeCoordinator,
    StatusStripBuilder,
    WorkspaceRuntimeCoordinator,
)
from .skins import ORANGE_EMBER, SkinTokens, get_skin
from .svg_viewer import SvgPreviewWindow
from .toolbar_controller import ToolbarController
from .tree_controller import TreeController
from .ui_contribution_registry import UIContributionRegistry
from .visual_runtime import VisualRuntimeCoordinator
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
        self.runtime_diagnostics = RuntimeDiagnostics(
            settings=self.settings,
            logger=self._emit_diagnostic_log,
        )
        self._startup_health_summary: dict[str, object] = {}
        self.STATE_VERSION = STATE_VERSION
        self.runtime_diagnostics.startup_step(
            'core-setup',
            ok=True,
            detail='settings/backend/skin tokens ready',
        )
        
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
        
        # UI state
        self._svg_window: SvgPreviewWindow | None = None
        self._restored_preview_once = False
        self._pending_folder_filter = '(todo)'
        self._pending_ext_filter = '(todas)'
        
        # Initialize controllers
        self.toolbar_controller = ToolbarController(self)
        self.tree_controller = TreeController(self)
        self.search_controller = SearchController(self)
        self.preview_controller = PreviewController(self)
        self.navigation_controller = NavigationController(self)
        self.dock_manager = DockManager(self)
        self.layout_manager = LayoutManager(self)

        # Internal shell builders
        self.central_workspace_builder = CentralWorkspaceBuilder(self)
        self.status_strip_builder = StatusStripBuilder(self)
        self.shell_menu_builder = ShellMenuBuilder(self)
        self.shell_contribution_bridge = ShellContributionBridge(
            self,
            self.shell_menu_builder,
        )
        self.workspace_runtime = WorkspaceRuntimeCoordinator(self)
        self.bookmark_runtime = BookmarkRuntimeCoordinator(self)
        self.visual_runtime = VisualRuntimeCoordinator(self)
        self.skin_runtime = SkinRuntimeCoordinator(self)
        
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
        self.runtime_diagnostics.startup_step(
            'window-configured',
            ok=True,
            detail='dock and tab behavior configured',
        )

    def _build_ui(self) -> None:
        """Build all UI components."""
        self.runtime_diagnostics.trace('startup', 'build ui started')
        self.toolbar_controller.build_toolbar()
        self.runtime_diagnostics.startup_step('toolbar-built', ok=True)
        self.central_workspace_builder.build(self._skin_tokens)
        self.runtime_diagnostics.startup_step('central-workspace-built', ok=True)
        self.dock_manager.build_docks(self._skin_tokens)
        self.runtime_diagnostics.startup_step('docks-built', ok=True)
        self.status_strip_builder.build()
        self.runtime_diagnostics.startup_step('status-strip-built', ok=True)
        self.shell_menu_builder.build()
        self.runtime_diagnostics.startup_step('shell-menu-built', ok=True)
        self.shell_contribution_bridge.apply()
        self.runtime_diagnostics.startup_step('plugin-contributions-applied', ok=True)
        self.visual_runtime.process_shell_surfaces(
            self._skin_tokens,
            reason='startup-build',
            force=False,
        )
        self.runtime_diagnostics.startup_step('visual-runtime-primed', ok=True)

    def _finalize_setup(self) -> None:
        """Finalize setup and restore state."""
        self.layout_manager.restore_ui_state()
        self.runtime_diagnostics.startup_step('layout-restored', ok=True)
        self.apply_selected_skin(self._skin_tokens.name)
        self.runtime_diagnostics.startup_step('skin-applied', ok=True, detail=self._skin_tokens.name)
        self._update_preview_actions()
        self.runtime_diagnostics.startup_step('preview-actions-updated', ok=True)
        self._refresh_startup_health_summary()
        self.log('Listo. Ember Graph Workstation conectado al backend real.')

        skip_auto_index = str(os.environ.get('HITECH_QT_SKIP_AUTO_INDEX', '')).strip().lower() in {
            '1',
            'true',
            'yes',
            'on',
        }
        if skip_auto_index:
            self.runtime_diagnostics.startup_step(
                'auto-index-skipped',
                ok=True,
                detail='HITECH_QT_SKIP_AUTO_INDEX',
            )
            return

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
        self.service_container.register('runtime_diagnostics', self.runtime_diagnostics)
        
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
            plugin_report = self.plugin_manager.get_diagnostics_report()
            self.runtime_diagnostics.trace(
                'plugin-manager',
                'plugins initialized',
                loaded=plugin_report.get('loaded_plugins_count', 0),
                initialized=plugin_report.get('initialized_plugins_count', 0),
                load_failures=plugin_report.get('load_failures_count', 0),
                init_failures=plugin_report.get('init_failures_count', 0),
            )
            self.runtime_diagnostics.startup_step(
                'plugins-initialized',
                ok=(
                    int(plugin_report.get('load_failures_count', 0)) == 0
                    and int(plugin_report.get('init_failures_count', 0)) == 0
                ),
                detail=(
                    f"loaded={plugin_report.get('loaded_plugins_count', 0)} "
                    f"initialized={plugin_report.get('initialized_plugins_count', 0)}"
                ),
            )
    
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

    # ========== Index Operations ==========

    def choose_repo(self) -> None:
        self.workspace_runtime.choose_repo()

    def start_indexing(self, auto: bool = False) -> None:
        self.workspace_runtime.start_indexing(auto=auto)

    def _clear_index_thread(self) -> None:
        self.workspace_runtime._clear_index_thread()

    def on_index_ready(self, payload: object) -> None:
        self.workspace_runtime.on_index_ready(payload)

    def clear_views_for_reindex(self) -> None:
        self.workspace_runtime.clear_views_for_reindex()

    # ========== Filter Operations ==========

    def rebuild_filter_values(self) -> None:
        self.workspace_runtime.rebuild_filter_values()

    def rebuild_quick_filters(self) -> None:
        self.workspace_runtime.rebuild_quick_filters()

    def sync_quick_filter_combo(self) -> None:
        self.workspace_runtime.sync_quick_filter_combo()

    def on_quick_filter_selected(self) -> None:
        self.workspace_runtime.on_quick_filter_selected()

    def on_filter_inputs_changed(self) -> None:
        self.workspace_runtime.on_filter_inputs_changed()

    def on_include_hidden_changed(self) -> None:
        self.workspace_runtime.on_include_hidden_changed()

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
        self.skin_runtime.apply_selected_skin(skin_name)

    def _apply_skin_to_widgets(self) -> None:
        self.skin_runtime._apply_skin_to_widgets()

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
        self.bookmark_runtime.open_selected_bookmark()

    def remove_selected_bookmark(self) -> None:
        self.bookmark_runtime.remove_selected_bookmark()

    # ========== Bookmark Operations ==========

    def add_current_preview_bookmark(self) -> None:
        self.bookmark_runtime.add_current_preview_bookmark()

    def refresh_bookmarks_view(self) -> None:
        self.bookmark_runtime.refresh_bookmarks_view()

    # ========== Layout Operations ==========

    def reset_layout(self, save_snapshot: bool = True) -> None:
        """Reset to default layout."""
        self.layout_manager.reset_layout(save_snapshot)
        self.visual_runtime.process_shell_surfaces(
            self._skin_tokens,
            reason='layout-reset',
            force=False,
        )

    def apply_focus_layout(self) -> None:
        """Apply focus layout."""
        self.layout_manager.apply_focus_layout()
        self.visual_runtime.process_shell_surfaces(
            self._skin_tokens,
            reason='layout-focus',
            force=False,
        )

    def process_visual_subtree(
        self,
        root,
        *,
        reason: str = 'manual-subtree',
        force: bool = False,
        debug: bool | None = None,
    ) -> None:
        """Explicit helper for processing rebuilt or late-added widget subtrees."""
        self.visual_runtime.process_subtree(
            root,
            tokens=self._skin_tokens,
            reason=reason,
            force=force,
            debug=debug,
        )

    # ========== Developer Diagnostics ==========

    def get_developer_diagnostics_snapshot(self) -> dict[str, object]:
        plugin_report = {}
        if hasattr(self, 'plugin_manager') and self.plugin_manager is not None:
            plugin_report = self.plugin_manager.get_diagnostics_report()

        integration_report = {}
        if (
            hasattr(self, 'shell_contribution_bridge')
            and self.shell_contribution_bridge is not None
            and hasattr(self.shell_contribution_bridge, 'get_integration_report')
        ):
            integration_report = self.shell_contribution_bridge.get_integration_report()

        summary = self.runtime_diagnostics.build_startup_summary(
            self,
            plugin_report=plugin_report,
            integration_report=integration_report,
        )
        return {
            'startup_summary': summary,
            'startup_steps': self.runtime_diagnostics.get_startup_steps(),
            'warnings': self.runtime_diagnostics.get_warnings(),
            'traces': self.runtime_diagnostics.get_trace_events(),
            'plugin_report': plugin_report,
            'integration_report': integration_report,
        }

    def _refresh_startup_health_summary(self) -> None:
        snapshot = self.get_developer_diagnostics_snapshot()
        summary = snapshot.get('startup_summary', {})
        if not isinstance(summary, dict):
            return
        self._startup_health_summary = summary
        line = self.runtime_diagnostics.summary_line(summary)
        self.log(f"Startup health: {line}")

    def _emit_diagnostic_log(self, message: str) -> None:
        line = f'[{now_str()}] {message}'
        delivered_to_widget = False
        log_widget = getattr(self, 'log_text', None)
        if log_widget is not None and hasattr(log_widget, 'appendPlainText'):
            try:
                log_widget.appendPlainText(line)
                delivered_to_widget = True
            except Exception:
                pass
        debug_enabled = bool(
            getattr(getattr(self, 'runtime_diagnostics', None), 'debug_enabled', False)
        )
        if debug_enabled or not delivered_to_widget:
            print(line)

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
        self.workspace_runtime.on_worker_error(error_text)

    # ========== Stats and Rendering ==========

    def render_stats(self) -> None:
        self.workspace_runtime.render_stats()

    def _update_metric_cards_idle(self) -> None:
        self.workspace_runtime._update_metric_cards_idle()

    def _update_metric_cards_after_index(self) -> None:
        self.workspace_runtime._update_metric_cards_after_index()

    def _update_preview_actions(self) -> None:
        self.workspace_runtime._update_preview_actions()

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
        splitter = getattr(self, 'central_splitter', None)
        if splitter is not None:
            try:
                self.settings.setValue('central_splitter_sizes', splitter.sizes())
            except Exception:
                self.settings.setValue('central_splitter_sizes', [])
        else:
            self.settings.setValue('central_splitter_sizes', [])
        self.settings.setValue('last_repo', self.repo_combo.currentText())
        self.settings.setValue('last_preview_rel', self.current_preview_rel or '')
        self.backend.remember_repo(self.repo_combo.currentText())
        self.backend.update_filter_settings(
            self.folder_combo.currentText() or '(todo)',
            self.ext_combo.currentText() or '(todas)'
        )
        super().closeEvent(event)
