from __future__ import annotations

from dataclasses import dataclass

from .catalog import get_ingredient
from .recipe import ScreenRecipe


@dataclass(frozen=True, slots=True)
class PreviewSummary:
    active_zones: tuple[str, ...]
    ingredients: tuple[str, ...]
    visual_intent: dict[str, str]
    estimated_files: tuple[str, ...]

    def to_markdown(self) -> str:
        lines = [
            "# Preview de receta",
            "",
            "## Zonas activas",
            *(f"- {zone}" for zone in self.active_zones),
            "",
            "## Ingredientes",
            *(f"- {ingredient}" for ingredient in self.ingredients),
            "",
            "## Intención visual",
        ]
        lines.extend(f"- {key}: {value}" for key, value in self.visual_intent.items())
        lines.extend(["", "## Archivos estimados", *(f"- {item}" for item in self.estimated_files)])
        return "\n".join(lines)



def preview_recipe(recipe: ScreenRecipe) -> PreviewSummary:
    ingredient_labels = []
    for ingredient_id in recipe.ingredients:
        spec = get_ingredient(ingredient_id)
        ingredient_labels.append(spec.label if spec else ingredient_id)

    return PreviewSummary(
        active_zones=tuple(recipe.active_zones()),
        ingredients=tuple(ingredient_labels),
        visual_intent=recipe.normalized_visual_intent(),
        estimated_files=(str(recipe.output_path()),),
    )
