from __future__ import annotations

from typing import Dict

from ui.theme.semantic_roles import ThemeRoles


class ThemePalette:
    def __init__(self, roles: ThemeRoles) -> None:
        self._roles = roles

    @property
    def roles(self) -> ThemeRoles:
        return self._roles

    def as_dict(self) -> Dict[str, str]:
        surface = self._roles.surface
        text = self._roles.text
        actions = self._roles.actions
        feedback = self._roles.feedback
        field = self._roles.field
        return {
            'surface.app_canvas': surface.app_canvas,
            'surface.panel_default': surface.panel_default,
            'surface.panel_elevated': surface.panel_elevated,
            'surface.panel_overlay': surface.panel_overlay,
            'surface.section_subtle': surface.section_subtle,
            'surface.section_strong': surface.section_strong,
            'surface.list_row_hover': surface.list_row_hover,
            'surface.list_row_selected': surface.list_row_selected,
            'surface.separator': surface.separator,
            'text.title': text.title,
            'text.body': text.body,
            'text.secondary': text.secondary,
            'text.muted': text.muted,
            'text.inverse': text.inverse,
            'text.link': text.link,
            'text.disabled': text.disabled,
            'actions.primary_fill': actions.primary_fill,
            'actions.primary_fill_hover': actions.primary_fill_hover,
            'actions.primary_fill_pressed': actions.primary_fill_pressed,
            'actions.primary_text': actions.primary_text,
            'actions.secondary_fill': actions.secondary_fill,
            'actions.secondary_fill_hover': actions.secondary_fill_hover,
            'actions.secondary_fill_pressed': actions.secondary_fill_pressed,
            'actions.secondary_text': actions.secondary_text,
            'actions.ghost_hover': actions.ghost_hover,
            'actions.ghost_pressed': actions.ghost_pressed,
            'actions.ghost_text': actions.ghost_text,
            'feedback.success_fill': feedback.success_fill,
            'feedback.warning_fill': feedback.warning_fill,
            'feedback.danger_fill': feedback.danger_fill,
            'feedback.info_fill': feedback.info_fill,
            'feedback.success_text': feedback.success_text,
            'feedback.warning_text': feedback.warning_text,
            'feedback.danger_text': feedback.danger_text,
            'feedback.info_text': feedback.info_text,
            'field.fill': field.fill,
            'field.fill_hover': field.fill_hover,
            'field.fill_focus': field.fill_focus,
            'field.stroke': field.stroke,
            'field.stroke_focus': field.stroke_focus,
            'field.placeholder': field.placeholder,
            'focus_ring': self._roles.focus_ring,
            'scrim': self._roles.scrim,
        }
