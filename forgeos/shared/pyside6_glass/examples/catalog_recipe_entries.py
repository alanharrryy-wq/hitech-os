from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import QWidget

from ..foundry import build_foundry_preview, get_foundry_recipe, list_foundry_recipes, register_builtin_foundry


@dataclass(frozen=True, slots=True)
class RecipeCatalogEntrySpec:
    entry_id: str
    recipe_id: str
    title: str
    subtitle: str
    description: str
    category: str = "Recipe Foundry"
    tags: tuple[str, ...] = ("recipe", "foundry", "premium")
    status: str = "stable"
    keywords: tuple[str, ...] = ()
    best_for: str = ""
    use_when: str = ""
    sort_order: int = 800
    icon_name: str | None = "sparkles"


def build_recipe_catalog_entry(spec: RecipeCatalogEntrySpec, parent: QWidget | None = None) -> QWidget:
    register_builtin_foundry()
    return build_foundry_preview(spec.recipe_id, parent=parent)


def iter_recipe_catalog_specs() -> tuple[RecipeCatalogEntrySpec, ...]:
    register_builtin_foundry()
    specs: list[RecipeCatalogEntrySpec] = []
    for recipe_id in list_foundry_recipes():
        recipe = get_foundry_recipe(recipe_id)
        keywords = tuple(sorted(set(recipe.tags) | {{recipe.recipe_id, recipe.payload["experience"]["beauty_profile"]}}))
        specs.append(
            RecipeCatalogEntrySpec(
                entry_id=f"recipe.{{recipe.recipe_id}}",
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
    "RecipeCatalogEntrySpec",
    "build_recipe_catalog_entry",
    "iter_recipe_catalog_specs",
]
