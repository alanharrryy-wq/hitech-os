"""Builder y tooling de scaffolding para `ui_baseline`."""

from .catalog import INGREDIENT_CATALOG
from .generator import generate_screen, render_screen_code
from .preview import preview_recipe
from .recipe import ScreenRecipe, derive_class_name

__all__ = [
    "INGREDIENT_CATALOG",
    "ScreenRecipe",
    "derive_class_name",
    "generate_screen",
    "preview_recipe",
    "render_screen_code",
]
