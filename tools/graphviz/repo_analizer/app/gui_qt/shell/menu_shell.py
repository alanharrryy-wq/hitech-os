from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QDockWidget, QMenu

from ..skins import list_skins

try:
    from shiboken6 import isValid as qt_object_is_valid
except ImportError:  # pragma: no cover - PySide6 ships shiboken6
    def qt_object_is_valid(obj):
        return obj is not None

if TYPE_CHECKING:
    from ..main_window import RepoAnalyzerMainWindow
    from ..ui_contribution_registry import MenuActionContribution


class ShellMenuBuilder:
    """Compose shell menus and provide stable menu-path extension points."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window
        self._menu_path_cache: dict[str, QMenu] = {}
        self._plugin_menu_actions: list[QAction] = []
        self._tool_switch_actions: list[QAction] = []
        self._search_actions: list[QAction] = []
        self._inspect_actions: list[QAction] = []
        self._tools_menu: QMenu | None = None
        self._tools_switch_menu: QMenu | None = None
        self._tools_extensions_menu: QMenu | None = None

    def build(self) -> None:
        menu = self.main.menuBar()
        menu.setObjectName('menuBarSurface')
        menu.setProperty('visualRole', 'toolbar-surface')
        menu.setProperty('visualTier', 'themed')
        menu.clear()
        self._reset_runtime_state()

        file_menu = menu.addMenu("File")
        self._remember_menu_path("File", file_menu)
        file_menu.addAction("Open Repo...").triggered.connect(self.main.choose_repo)
        file_menu.addAction("Export Results...").triggered.connect(
            self.main.search_controller.export_results
        )
        file_menu.addSeparator()
        prefs_action = file_menu.addAction("Preferences...")
        prefs_action.setShortcut(QKeySequence("Ctrl+,"))
        prefs_action.triggered.connect(self.main.open_preferences_dialog)
        file_menu.addSeparator()
        file_menu.addAction("Exit").triggered.connect(self.main.close)

        tools_menu = menu.addMenu("Tools")
        self._remember_menu_path("Tools", tools_menu)
        self._tools_menu = tools_menu

        launcher_action = tools_menu.addAction("Open Tools Launcher")
        launcher_action.setShortcut(QKeySequence("Ctrl+Shift+L"))
        launcher_action.triggered.connect(self.main.focus_tools_launcher)

        self._tools_switch_menu = tools_menu.addMenu("Switch Active Tool")
        self._remember_menu_path("Tools/Switch Active Tool", self._tools_switch_menu)

        reopen_action = tools_menu.addAction("Reopen Last Active Tool")
        reopen_action.setShortcut(QKeySequence("Ctrl+Shift+T"))
        reopen_action.triggered.connect(self._reopen_last_active_tool)

        self._tools_extensions_menu = tools_menu.addMenu("Extensions")
        self._remember_menu_path("Tools/Extensions", self._tools_extensions_menu)

        search_menu = menu.addMenu("Search")
        self._remember_menu_path("Search", search_menu)
        run_search = search_menu.addAction("Run Search")
        run_search.setShortcut(QKeySequence("Ctrl+Enter"))
        run_search.triggered.connect(
            lambda checked=False: self._activate_group_and_call("search", self.main.start_search)
        )
        self._search_actions.append(run_search)

        clear_search = search_menu.addAction("Clear Search Results")
        clear_search.triggered.connect(
            lambda checked=False: self._activate_group_and_call(
                "search",
                self.main.search_controller.clear_search,
            )
        )
        self._search_actions.append(clear_search)

        export_search = search_menu.addAction("Export Search Results...")
        export_search.triggered.connect(
            lambda checked=False: self._activate_group_and_call(
                "search",
                self.main.search_controller.export_results,
            )
        )
        self._search_actions.append(export_search)

        search_menu.addSeparator()
        toggle_advanced = search_menu.addAction("Show Advanced Controls")
        toggle_advanced.setCheckable(True)
        toggle_advanced.setChecked(bool(self.main.command_toolbar.isVisible()))
        toggle_advanced.triggered.connect(
            lambda checked=False: self.main.command_toolbar.setVisible(bool(checked))
        )
        self._search_actions.append(toggle_advanced)

        inspect_menu = menu.addMenu("Inspect")
        self._remember_menu_path("Inspect", inspect_menu)
        for dock_name, label in (
            ("explorer_dock", "Explorer"),
            ("inspector_dock", "Inspector"),
            ("results_dock", "Results"),
            ("bookmarks_dock", "Bookmarks"),
        ):
            dock = getattr(self.main, dock_name, None)
            if isinstance(dock, QDockWidget):
                action = dock.toggleViewAction()
                action.setText(label)
                inspect_menu.addAction(action)
                self._inspect_actions.append(action)

        graph_menu = menu.addMenu("Graph")
        self._remember_menu_path("Graph", graph_menu)
        graph_menu.addAction("Open SVG Workspace").triggered.connect(
            lambda checked=False: self._activate_group_and_call(
                "graph",
                self.main.preview_controller.open_svg_workspace,
            )
        )
        for dock_name, label in (
            ("workspace_summary_dock", "Repository Summary"),
            ("preview_workspace_dock", "Preview"),
            ("central_inspector_dock", "Context Inspector"),
        ):
            dock = getattr(self.main, dock_name, None)
            if isinstance(dock, QDockWidget):
                action = dock.toggleViewAction()
                action.setText(label)
                graph_menu.addAction(action)

        run_menu = menu.addMenu("Run")
        self._remember_menu_path("Run", run_menu)
        run_menu.addAction("Index Repository").triggered.connect(
            lambda checked=False: self._activate_group_and_call("run", self.main.start_indexing)
        )
        run_menu.addAction("Focus Layout").triggered.connect(
            lambda checked=False: self._activate_group_and_call("run", self.main.apply_focus_layout)
        )
        run_menu.addAction("Balanced Layout").triggered.connect(
            lambda checked=False: self._activate_group_and_call("run", self.main.reset_layout)
        )
        run_menu.addSeparator()
        run_menu.addAction("Save Layout Snapshot").triggered.connect(
            self.main.layout_manager.save_current_layout_snapshot
        )
        run_menu.addAction("Restore Layout Snapshot").triggered.connect(
            self.main.layout_manager.restore_saved_layout_snapshot
        )

        settings_menu = menu.addMenu("Settings")
        self._remember_menu_path("Settings", settings_menu)
        settings_menu.addAction("Preferences...").triggered.connect(
            lambda checked=False: self._activate_group_and_call(
                "settings",
                self.main.open_preferences_dialog,
            )
        )
        skins_menu = settings_menu.addMenu("Skins")
        self._remember_menu_path("Settings/Skins", skins_menu)
        for skin in list_skins():
            action = skins_menu.addAction(skin.display_name)
            action.triggered.connect(
                lambda checked=False, name=skin.name: self.main.apply_selected_skin(name)
            )

        self.refresh_tool_entries()

    def add_plugin_menu_action(self, contribution: MenuActionContribution) -> QAction:
        menu = self.find_or_create_menu_path(contribution.menu_path)
        if menu is None or not self._is_menu_alive(menu):
            raise RuntimeError(
                f"Could not resolve live menu path for plugin contribution '{contribution.contribution_id}'"
            )

        action = QAction(contribution.text, menu)
        action.setObjectName(
            f"plugin_menu_action_{self._sanitize_plugin_ui_name(contribution.contribution_id)}"
        )
        action.setProperty('pluginContributionId', contribution.contribution_id)
        action.setProperty('pluginContributionKind', 'menu')
        action.setProperty('pluginMenuPath', contribution.menu_path)
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
        return action

    def refresh_tool_entries(self) -> None:
        self._clear_dynamic_tool_actions()
        tool_workspace = getattr(self.main, "tool_workspace", None)
        if tool_workspace is None:
            return

        if self._tools_switch_menu is not None and self._is_menu_alive(self._tools_switch_menu):
            entries = tool_workspace.list_tools()
            catalog = self.main.service_container.get("tool_catalog")
            if not entries:
                placeholder = self._tools_switch_menu.addAction("No tools available")
                placeholder.setEnabled(False)
                self._tool_switch_actions.append(placeholder)
            for entry in entries:
                descriptor = catalog.get_tool(entry.tool_id) if catalog is not None else None
                enabled = bool(descriptor.enabled) if descriptor is not None else True
                category = str(descriptor.category) if descriptor is not None else "other"
                action = self._tools_switch_menu.addAction(
                    f"[{category}] {entry.display_name}"
                )
                action.setCheckable(True)
                action.setChecked(entry.active)
                action.setEnabled(enabled)
                action.triggered.connect(
                    lambda checked=False, tool_id=entry.tool_id: self._activate_tool_from_menu(
                        tool_id
                    )
                )
                self._tool_switch_actions.append(action)

        launcher_panel = getattr(self.main, "tool_launcher_panel", None)
        if launcher_panel is not None and hasattr(launcher_panel, "refresh"):
            try:
                launcher_panel.refresh()
            except Exception:
                pass

    def find_or_create_menu_path(self, menu_path: str) -> QMenu:
        menu_path = self._normalize_public_menu_path(menu_path)
        parts = [part.strip() for part in menu_path.split("/") if part.strip()]
        if not parts:
            raise ValueError("menu_path cannot be empty")

        current_menu: QMenu | None = None
        current_path: list[str] = []
        for index, part in enumerate(parts):
            current_path.append(part)
            path_str = "/".join(current_path)

            cached_menu = self._get_cached_menu(path_str)
            if cached_menu is not None:
                current_menu = cached_menu
                continue

            if index == 0:
                current_menu = self._find_or_create_top_level_menu(part)
            else:
                if current_menu is None or not self._is_menu_alive(current_menu):
                    raise RuntimeError(
                        f"Parent menu became invalid while resolving '{menu_path}'"
                    )
                current_menu = self._find_or_create_sub_menu(current_menu, part)

            self._remember_menu_path(path_str, current_menu)

        if current_menu is None or not self._is_menu_alive(current_menu):
            raise RuntimeError(f"Menu path '{menu_path}' resolved to an invalid QMenu")
        return current_menu

    def _reset_runtime_state(self) -> None:
        self._menu_path_cache.clear()
        self._plugin_menu_actions.clear()
        self._tool_switch_actions.clear()
        self._search_actions.clear()
        self._inspect_actions.clear()
        self._tools_menu = None
        self._tools_switch_menu = None
        self._tools_extensions_menu = None

    def _menu_cache_key(self, menu_path: str) -> str:
        normalized_path = self._normalize_public_menu_path(menu_path)
        parts = [part.strip() for part in normalized_path.split("/") if part.strip()]
        return "/".join(self._normalize_menu_text(part) for part in parts)

    def _remember_menu_path(self, menu_path: str, menu: QMenu) -> QMenu:
        key = self._menu_cache_key(menu_path)
        if key and self._is_menu_alive(menu):
            self._menu_path_cache[key] = menu
        return menu

    def _get_cached_menu(self, menu_path: str) -> QMenu | None:
        key = self._menu_cache_key(menu_path)
        if not key:
            return None

        menu = self._menu_path_cache.get(key)
        if self._is_menu_alive(menu):
            return menu

        self._menu_path_cache.pop(key, None)
        return None

    def _find_or_create_top_level_menu(self, title: str) -> QMenu:
        normalized = self._normalize_menu_text(title)
        for action in self.main.menuBar().actions():
            menu = action.menu()
            if not self._is_menu_alive(menu):
                continue
            if self._normalize_menu_text(menu.title()) == normalized:
                return menu

        menu = QMenu(title, self.main.menuBar())
        self.main.menuBar().addMenu(menu)
        return menu

    def _find_or_create_sub_menu(self, parent_menu: QMenu, title: str) -> QMenu:
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

    def _is_menu_alive(self, menu: QMenu | None) -> bool:
        if menu is None:
            return False
        try:
            return bool(qt_object_is_valid(menu))
        except RuntimeError:
            return False

    def _normalize_menu_text(self, value: str) -> str:
        return value.replace("&", "").strip().lower()

    def _sanitize_plugin_ui_name(self, value: str) -> str:
        sanitized = "".join(ch if ch.isalnum() else "_" for ch in value.strip().lower())
        return sanitized.strip("_") or "plugin"

    def _normalize_public_menu_path(self, menu_path: str) -> str:
        parts = [part.strip() for part in str(menu_path or "").split("/") if part.strip()]
        if not parts:
            return ""
        root = self._normalize_menu_text(parts[0])
        if root in {"plugins", "plugin"}:
            mapped = ["Tools", "Extensions", *parts[1:]]
            return "/".join(mapped)
        if root == "view":
            mapped = ["Inspect", *parts[1:]]
            return "/".join(mapped)
        if root == "workspace":
            mapped = ["Run", *parts[1:]]
            return "/".join(mapped)
        return "/".join(parts)

    def _clear_dynamic_tool_actions(self) -> None:
        for action in self._tool_switch_actions:
            if self._tools_switch_menu is not None and self._is_menu_alive(self._tools_switch_menu):
                self._tools_switch_menu.removeAction(action)
        self._tool_switch_actions.clear()

    def _reopen_last_active_tool(self) -> None:
        reopen = getattr(self.main, "reopen_last_tool_via_group", None)
        if callable(reopen):
            reopen(reason="menu-reopen")
        else:
            tool_workspace = getattr(self.main, "tool_workspace", None)
            if tool_workspace is not None:
                tool_workspace.reopen_last_active_tool()
        self.refresh_tool_entries()

    def _activate_tool_from_menu(self, tool_id: str) -> None:
        route = getattr(self.main, "activate_group_for_tool", None)
        if callable(route):
            route(tool_id, reason="menu-switch")
        tool_workspace = getattr(self.main, "tool_workspace", None)
        if tool_workspace is None:
            return
        tool_workspace.activate_tool(tool_id, reason="menu-switch")
        self.refresh_tool_entries()

    def _activate_group_and_call(self, group_id: str, callback) -> None:
        activate = getattr(self.main, "activate_shell_group", None)
        if callable(activate):
            activate(group_id, reason=f"menu:{group_id}")
        callback()

    def _iter_shell_docks(self) -> tuple[QDockWidget, ...]:
        dock_names = (
            "workspace_summary_dock",
            "preview_workspace_dock",
            "central_inspector_dock",
            "tools_launcher_dock",
            "explorer_dock",
            "results_dock",
            "inspector_dock",
            "bookmarks_dock",
        )
        return tuple(
            dock
            for name in dock_names
            for dock in (getattr(self.main, name, None),)
            if isinstance(dock, QDockWidget)
        )
