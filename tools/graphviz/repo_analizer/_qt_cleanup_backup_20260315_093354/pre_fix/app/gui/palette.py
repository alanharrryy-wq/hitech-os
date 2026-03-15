from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemePalette:
    name: str
    bg: str
    panel: str
    panel_alt: str
    panel_deep: str
    border: str
    text: str
    text_muted: str
    accent: str
    accent_hover: str
    accent_soft: str
    selection: str
    selection_soft: str
    warning: str
    success: str
    input_bg: str
    input_fg: str
    input_border: str
    code_bg: str
    code_fg: str
    code_line_active: str
    code_match_bg: str
    code_match_fg: str
    menu_bg: str
    menu_fg: str
    menu_active_bg: str
    menu_active_fg: str
    list_bg: str
    list_fg: str
    scrollbar_trough: str


DARK_GRAPHITE = ThemePalette(
    name='dark_graphite',
    bg='#1b1d21',
    panel='#23262b',
    panel_alt='#2a2f36',
    panel_deep='#17191d',
    border='#3a404a',
    text='#e8edf3',
    text_muted='#aeb7c3',
    accent='#4f8cff',
    accent_hover='#76a8ff',
    accent_soft='#223b67',
    selection='#355f9e',
    selection_soft='#2a3d58',
    warning='#f7d774',
    success='#53c58a',
    input_bg='#202329',
    input_fg='#edf2f8',
    input_border='#49525f',
    code_bg='#15181d',
    code_fg='#eef3f8',
    code_line_active='#1d3556',
    code_match_bg='#f2d479',
    code_match_fg='#141518',
    menu_bg='#252931',
    menu_fg='#ebf0f6',
    menu_active_bg='#3d6ec0',
    menu_active_fg='#ffffff',
    list_bg='#1d2026',
    list_fg='#e7edf4',
    scrollbar_trough='#1a1d22',
)


DEFAULT_THEME = DARK_GRAPHITE
