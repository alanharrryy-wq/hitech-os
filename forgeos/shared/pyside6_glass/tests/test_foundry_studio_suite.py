from __future__ import annotations

from pyside6_glass.foundry_studio_suite import (
    STUDIO_SUITE_VERSION,
    StudioVariantSelection,
    list_studio_tools,
    studio_suite_registry_snapshot,
)


def test_studio_version() -> None:
    assert STUDIO_SUITE_VERSION == "foundry.studio_suite.v1"


def test_tools_available() -> None:
    tools = list_studio_tools()
    assert any(tool.tool_id == "doctor" for tool in tools)
    assert any(tool.tool_id == "gallery" for tool in tools)


def test_snapshot_has_tools() -> None:
    snap = studio_suite_registry_snapshot()
    assert snap["version"] == STUDIO_SUITE_VERSION
    assert snap["tools"]


def test_selection_dataclass() -> None:
    selection = StudioVariantSelection(
        recipe_id="demo",
        beauty_profile="premium_focus",
        color_story="graphite_cyan",
        motion_profile="snappy_deluxe",
        layout_pack="ops_grid",
        shell_pack="command_shell",
        interaction_profile="operator_dense",
        density="comfortable",
    )
    assert selection.recipe_id == "demo"
