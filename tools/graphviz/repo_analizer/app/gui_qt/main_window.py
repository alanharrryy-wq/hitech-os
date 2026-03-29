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
from .event_bus import EventBus, Events
from .layout_manager import LayoutManager
from .navigation_controller import NavigationController
from .preferences import (
    PreferencesDialog,
    PreferencesRuntime,
    RuntimePolicyApplicator,
)
from .preview_controller import PreviewController
from .plugins import PluginManager
from .search_controller import SearchController
from .services import ServiceContainer
from .shell import (
    BookmarkRuntimeCoordinator,
    CentralWorkspaceBuilder,
    CommandRoutingRuntime,
    ShellGroupRuntime,
    ShellContributionBridge,
    ShellMenuBuilder,
    SkinRuntimeCoordinator,
    StatusStripBuilder,
    ToolWorkspaceCoordinator,
    WorkstationContextBridge,
    WorkstationContextRuntime,
    WorkspaceRuntimeCoordinator,
)
from .skins import ORANGE_EMBER, SkinTokens, get_skin
from .tools import ToolCatalogService
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
        self.preferences_runtime = PreferencesRuntime(
            self.settings,
            default_skin_name=ORANGE_EMBER.name,
        )
        self.runtime_policy_applicator = RuntimePolicyApplicator()
        self.tool_catalog = ToolCatalogService(self.settings)
        self.backend = AnalyzerBackend()
        self._skin_tokens: SkinTokens = get_skin(
            self.preferences_runtime.current.skin_name
        )
        self.runtime_diagnostics = RuntimeDiagnostics(
            settings=self.settings,
            logger=self._emit_diagnostic_log,
        )
        self._runtime_event_unsubscribers: list[object] = []
        self._startup_health_summary: dict[str, object] = {}
        self.STATE_VERSION = STATE_VERSION
        self.runtime_diagnostics.startup_step(
            'core-setup',
            ok=True,
            detail='settings/backend/skin tokens ready',
        )
        
        # Repository state
        default_repo_root = str(Path(__file__).resolve().parents[3])
        self._repo_path = self.backend.settings.get('last_repo', '') or default_repo_root
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
        self.quick_filter_all_label = '(all folders)'
        self.quick_filter_manual_label = '(manual filter)'
        
        # Threading
        self._index_thread: QThread | None = None
        self._index_worker: IndexWorker | None = None
        
        # UI state
        self._svg_window: SvgPreviewWindow | None = None
        self._restored_preview_once = False
        self._pending_folder_filter = '(all)'
        self._pending_ext_filter = '(all)'
        
        # Initialize controllers
        self.toolbar_controller = ToolbarController(self)
        self.tree_controller = TreeController(self)
        self.search_controller = SearchController(self)
        self.preview_controller = PreviewController(self)
        self.navigation_controller = NavigationController(self)
        self.dock_manager = DockManager(self)
        self.layout_manager = LayoutManager(self)
        self.shell_group_runtime: ShellGroupRuntime | None = None

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
        self.tool_workspace = ToolWorkspaceCoordinator(self)
        
        # Initialize extensibility infrastructure
        self._initialize_extensibility()
        
        # Build UI
        self._setup_window()
        self._build_ui()
        self._finalize_setup()

    def _setup_window(self) -> None:
        """Configure main window properties."""
        self.setWindowTitle(f'{APP_TITLE} • Workstation')
        self.resize(1760, 1080)
        self.setDockNestingEnabled(False)
        self.setAnimated(False)
        self.setDockOptions(
            QMainWindow.AllowTabbedDocks
            | QMainWindow.AnimatedDocks
        )
        self.setTabPosition(Qt.AllDockWidgetAreas, QTabWidget.North)
        self.setDocumentMode(True)
        self.runtime_diagnostics.startup_step(
            'window-configured',
            ok=True,
            detail='workstation host configured',
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
        self._register_core_shell_surfaces()
        self.runtime_diagnostics.startup_step('shell-core-surfaces-registered', ok=True)
        self.status_strip_builder.build()
        self.runtime_diagnostics.startup_step('status-strip-built', ok=True)
        self.shell_menu_builder.build()
        self.runtime_diagnostics.startup_step('shell-menu-built', ok=True)
        self.shell_contribution_bridge.apply()
        self.runtime_diagnostics.startup_step('plugin-contributions-applied', ok=True)
        self.toolbar_controller.refresh_tool_switcher()
        self.visual_runtime.process_shell_surfaces(
            self._skin_tokens,
            reason='startup-build',
            force=False,
        )
        self.runtime_diagnostics.startup_step('visual-runtime-primed', ok=True)

    def _finalize_setup(self) -> None:
        """Finalize setup and restore state."""
        self.layout_manager.restore_ui_state()
        self.layout_manager.apply_startup_disclosure()
        self.runtime_diagnostics.startup_step('layout-restored', ok=True)
        if self.shell_group_runtime is not None:
            self.shell_group_runtime.restore_startup_group()
            self.runtime_diagnostics.startup_step('group-shell-restored', ok=True)
        self.preferences_runtime.apply_app_font()
        self._apply_runtime_policies(reason='startup')
        self.runtime_diagnostics.startup_step('preferences-applied', ok=True)
        self.apply_selected_skin(self._skin_tokens.name)
        self.runtime_diagnostics.startup_step('skin-applied', ok=True, detail=self._skin_tokens.name)
        self._update_preview_actions()
        self.runtime_diagnostics.startup_step('preview-actions-updated', ok=True)
        self.workstation_context.update(
            repo_root=str(self._repo_path or ""),
            repo_name=Path(str(self._repo_path or "")).name,
            active_scope="(all)",
            active_extension="(all)",
            status_text="startup-ready",
        )
        self._refresh_startup_health_summary()
        self.log('Workstation shell ready.')

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
        self.workstation_context = WorkstationContextRuntime(self.event_bus, self)
        self.command_runtime = CommandRoutingRuntime(
            self.command_dispatcher,
            self.event_bus,
            self,
        )
        self.shell_group_runtime = ShellGroupRuntime(self)
        self.workstation_context_bridge = WorkstationContextBridge(
            self.event_bus,
            self.workstation_context,
            tool_workspace=self.tool_workspace,
            parent=self,
        )
        self._wire_runtime_diagnostic_subscriptions()
        
        # Register services in container
        self.service_container.register('event_bus', self.event_bus)
        self.service_container.register('command_dispatcher', self.command_dispatcher)
        self.service_container.register('backend', self.backend)
        self.service_container.register('ui_contribution_registry', self.ui_contribution_registry)
        self.service_container.register('tool_catalog', self.tool_catalog)
        self.service_container.register('settings', self.settings)
        self.service_container.register('preferences_runtime', self.preferences_runtime)
        self.service_container.register('main_window', self)
        self.service_container.register('runtime_diagnostics', self.runtime_diagnostics)
        self.service_container.register('tool_workspace', self.tool_workspace)
        self.service_container.register('workstation_context', self.workstation_context)
        self.service_container.register('command_runtime', self.command_runtime)
        self.service_container.register('shell_group_runtime', self.shell_group_runtime)
        
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
            self._sync_tool_catalog_from_plugins()
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

    def _sync_tool_catalog_from_plugins(self) -> None:
        plugin_manager = getattr(self, "plugin_manager", None)
        if plugin_manager is None:
            return
        for plugin_name in plugin_manager.get_all_plugins().keys():
            manifest = plugin_manager.get_plugin_manifest(plugin_name)
            manifest_payload = manifest.to_dict() if manifest is not None else {
                "name": plugin_name,
                "description": "",
                "enabled": True,
            }
            self.tool_catalog.register_from_manifest(
                tool_id=plugin_name,
                manifest_like=manifest_payload,
                default_source="plugin",
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

    def _wire_runtime_diagnostic_subscriptions(self) -> None:
        diagnostics = getattr(self, "runtime_diagnostics", None)
        if diagnostics is None or not hasattr(diagnostics, "trace"):
            return
        subscriptions = (
            Events.TOOL_LIFECYCLE_TRANSITION,
            Events.TOOL_INVARIANT_CORRECTED,
            Events.PROCESS_SESSION_STATE_CHANGED,
        )
        for event_name in subscriptions:
            try:
                unsub = self.event_bus.subscribe(
                    event_name,
                    lambda payload, _event_name=event_name: self._on_runtime_event(
                        _event_name,
                        payload,
                    ),
                )
                self._runtime_event_unsubscribers.append(unsub)
            except Exception:
                continue

    def _on_runtime_event(self, event_name: str, payload: object) -> None:
        diagnostics = getattr(self, "runtime_diagnostics", None)
        if diagnostics is None or not hasattr(diagnostics, "trace"):
            return
        if isinstance(payload, dict):
            diagnostics.trace("runtime-mechanics", event_name, **payload)
            return
        diagnostics.trace("runtime-mechanics", event_name, payload=str(payload))

    def _register_core_shell_surfaces(self) -> None:
        self.tool_workspace.register_core_surface(
            contribution_id='shell.workspace_summary',
            title='Repository Summary',
            dock=self.workspace_summary_dock,
        )
        self.tool_workspace.register_core_surface(
            contribution_id='shell.preview_workspace',
            title='Preview',
            dock=self.preview_workspace_dock,
        )
        self.tool_workspace.register_core_surface(
            contribution_id='shell.central_inspector',
            title='Context Inspector',
            dock=self.central_inspector_dock,
        )
        self.tool_workspace.register_core_surface(
            contribution_id='shell.explorer',
            title='Explorer',
            dock=self.explorer_dock,
        )
        self.tool_workspace.register_core_surface(
            contribution_id='shell.tools_launcher',
            title='Tools',
            dock=self.tools_launcher_dock,
        )
        self.tool_workspace.register_core_surface(
            contribution_id='shell.results',
            title='Results',
            dock=self.results_dock,
        )
        self.tool_workspace.register_core_surface(
            contribution_id='shell.inspector',
            title='Inspector',
            dock=self.inspector_dock,
        )
        self.tool_workspace.register_core_surface(
            contribution_id='shell.bookmarks',
            title='Bookmarks',
            dock=self.bookmarks_dock,
        )

    def focus_tools_launcher(self) -> None:
        self.activate_shell_group("explore", reason="tools-launcher-focus")
        dock = getattr(self, "tools_launcher_dock", None)
        if dock is None:
            return
        try:
            dock.show()
            dock.raise_()
            dock.activateWindow()
        except Exception:
            pass

        panel = getattr(self, "tool_launcher_panel", None)
        if panel is not None and hasattr(panel, "refresh"):
            try:
                panel.refresh()
            except Exception:
                pass

        self.statusBar().showMessage("Tools launcher ready", 1800)

    def activate_shell_group(self, group_id: str, *, reason: str = "manual") -> bool:
        runtime = self.service_container.get("shell_group_runtime")
        if runtime is None:
            return False
        applied = bool(runtime.apply_group(group_id, reason=reason, force=True))
        self.toolbar_controller.refresh_group_selector()
        return applied

    def activate_group_for_tool(self, tool_id: str, *, reason: str = "tool-route") -> str:
        runtime = self.service_container.get("shell_group_runtime")
        if runtime is None:
            return ""
        group_id = str(runtime.activate_for_tool(tool_id, reason=reason) or "")
        self.toolbar_controller.refresh_group_selector()
        return group_id

    def reopen_last_tool_via_group(self, *, reason: str = "reopen") -> bool:
        runtime = self.service_container.get("shell_group_runtime")
        if runtime is None:
            return False
        reopened = bool(runtime.reopen_last_tool(reason=reason))
        self.toolbar_controller.refresh_group_selector()
        return reopened

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

    # ========== Preferences ==========

    def open_preferences_dialog(self) -> None:
        dialog = PreferencesDialog(self.preferences_runtime, self)
        if dialog.exec() != PreferencesDialog.Accepted:
            return

        updates = dialog.gather_updates()
        previous_skin = self._skin_tokens.name
        self.preferences_runtime.update(**updates)
        self.preferences_runtime.apply_app_font()
        self._apply_runtime_policies(reason='preferences')

        requested_skin = self.preferences_runtime.current.skin_name
        if requested_skin != previous_skin:
            self.apply_selected_skin(requested_skin)

        persistence_issues = self.preferences_runtime.validate_persistence_contract()
        if persistence_issues:
            for issue in persistence_issues:
                self.log(f"[preferences] warning: {issue}")

        self.log("Preferences updated. Some loading flags require restart.")
        self.shell_menu_builder.refresh_tool_entries()
        self.toolbar_controller.refresh_tool_switcher()

    def _apply_runtime_policies(self, *, reason: str) -> None:
        policy = self.preferences_runtime.runtime_policy()
        apply_report = self.runtime_policy_applicator.apply(self, policy)

        self.tool_workspace.set_single_active_mode(
            self.preferences_runtime.prefers_single_active_tool()
        )

        self.workstation_context.update(
            runtime_density=policy.density_scale,
            runtime_motion=policy.motion_policy,
            runtime_performance=policy.performance_policy,
            status_text=(
                f"policy:{reason} density={policy.density_scale} "
                f"motion={policy.motion_policy} perf={policy.performance_policy}"
            )
        )
        diagnostics = getattr(self, "runtime_diagnostics", None)
        if diagnostics is not None and hasattr(diagnostics, "trace"):
            diagnostics.trace(
                "preferences-runtime",
                "policy-applied",
                reason=reason,
                applied=len(apply_report.applied_targets),
                skipped=len(apply_report.skipped_targets),
                failures=len(apply_report.failures),
            )

    def get_settings_center_hook_payload(self) -> dict[str, object]:
        payload = self.preferences_runtime.settings_center_hook_payload()
        payload["apply_report"] = {
            "runtime_density": str(self.property("runtimeDensityScale") or ""),
            "runtime_motion": str(self.property("runtimeMotionPolicy") or ""),
            "runtime_performance": str(self.property("runtimePerformancePolicy") or ""),
            "runtime_typography_scale": float(self.property("runtimeTypographyScale") or 0.0),
            "runtime_spacing_scale": float(self.property("runtimeSpacingScale") or 0.0),
            "runtime_min_font_pt": int(self.property("runtimeMinReadableFontPt") or 0),
        }
        return payload

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
        bus = getattr(self, "event_bus", None)
        if bus is not None:
            try:
                bus.publish(Events.STATUS_CHANGED, {"message": msg})
            except Exception:
                pass

    # ========== Window Events ==========

    def closeEvent(self, event) -> None:
        """Save state before closing."""
        command_runtime = getattr(self, 'command_runtime', None)
        if command_runtime is not None and hasattr(command_runtime, 'dispose'):
            try:
                command_runtime.dispose()
            except Exception:
                pass
        context_bridge = getattr(self, 'workstation_context_bridge', None)
        if context_bridge is not None and hasattr(context_bridge, 'dispose'):
            try:
                context_bridge.dispose()
            except Exception:
                pass
        tool_workspace = getattr(self, 'tool_workspace', None)
        if tool_workspace is not None and hasattr(tool_workspace, 'dispose'):
            try:
                tool_workspace.dispose()
            except Exception:
                pass
        toolbar_controller = getattr(self, 'toolbar_controller', None)
        if toolbar_controller is not None and hasattr(toolbar_controller, 'dispose'):
            try:
                toolbar_controller.dispose()
            except Exception:
                pass
        shell_group_runtime = getattr(self, 'shell_group_runtime', None)
        if shell_group_runtime is not None and hasattr(shell_group_runtime, 'deleteLater'):
            try:
                shell_group_runtime.deleteLater()
            except Exception:
                pass
        status_strip_builder = getattr(self, 'status_strip_builder', None)
        if status_strip_builder is not None and hasattr(status_strip_builder, 'dispose'):
            try:
                status_strip_builder.dispose()
            except Exception:
                pass
        while self._runtime_event_unsubscribers:
            handler = self._runtime_event_unsubscribers.pop()
            if callable(handler):
                try:
                    handler()
                except Exception:
                    pass
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
            self.folder_combo.currentText() or '(all)',
            self.ext_combo.currentText() or '(all)'
        )
        super().closeEvent(event)
