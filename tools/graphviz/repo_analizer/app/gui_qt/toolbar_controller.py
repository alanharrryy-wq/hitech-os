from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QComboBox, QLineEdit, QSizePolicy, QToolBar, QWidget

from .widgets import AccentButton

if TYPE_CHECKING:
    from .main_window import RepoAnalyzerMainWindow
    from .skins import SkinTokens
    from .ui_contribution_registry import ToolbarActionContribution


class ToolbarController:
    """Manages toolbar creation and workspace command controls."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window
        self.buttons: list[AccentButton] = []
        self.plugin_actions: list[QAction] = []

    def build_toolbar(self) -> None:
        """Build workspace and command toolbars."""
        self._build_workspace_toolbar()
        self.main.addToolBarBreak(Qt.TopToolBarArea)
        self._build_command_toolbar()

    def _build_workspace_toolbar(self) -> None:
        """Build the top workspace toolbar with repo selection."""
        from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

        toolbar = QToolBar('WorkspaceToolbar', self.main)
        toolbar.setObjectName('WorkspaceToolbar')
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.main.addToolBar(Qt.TopToolBarArea, toolbar)
        self.main.workspace_toolbar = toolbar

        # Title section
        title_wrap = QWidget(self.main)
        title_layout = QVBoxLayout(title_wrap)
        title_layout.setContentsMargins(0, 0, 12, 0)
        title_layout.setSpacing(0)

        title = QLabel('Repo Analyzer', title_wrap)
        title.setObjectName('heroTitleLabel')
        subtitle = QLabel('Ember Graph Workstation • IDE shell premium para uso diario intenso', title_wrap)
        subtitle.setObjectName('subtitleLabel')
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        toolbar.addWidget(title_wrap)

        # Accent bar
        accent_bar = QFrame(self.main)
        accent_bar.setObjectName('accentBar')
        accent_bar.setFixedSize(4, 42)
        toolbar.addWidget(accent_bar)

        # Repo combo
        self.main.repo_combo = QComboBox(self.main)
        self.main.repo_combo.setEditable(True)
        self.main.repo_combo.setMinimumWidth(520)
        self.main.repo_combo.addItems(self.main.backend.settings.get('recent_repos', []))
        self.main.repo_combo.setCurrentText(self.main._repo_path)
        toolbar.addWidget(self.main.repo_combo)

        # Browse button
        self.main.browse_btn = AccentButton('Browse', self.main._skin_tokens, self.main)
        self.main.browse_btn.clicked.connect(self.main.choose_repo)
        toolbar.addWidget(self.main.browse_btn)
        self.buttons.append(self.main.browse_btn)

        # Reindex button
        self.main.reindex_btn = AccentButton('Reindex', self.main._skin_tokens, self.main, strong=True)
        self.main.reindex_btn.clicked.connect(self.main.start_indexing)
        toolbar.addWidget(self.main.reindex_btn)
        self.buttons.append(self.main.reindex_btn)

        toolbar.addSeparator()

        # Navigation actions
        self.main.back_action = QAction('Back', self.main)
        self.main.back_action.setShortcut(QKeySequence('Alt+Left'))
        self.main.back_action.triggered.connect(self.main.navigate_back)
        toolbar.addAction(self.main.back_action)

        self.main.forward_action = QAction('Forward', self.main)
        self.main.forward_action.setShortcut(QKeySequence('Alt+Right'))
        self.main.forward_action.triggered.connect(self.main.navigate_forward)
        toolbar.addAction(self.main.forward_action)

        self.main.bookmark_action = QAction('Bookmark', self.main)
        self.main.bookmark_action.triggered.connect(self.main.add_current_preview_bookmark)
        toolbar.addAction(self.main.bookmark_action)

        # Spacer
        spacer = QWidget(self.main)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        # Skin combo
        self.main.skin_combo = QComboBox(self.main)
        from .skins import list_skins

        for skin in list_skins():
            self.main.skin_combo.addItem(skin.display_name, skin.name)
        self.main.skin_combo.currentIndexChanged.connect(self.main.on_skin_combo_changed)
        toolbar.addWidget(self.main.skin_combo)

    def _build_command_toolbar(self) -> None:
        """Build the command toolbar with search and filters."""
        toolbar = QToolBar('CommandToolbar', self.main)
        toolbar.setObjectName('CommandToolbar')
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.main.addToolBar(Qt.TopToolBarArea, toolbar)
        self.main.command_toolbar = toolbar

        # Search box
        self.main.search_box = QLineEdit(self.main)
        self.main.search_box.setPlaceholderText('Search repo, symbols, imports, paths...')
        self.main.search_box.setMinimumWidth(420)
        self.main.search_box.returnPressed.connect(self.main.start_search)
        toolbar.addWidget(self.main.search_box)

        # Search button
        self.main.search_btn = AccentButton('Search', self.main._skin_tokens, self.main, strong=True)
        self.main.search_btn.clicked.connect(self.main.start_search)
        toolbar.addWidget(self.main.search_btn)
        self.buttons.append(self.main.search_btn)

        # Quick filter combo
        self.main.quick_filter_combo = QComboBox(self.main)
        self.main.quick_filter_combo.setMinimumWidth(220)
        self.main.quick_filter_combo.currentIndexChanged.connect(self.main.on_quick_filter_selected)
        toolbar.addWidget(self.main.quick_filter_combo)

        # Extension combo
        self.main.ext_combo = QComboBox(self.main)
        self.main.ext_combo.setMinimumWidth(150)
        self.main.ext_combo.currentIndexChanged.connect(self.main.on_filter_inputs_changed)
        toolbar.addWidget(self.main.ext_combo)

        # Sort combo
        self.main.sort_combo = QComboBox(self.main)
        self.main.sort_combo.addItems(['path', 'modified', 'size', 'ext'])
        toolbar.addWidget(self.main.sort_combo)

        toolbar.addSeparator()

        # Layout actions
        self.main.focus_action = QAction('Focus Layout', self.main)
        self.main.focus_action.triggered.connect(self.main.apply_focus_layout)
        toolbar.addAction(self.main.focus_action)

        self.main.default_layout_action = QAction('Ember Layout', self.main)
        self.main.default_layout_action.triggered.connect(self.main.reset_layout)
        toolbar.addAction(self.main.default_layout_action)

    def add_plugin_action(self, contribution: ToolbarActionContribution) -> QAction:
        """Add a plugin-provided action to a supported toolbar."""
        toolbar = self._resolve_toolbar(contribution.target)
        action = QAction(contribution.text, self.main)
        action.setObjectName(
            f"plugin_action_{self._sanitize_action_name(contribution.contribution_id)}"
        )
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
        """Apply skin to all toolbar buttons."""
        from .widgets import install_hover_raise

        for button in self.buttons:
            button.set_skin(skin_tokens)
            install_hover_raise(button, 1.5)
