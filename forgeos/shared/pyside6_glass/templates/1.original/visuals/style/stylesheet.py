from __future__ import annotations

from functools import lru_cache

from ..common.color import mix_hex, with_alpha
from ..common.helpers import clean_text
from ..themes.catalog import resolve_theme
from .scale import resolve_scale


def is_silver_theme_id(theme_id: str | None) -> bool:
    lowered = clean_text(theme_id).lower()
    return any(tag in lowered for tag in ("silver", "frost", "argent", "mercury"))


def _qss_vertical_gradient(top: str, bottom: str) -> str:
    return (
        "qlineargradient(x1:0, y1:0, x2:0, y2:1, "
        f"stop:0 {top}, stop:0.55 {top}, stop:1 {bottom})"
    )


def _qss_horizontal_gradient(left: str, right: str) -> str:
    return (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        f"stop:0 {left}, stop:1 {right})"
    )


@lru_cache(maxsize=32)
def build_stylesheet(theme_id: str, scale_id: str = "100") -> str:
    render = resolve_theme(theme_id)
    scale = resolve_scale(scale_id)
    s = scale.px

    t = render.tokens
    dark = render.is_dark
    silver_theme = is_silver_theme_id(render.theme_id)

    dialog_bg = "transparent"
    shell_top = with_alpha(mix_hex(t["header_fill"], t["legend_fill"], 0.42 if dark else 0.16), 0.64 if dark else 0.76)
    shell_bottom = with_alpha(mix_hex(t["canvas_bg"], t["header_fill"], 0.26 if dark else 0.08), 0.52 if dark else 0.68)
    shell_border = with_alpha(mix_hex(t["focus"], t["legend_stroke"], 0.24 if dark else 0.10), 0.20 if dark else 0.30)
    shell_rim = with_alpha(t["focus"], 0.26 if dark else 0.24)

    hero_top = with_alpha(mix_hex(t["focus"], t["header_fill"], 0.14 if dark else 0.04), 0.24 if dark else 0.52)
    hero_bottom = with_alpha(mix_hex(t["legend_fill"], t["canvas_bg"], 0.18 if dark else 0.05), 0.58 if dark else 0.70)
    hero_border = with_alpha(t["focus"], 0.26 if dark else 0.32)

    card_top = with_alpha(mix_hex(t["legend_fill"], t["header_fill"], 0.12 if dark else 0.04), 0.54 if dark else 0.68)
    card_bottom = with_alpha(mix_hex(t["canvas_bg"], t["legend_fill"], 0.20 if dark else 0.05), 0.42 if dark else 0.58)
    muted_top = with_alpha(mix_hex(t["canvas_bg"], t["legend_fill"], 0.26 if dark else 0.06), 0.38 if dark else 0.56)
    muted_bottom = with_alpha(mix_hex(t["canvas_bg"], t["header_fill"], 0.18 if dark else 0.05), 0.34 if dark else 0.50)
    footer_top = with_alpha(mix_hex(t["header_fill"], t["canvas_bg"], 0.18 if dark else 0.06), 0.40 if dark else 0.56)
    footer_bottom = with_alpha(mix_hex(t["canvas_bg"], t["legend_fill"], 0.18 if dark else 0.06), 0.32 if dark else 0.48)
    card_border = with_alpha(t["legend_stroke"], 0.20 if dark else 0.32)
    muted_border = with_alpha(t["header_stroke"], 0.16 if dark else 0.26)
    line = with_alpha(t["header_stroke"], 0.08 if dark else 0.14)
    line_glow = with_alpha(t["focus"], 0.24 if dark else 0.16)

    title = t["header_title"]
    subtitle = mix_hex(t["header_meta"], t["text_soft"], 0.18)
    section = t["header_title"]
    panel_title = mix_hex(t["header_title"], t["focus"], 0.08 if dark else 0.14)
    field = mix_hex(t["focus"], t["chip_light"], 0.74 if dark else 0.26)
    eyebrow = mix_hex(t["focus"], t["header_meta"], 0.42 if dark else 0.26)
    hint = t["footer_text"]
    value = t["text_main"]
    mono = t["text_soft"]
    chrome_title = mix_hex(t["header_title"], t["text_main"], 0.24 if dark else 0.12)
    chrome_icon = mix_hex(t["focus"], t["chip_light"], 0.56 if dark else 0.24)
    chrome_bg_top = with_alpha(mix_hex(t["header_fill"], t["canvas_bg"], 0.26 if dark else 0.06), 0.58 if dark else 0.74)
    chrome_bg_bottom = with_alpha(mix_hex(t["legend_fill"], t["canvas_bg"], 0.20 if dark else 0.04), 0.42 if dark else 0.60)
    chrome_border = with_alpha(t["legend_stroke"], 0.16 if dark else 0.26)
    chrome_button_fg = mix_hex(t["text_main"], t["chip_light"], 0.18 if dark else 0.10)
    chrome_button_bg = with_alpha(mix_hex(t["canvas_bg"], t["legend_fill"], 0.20 if dark else 0.06), 0.46 if dark else 0.68)
    chrome_button_border = with_alpha(t["header_stroke"], 0.16 if dark else 0.26)
    chrome_button_hover = with_alpha(t["focus"], 0.18 if dark else 0.14)
    chrome_close_hover = with_alpha(t["warning_fill"], 0.28 if dark else 0.24)
    chrome_close_border = with_alpha(t["warning_stroke"], 0.36 if dark else 0.38)

    neutral_chip_text = t["text_soft"] if dark else mix_hex(t["header_meta"], t["text_main"], 0.18)
    neutral_chip_bg = with_alpha(mix_hex(t["legend_fill"], t["canvas_bg"], 0.24 if dark else 0.08), 0.34 if dark else 0.64)
    neutral_chip_border = with_alpha(t["muted_stroke"], 0.18 if dark else 0.24)
    good_chip_text = mix_hex(t["badge_out"], t["chip_light"], 0.72 if dark else 0.40)
    good_chip_bg = with_alpha(t["badge_out"], 0.12 if dark else 0.16)
    good_chip_border = with_alpha(t["badge_out"], 0.24 if dark else 0.30)
    warn_chip_text = mix_hex(t["warning_stroke"], t["chip_light"], 0.70 if dark else 0.24)
    warn_chip_bg = with_alpha(t["warning_stroke"], 0.12 if dark else 0.18)
    warn_chip_border = with_alpha(t["warning_stroke"], 0.24 if dark else 0.30)
    accent_chip_text = mix_hex(t["focus"], t["chip_light"], 0.78 if dark else 0.30)
    accent_chip_bg = with_alpha(t["focus"], 0.14 if dark else 0.16)
    accent_chip_border = with_alpha(t["focus"], 0.30 if dark else 0.34)

    input_bg = with_alpha(mix_hex(t["canvas_bg"], t["legend_fill"], 0.18 if dark else 0.04), 0.58 if dark else 0.72)
    input_fg = value
    input_border = with_alpha(t["legend_stroke"], 0.16 if dark else 0.30)
    input_hover = with_alpha(t["focus"], 0.44 if dark else 0.50)
    input_focus = with_alpha(t["focus"], 0.84 if dark else 0.82)
    input_focus_bg = with_alpha(mix_hex(t["canvas_bg"], t["header_fill"], 0.16 if dark else 0.06), 0.70 if dark else 0.82)
    input_focus_glow = with_alpha(t["focus"], 0.26 if dark else 0.22)
    input_disabled_fg = with_alpha(t["muted_text"], 0.82)
    input_disabled_bg = with_alpha(mix_hex(t["canvas_bg"], t["legend_fill"], 0.12 if dark else 0.04), 0.30 if dark else 0.58)
    input_disabled_border = with_alpha(t["legend_stroke"], 0.08 if dark else 0.16)
    dropdown_bg = with_alpha(mix_hex(t["legend_fill"], t["canvas_bg"], 0.10 if dark else 0.03), 0.82 if dark else 0.88)
    selection_bg = t["focus"]
    selection_fg = t["chip_light"]

    primary_top = mix_hex(t["focus"], t["chip_light"], 0.04 if dark else 0.12)
    primary_bottom = mix_hex(t["focus"], t["canvas_bg"], 0.12 if dark else 0.04)
    primary_border = with_alpha(t["focus"], 0.36 if dark else 0.40)
    primary_hover_top = mix_hex(t["focus"], t["chip_light"], 0.10 if dark else 0.16)
    primary_hover_bottom = mix_hex(t["focus"], t["chip_light"], 0.04 if dark else 0.10)

    secondary_top = with_alpha(mix_hex(t["header_fill"], t["legend_fill"], 0.16 if dark else 0.06), 0.62 if dark else 0.78)
    secondary_bottom = with_alpha(mix_hex(t["canvas_bg"], t["header_fill"], 0.18 if dark else 0.05), 0.46 if dark else 0.64)
    secondary_border = with_alpha(t["legend_stroke"], 0.16 if dark else 0.26)
    secondary_hover_top = with_alpha(mix_hex(t["focus"], t["legend_fill"], 0.10 if dark else 0.05), 0.72 if dark else 0.86)
    secondary_hover_bottom = with_alpha(mix_hex(t["focus"], t["canvas_bg"], 0.10 if dark else 0.04), 0.52 if dark else 0.68)

    success_top = mix_hex(t["badge_out"], t["chip_light"], 0.06 if dark else 0.12)
    success_bottom = mix_hex(t["badge_out"], t["canvas_bg"], 0.16 if dark else 0.04)
    success_border = with_alpha(t["badge_out"], 0.28 if dark else 0.30)
    success_hover_top = mix_hex(t["badge_out"], t["chip_light"], 0.12 if dark else 0.18)
    success_hover_bottom = mix_hex(t["badge_out"], t["chip_light"], 0.04 if dark else 0.10)

    danger_top = with_alpha(mix_hex(t["warning_fill"], t["header_fill"], 0.20 if dark else 0.10), 0.64 if dark else 0.76)
    danger_bottom = with_alpha(mix_hex(t["warning_fill"], t["canvas_bg"], 0.26 if dark else 0.08), 0.52 if dark else 0.66)
    danger_border = with_alpha(t["warning_stroke"], 0.22 if dark else 0.28)
    danger_hover_top = with_alpha(mix_hex(t["warning_fill"], t["warning_stroke"], 0.12 if dark else 0.08), 0.74 if dark else 0.84)
    danger_hover_bottom = with_alpha(mix_hex(t["warning_fill"], t["warning_stroke"], 0.20 if dark else 0.12), 0.58 if dark else 0.72)

    disabled_bg = with_alpha(mix_hex(t["header_fill"], t["canvas_bg"], 0.18 if dark else 0.08), 0.34 if dark else 0.56)
    disabled_fg = with_alpha(t["muted_text"], 0.84)
    disabled_border = with_alpha(t["legend_stroke"], 0.06 if dark else 0.16)

    progress_bg = with_alpha(mix_hex(t["canvas_bg"], t["legend_fill"], 0.18 if dark else 0.06), 0.46 if dark else 0.56)
    progress_border = with_alpha(t["legend_stroke"], 0.16 if dark else 0.24)
    progress_text = value
    progress_chunk_start = mix_hex(t["focus"], t["chip_light"], 0.12 if dark else 0.26)
    progress_chunk_mid = mix_hex(t["focus"], "#ffffff", 0.30 if dark else 0.40)
    progress_chunk_end = mix_hex(t["focus"], t["canvas_bg"], 0.20 if dark else 0.10)
    progress_chunk_glow = with_alpha(t["focus"], 0.52 if dark else 0.48)

    scale_selector_bg = with_alpha(mix_hex(t["header_fill"], t["canvas_bg"], 0.20 if dark else 0.08), 0.56 if dark else 0.70)
    scale_selector_border = with_alpha(t["legend_stroke"], 0.18 if dark else 0.24)
    scale_pill_bg = with_alpha(mix_hex(t["canvas_bg"], t["legend_fill"], 0.14 if dark else 0.06), 0.48 if dark else 0.62)
    scale_pill_border = with_alpha(t["header_stroke"], 0.16 if dark else 0.24)
    scale_pill_fg = mono
    scale_active_bg = with_alpha(t["focus"], 0.20 if dark else 0.24)
    scale_active_border = with_alpha(t["focus"], 0.50 if dark else 0.52)
    scale_active_fg = selection_fg

    tooltip_bg = with_alpha(mix_hex(t["header_fill"], t["canvas_bg"], 0.14 if dark else 0.05), 0.94 if dark else 0.98)
    tooltip_border = with_alpha(t["focus"], 0.22 if dark else 0.28)

    if silver_theme:
        shell_top = with_alpha("#eef6ff", 0.06)
        shell_bottom = with_alpha("#94a8c1", 0.03)
        shell_border = with_alpha("#eef8ff", 0.20)
        shell_rim = with_alpha(t["focus"], 0.38)

        hero_top = with_alpha("#eef7ff", 0.08)
        hero_bottom = with_alpha(t["focus"], 0.05)
        hero_border = with_alpha(t["focus"], 0.40)

        card_top = with_alpha("#edf6ff", 0.07)
        card_bottom = with_alpha("#a4b5ca", 0.04)
        muted_top = with_alpha("#e6f1fb", 0.08)
        muted_bottom = with_alpha("#9cb0c8", 0.05)
        footer_top = with_alpha("#eef6ff", 0.08)
        footer_bottom = with_alpha("#9caec5", 0.05)
        card_border = with_alpha("#eaf6ff", 0.16)
        muted_border = with_alpha("#eaf6ff", 0.12)
        line = with_alpha("#d8e7f6", 0.12)
        line_glow = with_alpha(t["focus"], 0.20)

        title = "#f5fbff"
        subtitle = "#c1d0df"
        section = "#edf6ff"
        panel_title = "#f0f8ff"
        field = "#95eeff"
        eyebrow = "#7fc8df"
        hint = "#98adc2"
        value = "#e0edf9"
        mono = "#b8cade"
        chrome_title = "#dce8f3"
        chrome_icon = "#86e9ff"
        chrome_bg_top = with_alpha("#edf6ff", 0.05)
        chrome_bg_bottom = with_alpha("#95aac3", 0.03)
        chrome_border = with_alpha("#eef8ff", 0.10)
        chrome_button_fg = "#ebf4ff"
        chrome_button_bg = with_alpha("#0c1520", 0.36)
        chrome_button_border = with_alpha("#eef8ff", 0.08)
        chrome_button_hover = with_alpha(t["focus"], 0.16)
        chrome_close_hover = with_alpha(t["focus"], 0.18)
        chrome_close_border = with_alpha(t["focus"], 0.26)

        neutral_chip_text = "#d7e6f3"
        neutral_chip_bg = with_alpha("#0c1520", 0.30)
        neutral_chip_border = with_alpha("#eef8ff", 0.10)
        good_chip_text = "#d7f3fa"
        good_chip_bg = with_alpha(t["badge_out"], 0.12)
        good_chip_border = with_alpha(t["badge_out"], 0.24)
        warn_chip_text = "#f0e5d4"
        warn_chip_bg = with_alpha(t["warning_stroke"], 0.12)
        warn_chip_border = with_alpha(t["warning_stroke"], 0.24)
        accent_chip_text = "#ecfbff"
        accent_chip_bg = with_alpha(t["focus"], 0.14)
        accent_chip_border = with_alpha(t["focus"], 0.30)

        input_bg = with_alpha("#0a1320", 0.62)
        input_fg = "#eff8ff"
        input_border = with_alpha("#e7f5ff", 0.12)
        input_hover = with_alpha(t["focus"], 0.50)
        input_focus = with_alpha(t["focus"], 0.84)
        input_focus_bg = with_alpha("#0e1824", 0.58)
        input_focus_glow = with_alpha(t["focus"], 0.24)
        input_disabled_fg = with_alpha("#9db0c4", 0.74)
        input_disabled_bg = with_alpha("#0b121c", 0.24)
        input_disabled_border = with_alpha("#e7f5ff", 0.06)
        dropdown_bg = with_alpha("#0f1825", 0.94)
        selection_bg = t["focus"]
        selection_fg = "#08111a"

        primary_top = mix_hex(t["focus"], "#ffffff", 0.20)
        primary_bottom = mix_hex(t["focus"], "#74dcef", 0.08)
        primary_border = with_alpha(t["focus"], 0.40)
        primary_hover_top = mix_hex(t["focus"], "#ffffff", 0.28)
        primary_hover_bottom = mix_hex(t["focus"], "#8cefff", 0.18)

        secondary_top = with_alpha("#edf6ff", 0.08)
        secondary_bottom = with_alpha("#95aac1", 0.04)
        secondary_border = with_alpha("#eef8ff", 0.12)
        secondary_hover_top = with_alpha("#edf6ff", 0.12)
        secondary_hover_bottom = with_alpha(t["focus"], 0.06)

        success_top = primary_top
        success_bottom = primary_bottom
        success_border = with_alpha(t["focus"], 0.28)
        success_hover_top = primary_hover_top
        success_hover_bottom = primary_hover_bottom

        danger_top = with_alpha("#f2f6fb", 0.08)
        danger_bottom = with_alpha("#a6b4c3", 0.05)
        danger_border = with_alpha("#eef8ff", 0.12)
        danger_hover_top = with_alpha("#f2f6fb", 0.12)
        danger_hover_bottom = with_alpha(t["focus"], 0.05)

        disabled_bg = with_alpha("#0d141d", 0.20)
        disabled_fg = with_alpha("#9fb4c7", 0.62)
        disabled_border = with_alpha("#e7f5ff", 0.06)

        progress_bg = with_alpha("#0c1520", 0.38)
        progress_border = with_alpha("#eef8ff", 0.10)
        progress_text = "#e4f0fb"
        progress_chunk_start = mix_hex(t["focus"], "#ffffff", 0.20)
        progress_chunk_mid = mix_hex(t["focus"], "#ffffff", 0.34)
        progress_chunk_end = mix_hex(t["focus"], "#6dd9ee", 0.08)
        progress_chunk_glow = with_alpha(t["focus"], 0.52)

        scale_selector_bg = with_alpha("#0d1723", 0.40)
        scale_selector_border = with_alpha("#e8f6ff", 0.12)
        scale_pill_bg = with_alpha("#0b141f", 0.42)
        scale_pill_border = with_alpha("#e8f6ff", 0.08)
        scale_pill_fg = "#c7d8e8"
        scale_active_bg = with_alpha(t["focus"], 0.18)
        scale_active_border = with_alpha(t["focus"], 0.40)
        scale_active_fg = "#ecfbff"

        tooltip_bg = with_alpha("#0f1825", 0.94)
        tooltip_border = with_alpha(t["focus"], 0.24)

    radius_shell = s(28, 14)
    radius_shell_progress = s(26, 14)
    radius_chrome = s(12, 8)
    radius_hero = s(22, 12)
    radius_card = s(18, 10)
    radius_chip = s(12, 8)
    radius_input = s(14, 8)
    radius_button = s(14, 8)
    radius_progress = max(3, s(4, 3))
    radius_scale = s(13, 8)

    font_title = s(28, 18)
    font_eyebrow = s(10, 9)
    font_window_title = s(12, 10)
    font_window_icon = s(11, 10)
    font_subtitle = s(12, 10)
    font_section = s(15, 12)
    font_panel_title = s(13, 11)
    font_field = s(11, 10)
    font_hint = s(11, 10)
    font_value = s(12, 10)
    font_mono = s(12, 10)
    font_chip = s(11, 10)
    font_button = s(12, 10)
    font_progress = s(10, 9)
    font_scale = s(10, 9)

    input_pad_v = s(10, 6)
    input_pad_h = s(12, 8)
    button_pad_v = s(10, 6)
    button_pad_h = s(16, 10)
    chip_pad_v = s(7, 5)
    chip_pad_h = s(11, 8)

    chrome_btn_w = s(30, 22)
    chrome_btn_h = s(22, 18)
    scale_pill_h = s(24, 18)
    progress_h = max(4, s(5, 4))
    scrollbar_w = max(6, s(8, 6))

    return f"""
    QDialog,
    QMessageBox {{
        background: {dialog_bg};
        color: {value};
        border: none;
    }}

    QWidget#GlassStage,
    QWidget#GlassContent {{
        background: transparent;
        border: none;
    }}

    QFrame#Shell {{
        background: {_qss_vertical_gradient(shell_top, shell_bottom)};
        border: 1px solid {shell_border};
        border-radius: {radius_shell}px;
    }}

    QFrame#Shell:hover {{
        border: 1px solid {shell_rim};
    }}

    QFrame#Shell[variant="progress"] {{
        border-radius: {radius_shell_progress}px;
    }}

    QFrame#WindowChrome {{
        background: {_qss_vertical_gradient(chrome_bg_top, chrome_bg_bottom)};
        border: 1px solid {chrome_border};
        border-radius: {radius_chrome}px;
    }}

    QFrame[card="hero"] {{
        background: {_qss_vertical_gradient(hero_top, hero_bottom)};
        border: 1px solid {hero_border};
        border-radius: {radius_hero}px;
    }}

    QFrame[card="true"] {{
        background: {_qss_vertical_gradient(card_top, card_bottom)};
        border: 1px solid {card_border};
        border-radius: {radius_card}px;
    }}

    QFrame[card="muted"] {{
        background: {_qss_vertical_gradient(muted_top, muted_bottom)};
        border: 1px solid {muted_border};
        border-radius: {radius_card}px;
    }}

    QFrame[card="footer"] {{
        background: {_qss_vertical_gradient(footer_top, footer_bottom)};
        border: 1px solid {muted_border};
        border-radius: {radius_card}px;
    }}

    QFrame[hoverable="true"][hover="true"] {{
        border: 1px solid {input_hover};
    }}

    QFrame[slot="placeholder"] {{
        background: {with_alpha(t["canvas_bg"], 0.22)};
        border: 1px dashed {with_alpha(t["focus"], 0.34)};
        border-radius: {s(14, 8)}px;
    }}

    QFrame#Line {{
        background: {_qss_horizontal_gradient(line_glow, line)};
        min-height: 1px;
        max-height: 1px;
        border-radius: 1px;
        border: none;
    }}

    QLabel[role="title"] {{
        color: {title};
        font-size: {font_title}px;
        font-weight: 760;
        letter-spacing: 0.2px;
    }}

    QLabel[role="eyebrow"] {{
        color: {eyebrow};
        font-size: {font_eyebrow}px;
        font-weight: 700;
        letter-spacing: 1.1px;
        text-transform: uppercase;
    }}

    QLabel[role="window_title"] {{
        color: {chrome_title};
        font-size: {font_window_title}px;
        font-weight: 740;
        letter-spacing: 0.2px;
    }}

    QLabel[role="window_icon"] {{
        color: {chrome_icon};
        font-size: {font_window_icon}px;
        font-weight: 700;
    }}

    QLabel[role="subtitle"] {{
        color: {subtitle};
        font-size: {font_subtitle}px;
        line-height: 1.35em;
    }}

    QLabel[role="section"] {{
        color: {section};
        font-size: {font_section}px;
        font-weight: 720;
    }}

    QLabel[role="panel_title"] {{
        color: {panel_title};
        font-size: {font_panel_title}px;
        font-weight: 720;
    }}

    QLabel[role="field"] {{
        color: {field};
        font-size: {font_field}px;
        font-weight: 720;
        letter-spacing: 0.7px;
        text-transform: uppercase;
    }}

    QLabel[role="hint"] {{
        color: {hint};
        font-size: {font_hint}px;
        line-height: 1.35em;
    }}

    QLabel[role="value"] {{
        color: {value};
        font-size: {font_value}px;
    }}

    QLabel[role="mono"] {{
        color: {mono};
        font-size: {font_mono}px;
        font-family: "Consolas", "Cascadia Code", monospace;
    }}

    QLabel[chip="true"] {{
        border-radius: {radius_chip}px;
        padding: {chip_pad_v}px {chip_pad_h}px;
        font-size: {font_chip}px;
        font-weight: 760;
        letter-spacing: 0.3px;
    }}

    QLabel[chip="true"][tone="neutral"] {{
        color: {neutral_chip_text};
        background: {neutral_chip_bg};
        border: 1px solid {neutral_chip_border};
    }}

    QLabel[chip="true"][tone="good"] {{
        color: {good_chip_text};
        background: {good_chip_bg};
        border: 1px solid {good_chip_border};
    }}

    QLabel[chip="true"][tone="warn"] {{
        color: {warn_chip_text};
        background: {warn_chip_bg};
        border: 1px solid {warn_chip_border};
    }}

    QLabel[chip="true"][tone="accent"] {{
        color: {accent_chip_text};
        background: {accent_chip_bg};
        border: 1px solid {accent_chip_border};
    }}

    QLineEdit,
    QComboBox,
    QMessageBox QLineEdit {{
        background: {input_bg};
        color: {input_fg};
        border: 1px solid {input_border};
        border-radius: {radius_input}px;
        padding: {input_pad_v}px {input_pad_h}px;
        font-size: {font_value}px;
        selection-background-color: {selection_bg};
        selection-color: {selection_fg};
    }}

    QLineEdit:hover,
    QComboBox:hover,
    QMessageBox QLineEdit:hover {{
        border: 1px solid {input_hover};
    }}

    QLineEdit:focus,
    QComboBox:focus,
    QMessageBox QLineEdit:focus {{
        border: 1px solid {input_focus};
        background: {input_focus_bg};
        outline: none;
    }}

    QLineEdit:focus {{
        selection-background-color: {selection_bg};
        selection-color: {selection_fg};
    }}

    QLineEdit[focus="true"],
    QComboBox[focus="true"] {{
        border: 1px solid {input_focus};
    }}

    QLineEdit::placeholder {{
        color: {with_alpha(mono, 0.74)};
    }}

    QLineEdit:disabled,
    QComboBox:disabled,
    QMessageBox QLineEdit:disabled {{
        color: {input_disabled_fg};
        background: {input_disabled_bg};
        border: 1px solid {input_disabled_border};
    }}

    QComboBox::drop-down {{
        border: none;
        width: {s(30, 22)}px;
        background: transparent;
    }}

    QComboBox::down-arrow {{
        image: none;
        width: 0px;
        height: 0px;
        border-left: {s(5, 4)}px solid transparent;
        border-right: {s(5, 4)}px solid transparent;
        border-top: {s(7, 5)}px solid {field};
        margin-right: {s(8, 6)}px;
    }}

    QComboBox QAbstractItemView {{
        background: {dropdown_bg};
        color: {value};
        border: 1px solid {card_border};
        border-radius: {s(12, 8)}px;
        selection-background-color: {selection_bg};
        selection-color: {selection_fg};
        outline: none;
        padding: {s(4, 3)}px;
    }}

    QPushButton,
    QMessageBox QPushButton {{
        min-height: {s(18, 14)}px;
        border-radius: {radius_button}px;
        padding: {button_pad_v}px {button_pad_h}px;
        font-size: {font_button}px;
        font-weight: 760;
        outline: none;
        color: {value};
        background: {_qss_vertical_gradient(secondary_top, secondary_bottom)};
        border: 1px solid {secondary_border};
        text-align: center;
    }}

    QPushButton:hover,
    QMessageBox QPushButton:hover {{
        background: {_qss_vertical_gradient(secondary_hover_top, secondary_hover_bottom)};
        border: 1px solid {input_hover};
    }}

    QPushButton[variant="primary"],
    QMessageBox QPushButton[variant="primary"] {{
        color: {selection_fg};
        background: {_qss_vertical_gradient(primary_top, primary_bottom)};
        border: 1px solid {primary_border};
    }}

    QPushButton[variant="primary"]:hover,
    QMessageBox QPushButton[variant="primary"]:hover {{
        background: {_qss_vertical_gradient(primary_hover_top, primary_hover_bottom)};
        border: 1px solid {input_hover};
    }}

    QPushButton[variant="secondary"] {{
        color: {value};
        background: {_qss_vertical_gradient(secondary_top, secondary_bottom)};
        border: 1px solid {secondary_border};
    }}

    QPushButton[variant="secondary"]:hover {{
        background: {_qss_vertical_gradient(secondary_hover_top, secondary_hover_bottom)};
        border: 1px solid {input_hover};
    }}

    QPushButton[variant="success"] {{
        color: {selection_fg};
        background: {_qss_vertical_gradient(success_top, success_bottom)};
        border: 1px solid {success_border};
    }}

    QPushButton[variant="success"]:hover {{
        background: {_qss_vertical_gradient(success_hover_top, success_hover_bottom)};
        border: 1px solid {good_chip_border};
    }}

    QPushButton[variant="danger"],
    QMessageBox QPushButton[variant="danger"] {{
        color: {value};
        background: {_qss_vertical_gradient(danger_top, danger_bottom)};
        border: 1px solid {danger_border};
    }}

    QPushButton[variant="danger"]:hover,
    QMessageBox QPushButton[variant="danger"]:hover {{
        background: {_qss_vertical_gradient(danger_hover_top, danger_hover_bottom)};
        border: 1px solid {warn_chip_border};
    }}

    QPushButton:disabled,
    QMessageBox QPushButton:disabled {{
        color: {disabled_fg};
        background: {disabled_bg};
        border: 1px solid {disabled_border};
    }}

    QPushButton[chrome="true"] {{
        min-width: {chrome_btn_w}px;
        max-width: {chrome_btn_w}px;
        min-height: {chrome_btn_h}px;
        max-height: {chrome_btn_h}px;
        border-radius: {s(8, 6)}px;
        padding: 0px;
        font-size: {font_window_icon}px;
        font-weight: 760;
        color: {chrome_button_fg};
        background: {chrome_button_bg};
        border: 1px solid {chrome_button_border};
    }}

    QPushButton[chrome="true"]:hover {{
        background: {chrome_button_hover};
        border: 1px solid {input_hover};
    }}

    QPushButton[chrome="true"]:pressed {{
        background: {with_alpha(t["focus"], 0.28 if dark else 0.22)};
        border: 1px solid {input_focus};
    }}

    QPushButton[chrome="true"][chrome_kind="close"]:hover {{
        background: {chrome_close_hover};
        border: 1px solid {chrome_close_border};
    }}

    QFrame[scale_selector="true"] {{
        background: {scale_selector_bg};
        border: 1px solid {scale_selector_border};
        border-radius: {radius_scale}px;
    }}

    QPushButton[scale_pill="true"] {{
        min-height: {scale_pill_h}px;
        border-radius: {s(9, 6)}px;
        background: {scale_pill_bg};
        border: 1px solid {scale_pill_border};
        color: {scale_pill_fg};
        font-size: {font_scale}px;
        font-weight: 720;
        padding: 0px {s(8, 5)}px;
    }}

    QPushButton[scale_pill="true"]:hover {{
        border: 1px solid {input_hover};
    }}

    QPushButton[scale_pill="true"][active="true"] {{
        background: {scale_active_bg};
        border: 1px solid {scale_active_border};
        color: {scale_active_fg};
    }}

    QComboBox[toolbar_theme="true"] {{
        min-height: {scale_pill_h}px;
        border-radius: {s(10, 7)}px;
        padding: 0px {s(10, 6)}px;
        font-size: {font_scale}px;
        font-weight: 700;
        color: {scale_pill_fg};
        background: {scale_pill_bg};
        border: 1px solid {scale_pill_border};
    }}

    QComboBox[toolbar_theme="true"]:hover {{
        border: 1px solid {input_hover};
    }}

    QComboBox[toolbar_theme="true"]:focus {{
        border: 1px solid {scale_active_border};
        background: {scale_selector_bg};
    }}

    QComboBox[toolbar_theme="true"]::drop-down {{
        border: none;
        width: {s(22, 16)}px;
        background: transparent;
    }}

    QComboBox[toolbar_theme="true"]::down-arrow {{
        image: none;
        width: 0px;
        height: 0px;
        border-left: {s(4, 3)}px solid transparent;
        border-right: {s(4, 3)}px solid transparent;
        border-top: {s(6, 4)}px solid {scale_pill_fg};
        margin-right: {s(6, 4)}px;
    }}

    QLabel[role="perf_ghost"] {{
        background: transparent;
        border: none;
        color: {with_alpha(mono, 0.54 if dark else 0.40)};
        font-size: {max(10, font_scale - 1)}px;
        font-weight: 560;
        padding: 0px {s(2, 1)}px 0px {s(2, 1)}px;
        margin-top: {s(1, 1)}px;
    }}

    QLineEdit[readOnly="true"],
    QLabel[role="mono"] {{
        selection-background-color: {selection_bg};
        selection-color: {selection_fg};
    }}

    QProgressBar {{
        min-height: {progress_h}px;
        max-height: {progress_h}px;
        border-radius: {radius_progress}px;
        background: {progress_bg};
        border: 1px solid {progress_border};
        text-align: center;
        color: {progress_text};
        font-size: {font_progress}px;
        font-weight: 760;
        padding: 0px;
    }}

    QProgressBar::chunk {{
        border-radius: {radius_progress}px;
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 {progress_chunk_start},
            stop:0.62 {progress_chunk_mid},
            stop:1 {progress_chunk_end}
        );
        border: 1px solid {progress_chunk_glow};
        margin: 0px;
    }}

    QScrollArea {{
        background: transparent;
        border: none;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: {scrollbar_w}px;
        margin: {s(3, 2)}px 0px {s(3, 2)}px 0px;
    }}

    QScrollBar::handle:vertical {{
        background: {with_alpha(t["legend_stroke"], 0.28)};
        border-radius: {max(3, s(4, 3))}px;
        min-height: {s(28, 18)}px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {with_alpha(t["focus"], 0.36)};
    }}

    QScrollBar:horizontal {{
        background: transparent;
        height: {scrollbar_w}px;
        margin: 0px {s(3, 2)}px 0px {s(3, 2)}px;
    }}

    QScrollBar::handle:horizontal {{
        background: {with_alpha(t["legend_stroke"], 0.28)};
        border-radius: {max(3, s(4, 3))}px;
        min-width: {s(28, 18)}px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background: {with_alpha(t["focus"], 0.36)};
    }}

    QScrollBar::add-line,
    QScrollBar::sub-line,
    QScrollBar::add-page,
    QScrollBar::sub-page {{
        background: transparent;
        border: none;
        width: 0px;
        height: 0px;
    }}

    QToolTip {{
        background: {tooltip_bg};
        color: {value};
        border: 1px solid {tooltip_border};
        border-radius: {s(10, 7)}px;
        padding: {s(6, 4)}px {s(8, 5)}px;
    }}
    """.strip()
