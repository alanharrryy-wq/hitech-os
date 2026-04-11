from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import QWidget

from ..foundry_foundation import (
    build_foundry_preview,
    get_foundry_recipe,
    list_foundry_recipes,
    register_builtin_foundry_foundation,
)


@dataclass(frozen=True, slots=True)
class FoundryFoundationCatalogEntrySpec:
    entry_id: str
    recipe_id: str
    title: str
    subtitle: str
    description: str
    category: str = "Foundry Foundation"
    tags: tuple[str, ...] = ("foundry", "foundation", "premium")
    status: str = "stable"
    keywords: tuple[str, ...] = ()
    best_for: str = ""
    use_when: str = ""
    sort_order: int = 900
    icon_name: str | None = "sparkles"


def build_foundry_foundation_catalog_entry(spec: FoundryFoundationCatalogEntrySpec, parent: QWidget | None = None) -> QWidget:
    register_builtin_foundry_foundation()
    return build_foundry_preview(spec.recipe_id, parent=parent)


def iter_foundry_foundation_catalog_specs() -> tuple[FoundryFoundationCatalogEntrySpec, ...]:
    register_builtin_foundry_foundation()
    specs: list[FoundryFoundationCatalogEntrySpec] = []
    for recipe_id in list_foundry_recipes():
        recipe = get_foundry_recipe(recipe_id)
        beauty = recipe.payload["experience"]["beauty_profile"]
        color_story = recipe.payload["experience"]["color_story"]
        keywords = tuple(sorted(set(recipe.tags) | {recipe.recipe_id, beauty, color_story}))
        specs.append(
            FoundryFoundationCatalogEntrySpec(
                entry_id=f"foundation.{recipe.recipe_id}",
                recipe_id=recipe.recipe_id,
                title=recipe.title,
                subtitle=recipe.subtitle,
                description=recipe.description,
                category=recipe.category,
                tags=recipe.tags,
                status=recipe.status,
                keywords=keywords,
                best_for=recipe.best_for,
                use_when=recipe.use_when,
                sort_order=recipe.sort_order,
                icon_name=recipe.icon_name,
            )
        )
    return tuple(sorted(specs, key=lambda item: (item.sort_order, item.title.lower())))


__all__ = [
    "FoundryFoundationCatalogEntrySpec",
    "build_foundry_foundation_catalog_entry",
    "iter_foundry_foundation_catalog_specs",
]
