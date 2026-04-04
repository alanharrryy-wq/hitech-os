from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QWidget

from .appearance import AppearanceCoordinator, AppearanceProfile, AppearanceSnapshot, EffectsProfile, resolve_appearance_tokens
from .controls import create_button
from .contracts import DEFAULT_THEME_ID
from .effects import apply_shadow, enable_card_hover, repolish
from .rendering import apply_surface_role, install_surface_renderer, sync_surface_renderer
from .theme import build_stylesheet


class _GlassPanelTemplateAppearanceMixin:
    def _collect_visual_hosts(self) -> list[QWidget]:
        hosts = [
            self.cards.shell,
            self.cards.hero,
            self.cards.main,
            self.cards.side,
            self.cards.footer,
            self.cards.status,
        ]
        resolved: list[QWidget] = []
        seen: set[int] = set()
        for widget in hosts:
            if not isinstance(widget, QWidget):
                continue
            marker = id(widget)
            if marker in seen:
                continue
            seen.add(marker)
            enable_card_hover(widget)
            resolved.append(widget)
        return resolved


    def _collect_surface_hosts(self) -> list[QWidget]:
        mapped = [
            (self.cards.shell, 'shell', 'glass', 'high', 'rich'),
            (self.cards.hero, 'hero', 'glass', 'high', 'rich'),
            (self.cards.main, 'panel_workspace', 'panel', 'normal', 'normal'),
            (self.cards.side, 'panel_detail', 'panel', 'normal', 'normal'),
            (self.cards.footer, 'footer', 'flat', 'subtle', 'soft'),
            (self.cards.status, 'status', 'flat', 'subtle', 'soft'),
        ]
        resolved: list[QWidget] = []
        seen: set[int] = set()
        for widget, role, variant, emphasis, fx_level in mapped:
            if not isinstance(widget, QWidget):
                continue
            apply_surface_role(
                widget,
                role=role,
                variant=variant,
                emphasis=emphasis,
                fx_level=fx_level,
            )
            marker = id(widget)
            if marker not in seen:
                resolved.append(widget)
                seen.add(marker)
        for panel in self._panels.values():
            apply_surface_role(
                panel,
                role=str(panel.property('visualRole') or f"panel_{panel.property('panelRole') or 'workspace'}"),
                variant='panel',
                emphasis='normal',
                fx_level=str(panel.property('visualFxLevel') or 'normal'),
            )
            marker = id(panel)
            if marker not in seen:
                resolved.append(panel)
                seen.add(marker)
        return resolved


    def _install_surface_renderers(self) -> None:
        for widget in self._surface_hosts:
            install_surface_renderer(widget)


    def _sync_surface_renderers(self) -> None:
        snapshot = self._appearance_snapshot
        if snapshot is None:
            snapshot = AppearanceSnapshot(
                profile=self._current_appearance_profile(),
                effects=self._current_effects_profile(),
                preset_name=None,
                source='template:derived',
            )
        self._surface_hosts = self._collect_surface_hosts()
        for widget in self._surface_hosts:
            sync_surface_renderer(widget, snapshot)


    def set_appearance_coordinator(
        self,
        coordinator: AppearanceCoordinator | None,
        *,
        apply_current: bool = True,
    ) -> None:
        current = getattr(self, '_appearance_coordinator', None)
        if current is coordinator:
            if coordinator is not None and apply_current:
                self.apply_appearance_snapshot(coordinator.snapshot(source='template_bind'))
            return
        if current is not None:
            try:
                current.appearanceChanged.disconnect(self.apply_appearance_snapshot)
            except Exception:
                pass
        self._appearance_coordinator = coordinator
        if coordinator is not None:
            coordinator.appearanceChanged.connect(self.apply_appearance_snapshot)
            if apply_current:
                self.apply_appearance_snapshot(coordinator.snapshot(source='template_bind'))


    def appearance_snapshot(self) -> AppearanceSnapshot | None:
        return self._appearance_snapshot


    def _current_appearance_profile(self) -> AppearanceProfile:
        if self._appearance_snapshot is not None:
            return self._appearance_snapshot.profile.normalized()
        return AppearanceProfile(
            theme_id=self._theme_id,
            density=self._density,
            typography_scale=self._typography_scale,
            tab_density=self._tabs_density,
            tab_variant=self._tabs_variant,
            border_strength_scale=self._border_strength_scale,
            surface_opacity_scale=self._surface_opacity_scale,
            blur_intensity_scale=self._blur_intensity_scale,
            elevation_scale=self._elevation_scale,
            corner_radius_scale=self._corner_radius_scale,
        ).normalized()


    def _current_effects_profile(self) -> EffectsProfile:
        if self._appearance_snapshot is not None:
            return self._appearance_snapshot.effects.normalized()
        return EffectsProfile.from_appearance(self._current_appearance_profile())


    def apply_appearance_bundle(self, profile: AppearanceProfile, effects: EffectsProfile | None = None) -> None:
        self.apply_appearance_snapshot(
            AppearanceSnapshot(
                profile=profile.normalized(),
                effects=(effects or EffectsProfile.from_appearance(profile)).normalized(),
                preset_name=None,
                source='template_bundle',
            )
        )


    def apply_appearance_snapshot(self, snapshot: AppearanceSnapshot) -> None:
        profile = snapshot.profile.normalized()
        effects = snapshot.effects.normalized()
        self._appearance_sync_guard = True
        try:
            self._appearance_snapshot = AppearanceSnapshot(
                profile=profile,
                effects=effects,
                preset_name=snapshot.preset_name,
                source=snapshot.source,
            )
            self._theme_id = profile.theme_id
            self._density = profile.density
            self._typography_scale = profile.typography_scale
            self._tabs_density = profile.tab_density
            self._tabs_variant = profile.tab_variant
            self._border_strength_scale = profile.border_strength_scale
            self._surface_opacity_scale = profile.surface_opacity_scale
            self._blur_intensity_scale = profile.blur_intensity_scale
            self._elevation_scale = profile.elevation_scale
            self._corner_radius_scale = profile.corner_radius_scale
            if self.workspace_tabs is not None:
                self.workspace_tabs.set_tab_density(self._tabs_density)
                self.workspace_tabs.set_tab_variant(self._tabs_variant)
            self._apply_theme_stylesheet()
            self._apply_visual_effects()
        finally:
            self._appearance_sync_guard = False


    def _apply_visual_effects(self) -> None:
        profile = self._current_appearance_profile()
        effects = self._current_effects_profile()
        tokens = resolve_appearance_tokens(profile, effects)
        self.setProperty("themeId", profile.theme_id)
        backdrop = getattr(self, '_glass_backdrop', None)
        if backdrop is not None and hasattr(backdrop, 'apply_appearance'):
            try:
                backdrop.apply_appearance(profile, effects)
            except Exception:
                pass
        elif backdrop is not None and hasattr(backdrop, 'apply_theme'):
            try:
                backdrop.apply_theme(profile.theme_id)
            except Exception:
                pass
        shadow_enabled = bool(effects.shadow_enabled and tokens.elevation_scale > 0.0)
        for widget in getattr(self, '_visual_hosts', ()):
            widget.setProperty("themeId", profile.theme_id)
            apply_shadow(
                widget,
                blur=tokens.shadow_blur,
                x_offset=0.0,
                y_offset=tokens.shadow_offset_y,
                alpha=tokens.shadow_alpha,
                enabled=shadow_enabled,
            )
            widget.setProperty('glowIntensity', tokens.glow_intensity)
            widget.setProperty('neonIntensity', tokens.neon_intensity)
            widget.setProperty('cornerRadiusScale', tokens.corner_radius_scale)
            widget.setProperty('visualDensity', tokens.density)
            repolish(widget, recursive=False)
        self._sync_surface_renderers()
        repolish(self, recursive=False)


    def _apply_theme_stylesheet(self) -> None:
        if not self._apply_stylesheet:
            return
        self.setProperty("themeId", self._theme_id)
        for widget in (self.cards.shell, self.cards.hero, self.cards.main, self.cards.side, self.cards.footer, self.cards.status):
            if isinstance(widget, QWidget):
                widget.setProperty("themeId", self._theme_id)
        self.setStyleSheet(
            build_stylesheet(
                self._theme_id,
                density=self._density,
                typography_scale=self._typography_scale,
                tab_density=self._tabs_density,
                tab_variant=self._tabs_variant,
                border_strength_scale=self._border_strength_scale,
                surface_opacity_scale=self._surface_opacity_scale,
            )
        )
        backdrop = getattr(self, "_glass_backdrop", None)
        if backdrop is not None and hasattr(backdrop, "apply_appearance"):
            try:
                backdrop.apply_appearance(self._current_appearance_profile(), self._current_effects_profile())
            except Exception:
                pass
        elif backdrop is not None and hasattr(backdrop, "apply_theme"):
            try:
                backdrop.apply_theme(self._theme_id)
            except Exception:
                pass


    def set_theme(self, theme_id: str) -> None:
        self._theme_id = str(theme_id or DEFAULT_THEME_ID)
        if self._appearance_coordinator is not None and not self._appearance_sync_guard:
            self._appearance_coordinator.update_profile(theme_id=self._theme_id, source='template:set_theme')
            return
        self._apply_theme_stylesheet()
        self._apply_visual_effects()


    def set_density(self, density: str) -> None:
        self._density = str(density or "comfortable")
        if self._appearance_coordinator is not None and not self._appearance_sync_guard:
            self._appearance_coordinator.update_profile(density=self._density, source='template:set_density')
            return
        self._apply_theme_stylesheet()
        self._apply_visual_effects()


    def set_typography_scale(self, scale: str) -> None:
        self._typography_scale = str(scale or "md")
        if self._appearance_coordinator is not None and not self._appearance_sync_guard:
            self._appearance_coordinator.update_profile(typography_scale=self._typography_scale, source='template:set_typography_scale')
            return
        self._apply_theme_stylesheet()
        self._apply_visual_effects()


    def set_tab_placement(self, placement: str) -> None:
        self._tabs_placement = str(placement or "top")
        if self.workspace_tabs is not None:
            self.workspace_tabs.set_tab_placement(self._tabs_placement)


    def set_tab_variant(self, variant: str) -> None:
        self._tabs_variant = str(variant or "glass")
        if self.workspace_tabs is not None:
            self.workspace_tabs.set_tab_variant(self._tabs_variant)
        if self._appearance_coordinator is not None and not self._appearance_sync_guard:
            self._appearance_coordinator.update_profile(tab_variant=self._tabs_variant, source='template:set_tab_variant')
            return
        self._apply_theme_stylesheet()
        self._apply_visual_effects()


    def set_tab_density(self, density: str) -> None:
        self._tabs_density = str(density or "comfortable")
        if self.workspace_tabs is not None:
            self.workspace_tabs.set_tab_density(self._tabs_density)
        if self._appearance_coordinator is not None and not self._appearance_sync_guard:
            self._appearance_coordinator.update_profile(tab_density=self._tabs_density, source='template:set_tab_density')
            return
        self._apply_theme_stylesheet()
        self._apply_visual_effects()


    def set_tab_icon_mode(self, icon_mode: str) -> None:
        self._tabs_icon_mode = str(icon_mode or "icon_text")
        if self.workspace_tabs is not None:
            self.workspace_tabs.set_tab_icon_mode(self._tabs_icon_mode)


    def set_hide_single_tab_bar(self, enabled: bool) -> None:
        self._tabs_hide_single = bool(enabled)
        if self.workspace_tabs is not None:
            self.workspace_tabs.set_hide_if_single_visible(enabled)


    def set_title(self, title: str) -> None:
        self._title = str(title)
        if self._title_label is not None:
            self._title_label.setText(self._title)


    def set_subtitle(self, subtitle: str) -> None:
        self._subtitle = str(subtitle)
        if self._subtitle_label is not None:
            self._subtitle_label.setText(self._subtitle)


    def set_eyebrow(self, eyebrow: str) -> None:
        self._eyebrow = str(eyebrow)
        if self._eyebrow_label is not None:
            self._eyebrow_label.setText(self._eyebrow)


    def set_status_text(self, text: str | None) -> None:
        if self._status_label is None:
            return
        value = (text or "").strip()
        if value:
            self._status_label.setText(value)
            self._status_label.show()
            self.cards.status.show()
            return
        self._status_label.hide()
        self.cards.status.hide()


    def set_side_visible(self, visible: bool) -> None:
        self.cards.side.setVisible(bool(visible))
        self.layout_controller.set_collapsed("main_side", 1, not bool(visible))


    def set_footer_visible(self, visible: bool) -> None:
        self.cards.footer.setVisible(bool(visible))


    def set_status_visible(self, visible: bool) -> None:
        self.cards.status.setVisible(bool(visible))


    def set_submit_enabled(self, enabled: bool) -> None:
        if self.actions.submit_button is not None:
            self.actions.submit_button.setEnabled(bool(enabled))


    def bind_cancel(self, callback: Callable[[], None]) -> None:
        if self.actions.cancel_button is not None:
            self.actions.cancel_button.clicked.connect(callback)


    def bind_submit(self, callback: Callable[[], None]) -> None:
        if self.actions.submit_button is not None:
            self.actions.submit_button.clicked.connect(callback)


    def add_footer_action(
        self,
        text: str,
        variant: str = "secondary",
        *,
        align: str = "right",
        on_click: Callable[[], None] | None = None,
        minimum_width: int | None = None,
        icon_name: str | None = None,
    ) -> QPushButton:
        self.cards.footer.show()
        button = create_button(
            text,
            variant,
            on_click=on_click,
            parent=self.cards.footer,
            minimum_width=minimum_width,
            icon_name=icon_name,
        )
        if align.strip().lower() == "left":
            self.slots.footer_slot.insertWidget(0, button, 0, Qt.AlignLeft)
        else:
            self.slots.footer_slot.addWidget(button, 0, Qt.AlignRight)
        return button

__all__ = ["_GlassPanelTemplateAppearanceMixin"]
