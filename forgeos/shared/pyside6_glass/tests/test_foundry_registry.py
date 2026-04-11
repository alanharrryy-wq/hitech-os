from forgeos.shared.pyside6_glass.foundry import (
    get_foundry_recipe,
    get_recipe_schema,
    list_beauty_profiles,
    list_color_stories,
    list_foundry_recipes,
    list_motion_profiles,
    register_builtin_foundry,
    validate_foundry_recipe,
)


def test_recipe_schema_has_required_sections() -> None:
    schema = get_recipe_schema()
    assert schema["properties"]["meta"]["type"] == "object"
    assert "surfaces" in schema["properties"]
    assert "behavior" in schema["properties"]
    assert "quality" in schema["properties"]


def test_builtin_foundry_registration_exposes_core_tokens() -> None:
    register_builtin_foundry(force=True)
    assert "premium_focus" in list_beauty_profiles()
    assert "graphite_cyan" in list_color_stories()
    assert "snappy_deluxe" in list_motion_profiles()


def test_builtin_foundry_recipes_are_available() -> None:
    register_builtin_foundry(force=True)
    recipe_ids = list_foundry_recipes()
    assert "recipe.ops_console_premium" in recipe_ids
    assert "recipe.analytics_cinematic" in recipe_ids
    recipe = get_foundry_recipe("recipe.ops_console_premium")
    assert recipe.payload["meta"]["title"] == "Operations Console Premium"


def test_validate_foundry_recipe_normalizes_surfaces() -> None:
    normalized = validate_foundry_recipe(
        {{
            "meta": {{"id": "demo", "title": "Demo"}},
            "experience": {{
                "beauty_profile": "premium_focus",
                "color_story": "graphite_cyan",
                "motion_profile": "snappy_deluxe",
            }},
            "surfaces": [
                {{"id": "hero", "type": "hero_banner", "region": "hero", "title": "Hero"}},
                {{"id": "table", "type": "data_grid", "region": "main", "title": "Rows"}},
            ],
        }}
    )
    assert normalized["meta"]["id"] == "demo"
    assert len(normalized["surfaces"]) == 2
