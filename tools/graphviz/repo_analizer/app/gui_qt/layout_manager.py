from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QMessageBox

if TYPE_CHECKING:
    from .main_window import RepoAnalyzerMainWindow


class LayoutManager:
    """Manages layout save/restore and layout transitions."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window

    def restore_ui_state(self) -> None:
        """Restore saved window geometry and state."""
        geometry = self.main.settings.value('geometry')
        state = self.main.settings.value('window_state_v3')
        
        if geometry:
            self.main.restoreGeometry(geometry)
        if state:
            self.main.restoreState(state, self.main.STATE_VERSION)
        else:
            self.reset_layout(save_snapshot=False)

        # Restore filter settings
        folder_filter = self.main.backend.settings.get('last_folder_filter', '(todo)')
        ext_filter = self.main.backend.settings.get('last_ext_filter', '(todas)')
        self.main._pending_folder_filter = folder_filter
        self.main._pending_ext_filter = ext_filter

        # Restore skin
        skin_name = self.main._skin_tokens.name
        idx = self.main.skin_combo.findData(skin_name)
        if idx >= 0:
            self.main.skin_combo.setCurrentIndex(idx)

        self.main.repo_combo.setCurrentText(str(self.main._repo_path))

        # Initialize combo boxes
        self.main.quick_filter_combo.clear()
        self.main.quick_filter_combo.addItem(self.main.quick_filter_all_label)
        self.main.ext_combo.clear()
        self.main.ext_combo.addItems(['(todas)', 'TS/JS', '(sin extensión)'])
        self.main.folder_combo.clear()
        self.main.folder_combo.addItem('(todo)')
        self.main.refresh_bookmarks_view()

        # Restore splitter sizes
        splitter_sizes = self.main.settings.value('central_splitter_sizes')
        if isinstance(splitter_sizes, list) and splitter_sizes:
            try:
                self.main.central_splitter.setSizes(splitter_sizes)
            except Exception:
                pass

        self.main._update_metric_cards_idle()

    def reset_layout(self, save_snapshot: bool = True) -> None:
        """Reset to default Ember layout."""
        from PySide6.QtCore import Qt

        for dock in (
            self.main.explorer_dock,
            self.main.results_dock,
            self.main.inspector_dock,
            self.main.bookmarks_dock,
        ):
            self.main.removeDockWidget(dock)

        self.main.addDockWidget(Qt.LeftDockWidgetArea, self.main.explorer_dock)
        self.main.addDockWidget(Qt.BottomDockWidgetArea, self.main.results_dock)
        self.main.addDockWidget(Qt.RightDockWidgetArea, self.main.inspector_dock)
        self.main.addDockWidget(Qt.RightDockWidgetArea, self.main.bookmarks_dock)

        self.main.tabifyDockWidget(self.main.inspector_dock, self.main.bookmarks_dock)
        self.main.inspector_dock.raise_()

        self.main.resizeDocks([self.main.explorer_dock, self.main.inspector_dock], [340, 380], Qt.Horizontal)
        self.main.resizeDocks([self.main.results_dock], [310], Qt.Vertical)
        self.main.central_splitter.setSizes([760, 300])

        self.main.statusBar().showMessage('Layout Ember Graph restaurado', 2200)

        if save_snapshot:
            self.save_current_layout_snapshot()

    def apply_focus_layout(self) -> None:
        """Apply focus layout (hide results and bookmarks)."""
        self.main.explorer_dock.show()
        self.main.inspector_dock.show()
        self.main.results_dock.hide()
        self.main.bookmarks_dock.hide()
        self.main.resizeDocks([self.main.explorer_dock, self.main.inspector_dock], [280, 320], Qt.Horizontal)
        self.main.central_splitter.setSizes([880, 220])
        self.main.statusBar().showMessage('Focus layout aplicado', 2200)

    def save_current_layout_snapshot(self) -> None:
        """Save current layout as snapshot."""
        self.main.settings.setValue('workspace_snapshot_state_v3', self.main.saveState(self.main.STATE_VERSION))
        self.main.settings.setValue('workspace_snapshot_splitter', self.main.central_splitter.sizes())
        self.main.statusBar().showMessage('Layout actual guardado', 2200)

    def restore_saved_layout_snapshot(self) -> None:
        """Restore previously saved layout snapshot."""
        state = self.main.settings.value('workspace_snapshot_state_v3')
        splitter_sizes = self.main.settings.value('workspace_snapshot_splitter')

        if not state:
            QMessageBox.information(self.main, 'Repo Analyzer', 'No hay layout guardado.')
            return

        self.main.restoreState(state, self.main.STATE_VERSION)

        if isinstance(splitter_sizes, list) and splitter_sizes:
            try:
                self.main.central_splitter.setSizes(splitter_sizes)
            except Exception:
                pass

        self.main.statusBar().showMessage('Layout guardado restaurado', 2200)
