from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..widgets import MetricTile, PanelCard

_REPO_ROOT = Path(__file__).resolve().parents[6]
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)

from forgeos.shared.pyside6_glass.scene import (
    build_glass_dialog_scene as shared_build_glass_dialog_scene,
)

if TYPE_CHECKING:
    from ..main_window import RepoAnalyzerMainWindow
    from ..skins import SkinTokens


class CentralWorkspaceBuilder:
    """Prepare central workspace panels and host a neutral center canvas."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window

    def build(self, skin_tokens: SkinTokens) -> None:
        """
        Build central workspace assets.

        The user-facing workspace surfaces are prepared here and later attached as
        movable QDockWidgets by DockManager.
        """
        central = QWidget(self.main)
        central.setObjectName('workspaceCanvasRootSurface')
        central.setProperty('visualRole', 'workspace-root')
        central.setProperty('visualTier', 'premium')
        outer, content_layer, backdrop = shared_build_glass_dialog_scene(
            central,
            margins=(10, 10, 10, 10),
            apply_stylesheet=False,
            variant='selector',
        )
        outer.setSpacing(0)
        self.main._glass_backdrop = backdrop

        stage_layout = QVBoxLayout(content_layer)
        stage_layout.setContentsMargins(8, 8, 8, 8)
        stage_layout.setSpacing(0)

        shell = QFrame(content_layer)
        shell.setObjectName('Shell')
        shell.setProperty('variant', 'selector')
        shell.setProperty('visualRole', 'workspace-surface')
        shell.setProperty('visualTier', 'premium')
        stage_layout.addWidget(shell, 1)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(10, 10, 10, 10)
        shell_layout.setSpacing(0)

        canvas_hint = QWidget(shell)
        canvas_hint.setObjectName('workspaceCanvasSurface')
        canvas_hint.setProperty('visualRole', 'workspace-surface')
        canvas_hint.setProperty('visualTier', 'themed')
        shell_layout.addWidget(canvas_hint, 1)
        self.main.setCentralWidget(central)

        self.main.workspace_summary_panel = self._build_hero_card(skin_tokens, self.main)
        self.main.preview_workspace_panel = self.main.preview_controller.build_preview_panel(
            skin_tokens,
            self.main,
        )
        self.main.central_inspector_panel = self.main.preview_controller.build_inspector_panel(
            skin_tokens,
            self.main,
        )
        self.main.central_splitter = None

    def _build_hero_card(self, skin_tokens: SkinTokens, parent: QWidget) -> PanelCard:
        card = PanelCard(skin_tokens, accent=True, parent=parent)
        card.setProperty('visualRole', 'hero-surface')
        card.setProperty('visualTier', 'premium')
        card.setProperty('premium', True)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        header_row = QHBoxLayout()
        header_left = QVBoxLayout()
        header_left.setContentsMargins(0, 0, 0, 0)
        header_left.setSpacing(2)

        self.main.hero_repo_label = QLabel("No repository indexed", card)
        self.main.hero_repo_label.setObjectName("heroTitleLabel")
        self.main.hero_scope_label = QLabel(
            "Select a repository to start structural analysis",
            card,
        )
        self.main.hero_scope_label.setObjectName("workspaceMutedLabel")
        header_left.addWidget(self.main.hero_repo_label)
        header_left.addWidget(self.main.hero_scope_label)
        header_row.addLayout(header_left, 1)

        self.main.hero_mode_pill = QLabel("Workbench ready", card)
        self.main.hero_mode_pill.setObjectName("heroMetaPill")
        header_row.addWidget(self.main.hero_mode_pill, 0, Qt.AlignTop)
        layout.addLayout(header_row)

        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(12)
        self.main.metric_repo = MetricTile(skin_tokens, "Repo", card)
        self.main.metric_files = MetricTile(skin_tokens, "Files", card)
        self.main.metric_scope = MetricTile(skin_tokens, "Scope", card)
        self.main.metric_results = MetricTile(skin_tokens, "Results", card)

        for tile in (
            self.main.metric_repo,
            self.main.metric_files,
            self.main.metric_scope,
            self.main.metric_results,
        ):
            metrics_row.addWidget(tile, 1)
            tile.setProperty('visualRole', 'metric-surface')
            tile.setProperty('premium', True)

        layout.addLayout(metrics_row)
        return card
