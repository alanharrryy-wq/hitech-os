from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from typing import Any, Callable, Mapping

from .contracts import (
    DEFAULT_THEME_ID,
    SUPPORTED_ANIMATION_LEVELS,
    SUPPORTED_DENSITY,
    SUPPORTED_EXPERIENCE_MODES,
    SUPPORTED_TAB_DENSITY,
    SUPPORTED_TAB_ICON_MODES,
    SUPPORTED_TAB_PLACEMENT,
    SUPPORTED_TAB_VARIANTS,
    SUPPORTED_TYPOGRAPHY_SCALE,
)


def _choice(value: str | None, allowed: tuple[str, ...], default: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in allowed:
        return normalized
    return default


def _positive_int(value: int, default: int, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except Exception:
        return max(minimum, int(default))
    return max(minimum, parsed)


def _positive_float(value: float, default: float, minimum: float = 0.0) -> float:
    try:
        parsed = float(value)
    except Exception:
        return max(minimum, float(default))
    return max(minimum, parsed)


@dataclass(frozen=True, slots=True)
class GlassAnimationConfig:
    level: str = "standard"
    reduced_motion: bool = False
    transition_ms: int = 160
    hover_ms: int = 110
    panel_toggle_ms: int = 180
    tab_switch_ms: int = 130

    def normalized(self) -> GlassAnimationConfig:
        return replace(
            self,
            level=_choice(self.level, SUPPORTED_ANIMATION_LEVELS, "standard"),
            transition_ms=_positive_int(self.transition_ms, 160, minimum=0),
            hover_ms=_positive_int(self.hover_ms, 110, minimum=0),
            panel_toggle_ms=_positive_int(self.panel_toggle_ms, 180, minimum=0),
            tab_switch_ms=_positive_int(self.tab_switch_ms, 130, minimum=0),
        )


@dataclass(frozen=True, slots=True)
class GlassAccessibilityConfig:
    show_focus_ring: bool = True
    enforce_icon_accessible_name: bool = True
    enforce_tooltip_for_icon_only: bool = True
    high_contrast_mode: bool = False


@dataclass(frozen=True, slots=True)
class GlassInteractionConfig:
    keyboard_shortcuts_enabled: bool = True
    tab_shortcuts_enabled: bool = True
    panel_shortcuts_enabled: bool = True
    command_palette_enabled: bool = False
    layout_edit_mode_default: bool = False
    quick_switch_shortcut: str = "Ctrl+Tab"
    reverse_switch_shortcut: str = "Ctrl+Shift+Tab"


@dataclass(frozen=True, slots=True)
class GlassPersistenceConfig:
    enabled: bool = True
    autosave: bool = False
    storage_path: str = "tools/_local/tmp/glass_workspace_state.json"
    save_tab_order: bool = True
    save_layout: bool = True
    save_panel_state: bool = True
    save_visual_preferences: bool = True
    schema_version: int = 2
    migrate_older_schema: bool = True

    def normalized(self) -> GlassPersistenceConfig:
        return replace(
            self,
            storage_path=str(self.storage_path or "").strip()
            or "tools/_local/tmp/glass_workspace_state.json",
            schema_version=_positive_int(self.schema_version, 2, minimum=1),
        )


@dataclass(frozen=True, slots=True)
class GlassVisualScaleConfig:
    spacing_scale: float = 1.0
    padding_scale: float = 1.0
    icon_scale: float = 1.0
    control_height_scale: float = 1.0
    corner_radius_scale: float = 1.0
    border_strength_scale: float = 1.0
    surface_opacity_scale: float = 1.0
    blur_intensity_scale: float = 1.0
    elevation_scale: float = 1.0
    breathing_room_scale: float = 1.0
    data_density_bias: float = 0.0

    def normalized(self) -> GlassVisualScaleConfig:
        return replace(
            self,
            spacing_scale=_positive_float(self.spacing_scale, 1.0, minimum=0.2),
            padding_scale=_positive_float(self.padding_scale, 1.0, minimum=0.2),
            icon_scale=_positive_float(self.icon_scale, 1.0, minimum=0.4),
            control_height_scale=_positive_float(self.control_height_scale, 1.0, minimum=0.4),
            corner_radius_scale=_positive_float(self.corner_radius_scale, 1.0, minimum=0.3),
            border_strength_scale=_positive_float(self.border_strength_scale, 1.0, minimum=0.2),
            surface_opacity_scale=_positive_float(self.surface_opacity_scale, 1.0, minimum=0.3),
            blur_intensity_scale=_positive_float(self.blur_intensity_scale, 1.0, minimum=0.0),
            elevation_scale=_positive_float(self.elevation_scale, 1.0, minimum=0.0),
            breathing_room_scale=_positive_float(self.breathing_room_scale, 1.0, minimum=0.2),
            data_density_bias=max(-1.0, min(1.0, float(self.data_density_bias))),
        )


@dataclass(frozen=True, slots=True)
class GlassTypographyConfig:
    scale: str = "lg"
    primary_family: str = "Segoe UI"
    secondary_family: str = "Segoe UI"
    monospace_family: str = "Consolas"
    weight_regular: int = 500
    weight_semibold: int = 650
    weight_bold: int = 760
    line_height_mode: str = "regular"

    def normalized(self) -> GlassTypographyConfig:
        mode = _choice(self.line_height_mode, ("compact", "regular", "relaxed"), "regular")
        return replace(
            self,
            scale=_choice(self.scale, SUPPORTED_TYPOGRAPHY_SCALE, "lg"),
            primary_family=str(self.primary_family or "Segoe UI"),
            secondary_family=str(self.secondary_family or "Segoe UI"),
            monospace_family=str(self.monospace_family or "Consolas"),
            weight_regular=_positive_int(self.weight_regular, 500, minimum=100),
            weight_semibold=_positive_int(self.weight_semibold, 650, minimum=100),
            weight_bold=_positive_int(self.weight_bold, 760, minimum=100),
            line_height_mode=mode,
        )


@dataclass(frozen=True, slots=True)
class GlassThemeConfig:
    theme_id: str = DEFAULT_THEME_ID
    density: str = "comfortable"
    experience_mode: str = "default"
    visual_scale: GlassVisualScaleConfig = field(default_factory=GlassVisualScaleConfig)
    typography: GlassTypographyConfig = field(default_factory=GlassTypographyConfig)
    animation: GlassAnimationConfig = field(default_factory=GlassAnimationConfig)
    subtheme_id: str | None = None

    def normalized(self) -> GlassThemeConfig:
        return replace(
            self,
            theme_id=str(self.theme_id or DEFAULT_THEME_ID).strip().lower() or DEFAULT_THEME_ID,
            density=_choice(self.density, SUPPORTED_DENSITY, "comfortable"),
            experience_mode=_choice(self.experience_mode, SUPPORTED_EXPERIENCE_MODES, "default"),
            visual_scale=self.visual_scale.normalized(),
            typography=self.typography.normalized(),
            animation=self.animation.normalized(),
            subtheme_id=str(self.subtheme_id).strip().lower() if self.subtheme_id else None,
        )


@dataclass(frozen=True, slots=True)
class GlassRegionPolicyConfig:
    scroll_policy: str = "auto"
    shrink_policy: str = "balanced"
    overflow_policy: str = "clip"
    growth_policy: str = "balanced"
    allow_floating: bool = False
    allow_detach: bool = False

    def normalized(self) -> GlassRegionPolicyConfig:
        return replace(
            self,
            scroll_policy=_choice(self.scroll_policy, ("auto", "always", "never"), "auto"),
            shrink_policy=_choice(self.shrink_policy, ("balanced", "prefer_main", "prefer_side"), "balanced"),
            overflow_policy=_choice(self.overflow_policy, ("clip", "scroll", "expand"), "clip"),
            growth_policy=_choice(self.growth_policy, ("balanced", "main_bias", "side_bias"), "balanced"),
        )


@dataclass(frozen=True, slots=True)
class GlassRegionConfig:
    show_side: bool = True
    show_footer: bool = True
    show_status: bool = True
    show_inspector: bool = False
    show_activity: bool = False
    main_side_sizes: tuple[int, int] = (760, 420)
    main_side_inspector_sizes: tuple[int, int, int] = (680, 320, 280)
    min_main_width: int = 460
    min_side_width: int = 240
    min_inspector_width: int = 220
    policy: GlassRegionPolicyConfig = field(default_factory=GlassRegionPolicyConfig)

    def normalized(self) -> GlassRegionConfig:
        main, side = self.main_side_sizes
        a, b, c = self.main_side_inspector_sizes
        return replace(
            self,
            main_side_sizes=(_positive_int(main, 760), _positive_int(side, 420)),
            main_side_inspector_sizes=(
                _positive_int(a, 680),
                _positive_int(b, 320),
                _positive_int(c, 280),
            ),
            min_main_width=_positive_int(self.min_main_width, 460, minimum=120),
            min_side_width=_positive_int(self.min_side_width, 240, minimum=120),
            min_inspector_width=_positive_int(self.min_inspector_width, 220, minimum=120),
            policy=self.policy.normalized(),
        )


@dataclass(frozen=True, slots=True)
class GlassTabConfig:
    enabled: bool = True
    movable: bool = True
    closable: bool = False
    pinnable: bool = True
    favorites_enabled: bool = True
    document_mode: bool = True
    placement: str = "top"
    density: str = "comfortable"
    variant: str = "glass"
    icon_mode: str = "icon_text"
    hide_if_single_visible: bool = False
    overflow_scroll_buttons: bool = True
    default_tab_id: str = "workspace"
    default_tab_title: str = "Workspace"

    def normalized(self) -> GlassTabConfig:
        return replace(
            self,
            placement=_choice(self.placement, SUPPORTED_TAB_PLACEMENT, "top"),
            density=_choice(self.density, SUPPORTED_TAB_DENSITY, "comfortable"),
            variant=_choice(self.variant, SUPPORTED_TAB_VARIANTS, "glass"),
            icon_mode=_choice(self.icon_mode, SUPPORTED_TAB_ICON_MODES, "icon_text"),
            default_tab_id=str(self.default_tab_id or "workspace").strip() or "workspace",
            default_tab_title=str(self.default_tab_title or "Workspace").strip() or "Workspace",
        )


@dataclass(frozen=True, slots=True)
class GlassLayoutConfig:
    active_layout: str = "main_side"
    allow_runtime_switch: bool = True
    allow_user_layout_save: bool = True
    edit_mode_enabled: bool = False
    named_layouts: dict[str, dict[str, list[int] | tuple[int, ...]]] = field(default_factory=dict)

    def normalized(self) -> GlassLayoutConfig:
        normalized_layouts: dict[str, dict[str, list[int] | tuple[int, ...]]] = {}
        for name, payload in (self.named_layouts or {}).items():
            section: dict[str, list[int] | tuple[int, ...]] = {}
            if isinstance(payload, Mapping):
                for key, value in payload.items():
                    if isinstance(value, (list, tuple)):
                        section[str(key)] = [int(item) for item in value]
            normalized_layouts[str(name)] = section
        return replace(
            self,
            active_layout=str(self.active_layout or "main_side").strip() or "main_side",
            named_layouts=normalized_layouts,
        )


@dataclass(frozen=True, slots=True)
class GlassActionConfig:
    include_default_actions: bool = True
    cancel_text: str = "Cancel"
    submit_text: str = "Continue"
    cancel_variant: str = "danger"
    submit_variant: str = "primary"
    primary_shortcut: str = "Ctrl+Return"
    secondary_shortcut: str = "Esc"


@dataclass(frozen=True, slots=True)
class GlassTemplateConfig:
    title: str = "Workspace"
    subtitle: str = "Compose your workflow with reusable glass panels."
    eyebrow: str = "WORKSPACE"
    variant: str = "selector"
    theme: GlassThemeConfig = field(default_factory=GlassThemeConfig)
    regions: GlassRegionConfig = field(default_factory=GlassRegionConfig)
    tabs: GlassTabConfig = field(default_factory=GlassTabConfig)
    layout: GlassLayoutConfig = field(default_factory=GlassLayoutConfig)
    actions: GlassActionConfig = field(default_factory=GlassActionConfig)
    interaction: GlassInteractionConfig = field(default_factory=GlassInteractionConfig)
    accessibility: GlassAccessibilityConfig = field(default_factory=GlassAccessibilityConfig)
    persistence: GlassPersistenceConfig = field(default_factory=GlassPersistenceConfig)
    apply_stylesheet: bool = True
    with_chrome: bool = True
    debug_mode: bool = False

    def normalized(self) -> GlassTemplateConfig:
        return replace(
            self,
            title=str(self.title or "Workspace"),
            subtitle=str(self.subtitle or ""),
            eyebrow=str(self.eyebrow or "WORKSPACE"),
            variant=str(self.variant or "selector"),
            theme=self.theme.normalized(),
            regions=self.regions.normalized(),
            tabs=self.tabs.normalized(),
            layout=self.layout.normalized(),
            persistence=self.persistence.normalized(),
        )


@dataclass(frozen=True, slots=True)
class GlassResolvedConfig:
    config: GlassTemplateConfig
    field_sources: dict[str, str]
    layers_applied: tuple[str, ...]

    def source_for(self, field_path: str) -> str | None:
        return self.field_sources.get(field_path)


def _merge_dict(base: dict[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _merge_dict(dict(merged[key]), value)
            continue
        merged[key] = value
    return merged


def _flatten(payload: Mapping[str, Any], prefix: str = "") -> dict[str, Any]:
    flat: dict[str, Any] = {}
    for key, value in payload.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, Mapping):
            flat.update(_flatten(value, prefix=path))
            continue
        flat[path] = value
    return flat


def _as_plain(config: GlassTemplateConfig) -> dict[str, Any]:
    return asdict(config)


def _template_config_from_dict(payload: Mapping[str, Any]) -> GlassTemplateConfig:
    theme_payload = payload.get("theme") or {}
    visual_scale_payload = theme_payload.get("visual_scale") or {}
    typography_payload = theme_payload.get("typography") or {}
    animation_payload = theme_payload.get("animation") or {}

    regions_payload = payload.get("regions") or {}
    region_policy_payload = regions_payload.get("policy") or {}

    return GlassTemplateConfig(
        title=str(payload.get("title", "Workspace")),
        subtitle=str(payload.get("subtitle", "")),
        eyebrow=str(payload.get("eyebrow", "WORKSPACE")),
        variant=str(payload.get("variant", "selector")),
        theme=GlassThemeConfig(
            theme_id=str(theme_payload.get("theme_id", DEFAULT_THEME_ID)),
            density=str(theme_payload.get("density", "comfortable")),
            experience_mode=str(theme_payload.get("experience_mode", "default")),
            subtheme_id=theme_payload.get("subtheme_id"),
            visual_scale=GlassVisualScaleConfig(**visual_scale_payload),
            typography=GlassTypographyConfig(**typography_payload),
            animation=GlassAnimationConfig(**animation_payload),
        ),
        regions=GlassRegionConfig(
            show_side=bool(regions_payload.get("show_side", True)),
            show_footer=bool(regions_payload.get("show_footer", True)),
            show_status=bool(regions_payload.get("show_status", True)),
            show_inspector=bool(regions_payload.get("show_inspector", False)),
            show_activity=bool(regions_payload.get("show_activity", False)),
            main_side_sizes=tuple(regions_payload.get("main_side_sizes", (760, 420))),
            main_side_inspector_sizes=tuple(regions_payload.get("main_side_inspector_sizes", (680, 320, 280))),
            min_main_width=int(regions_payload.get("min_main_width", 460)),
            min_side_width=int(regions_payload.get("min_side_width", 240)),
            min_inspector_width=int(regions_payload.get("min_inspector_width", 220)),
            policy=GlassRegionPolicyConfig(**region_policy_payload),
        ),
        tabs=GlassTabConfig(**(payload.get("tabs") or {})),
        layout=GlassLayoutConfig(**(payload.get("layout") or {})),
        actions=GlassActionConfig(**(payload.get("actions") or {})),
        interaction=GlassInteractionConfig(**(payload.get("interaction") or {})),
        accessibility=GlassAccessibilityConfig(**(payload.get("accessibility") or {})),
        persistence=GlassPersistenceConfig(**(payload.get("persistence") or {})),
        apply_stylesheet=bool(payload.get("apply_stylesheet", True)),
        with_chrome=bool(payload.get("with_chrome", True)),
        debug_mode=bool(payload.get("debug_mode", False)),
    ).normalized()


def merge_template_config(*configs: GlassTemplateConfig) -> GlassTemplateConfig:
    if not configs:
        return GlassTemplateConfig().normalized()
    merged = _as_plain(configs[0].normalized())
    for cfg in configs[1:]:
        merged = _merge_dict(merged, _as_plain(cfg.normalized()))
    return _template_config_from_dict(merged)


def _layered_resolution(
    framework_defaults: GlassTemplateConfig,
    layers: list[tuple[str, GlassTemplateConfig]],
) -> GlassResolvedConfig:
    merged_payload = _as_plain(framework_defaults.normalized())
    provenance = {path: "framework_defaults" for path in _flatten(merged_payload)}
    applied_layers: list[str] = ["framework_defaults"]

    for layer_name, cfg in layers:
        payload = _as_plain(cfg.normalized())
        layer_flat = _flatten(payload)
        merged_payload = _merge_dict(merged_payload, payload)
        for path in layer_flat:
            provenance[path] = layer_name
        applied_layers.append(layer_name)

    resolved = _template_config_from_dict(merged_payload)
    return GlassResolvedConfig(
        config=resolved,
        field_sources=provenance,
        layers_applied=tuple(applied_layers),
    )


def _neutral_preset() -> GlassTemplateConfig:
    return GlassTemplateConfig()


def _form_console_preset() -> GlassTemplateConfig:
    return GlassTemplateConfig(
        title="Form Console",
        subtitle="Capture structured input with validated fields and side helpers.",
        eyebrow="FORM",
        theme=GlassThemeConfig(experience_mode="data_entry"),
        regions=GlassRegionConfig(show_side=True, show_footer=True, show_status=True, main_side_sizes=(800, 360)),
        tabs=GlassTabConfig(enabled=True, movable=True, default_tab_id="capture", default_tab_title="Capture"),
    )


def _dashboard_preset() -> GlassTemplateConfig:
    return GlassTemplateConfig(
        title="Dashboard Console",
        subtitle="Monitor metrics, trends, and alerts across reusable panels.",
        eyebrow="DASHBOARD",
        theme=GlassThemeConfig(experience_mode="dashboard", density="cozy"),
        regions=GlassRegionConfig(show_side=True, show_footer=True, show_status=True, main_side_sizes=(860, 380)),
        tabs=GlassTabConfig(enabled=True, movable=True, default_tab_id="overview", default_tab_title="Overview"),
        layout=GlassLayoutConfig(active_layout="dashboard"),
    )


def _inspector_preset() -> GlassTemplateConfig:
    return GlassTemplateConfig(
        title="Inspector Console",
        subtitle="Review details and context with focused side inspection.",
        eyebrow="INSPECTOR",
        theme=GlassThemeConfig(experience_mode="inspector"),
        regions=GlassRegionConfig(
            show_side=True,
            show_footer=True,
            show_status=True,
            show_inspector=True,
            main_side_sizes=(700, 500),
            main_side_inspector_sizes=(620, 320, 260),
        ),
        tabs=GlassTabConfig(enabled=True, movable=False, default_tab_id="inspect", default_tab_title="Inspect"),
        layout=GlassLayoutConfig(active_layout="main_side_inspector"),
    )


def _compact_operator_preset() -> GlassTemplateConfig:
    return GlassTemplateConfig(
        title="Operator Console",
        subtitle="Compact density and fast keyboard-centric interactions.",
        eyebrow="OPS",
        theme=GlassThemeConfig(
            density="compact",
            experience_mode="operator",
            typography=GlassTypographyConfig(scale="sm"),
        ),
        regions=GlassRegionConfig(show_side=False, show_footer=True, show_status=True, main_side_sizes=(1120, 0)),
        tabs=GlassTabConfig(
            enabled=True,
            movable=True,
            density="compact",
            variant="segmented",
            default_tab_id="active",
            default_tab_title="Active",
        ),
        interaction=GlassInteractionConfig(command_palette_enabled=True),
    )


def _tabbed_workspace_preset() -> GlassTemplateConfig:
    return GlassTemplateConfig(
        title="Tabbed Workspace",
        subtitle="Separate contexts with explicit visibility and hold states.",
        eyebrow="WORKSPACE",
        theme=GlassThemeConfig(experience_mode="default"),
        regions=GlassRegionConfig(show_side=True, show_footer=True, show_status=True, main_side_sizes=(760, 420)),
        tabs=GlassTabConfig(
            enabled=True,
            movable=True,
            closable=True,
            pinnable=True,
            favorites_enabled=True,
            default_tab_id="workspace",
            default_tab_title="Workspace",
        ),
    )


def _presentation_preset() -> GlassTemplateConfig:
    return GlassTemplateConfig(
        title="Presentation Mode",
        subtitle="Low-density high legibility with reduced chrome noise.",
        eyebrow="PRESENT",
        theme=GlassThemeConfig(
            density="extended",
            experience_mode="presentation",
            typography=GlassTypographyConfig(scale="xl"),
            animation=GlassAnimationConfig(level="subtle"),
        ),
        regions=GlassRegionConfig(show_side=False, show_footer=False, show_status=True, main_side_sizes=(1200, 0)),
        tabs=GlassTabConfig(enabled=False),
        interaction=GlassInteractionConfig(keyboard_shortcuts_enabled=True, command_palette_enabled=False),
    )


_PRESET_FACTORIES: dict[str, Callable[[], GlassTemplateConfig]] = {
    "neutral": _neutral_preset,
    "form_console": _form_console_preset,
    "dashboard": _dashboard_preset,
    "inspector": _inspector_preset,
    "compact_operator": _compact_operator_preset,
    "tabbed_workspace": _tabbed_workspace_preset,
    "presentation": _presentation_preset,
}


def register_template_preset(
    name: str,
    *,
    factory: Callable[[], GlassTemplateConfig] | None = None,
    config: GlassTemplateConfig | None = None,
    base_preset: str | None = None,
    override: bool = False,
) -> None:
    normalized = str(name or "").strip().lower()
    if not normalized:
        raise ValueError("preset name is required")
    if not override and normalized in _PRESET_FACTORIES:
        raise ValueError(f"preset '{normalized}' already registered")
    if factory is None and config is None:
        raise ValueError("factory or config is required")

    def resolver() -> GlassTemplateConfig:
        inherited = get_template_preset(base_preset) if base_preset else get_template_preset("neutral")
        own = factory() if factory is not None else config or GlassTemplateConfig()
        return merge_template_config(inherited, own)

    _PRESET_FACTORIES[normalized] = resolver


def list_template_presets() -> tuple[str, ...]:
    return tuple(sorted(_PRESET_FACTORIES.keys()))


def get_template_preset(name: str = "neutral") -> GlassTemplateConfig:
    normalized = str(name or "neutral").strip().lower()
    factory = _PRESET_FACTORIES.get(normalized, _PRESET_FACTORIES["neutral"])
    return factory().normalized()


def resolve_template_config(
    config: GlassTemplateConfig | None = None,
    *,
    preset: str | None = None,
    framework_defaults: GlassTemplateConfig | None = None,
    theme_defaults: GlassTemplateConfig | None = None,
    app_overrides: GlassTemplateConfig | None = None,
    workspace_overrides: GlassTemplateConfig | None = None,
    runtime_overrides: GlassTemplateConfig | None = None,
) -> GlassTemplateConfig:
    return resolve_template_config_with_provenance(
        config=config,
        preset=preset,
        framework_defaults=framework_defaults,
        theme_defaults=theme_defaults,
        app_overrides=app_overrides,
        workspace_overrides=workspace_overrides,
        runtime_overrides=runtime_overrides,
    ).config


def resolve_template_config_with_provenance(
    config: GlassTemplateConfig | None = None,
    *,
    preset: str | None = None,
    framework_defaults: GlassTemplateConfig | None = None,
    theme_defaults: GlassTemplateConfig | None = None,
    app_overrides: GlassTemplateConfig | None = None,
    workspace_overrides: GlassTemplateConfig | None = None,
    runtime_overrides: GlassTemplateConfig | None = None,
) -> GlassResolvedConfig:
    base = (framework_defaults or get_template_preset("neutral")).normalized()
    layers: list[tuple[str, GlassTemplateConfig]] = []
    if theme_defaults is not None:
        layers.append(("theme_defaults", theme_defaults))
    if preset is not None:
        layers.append(("preset_defaults", get_template_preset(preset)))
    if app_overrides is not None:
        layers.append(("app_overrides", app_overrides))
    if workspace_overrides is not None:
        layers.append(("workspace_overrides", workspace_overrides))
    if runtime_overrides is not None:
        layers.append(("runtime_overrides", runtime_overrides))
    if config is not None:
        layers.append(("explicit_config", config))
    return _layered_resolution(base, layers)
