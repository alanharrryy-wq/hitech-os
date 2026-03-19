from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QLineEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout

from .widgets import PanelCard

if TYPE_CHECKING:
    from .main_window import RepoAnalyzerMainWindow
    from .skins import SkinTokens

ROLE_RELPATH = 256  # Qt.UserRole + 1
ROLE_ABSPATH = 257  # Qt.UserRole + 2
ROLE_NODE_KIND = 258  # Qt.UserRole + 3


class TreeController:
    """Manages the repository tree widget and filtering."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window
        self._tree_items_by_relpath: dict[str, QTreeWidgetItem] = {}
        self._tree_selection_guard = False

    def build_tree_dock_widget(self, skin_tokens: SkinTokens) -> tuple[QLineEdit, QTreeWidget]:
        """Create and return the explorer tree widget with filter."""
        explorer_card = PanelCard(skin_tokens, accent=True, parent=self.main.explorer_dock)
        explorer_layout = QVBoxLayout(explorer_card)
        explorer_layout.setContentsMargins(16, 16, 16, 16)
        explorer_layout.setSpacing(9)

        tree_filter_box = QLineEdit(explorer_card)
        tree_filter_box.setObjectName('treeFilterSurface')
        tree_filter_box.setProperty('visualRole', 'status-surface')
        tree_filter_box.setProperty('visualTier', 'themed')
        tree_filter_box.setPlaceholderText('Filtrar por nombre de archivo o ruta relativa...')
        tree_filter_box.textChanged.connect(self.on_tree_filter_changed)
        explorer_layout.addWidget(tree_filter_box)

        repo_tree = QTreeWidget(explorer_card)
        repo_tree.setObjectName('repoTreeSurface')
        repo_tree.setProperty('visualRole', 'summary-surface')
        repo_tree.setProperty('visualTier', 'themed')
        repo_tree.setHeaderLabels(['Repositorio'])
        repo_tree.setAlternatingRowColors(True)
        repo_tree.setAnimated(True)
        repo_tree.setIndentation(20)
        repo_tree.setUniformRowHeights(True)
        repo_tree.itemSelectionChanged.connect(self.on_tree_selection_changed)
        repo_tree.itemDoubleClicked.connect(self.on_tree_double_click)
        explorer_layout.addWidget(repo_tree, 1)

        self.main.explorer_dock.setWidget(explorer_card)

        return tree_filter_box, repo_tree

    def rebuild_repo_tree(self) -> None:
        """Rebuild the tree from index data."""
        tree = self.main.repo_tree
        tree.clear()
        self._tree_items_by_relpath.clear()

        repo_root = self.main.index_data.get('root', '')
        if not repo_root:
            return

        root_label = Path(repo_root).name or repo_root
        root_item = QTreeWidgetItem([root_label])
        root_item.setData(0, ROLE_NODE_KIND, 'root')
        root_item.setExpanded(True)
        tree.addTopLevelItem(root_item)

        # Build folder and file hierarchy
        folder_children: dict[str, set[str]] = defaultdict(set)
        file_children: dict[str, list[str]] = defaultdict(list)

        for rel in self.main.index_data.get('files', {}).keys():
            parts = rel.split('/')
            if len(parts) == 1:
                file_children[''].append(rel)
            for depth in range(1, len(parts)):
                parent_rel = '/'.join(parts[:depth])
                child_folder_rel = '/'.join(parts[: depth + 1])
                folder_children[parent_rel].add(child_folder_rel)
            file_children['/'.join(parts[:-1])].append(rel)

        def insert_branch(parent_item: QTreeWidgetItem, parent_rel: str, depth: int) -> None:
            child_folders = sorted(
                folder_children.get(parent_rel, set()),
                key=lambda x: Path(x).name.lower()
            )
            child_files = sorted(
                file_children.get(parent_rel, []),
                key=lambda x: Path(x).name.lower()
            )

            for folder_rel in child_folders:
                folder_name = Path(folder_rel).name
                folder_item = QTreeWidgetItem([folder_name])
                folder_item.setData(0, ROLE_NODE_KIND, 'folder')
                folder_item.setData(0, ROLE_RELPATH, folder_rel)
                parent_item.addChild(folder_item)
                insert_branch(folder_item, folder_rel, depth + 1)

            for file_rel in child_files:
                file_name = Path(file_rel).name
                file_item = QTreeWidgetItem([file_name])
                file_item.setData(0, ROLE_NODE_KIND, 'file')
                file_item.setData(0, ROLE_RELPATH, file_rel)
                full_path = Path(self.main.index_data.get('root', '')) / file_rel
                file_item.setData(0, ROLE_ABSPATH, str(full_path))
                parent_item.addChild(file_item)
                self._tree_items_by_relpath[file_rel] = file_item

        insert_branch(root_item, '', 0)
        tree.expandItem(root_item)
        tree.resizeColumnToContents(0)

        if self.main.tree_filter_box.text().strip():
            self.on_tree_filter_changed(self.main.tree_filter_box.text())

    def on_tree_selection_changed(self) -> None:
        """Handle tree selection changes."""
        if self._tree_selection_guard:
            return

        items = self.main.repo_tree.selectedItems()
        if not items:
            return

        item = items[0]
        if item.data(0, ROLE_NODE_KIND) != 'file':
            return

        relpath = item.data(0, ROLE_RELPATH)
        if isinstance(relpath, str) and relpath:
            self.main.show_preview_for_relpath(relpath)
            # Publish event for extensibility (preview_controller will also publish)
            from .event_bus import Events
            self.main.event_bus.publish(
                Events.TREE_REBUILT,
                {'source': 'tree_selection', 'relpath': relpath}
            )

    def on_tree_double_click(self, item: QTreeWidgetItem, _column: int) -> None:
        """Handle double-click on tree items."""
        if item.data(0, ROLE_NODE_KIND) == 'file':
            path = item.data(0, ROLE_ABSPATH)
            if isinstance(path, str) and path:
                self.main.open_with_system(path)

    def on_tree_filter_changed(self, text: str) -> None:
        """Filter tree items by text."""
        needle = text.strip().lower()
        root = self.main.repo_tree.invisibleRootItem()
        for i in range(root.childCount()):
            self._filter_tree_item(root.child(i), needle)

    def _filter_tree_item(self, item: QTreeWidgetItem, needle: str) -> bool:
        """Recursively filter tree items."""
        own_text = item.text(0).lower()
        relpath = item.data(0, ROLE_RELPATH)
        rel_text = relpath.lower() if isinstance(relpath, str) else ''

        match = not needle or needle in own_text or needle in rel_text
        child_match = False

        for idx in range(item.childCount()):
            child_visible = self._filter_tree_item(item.child(idx), needle)
            child_match = child_match or child_visible

        visible = match or child_match or item.data(0, ROLE_NODE_KIND) == 'root'
        item.setHidden(not visible)

        if child_match and needle:
            item.setExpanded(True)

        return visible

    def select_tree_item_by_relpath(self, relpath: str) -> None:
        """Select and scroll to a tree item by relative path."""
        item = self._tree_items_by_relpath.get(relpath)
        if item is None:
            return

        self._tree_selection_guard = True
        try:
            self.main.repo_tree.setCurrentItem(item)
            self.main.repo_tree.scrollToItem(item)
        finally:
            self._tree_selection_guard = False
