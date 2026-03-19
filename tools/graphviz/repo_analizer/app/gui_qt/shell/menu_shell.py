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
        file_menu.addAction("Exit").triggered.connect(self.main.close)

        workspace_menu = menu.addMenu("Workspace")
        self._remember_menu_path("Workspace", workspace_menu)
        workspace_menu.addAction("Save Current Layout").triggered.connect(
            self.main.layout_manager.save_current_layout_snapshot
        )
        workspace_menu.addAction("Restore Saved Layout").triggered.connect(
            self.main.layout_manager.restore_saved_layout_snapshot
        )
        workspace_menu.addAction("Reset to Balanced Layout").triggered.connect(
            self.main.reset_layout
        )
        workspace_menu.addAction("Apply Focus Layout").triggered.connect(
            self.main.apply_focus_layout
        )

        view_menu = menu.addMenu("View")
        self._remember_menu_path("View", view_menu)
        skins_menu = view_menu.addMenu("Skins")
        self._remember_menu_path("View/Skins", skins_menu)
        for skin in list_skins():
            action = skins_menu.addAction(skin.display_name)
            action.triggered.connect(
                lambda checked=False, name=skin.name: self.main.apply_selected_skin(name)
            )

        view_menu.addSeparator()
        dock_names = (
            "workspace_summary_dock",
            "preview_workspace_dock",
            "central_inspector_dock",
            "explorer_dock",
            "results_dock",
            "inspector_dock",
            "bookmarks_dock",
        )
        for name in dock_names:
            dock = getattr(self.main, name, None)
            if isinstance(dock, QDockWidget):
                view_menu.addAction(dock.toggleViewAction())

        view_menu.addSeparator()
        view_menu.addAction(self.main.workspace_toolbar.toggleViewAction())
        view_menu.addAction(self.main.command_toolbar.toggleViewAction())

        navigate_menu = menu.addMenu("Navigate")
        self._remember_menu_path("Navigate", navigate_menu)
        navigate_menu.addAction(self.main.back_action)
        navigate_menu.addAction(self.main.forward_action)
        navigate_menu.addAction("Open SVG Workspace").triggered.connect(
            self.main.preview_controller.open_svg_workspace
        )

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

    def find_or_create_menu_path(self, menu_path: str) -> QMenu:
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

    def _menu_cache_key(self, menu_path: str) -> str:
        parts = [part.strip() for part in menu_path.split("/") if part.strip()]
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
