from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QThread, Slot
from PySide6.QtWidgets import QFileDialog, QMessageBox

from app.config import APP_TITLE
from app.helpers import human_size

from ..event_bus import Events
from ..workers import IndexWorker

if TYPE_CHECKING:
    from ..main_window import RepoAnalyzerMainWindow


class WorkspaceRuntimeCoordinator(QObject):
    """Coordinate workspace runtime state: index, filters, stats and shell indicators."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        super().__init__(main_window)
        self.main = main_window

    def choose_repo(self) -> None:
        start_dir = str(self.main.repo_combo.currentText() or Path.home())
        folder = QFileDialog.getExistingDirectory(self.main, "Selecciona repo", start_dir)
        if folder:
            self.main.repo_combo.setCurrentText(folder)
            self.main.backend.remember_repo(folder)
            self.main.refresh_bookmarks_view()
            self.start_indexing()

    def start_indexing(self, auto: bool = False) -> None:
        repo = self.main.repo_combo.currentText().strip()
        if not repo:
            if not auto:
                QMessageBox.warning(self.main, APP_TITLE, "Ingresa una ruta de repo.")
            return

        repo_path = Path(repo)
        if not repo_path.exists() or not repo_path.is_dir():
            QMessageBox.critical(
                self.main,
                APP_TITLE,
                "La ruta del repo no existe o no es una carpeta.",
            )
            return

        if self.main._index_thread is not None:
            QMessageBox.information(self.main, APP_TITLE, "Ya hay un indexado en progreso.")
            return

        self.main.backend.remember_repo(repo)
        self.main.refresh_bookmarks_view()
        self.clear_views_for_reindex()

        self.main.progress_bar.show()
        self.main.progress_bar.setRange(0, 0)
        self.main.statusBar().showMessage("Indexando repo…")
        self.main.hero_repo_label.setText(Path(repo).name or repo)
        self.main.hero_scope_label.setText(repo)
        self.main.hero_mode_pill.setText("Indexando workspace")
        self.main.log(f"Indexando: {repo_path}")

        thread = QThread(self.main)
        worker = IndexWorker(
            self.main.backend,
            repo,
            self.main.include_hidden_check.isChecked(),
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self.main.statusBar().showMessage)
        worker.finished.connect(self.on_index_ready)
        worker.error.connect(self.on_worker_error)
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_index_thread)

        self.main._index_thread = thread
        self.main._index_worker = worker
        thread.start()

    @Slot()
    def _clear_index_thread(self) -> None:
        self.main._index_thread = None
        self.main._index_worker = None

    @Slot(object)
    def on_index_ready(self, payload: object) -> None:
        self.main.progress_bar.hide()
        self.main.progress_bar.setRange(0, 1)
        self.main.index_data = payload if isinstance(payload, dict) else {}

        total_files = len(self.main.index_data.get("files", {}))
        ext_counts = self.main.index_data.get("ext_counts", {})
        elapsed = self.main.index_data.get("stats", {}).get("elapsed_sec", 0)

        self.main.status_summary.setText(f"{total_files} archivos | {len(ext_counts)} extensiones")
        self.main.hero_mode_pill.setText("Workspace indexado")
        self.main.log(f"Index listo: {total_files} archivos en {elapsed}s")

        self.main.tree_controller.rebuild_repo_tree()
        self.rebuild_filter_values()
        self.rebuild_quick_filters()
        self.main.refresh_bookmarks_view()
        self.render_stats()
        self._update_metric_cards_after_index()

        self.main.event_bus.publish(
            Events.INDEX_COMPLETED,
            {
                "root": self.main.index_data.get("root", ""),
                "file_count": total_files,
                "ext_count": len(ext_counts),
                "elapsed_sec": elapsed,
            },
        )

        self.main.statusBar().showMessage(
            f'Repo indexado: {self.main.index_data.get("root", "")}',
            3000,
        )

        last_preview = self.main.settings.value("last_preview_rel", "")
        if (
            not self.main._restored_preview_once
            and isinstance(last_preview, str)
            and last_preview in self.main.index_data.get("files", {})
        ):
            self.main._restored_preview_once = True
            self.main.preview_controller.show_preview_for_relpath(
                last_preview,
                add_history=False,
            )

    def clear_views_for_reindex(self) -> None:
        self.main.repo_tree.clear()
        self.main.results_model.removeRows(0, self.main.results_model.rowCount())
        self.main.imports_tree.clear()
        self.main.dependents_tree.clear()
        self.main.preview.clear()
        self.main.file_summary.clear()
        self.main.preview_title_label.setText("Sin archivo seleccionado")
        self.main.preview_meta_label.setText("Selecciona algo del árbol o desde resultados")
        self.main.current_preview_rel = None
        self.main.current_preview_path = None
        self.main.search_results = []
        self.main.tree_controller._tree_items_by_relpath.clear()

        self.main.quick_filter_combo.blockSignals(True)
        self.main.quick_filter_combo.clear()
        self.main.quick_filter_combo.addItem(self.main.quick_filter_all_label)
        self.main.quick_filter_combo.blockSignals(False)

        self._update_preview_actions()
        self._update_metric_cards_idle()

    def rebuild_filter_values(self) -> None:
        folders = ["(todo)", *sorted(self.main.index_data.get("folder_counts", {}).keys())]
        self.main.folder_combo.blockSignals(True)
        self.main.folder_combo.clear()
        self.main.folder_combo.addItems(folders)
        existing = getattr(
            self.main,
            "_pending_folder_filter",
            self.main.backend.settings.get("last_folder_filter", "(todo)"),
        )
        self.main.folder_combo.setCurrentText(existing if existing in folders else "(todo)")
        self.main.folder_combo.blockSignals(False)

        detected_exts = sorted(
            [ext for ext in self.main.index_data.get("ext_counts", {}).keys() if ext],
            key=str.lower,
        )
        exts = ["(todas)", "TS/JS", "(sin extensión)", *detected_exts]
        self.main.ext_combo.blockSignals(True)
        self.main.ext_combo.clear()
        self.main.ext_combo.addItems(exts)
        current_ext = getattr(
            self.main,
            "_pending_ext_filter",
            self.main.backend.settings.get("last_ext_filter", "(todas)"),
        )
        self.main.ext_combo.setCurrentText(current_ext if current_ext in exts else "(todas)")
        self.main.ext_combo.blockSignals(False)

        self.on_filter_inputs_changed()

    def rebuild_quick_filters(self) -> None:
        counts = self.main.index_data.get("top_level_counts", {})
        values = [self.main.quick_filter_all_label]
        self.main.quick_filter_map = {self.main.quick_filter_all_label: "(todo)"}

        for folder, count in list(counts.items())[:30]:
            label = f"{folder} ({count})"
            values.append(label)
            self.main.quick_filter_map[label] = folder

        self.main.quick_filter_combo.blockSignals(True)
        self.main.quick_filter_combo.clear()
        self.main.quick_filter_combo.addItems(values)
        self.main.quick_filter_combo.blockSignals(False)
        self.sync_quick_filter_combo()

    def sync_quick_filter_combo(self) -> None:
        current_folder = self.main.folder_combo.currentText() or "(todo)"
        for label, folder in self.main.quick_filter_map.items():
            if folder == current_folder:
                self.main.quick_filter_combo.setCurrentText(label)
                return

        if current_folder not in ("", "(todo)"):
            if self.main.quick_filter_combo.findText(self.main.quick_filter_manual_label) < 0:
                self.main.quick_filter_combo.addItem(self.main.quick_filter_manual_label)
            self.main.quick_filter_combo.setCurrentText(self.main.quick_filter_manual_label)
        else:
            self.main.quick_filter_combo.setCurrentText(self.main.quick_filter_all_label)

    def on_quick_filter_selected(self) -> None:
        label = self.main.quick_filter_combo.currentText().strip() or self.main.quick_filter_all_label
        folder = self.main.quick_filter_map.get(label, "(todo)")
        self.main.folder_combo.setCurrentText(folder)
        self.on_filter_inputs_changed()

    def on_filter_inputs_changed(self) -> None:
        folder = self.main.folder_combo.currentText() or "(todo)"
        ext = self.main.ext_combo.currentText() or "(todas)"
        self.main.backend.update_filter_settings(folder, ext)
        self.sync_quick_filter_combo()

        scope = "todo el repo" if folder == "(todo)" else folder
        self.main.status_scope_label.setText(f"scope: {scope}")
        self.main.metric_scope.set_data(scope, f"ext: {ext}")

        if folder == "(todo)":
            self.main.statusBar().showMessage("Filtro de carpeta: todo el repo", 1600)
        else:
            self.main.statusBar().showMessage(f"Filtro de carpeta activo: {folder}", 1600)

    def on_include_hidden_changed(self) -> None:
        if self.main.index_data.get("root"):
            pass

    @Slot(str)
    def on_worker_error(self, error_text: str) -> None:
        self.main.progress_bar.hide()
        self.main.progress_bar.setRange(0, 1)
        self.main.hero_mode_pill.setText("Error en pipeline")
        self.main.log(error_text)
        QMessageBox.critical(self.main, APP_TITLE, error_text)

    def render_stats(self) -> None:
        data = self.main.index_data
        if not data.get("files"):
            self.main.stats_text.clear()
            return

        stats = data.get("stats", {})
        lines = [
            f"Repo: {data['root']}",
            f"Archivos indexados: {len(data['files'])}",
            f"Tiempo de indexado: {stats.get('elapsed_sec', 0)} s",
            "",
            "Extensiones:",
        ]

        for ext, count in data.get("ext_counts", {}).items():
            lines.append(f"  {ext:<12} {count}")

        lines.extend(["", "Top-level folders:"])
        for folder, count in data.get("top_level_counts", {}).items():
            lines.append(f"  {folder:<28} {count}")

        lines.extend(["", "Archivos más grandes:"])
        for item in stats.get("largest_files", []):
            lines.append(f"  {human_size(item['size']).rjust(8)}   {item['relpath']}")

        self.main.stats_text.setPlainText("\n".join(lines))

    def _update_metric_cards_idle(self) -> None:
        repo_name = Path(self.main.repo_combo.currentText().strip() or "repo").name or "repo"
        self.main.metric_repo.set_data(repo_name, "aún sin indexado")
        self.main.metric_files.set_data("0", "archivos en memoria")
        self.main.metric_scope.set_data("todo el repo", "scope inicial")
        self.main.metric_results.set_data("0", "sin búsqueda")

    def _update_metric_cards_after_index(self) -> None:
        repo_root = self.main.index_data.get("root", "")
        repo_name = (
            Path(repo_root).name
            if repo_root
            else Path(self.main.repo_combo.currentText().strip() or "repo").name
        )
        total_files = len(self.main.index_data.get("files", {}))
        total_ext = len(self.main.index_data.get("ext_counts", {}))
        elapsed = self.main.index_data.get("stats", {}).get("elapsed_sec", 0)

        self.main.metric_repo.set_data(repo_name or "repo", repo_root or "ruta sin resolver")
        self.main.metric_files.set_data(str(total_files), f"{total_ext} extensiones • {elapsed}s")
        scope = self.main.folder_combo.currentText() or "(todo)"
        self.main.metric_scope.set_data(
            "todo el repo" if scope == "(todo)" else scope,
            self.main.ext_combo.currentText() or "(todas)",
        )
        self.main.metric_results.set_data(
            str(len(self.main.search_results)),
            self.main.search_box.text().strip() or "sin query activa",
        )

    def _update_preview_actions(self) -> None:
        has_preview = bool(self.main.current_preview_path)
        is_svg = bool(
            self.main.current_preview_path
            and Path(self.main.current_preview_path).suffix.lower() == ".svg"
        )

        self.main.open_system_btn.setEnabled(has_preview)
        self.main.open_svg_btn.setEnabled(is_svg)
        self.main.bookmark_btn.setEnabled(has_preview)
        self.main.back_action.setEnabled(self.main.navigation_controller._preview_history_index > 0)
        self.main.forward_action.setEnabled(
            self.main.navigation_controller._preview_history_index
            < len(self.main.navigation_controller._preview_history) - 1
        )
        self.main.bookmark_action.setEnabled(has_preview)
