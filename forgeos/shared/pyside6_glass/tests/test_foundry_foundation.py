from forgeos.shared.pyside6_glass.foundry_foundation import (
    FOUNDATION_SCHEMA_VERSION,
    get_foundry_schema,
    get_foundry_recipe,
    list_beauty_profiles,
    list_color_stories,
    list_foundry_recipes,
    list_layout_packs,
    list_motion_profiles,
    list_shell_packs,
    register_builtin_foundry_foundation,
    validate_foundry_recipe,
)


def test_schema_version_and_required_sections() -> None:
    schema = get_foundry_schema()
    assert schema["schema_version"] == FOUNDATION_SCHEMA_VERSION
    assert "meta" in schema["properties"]
    assert "experience" in schema["properties"]
    assert "surfaces" in schema["properties"]


def test_registry_tokens_exist() -> None:
    register_builtin_foundry_foundation(force=True)
    assert "premium_focus" in list_beauty_profiles()
    assert "graphite_cyan" in list_color_stories()
    assert "snappy_deluxe" in list_motion_profiles()
    assert "balanced_split" in list_layout_packs()
    assert "frameless_glass" in list_shell_packs()


def test_builtin_recipes_available() -> None:
    register_builtin_foundry_foundation(force=True)
    recipe_ids = list_foundry_recipes()
    assert "foundation.ops_console_premium" in recipe_ids
    recipe = get_foundry_recipe("foundation.ops_console_premium")
    assert recipe.payload["meta"]["title"] == "Operations Console Premium"
    assert len(recipe.surfaces) >= 5


def test_validation_normalizes_surface_ids_and_regions() -> None:
    normalized = validate_foundry_recipe(
        {
            "meta": {"id": "demo", "title": "Demo"},
            "experience": {
                "beauty_profile": "premium_focus",
                "color_story": "graphite_cyan",
                "motion_profile": "snappy_deluxe",
            },
            "surfaces": [
                {"id": "Main Grid", "type": "data_grid", "region": "main", "title": "Rows"},
                {"id": "Side Inspector", "type": "inspector_panel", "region": "side", "title": "Inspector"},
            ],
        }
    )
    assert normalized["meta"]["id"] == "demo"
    assert normalized["surfaces"][0]["id"] in {"main_grid", "side_inspector"}
    assert len(normalized["surfaces"]) == 2
