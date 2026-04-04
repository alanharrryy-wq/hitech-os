from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLabel, QWidget

from .appearance import AppearanceCoordinator, AppearanceSnapshot
from .config import GlassTemplateConfig, resolve_template_config
from .contracts import DEFAULT_THEME_ID
from ._template_layout import GlassLayoutController
from ._template_shell_appearance import _GlassPanelTemplateAppearanceMixin
from ._template_shell_build import _GlassPanelTemplateBuildMixin
from ._template_shell_state import _GlassPanelTemplateStateMixin
from ._template_shell_workspace import _GlassPanelTemplateWorkspaceMixin
from ._template_tabs import GlassWorkspaceTabs


class GlassPanelTemplate(
    _GlassPanelTemplateBuildMixin,
    _GlassPanelTemplateAppearanceMixin,
    _GlassPanelTemplateWorkspaceMixin,
    _GlassPanelTemplateStateMixin,
    QWidget,
):
    """Reusable glass shell with tabs, role-aware panels, and layout control."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        config: GlassTemplateConfig | None = None,
        preset: str | None = None,
        title: str | None = None,
        subtitle: str | None = None,
        eyebrow: str | None = None,
        variant: str | None = None,
        theme_id: str | None = None,
        density: str | None = None,
        typography_scale: str | None = None,
        with_chrome: bool | None = None,
        show_side: bool | None = None,
        show_footer: bool | None = None,
        show_status: bool | None = None,
        include_default_actions: bool | None = None,
        cancel_text: str | None = None,
        submit_text: str | None = None,
        cancel_variant: str | None = None,
        submit_variant: str | None = None,
        apply_stylesheet: bool | None = None,
        enable_workspace_tabs: bool | None = None,
        default_tab_id: str | None = None,
        default_tab_title: str | None = None,
        appearance_coordinator: AppearanceCoordinator | None = None,
    ) -> None:
        super().__init__(parent)
        resolved = resolve_template_config(config, preset=preset)

        self._title = str(title if title is not None else resolved.title)
        self._subtitle = str(subtitle if subtitle is not None else resolved.subtitle)
        self._eyebrow = str(eyebrow if eyebrow is not None else resolved.eyebrow)
        self._variant = str(variant if variant is not None else resolved.variant)
        self._theme_id = str(theme_id if theme_id is not None else resolved.theme.theme_id or DEFAULT_THEME_ID)
        self._density = str(density if density is not None else resolved.theme.density)
        self._typography_scale = str(typography_scale if typography_scale is not None else resolved.theme.typography.scale)
        self._show_side = bool(show_side if show_side is not None else resolved.regions.show_side)
        self._show_footer = bool(show_footer if show_footer is not None else resolved.regions.show_footer)
        self._show_status = bool(show_status if show_status is not None else resolved.regions.show_status)
        self._with_chrome = bool(with_chrome if with_chrome is not None else resolved.with_chrome)
        self._include_default_actions = bool(
            include_default_actions
            if include_default_actions is not None
            else resolved.actions.include_default_actions
        )
        self._cancel_text = str(cancel_text if cancel_text is not None else resolved.actions.cancel_text)
        self._submit_text = str(submit_text if submit_text is not None else resolved.actions.submit_text)
        self._cancel_variant = str(cancel_variant if cancel_variant is not None else resolved.actions.cancel_variant)
        self._submit_variant = str(submit_variant if submit_variant is not None else resolved.actions.submit_variant)
        self._apply_stylesheet = bool(
            apply_stylesheet if apply_stylesheet is not None else resolved.apply_stylesheet
        )
        self._enable_workspace_tabs = bool(
            enable_workspace_tabs if enable_workspace_tabs is not None else resolved.tabs.enabled
        )
        self._tabs_movable = bool(resolved.tabs.movable)
        self._tabs_closable = bool(resolved.tabs.closable)
        self._tabs_document_mode = bool(resolved.tabs.document_mode)
        self._tabs_placement = str(resolved.tabs.placement)
        self._tabs_density = str(resolved.tabs.density)
        self._tabs_variant = str(resolved.tabs.variant)
        self._tabs_icon_mode = str(resolved.tabs.icon_mode)
        self._tabs_hide_single = bool(resolved.tabs.hide_if_single_visible)
        self._tabs_overflow_scroll = bool(resolved.tabs.overflow_scroll_buttons)
        self._default_tab_id = str(default_tab_id if default_tab_id is not None else resolved.tabs.default_tab_id)
        self._default_tab_title = str(
            default_tab_title if default_tab_title is not None else resolved.tabs.default_tab_title
        )
        self._default_main_side_sizes = list(resolved.regions.main_side_sizes)
        self._layout_named_presets = dict(resolved.layout.named_layouts)
        self._active_layout_name = str(resolved.layout.active_layout or "main_side")
        self._allow_layout_switch = bool(resolved.layout.allow_runtime_switch)
        self._allow_layout_save = bool(resolved.layout.allow_user_layout_save)
        self._edit_mode_enabled = bool(resolved.layout.edit_mode_enabled)
        self._primary_shortcut = str(resolved.actions.primary_shortcut or "Ctrl+Return")
        self._secondary_shortcut = str(resolved.actions.secondary_shortcut or "Esc")
        self._icon_scale = float(resolved.theme.visual_scale.icon_scale)
        self._border_strength_scale = float(resolved.theme.visual_scale.border_strength_scale)
        self._surface_opacity_scale = float(resolved.theme.visual_scale.surface_opacity_scale)
        self._blur_intensity_scale = float(resolved.theme.visual_scale.blur_intensity_scale)
        self._elevation_scale = float(resolved.theme.visual_scale.elevation_scale)
        self._corner_radius_scale = float(resolved.theme.visual_scale.corner_radius_scale)
        self._appearance_coordinator: AppearanceCoordinator | None = None
        self._appearance_snapshot: AppearanceSnapshot | None = None
        self._appearance_sync_guard = False

        self._title_label: QLabel | None = None
        self._subtitle_label: QLabel | None = None
        self._eyebrow_label: QLabel | None = None
        self._status_label: QLabel | None = None

        self.layout_controller = GlassLayoutController(splitters={}, default_sizes={})
        self._panels: dict[str, GlassPanelFrame] = {}
        self._slot_shell_ids: set[str] = set()
        self.workspace_tabs: GlassWorkspaceTabs | None = None

        self.slots, self.cards, self.actions = self._build()
        self._visual_hosts = self._collect_visual_hosts()
        self._surface_hosts = self._collect_surface_hosts()
        self._install_surface_renderers()
        self._apply_theme_stylesheet()
        self._apply_visual_effects()
        if appearance_coordinator is not None:
            self.set_appearance_coordinator(appearance_coordinator, apply_current=True)


__all__ = ["GlassPanelTemplate"]
