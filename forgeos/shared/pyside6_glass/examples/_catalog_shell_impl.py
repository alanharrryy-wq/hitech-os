from __future__ import annotations

import json
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..catalog import (
    GlassCatalogEntry,
    get_catalog_entry,
    list_catalog_categories,
    list_catalog_entries,
    list_catalog_tags,
    register_builtin_catalog_entries,
)
from ..config import get_template_preset
from ..template import GlassPanelTemplate


def _clear_layout(layout: QVBoxLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget is not None:
            widget.setParent(None)
            continue
        if child_layout is not None:
            while child_layout.count():
                child_item = child_layout.takeAt(0)
                child_widget = child_item.widget()
                if child_widget is not None:
                    child_widget.setParent(None)


class GlassCatalogShell(QWidget):
    """Polished, extensible browser for built-in and registered catalog entries."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        register_builtin_catalog_entries()
        self._selected_entry_id: str | None = None
        self._entry_order: list[str] = []
        self._preview_instance_counter = 0
        self._category_counts: dict[str, int] = {}
        self._category_tags: dict[str, tuple[str, ...]] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.catalog = GlassPanelTemplate(
            self,
            config=get_template_preset("tabbed_workspace"),
            title="Glass Catalog",
            subtitle="Browse predefined framework compositions, presets, themes and primitives.",
            eyebrow="CATALOG",
            include_default_actions=False,
            show_side=True,
            show_status=True,
        )
        root.addWidget(self.catalog, 1)
        self._build_catalog_ui()
        self._wire()
        self._refresh_categories()
        self._refresh_entries()
        self.catalog.set_status_text("Catalog ready. Select an entry to inspect details.")

    def _build_catalog_ui(self) -> None:
        self.catalog.clear_slot("main")
        self.catalog.clear_slot("side")

        split = QSplitter(Qt.Horizontal, self.catalog)
        split.setChildrenCollapsible(False)
        split.setStretchFactor(0, 1)
        split.setStretchFactor(1, 2)

        left = QWidget(split)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        self.search_input = QLineEdit(left)
        self.search_input.setPlaceholderText("Search by title, tags, preset, theme, keywords...")
        self.search_input.setClearButtonEnabled(True)
        left_layout.addWidget(self.search_input)
        self.tags_input = QLineEdit(left)
        self.tags_input.setPlaceholderText("Optional tag filter (comma separated, e.g. dashboard,provider)")
        self.tags_input.setClearButtonEnabled(True)
        left_layout.addWidget(self.tags_input)

        category_label = QLabel("Categories", left)
        category_label.setProperty("role", "panel_title")
        left_layout.addWidget(category_label)
        self.category_list = QListWidget(left)
        self.category_list.setObjectName("GlassCatalogCategories")
        left_layout.addWidget(self.category_list, 1)

        entries_label = QLabel("Entries", left)
        entries_label.setProperty("role", "panel_title")
        left_layout.addWidget(entries_label)
        self.entry_list = QListWidget(left)
        self.entry_list.setObjectName("GlassCatalogEntries")
        left_layout.addWidget(self.entry_list, 2)

        right = QWidget(split)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        self.preview_title = QLabel("No catalog entry selected.", right)
        self.preview_title.setProperty("role", "title")
        self.preview_subtitle = QLabel("Choose an entry from the left rail.", right)
        self.preview_subtitle.setProperty("role", "subtitle")
        self.preview_subtitle.setWordWrap(True)
        right_layout.addWidget(self.preview_title)
        right_layout.addWidget(self.preview_subtitle)

        self.preview_host = QFrame(right)
        self.preview_host.setProperty("card", "true")
        preview_layout = QVBoxLayout(self.preview_host)
        preview_layout.setContentsMargins(10, 10, 10, 10)
        preview_layout.setSpacing(8)
        self.preview_placeholder = QLabel(
            "Preview is idle.\nUse Open Preview to build the selected catalog item.",
            self.preview_host,
        )
        self.preview_placeholder.setProperty("role", "panel_subtitle")
        self.preview_placeholder.setWordWrap(True)
        preview_layout.addWidget(self.preview_placeholder)
        self.preview_layout = preview_layout
        right_layout.addWidget(self.preview_host, 1)

        split.addWidget(left)
        split.addWidget(right)
        split.setSizes([420, 980])
        self.catalog.slots.main_slot.addWidget(split, 1)

        side_info = QWidget(self.catalog)
        side_layout = QVBoxLayout(side_info)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(8)

        self.meta_title = QLabel("Entry Details", side_info)
        self.meta_title.setProperty("role", "panel_title")
        side_layout.addWidget(self.meta_title)

        self.meta_summary = QLabel("No entry selected.", side_info)
        self.meta_summary.setProperty("role", "panel_subtitle")
        self.meta_summary.setWordWrap(True)
        side_layout.addWidget(self.meta_summary)

        self.meta_use_when = QLabel("", side_info)
        self.meta_use_when.setProperty("role", "caption")
        self.meta_use_when.setWordWrap(True)
        self.meta_use_when.setVisible(False)
        side_layout.addWidget(self.meta_use_when)

        self.meta_tags = QLabel("", side_info)
        self.meta_tags.setProperty("role", "caption")
        self.meta_tags.setWordWrap(True)
        self.meta_tags.setVisible(False)
        side_layout.addWidget(self.meta_tags)

        self.meta_text = QTextEdit(side_info)
        self.meta_text.setReadOnly(True)
        self.meta_text.setPlaceholderText("Metadata and discoverability details.")
        side_layout.addWidget(self.meta_text, 1)

        self.related_title = QLabel("See Also", side_info)
        self.related_title.setProperty("role", "panel_title")
        side_layout.addWidget(self.related_title)
        self.related_list = QListWidget(side_info)
        self.related_list.setObjectName("GlassCatalogRelated")
        side_layout.addWidget(self.related_list, 1)

        actions_row = QHBoxLayout()
        actions_row.setContentsMargins(0, 0, 0, 0)
        actions_row.setSpacing(8)
        self.btn_preview = QPushButton("Open Preview", side_info)
        self.btn_workspace = QPushButton("Add To Workspace", side_info)
        self.btn_clear_filters = QPushButton("Clear Filters", side_info)
        self.btn_clear_preview = QPushButton("Clear Preview", side_info)
        actions_row.addWidget(self.btn_preview)
        actions_row.addWidget(self.btn_workspace)
        actions_row.addWidget(self.btn_clear_filters)
        actions_row.addWidget(self.btn_clear_preview)
        side_layout.addLayout(actions_row)

        self.catalog.slots.side_slot.addWidget(side_info, 1)

    def _wire(self) -> None:
        self.search_input.textChanged.connect(lambda _text: self._refresh_entries())
        self.tags_input.textChanged.connect(lambda _text: self._refresh_entries())
        self.category_list.currentItemChanged.connect(lambda _curr, _prev: self._refresh_entries())
        self.entry_list.currentItemChanged.connect(self._on_entry_selected)
        self.btn_preview.clicked.connect(self._open_selected_preview)
        self.btn_workspace.clicked.connect(self._open_selected_in_workspace)
        self.btn_clear_filters.clicked.connect(self._clear_filters)
        self.btn_clear_preview.clicked.connect(self._clear_preview)
        self.related_list.itemDoubleClicked.connect(self._open_related_item)

    def _refresh_categories(self) -> None:
        selected = self._selected_category()
        self.category_list.blockSignals(True)
        self.category_list.clear()
        all_entries = list_catalog_entries(search=None)
        self._category_counts = {}
        for entry in all_entries:
            self._category_counts[entry.category] = int(self._category_counts.get(entry.category, 0)) + 1
        self._category_tags = {
            category: list_catalog_tags(category=category)
            for category in list_catalog_categories()
        }
        total_count = len(all_entries)

        categories = ("All",) + list_catalog_categories()
        for category in categories:
            if category == "All":
                display = f"All ({total_count})"
            else:
                display = f"{category} ({self._category_counts.get(category, 0)})"
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, category)
            self.category_list.addItem(item)
        self.category_list.blockSignals(False)
        self._select_category(selected if selected else "All")

    def _refresh_entries(self) -> None:
        selected_entry = self._selected_entry_id
        category = self._selected_category()
        query = self.search_input.text().strip()
        tags = self._selected_tags()
        entries = list_catalog_entries(
            category=None if category.lower() == "all" else category,
            search=query,
            tags=tags,
        )

        self._entry_order = [entry.entry_id for entry in entries]
        self.entry_list.blockSignals(True)
        self.entry_list.clear()
        if not entries:
            selected_tags_text = ", ".join(tags) if tags else "(none)"
            empty = QListWidgetItem(
                f"No entries for category '{category}' with query '{query or '(none)'}' and tags '{selected_tags_text}'."
            )
            empty.setFlags(Qt.NoItemFlags)
            self.entry_list.addItem(empty)
            self.entry_list.blockSignals(False)
            self._selected_entry_id = None
            self._show_entry_detail(None)
            self.catalog.set_status_text("No entries found for current filter. Try clearing query/tags.")
            return

        for entry in entries:
            item = QListWidgetItem(self._entry_text(entry))
            item.setData(Qt.UserRole, entry.entry_id)
            item.setToolTip(entry.description or entry.subtitle or entry.title)
            self.entry_list.addItem(item)
        self.entry_list.blockSignals(False)

        if selected_entry and selected_entry in self._entry_order:
            self._select_entry(selected_entry)
        else:
            first = entries[0]
            self._select_entry(first.entry_id)

        self.catalog.set_status_text(
            f"{len(entries)} entries available in '{category}'"
            + (f" filtered by query='{query}'." if query else "")
            + (f" tags={','.join(tags)}." if tags else ".")
        )

    def _on_entry_selected(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        entry_id = current.data(Qt.UserRole) if current is not None else None
        if not entry_id:
            self._selected_entry_id = None
            self._show_entry_detail(None)
            return
        self._selected_entry_id = str(entry_id)
        entry = get_catalog_entry(self._selected_entry_id)
        self._show_entry_detail(entry)

    def _show_entry_detail(self, entry: GlassCatalogEntry | None) -> None:
        if entry is None:
            self.preview_title.setText("No catalog entry selected.")
            self.preview_subtitle.setText("Choose an entry from the left rail, or clear active query/tag filters.")
            self.meta_title.setText("Entry Details")
            self.meta_summary.setText("No entry selected.")
            self.meta_use_when.setText("")
            self.meta_use_when.setVisible(False)
            self.meta_tags.setText("")
            self.meta_tags.setVisible(False)
            self.meta_text.setPlainText("")
            self.related_list.clear()
            return

        self.preview_title.setText(entry.title)
        self.preview_subtitle.setText(entry.subtitle or entry.description or "No subtitle.")
        category_count = self._category_counts.get(entry.category, 0)
        self.meta_title.setText(f"{entry.category} ({category_count}) · {entry.status.upper()}")
        hint_parts = []
        if entry.preset_hint:
            hint_parts.append(f"Preset: {entry.preset_hint}")
        if entry.theme_hint:
            hint_parts.append(f"Theme: {entry.theme_hint}")
        if entry.required_capabilities:
            hint_parts.append(f"Capabilities: {', '.join(entry.required_capabilities)}")
        if entry.icon_name:
            hint_parts.append(f"Icon: {entry.icon_name}")
        self.meta_summary.setText(" | ".join(hint_parts) if hint_parts else "No capability hints.")
        use_when = self._use_when_note(entry)
        self.meta_use_when.setText(f"Use when: {use_when}")
        self.meta_use_when.setVisible(True)
        if entry.tags:
            self.meta_tags.setText(f"Tags: {', '.join(entry.tags)}")
        else:
            category_tags = self._category_tags.get(entry.category, ())
            self.meta_tags.setText(f"Category tags: {', '.join(category_tags[:8])}" if category_tags else "Tags: (none)")
        self.meta_tags.setVisible(True)
        self.meta_text.setPlainText(
            json.dumps(
                {
                    "id": entry.entry_id,
                    "title": entry.title,
                    "subtitle": entry.subtitle,
                    "description": entry.description,
                    "category": entry.category,
                    "status": entry.status,
                    "tags": list(entry.tags),
                    "keywords": list(entry.keywords),
                    "preset_hint": entry.preset_hint,
                    "theme_hint": entry.theme_hint,
                    "required_capabilities": list(entry.required_capabilities),
                    "best_for": self._best_for_note(entry),
                    "use_when": use_when,
                    "category_tag_suggestions": list(self._category_tags.get(entry.category, ())),
                    "sort_order": entry.sort_order,
                    "metadata": entry.metadata,
                },
                indent=2,
                ensure_ascii=True,
            )
        )
        self._refresh_related(entry)

    def _best_for_note(self, entry: GlassCatalogEntry) -> str:
        if entry.best_for:
            return str(entry.best_for)
        category = str(entry.category or "").lower()
        if "data" in category:
            return "Operational monitoring, KPI review, and diagnostics-driven dashboards."
        if "controls" in category or "assets" in category:
            return "Composing reusable workstation controls and dense interaction surfaces."
        if "primitive" in category:
            return "Building reusable UI building blocks across multiple screens."
        if "runtime" in category:
            return "Testing orchestration, persistence, and integration boundary behaviors."
        return "General framework composition and visual exploration."

    def _use_when_note(self, entry: GlassCatalogEntry) -> str:
        if entry.use_when:
            return str(entry.use_when)
        if entry.metadata.get("use_when"):
            return str(entry.metadata.get("use_when"))
        if entry.keywords:
            return f"you need {', '.join(entry.keywords[:3])}."
        if entry.tags:
            return f"you are building {', '.join(entry.tags[:3])} surfaces."
        return "you need a reusable baseline composition."

    def _open_selected_preview(self) -> None:
        entry = self._current_entry()
        if entry is None:
            self.catalog.set_status_text("Select an entry before opening preview.")
            return
        if entry.builder is None:
            self.catalog.set_status_text(f"Entry '{entry.entry_id}' has no preview builder.")
            return
        try:
            widget = entry.builder(self.preview_host)
            if widget is None:
                raise RuntimeError("builder returned None")
        except Exception as exc:  # noqa: BLE001
            self.catalog.set_status_text(f"Preview failed for '{entry.entry_id}': {exc}")
            return
        self._render_preview_widget(widget, entry)
        self.catalog.set_status_text(f"Preview opened for '{entry.title}'.")

    def _open_selected_in_workspace(self) -> None:
        entry = self._current_entry()
        if entry is None:
            self.catalog.set_status_text("Select an entry before adding to workspace.")
            return
        if entry.builder is None:
            self.catalog.set_status_text(f"Entry '{entry.entry_id}' has no builder.")
            return
        if self.catalog.workspace_tabs is None:
            self._open_selected_preview()
            return

        try:
            widget = entry.builder(self.catalog)
            if widget is None:
                raise RuntimeError("builder returned None")
            self._preview_instance_counter += 1
            tab_id = f"catalog_{entry.entry_id}_{self._preview_instance_counter}"
            self.catalog.add_workspace_tab(
                tab_id=tab_id,
                title=entry.title,
                widget=widget,
                state="visible",
                icon_name=entry.icon_name or "layers",
                tooltip=entry.description,
                make_current=True,
                metadata={"catalog_entry_id": entry.entry_id},
            )
            self.catalog.set_status_text(f"'{entry.title}' added to workspace tabs.")
        except Exception as exc:  # noqa: BLE001
            self.catalog.set_status_text(f"Failed to add '{entry.title}' to workspace: {exc}")

    def _render_preview_widget(self, widget: QWidget, entry: GlassCatalogEntry) -> None:
        _clear_layout(self.preview_layout)
        widget.setParent(self.preview_host)
        self.preview_layout.addWidget(widget, 1)
        badge = QLabel(
            f"{entry.category} · {entry.status.upper()} · tags: {', '.join(entry.tags) if entry.tags else '(none)'}",
            self.preview_host,
        )
        badge.setProperty("role", "caption")
        badge.setWordWrap(True)
        self.preview_layout.addWidget(badge)

    def _clear_preview(self) -> None:
        _clear_layout(self.preview_layout)
        placeholder = QLabel(
            "Preview is idle.\nUse Open Preview to build the selected catalog item.",
            self.preview_host,
        )
        placeholder.setProperty("role", "panel_subtitle")
        placeholder.setWordWrap(True)
        self.preview_layout.addWidget(placeholder)
        self.catalog.set_status_text("Preview cleared.")

    def _clear_filters(self) -> None:
        self.search_input.clear()
        self.tags_input.clear()
        self._select_category("All")
        self._refresh_entries()
        self.catalog.set_status_text("Catalog filters cleared.")

    def _refresh_related(self, entry: GlassCatalogEntry) -> None:
        self.related_list.clear()
        related = self._related_entries(entry, limit=8)
        if not related:
            item = QListWidgetItem("No related entries found.")
            item.setFlags(Qt.NoItemFlags)
            self.related_list.addItem(item)
            return
        for related_entry in related:
            item = QListWidgetItem(f"{related_entry.title} · {related_entry.category}")
            item.setToolTip(related_entry.subtitle or related_entry.description)
            item.setData(Qt.UserRole, related_entry.entry_id)
            self.related_list.addItem(item)

    def _related_entries(self, entry: GlassCatalogEntry, *, limit: int = 8) -> list[GlassCatalogEntry]:
        candidates = list_catalog_entries(search=None)
        target_tags = set(entry.tags)
        target_keywords = set(entry.keywords)
        scored: list[tuple[int, GlassCatalogEntry]] = []
        for item in candidates:
            if item.entry_id == entry.entry_id:
                continue
            score = 0
            if item.category == entry.category:
                score += 3
            score += len(target_tags.intersection(item.tags)) * 2
            score += len(target_keywords.intersection(item.keywords))
            if score <= 0:
                continue
            scored.append((score, item))
        scored.sort(key=lambda pair: (-pair[0], pair[1].sort_order, pair[1].title.lower()))
        return [item for _, item in scored[: max(1, int(limit))]]

    def _open_related_item(self, item: QListWidgetItem) -> None:
        entry_id = str(item.data(Qt.UserRole) or "").strip()
        if not entry_id:
            return
        self._select_entry(entry_id)

    def _entry_text(self, entry: GlassCatalogEntry) -> str:
        tags = ", ".join(entry.tags[:3]) if entry.tags else "no tags"
        subtitle = entry.subtitle or entry.description or ""
        return (
            f"{entry.title}\n"
            f"{subtitle}\n"
            f"{entry.category} · {entry.status.upper()} · {tags}"
        )

    def _selected_category(self) -> str:
        item = self.category_list.currentItem()
        if item is None:
            return "All"
        value = str(item.data(Qt.UserRole) or item.text() or "All").strip()
        return value or "All"

    def _selected_tags(self) -> tuple[str, ...]:
        raw = self.tags_input.text().strip()
        if not raw:
            return ()
        values: list[str] = []
        for item in raw.split(","):
            normalized = str(item or "").strip().lower()
            if normalized:
                values.append(normalized)
        return tuple(values)

    def _select_category(self, category: str) -> None:
        target = str(category or "All").strip().lower()
        for index in range(self.category_list.count()):
            item = self.category_list.item(index)
            value = str(item.data(Qt.UserRole) or item.text()).strip().lower()
            if value == target:
                self.category_list.setCurrentRow(index)
                return
        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)

    def _select_entry(self, entry_id: str) -> None:
        target = str(entry_id or "").strip().lower()
        for index in range(self.entry_list.count()):
            item = self.entry_list.item(index)
            if str(item.data(Qt.UserRole) or "").strip().lower() == target:
                self.entry_list.setCurrentRow(index)
                return

    def _current_entry(self) -> GlassCatalogEntry | None:
        if not self._selected_entry_id:
            return None
        return get_catalog_entry(self._selected_entry_id)
