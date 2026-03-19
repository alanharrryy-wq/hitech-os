from __future__ import annotations

from typing import TYPE_CHECKING


from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget

from .shell.dock_sections import DockSectionFactory

if TYPE_CHECKING:
    from .main_window import RepoAnalyzerMainWindow
    from .skins import SkinTokens
    from .ui_contribution_registry import DockContribution


class DockManager:
    """Manages dock widgets setup and organization."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window
        self._sections = DockSectionFactory(main_window)

    def build_docks(self, skin_tokens: SkinTokens) -> None:
        """Create and configure all dock widgets."""
        self.main.workspace_summary_dock = self.register_feature_panel(
            title='Workspace Summary',
            area=Qt.TopDockWidgetArea,
            widget_factory=lambda dock: self._prebuilt_panel('workspace_summary_panel', 'Workspace Summary'),
            skin_tokens=skin_tokens,
            object_name='dock_workspace_summary',
            reason='dock-manager-workspace-summary',
            visual_role='hero-surface',
        )
        self.main.preview_workspace_dock = self.register_feature_panel(
            title='Preview Workspace',
            area=Qt.TopDockWidgetArea,
            widget_factory=lambda dock: self._prebuilt_panel('preview_workspace_panel', 'Preview Workspace'),
            skin_tokens=skin_tokens,
            object_name='dock_preview_workspace',
            reason='dock-manager-preview-workspace',
            visual_role='panel-surface',
        )
        self.main.central_inspector_dock = self.register_feature_panel(
            title='Inspector Central',
            area=Qt.TopDockWidgetArea,
            widget_factory=lambda dock: self._prebuilt_panel('central_inspector_panel', 'Inspector Central'),
            skin_tokens=skin_tokens,
            object_name='dock_central_inspector',
            reason='dock-manager-central-inspector',
            visual_role='panel-surface',
        )

        self.main.explorer_dock = self._make_dock('Explorer', Qt.LeftDockWidgetArea)
        self.main.results_dock = self._make_dock('Results', Qt.BottomDockWidgetArea)

        # Build explorer dock (via tree controller)
        tree_filter_box, repo_tree = self.main.tree_controller.build_tree_dock_widget(skin_tokens)
        self.main.tree_filter_box = tree_filter_box
        self.main.repo_tree = repo_tree

        # Build results dock (via search controller)
        self.main.search_controller.build_results_dock_widget(skin_tokens)

        # Use feature panel helper to reduce repeated dock wiring for core shell surfaces.
        self.main.inspector_dock = self.register_feature_panel(
            title='Inspector',
            area=Qt.RightDockWidgetArea,
            widget_factory=lambda dock: self._sections.build_inspector_section(
                skin_tokens,
                parent=dock,
            ),
            skin_tokens=skin_tokens,
            object_name='dock_inspector',
            reason='dock-manager-inspector-panel',
            visual_role='dock-content-root',
        )
        self.main.bookmarks_dock = self.register_feature_panel(
            title='Bookmarks',
            area=Qt.RightDockWidgetArea,
            widget_factory=lambda dock: self._sections.build_bookmarks_section(
                skin_tokens,
                parent=dock,
            ),
            skin_tokens=skin_tokens,
            object_name='dock_bookmarks',
            reason='dock-manager-bookmarks-panel',
            visual_role='dock-content-root',
        )

        # Tabify and finalize
        self.main.tabifyDockWidget(self.main.inspector_dock, self.main.bookmarks_dock)
        self.main.inspector_dock.raise_()
        self.main.splitDockWidget(
            self.main.workspace_summary_dock,
            self.main.preview_workspace_dock,
            Qt.Vertical,
        )
        self.main.splitDockWidget(
            self.main.preview_workspace_dock,
            self.main.central_inspector_dock,
            Qt.Vertical,
        )
        self.main.preview_workspace_dock.raise_()

        self.main.resizeDocks(
            [self.main.explorer_dock, self.main.inspector_dock],
            [350, 420],
            Qt.Horizontal
        )
        self.main.resizeDocks([self.main.results_dock], [300], Qt.Vertical)
        self.main.resizeDocks(
            [
                self.main.workspace_summary_dock,
                self.main.preview_workspace_dock,
                self.main.central_inspector_dock,
            ],
            [220, 420, 280],
            Qt.Vertical,
        )

        # Route all built-in docks through the central visual runtime.
        for dock in (
            self.main.workspace_summary_dock,
            self.main.preview_workspace_dock,
            self.main.central_inspector_dock,
            self.main.explorer_dock,
            self.main.results_dock,
            self.main.inspector_dock,
            self.main.bookmarks_dock,
        ):
            self._prepare_dock_content_root(dock)
            self._process_dock_visual_runtime(dock, skin_tokens, reason='dock-manager-builtins')

    def _prebuilt_panel(self, attr_name: str, label: str):
        panel = getattr(self.main, attr_name, None)
        if panel is None:
            raise RuntimeError(f"Prebuilt panel '{label}' was not prepared before dock attach")
        return panel

    def add_plugin_dock(
        self,
        contribution: DockContribution,
        skin_tokens: SkinTokens | None = None,
    ) -> QDockWidget:
        """Create and attach a plugin-provided dock widget."""
        area = self._resolve_dock_area(contribution.area)
        return self.register_feature_panel(
            title=contribution.title,
            area=area,
            widget_factory=contribution.widget_factory,
            skin_tokens=skin_tokens,
            object_name=f"plugin_dock_{self._sanitize_object_name(contribution.contribution_id)}",
            visible=contribution.visible,
            closable=contribution.closable,
            floatable=contribution.floatable,
            movable=contribution.movable,
            allowed_areas=contribution.allowed_areas,
            reason='dock-manager-plugin',
            visual_role='plugin-dock-root',
        )

    def _resolve_dock_area(self, area) -> Qt.DockWidgetArea:
        """Resolve plugin dock area aliases into Qt dock areas."""
        if isinstance(area, Qt.DockWidgetArea):
            return area

        mapping = {
            'left': Qt.LeftDockWidgetArea,
            'right': Qt.RightDockWidgetArea,
            'top': Qt.TopDockWidgetArea,
            'bottom': Qt.BottomDockWidgetArea,
        }
        return mapping.get(str(area).strip().lower(), Qt.RightDockWidgetArea)

    def _sanitize_object_name(self, value: str) -> str:
        """Make a safe objectName fragment for plugin docks."""
        sanitized = ''.join(ch if ch.isalnum() else '_' for ch in value.strip().lower())
        return sanitized.strip('_') or 'plugin'

    def _make_dock(self, title: str, area) -> QDockWidget:
        """Create a dock widget."""
        dock = QDockWidget(title, self.main)
        dock.setObjectName(f'dock_{title.lower()}')
        dock.setProperty('visualTier', 'themed')
        dock.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
            | QDockWidget.DockWidgetClosable
        )
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        dock.setProperty('visualRole', 'dock-shell')
        self.main.addDockWidget(area, dock)
        return dock

    def register_feature_panel(
        self,
        *,
        title: str,
        area,
        widget_factory,
        skin_tokens: SkinTokens | None = None,
        object_name: str = '',
        visible: bool = True,
        closable: bool = True,
        floatable: bool = True,
        movable: bool = True,
        allowed_areas=None,
        reason: str = 'dock-manager-feature-panel',
        visual_role: str = 'dock-content-root',
    ) -> QDockWidget:
        """
        Register and attach a feature dock panel through one safe, idempotent path.

        This helper is the default fast path for new core panels and plugin docks.
        """
        dock = self._make_dock(title, area)
        if object_name:
            dock.setObjectName(object_name)

        features = QDockWidget.NoDockWidgetFeatures
        if movable:
            features |= QDockWidget.DockWidgetMovable
        if floatable:
            features |= QDockWidget.DockWidgetFloatable
        if closable:
            features |= QDockWidget.DockWidgetClosable
        dock.setFeatures(features)

        if allowed_areas is not None:
            dock.setAllowedAreas(allowed_areas)

        widget = widget_factory(dock)
        if widget is None:
            raise RuntimeError(f"Feature panel '{title}' did not return a widget")

        dock.setWidget(widget)
        if visual_role and not widget.property('visualRole'):
            widget.setProperty('visualRole', visual_role)
        widget.setProperty('dockContentRoot', True)

        self._prepare_dock_content_root(dock)
        self._process_dock_visual_runtime(dock, skin_tokens, reason=reason)

        if not visible:
            dock.hide()

        diagnostics = getattr(self.main, 'runtime_diagnostics', None)
        if diagnostics is not None and hasattr(diagnostics, 'trace'):
            diagnostics.trace(
                'dock-manager',
                'feature panel attached',
                title=title,
                object_name=dock.objectName(),
                reason=reason,
            )

        return dock

    def _prepare_dock_content_root(self, dock: QDockWidget) -> None:
        """Mark dock content root so visual runtime can classify it deterministically."""
        widget = dock.widget()
        if widget is None:
            return

        if not widget.property('visualRole'):
            if dock.objectName().startswith('plugin_dock_'):
                widget.setProperty('visualRole', 'plugin-dock-root')
            else:
                widget.setProperty('visualRole', 'dock-content-root')
        widget.setProperty('dockContentRoot', True)

    def _process_dock_visual_runtime(
        self,
        dock: QDockWidget,
        skin_tokens: SkinTokens | None,
        *,
        reason: str,
    ) -> None:
        runtime = getattr(self.main, 'visual_runtime', None)
        if runtime is None:
            return

        tokens = skin_tokens or getattr(self.main, '_skin_tokens', None)
        if tokens is None:
            return

        try:
            report = runtime.process_dock_widget(
                dock,
                tokens=tokens,
                reason=reason,
            )
            diagnostics = getattr(self.main, 'runtime_diagnostics', None)
            if diagnostics is not None and hasattr(diagnostics, 'trace'):
                diagnostics.trace(
                    'dock-manager',
                    'dock visual runtime processed',
                    dock=dock.objectName(),
                    discovered=report.discovered,
                    skinned=report.skin_applied,
                    effects=report.effects_applied,
                    failures=report.failures,
                )
        except Exception as exc:
            logger = getattr(self.main, 'log', None)
            if callable(logger):
                logger(f'[dock-manager] visual runtime skipped for {dock.objectName()}: {exc}')
            diagnostics = getattr(self.main, 'runtime_diagnostics', None)
            if diagnostics is not None and hasattr(diagnostics, 'warning'):
                diagnostics.warning(
                    'dock-manager',
                    'visual runtime skipped',
                    dock=dock.objectName(),
                    detail=str(exc),
                )
