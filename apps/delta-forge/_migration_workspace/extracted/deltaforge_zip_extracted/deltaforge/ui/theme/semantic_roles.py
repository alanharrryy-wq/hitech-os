from __future__ import annotations

from dataclasses import dataclass

from ui.theme.tokens import ThemeTokens


@dataclass(frozen=True)
class SurfaceRoles:
    app_canvas: str
    panel_default: str
    panel_elevated: str
    panel_overlay: str
    section_subtle: str
    section_strong: str
    list_row_hover: str
    list_row_selected: str
    separator: str


@dataclass(frozen=True)
class TextRoles:
    title: str
    body: str
    secondary: str
    muted: str
    inverse: str
    link: str
    disabled: str


@dataclass(frozen=True)
class ActionRoles:
    primary_fill: str
    primary_fill_hover: str
    primary_fill_pressed: str
    primary_text: str
    secondary_fill: str
    secondary_fill_hover: str
    secondary_fill_pressed: str
    secondary_text: str
    ghost_hover: str
    ghost_pressed: str
    ghost_text: str


@dataclass(frozen=True)
class FeedbackRoles:
    success_fill: str
    warning_fill: str
    danger_fill: str
    info_fill: str
    success_text: str
    warning_text: str
    danger_text: str
    info_text: str


@dataclass(frozen=True)
class FieldRoles:
    fill: str
    fill_hover: str
    fill_focus: str
    stroke: str
    stroke_focus: str
    placeholder: str


@dataclass(frozen=True)
class ThemeRoles:
    surface: SurfaceRoles
    text: TextRoles
    actions: ActionRoles
    feedback: FeedbackRoles
    field: FieldRoles
    focus_ring: str
    scrim: str


def build_semantic_roles(tokens: ThemeTokens) -> ThemeRoles:
    colors = tokens.colors

    def c(key: str, default: str) -> str:
        return str(colors.get(key, default))

    return ThemeRoles(
        surface=SurfaceRoles(
            app_canvas=c("canvas", "#0b1118"),
            panel_default=c("panel", "#151f2b"),
            panel_elevated=c("panel_elevated", "#1c2a3a"),
            panel_overlay=c("panel_overlay", "#223244"),
            section_subtle=c("surface_subtle", "#162230"),
            section_strong=c("surface_strong", "#223447"),
            list_row_hover=c("surface_strong", "#223447"),
            list_row_selected=c("selection_fill", "#1f4564"),
            separator=c("stroke_soft", "#30465d"),
        ),
        text=TextRoles(
            title=c("text_primary", c("text", "#e5edf6")),
            body=c("text_primary", c("text", "#e5edf6")),
            secondary=c("text_secondary", c("text_soft", "#9fb2c8")),
            muted=c("text_muted", "#7d91a8"),
            inverse=c("text_inverse", "#081119"),
            link=c("accent", "#57a6ff"),
            disabled=c("text_muted", "#7d91a8"),
        ),
        actions=ActionRoles(
            primary_fill=c("accent", "#57a6ff"),
            primary_fill_hover=c("accent_hover", "#79c7ff"),
            primary_fill_pressed=c("accent_pressed", "#3a8be8"),
            primary_text=c("text_inverse", "#081119"),
            secondary_fill=c("surface_strong", "#223447"),
            secondary_fill_hover=c("panel_overlay", "#223244"),
            secondary_fill_pressed=c("stroke_soft", "#30465d"),
            secondary_text=c("text_primary", c("text", "#e5edf6")),
            ghost_hover=c("surface_strong", "#223447"),
            ghost_pressed=c("stroke_soft", "#30465d"),
            ghost_text=c("text_secondary", c("text_soft", "#9fb2c8")),
        ),
        feedback=FeedbackRoles(
            success_fill=c("success", c("positive", "#36c57a")),
            warning_fill=c("warning", "#f4b45a"),
            danger_fill=c("danger", "#ff6f75"),
            info_fill=c("info", c("accent", "#57a6ff")),
            success_text=c("text_inverse", "#081119"),
            warning_text=c("text_inverse", "#081119"),
            danger_text=c("text_inverse", "#081119"),
            info_text=c("text_inverse", "#081119"),
        ),
        field=FieldRoles(
            fill=c("surface_subtle", "#162230"),
            fill_hover=c("panel_elevated", "#1c2a3a"),
            fill_focus=c("panel_overlay", "#223244"),
            stroke=c("stroke_soft", "#30465d"),
            stroke_focus=c("accent", "#57a6ff"),
            placeholder=c("text_muted", "#7d91a8"),
        ),
        focus_ring=c("focus_ring", c("focus", "#4da6ff")),
        scrim=c("scrim", "rgba(4, 11, 18, 185)"),
    )
