from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..widgets import MetricTile, PanelCard

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
        outer = QVBoxLayout(central)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(0)
        canvas_hint = QWidget(central)
        canvas_hint.setObjectName('workspaceCanvasSurface')
        canvas_hint.setProperty('visualRole', 'workspace-surface')
        canvas_hint.setProperty('visualTier', 'themed')
        outer.addWidget(canvas_hint, 1)
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
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        header_row = QHBoxLayout()
        header_left = QVBoxLayout()
        header_left.setContentsMargins(0, 0, 0, 0)
        header_left.setSpacing(2)

        self.main.hero_repo_label = QLabel("Sin repo indexado", card)
        self.main.hero_repo_label.setObjectName("heroTitleLabel")
        self.main.hero_scope_label = QLabel(
            "Selecciona un repositorio para empezar el análisis estructural",
            card,
        )
        self.main.hero_scope_label.setObjectName("workspaceMutedLabel")
        header_left.addWidget(self.main.hero_repo_label)
        header_left.addWidget(self.main.hero_scope_label)
        header_row.addLayout(header_left, 1)

        self.main.hero_mode_pill = QLabel("Workbench listo", card)
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
