from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Qt, QThread, Slot
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QSpinBox,
    QTableView,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QStandardItem, QStandardItemModel

from app.config import DEFAULT_MAX_RESULTS
from app.helpers import human_size
from .widgets import AccentButton, PanelCard
from .workers import SearchWorker

if TYPE_CHECKING:
    from .main_window import RepoAnalyzerMainWindow
    from .skins import SkinTokens

ROLE_RELPATH = 256  # Qt.UserRole + 1
ROLE_ABSPATH = 257  # Qt.UserRole + 2
ROLE_RESULT_LINE = 259  # Qt.UserRole + 4
ROLE_RESULT_MATCHES = 260  # Qt.UserRole + 5


class SearchController(QObject):
    """Manages all search functionality and results display."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        super().__init__(main_window)
        self.main = main_window
        self._search_thread: QThread | None = None
        self._search_worker: SearchWorker | None = None

    def build_results_dock_widget(self, skin_tokens: SkinTokens) -> None:
        """Create the results table view."""
        results_card = PanelCard(skin_tokens, accent=True, parent=self.main.results_dock)
        results_layout = QVBoxLayout(results_card)
        results_layout.setContentsMargins(14, 14, 14, 14)
        results_layout.setSpacing(10)

        results_table = QTableView(results_card)
        results_table.setObjectName('resultsTableSurface')
        results_table.setProperty('visualRole', 'summary-surface')
        results_table.setProperty('visualTier', 'themed')
        results_model = QStandardItemModel(0, 6, results_table)
        results_model.setHorizontalHeaderLabels([
            'Ruta',
            'Modificado',
            'Tamaño',
            'Extensión',
            'Hits',
            'Snippet',
        ])
        results_table.setModel(results_model)
        results_table.setAlternatingRowColors(True)
        results_table.setSortingEnabled(False)
        results_table.verticalHeader().setVisible(False)
        results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        results_table.setSelectionMode(QAbstractItemView.SingleSelection)
        results_table.horizontalHeader().setStretchLastSection(False)
        results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        results_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        results_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        results_table.clicked.connect(self.on_results_clicked)
        results_table.doubleClicked.connect(self.on_results_double_clicked)
        results_layout.addWidget(results_table, 1)

        self.main.results_dock.setWidget(results_card)

        self.main.results_table = results_table
        self.main.results_model = results_model

    def build_search_inspector_tab(self, parent: QWidget, skin_tokens: SkinTokens) -> QWidget:
        """Create the search operations inspector tab."""
        search_tab = QWidget(parent)
        search_tab.setObjectName('searchInspectorSurface')
        search_tab.setProperty('visualRole', 'panel-surface')
        search_tab.setProperty('visualTier', 'themed')
        search_form = QFormLayout(search_tab)
        search_form.setContentsMargins(8, 8, 8, 8)
        search_form.setSpacing(10)

        # Folder combo
        self.main.folder_combo = QComboBox(search_tab)
        self.main.folder_combo.currentIndexChanged.connect(self.main.on_filter_inputs_changed)
        search_form.addRow('Carpeta', self.main.folder_combo)

        # Search options checkboxes
        self.main.case_check = QCheckBox('Case sensitive', search_tab)
        self.main.regex_check = QCheckBox('Regex', search_tab)
        self.main.word_check = QCheckBox('Whole word', search_tab)
        self.main.names_only_check = QCheckBox('Solo nombres', search_tab)
        self.main.include_hidden_check = QCheckBox('Incluir ocultos', search_tab)
        self.main.include_hidden_check.toggled.connect(self.main.on_include_hidden_changed)

        checks_wrap = QWidget(search_tab)
        checks_wrap.setObjectName('searchOptionsSurface')
        checks_wrap.setProperty('visualRole', 'panel-surface')
        checks_wrap.setProperty('visualTier', 'themed')
        checks_layout = QVBoxLayout(checks_wrap)
        checks_layout.setContentsMargins(0, 0, 0, 0)
        checks_layout.setSpacing(6)
        for chk in (
            self.main.case_check,
            self.main.regex_check,
            self.main.word_check,
            self.main.names_only_check,
            self.main.include_hidden_check,
        ):
            checks_layout.addWidget(chk)
        search_form.addRow('Opciones', checks_wrap)

        # Max results spinner
        self.main.max_results_spin = QSpinBox(search_tab)
        self.main.max_results_spin.setRange(50, 10000)
        self.main.max_results_spin.setSingleStep(50)
        self.main.max_results_spin.setValue(DEFAULT_MAX_RESULTS)
        search_form.addRow('Máx. resultados', self.main.max_results_spin)

        # Action buttons
        search_buttons_row = QWidget(search_tab)
        search_buttons_row.setObjectName('searchActionsSurface')
        search_buttons_row.setProperty('visualRole', 'panel-surface')
        search_buttons_row.setProperty('visualTier', 'themed')
        row_layout = QHBoxLayout(search_buttons_row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        self.main.search_now_btn = AccentButton('Buscar', skin_tokens, search_buttons_row, strong=True)
        self.main.search_now_btn.clicked.connect(self.main.start_search)
        
        self.main.clear_search_btn = AccentButton('Limpiar', skin_tokens, search_buttons_row)
        self.main.clear_search_btn.clicked.connect(self.clear_search)
        
        self.main.export_btn = AccentButton('Exportar', skin_tokens, search_buttons_row)
        self.main.export_btn.clicked.connect(self.export_results)
        
        self.main.open_repo_btn = AccentButton('Abrir carpeta', skin_tokens, search_buttons_row)
        self.main.open_repo_btn.clicked.connect(self.main.open_current_repo_folder)

        for btn in (
            self.main.search_now_btn,
            self.main.clear_search_btn,
            self.main.export_btn,
            self.main.open_repo_btn,
        ):
            row_layout.addWidget(btn)

        search_form.addRow(search_buttons_row)

        return search_tab

    def start_search(self) -> None:
        """Execute search with current parameters."""
        if not self.main.index_data.get('files'):
            QMessageBox.warning(self.main, 'Repo Analyzer', 'Primero indexa un repo.')
            return

        if self._search_thread is not None:
            QMessageBox.information(self.main, 'Repo Analyzer', 'Ya hay una búsqueda en progreso.')
            return

        query = self.main.search_box.text().strip()
        folder = self.main.folder_combo.currentText() or '(todo)'
        ext_filter = self.main.ext_combo.currentText() or '(todas)'
        sort_mode = self.main.sort_combo.currentText() or 'path'
        max_results = max(1, int(self.main.max_results_spin.value() or DEFAULT_MAX_RESULTS))

        self.main.progress_bar.show()
        self.main.progress_bar.setRange(0, 0)
        self.main.statusBar().showMessage('Buscando…')
        self.main.hero_mode_pill.setText('Search pipeline activo')
        self.main.log(
            f"Buscar: '{query or '(vacío)'}' | folder={folder} | ext={ext_filter} | "
            f"regex={self.main.regex_check.isChecked()} | names_only={self.main.names_only_check.isChecked()}"
        )
        self.main.backend.remember_search(query)
        self.main.backend.update_filter_settings(folder, ext_filter)

        thread = QThread(self.main)
        worker = SearchWorker(
            self.main.backend,
            dict(self.main.index_data),
            query,
            folder,
            ext_filter,
            sort_mode,
            self.main.case_check.isChecked(),
            self.main.regex_check.isChecked(),
            self.main.word_check.isChecked(),
            self.main.names_only_check.isChecked(),
            max_results,
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self.main.statusBar().showMessage)
        worker.finished.connect(self.on_search_ready)
        worker.error.connect(self.main.on_worker_error)
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_search_thread)

        self._search_thread = thread
        self._search_worker = worker
        thread.start()

    @Slot(object)
    def on_search_ready(self, results_obj: object) -> None:
        """Handle search completion."""
        self.main.progress_bar.hide()
        self.main.progress_bar.setRange(0, 1)
        self.main.search_results = list(results_obj) if isinstance(results_obj, list) else []
        self.main.results_model.removeRows(0, self.main.results_model.rowCount())

        for result in self.main.search_results:
            row_items = [
                QStandardItem(result.display_path),
                QStandardItem(result.modified),
                QStandardItem(human_size(result.size)),
                QStandardItem(result.ext),
                QStandardItem(str(result.matches)),
                QStandardItem(result.snippet or ''),
            ]
            for item in row_items:
                item.setEditable(False)
            row_items[0].setData(result.relpath, ROLE_RELPATH)
            row_items[0].setData(result.abspath, ROLE_ABSPATH)
            row_items[0].setData(result.line, ROLE_RESULT_LINE)
            row_items[0].setData(result.matches, ROLE_RESULT_MATCHES)
            self.main.results_model.appendRow(row_items)

        self.main.results_table.resizeRowsToContents()
        count = len(self.main.search_results)
        self.main.metric_results.set_data(str(count), self.main.search_box.text().strip() or 'listado por filtros')
        self.main.hero_mode_pill.setText('Search lista para inspección')

        if self.main.search_results:
            self.main.results_dock.show()
            self.main.statusBar().showMessage(f'{count} resultados', 2500)
            self.main.log(f'Búsqueda terminada: {count} resultados')
        else:
            self.main.statusBar().showMessage('Sin resultados', 2200)
            self.main.log('Búsqueda sin resultados')

        # Publish event for extensibility
        from .event_bus import Events
        self.main.event_bus.publish(
            Events.SEARCH_COMPLETED,
            {
                'query': self.main.search_box.text().strip(),
                'results_count': count,
                'results': [
                    {'relpath': r.relpath, 'matches': r.matches}
                    for r in self.main.search_results
                ]
            }
        )

    def on_results_clicked(self, index) -> None:
        """Handle result table click."""
        if not index.isValid():
            return
        relpath = self.main.results_model.item(index.row(), 0).data(ROLE_RELPATH)
        line = self.main.results_model.item(index.row(), 0).data(ROLE_RESULT_LINE) or 0
        if isinstance(relpath, str) and relpath:
            self.main.show_preview_for_relpath(relpath, int(line))

    def on_results_double_clicked(self, index) -> None:
        """Handle result table double-click."""
        if not index.isValid():
            return
        path = self.main.results_model.item(index.row(), 0).data(ROLE_ABSPATH)
        if isinstance(path, str) and path:
            self.main.open_with_system(path)

    def clear_search(self) -> None:
        """Clear search results."""
        self.main.search_box.clear()
        self.main.results_model.removeRows(0, self.main.results_model.rowCount())
        self.main.search_results = []
        self.main.metric_results.set_data('0', 'sin resultados cacheados')
        self.main.statusBar().showMessage('Búsqueda limpia.', 1600)

    def export_results(self) -> None:
        """Export search results to file."""
        if not self.main.search_results:
            QMessageBox.information(self.main, 'Repo Analyzer', 'No hay resultados para exportar.')
            return

        path, _ = QFileDialog.getSaveFileName(
            self.main,
            'Exportar resultados',
            '',
            'CSV (*.csv);;JSON (*.json);;TXT (*.txt);;Todos (*.*)',
        )
        if not path:
            return

        try:
            self.main.backend.export_results(self.main.search_results, Path(path))
            self.main.log(f'Resultados exportados: {path}')
            QMessageBox.information(self.main, 'Repo Analyzer', f'Exportado correctamente:\n{path}')
        except Exception as e:
            QMessageBox.critical(self.main, 'Repo Analyzer', f'No se pudo exportar:\n{e}')

    @Slot()
    def _clear_search_thread(self) -> None:
        """Clear search thread reference."""
        self._search_thread = None
        self._search_worker = None
