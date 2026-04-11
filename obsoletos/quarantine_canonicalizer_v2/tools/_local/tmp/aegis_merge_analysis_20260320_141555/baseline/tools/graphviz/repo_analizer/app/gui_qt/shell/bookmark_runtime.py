from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..main_window import RepoAnalyzerMainWindow


class BookmarkRuntimeCoordinator:
    """Handle bookmark-related shell actions."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window

    def open_selected_bookmark(self) -> None:
        item = self.main.bookmarks_list.currentItem()
        if not item:
            return
        self.main.show_preview_for_relpath(item.text())

    def remove_selected_bookmark(self) -> None:
        item = self.main.bookmarks_list.currentItem()
        if not item:
            return
        self.main.backend.remove_bookmark(self.main.repo_combo.currentText(), item.text())
        self.refresh_bookmarks_view()
        self.main.log(f"Bookmark removido: {item.text()}")

    def add_current_preview_bookmark(self) -> None:
        if not self.main.current_preview_rel:
            return
        self.main.backend.add_bookmark(
            self.main.repo_combo.currentText(),
            self.main.current_preview_rel,
        )
        self.refresh_bookmarks_view()
        self.main.log(f"Bookmark agregado: {self.main.current_preview_rel}")

    def refresh_bookmarks_view(self) -> None:
        self.main.bookmarks_list.clear()
        repo = self.main.repo_combo.currentText().strip()
        for rel in self.main.backend.get_repo_bookmarks(repo):
            self.main.bookmarks_list.addItem(rel)
