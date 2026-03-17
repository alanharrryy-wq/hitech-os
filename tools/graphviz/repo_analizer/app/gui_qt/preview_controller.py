from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.helpers import human_size
from .widgets import AccentButton, PanelCard

if TYPE_CHECKING:
    from .main_window import RepoAnalyzerMainWindow
    from .skins import SkinTokens

ROLE_RELPATH = 256  # Qt.UserRole + 1


class PreviewController:
    """Manages file preview, imports, and dependents panel."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window

    def build_preview_panel(self, skin_tokens: SkinTokens, central_splitter) -> QWidget:
        """Build the preview panel with imports and dependents."""
        preview_card = PanelCard(skin_tokens, accent=True, parent=central_splitter)
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(18, 16, 18, 16)
        preview_layout.setSpacing(10)

        # Header
        preview_header = QHBoxLayout()
        preview_title_box = QVBoxLayout()
        preview_title_box.setContentsMargins(0, 0, 0, 0)
        preview_title_box.setSpacing(2)

        self.main.preview_title_label = QLabel('Sin archivo seleccionado', preview_card)
        self.main.preview_title_label.setObjectName('heroTitleLabel')
        self.main.preview_meta_label = QLabel('Selecciona algo del árbol o desde resultados', preview_card)
        self.main.preview_meta_label.setObjectName('panelMutedLabel')
        preview_title_box.addWidget(self.main.preview_title_label)
        preview_title_box.addWidget(self.main.preview_meta_label)
        preview_header.addLayout(preview_title_box, 1)

        self.main.open_system_btn = AccentButton('Abrir con sistema', skin_tokens, preview_card)
        self.main.open_system_btn.clicked.connect(self.main.open_current_preview_with_system)
        preview_header.addWidget(self.main.open_system_btn)
        self.main._toolbar_buttons.append(self.main.open_system_btn)

        self.main.open_svg_btn = AccentButton('SVG Workspace', skin_tokens, preview_card)
        self.main.open_svg_btn.clicked.connect(self.main.open_svg_workspace)
        preview_header.addWidget(self.main.open_svg_btn)
        self.main._toolbar_buttons.append(self.main.open_svg_btn)

        self.main.bookmark_btn = AccentButton('Bookmark', skin_tokens, preview_card)
        self.main.bookmark_btn.clicked.connect(self.main.add_current_preview_bookmark)
        preview_header.addWidget(self.main.bookmark_btn)
        self.main._toolbar_buttons.append(self.main.bookmark_btn)

        preview_layout.addLayout(preview_header)

        # Preview text
        self.main.preview = QPlainTextEdit(preview_card)
        self.main.preview.setReadOnly(True)
        self.main.preview.setLineWrapMode(QPlainTextEdit.NoWrap)
        code_font = QFont('Consolas', 10)
        code_font.setStyleHint(QFont.Monospace)
        self.main.preview.setFont(code_font)
        preview_layout.addWidget(self.main.preview, 1)

        self.main.preview_hint_label = QLabel(
            'Doble clic en árbol o resultados para abrir con tu sistema. Alt+Left / Alt+Right para navegar.',
            preview_card
        )
        self.main.preview_hint_label.setObjectName('panelMutedLabel')
        preview_layout.addWidget(self.main.preview_hint_label)

        self.main._panel_cards.append(preview_card)
        return preview_card

    def build_inspector_panel(self, skin_tokens: SkinTokens, central_splitter) -> QWidget:
        """Build the central inspector panel with stats, imports, dependents."""
        insights_card = PanelCard(skin_tokens, accent=False, parent=central_splitter)
        insights_layout = QVBoxLayout(insights_card)
        insights_layout.setContentsMargins(18, 16, 18, 16)
        insights_layout.setSpacing(10)

        # Header
        insights_header = QHBoxLayout()
        insights_title = QLabel('Inspector central', insights_card)
        insights_title.setObjectName('heroTitleLabel')
        insights_header.addWidget(insights_title)
        insights_header.addStretch(1)
        self.main.insights_pill = QLabel('Stats • Imports • Dependents • Log', insights_card)
        self.main.insights_pill.setObjectName('panelPill')
        insights_header.addWidget(self.main.insights_pill)
        insights_layout.addLayout(insights_header)

        # Tabs
        from PySide6.QtWidgets import QTabWidget

        self.main.insights_tabs = QTabWidget(insights_card)

        # Stats tab
        self.main.stats_text = QPlainTextEdit(insights_card)
        self.main.stats_text.setReadOnly(True)

        # Log tab
        self.main.log_text = QPlainTextEdit(insights_card)
        self.main.log_text.setReadOnly(True)

        # Imports tab
        self.main.imports_tree = QTreeWidget(insights_card)
        self.main.imports_tree.setHeaderLabels(['Import', 'Resuelto'])
        self.main.imports_tree.itemDoubleClicked.connect(self.on_import_double_click)

        # Dependents tab
        self.main.dependents_tree = QTreeWidget(insights_card)
        self.main.dependents_tree.setHeaderLabels(['Archivo dependiente'])
        self.main.dependents_tree.itemDoubleClicked.connect(self.on_dependent_double_click)

        self.main.insights_tabs.addTab(self.main.stats_text, 'Stats')
        self.main.insights_tabs.addTab(self.main.imports_tree, 'Imports')
        self.main.insights_tabs.addTab(self.main.dependents_tree, 'Dependents')
        self.main.insights_tabs.addTab(self.main.log_text, 'Log')
        insights_layout.addWidget(self.main.insights_tabs, 1)

        self.main._panel_cards.append(insights_card)
        return insights_card

    def show_preview_for_relpath(self, relpath: str, line: int = 0, *, add_history: bool = True) -> None:
        """Show preview for a file."""
        try:
            preview = self.main.backend.build_preview(self.main.index_data, relpath, line=line)
        except Exception as e:
            QMessageBox.critical(self.main, 'Repo Analyzer', f'No se pudo abrir preview:\n{e}')
            return

        self.main.current_preview_rel = preview.relpath
        self.main.current_preview_path = preview.abspath
        self.main.preview_title_label.setText(Path(preview.relpath).name)
        self.main.preview_meta_label.setText(preview.title)
        self.main.preview.setPlainText(preview.rendered_text)
        self.populate_imports(preview)
        self.populate_dependents(preview)
        self.populate_file_summary(preview)
        self.main.tree_controller.select_tree_item_by_relpath(relpath)

        if line > 0:
            self.jump_preview_to_line(line)
        else:
            cursor = self.main.preview.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self.main.preview.setTextCursor(cursor)

        self.main.settings.setValue('last_preview_rel', relpath)

        if add_history:
            self.main.navigation_controller._push_preview_history(relpath, line)

        self.main._update_preview_actions()

        # Publish events for extensibility
        from .event_bus import Events
        self.main.event_bus.publish(
            Events.FILE_SELECTED,
            {'relpath': relpath, 'line': line}
        )
        self.main.event_bus.publish(
            Events.PREVIEW_OPENED,
            {'relpath': relpath, 'line': line, 'abspath': preview.abspath}
        )

    def populate_imports(self, preview) -> None:
        """Populate imports tree tab."""
        self.main.imports_tree.clear()
        for raw, resolved in preview.imports:
            item = QTreeWidgetItem([raw, resolved])
            item.setData(0, ROLE_RELPATH, resolved)
            self.main.imports_tree.addTopLevelItem(item)
        self.main.imports_tree.resizeColumnToContents(0)
        self.main.imports_tree.resizeColumnToContents(1)

    def populate_dependents(self, preview) -> None:
        """Populate dependents tree tab."""
        self.main.dependents_tree.clear()
        for rel in preview.dependents:
            item = QTreeWidgetItem([rel])
            item.setData(0, ROLE_RELPATH, rel)
            self.main.dependents_tree.addTopLevelItem(item)
        self.main.dependents_tree.resizeColumnToContents(0)

    def populate_file_summary(self, preview) -> None:
        """Populate file summary panel."""
        path = Path(preview.abspath)
        try:
            size = path.stat().st_size
        except Exception:
            size = 0

        lines = [
            f'Relpath: {preview.relpath}',
            f'Ruta: {preview.abspath}',
            f'Tamaño: {human_size(size)}',
            f'Extensión: {path.suffix.lower() or "(sin extensión)"}',
            f'Imports detectados: {len(preview.imports)}',
            f'Dependents detectados: {len(preview.dependents)}',
        ]
        if preview.line:
            lines.append(f'Línea objetivo: {preview.line}')
        if path.suffix.lower() == '.svg':
            lines.append('Tip: usa SVG Workspace para paneo y zoom fino.')

        self.main.file_summary.setPlainText('\n'.join(lines))

    def jump_preview_to_line(self, line: int) -> None:
        """Jump preview to specific line."""
        cursor = self.main.preview.textCursor()
        cursor.movePosition(QTextCursor.Start)
        for _ in range(max(0, line - 1)):
            cursor.movePosition(QTextCursor.Down)
        self.main.preview.setTextCursor(cursor)
        self.main.preview.centerCursor()

    def on_import_double_click(self, item: QTreeWidgetItem, _column: int) -> None:
        """Handle double-click on import."""
        resolved = item.data(0, ROLE_RELPATH)
        if isinstance(resolved, str) and resolved:
            self.show_preview_for_relpath(resolved)

    def on_dependent_double_click(self, item: QTreeWidgetItem, _column: int) -> None:
        """Handle double-click on dependent."""
        relpath = item.data(0, ROLE_RELPATH)
        if isinstance(relpath, str) and relpath:
            self.show_preview_for_relpath(relpath)

    def open_current_preview_with_system(self) -> None:
        """Open current preview file with system default app."""
        if self.main.current_preview_path:
            self.main.open_with_system(self.main.current_preview_path)

    def open_svg_workspace(self) -> None:
        """Open SVG workspace for current preview."""
        if not self.main.current_preview_path:
            return

        if Path(self.main.current_preview_path).suffix.lower() != '.svg':
            return

        from .svg_viewer import SvgPreviewWindow

        if self.main._svg_window is None:
            self.main._svg_window = SvgPreviewWindow(self.main._skin_tokens)

        self.main._svg_window.set_skin(self.main._skin_tokens)
        self.main._svg_window.load_svg(
            self.main.current_preview_path,
            self.main.current_preview_rel or Path(self.main.current_preview_path).name
        )
        self.main._svg_window.show()
        self.main._svg_window.raise_()
        self.main._svg_window.activateWindow()

    def open_current_repo_folder(self) -> None:
        """Open the current repo folder with system default."""
        repo = self.main.repo_combo.currentText().strip()
        if repo and Path(repo).exists():
            self.main.open_with_system(repo)

    def open_with_system(self, path: str) -> None:
        """Open a path with the system's default application."""
        try:
            if sys.platform == 'win32':
                subprocess.Popen(['explorer', '/select,', path])
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', '-R', path])
            else:
                subprocess.Popen(['xdg-open', path])
        except Exception as e:
            QMessageBox.warning(self.main, 'Repo Analyzer', f'No se pudo abrir con el sistema:\n{e}')

