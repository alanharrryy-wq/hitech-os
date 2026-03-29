from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .event_bus import Events
from .widgets import AccentButton, GhostButton, QuietButton, SecondaryButton

if TYPE_CHECKING:
    from .main_window import RepoAnalyzerMainWindow
    from .skins import SkinTokens
    from .ui_contribution_registry import ToolbarActionContribution


class ToolbarController:
    """Compose compact shell chrome and keep compatibility toolbar hooks."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window
        self.buttons: list[Any] = []
        self.plugin_actions: list[QAction] = []
        self.group_buttons: dict[str, Any] = {}
        self._runtime_unsubscribers: list[object] = []
        self._switch_signals_blocked = False

    def build_toolbar(self) -> None:
        """Build a compact shell toolbar plus a hidden compatibility toolbar."""
        self._build_workspace_toolbar()
        self._build_command_toolbar()
        self.refresh_tool_switcher()
        self.refresh_group_selector()
        self._wire_runtime_events()

    def dispose(self) -> None:
        while self._runtime_unsubscribers:
            unsub = self._runtime_unsubscribers.pop()
            if callable(unsub):
                try:
                    unsub()
                except Exception:
                    pass

    def refresh_tool_switcher(self) -> None:
        combo = getattr(self.main, "tool_switch_combo", None)
        if combo is None:
            return
        workspace = getattr(self.main, "tool_workspace", None)
        if workspace is None:
            return

        previous_tool_id = str(combo.currentData() or "").strip()
        entries = workspace.list_tools()
        catalog = self.main.service_container.get("tool_catalog")

        self._switch_signals_blocked = True
        combo.blockSignals(True)
        try:
            combo.clear()

            active_index = -1
            for index, entry in enumerate(entries):
                descriptor = catalog.get_tool(entry.tool_id) if catalog is not None else None
                enabled = bool(descriptor.enabled) if descriptor is not None else True
                label = entry.display_name
                if not enabled:
                    label = f"{label} (Disabled)"
                combo.addItem(label, entry.tool_id)
                if not enabled:
                    combo.model().item(index).setEnabled(False)  # type: ignore[union-attr]

                if entry.active:
                    active_index = index
                elif previous_tool_id and previous_tool_id == entry.tool_id and active_index < 0:
                    active_index = index

            # Keep signals blocked while restoring selection to avoid reentrant
            # activate->lifecycle->refresh loops.
            if active_index >= 0:
                combo.setCurrentIndex(active_index)
        finally:
            combo.blockSignals(False)
            self._switch_signals_blocked = False

    def refresh_group_selector(self) -> None:
        runtime = self.main.service_container.get("shell_group_runtime")
        if runtime is None:
            return
        active_group_id = str(getattr(runtime, "active_group_id", "") or "").strip()
        for group_id, button in self.group_buttons.items():
            try:
                button.blockSignals(True)
                button.setChecked(group_id == active_group_id)
            except Exception:
                continue
            finally:
                try:
                    button.blockSignals(False)
                except Exception:
                    pass

    def _build_workspace_toolbar(self) -> None:
        """Build compact top rail: tools, repo, search, nav, settings."""
        toolbar = QToolBar("ShellToolbar", self.main)
        toolbar.setObjectName("WorkspaceToolbar")
        toolbar.setProperty("visualRole", "toolbar-surface")
        toolbar.setProperty("visualTier", "themed")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.main.addToolBar(Qt.TopToolBarArea, toolbar)
        self.main.workspace_toolbar = toolbar

        groups_surface = self._create_surface("workspaceGroupsSurface", role="toolbar-surface")
        groups_layout = QVBoxLayout(groups_surface)
        groups_layout.setContentsMargins(10, 8, 10, 8)
        groups_layout.setSpacing(4)
        groups_layout.addWidget(self._build_section_caption("Groups", parent=groups_surface))

        groups_row = QHBoxLayout()
        groups_row.setContentsMargins(0, 0, 0, 0)
        groups_row.setSpacing(6)

        runtime = self.main.service_container.get("shell_group_runtime")
        groups = runtime.list_groups() if runtime is not None else ()
        self.group_buttons.clear()
        for group in groups:
            button = QuietButton(group.label, self.main._skin_tokens, groups_surface)
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setToolTip(group.purpose)
            button.clicked.connect(
                lambda checked=False, group_id=group.group_id: self._on_group_selected(group_id)
            )
            self._register_skinnable(button)
            self.group_buttons[group.group_id] = button
            groups_row.addWidget(button)

        groups_layout.addLayout(groups_row)
        toolbar.addWidget(groups_surface)

        tools_surface = self._create_surface("workspaceToolsSurface", role="toolbar-surface")
        tools_layout = QVBoxLayout(tools_surface)
        tools_layout.setContentsMargins(10, 8, 10, 8)
        tools_layout.setSpacing(4)
        tools_layout.addWidget(self._build_section_caption("Tools", parent=tools_surface))

        tools_row = QHBoxLayout()
        tools_row.setContentsMargins(0, 0, 0, 0)
        tools_row.setSpacing(6)

        self.main.open_tools_btn = QuietButton("Open Launcher", self.main._skin_tokens, tools_surface)
        self.main.open_tools_btn.clicked.connect(self.main.focus_tools_launcher)
        self._register_skinnable(self.main.open_tools_btn)
        tools_row.addWidget(self.main.open_tools_btn)

        self.main.tool_switch_combo = QComboBox(tools_surface)
        self.main.tool_switch_combo.setObjectName("toolSwitchComboBox")
        self.main.tool_switch_combo.setMinimumWidth(220)
        self.main.tool_switch_combo.currentIndexChanged.connect(self._on_tool_switch_selected)
        tools_row.addWidget(self.main.tool_switch_combo, 1)

        self.main.reopen_tool_btn = GhostButton("Reopen Last", self.main._skin_tokens, tools_surface)
        self.main.reopen_tool_btn.clicked.connect(self._reopen_last_tool)
        self._register_skinnable(self.main.reopen_tool_btn)
        tools_row.addWidget(self.main.reopen_tool_btn)

        tools_layout.addLayout(tools_row)
        toolbar.addWidget(tools_surface)

        repo_surface = self._create_surface("workspaceRepoSurface")
        repo_layout = QVBoxLayout(repo_surface)
        repo_layout.setContentsMargins(10, 8, 10, 8)
        repo_layout.setSpacing(4)
        repo_layout.addWidget(self._build_section_caption("Repository", parent=repo_surface))

        repo_row = QHBoxLayout()
        repo_row.setContentsMargins(0, 0, 0, 0)
        repo_row.setSpacing(6)

        self.main.repo_combo = QComboBox(repo_surface)
        self.main.repo_combo.setObjectName("repoComboBox")
        self.main.repo_combo.setEditable(True)
        self.main.repo_combo.setMinimumWidth(320)
        self.main.repo_combo.addItems(self.main.backend.settings.get("recent_repos", []))
        self.main.repo_combo.setCurrentText(self.main._repo_path)
        repo_row.addWidget(self.main.repo_combo, 1)

        self.main.browse_btn = GhostButton("Browse", self.main._skin_tokens, repo_surface)
        self.main.browse_btn.clicked.connect(self.main.choose_repo)
        self._register_skinnable(self.main.browse_btn)
        repo_row.addWidget(self.main.browse_btn)

        self.main.reindex_btn = AccentButton("Index", self.main._skin_tokens, repo_surface, strong=True)
        self.main.reindex_btn.clicked.connect(self.main.start_indexing)
        self._register_skinnable(self.main.reindex_btn)
        repo_row.addWidget(self.main.reindex_btn)

        repo_layout.addLayout(repo_row)
        toolbar.addWidget(repo_surface)

        search_surface = self._create_surface("workspaceSearchSurface")
        search_layout = QVBoxLayout(search_surface)
        search_layout.setContentsMargins(10, 8, 10, 8)
        search_layout.setSpacing(4)
        search_layout.addWidget(self._build_section_caption("Search", parent=search_surface))

        search_row = QHBoxLayout()
        search_row.setContentsMargins(0, 0, 0, 0)
        search_row.setSpacing(6)

        self.main.search_box = QLineEdit(search_surface)
        self.main.search_box.setObjectName("heroSearchBox")
        self.main.search_box.setPlaceholderText("Search files, symbols, paths, imports, snippets...")
        self.main.search_box.setMinimumWidth(280)
        self.main.search_box.returnPressed.connect(self.main.start_search)
        search_row.addWidget(self.main.search_box, 1)

        self.main.search_btn = AccentButton("Search", self.main._skin_tokens, search_surface, strong=True)
        self.main.search_btn.clicked.connect(self.main.start_search)
        self._register_skinnable(self.main.search_btn)
        search_row.addWidget(self.main.search_btn)

        search_layout.addLayout(search_row)
        toolbar.addWidget(search_surface)

        nav_surface = self._create_surface("workspaceNavSurface")
        nav_layout = QVBoxLayout(nav_surface)
        nav_layout.setContentsMargins(10, 8, 10, 8)
        nav_layout.setSpacing(4)
        nav_layout.addWidget(self._build_section_caption("Navigate", parent=nav_surface))

        nav_row = QHBoxLayout()
        nav_row.setContentsMargins(0, 0, 0, 0)
        nav_row.setSpacing(6)

        self.main.back_action = self._create_action(
            "Back",
            shortcut="Alt+Left",
            callback=self.main.navigate_back,
            tooltip="Navigate to the previous preview",
        )
        back_button = QuietButton("Back", self.main._skin_tokens, nav_surface)
        self._bind_action_button(self.main.back_action, back_button)
        self._register_skinnable(back_button)
        nav_row.addWidget(back_button)

        self.main.forward_action = self._create_action(
            "Forward",
            shortcut="Alt+Right",
            callback=self.main.navigate_forward,
            tooltip="Navigate to the next preview",
        )
        forward_button = QuietButton("Forward", self.main._skin_tokens, nav_surface)
        self._bind_action_button(self.main.forward_action, forward_button)
        self._register_skinnable(forward_button)
        nav_row.addWidget(forward_button)

        self.main.bookmark_action = self._create_action(
            "Bookmark",
            shortcut="Ctrl+D",
            callback=self.main.add_current_preview_bookmark,
            tooltip="Save the current preview as a bookmark",
        )
        bookmark_button = QuietButton("Bookmark", self.main._skin_tokens, nav_surface)
        self._bind_action_button(self.main.bookmark_action, bookmark_button)
        self._register_skinnable(bookmark_button)
        nav_row.addWidget(bookmark_button)

        nav_layout.addLayout(nav_row)
        toolbar.addWidget(nav_surface)

        spacer = QWidget(self.main)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        settings_surface = self._create_surface("workspaceSettingsSurface")
        settings_layout = QVBoxLayout(settings_surface)
        settings_layout.setContentsMargins(10, 8, 10, 8)
        settings_layout.setSpacing(4)
        settings_layout.addWidget(self._build_section_caption("Settings", parent=settings_surface))

        settings_row = QHBoxLayout()
        settings_row.setContentsMargins(0, 0, 0, 0)
        settings_row.setSpacing(6)

        self.main.preferences_btn = SecondaryButton("Preferences", self.main._skin_tokens, settings_surface)
        self.main.preferences_btn.clicked.connect(self.main.open_preferences_dialog)
        self._register_skinnable(self.main.preferences_btn)
        settings_row.addWidget(self.main.preferences_btn)

        self.main.skin_combo = QComboBox(settings_surface)
        self.main.skin_combo.setObjectName("skinComboBox")
        self.main.skin_combo.setMinimumWidth(160)
        from .skins import list_skins

        for skin in list_skins():
            self.main.skin_combo.addItem(skin.display_name, skin.name)
        self.main.skin_combo.currentIndexChanged.connect(self.main.on_skin_combo_changed)
        settings_row.addWidget(self.main.skin_combo)

        settings_layout.addLayout(settings_row)
        toolbar.addWidget(settings_surface)

    def _build_command_toolbar(self) -> None:
        """
        Build secondary compatibility toolbar.

        This toolbar is hidden by default and acts as an additive hook zone for
        legacy toolbar contributions and advanced shell controls.
        """
        toolbar = QToolBar("CompatibilityToolbar", self.main)
        toolbar.setObjectName("CommandToolbar")
        toolbar.setProperty("visualRole", "toolbar-surface")
        toolbar.setProperty("visualTier", "themed")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.main.addToolBar(Qt.TopToolBarArea, toolbar)
        self.main.command_toolbar = toolbar
        toolbar.hide()

        filters_surface = self._create_surface("commandFiltersSurface")
        filters_layout = QVBoxLayout(filters_surface)
        filters_layout.setContentsMargins(10, 8, 10, 8)
        filters_layout.setSpacing(4)
        filters_layout.addWidget(self._build_section_caption("Advanced Filters", parent=filters_surface))

        filters_row = QHBoxLayout()
        filters_row.setContentsMargins(0, 0, 0, 0)
        filters_row.setSpacing(6)

        self.main.quick_filter_combo = QComboBox(filters_surface)
        self.main.quick_filter_combo.setObjectName("quickFilterComboBox")
        self.main.quick_filter_combo.setMinimumWidth(180)
        self.main.quick_filter_combo.currentIndexChanged.connect(self.main.on_quick_filter_selected)
        filters_row.addWidget(self.main.quick_filter_combo)

        self.main.ext_combo = QComboBox(filters_surface)
        self.main.ext_combo.setObjectName("extComboBox")
        self.main.ext_combo.setMinimumWidth(128)
        self.main.ext_combo.currentIndexChanged.connect(self.main.on_filter_inputs_changed)
        filters_row.addWidget(self.main.ext_combo)

        self.main.sort_combo = QComboBox(filters_surface)
        self.main.sort_combo.setObjectName("sortComboBox")
        self.main.sort_combo.setMinimumWidth(120)
        self.main.sort_combo.addItems(["path", "modified", "size", "ext"])
        filters_row.addWidget(self.main.sort_combo)

        filters_layout.addLayout(filters_row)
        toolbar.addWidget(filters_surface)

        layout_surface = self._create_surface("commandLayoutSurface")
        layout_layout = QVBoxLayout(layout_surface)
        layout_layout.setContentsMargins(10, 8, 10, 8)
        layout_layout.setSpacing(4)
        layout_layout.addWidget(self._build_section_caption("Shell Layout", parent=layout_surface))

        layout_row = QHBoxLayout()
        layout_row.setContentsMargins(0, 0, 0, 0)
        layout_row.setSpacing(6)

        self.main.focus_action = self._create_action(
            "Focus Layout",
            shortcut="Ctrl+1",
            callback=self.main.apply_focus_layout,
            tooltip="Hide secondary shell surfaces and keep focus on active tool",
        )
        focus_button = SecondaryButton("Focus", self.main._skin_tokens, layout_surface)
        self._bind_action_button(self.main.focus_action, focus_button)
        self._register_skinnable(focus_button)
        layout_row.addWidget(focus_button)

        self.main.default_layout_action = self._create_action(
            "Balanced Layout",
            shortcut="Ctrl+0",
            callback=self.main.reset_layout,
            tooltip="Restore balanced shell surfaces",
        )
        reset_button = GhostButton("Balanced", self.main._skin_tokens, layout_surface)
        self._bind_action_button(self.main.default_layout_action, reset_button)
        self._register_skinnable(reset_button)
        layout_row.addWidget(reset_button)

        layout_layout.addLayout(layout_row)
        toolbar.addWidget(layout_surface)

    def _wire_runtime_events(self) -> None:
        bus = getattr(self.main, "event_bus", None)
        if bus is None or not hasattr(bus, "subscribe") or self._runtime_unsubscribers:
            return

        for event_name in (
            Events.TOOL_REGISTERED,
            Events.TOOL_ACTIVATED,
            Events.TOOL_DEACTIVATED,
            Events.TOOL_LIFECYCLE_TRANSITION,
            Events.SHELL_GROUP_CHANGED,
        ):
            try:
                if event_name == Events.SHELL_GROUP_CHANGED:
                    unsub = bus.subscribe(event_name, lambda _payload=None: self.refresh_group_selector())
                else:
                    unsub = bus.subscribe(event_name, lambda _payload=None: self.refresh_tool_switcher())
                self._runtime_unsubscribers.append(unsub)
            except Exception:
                continue

    def _on_group_selected(self, group_id: str) -> None:
        activate = getattr(self.main, "activate_shell_group", None)
        if callable(activate):
            activate(group_id, reason="toolbar-group")
        self.refresh_group_selector()

    def _on_tool_switch_selected(self, index: int) -> None:
        if self._switch_signals_blocked or index < 0:
            return
        combo = getattr(self.main, "tool_switch_combo", None)
        if combo is None:
            return
        tool_id = str(combo.itemData(index) or "").strip()
        if not tool_id:
            return
        workspace = getattr(self.main, "tool_workspace", None)
        if workspace is None:
            return
        if str(getattr(workspace, "active_tool_id", "") or "") == tool_id:
            return
        route_for_tool = getattr(self.main, "activate_group_for_tool", None)
        if callable(route_for_tool):
            route_for_tool(tool_id, reason="toolbar-switch")
        workspace.activate_tool(tool_id, reason="toolbar-switch")

    def _reopen_last_tool(self) -> None:
        reopen_via_group = getattr(self.main, "reopen_last_tool_via_group", None)
        if callable(reopen_via_group):
            reopen_via_group(reason="toolbar-reopen")
            return
        workspace = getattr(self.main, "tool_workspace", None)
        if workspace is not None:
            workspace.reopen_last_active_tool()

    def _create_surface(self, object_name: str, *, role: str = "panel-surface", tier: str = "themed") -> QFrame:
        frame = QFrame(self.main)
        frame.setObjectName(object_name)
        frame.setFrameShape(QFrame.NoFrame)
        frame.setProperty("visualRole", role)
        frame.setProperty("visualTier", tier)
        return frame

    def _build_section_caption(self, text: str, *, parent: QWidget | None = None) -> QLabel:
        label = QLabel(text, parent or self.main)
        label.setObjectName("toolbarSectionCaption")
        return label

    def _create_action(
        self,
        text: str,
        *,
        callback,
        shortcut: str | None = None,
        tooltip: str | None = None,
    ) -> QAction:
        action = QAction(text, self.main)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        if tooltip:
            action.setToolTip(tooltip)
            action.setStatusTip(tooltip)
        action.triggered.connect(callback)
        self.main.addAction(action)
        return action

    def _bind_action_button(self, action: QAction, button: QWidget) -> None:
        button.clicked.connect(lambda checked=False, a=action: a.trigger())
        if not action.shortcut().isEmpty():
            button.setShortcut(action.shortcut())

        def _sync() -> None:
            try:
                button.setEnabled(action.isEnabled())
                shortcut_text = action.shortcut().toString()
                tooltip = action.toolTip() or action.statusTip() or action.text()
                if shortcut_text:
                    tooltip = f"{tooltip} ({shortcut_text})"
                button.setToolTip(tooltip)
                button.setStatusTip(tooltip)
            except Exception:
                pass

        action.changed.connect(_sync)
        _sync()

    def _register_skinnable(self, widget: Any) -> None:
        self.buttons.append(widget)

    def add_plugin_action(self, contribution: ToolbarActionContribution) -> QAction:
        """
        Add plugin-provided action through compatibility toolbar.

        Product-facing canonical entry remains Tools launcher/menu; plugin toolbar
        actions are still wired for compatibility and diagnostics.
        """
        toolbar = self._resolve_toolbar(contribution.target)
        action = QAction(contribution.text, self.main)
        action.setObjectName(
            f"plugin_action_{self._sanitize_action_name(contribution.contribution_id)}"
        )
        action.setProperty("pluginContributionId", contribution.contribution_id)
        action.setProperty("pluginContributionKind", "toolbar")
        if contribution.shortcut:
            action.setShortcut(QKeySequence(contribution.shortcut))
        if contribution.tooltip:
            action.setToolTip(contribution.tooltip)
            action.setStatusTip(contribution.tooltip)
        action.triggered.connect(
            lambda checked=False, callback=contribution.callback: callback()
        )
        toolbar.addAction(action)
        self.plugin_actions.append(action)
        return action

    def _resolve_toolbar(self, target: str) -> QToolBar:
        preferences_runtime = getattr(self.main, "preferences_runtime", None)
        include_dev_tools = bool(
            getattr(getattr(preferences_runtime, "current", None), "include_dev_tools", False)
        )
        if include_dev_tools and str(target).strip().lower() == "workspace":
            return self.main.workspace_toolbar
        return self.main.command_toolbar

    def _sanitize_action_name(self, value: str) -> str:
        sanitized = "".join(ch if ch.isalnum() else "_" for ch in value.strip().lower())
        return sanitized.strip("_") or "plugin"

    def apply_skin_to_buttons(self, skin_tokens: SkinTokens) -> None:
        """Apply active skin tokens to toolbar buttons that support set_skin."""
        from .widgets import install_hover_raise

        for button in self.buttons:
            if hasattr(button, "set_skin"):
                button.set_skin(skin_tokens)
                install_hover_raise(button, 1.5)
