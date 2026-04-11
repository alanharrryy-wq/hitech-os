from __future__ import annotations

"""
Declarative recipe foundry for premium workstation-style PySide6 glass experiences.

Design intent
-------------
This module gives the framework a higher-level "recipe" contract so teams can
describe beautiful interfaces by intent instead of hand-assembling loose widgets.

The recipe model is deliberately biased toward:
- composition by regions and surfaces instead of ad-hoc absolute positioning
- layout presets instead of resize-event micromanagement
- lazy and deferred loading instead of front-loading every heavy widget
- beauty encoded as tokens (beauty profile, color story, motion profile)
- predictable shell ownership via GlassPanelTemplate + GlassWorkspaceRuntime

The contract is intentionally conservative about layout mutation so that "pretty"
does not come at the cost of layers colliding, tabs becoming unusable, or
resize behavior becoming brittle.
"""

from copy import deepcopy
from dataclasses import dataclass, field
import json
from typing import Any, Callable, Iterable, Mapping, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from .assets import (
    CollapsibleSection,
    CompactToolbar,
    ControlCard,
    FilterChipBar,
    HeroPanel,
    MiniLegend,
    ParameterPanel,
    SearchCommandBar,
    StatPill,
    StatusPill,
    TogglePill,
)
from .config import (
    GlassAnimationConfig,
    GlassLayoutConfig,
    GlassRegionConfig,
    GlassTemplateConfig,
    GlassThemeConfig,
    GlassTypographyConfig,
    GlassVisualScaleConfig,
    get_template_preset,
    list_template_presets,
    register_template_preset,
)
from .primitives import (
    DashboardWidgetShell,
    EmptyStateCard,
    ErrorStateCard,
    LoadingStateCard,
    MetricValue,
    PanelHeader,
    QuickActionsStrip,
    StatCard,
)
from .runtime import (
    GlassRuntimeContext,
    GlassVisibilityPolicy,
    GlassVisibilityRule,
    GlassWorkspaceRuntime,
)
from .template import GlassPanelTemplate, GlassWorkspaceTabSpec
from .theme import GlassPalette, list_theme_ids, register_theme

RECIPE_SCHEMA_VERSION = "foundry.recipe.v1"

BEAUTY_PROFILES: dict[str, dict[str, Any]] = {
    "premium_focus": {
        "description": "High-contrast premium workstation balance with restrained ornament.",
        "default_preset": "foundry_premium_focus",
        "default_density": "comfortable",
        "shadow_depth": 0.42,
        "blur_strength": 0.20,
        "glow_strength": 0.10,
    },
    "cinematic_glass": {
        "description": "Layered glass atmosphere with richer depth and soft luminous accents.",
        "default_preset": "foundry_cinematic_glass",
        "default_density": "comfortable",
        "shadow_depth": 0.56,
        "blur_strength": 0.32,
        "glow_strength": 0.18,
    },
    "industrial_precision": {
        "description": "Tighter, denser, sharper operational language with reduced decorative drift.",
        "default_preset": "foundry_precision_inspector",
        "default_density": "compact",
        "shadow_depth": 0.30,
        "blur_strength": 0.08,
        "glow_strength": 0.04,
    },
    "executive_signal": {
        "description": "Editorial spacing with dashboard-grade hierarchy for overview-driven rooms.",
        "default_preset": "foundry_command_wall",
        "default_density": "comfortable",
        "shadow_depth": 0.38,
        "blur_strength": 0.14,
        "glow_strength": 0.08,
    },
}

COLOR_STORIES: dict[str, dict[str, Any]] = {
    "graphite_cyan": {
        "theme_id": "graphite_cyan_foundry",
        "description": "Graphite shell with cool cyan accent energy.",
    },
    "obsidian_violet": {
        "theme_id": "obsidian_violet_foundry",
        "description": "Dark obsidian shell with violet detail accents.",
    },
    "frosted_emerald": {
        "theme_id": "frosted_emerald_foundry",
        "description": "Cool glass shell with emerald operational accents.",
    },
    "ember_gold": {
        "theme_id": "ember_gold_foundry",
        "description": "Dark command shell with amber/gold priority emphasis.",
    },
}

MOTION_PROFILES: dict[str, dict[str, Any]] = {
    "none": {
        "description": "Motion-minimal profile for deterministic operator contexts.",
        "animation_level": "none",
        "transition_ms": 0,
        "hover_ms": 0,
        "panel_toggle_ms": 0,
        "tab_switch_ms": 0,
    },
    "subtle": {
        "description": "Low-amplitude motion profile for most productivity surfaces.",
        "animation_level": "subtle",
        "transition_ms": 150,
        "hover_ms": 90,
        "panel_toggle_ms": 120,
        "tab_switch_ms": 120,
    },
    "snappy_deluxe": {
        "description": "Crisp, premium motion that keeps operational cadence without syrup.",
        "animation_level": "normal",
        "transition_ms": 180,
        "hover_ms": 110,
        "panel_toggle_ms": 150,
        "tab_switch_ms": 140,
    },
    "expressive_glass": {
        "description": "Richer motion for showroom or cinematic surfaces.",
        "animation_level": "normal",
        "transition_ms": 240,
        "hover_ms": 140,
        "panel_toggle_ms": 190,
        "tab_switch_ms": 180,
    },
}

SURFACE_TYPES: tuple[str, ...] = (
    "hero_banner",
    "metric_strip",
    "data_grid",
    "chart",
    "inspector_panel",
    "activity_feed",
    "control_stack",
    "diagnostics",
    "state_gallery",
    "text_block",
    "tab_group",
)

REGION_IDS: tuple[str, ...] = ("hero", "main", "side", "status")
TAB_ALLOWED_STATES: tuple[str, ...] = ("visible", "hold", "hidden", "disabled", "pending", "warning", "background")
PANEL_ALLOWED_STATES: tuple[str, ...] = ("visible", "hidden", "collapsed", "deferred", "disabled", "background", "hold")


@dataclass(frozen=True, slots=True)
class GlassFoundryRecipe:
    recipe_id: str
    title: str
    subtitle: str
    description: str
    payload: dict[str, Any]
    tags: tuple[str, ...] = ()
    category: str = "Recipe Foundry"
    status: str = "stable"
    icon_name: str | None = "sparkles"
    sort_order: int = 800
    best_for: str = ""
    use_when: str = ""


@dataclass(frozen=True, slots=True)
class GlassFoundryRegistrySnapshot:
    recipes: tuple[str, ...]
    beauty_profiles: tuple[str, ...]
    color_stories: tuple[str, ...]
    motion_profiles: tuple[str, ...]
    theme_ids: tuple[str, ...]
    preset_ids: tuple[str, ...]


_FOUNDRY_RECIPES: dict[str, GlassFoundryRecipe] = {{}}
_BUILTINS_REGISTERED = False


def _deep_merge(base: Any, override: Any) -> Any:
    if isinstance(base, Mapping) and isinstance(override, Mapping):
        merged = {{str(key): deepcopy(value) for key, value in base.items()}}
        for key, value in override.items():
            if key in merged:
                merged[str(key)] = _deep_merge(merged[str(key)], value)
            else:
                merged[str(key)] = deepcopy(value)
        return merged
    if isinstance(override, list):
        return [deepcopy(item) for item in override]
    return deepcopy(override)


def _dedupe_preserve(items: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        normalized = str(item or "").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return tuple(ordered)


def _default_recipe_payload() -> dict[str, Any]:
    return {{
        "meta": {{
            "id": "unnamed_recipe",
            "version": 1,
            "title": "Unnamed Recipe",
            "intent": "workspace",
            "audience": "default",
            "mood": "premium",
            "density": "comfortable",
            "platform": "desktop",
        }},
        "experience": {{
            "visual_language": "premium_workstation",
            "beauty_profile": "premium_focus",
            "color_story": "graphite_cyan",
            "motion_profile": "snappy_deluxe",
            "emphasis": {{
                "contrast": "medium",
                "depth": "medium",
                "glow": "subtle",
                "blur": "soft",
                "ornament": "restrained",
            }},
            "rhythm": {{
                "spacing_scale": 1.0,
                "corner_roundness": 0.9,
                "surface_layering": 0.8,
                "whitespace_balance": "balanced",
            }},
        }},
        "shell": {{
            "window": {{
                "frame": "frameless",
                "translucency": True,
                "shadow": "soft",
                "blur_strength": 0.20,
            }},
            "navigation": {{
                "model": "left_rail",
                "collapsible": True,
                "floating_search": True,
            }},
            "header": {{
                "visible": True,
                "style": "elevated",
                "height": "md",
            }},
            "status_bar": {{
                "visible": True,
                "diagnostics_slot": True,
            }},
        }},
        "regions": {{
            "hero": {{"visible": True, "role": "contextual_banner", "prominence": "medium"}},
            "main": {{"visible": True, "role": "primary_workspace", "layout": "stacked"}},
            "side": {{"visible": True, "role": "contextual_inspector", "width": "md", "deferred": True}},
            "status": {{"visible": True, "role": "runtime_feedback"}},
        }},
        "surfaces": [],
        "behavior": {{
            "preset": "",
            "layouts": {{
                "default": "inspect",
                "presets": {{
                    "focus": {{"main_side": [980, 220]}},
                    "inspect": {{"main_side": [760, 420]}},
                    "wallboard": {{"main_side": [1100, 180]}},
                }},
                "persistent": True,
            }},
            "visibility": {{
                "rules": [],
            }},
            "performance": {{
                "lazy_tabs": True,
                "deferred_panels": True,
                "chart_throttle_ms": 120,
            }},
        }},
        "data": {{
            "sources": [],
            "ui_states": {{
                "loading": {{"treatment": "shimmer_soft"}},
                "empty": {{"treatment": "illustration_message", "tone": "elegant"}},
                "error": {{"treatment": "inline_diagnostic", "recover_actions": ["retry", "inspect"]}},
            }},
        }},
        "quality": {{
            "beauty_checks": {{
                "no_inline_colors": True,
                "no_unstyled_widgets": True,
                "spacing_scale_enforced": True,
                "icon_family_enforced": True,
                "motion_profile_enforced": True,
            }},
            "render_checks": {{
                "theme_switch_test": True,
                "compact_mode_test": True,
                "empty_state_test": True,
                "error_state_test": True,
                "screenshot_baselines": True,
            }},
        }},
    }}


def get_recipe_schema() -> dict[str, Any]:
    return {{
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "forgeos.pyside6_glass.recipe_foundry.schema.json",
        "title": "PySide6 Glass Recipe Foundry Schema",
        "description": (
            "Declarative experience schema for premium workstation interfaces. "
            "The contract encodes visual language, rhythm, motion, surface composition, "
            "and runtime guardrails so that beauty remains compatible with reusable shell "
            "and runtime orchestration."
        ),
        "type": "object",
        "required": ["meta", "experience", "regions", "surfaces", "behavior", "quality"],
        "properties": {{
            "meta": {{
                "type": "object",
                "required": ["id", "title"],
                "properties": {{
                    "id": {{"type": "string"}},
                    "version": {{"type": "integer", "minimum": 1}},
                    "title": {{"type": "string"}},
                    "intent": {{"type": "string"}},
                    "audience": {{"type": "string"}},
                    "mood": {{"type": "string"}},
                    "density": {{"enum": ["compact", "comfortable", "spacious", "extended"]}},
                    "platform": {{"enum": ["desktop"]}},
                }},
            }},
            "experience": {{
                "type": "object",
                "required": ["beauty_profile", "color_story", "motion_profile"],
                "properties": {{
                    "visual_language": {{"type": "string"}},
                    "beauty_profile": {{"enum": sorted(BEAUTY_PROFILES)}},
                    "color_story": {{"enum": sorted(COLOR_STORIES)}},
                    "motion_profile": {{"enum": sorted(MOTION_PROFILES)}},
                }},
            }},
            "regions": {{
                "type": "object",
                "properties": {{region: {{"type": "object"}} for region in REGION_IDS}},
            }},
            "surfaces": {{
                "type": "array",
                "items": {{
                    "type": "object",
                    "required": ["id", "type", "region", "title"],
                    "properties": {{
                        "id": {{"type": "string"}},
                        "type": {{"enum": list(SURFACE_TYPES)}},
                        "region": {{"enum": list(REGION_IDS)}},
                        "title": {{"type": "string"}},
                        "subtitle": {{"type": "string"}},
                        "variant": {{"type": "string"}},
                        "icon_name": {{"type": "string"}},
                        "state": {{"type": "string"}},
                        "lazy": {{"type": "boolean"}},
                        "deferred": {{"type": "boolean"}},
                        "payload": {{"type": "object"}},
                        "tabs": {{"type": "array"}},
                        "visibility": {{"type": "object"}},
                    }},
                }},
            }},
            "behavior": {{
                "type": "object",
                "properties": {{
                    "preset": {{"type": "string"}},
                    "layouts": {{"type": "object"}},
                    "visibility": {{"type": "object"}},
                    "performance": {{"type": "object"}},
                }},
            }},
            "quality": {{
                "type": "object",
                "properties": {{
                    "beauty_checks": {{"type": "object"}},
                    "render_checks": {{"type": "object"}},
                }},
            }},
        }},
    }}


def list_beauty_profiles() -> tuple[str, ...]:
    return tuple(sorted(BEAUTY_PROFILES.keys()))


def list_color_stories() -> tuple[str, ...]:
    return tuple(sorted(COLOR_STORIES.keys()))


def list_motion_profiles() -> tuple[str, ...]:
    return tuple(sorted(MOTION_PROFILES.keys()))


def validate_foundry_recipe(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise TypeError("recipe payload must be a mapping")
    merged = _deep_merge(_default_recipe_payload(), dict(payload))
    meta = merged["meta"]
    experience = merged["experience"]
    surfaces = merged["surfaces"]

    meta["id"] = str(meta.get("id") or "").strip() or "unnamed_recipe"
    meta["title"] = str(meta.get("title") or "").strip() or meta["id"].replace("_", " ").title()
    merged["meta"]["version"] = int(meta.get("version") or 1)
    if experience["beauty_profile"] not in BEAUTY_PROFILES:
        raise ValueError(f"unknown beauty profile: {{experience['beauty_profile']}}")
    if experience["color_story"] not in COLOR_STORIES:
        raise ValueError(f"unknown color story: {{experience['color_story']}}")
    if experience["motion_profile"] not in MOTION_PROFILES:
        raise ValueError(f"unknown motion profile: {{experience['motion_profile']}}")

    seen_ids: set[str] = set()
    normalized_surfaces: list[dict[str, Any]] = []
    for index, surface in enumerate(surfaces):
        if not isinstance(surface, Mapping):
            raise TypeError(f"surface at index {{index}} must be a mapping")
        entry = _deep_merge(
            {{
                "id": f"surface_{{index + 1}}",
                "type": "text_block",
                "region": "main",
                "title": f"Surface {{index + 1}}",
                "subtitle": "",
                "variant": "default",
                "icon_name": "",
                "state": "visible",
                "lazy": False,
                "deferred": False,
                "payload": {{}},
                "tabs": [],
                "visibility": {{}},
            }},
            surface,
        )
        entry["id"] = str(entry["id"] or "").strip() or f"surface_{{index + 1}}"
        if entry["id"] in seen_ids:
            raise ValueError(f"duplicate surface id: {{entry['id']}}")
        seen_ids.add(entry["id"])
        if entry["type"] not in SURFACE_TYPES:
            raise ValueError(f"unknown surface type for {{entry['id']}}: {{entry['type']}}")
        if entry["region"] not in REGION_IDS:
            raise ValueError(f"unknown region for {{entry['id']}}: {{entry['region']}}")
        state = str(entry["state"] or "visible").strip().lower()
        allowed_states = TAB_ALLOWED_STATES if entry["type"] == "tab_group" else PANEL_ALLOWED_STATES
        if state not in allowed_states:
            entry["state"] = "visible"
        normalized_surfaces.append(entry)
    merged["surfaces"] = normalized_surfaces

    known_surface_ids = {{surface["id"] for surface in normalized_surfaces}}
    for surface in normalized_surfaces:
        if surface["type"] != "tab_group":
            continue
        tabs = []
        for tab_index, tab in enumerate(surface.get("tabs") or []):
            if not isinstance(tab, Mapping):
                raise TypeError(f"tab entry for surface {{surface['id']}} must be a mapping")
            content_ids = [str(item).strip() for item in tab.get("content_surface_ids") or [] if str(item).strip()]
            unknown = [item for item in content_ids if item not in known_surface_ids]
            if unknown:
                raise ValueError(
                    f"tab '{{tab.get('id') or tab_index}}' in surface '{{surface['id']}}' references unknown surfaces: {{unknown}}"
                )
            tabs.append(
                {{
                    "id": str(tab.get("id") or f"{{surface['id']}}_tab_{{tab_index + 1}}").strip(),
                    "title": str(tab.get("title") or f"Tab {{tab_index + 1}}").strip(),
                    "icon_name": str(tab.get("icon_name") or "").strip(),
                    "state": str(tab.get("state") or "visible").strip().lower() or "visible",
                    "lazy": bool(tab.get("lazy", surface.get("lazy", False))),
                    "content_surface_ids": content_ids,
                    "subtitle": str(tab.get("subtitle") or "").strip(),
                }}
            )
        surface["tabs"] = tabs

    return merged


def register_foundry_recipe(
    recipe_id: str,
    payload: Mapping[str, Any],
    *,
    description: str = "",
    tags: Sequence[str] = (),
    category: str = "Recipe Foundry",
    status: str = "stable",
    icon_name: str | None = "sparkles",
    sort_order: int = 800,
    best_for: str = "",
    use_when: str = "",
    override: bool = False,
) -> GlassFoundryRecipe:
    normalized_id = str(recipe_id or "").strip().lower()
    if not normalized_id:
        raise ValueError("recipe_id is required")
    if not override and normalized_id in _FOUNDRY_RECIPES:
        raise ValueError(f"recipe '{{normalized_id}}' already registered")
    normalized_payload = validate_foundry_recipe(payload)
    recipe = GlassFoundryRecipe(
        recipe_id=normalized_id,
        title=str(normalized_payload["meta"]["title"]),
        subtitle=str(normalized_payload["experience"]["visual_language"]).replace("_", " ").title(),
        description=str(description or normalized_payload["meta"].get("mood") or "Recipe foundry entry."),
        payload=normalized_payload,
        tags=_dedupe_preserve(tags),
        category=str(category or "Recipe Foundry"),
        status=str(status or "stable"),
        icon_name=str(icon_name) if icon_name else None,
        sort_order=int(sort_order),
        best_for=str(best_for or ""),
        use_when=str(use_when or ""),
    )
    _FOUNDRY_RECIPES[normalized_id] = recipe
    return recipe


def list_foundry_recipes() -> tuple[str, ...]:
    return tuple(sorted(_FOUNDRY_RECIPES.keys()))


def get_foundry_recipe(recipe_id: str) -> GlassFoundryRecipe:
    normalized = str(recipe_id or "").strip().lower()
    recipe = _FOUNDRY_RECIPES.get(normalized)
    if recipe is None:
        raise KeyError(f"recipe '{{normalized}}' is not registered")
    return recipe


def register_foundry_theme_pack(
    theme_id: str,
    palette: GlassPalette,
    *,
    parent_theme_id: str | None = None,
    description: str = "",
    override: bool = False,
) -> None:
    if str(theme_id or "").strip().lower() in set(list_theme_ids()) and not override:
        return
    register_theme(
        theme_id,
        palette,
        parent_theme_id=parent_theme_id,
        description=description,
        override=override,
    )


def _make_palette(
    *,
    shell_top: str,
    shell_bottom: str,
    accent: str,
    accent_soft: str,
    text_primary: str,
    text_muted: str,
    card_top: str,
    card_bottom: str,
    card_border: str,
    button_top: str,
    button_bottom: str,
    button_border: str,
    danger_top: str,
    danger_bottom: str,
    danger_border: str,
    warning_top: str,
    warning_bottom: str,
    warning_border: str,
    success_top: str,
    success_bottom: str,
    success_border: str,
) -> GlassPalette:
    return GlassPalette(
        shell_top=shell_top,
        shell_bottom=shell_bottom,
        shell_border=card_border,
        shell_border_hover=accent_soft,
        chrome_top=card_top,
        chrome_bottom=card_bottom,
        chrome_border=card_border,
        card_top=card_top,
        card_bottom=card_bottom,
        card_border=card_border,
        text_primary=text_primary,
        text_muted=text_muted,
        text_inverse="#081018",
        accent=accent,
        accent_soft=accent_soft,
        button_top=button_top,
        button_bottom=button_bottom,
        button_border=button_border,
        danger_top=danger_top,
        danger_bottom=danger_bottom,
        danger_border=danger_border,
        warning_top=warning_top,
        warning_bottom=warning_bottom,
        warning_border=warning_border,
        success_top=success_top,
        success_bottom=success_bottom,
        success_border=success_border,
        input_bg=shell_bottom,
        input_border=card_border,
        input_border_hover=accent_soft,
        progress_bg=shell_bottom,
        progress_chunk_top=accent,
        progress_chunk_bottom=accent,
        tab_bg=card_bottom,
        tab_active_bg=button_top,
        tab_hold_bg=card_top,
        tab_pending_bg=success_bottom,
        tab_warning_bg=warning_bottom,
        tab_border=card_border,
        tab_text=text_primary,
        tab_text_muted=text_muted,
        panel_form_border=card_border,
        panel_data_border=success_border,
        panel_metrics_border=warning_border,
        panel_detail_border=accent_soft,
        panel_summary_border=accent_soft,
        panel_aux_border=card_border,
    )


def _register_builtin_theme_packs() -> None:
    register_foundry_theme_pack(
        "graphite_cyan_foundry",
        _make_palette(
            shell_top="rgba(19, 25, 35, 0.95)",
            shell_bottom="rgba(9, 14, 22, 0.96)",
            accent="#7ce7ff",
            accent_soft="rgba(124, 231, 255, 0.26)",
            text_primary="#e7f5ff",
            text_muted="#aabfd0",
            card_top="rgba(53, 71, 92, 0.36)",
            card_bottom="rgba(30, 40, 56, 0.34)",
            card_border="rgba(147, 207, 235, 0.24)",
            button_top="rgba(84, 161, 208, 0.42)",
            button_bottom="rgba(54, 111, 147, 0.30)",
            button_border="rgba(142, 214, 250, 0.36)",
            danger_top="rgba(200, 118, 112, 0.18)",
            danger_bottom="rgba(154, 85, 79, 0.14)",
            danger_border="rgba(221, 163, 156, 0.28)",
            warning_top="rgba(210, 166, 100, 0.18)",
            warning_bottom="rgba(153, 111, 57, 0.14)",
            warning_border="rgba(230, 191, 133, 0.28)",
            success_top="rgba(97, 190, 154, 0.18)",
            success_bottom="rgba(60, 131, 106, 0.14)",
            success_border="rgba(137, 218, 187, 0.28)",
        ),
        description="Graphite/cyan premium foundry story.",
    )
    register_foundry_theme_pack(
        "obsidian_violet_foundry",
        _make_palette(
            shell_top="rgba(22, 19, 32, 0.95)",
            shell_bottom="rgba(10, 8, 18, 0.96)",
            accent="#c7a2ff",
            accent_soft="rgba(199, 162, 255, 0.25)",
            text_primary="#f2ebff",
            text_muted="#bdb0d5",
            card_top="rgba(70, 55, 96, 0.38)",
            card_bottom="rgba(39, 29, 58, 0.34)",
            card_border="rgba(179, 156, 225, 0.24)",
            button_top="rgba(117, 91, 179, 0.42)",
            button_bottom="rgba(82, 63, 125, 0.31)",
            button_border="rgba(199, 170, 255, 0.33)",
            danger_top="rgba(201, 122, 137, 0.18)",
            danger_bottom="rgba(144, 74, 91, 0.14)",
            danger_border="rgba(223, 162, 176, 0.27)",
            warning_top="rgba(213, 168, 110, 0.18)",
            warning_bottom="rgba(153, 112, 60, 0.14)",
            warning_border="rgba(235, 198, 144, 0.26)",
            success_top="rgba(118, 190, 160, 0.18)",
            success_bottom="rgba(78, 135, 111, 0.14)",
            success_border="rgba(149, 222, 192, 0.28)",
        ),
        description="Obsidian/violet cinematic foundry story.",
    )
    register_foundry_theme_pack(
        "frosted_emerald_foundry",
        _make_palette(
            shell_top="rgba(18, 29, 26, 0.95)",
            shell_bottom="rgba(7, 15, 14, 0.96)",
            accent="#79f2cb",
            accent_soft="rgba(121, 242, 203, 0.24)",
            text_primary="#e8fbf5",
            text_muted="#b1d5c9",
            card_top="rgba(45, 78, 71, 0.36)",
            card_bottom="rgba(26, 51, 47, 0.33)",
            card_border="rgba(136, 207, 185, 0.25)",
            button_top="rgba(72, 167, 145, 0.42)",
            button_bottom="rgba(45, 118, 102, 0.30)",
            button_border="rgba(128, 224, 197, 0.34)",
            danger_top="rgba(196, 121, 116, 0.18)",
            danger_bottom="rgba(143, 79, 76, 0.14)",
            danger_border="rgba(221, 160, 155, 0.28)",
            warning_top="rgba(210, 174, 110, 0.18)",
            warning_bottom="rgba(154, 119, 60, 0.14)",
            warning_border="rgba(235, 202, 144, 0.28)",
            success_top="rgba(93, 200, 162, 0.18)",
            success_bottom="rgba(56, 140, 112, 0.14)",
            success_border="rgba(127, 224, 188, 0.30)",
        ),
        description="Frosted emerald analytical foundry story.",
    )
    register_foundry_theme_pack(
        "ember_gold_foundry",
        _make_palette(
            shell_top="rgba(33, 24, 18, 0.95)",
            shell_bottom="rgba(18, 12, 8, 0.96)",
            accent="#ffd27f",
            accent_soft="rgba(255, 210, 127, 0.24)",
            text_primary="#fff3de",
            text_muted="#d8c3a1",
            card_top="rgba(85, 63, 40, 0.36)",
            card_bottom="rgba(51, 36, 22, 0.34)",
            card_border="rgba(226, 186, 120, 0.25)",
            button_top="rgba(181, 125, 48, 0.42)",
            button_bottom="rgba(122, 82, 28, 0.30)",
            button_border="rgba(255, 213, 138, 0.34)",
            danger_top="rgba(206, 117, 98, 0.18)",
            danger_bottom="rgba(151, 73, 60, 0.14)",
            danger_border="rgba(229, 160, 146, 0.28)",
            warning_top="rgba(219, 175, 91, 0.18)",
            warning_bottom="rgba(155, 112, 43, 0.14)",
            warning_border="rgba(242, 202, 122, 0.28)",
            success_top="rgba(114, 185, 139, 0.18)",
            success_bottom="rgba(68, 133, 96, 0.14)",
            success_border="rgba(150, 219, 177, 0.28)",
        ),
        description="Ember/gold executive foundry story.",
    )


def _register_builtin_presets() -> None:
    definitions = {{
        "foundry_premium_focus": GlassTemplateConfig(
            title="Foundry Premium Focus",
            subtitle="Balanced premium workstation preset for recipe-built interfaces.",
            eyebrow="FOUNDRY",
            theme=GlassThemeConfig(
                theme_id="graphite_cyan_foundry",
                density="comfortable",
                experience_mode="default",
                visual_scale=GlassVisualScaleConfig(
                    spacing_scale=0.98,
                    padding_scale=0.98,
                    icon_scale=1.0,
                    control_height_scale=1.0,
                    corner_radius_scale=0.95,
                    surface_opacity_scale=1.0,
                    blur_intensity_scale=1.05,
                    breathing_room_scale=1.0,
                ),
                typography=GlassTypographyConfig(scale="md", line_height_mode="regular"),
                animation=GlassAnimationConfig(level="normal", transition_ms=180, hover_ms=110, panel_toggle_ms=150, tab_switch_ms=140),
            ),
            regions=GlassRegionConfig(show_side=True, show_footer=False, show_status=True, main_side_sizes=(820, 380)),
            layout=GlassLayoutConfig(
                active_layout="inspect",
                named_layouts={{
                    "focus": {{"main_side": [980, 220]}},
                    "inspect": {{"main_side": [820, 380]}},
                    "wallboard": {{"main_side": [1080, 180]}},
                }},
            ),
        ),
        "foundry_cinematic_glass": GlassTemplateConfig(
            title="Foundry Cinematic Glass",
            subtitle="Lush glass preset for rich showcase and control-room recipes.",
            eyebrow="FOUNDRY",
            theme=GlassThemeConfig(
                theme_id="obsidian_violet_foundry",
                density="comfortable",
                experience_mode="default",
                visual_scale=GlassVisualScaleConfig(
                    spacing_scale=1.02,
                    padding_scale=1.02,
                    icon_scale=1.0,
                    control_height_scale=1.0,
                    corner_radius_scale=1.08,
                    surface_opacity_scale=1.0,
                    blur_intensity_scale=1.25,
                    breathing_room_scale=1.06,
                ),
                typography=GlassTypographyConfig(scale="md", line_height_mode="relaxed"),
                animation=GlassAnimationConfig(level="normal", transition_ms=240, hover_ms=140, panel_toggle_ms=190, tab_switch_ms=180),
            ),
            regions=GlassRegionConfig(show_side=True, show_footer=False, show_status=True, main_side_sizes=(860, 400)),
            layout=GlassLayoutConfig(
                active_layout="inspect",
                named_layouts={{
                    "focus": {{"main_side": [1040, 240]}},
                    "inspect": {{"main_side": [860, 400]}},
                    "wallboard": {{"main_side": [1120, 180]}},
                }},
            ),
        ),
        "foundry_precision_inspector": GlassTemplateConfig(
            title="Foundry Precision Inspector",
            subtitle="Dense, practical preset for inspector-heavy professional tools.",
            eyebrow="FOUNDRY",
            theme=GlassThemeConfig(
                theme_id="frosted_emerald_foundry",
                density="compact",
                experience_mode="operator",
                visual_scale=GlassVisualScaleConfig(
                    spacing_scale=0.90,
                    padding_scale=0.92,
                    icon_scale=0.96,
                    control_height_scale=0.94,
                    corner_radius_scale=0.80,
                    surface_opacity_scale=0.98,
                    blur_intensity_scale=0.85,
                    breathing_room_scale=0.88,
                    data_density_bias=0.35,
                ),
                typography=GlassTypographyConfig(scale="sm", line_height_mode="compact"),
                animation=GlassAnimationConfig(level="subtle", transition_ms=130, hover_ms=85, panel_toggle_ms=100, tab_switch_ms=100),
            ),
            regions=GlassRegionConfig(show_side=True, show_footer=False, show_status=True, main_side_sizes=(760, 420)),
            layout=GlassLayoutConfig(
                active_layout="inspect",
                named_layouts={{
                    "focus": {{"main_side": [920, 240]}},
                    "inspect": {{"main_side": [760, 420]}},
                    "wallboard": {{"main_side": [1020, 180]}},
                }},
            ),
        ),
        "foundry_command_wall": GlassTemplateConfig(
            title="Foundry Command Wall",
            subtitle="Overview-first preset for command center and executive wallboard recipes.",
            eyebrow="FOUNDRY",
            theme=GlassThemeConfig(
                theme_id="ember_gold_foundry",
                density="comfortable",
                experience_mode="presentation",
                visual_scale=GlassVisualScaleConfig(
                    spacing_scale=1.04,
                    padding_scale=1.04,
                    icon_scale=1.05,
                    control_height_scale=1.02,
                    corner_radius_scale=1.0,
                    surface_opacity_scale=1.0,
                    blur_intensity_scale=1.00,
                    breathing_room_scale=1.08,
                ),
                typography=GlassTypographyConfig(scale="lg", line_height_mode="regular"),
                animation=GlassAnimationConfig(level="subtle", transition_ms=170, hover_ms=90, panel_toggle_ms=120, tab_switch_ms=120),
            ),
            regions=GlassRegionConfig(show_side=True, show_footer=False, show_status=True, main_side_sizes=(980, 300)),
            layout=GlassLayoutConfig(
                active_layout="wallboard",
                named_layouts={{
                    "focus": {{"main_side": [1150, 180]}},
                    "inspect": {{"main_side": [920, 340]}},
                    "wallboard": {{"main_side": [1060, 240]}},
                }},
            ),
        ),
    }}
    existing = set(list_template_presets())
    for preset_id, config in definitions.items():
        if preset_id in existing:
            continue
        register_template_preset(preset_id, config=config, base_preset="neutral", override=False)


def _motion_profile_config(profile_id: str) -> GlassAnimationConfig:
    token = MOTION_PROFILES.get(profile_id, MOTION_PROFILES["snappy_deluxe"])
    return GlassAnimationConfig(
        level=token["animation_level"],
        transition_ms=token["transition_ms"],
        hover_ms=token["hover_ms"],
        panel_toggle_ms=token["panel_toggle_ms"],
        tab_switch_ms=token["tab_switch_ms"],
    )


def _profile_density(profile_id: str) -> str:
    return str(BEAUTY_PROFILES.get(profile_id, BEAUTY_PROFILES["premium_focus"]).get("default_density") or "comfortable")


def _profile_preset(profile_id: str) -> str:
    return str(BEAUTY_PROFILES.get(profile_id, BEAUTY_PROFILES["premium_focus"]).get("default_preset") or "dashboard")


def _color_story_theme_id(color_story: str) -> str:
    return str(COLOR_STORIES.get(color_story, COLOR_STORIES["graphite_cyan"]).get("theme_id") or "graphite_cyan_foundry")


def _intent_icon(intent: str) -> str:
    mapping = {{
        "operations": "activity",
        "analytics": "bar-chart-3",
        "inspector": "search",
        "command": "cpu",
        "workspace": "layers",
    }}
    return mapping.get(str(intent or "").strip().lower(), "sparkles")


def _surface_icon(surface_type: str, fallback: str = "sparkles") -> str:
    mapping = {{
        "hero_banner": "sparkles",
        "metric_strip": "gauge",
        "data_grid": "table",
        "chart": "line-chart",
        "inspector_panel": "search",
        "activity_feed": "list",
        "control_stack": "sliders-horizontal",
        "diagnostics": "cpu",
        "state_gallery": "shapes",
        "text_block": "file-text",
        "tab_group": "layers",
    }}
    return mapping.get(surface_type, fallback)


def _rich_text_block(text: str, parent: QWidget | None = None) -> QTextEdit:
    editor = QTextEdit(parent)
    editor.setReadOnly(True)
    editor.setPlainText(str(text or ""))
    return editor


def _build_metric_strip(surface: Mapping[str, Any], parent: QWidget | None = None) -> QWidget:
    host = QWidget(parent)
    layout = QVBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)
    metrics = list(surface.get("payload", {{}}).get("metrics") or [])
    if not metrics:
        metrics = [
            {{"label": "Throughput", "value": "214/min", "trend": "up"}},
            {{"label": "Errors", "value": "0.4%", "trend": "down"}},
            {{"label": "Queue", "value": "31", "trend": "flat"}},
        ]
    for metric in metrics:
        layout.addWidget(
            StatPill(
                str(metric.get("label") or "Metric"),
                str(metric.get("value") or "--"),
                trend=str(metric.get("trend") or "flat"),
                parent=host,
            )
        )
    return host


def _build_chart_surface(surface: Mapping[str, Any], parent: QWidget | None = None) -> QWidget:
    shell = DashboardWidgetShell(
        str(surface.get("title") or "Chart"),
        subtitle=str(surface.get("subtitle") or "Time-series preview surface"),
        parent=parent,
    )
    chart_kind = str(surface.get("payload", {{}}).get("kind") or "line")
    try:
        import pyqtgraph as pg  # type: ignore

        plot = pg.PlotWidget(shell)
        plot.showGrid(x=True, y=True, alpha=0.18)
        plot.setMouseEnabled(x=False, y=False)
        points = [4, 7, 6, 12, 11, 16, 15, 18, 17]
        x_axis = list(range(len(points)))
        plot.plot(x_axis, points, pen=pg.mkPen(width=2))
        shell.content.addWidget(plot, 1)
        legend = MiniLegend(shell)
        legend.add_status(f"{{chart_kind.title()}} series", "info")
        legend.add_status("Interactive", "success")
        shell.content.addWidget(legend)
    except Exception:
        shell.content.addWidget(_rich_text_block("pyqtgraph unavailable in this environment. Chart preview fallback.", shell))
    return shell


def _build_table_surface(surface: Mapping[str, Any], parent: QWidget | None = None) -> QWidget:
    shell = DashboardWidgetShell(
        str(surface.get("title") or "Data Grid"),
        subtitle=str(surface.get("subtitle") or "Structured rows preview"),
        parent=parent,
    )
    search = SearchCommandBar(
        placeholder=str(surface.get("payload", {{}}).get("search_placeholder") or "Filter rows, entities or columns..."),
        parent=shell,
    )
    shell.content.addWidget(search)

    rows = list(surface.get("payload", {{}}).get("rows") or [])
    columns = list(surface.get("payload", {{}}).get("columns") or [])
    if not columns:
        columns = ["Name", "State", "Owner", "Latency"]
    if not rows:
        rows = [
            {{"Name": "alpha", "State": "healthy", "Owner": "agent.ops", "Latency": "12 ms"}},
            {{"Name": "bravo", "State": "warning", "Owner": "agent.qa", "Latency": "39 ms"}},
            {{"Name": "charlie", "State": "pending", "Owner": "agent.sync", "Latency": "21 ms"}},
        ]

    table = QTableWidget(len(rows), len(columns), shell)
    table.setHorizontalHeaderLabels([str(column) for column in columns])
    table.verticalHeader().setVisible(False)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QTableWidget.SingleSelection)
    header = table.horizontalHeader()
    if header is not None:
        header.setStretchLastSection(True)
        for index in range(max(0, len(columns) - 1)):
            header.setSectionResizeMode(index, QHeaderView.Stretch)
    for row_index, row in enumerate(rows):
        for column_index, column_name in enumerate(columns):
            item = QTableWidgetItem(str(row.get(column_name, "")))
            table.setItem(row_index, column_index, item)
    shell.content.addWidget(table, 1)
    return shell


def _build_inspector_surface(surface: Mapping[str, Any], parent: QWidget | None = None) -> QWidget:
    panel = ParameterPanel(str(surface.get("title") or "Inspector"), parent=parent)
    fields = list(surface.get("payload", {{}}).get("fields") or [])
    if not fields:
        fields = [
            {{"type": "text", "label": "Entity ID", "placeholder": "entity-001"}},
            {{"type": "text", "label": "Owner", "placeholder": "agent.ops"}},
            {{"type": "toggle", "label": "Trace Enabled", "checked": True}},
            {{"type": "slider", "label": "Refresh (s)", "minimum": 1, "maximum": 60, "value": 8}},
        ]
    for field_spec in fields:
        kind = str(field_spec.get("type") or "text").strip().lower()
        label = str(field_spec.get("label") or "Field")
        if kind == "toggle":
            panel.add_toggle(label, checked=bool(field_spec.get("checked", False)))
            continue
        if kind == "slider":
            panel.add_slider(
                label,
                minimum=int(field_spec.get("minimum", 0)),
                maximum=int(field_spec.get("maximum", 100)),
                value=int(field_spec.get("value", 0)),
            )
            continue
        panel.add_text_field(label, placeholder=str(field_spec.get("placeholder") or ""))
    return panel


def _build_activity_feed(surface: Mapping[str, Any], parent: QWidget | None = None) -> QWidget:
    shell = DashboardWidgetShell(
        str(surface.get("title") or "Activity Feed"),
        subtitle=str(surface.get("subtitle") or "Recent events and operator-visible milestones"),
        parent=parent,
    )
    feed = QListWidget(shell)
    entries = list(surface.get("payload", {{}}).get("entries") or [])
    if not entries:
        entries = [
            "Queue refreshed · 12:43:18",
            "Latency spike detected on edge-4",
            "Operator switched layout to inspect",
            "Diagnostics snapshot captured",
        ]
    for entry in entries:
        QListWidgetItem(str(entry), feed)
    shell.content.addWidget(feed, 1)
    return shell


def _build_control_stack(surface: Mapping[str, Any], parent: QWidget | None = None) -> QWidget:
    host = QWidget(parent)
    layout = QVBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)

    toolbar = CompactToolbar(str(surface.get("title") or "Quick Actions"), parent=host)
    actions = list(surface.get("payload", {{}}).get("actions") or [])
    if not actions:
        actions = [
            {{"label": "Refresh", "icon_name": "refresh-cw", "variant": "secondary"}},
            {{"label": "Focus", "icon_name": "target", "variant": "ghost"}},
            {{"label": "Export", "icon_name": "download", "variant": "primary"}},
        ]
    for action in actions:
        toolbar.add_action(
            str(action.get("label") or "Action"),
            icon_name=str(action.get("icon_name") or "sparkles"),
            variant=str(action.get("variant") or "secondary"),
        )
    layout.addWidget(toolbar)

    card = ControlCard(
        str(surface.get("payload", {{}}).get("card_title") or "Filters"),
        subtitle=str(surface.get("payload", {{}}).get("card_subtitle") or "Refine the visible working set"),
        parent=host,
    )
    chips = FilterChipBar(card)
    for index, chip in enumerate(surface.get("payload", {{}}).get("chips") or ["All", "Healthy", "Warning", "Critical"]):
        chips.add_chip(str(chip).lower(), str(chip), checked=index == 0)
    card.content.addWidget(chips)
    card.content.addWidget(TogglePill("Auto Refresh", "Paused", checked=True, parent=card))
    layout.addWidget(card)

    section = CollapsibleSection(
        str(surface.get("payload", {{}}).get("advanced_title") or "Advanced Controls"),
        subtitle="Dense controls that stay contained instead of floating above the shell.",
        collapsed=True,
        parent=host,
    )
    section.body_layout.addWidget(StatusPill("Debug overlays disabled by default", kind="warning", parent=section))
    section.body_layout.addWidget(StatusPill("Resize protected by named layouts", kind="success", parent=section))
    layout.addWidget(section)
    return host


def _build_diagnostics_surface(surface: Mapping[str, Any], recipe_payload: Mapping[str, Any], parent: QWidget | None = None) -> QWidget:
    shell = DashboardWidgetShell(
        str(surface.get("title") or "Diagnostics"),
        subtitle=str(surface.get("subtitle") or "Recipe, motion and runtime diagnostics"),
        parent=parent,
    )
    legend = MiniLegend(shell)
    legend.add_status("Layer-safe slots", "success")
    legend.add_status("Deferred side panels", "success")
    legend.add_status("Named layouts", "info")
    shell.content.addWidget(legend)

    snapshot = {{
        "recipe_id": recipe_payload["meta"]["id"],
        "beauty_profile": recipe_payload["experience"]["beauty_profile"],
        "color_story": recipe_payload["experience"]["color_story"],
        "motion_profile": recipe_payload["experience"]["motion_profile"],
        "surfaces": [item["id"] for item in recipe_payload.get("surfaces", [])],
        "layouts": recipe_payload.get("behavior", {{}}).get("layouts", {{}}),
    }}
    shell.content.addWidget(_rich_text_block(json.dumps(snapshot, indent=2, ensure_ascii=True), shell), 1)
    return shell


def _build_state_gallery(surface: Mapping[str, Any], parent: QWidget | None = None) -> QWidget:
    host = QWidget(parent)
    layout = QVBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    layout.addWidget(LoadingStateCard("Loading premium surface", progress=68, parent=host))
    layout.addWidget(EmptyStateCard("No matching rows", "Try widening filters or changing scope.", parent=host))
    layout.addWidget(ErrorStateCard("Partial outage", "A downstream provider returned an error envelope.", parent=host))
    return host


def _build_text_surface(surface: Mapping[str, Any], parent: QWidget | None = None) -> QWidget:
    return _rich_text_block(str(surface.get("payload", {{}}).get("text") or surface.get("subtitle") or surface.get("title")), parent)


def _build_hero_surface(surface: Mapping[str, Any], recipe_payload: Mapping[str, Any], parent: QWidget | None = None) -> QWidget:
    eyebrow = str(recipe_payload.get("meta", {{}}).get("intent") or "RECIPE").upper()
    hero = HeroPanel(
        str(surface.get("title") or recipe_payload["meta"]["title"]),
        subtitle=str(surface.get("subtitle") or recipe_payload["experience"]["visual_language"].replace("_", " ").title()),
        eyebrow=eyebrow,
        parent=parent,
    )
    summary = QWidget(hero)
    row = QHBoxLayout(summary)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(8)
    metrics = list(surface.get("payload", {{}}).get("summary_metrics") or [])
    if not metrics:
        metrics = [
            {{"label": "Beauty", "value": recipe_payload["experience"]["beauty_profile"]}},
            {{"label": "Color", "value": recipe_payload["experience"]["color_story"]}},
            {{"label": "Motion", "value": recipe_payload["experience"]["motion_profile"]}},
        ]
    for metric in metrics:
        row.addWidget(
            StatPill(
                str(metric.get("label") or "Metric"),
                str(metric.get("value") or "--"),
                trend=str(metric.get("trend") or "flat"),
                parent=summary,
            )
        )
    hero.content.addWidget(summary)
    return hero


def _build_surface_widget(surface: Mapping[str, Any], recipe_payload: Mapping[str, Any], parent: QWidget | None = None) -> QWidget:
    surface_type = str(surface.get("type") or "text_block")
    if surface_type == "hero_banner":
        return _build_hero_surface(surface, recipe_payload, parent)
    if surface_type == "metric_strip":
        return _build_metric_strip(surface, parent)
    if surface_type == "data_grid":
        return _build_table_surface(surface, parent)
    if surface_type == "chart":
        return _build_chart_surface(surface, parent)
    if surface_type == "inspector_panel":
        return _build_inspector_surface(surface, parent)
    if surface_type == "activity_feed":
        return _build_activity_feed(surface, parent)
    if surface_type == "control_stack":
        return _build_control_stack(surface, parent)
    if surface_type == "diagnostics":
        return _build_diagnostics_surface(surface, recipe_payload, parent)
    if surface_type == "state_gallery":
        return _build_state_gallery(surface, parent)
    return _build_text_surface(surface, parent)


def _attach_toolbar(panel: QFrame, surface: Mapping[str, Any]) -> None:
    toolbar = CompactToolbar(str(surface.get("title") or "Actions"), parent=panel)
    toolbar.add_action("Focus", icon_name="target", variant="ghost")
    toolbar.add_action("Inspect", icon_name="search", variant="secondary")
    toolbar.add_action("Export", icon_name="download", variant="primary")
    panel.toolbar_layout().addWidget(toolbar)


def _apply_surface_state(template: GlassPanelTemplate, runtime: GlassWorkspaceRuntime, surface: Mapping[str, Any]) -> None:
    visibility = dict(surface.get("visibility") or {{}})
    if not visibility:
        return
    rule = GlassVisibilityRule(
        target_kind=str(visibility.get("target_kind") or ("tab" if surface["type"] == "tab_group" else "panel")),
        target_id=str(visibility.get("target_id") or surface["id"]),
        visible_state=str(visibility.get("visible_state") or "visible"),
        required_capabilities=tuple(str(item) for item in visibility.get("required_capabilities") or ()),
        allowed_roles=tuple(str(item) for item in visibility.get("allowed_roles") or ()),
        allowed_modes=tuple(str(item) for item in visibility.get("allowed_modes") or ()),
        required_flag=str(visibility.get("required_flag")) if visibility.get("required_flag") is not None else None,
        required_flag_value=visibility.get("required_flag_value", True),
    )
    runtime.visibility_policy.register(rule)


def _mount_standard_surface(
    template: GlassPanelTemplate,
    runtime: GlassWorkspaceRuntime,
    surface: Mapping[str, Any],
    recipe_payload: Mapping[str, Any],
) -> None:
    region = str(surface.get("region") or "main")
    target_slot = "status" if region == "status" else ("side" if region == "side" else "main")
    deferred = bool(surface.get("deferred")) and target_slot == "side"

    def _factory() -> QWidget:
        return _build_surface_widget(surface, recipe_payload, template)

    panel = template.create_panel(
        panel_id=str(surface["id"]),
        title=str(surface.get("title") or surface["id"]),
        target_slot=target_slot,
        role=str(recipe_payload.get("regions", {{}}).get(region, {{}}).get("role") or region),
        subtitle=str(surface.get("subtitle") or ""),
        state="deferred" if deferred else str(surface.get("state") or "visible"),
        icon_name=str(surface.get("icon_name") or _surface_icon(str(surface.get("type") or ""))),
        deferred_factory=_factory if deferred else None,
        toolbar_enabled=True,
        footer_enabled=False,
    )
    if not deferred:
        panel.content_layout.addWidget(_factory(), 1)
    _attach_toolbar(panel, surface)
    _apply_surface_state(template, runtime, surface)


def _mount_tab_group(
    template: GlassPanelTemplate,
    runtime: GlassWorkspaceRuntime,
    surface: Mapping[str, Any],
    recipe_payload: Mapping[str, Any],
    surface_index: Mapping[str, Mapping[str, Any]],
) -> None:
    tab_group_id = str(surface["id"])
    tabs = surface.get("tabs") or []
    if template.workspace_tabs is None:
        for tab in tabs:
            host = QWidget(template)
            host_layout = QVBoxLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(8)
            for child_surface_id in tab.get("content_surface_ids") or []:
                child_surface = surface_index.get(str(child_surface_id))
                if child_surface is None:
                    continue
                widget = _build_surface_widget(child_surface, recipe_payload, host)
                host_layout.addWidget(widget)
            template.slots.main_slot.addWidget(host)
        return

    for tab in tabs:
        def _tab_factory(tab_spec: Mapping[str, Any] = tab) -> QWidget:
            host = QWidget(template)
            host_layout = QVBoxLayout(host)
            host_layout.setContentsMargins(0, 0, 0, 0)
            host_layout.setSpacing(8)
            for child_surface_id in tab_spec.get("content_surface_ids") or []:
                child_surface = surface_index.get(str(child_surface_id))
                if child_surface is None:
                    continue
                widget = _build_surface_widget(child_surface, recipe_payload, host)
                host_layout.addWidget(widget)
            return host

        widget = None if bool(tab.get("lazy")) else _tab_factory()
        template.add_workspace_tab(
            GlassWorkspaceTabSpec(
                tab_id=str(tab.get("id") or f"{{tab_group_id}}_{{len(tabs)}}"),
                title=str(tab.get("title") or "Tab"),
                subtitle=str(tab.get("subtitle") or ""),
                icon_name=str(tab.get("icon_name") or "layers"),
                state=str(tab.get("state") or "visible"),
                lazy_factory=_tab_factory if bool(tab.get("lazy")) else None,
            ),
            widget=widget,
            make_current=False,
        )
    _apply_surface_state(template, runtime, surface)


def _build_foundry_runtime(template: GlassPanelTemplate, recipe_payload: Mapping[str, Any], preset: str) -> GlassWorkspaceRuntime:
    runtime = GlassWorkspaceRuntime(template, preset=preset)
    layouts = dict(recipe_payload.get("behavior", {{}}).get("layouts", {{}}).get("presets") or {{}})
    for name, payload in layouts.items():
        runtime.register_layout(str(name), dict(payload))
    runtime.apply_resolved_config()
    runtime.bind_default_shortcuts(template)
    return runtime


def build_foundry_preview(recipe: str | Mapping[str, Any], parent: QWidget | None = None) -> GlassPanelTemplate:
    register_builtin_foundry()
    recipe_payload = get_foundry_recipe(recipe).payload if isinstance(recipe, str) else validate_foundry_recipe(recipe)
    beauty_profile = str(recipe_payload["experience"]["beauty_profile"])
    color_story = str(recipe_payload["experience"]["color_story"])
    motion_profile = str(recipe_payload["experience"]["motion_profile"])
    preset = str(recipe_payload.get("behavior", {{}}).get("preset") or _profile_preset(beauty_profile))
    theme_id = _color_story_theme_id(color_story)
    density = str(recipe_payload["meta"].get("density") or _profile_density(beauty_profile))

    base_config = get_template_preset(preset)
    foundry_config = GlassTemplateConfig(
        title=str(recipe_payload["meta"]["title"]),
        subtitle=str(recipe_payload["experience"]["visual_language"]).replace("_", " ").title(),
        eyebrow=str(recipe_payload["meta"].get("intent") or "FOUNDRY").upper(),
        theme=GlassThemeConfig(
            theme_id=theme_id,
            density=density,
            experience_mode=base_config.theme.experience_mode,
            visual_scale=base_config.theme.visual_scale,
            typography=base_config.theme.typography,
            animation=_motion_profile_config(motion_profile),
        ),
        regions=base_config.regions,
        tabs=base_config.tabs,
        layout=base_config.layout,
        actions=base_config.actions,
        interaction=base_config.interaction,
        accessibility=base_config.accessibility,
        persistence=base_config.persistence,
        apply_stylesheet=base_config.apply_stylesheet,
        with_chrome=base_config.with_chrome,
        debug_mode=base_config.debug_mode,
    )

    template = GlassPanelTemplate(
        parent,
        config=foundry_config,
        title=str(recipe_payload["meta"]["title"]),
        subtitle=str(recipe_payload["experience"]["visual_language"]).replace("_", " ").title(),
        eyebrow=str(recipe_payload["meta"].get("intent") or "FOUNDRY").upper(),
        include_default_actions=False,
        show_status=bool(recipe_payload.get("regions", {{}}).get("status", {{}}).get("visible", True)),
        show_footer=False,
        theme_id=theme_id,
        density=density,
    )

    runtime = _build_foundry_runtime(template, recipe_payload, preset)
    surface_index = {{surface["id"]: surface for surface in recipe_payload.get("surfaces", [])}}

    template.clear_slot("hero")
    template.clear_slot("main")
    template.clear_slot("side")
    template.clear_slot("status")

    for surface in recipe_payload.get("surfaces", []):
        if surface["type"] == "tab_group":
            continue
        if str(surface.get("region") or "") == "hero":
            template.slots.hero_slot.addWidget(_build_surface_widget(surface, recipe_payload, template))
            continue
        _mount_standard_surface(template, runtime, surface, recipe_payload)

    for surface in recipe_payload.get("surfaces", []):
        if surface["type"] == "tab_group":
            _mount_tab_group(template, runtime, surface, recipe_payload, surface_index)

    default_layout = str(recipe_payload.get("behavior", {{}}).get("layouts", {{}}).get("default") or "")
    if default_layout:
        runtime.apply_layout(default_layout, tolerate_missing=True)

    flags = {{"debug_panel_on": True, "compact_density": density == "compact", "persist_workspace": True}}
    context = GlassRuntimeContext(role="default", mode=str(recipe_payload["meta"].get("intent") or "default"), flags=flags)
    runtime.apply_visibility_context(context)

    status_line = (
        f"Recipe '{{recipe_payload['meta']['id']}}' ready · "
        f"{{beauty_profile}} · {{color_story}} · {{motion_profile}}"
    )
    template.set_status_text(status_line)
    template._foundry_runtime = runtime  # type: ignore[attr-defined]
    return template


def build_foundry_runtime(recipe: str | Mapping[str, Any], parent: QWidget | None = None) -> tuple[GlassPanelTemplate, GlassWorkspaceRuntime]:
    template = build_foundry_preview(recipe, parent=parent)
    runtime = getattr(template, "_foundry_runtime", None)
    if runtime is None:
        raise RuntimeError("foundry runtime was not attached to preview")
    return template, runtime


def _builtin_recipe_definitions() -> list[dict[str, Any]]:
    return [
        {{
            "recipe_id": "recipe.ops_console_premium",
            "description": "Operations console with resilient table+chart+inspector composition.",
            "tags": ("recipe", "operations", "console", "premium"),
            "icon_name": "activity",
            "sort_order": 810,
            "best_for": "High-signal operator desks that need metrics, rows and safe side inspection.",
            "use_when": "you need a gorgeous operational console without hand-tuning resize behavior.",
            "payload": {{
                "meta": {{
                    "id": "ops_console_premium",
                    "title": "Operations Console Premium",
                    "intent": "operations",
                    "audience": "operator",
                    "mood": "focused",
                    "density": "compact",
                }},
                "experience": {{
                    "visual_language": "industrial_lux_console",
                    "beauty_profile": "industrial_precision",
                    "color_story": "graphite_cyan",
                    "motion_profile": "subtle",
                }},
                "behavior": {{
                    "preset": "foundry_precision_inspector",
                    "layouts": {{
                        "default": "inspect",
                        "presets": {{
                            "focus": {{"main_side": [980, 220]}},
                            "inspect": {{"main_side": [760, 420]}},
                            "wallboard": {{"main_side": [1080, 180]}},
                        }},
                    }},
                }},
                "surfaces": [
                    {{
                        "id": "ops_hero",
                        "type": "hero_banner",
                        "region": "hero",
                        "title": "Ops Command Surface",
                        "subtitle": "Dense workstation shell with named layouts and side-detail discipline.",
                        "payload": {{
                            "summary_metrics": [
                                {{"label": "Mode", "value": "Operator"}},
                                {{"label": "Layouts", "value": "Focus / Inspect / Wallboard"}},
                                {{"label": "Guarantee", "value": "No manual resize spaghetti"}},
                            ]
                        }},
                    }},
                    {{
                        "id": "ops_metrics",
                        "type": "metric_strip",
                        "region": "main",
                        "title": "KPI Pulse",
                        "subtitle": "Compact signals for queue, throughput and failure rate",
                        "payload": {{
                            "metrics": [
                                {{"label": "Throughput", "value": "248/min", "trend": "up"}},
                                {{"label": "Failures", "value": "0.27%", "trend": "down"}},
                                {{"label": "Queue", "value": "29", "trend": "flat"}},
                            ]
                        }},
                    }},
                    {{
                        "id": "ops_table",
                        "type": "data_grid",
                        "region": "main",
                        "title": "Work Queue",
                        "subtitle": "Primary operator surface with stable row rhythm",
                    }},
                    {{
                        "id": "ops_trend",
                        "type": "chart",
                        "region": "main",
                        "title": "Latency Trend",
                        "subtitle": "Time-series envelope for current workload",
                        "payload": {{"kind": "line"}},
                    }},
                    {{
                        "id": "ops_controls",
                        "type": "control_stack",
                        "region": "side",
                        "title": "Quick Controls",
                        "subtitle": "Contained controls, no floating overlay chaos",
                        "deferred": True,
                    }},
                    {{
                        "id": "ops_inspector",
                        "type": "inspector_panel",
                        "region": "side",
                        "title": "Record Inspector",
                        "subtitle": "Deferred side detail",
                        "deferred": True,
                    }},
                    {{
                        "id": "ops_diagnostics",
                        "type": "diagnostics",
                        "region": "status",
                        "title": "Guardrails",
                        "subtitle": "Layout, motion and debug snapshot",
                    }},
                ],
            }},
        }},
        {{
            "recipe_id": "recipe.analytics_cinematic",
            "description": "Cinematic analytics workspace with tabs, charts and presentable hero rhythm.",
            "tags": ("recipe", "analytics", "dashboard", "cinematic"),
            "icon_name": "bar-chart-3",
            "sort_order": 820,
            "best_for": "Analytics rooms that need more wow without losing workstation bones.",
            "use_when": "you want tabs, charts, summary rhythm and tasteful glass depth.",
            "payload": {{
                "meta": {{
                    "id": "analytics_cinematic",
                    "title": "Analytics Cinematic Board",
                    "intent": "analytics",
                    "audience": "analyst",
                    "mood": "cinematic",
                    "density": "comfortable",
                }},
                "experience": {{
                    "visual_language": "cinematic_signal_board",
                    "beauty_profile": "cinematic_glass",
                    "color_story": "obsidian_violet",
                    "motion_profile": "expressive_glass",
                }},
                "behavior": {{
                    "preset": "foundry_cinematic_glass",
                    "layouts": {{
                        "default": "wallboard",
                        "presets": {{
                            "focus": {{"main_side": [1020, 220]}},
                            "inspect": {{"main_side": [820, 420]}},
                            "wallboard": {{"main_side": [1100, 180]}},
                        }},
                    }},
                }},
                "surfaces": [
                    {{
                        "id": "analytics_hero",
                        "type": "hero_banner",
                        "region": "hero",
                        "title": "Analytics Signal Board",
                        "subtitle": "Presentation-grade command surface with elegant depth and strict shell discipline.",
                    }},
                    {{
                        "id": "analytics_tabs",
                        "type": "tab_group",
                        "region": "main",
                        "title": "Analytics Views",
                        "tabs": [
                            {{
                                "id": "overview",
                                "title": "Overview",
                                "icon_name": "layout-dashboard",
                                "content_surface_ids": ["analytics_metrics", "analytics_chart", "analytics_feed"],
                            }},
                            {{
                                "id": "details",
                                "title": "Details",
                                "icon_name": "table",
                                "lazy": True,
                                "content_surface_ids": ["analytics_table", "analytics_states"],
                            }},
                            {{
                                "id": "diagnostics",
                                "title": "Diagnostics",
                                "icon_name": "cpu",
                                "lazy": True,
                                "content_surface_ids": ["analytics_diag"],
                            }},
                        ],
                    }},
                    {{
                        "id": "analytics_metrics",
                        "type": "metric_strip",
                        "region": "main",
                        "title": "North Star Metrics",
                    }},
                    {{
                        "id": "analytics_chart",
                        "type": "chart",
                        "region": "main",
                        "title": "Signal Wave",
                        "subtitle": "Live metric pulse preview",
                        "payload": {{"kind": "line_area"}},
                    }},
                    {{
                        "id": "analytics_feed",
                        "type": "activity_feed",
                        "region": "main",
                        "title": "Event Stream",
                    }},
                    {{
                        "id": "analytics_table",
                        "type": "data_grid",
                        "region": "main",
                        "title": "Dimensional Breakdown",
                    }},
                    {{
                        "id": "analytics_states",
                        "type": "state_gallery",
                        "region": "main",
                        "title": "State Gallery",
                    }},
                    {{
                        "id": "analytics_diag",
                        "type": "diagnostics",
                        "region": "main",
                        "title": "Recipe Snapshot",
                    }},
                    {{
                        "id": "analytics_side",
                        "type": "control_stack",
                        "region": "side",
                        "title": "Filters + Actions",
                        "deferred": True,
                    }},
                ],
            }},
        }},
        {{
            "recipe_id": "recipe.inspector_precision",
            "description": "Sharp inspector workspace for event, entity and payload investigation.",
            "tags": ("recipe", "inspector", "debug", "precision"),
            "icon_name": "search",
            "sort_order": 830,
            "best_for": "Main-list plus side-detail flows where cleanliness and predictability matter more than spectacle.",
            "use_when": "you are building an investigation or review tool and want zero layer nonsense.",
            "payload": {{
                "meta": {{
                    "id": "inspector_precision",
                    "title": "Precision Inspector Workspace",
                    "intent": "inspector",
                    "audience": "reviewer",
                    "mood": "technical",
                    "density": "compact",
                }},
                "experience": {{
                    "visual_language": "precision_inspection_lab",
                    "beauty_profile": "industrial_precision",
                    "color_story": "frosted_emerald",
                    "motion_profile": "subtle",
                }},
                "behavior": {{
                    "preset": "foundry_precision_inspector",
                }},
                "surfaces": [
                    {{
                        "id": "inspector_hero",
                        "type": "hero_banner",
                        "region": "hero",
                        "title": "Inspection Lab",
                        "subtitle": "A clean split-view recipe that resists collapse drama.",
                    }},
                    {{
                        "id": "inspector_table",
                        "type": "data_grid",
                        "region": "main",
                        "title": "Entity Stream",
                    }},
                    {{
                        "id": "inspector_feed",
                        "type": "activity_feed",
                        "region": "main",
                        "title": "Recent Timeline",
                    }},
                    {{
                        "id": "inspector_panel",
                        "type": "inspector_panel",
                        "region": "side",
                        "title": "Entity Details",
                        "deferred": True,
                    }},
                    {{
                        "id": "inspector_controls",
                        "type": "control_stack",
                        "region": "side",
                        "title": "Review Actions",
                        "deferred": True,
                    }},
                    {{
                        "id": "inspector_diag",
                        "type": "diagnostics",
                        "region": "status",
                        "title": "Quality Guardrails",
                    }},
                ],
            }},
        }},
        {{
            "recipe_id": "recipe.command_center_executive",
            "description": "Executive command center with editorial rhythm and overview-first surfaces.",
            "tags": ("recipe", "command", "executive", "wallboard"),
            "icon_name": "cpu",
            "sort_order": 840,
            "best_for": "Leadership or wallboard screens that still need to descend into actionable detail.",
            "use_when": "you want an expensive-looking command surface that still behaves like a sane workstation.",
            "payload": {{
                "meta": {{
                    "id": "command_center_executive",
                    "title": "Executive Command Center",
                    "intent": "command",
                    "audience": "leadership",
                    "mood": "editorial",
                    "density": "comfortable",
                }},
                "experience": {{
                    "visual_language": "executive_signal_room",
                    "beauty_profile": "executive_signal",
                    "color_story": "ember_gold",
                    "motion_profile": "subtle",
                }},
                "behavior": {{
                    "preset": "foundry_command_wall",
                    "layouts": {{
                        "default": "wallboard",
                        "presets": {{
                            "focus": {{"main_side": [1200, 160]}},
                            "inspect": {{"main_side": [930, 330]}},
                            "wallboard": {{"main_side": [1080, 220]}},
                        }},
                    }},
                }},
                "surfaces": [
                    {{
                        "id": "command_hero",
                        "type": "hero_banner",
                        "region": "hero",
                        "title": "Executive Signal Room",
                        "subtitle": "Overview-first recipe with enough gravity to feel premium, not gaudy.",
                    }},
                    {{
                        "id": "command_metrics",
                        "type": "metric_strip",
                        "region": "main",
                        "title": "Board Signals",
                    }},
                    {{
                        "id": "command_chart",
                        "type": "chart",
                        "region": "main",
                        "title": "Strategic Pulse",
                    }},
                    {{
                        "id": "command_feed",
                        "type": "activity_feed",
                        "region": "main",
                        "title": "Priority Stream",
                    }},
                    {{
                        "id": "command_side",
                        "type": "inspector_panel",
                        "region": "side",
                        "title": "Narrative Detail",
                        "deferred": True,
                    }},
                    {{
                        "id": "command_status",
                        "type": "diagnostics",
                        "region": "status",
                        "title": "Stability Notes",
                    }},
                ],
            }},
        }},
    ]


def register_builtin_foundry(*, force: bool = False) -> GlassFoundryRegistrySnapshot:
    global _BUILTINS_REGISTERED
    if _BUILTINS_REGISTERED and not force:
        return foundry_registry_snapshot()

    _register_builtin_theme_packs()
    _register_builtin_presets()

    for definition in _builtin_recipe_definitions():
        register_foundry_recipe(
            definition["recipe_id"],
            definition["payload"],
            description=definition["description"],
            tags=definition.get("tags", ()),
            icon_name=definition.get("icon_name"),
            sort_order=int(definition.get("sort_order", 800)),
            best_for=str(definition.get("best_for") or ""),
            use_when=str(definition.get("use_when") or ""),
            override=True,
        )

    _BUILTINS_REGISTERED = True
    return foundry_registry_snapshot()


def foundry_registry_snapshot() -> GlassFoundryRegistrySnapshot:
    return GlassFoundryRegistrySnapshot(
        recipes=list_foundry_recipes(),
        beauty_profiles=list_beauty_profiles(),
        color_stories=list_color_stories(),
        motion_profiles=list_motion_profiles(),
        theme_ids=tuple(sorted(list_theme_ids())),
        preset_ids=tuple(sorted(list_template_presets())),
    )


__all__ = [
    "RECIPE_SCHEMA_VERSION",
    "BEAUTY_PROFILES",
    "COLOR_STORIES",
    "MOTION_PROFILES",
    "GlassFoundryRecipe",
    "GlassFoundryRegistrySnapshot",
    "build_foundry_preview",
    "build_foundry_runtime",
    "foundry_registry_snapshot",
    "get_foundry_recipe",
    "get_recipe_schema",
    "list_beauty_profiles",
    "list_color_stories",
    "list_foundry_recipes",
    "list_motion_profiles",
    "register_builtin_foundry",
    "register_foundry_recipe",
    "register_foundry_theme_pack",
    "validate_foundry_recipe",
]
