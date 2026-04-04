from __future__ import annotations

from pathlib import Path
from textwrap import indent

from .catalog import get_ingredient
from .recipe import ScreenRecipe

_ZONE_ORDER = ("hero", "main", "side", "footer", "status")



def _panel_block(title: str, body: str) -> str:
    return f'''
        panel = QGroupBox("{title}", self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        description = QLabel("{body}", panel)
        description.setWordWrap(True)
        layout.addWidget(description)
        return panel
'''.rstrip()



def _ingredient_method_name(ingredient_id: str) -> str:
    return f"_ingredient_{ingredient_id}"



def _build_ingredient_method(ingredient_id: str) -> str:
    spec = get_ingredient(ingredient_id)
    if spec is None:
        title = ingredient_id.replace("_", " ").title()
        description = "Placeholder genérico generado automáticamente."
    else:
        title = spec.label
        description = spec.description

    return f'''
    def {_ingredient_method_name(ingredient_id)}(self) -> QWidget:
{indent(_panel_block(title, description), " " * 8)}
'''.rstrip()



def _zone_method(zone: str, recipe: ScreenRecipe, ingredient_ids: list[str]) -> str:
    if zone not in recipe.active_zones():
        return f'''
    def build_{zone}(self) -> QWidget | None:
        return None
'''.rstrip()

    calls = []
    for ingredient_id in ingredient_ids:
        calls.append(f"layout.addWidget(self.{_ingredient_method_name(ingredient_id)}())")

    if not calls:
        calls.extend(
            [
                'placeholder = QLabel("Contenido placeholder para revisión humana.", container)',
                "placeholder.setWordWrap(True)",
                "layout.addWidget(placeholder)",
            ]
        )

    call_block = "\n        ".join(calls)
    return f'''
    def build_{zone}(self) -> QWidget | None:
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        {call_block}
        return container
'''.rstrip()



def render_screen_code(recipe: ScreenRecipe) -> str:
    class_name = recipe.resolved_class_name()
    visual_intent = recipe.normalized_visual_intent()
    by_zone: dict[str, list[str]] = {zone: [] for zone in _ZONE_ORDER}
    for ingredient_id in recipe.ingredients:
        spec = get_ingredient(ingredient_id)
        if spec is not None:
            by_zone[spec.suggested_zone].append(spec.id)

    methods = []
    used_ingredients = []
    for zone in _ZONE_ORDER:
        methods.append(_zone_method(zone, recipe, by_zone.get(zone, [])))
        used_ingredients.extend(by_zone.get(zone, []))

    ingredient_methods = []
    for ingredient_id in dict.fromkeys(used_ingredients):
        ingredient_methods.append(_build_ingredient_method(ingredient_id))

    return f'''from __future__ import annotations

from PySide6.QtWidgets import QApplication, QGroupBox, QLabel, QVBoxLayout, QWidget

from forgeos.shared.pyside6_glass.ui_baseline.screen_template import VisualScreenTemplate


class {class_name}(VisualScreenTemplate):
    """Pantalla generada por `ui_baseline.builder.generator`."""

    visual_role = "{visual_intent['visual_role']}"
    visual_variant = "{visual_intent['visual_variant']}"
    visual_emphasis = "{visual_intent['visual_emphasis']}"
    visual_fx_level = "{visual_intent['visual_fx_level']}"
    visual_level = "{visual_intent['visual_level']}"
    data_state = "{visual_intent['data_state']}"
    base_preset = "{visual_intent['preset']}"

    enable_hero = {recipe.include_hero!r}
    enable_main = {recipe.include_main!r}
    enable_side = {recipe.include_side!r}
    enable_footer = {recipe.include_footer!r}
    enable_status = {recipe.include_status!r}

{chr(10).join(ingredient_methods)}

{chr(10).join(methods)}


def main() -> int:
    app = QApplication.instance() or QApplication([])
    widget = {class_name}()
    widget.setWindowTitle("{class_name}")
    widget.resize(1200, 760)
    widget.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
'''.rstrip() + "\n"



def generate_screen(recipe: ScreenRecipe, overwrite: bool = False) -> Path:
    path = recipe.output_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists() and not overwrite:
        raise FileExistsError(f"El archivo ya existe: {path}")

    path.write_text(render_screen_code(recipe), encoding="utf-8")
    return path
