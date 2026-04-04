from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget

from .appearance import (
    AppearanceCoordinator,
    AppearanceProfile,
    EffectsProfile,
    VisualIntelligenceBundle,
    VisualIntelligenceContext,
    select_visual_bundle,
)
from .config import (
    GlassResolvedConfig,
    GlassTemplateConfig,
    resolve_template_config_with_provenance,
)
from .persistence import GlassWorkspaceState, load_workspace_state, save_workspace_state
from .template import GlassPanelTemplate


@dataclass(frozen=True, slots=True)
class GlassRuntimeContext:
    role: str = "default"
    mode: str = "default"
    capabilities: frozenset[str] = frozenset()
    flags: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GlassVisibilityRule:
    target_kind: str  # tab | panel | action
    target_id: str
    visible_state: str = "visible"
    required_capabilities: tuple[str, ...] = ()
    allowed_roles: tuple[str, ...] = ()
    allowed_modes: tuple[str, ...] = ()
    required_flag: str | None = None
    required_flag_value: Any = True

    def resolve_state(self, context: GlassRuntimeContext) -> str:
        if self.required_capabilities:
            if not set(self.required_capabilities).issubset(set(context.capabilities)):
                return "hidden"
        if self.allowed_roles and context.role not in self.allowed_roles:
            return "hidden"
        if self.allowed_modes and context.mode not in self.allowed_modes:
            return "hidden"
        if self.required_flag is not None:
            if context.flags.get(self.required_flag) != self.required_flag_value:
                return "hidden"
        return self.visible_state


@dataclass(slots=True)
class GlassVisibilityPolicy:
    rules: list[GlassVisibilityRule] = field(default_factory=list)

    def register(self, rule: GlassVisibilityRule) -> None:
        self.rules.append(rule)

    def evaluate(self, context: GlassRuntimeContext) -> dict[tuple[str, str], str]:
        states: dict[tuple[str, str], str] = {}
        for rule in self.rules:
            states[(rule.target_kind, rule.target_id)] = rule.resolve_state(context)
        return states


class GlassWorkspaceRuntime:
    """
    Runtime orchestration layer for config resolution, layout switching,
    visibility policy, keyboard routing and workspace persistence.
    """

    def __init__(
        self,
        template: GlassPanelTemplate,
        *,
        framework_defaults: GlassTemplateConfig | None = None,
        preset: str | None = None,
        app_overrides: GlassTemplateConfig | None = None,
        workspace_overrides: GlassTemplateConfig | None = None,
        runtime_overrides: GlassTemplateConfig | None = None,
        explicit_config: GlassTemplateConfig | None = None,
        visibility_policy: GlassVisibilityPolicy | None = None,
        appearance_coordinator: AppearanceCoordinator | None = None,
        visual_context: VisualIntelligenceContext | None = None,
    ) -> None:
        self.template = template
        self.visibility_policy = visibility_policy or GlassVisibilityPolicy()
        self._framework_defaults = framework_defaults
        self._preset = preset
        self._app_overrides = app_overrides
        self._workspace_overrides = workspace_overrides
        self._runtime_overrides = runtime_overrides
        self._explicit_config = explicit_config
        self._resolved: GlassResolvedConfig = resolve_template_config_with_provenance(
            config=explicit_config,
            preset=preset,
            framework_defaults=framework_defaults,
            app_overrides=app_overrides,
            workspace_overrides=workspace_overrides,
            runtime_overrides=runtime_overrides,
        )
        self._layout_registry: dict[str, dict[str, list[int] | tuple[int, ...]]] = dict(
            self._resolved.config.layout.named_layouts
        )
        self._shortcuts: list[QShortcut] = []
        self._visual_context = visual_context.normalized() if visual_context is not None else None
        self._visual_intelligence: VisualIntelligenceBundle | None = None
        self._appearance_coordinator = appearance_coordinator or AppearanceCoordinator.from_template_config(
            self._resolved.config
        )
        if hasattr(self.template, 'set_appearance_coordinator'):
            self.template.set_appearance_coordinator(self._appearance_coordinator, apply_current=False)
        self._sync_appearance_from_resolved_config(source='runtime_init', emit=False)

    @property
    def resolved(self) -> GlassResolvedConfig:
        return self._resolved

    def current_config(self) -> GlassTemplateConfig:
        return self._resolved.config

    @property
    def appearance_coordinator(self) -> AppearanceCoordinator:
        return self._appearance_coordinator

    def appearance_snapshot(self):
        return self._appearance_coordinator.snapshot(source='runtime_snapshot')

    @property
    def visual_context(self) -> VisualIntelligenceContext | None:
        return self._visual_context

    @property
    def visual_intelligence(self) -> VisualIntelligenceBundle | None:
        return self._visual_intelligence

    def set_visual_context(self, context: VisualIntelligenceContext | None) -> None:
        self._visual_context = context.normalized() if context is not None else None
        self.apply_resolved_config()

    def set_visual_level(self, level: str) -> None:
        current = self._visual_context or VisualIntelligenceContext(
            experience_mode=self._resolved.config.theme.experience_mode,
            reduced_motion=self._resolved.config.theme.animation.reduced_motion,
            high_contrast_mode=self._resolved.config.accessibility.high_contrast_mode,
            data_density_bias=self._resolved.config.theme.visual_scale.data_density_bias,
        )
        self.set_visual_context(
            VisualIntelligenceContext(
                experience_mode=current.experience_mode,
                requested_visual_level=level,
                preferred_preset=current.preferred_preset,
                data_state=current.data_state,
                reduced_motion=current.reduced_motion,
                high_contrast_mode=current.high_contrast_mode,
                data_density_bias=current.data_density_bias,
                performance_sensitive=current.performance_sensitive,
                source=current.source,
            )
        )

    def set_data_state(self, state: str) -> None:
        current = self._visual_context or VisualIntelligenceContext(
            experience_mode=self._resolved.config.theme.experience_mode,
            reduced_motion=self._resolved.config.theme.animation.reduced_motion,
            high_contrast_mode=self._resolved.config.accessibility.high_contrast_mode,
            data_density_bias=self._resolved.config.theme.visual_scale.data_density_bias,
        )
        self.set_visual_context(
            VisualIntelligenceContext(
                experience_mode=current.experience_mode,
                requested_visual_level=current.requested_visual_level,
                preferred_preset=current.preferred_preset,
                data_state=state,
                reduced_motion=current.reduced_motion,
                high_contrast_mode=current.high_contrast_mode,
                data_density_bias=current.data_density_bias,
                performance_sensitive=current.performance_sensitive,
                source=current.source,
            )
        )

    def set_appearance_coordinator(self, coordinator: AppearanceCoordinator, *, apply_current: bool = True) -> None:
        self._appearance_coordinator = coordinator
        if hasattr(self.template, 'set_appearance_coordinator'):
            self.template.set_appearance_coordinator(coordinator, apply_current=apply_current)
        if apply_current:
            self._sync_appearance_from_resolved_config(source='runtime_rebind', emit=False)

    def _sync_appearance_from_resolved_config(self, *, source: str, emit: bool) -> None:
        profile = AppearanceProfile.from_template_config(self._resolved.config)
        effects = EffectsProfile.from_appearance(profile)
        preset_name = self._appearance_coordinator.preset_name
        source_label = source
        if self._visual_context is not None:
            context = self._visual_context
            context_bias = (
                profile.data_density_bias
                if abs(float(context.data_density_bias)) < 1e-9
                else context.data_density_bias
            )
            resolved_context = VisualIntelligenceContext(
                experience_mode=context.experience_mode or profile.experience_mode,
                requested_visual_level=context.requested_visual_level,
                preferred_preset=context.preferred_preset,
                data_state=context.data_state,
                reduced_motion=bool(context.reduced_motion or profile.reduced_motion),
                high_contrast_mode=bool(context.high_contrast_mode or profile.high_contrast_mode),
                data_density_bias=context_bias,
                performance_sensitive=context.performance_sensitive,
                source=context.source,
            ).normalized()
            intelligence = select_visual_bundle(
                resolved_context,
                base_profile=profile,
                base_effects=effects,
            )
            self._visual_intelligence = intelligence
            profile = intelligence.profile
            effects = intelligence.effects
            preset_name = intelligence.preset_name or preset_name
            source_label = f'{source}|{intelligence.source}'
        else:
            self._visual_intelligence = None
        snapshot = self._appearance_coordinator.replace(
            profile=profile,
            effects=effects,
            preset_name=preset_name,
            source=source_label,
            emit=emit,
        )
        if not emit and hasattr(self.template, 'apply_appearance_snapshot'):
            self.template.apply_appearance_snapshot(snapshot)

    def apply_resolved_config(self) -> None:
        config = self._resolved.config
        self._sync_appearance_from_resolved_config(source='resolved_config', emit=True)
        self.template.set_tab_placement(config.tabs.placement)
        self.template.set_tab_icon_mode(config.tabs.icon_mode)
        self.template.set_hide_single_tab_bar(config.tabs.hide_if_single_visible)
        self.template.set_side_visible(config.regions.show_side)
        self.template.set_footer_visible(config.regions.show_footer)
        self.template.set_status_visible(config.regions.show_status)
        self.template.set_submit_enabled(True)
        if config.layout.active_layout:
            self.apply_layout(config.layout.active_layout, tolerate_missing=True)

    def update_runtime_overrides(self, overrides: GlassTemplateConfig | None = None) -> None:
        self._runtime_overrides = overrides
        self._resolved = resolve_template_config_with_provenance(
            config=self._explicit_config,
            preset=self._preset,
            framework_defaults=self._framework_defaults,
            app_overrides=self._app_overrides,
            workspace_overrides=self._workspace_overrides,
            runtime_overrides=self._runtime_overrides,
        )
        self.apply_resolved_config()

    def activate_preset(
        self,
        preset: str,
        *,
        app_overrides: GlassTemplateConfig | None = None,
        workspace_overrides: GlassTemplateConfig | None = None,
        runtime_overrides: GlassTemplateConfig | None = None,
    ) -> None:
        self._preset = preset
        self._app_overrides = app_overrides
        self._workspace_overrides = workspace_overrides
        self._runtime_overrides = runtime_overrides
        self._resolved = resolve_template_config_with_provenance(
            config=self._explicit_config,
            preset=preset,
            framework_defaults=self._framework_defaults,
            app_overrides=app_overrides,
            workspace_overrides=workspace_overrides,
            runtime_overrides=runtime_overrides,
        )
        self._layout_registry.update(self._resolved.config.layout.named_layouts)
        self.apply_resolved_config()

    def register_layout(self, name: str, layout_payload: dict[str, list[int] | tuple[int, ...]]) -> None:
        normalized = str(name or "").strip().lower()
        if not normalized:
            raise ValueError("layout name is required")
        self._layout_registry[normalized] = dict(layout_payload)

    def save_current_layout(self, name: str) -> None:
        self.register_layout(name, self.template.snapshot_layout_state())

    def apply_layout(self, name: str, *, tolerate_missing: bool = False) -> None:
        normalized = str(name or "").strip().lower()
        payload = self._layout_registry.get(normalized)
        if payload is None:
            if tolerate_missing:
                return
            raise KeyError(f"layout '{normalized}' is not registered")
        self.template.restore_layout_state(payload)

    def restore_default_layout(self) -> None:
        self.template.layout_controller.reset_defaults()

    def apply_visibility_context(self, context: GlassRuntimeContext) -> None:
        states = self.visibility_policy.evaluate(context)
        for (target_kind, target_id), state in states.items():
            if target_kind == "tab":
                self.template.set_workspace_tab_state(target_id, state)
                continue
            if target_kind == "panel":
                self.template.set_panel_state(target_id, state)
                self.template.set_panel_visible(target_id, state not in {"hidden", "collapsed"})
                continue
            if target_kind == "action":
                # Reserved extension point. Current actions are user-managed.
                continue

    def bind_default_shortcuts(self, host: QWidget | None = None) -> None:
        root = host or self.template
        config = self._resolved.config.interaction
        if not config.keyboard_shortcuts_enabled:
            return
        self._shortcuts.clear()
        if config.tab_shortcuts_enabled:
            self._register_shortcut(root, config.quick_switch_shortcut, self._next_tab)
            self._register_shortcut(root, config.reverse_switch_shortcut, self._previous_tab)
        if config.panel_shortcuts_enabled:
            self._register_shortcut(root, "Ctrl+\\", self._toggle_side_panel)

    def _register_shortcut(self, host: QWidget, sequence: str, callback: Callable[[], None]) -> None:
        shortcut = QShortcut(QKeySequence(sequence), host)
        shortcut.activated.connect(callback)
        self._shortcuts.append(shortcut)

    def _next_tab(self) -> None:
        tabs = self.template.workspace_tabs
        if tabs is None or tabs.count() < 2:
            return
        tabs.setCurrentIndex((tabs.currentIndex() + 1) % tabs.count())

    def _previous_tab(self) -> None:
        tabs = self.template.workspace_tabs
        if tabs is None or tabs.count() < 2:
            return
        tabs.setCurrentIndex((tabs.currentIndex() - 1) % tabs.count())

    def _toggle_side_panel(self) -> None:
        currently_visible = bool(self.template.cards.side.isVisible())
        self.template.set_side_visible(not currently_visible)

    def export_workspace_state(self, *, metadata: dict[str, Any] | None = None) -> GlassWorkspaceState:
        config = self._resolved.config
        payload = dict(metadata or {})
        appearance = self.appearance_snapshot()
        payload.setdefault("active_theme_id", appearance.profile.theme_id)
        payload.setdefault("active_density", appearance.profile.density)
        payload.setdefault("active_typography_scale", appearance.profile.typography_scale)
        payload.setdefault("active_preset", appearance.preset_name or config.theme.experience_mode)
        payload.setdefault("active_layout", config.layout.active_layout)
        payload.setdefault("active_glow_intensity", appearance.effects.glow_intensity)
        return self.template.export_workspace_state(metadata=payload)

    def save_workspace_state(self, path: str | Path | None = None) -> Path | None:
        config = self._resolved.config.persistence
        if not config.enabled:
            return None
        target = Path(path) if path else Path(config.storage_path)
        state = self.export_workspace_state()
        return save_workspace_state(target, state)

    def load_workspace_state(self, path: str | Path | None = None) -> GlassWorkspaceState | None:
        config = self._resolved.config.persistence
        if not config.enabled:
            return None
        source = Path(path) if path else Path(config.storage_path)
        state = load_workspace_state(source)
        if state is None:
            return None
        self.template.apply_workspace_state(state)
        return state

    def diagnostics(self) -> dict[str, Any]:
        config = self._resolved.config
        appearance = self.appearance_snapshot()
        return {
            "theme_id": appearance.profile.theme_id,
            "density": appearance.profile.density,
            "experience_mode": config.theme.experience_mode,
            "appearance_preset": appearance.preset_name,
            "visual_context_level": (
                self._visual_context.requested_visual_level if self._visual_context is not None else None
            ),
            "visual_context_data_state": (
                self._visual_context.data_state if self._visual_context is not None else None
            ),
            "effective_visual_level": (
                self._visual_intelligence.effective_level if self._visual_intelligence is not None else None
            ),
            "visual_intelligence_source": (
                self._visual_intelligence.source if self._visual_intelligence is not None else None
            ),
            "glow_intensity": appearance.effects.glow_intensity,
            "blur_intensity_scale": appearance.profile.blur_intensity_scale,
            "layout_active": config.layout.active_layout,
            "layouts_registered": sorted(self._layout_registry.keys()),
            "tabs_enabled": config.tabs.enabled,
            "tab_variant": config.tabs.variant,
            "tab_density": config.tabs.density,
            "field_sources_count": len(self._resolved.field_sources),
            "layers_applied": list(self._resolved.layers_applied),
        }
