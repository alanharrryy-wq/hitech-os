from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget

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

    @property
    def resolved(self) -> GlassResolvedConfig:
        return self._resolved

    def current_config(self) -> GlassTemplateConfig:
        return self._resolved.config

    def apply_resolved_config(self) -> None:
        config = self._resolved.config
        self.template.set_theme(config.theme.theme_id)
        self.template.set_density(config.theme.density)
        self.template.set_typography_scale(config.theme.typography.scale)
        self.template.set_tab_placement(config.tabs.placement)
        self.template.set_tab_variant(config.tabs.variant)
        self.template.set_tab_density(config.tabs.density)
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
        payload.setdefault("active_theme_id", config.theme.theme_id)
        payload.setdefault("active_density", config.theme.density)
        payload.setdefault("active_preset", config.theme.experience_mode)
        payload.setdefault("active_layout", config.layout.active_layout)
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
        return {
            "theme_id": config.theme.theme_id,
            "density": config.theme.density,
            "experience_mode": config.theme.experience_mode,
            "layout_active": config.layout.active_layout,
            "layouts_registered": sorted(self._layout_registry.keys()),
            "tabs_enabled": config.tabs.enabled,
            "tab_variant": config.tabs.variant,
            "tab_density": config.tabs.density,
            "field_sources_count": len(self._resolved.field_sources),
            "layers_applied": list(self._resolved.layers_applied),
        }
