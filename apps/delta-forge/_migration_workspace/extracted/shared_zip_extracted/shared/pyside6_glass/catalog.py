from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Callable


CatalogBuilder = Callable[[Any | None], Any]


@dataclass(frozen=True, slots=True)
class GlassCatalogEntry:
    entry_id: str
    title: str
    subtitle: str = ""
    description: str = ""
    category: str = "General"
    tags: tuple[str, ...] = ()
    builder: CatalogBuilder | None = None
    preset_hint: str | None = None
    theme_hint: str | None = None
    status: str = "stable"
    required_capabilities: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    best_for: str = ""
    use_when: str = ""
    sort_order: int = 100
    icon_name: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def searchable_text(self) -> str:
        parts = [
            self.entry_id,
            self.title,
            self.subtitle,
            self.description,
            self.category,
            " ".join(self.tags),
            " ".join(self.keywords),
            self.best_for,
            self.use_when,
            self.preset_hint or "",
            self.theme_hint or "",
            self.status,
        ]
        return " ".join(str(item).lower() for item in parts if item)


_CATALOG_LOCK = RLock()
_CATALOG_ENTRIES: dict[str, GlassCatalogEntry] = {}
_BUILTINS_REGISTERED = False


def _normalize_values(values: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    if not values:
        return ()
    output: list[str] = []
    for item in values:
        normalized = str(item or "").strip().lower()
        if normalized:
            output.append(normalized)
    return tuple(output)


def register_catalog_entry(
    entry: GlassCatalogEntry | None = None,
    *,
    entry_id: str | None = None,
    title: str | None = None,
    subtitle: str = "",
    description: str = "",
    category: str = "General",
    tags: tuple[str, ...] | list[str] = (),
    builder: CatalogBuilder | None = None,
    preset_hint: str | None = None,
    theme_hint: str | None = None,
    status: str = "stable",
    required_capabilities: tuple[str, ...] | list[str] = (),
    keywords: tuple[str, ...] | list[str] = (),
    best_for: str = "",
    use_when: str = "",
    sort_order: int = 100,
    icon_name: str | None = None,
    metadata: dict[str, str] | None = None,
    override: bool = False,
) -> GlassCatalogEntry:
    candidate = entry
    if candidate is None:
        normalized_id = str(entry_id or "").strip().lower()
        normalized_title = str(title or "").strip()
        if not normalized_id:
            raise ValueError("entry_id is required")
        if not normalized_title:
            raise ValueError("title is required")
        candidate = GlassCatalogEntry(
            entry_id=normalized_id,
            title=normalized_title,
            subtitle=str(subtitle or ""),
            description=str(description or ""),
            category=str(category or "General"),
            tags=tuple(str(item).strip() for item in tags if str(item).strip()),
            builder=builder,
            preset_hint=str(preset_hint).strip() if preset_hint else None,
            theme_hint=str(theme_hint).strip() if theme_hint else None,
            status=str(status or "stable").strip().lower() or "stable",
            required_capabilities=tuple(
                str(item).strip() for item in required_capabilities if str(item).strip()
            ),
            keywords=tuple(str(item).strip() for item in keywords if str(item).strip()),
            best_for=str(best_for or "").strip(),
            use_when=str(use_when or "").strip(),
            sort_order=int(sort_order),
            icon_name=str(icon_name).strip() if icon_name else None,
            metadata=dict(metadata or {}),
        )
    else:
        if not isinstance(candidate, GlassCatalogEntry):
            raise TypeError("entry must be GlassCatalogEntry")
        normalized_id = str(candidate.entry_id or "").strip().lower()
        if not normalized_id:
            raise ValueError("entry.entry_id is required")
        candidate = GlassCatalogEntry(
            entry_id=normalized_id,
            title=candidate.title,
            subtitle=candidate.subtitle,
            description=candidate.description,
            category=candidate.category,
            tags=tuple(candidate.tags),
            builder=candidate.builder,
            preset_hint=candidate.preset_hint,
            theme_hint=candidate.theme_hint,
            status=str(candidate.status or "stable").strip().lower() or "stable",
            required_capabilities=tuple(candidate.required_capabilities),
            keywords=tuple(candidate.keywords),
            best_for=str(candidate.best_for or "").strip(),
            use_when=str(candidate.use_when or "").strip(),
            sort_order=int(candidate.sort_order),
            icon_name=candidate.icon_name,
            metadata=dict(candidate.metadata),
        )

    with _CATALOG_LOCK:
        if not override and candidate.entry_id in _CATALOG_ENTRIES:
            raise ValueError(f"catalog entry '{candidate.entry_id}' already exists")
        _CATALOG_ENTRIES[candidate.entry_id] = candidate
    return candidate


def get_catalog_entry(entry_id: str, *, include_builtins: bool = True) -> GlassCatalogEntry | None:
    if include_builtins:
        register_builtin_catalog_entries()
    key = str(entry_id or "").strip().lower()
    if not key:
        return None
    with _CATALOG_LOCK:
        return _CATALOG_ENTRIES.get(key)


def list_catalog_entries(
    *,
    category: str | None = None,
    search: str | None = None,
    status: str | None = None,
    tags: tuple[str, ...] | list[str] | None = None,
    required_capabilities: tuple[str, ...] | list[str] | None = None,
    limit: int | None = None,
    include_builtins: bool = True,
) -> list[GlassCatalogEntry]:
    if include_builtins:
        register_builtin_catalog_entries()
    selected_category = str(category or "").strip().lower()
    query = str(search or "").strip().lower()
    selected_status = str(status or "").strip().lower()
    selected_tags = _normalize_values(tags)
    selected_capabilities = _normalize_values(required_capabilities)
    with _CATALOG_LOCK:
        values = list(_CATALOG_ENTRIES.values())

    output: list[GlassCatalogEntry] = []
    for item in values:
        if selected_category and selected_category not in {"all", item.category.lower()}:
            continue
        if selected_status and item.status.lower() != selected_status:
            continue
        if selected_tags and not set(selected_tags).issubset({str(tag).strip().lower() for tag in item.tags}):
            continue
        if selected_capabilities and not set(selected_capabilities).issubset(
            {str(capability).strip().lower() for capability in item.required_capabilities}
        ):
            continue
        if query and query not in item.searchable_text():
            continue
        output.append(item)

    output.sort(key=lambda item: (str(item.category).lower(), int(item.sort_order), item.title.lower()))
    if limit is not None:
        output = output[: max(0, int(limit))]
    return output


def list_catalog_categories(*, include_builtins: bool = True) -> tuple[str, ...]:
    if include_builtins:
        register_builtin_catalog_entries()
    with _CATALOG_LOCK:
        categories = sorted({str(item.category or "General") for item in _CATALOG_ENTRIES.values()})
    return tuple(categories)


def list_catalog_tags(
    *,
    category: str | None = None,
    include_builtins: bool = True,
) -> tuple[str, ...]:
    if include_builtins:
        register_builtin_catalog_entries()
    selected_category = str(category or "").strip().lower()
    with _CATALOG_LOCK:
        values = list(_CATALOG_ENTRIES.values())
    tags: set[str] = set()
    for item in values:
        if selected_category and selected_category not in {"all", str(item.category).lower()}:
            continue
        for tag in item.tags:
            normalized = str(tag or "").strip().lower()
            if normalized:
                tags.add(normalized)
    return tuple(sorted(tags))


def register_builtin_catalog_entries(*, force: bool = False) -> int:
    global _BUILTINS_REGISTERED
    with _CATALOG_LOCK:
        if _BUILTINS_REGISTERED and not force:
            return len(_CATALOG_ENTRIES)
    from .examples.catalog_builtin import register_builtin_catalog_entries as register_builtins

    register_builtins(force=force)
    with _CATALOG_LOCK:
        _BUILTINS_REGISTERED = True
        return len(_CATALOG_ENTRIES)


def _clear_catalog_registry_for_tests() -> None:
    global _BUILTINS_REGISTERED
    with _CATALOG_LOCK:
        _CATALOG_ENTRIES.clear()
        _BUILTINS_REGISTERED = False
