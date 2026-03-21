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

from .widgets import AccentButton, GhostButton, QuietButton, SecondaryButton

if TYPE_CHECKING:
    from .main_window import RepoAnalyzerMainWindow
    from .skins import SkinTokens
    from .ui_contribution_registry import ToolbarActionContribution


class ToolbarController:
    """Manages workspace and command toolbar composition."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window
        self.buttons: list[Any] = []
        self.plugin_actions: list[QAction] = []

    def build_toolbar(self) -> None:
        """Build workspace and command decks."""
        self._build_workspace_toolbar()
        self.main.addToolBarBreak(Qt.TopToolBarArea)
        self._build_command_toolbar()

    def _build_workspace_toolbar(self) -> None:
        """Build top workspace deck with hero, repo, navigation, and skin controls."""
        toolbar = QToolBar('WorkspaceToolbar', self.main)
        toolbar.setObjectName('WorkspaceToolbar')
        toolbar.setProperty('visualRole', 'toolbar-surface')
        toolbar.setProperty('visualTier', 'themed')
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.main.addToolBar(Qt.TopToolBarArea, toolbar)
        self.main.workspace_toolbar = toolbar

        hero_surface = self._create_surface('workspaceHeroSurface', role='hero-surface', tier='premium')
        hero_layout = QVBoxLayout(hero_surface)
        hero_layout.setContentsMargins(18, 12, 18, 12)
        hero_layout.setSpacing(4)

        hero_top = QHBoxLayout()
        hero_top.setContentsMargins(0, 0, 0, 0)
        hero_top.setSpacing(7)

        title = QLabel('Repo Analyzer', hero_surface)
        title.setObjectName('heroTitleLabel')
        hero_top.addWidget(title)
        hero_top.addStretch(1)

        product_pill = QLabel('ENGINEERING CONSOLE', hero_surface)
        product_pill.setObjectName('heroMetaPill')
        hero_top.addWidget(product_pill)
        hero_layout.addLayout(hero_top)

        subtitle = QLabel(
            'Calm shell for repository search, structural review, and controlled navigation.',
            hero_surface,
        )
        subtitle.setObjectName('subtitleLabel')
        subtitle.setWordWrap(True)
        subtitle.setMinimumWidth(420)
        hero_layout.addWidget(subtitle)
        toolbar.addWidget(hero_surface)

        repo_surface = self._create_surface('workspaceRepoSurface')
        repo_layout = QVBoxLayout(repo_surface)
        repo_layout.setContentsMargins(12, 10, 12, 10)
        repo_layout.setSpacing(6)
        repo_layout.addWidget(self._build_section_caption('REPOSITORY CONTROL', parent=repo_surface))

        repo_row = QHBoxLayout()
        repo_row.setContentsMargins(0, 0, 0, 0)
        repo_row.setSpacing(7)

        self.main.repo_combo = QComboBox(repo_surface)
        self.main.repo_combo.setObjectName('repoComboBox')
        self.main.repo_combo.setEditable(True)
        self.main.repo_combo.setMinimumWidth(360)
        self.main.repo_combo.addItems(self.main.backend.settings.get('recent_repos', []))
        self.main.repo_combo.setCurrentText(self.main._repo_path)
        repo_row.addWidget(self.main.repo_combo, 1)

        self.main.browse_btn = GhostButton('Browse', self.main._skin_tokens, repo_surface)
        self.main.browse_btn.clicked.connect(self.main.choose_repo)
        self._register_skinnable(self.main.browse_btn)
        repo_row.addWidget(self.main.browse_btn)

        self.main.reindex_btn = AccentButton('Reindex', self.main._skin_tokens, repo_surface, strong=True)
        self.main.reindex_btn.clicked.connect(self.main.start_indexing)
        self._register_skinnable(self.main.reindex_btn)
        repo_row.addWidget(self.main.reindex_btn)

        repo_layout.addLayout(repo_row)
        toolbar.addWidget(repo_surface)

        nav_surface = self._create_surface('workspaceNavSurface')
        nav_layout = QVBoxLayout(nav_surface)
        nav_layout.setContentsMargins(12, 10, 12, 10)
        nav_layout.setSpacing(6)
        nav_layout.addWidget(self._build_section_caption('NAVIGATION', parent=nav_surface))

        nav_row = QHBoxLayout()
        nav_row.setContentsMargins(0, 0, 0, 0)
        nav_row.setSpacing(7)

        self.main.back_action = self._create_action(
            'Back',
            shortcut='Alt+Left',
            callback=self.main.navigate_back,
            tooltip='Navigate to the previous preview',
        )
        back_button = QuietButton('Back', self.main._skin_tokens, nav_surface)
        self._bind_action_button(self.main.back_action, back_button)
        self._register_skinnable(back_button)
        nav_row.addWidget(back_button)

        self.main.forward_action = self._create_action(
            'Forward',
            shortcut='Alt+Right',
            callback=self.main.navigate_forward,
            tooltip='Navigate to the next preview',
        )
        forward_button = QuietButton('Forward', self.main._skin_tokens, nav_surface)
        self._bind_action_button(self.main.forward_action, forward_button)
        self._register_skinnable(forward_button)
        nav_row.addWidget(forward_button)

        self.main.bookmark_action = self._create_action(
            'Bookmark',
            shortcut='Ctrl+D',
            callback=self.main.add_current_preview_bookmark,
            tooltip='Save the current preview as a bookmark',
        )
        bookmark_button = QuietButton('Bookmark', self.main._skin_tokens, nav_surface)
        self._bind_action_button(self.main.bookmark_action, bookmark_button)
        self._register_skinnable(bookmark_button)
        nav_row.addWidget(bookmark_button)

        nav_row.addStretch(1)
        nav_layout.addLayout(nav_row)
        toolbar.addWidget(nav_surface)

        spacer = QWidget(self.main)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        skin_surface = self._create_surface('workspaceSkinSurface')
        skin_layout = QVBoxLayout(skin_surface)
        skin_layout.setContentsMargins(12, 10, 12, 10)
        skin_layout.setSpacing(6)
        skin_layout.addWidget(self._build_section_caption('VISUAL SKIN', parent=skin_surface))

        self.main.skin_combo = QComboBox(skin_surface)
        self.main.skin_combo.setObjectName('skinComboBox')
        self.main.skin_combo.setMinimumWidth(200)
        from .skins import list_skins

        for skin in list_skins():
            self.main.skin_combo.addItem(skin.display_name, skin.name)
        self.main.skin_combo.currentIndexChanged.connect(self.main.on_skin_combo_changed)
        skin_layout.addWidget(self.main.skin_combo)
        toolbar.addWidget(skin_surface)

    def _build_command_toolbar(self) -> None:
        """Build the search, filters, and layout command deck."""
        toolbar = QToolBar('CommandToolbar', self.main)
        toolbar.setObjectName('CommandToolbar')
        toolbar.setProperty('visualRole', 'toolbar-surface')
        toolbar.setProperty('visualTier', 'themed')
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.main.addToolBar(Qt.TopToolBarArea, toolbar)
        self.main.command_toolbar = toolbar

        search_surface = self._create_surface('commandDeckSurface', role='toolbar-surface', tier='premium')
        search_layout = QVBoxLayout(search_surface)
        search_layout.setContentsMargins(12, 10, 12, 10)
        search_layout.setSpacing(6)
        search_layout.addWidget(self._build_section_caption('SEARCH DECK', parent=search_surface))

        search_row = QHBoxLayout()
        search_row.setContentsMargins(0, 0, 0, 0)
        search_row.setSpacing(7)

        self.main.search_box = QLineEdit(search_surface)
        self.main.search_box.setObjectName('heroSearchBox')
        self.main.search_box.setPlaceholderText('Search files, symbols, paths, imports, snippets...')
        self.main.search_box.setMinimumWidth(360)
        self.main.search_box.returnPressed.connect(self.main.start_search)
        search_row.addWidget(self.main.search_box, 1)

        self.main.search_btn = AccentButton('Search', self.main._skin_tokens, search_surface, strong=True)
        self.main.search_btn.clicked.connect(self.main.start_search)
        self._register_skinnable(self.main.search_btn)
        search_row.addWidget(self.main.search_btn)

        search_layout.addLayout(search_row)
        toolbar.addWidget(search_surface)

        filters_surface = self._create_surface('commandFiltersSurface')
        filters_layout = QVBoxLayout(filters_surface)
        filters_layout.setContentsMargins(12, 10, 12, 10)
        filters_layout.setSpacing(6)
        filters_layout.addWidget(self._build_section_caption('SMART FILTERS', parent=filters_surface))

        filters_row = QHBoxLayout()
        filters_row.setContentsMargins(0, 0, 0, 0)
        filters_row.setSpacing(7)

        self.main.quick_filter_combo = QComboBox(filters_surface)
        self.main.quick_filter_combo.setObjectName('quickFilterComboBox')
        self.main.quick_filter_combo.setMinimumWidth(190)
        self.main.quick_filter_combo.currentIndexChanged.connect(self.main.on_quick_filter_selected)
        filters_row.addWidget(self.main.quick_filter_combo)

        self.main.ext_combo = QComboBox(filters_surface)
        self.main.ext_combo.setObjectName('extComboBox')
        self.main.ext_combo.setMinimumWidth(128)
        self.main.ext_combo.currentIndexChanged.connect(self.main.on_filter_inputs_changed)
        filters_row.addWidget(self.main.ext_combo)

        self.main.sort_combo = QComboBox(filters_surface)
        self.main.sort_combo.setObjectName('sortComboBox')
        self.main.sort_combo.setMinimumWidth(120)
        self.main.sort_combo.addItems(['path', 'modified', 'size', 'ext'])
        filters_row.addWidget(self.main.sort_combo)

        filters_layout.addLayout(filters_row)
        toolbar.addWidget(filters_surface)

        layout_surface = self._create_surface('commandLayoutSurface')
        layout_layout = QVBoxLayout(layout_surface)
        layout_layout.setContentsMargins(12, 10, 12, 10)
        layout_layout.setSpacing(6)
        layout_layout.addWidget(self._build_section_caption('LAYOUT MODES', parent=layout_surface))

        layout_row = QHBoxLayout()
        layout_row.setContentsMargins(0, 0, 0, 0)
        layout_row.setSpacing(7)

        self.main.focus_action = self._create_action(
            'Focus Layout',
            shortcut='Ctrl+1',
            callback=self.main.apply_focus_layout,
            tooltip='Collapse the chrome and focus on the active work area',
        )
        focus_button = SecondaryButton('Focus Layout', self.main._skin_tokens, layout_surface)
        self._bind_action_button(self.main.focus_action, focus_button)
        self._register_skinnable(focus_button)
        layout_row.addWidget(focus_button)

        self.main.default_layout_action = self._create_action(
            'Balanced Layout',
            shortcut='Ctrl+0',
            callback=self.main.reset_layout,
            tooltip='Restore the balanced engineering workstation layout',
        )
        reset_button = GhostButton('Balanced Layout', self.main._skin_tokens, layout_surface)
        self._bind_action_button(self.main.default_layout_action, reset_button)
        self._register_skinnable(reset_button)
        layout_row.addWidget(reset_button)

        layout_layout.addLayout(layout_row)
        toolbar.addWidget(layout_surface)

    def _create_surface(self, object_name: str, *, role: str = 'panel-surface', tier: str = 'themed') -> QFrame:
        frame = QFrame(self.main)
        frame.setObjectName(object_name)
        frame.setFrameShape(QFrame.NoFrame)
        frame.setProperty('visualRole', role)
        frame.setProperty('visualTier', tier)
        return frame

    def _build_section_caption(self, text: str, *, parent: QWidget | None = None) -> QLabel:
        label = QLabel(text, parent or self.main)
        label.setObjectName('toolbarSectionCaption')
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
                    tooltip = f'{tooltip} ({shortcut_text})'
                button.setToolTip(tooltip)
                button.setStatusTip(tooltip)
            except Exception:
                pass

        action.changed.connect(_sync)
        _sync()

    def _register_skinnable(self, widget: Any) -> None:
        self.buttons.append(widget)

    def add_plugin_action(self, contribution: ToolbarActionContribution) -> QAction:
        """Add a plugin-provided action to a supported toolbar."""
        toolbar = self._resolve_toolbar(contribution.target)
        action = QAction(contribution.text, self.main)
        action.setObjectName(
            f"plugin_action_{self._sanitize_action_name(contribution.contribution_id)}"
        )
        action.setProperty('pluginContributionId', contribution.contribution_id)
        action.setProperty('pluginContributionKind', 'toolbar')
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
        """Resolve toolbar aliases to concrete toolbar instances."""
        if str(target).strip().lower() == 'workspace':
            return self.main.workspace_toolbar
        return self.main.command_toolbar

    def _sanitize_action_name(self, value: str) -> str:
        """Make a safe objectName fragment for plugin toolbar actions."""
        sanitized = ''.join(ch if ch.isalnum() else '_' for ch in value.strip().lower())
        return sanitized.strip('_') or 'plugin'

    def apply_skin_to_buttons(self, skin_tokens: SkinTokens) -> None:
        """Apply active skin tokens to all toolbar buttons."""
        from .widgets import install_hover_raise

        for button in self.buttons:
            if hasattr(button, 'set_skin'):
                button.set_skin(skin_tokens)
                install_hover_raise(button, 1.5)
