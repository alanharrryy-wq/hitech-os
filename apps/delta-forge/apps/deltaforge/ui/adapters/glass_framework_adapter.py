from __future__ import annotations

from pathlib import Path

from forgeos.shared.pyside6_glass import (
    GlassActionConfig,
    GlassAnimationConfig,
    GlassRegionConfig,
    GlassTabConfig,
    GlassTemplateConfig,
    GlassThemeConfig,
    GlassTypographyConfig,
    register_icon_pack,
    set_default_icon_pack,
)


_CONFIGURED = False


def configure_deltaforge_glass_framework() -> None:
    """App-specific adapter wiring for shared glass framework assets."""

    global _CONFIGURED
    if _CONFIGURED:
        return

    repo_root = Path(__file__).resolve().parents[4]
    icon_dir = repo_root / "apps" / "deltaforge" / "assets" / "icons"
    if icon_dir.exists():
        register_icon_pack("deltaforge", icon_dir, metadata={"owner": "deltaforge"})
        set_default_icon_pack("deltaforge")
    _CONFIGURED = True


def build_deltaforge_template_config() -> GlassTemplateConfig:
    """DeltaForge-specific default composition without polluting shared core."""

    return GlassTemplateConfig(
        title="DeltaForge Workspace",
        subtitle="Session-driven workstation powered by shared glass framework primitives.",
        eyebrow="DELTAFORGE",
        variant="selector",
        theme=GlassThemeConfig(
            theme_id="silver_frost_cyan",
            density="comfortable",
            experience_mode="operator",
            typography=GlassTypographyConfig(scale="md"),
            animation=GlassAnimationConfig(level="standard", reduced_motion=False),
        ),
        regions=GlassRegionConfig(
            show_side=True,
            show_footer=True,
            show_status=True,
            main_side_sizes=(760, 420),
        ),
        tabs=GlassTabConfig(
            enabled=True,
            movable=False,
            closable=False,
            document_mode=True,
            default_tab_id="session_workspace",
            default_tab_title="Session Workspace",
        ),
        actions=GlassActionConfig(
            include_default_actions=True,
            cancel_text="Cancel",
            submit_text="Execute",
            cancel_variant="danger",
            submit_variant="primary",
        ),
        apply_stylesheet=True,
        with_chrome=True,
    )
