from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSplitter, QVBoxLayout, QWidget

from ..widgets import MetricTile, PanelCard

if TYPE_CHECKING:
    from ..main_window import RepoAnalyzerMainWindow
    from ..skins import SkinTokens


class CentralWorkspaceBuilder:
    """Compose the permanent central shell workspace."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window

    def build(self, skin_tokens: SkinTokens) -> None:
        """Build hero + metrics + preview/inspector splitter."""
        central = QWidget(self.main)
        central.setObjectName('workspaceRootSurface')
        central.setProperty('visualRole', 'workspace-root')
        central.setProperty('visualTier', 'themed')
        outer = QVBoxLayout(central)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        hero_card = self._build_hero_card(skin_tokens, central)
        outer.addWidget(hero_card)

        self.main.central_splitter = QSplitter(Qt.Vertical, central)
        self.main.central_splitter.setObjectName('workspaceSplitterSurface')
        self.main.central_splitter.setProperty('visualRole', 'workspace-surface')
        self.main.central_splitter.setProperty('visualTier', 'themed')
        outer.addWidget(self.main.central_splitter, 1)

        preview_card = self.main.preview_controller.build_preview_panel(
            skin_tokens,
            self.main.central_splitter,
        )
        inspector_card = self.main.preview_controller.build_inspector_panel(
            skin_tokens,
            self.main.central_splitter,
        )

        self.main.central_splitter.addWidget(preview_card)
        self.main.central_splitter.addWidget(inspector_card)
        self.main.central_splitter.setSizes([760, 300])

        self.main.setCentralWidget(central)

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

        self.main.hero_repo_label = QLabel("Sin repo indexado", card)
        self.main.hero_repo_label.setObjectName("heroTitleLabel")
        self.main.hero_scope_label = QLabel(
            "Selecciona un repo para empezar a mapearlo",
            card,
        )
        self.main.hero_scope_label.setObjectName("workspaceMutedLabel")
        header_left.addWidget(self.main.hero_repo_label)
        header_left.addWidget(self.main.hero_scope_label)
        header_row.addLayout(header_left, 1)

        self.main.hero_mode_pill = QLabel("Workspace listo", card)
        self.main.hero_mode_pill.setObjectName("heroMetaPill")
        header_row.addWidget(self.main.hero_mode_pill, 0, Qt.AlignTop)
        layout.addLayout(header_row)

        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(10)
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
