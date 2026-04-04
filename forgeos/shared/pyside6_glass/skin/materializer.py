from __future__ import annotations

from ..contracts import (
    DEFAULT_THEME_ID,
    GLASS_DENSITY,
    GLASS_RADIUS,
    GLASS_TYPOGRAPHY,
    SUPPORTED_DENSITY,
    SUPPORTED_TAB_DENSITY,
    SUPPORTED_TAB_VARIANTS,
    SUPPORTED_TYPOGRAPHY_SCALE,
)
from .chrome_spec import build_chrome_spec
from .palette_registry import get_palette
from .surface_spec import build_surface_material_spec


def _choice(value: str, allowed: tuple[str, ...], fallback: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in allowed:
        return normalized
    return fallback


def _coerce_typography_scale(scale: str) -> str:
    return _choice(scale, SUPPORTED_TYPOGRAPHY_SCALE, "md")


def _coerce_density(density: str) -> str:
    return _choice(density, SUPPORTED_DENSITY, "comfortable")


def _coerce_tab_density(value: str) -> str:
    return _choice(value, SUPPORTED_TAB_DENSITY, "comfortable")


def _coerce_tab_variant(value: str) -> str:
    return _choice(value, SUPPORTED_TAB_VARIANTS, "glass")


def _sizes_for_scale(scale: str) -> dict[str, int]:
    if scale == "sm":
        return {
            "display": GLASS_TYPOGRAPHY.display_sm,
            "title": GLASS_TYPOGRAPHY.title_sm,
            "subtitle": GLASS_TYPOGRAPHY.subtitle_sm,
            "section": GLASS_TYPOGRAPHY.section_sm,
            "body": GLASS_TYPOGRAPHY.body_sm,
            "body_strong": GLASS_TYPOGRAPHY.body_strong_sm,
            "label": GLASS_TYPOGRAPHY.label_sm,
            "caption": GLASS_TYPOGRAPHY.caption_sm,
            "micro": GLASS_TYPOGRAPHY.microcopy_sm,
            "code": GLASS_TYPOGRAPHY.code_sm,
        }
    if scale == "lg":
        return {
            "display": GLASS_TYPOGRAPHY.display_md + 2,
            "title": GLASS_TYPOGRAPHY.title_lg,
            "subtitle": GLASS_TYPOGRAPHY.subtitle_lg,
            "section": GLASS_TYPOGRAPHY.section_lg,
            "body": GLASS_TYPOGRAPHY.body_lg,
            "body_strong": GLASS_TYPOGRAPHY.body_strong_lg,
            "label": GLASS_TYPOGRAPHY.label_lg,
            "caption": GLASS_TYPOGRAPHY.caption_lg,
            "micro": GLASS_TYPOGRAPHY.microcopy_lg,
            "code": GLASS_TYPOGRAPHY.code_lg,
        }
    if scale == "xl":
        return {
            "display": GLASS_TYPOGRAPHY.display_lg,
            "title": GLASS_TYPOGRAPHY.title_lg + 2,
            "subtitle": GLASS_TYPOGRAPHY.subtitle_lg + 1,
            "section": GLASS_TYPOGRAPHY.section_lg + 1,
            "body": GLASS_TYPOGRAPHY.body_lg + 1,
            "body_strong": GLASS_TYPOGRAPHY.body_strong_lg + 1,
            "label": GLASS_TYPOGRAPHY.label_lg + 1,
            "caption": GLASS_TYPOGRAPHY.caption_lg + 1,
            "micro": GLASS_TYPOGRAPHY.microcopy_lg + 1,
            "code": GLASS_TYPOGRAPHY.code_lg + 1,
        }
    return {
        "display": GLASS_TYPOGRAPHY.display_md,
        "title": GLASS_TYPOGRAPHY.title_md,
        "subtitle": GLASS_TYPOGRAPHY.subtitle_md,
        "section": GLASS_TYPOGRAPHY.section_md,
        "body": GLASS_TYPOGRAPHY.body_md,
        "body_strong": GLASS_TYPOGRAPHY.body_strong_md,
        "label": GLASS_TYPOGRAPHY.label_md,
        "caption": GLASS_TYPOGRAPHY.caption_md,
        "micro": GLASS_TYPOGRAPHY.microcopy_md,
        "code": GLASS_TYPOGRAPHY.code_md,
    }


def _density_values(density: str) -> dict[str, int]:
    if density == "compact":
        return {
            "input_y": GLASS_DENSITY.input_y_compact,
            "button_y": GLASS_DENSITY.button_y_compact,
            "panel_padding": GLASS_DENSITY.panel_padding_compact,
            "tab_x": GLASS_DENSITY.tab_padding_x_compact,
            "tab_y": GLASS_DENSITY.tab_padding_y_compact,
        }
    if density == "cozy":
        return {
            "input_y": GLASS_DENSITY.input_y_cozy,
            "button_y": GLASS_DENSITY.button_y_cozy,
            "panel_padding": GLASS_DENSITY.panel_padding_cozy,
            "tab_x": GLASS_DENSITY.tab_padding_x_cozy,
            "tab_y": GLASS_DENSITY.tab_padding_y_cozy,
        }
    if density == "extended":
        return {
            "input_y": GLASS_DENSITY.input_y_extended,
            "button_y": GLASS_DENSITY.button_y_extended,
            "panel_padding": GLASS_DENSITY.panel_padding_extended,
            "tab_x": GLASS_DENSITY.tab_padding_x_extended,
            "tab_y": GLASS_DENSITY.tab_padding_y_extended,
        }
    if density == "spacious":
        return {
            "input_y": GLASS_DENSITY.input_y_spacious,
            "button_y": GLASS_DENSITY.button_y_spacious,
            "panel_padding": GLASS_DENSITY.panel_padding_spacious,
            "tab_x": GLASS_DENSITY.tab_padding_x_extended + 1,
            "tab_y": GLASS_DENSITY.tab_padding_y_extended + 1,
        }
    return {
        "input_y": GLASS_DENSITY.input_y_comfortable,
        "button_y": GLASS_DENSITY.button_y_comfortable,
        "panel_padding": GLASS_DENSITY.panel_padding_comfortable,
        "tab_x": GLASS_DENSITY.tab_padding_x_comfortable,
        "tab_y": GLASS_DENSITY.tab_padding_y_comfortable,
    }


def _gradient(top: str, bottom: str) -> str:
    return f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {top}, stop:1 {bottom})"


def build_stylesheet(
    theme_id: str = DEFAULT_THEME_ID,
    *,
    density: str = "comfortable",
    typography_scale: str = "lg",
    tab_density: str | None = None,
    tab_variant: str = "glass",
    border_strength_scale: float = 1.0,
    surface_opacity_scale: float = 1.0,
) -> str:
    palette = get_palette(theme_id)
    r = GLASS_RADIUS
    sizes = _sizes_for_scale(_coerce_typography_scale(typography_scale))
    control_density = _density_values(_coerce_density(density))
    tab_density_values = _density_values(_coerce_tab_density(tab_density or density))
    variant = _coerce_tab_variant(tab_variant)
    surface = build_surface_material_spec(
        palette,
        border_strength_scale=border_strength_scale,
        surface_opacity_scale=surface_opacity_scale,
        tab_variant=variant,
        tab_radius=r.input,
        pill_radius=r.chip,
    )
    p = surface.palette
    chrome = build_chrome_spec(p)
    subtitle_size = max(sizes["subtitle"] + 1, sizes["body"])
    caption_size = max(sizes["caption"] + 1, sizes["label"])
    eyebrow_size = max(caption_size, sizes["label"] + 1)
    panel_title_size = max(caption_size + 1, sizes["body"])
    panel_subtitle_size = max(caption_size, sizes["label"])
    window_title_size = max(sizes["body"] + 1, sizes["section"])

    return f"""
QWidget#GlassStage,
QWidget#GlassContent {{
    background: transparent;
}}

QFrame#Shell {{
    background: {_gradient(p.shell_top, p.shell_bottom)};
    border: {surface.border_px}px solid {p.shell_border};
    border-radius: {r.shell}px;
}}
QFrame#Shell:hover {{
    border: {surface.border_px}px solid {p.shell_border_hover};
}}
QFrame#Shell[variant="progress"] {{
    border-radius: {r.shell_progress}px;
}}

QFrame#WindowChrome {{
    background: {_gradient(chrome.chrome_top, chrome.chrome_bottom)};
    border: {surface.border_px}px solid {chrome.chrome_border};
    border-radius: {max(0, r.window_chrome - 2)}px;
}}

QFrame[card="hero"] {{
    background: transparent;
    border: none;
    border-radius: {r.hero_card}px;
}}

QFrame[card="true"],
QFrame[card="muted"],
QFrame[card="footer"] {{
    background: {_gradient(p.card_top, p.card_bottom)};
    border: {surface.border_px}px solid {p.card_border};
    border-radius: {r.card}px;
}}
QFrame[card="clear"] {{
    background: transparent;
    border: none;
    border-radius: {r.card}px;
}}

QFrame[panelRole="main"],
QFrame[panelRole="workspace"] {{
    border-color: {p.card_border};
}}
QFrame[panelRole="form"] {{
    border-color: {p.panel_form_border};
}}
QFrame[panelRole="data"],
QFrame[panelRole="dashboard"] {{
    border-color: {p.panel_data_border};
}}
QFrame[panelRole="metrics"] {{
    border-color: {p.panel_metrics_border};
}}
QFrame[panelRole="detail"],
QFrame[panelRole="inspector"] {{
    border-color: {p.panel_detail_border};
}}
QFrame[panelRole="summary"] {{
    border-color: {p.panel_summary_border};
}}
QFrame[panelRole="aux"],
QFrame[panelRole="auxiliary"],
QFrame[panelRole="tools"],
QFrame[panelRole="activity"] {{
    border-color: {p.panel_aux_border};
}}
QFrame[panelState="hold"],
QFrame[panelState="background"] {{
    border-style: dashed;
}}
QFrame[panelState="disabled"] {{
    opacity: 0.72;
}}
QFrame[panelState="collapsed"],
QFrame[panelState="hidden"] {{
    border-color: transparent;
}}

QLabel[role="display"] {{
    color: {p.text_primary};
    font-size: {sizes["display"]}px;
    font-weight: {GLASS_TYPOGRAPHY.weight_bold};
}}
QLabel[role="title"] {{
    color: {p.text_primary};
    font-size: {sizes["title"]}px;
    font-weight: {GLASS_TYPOGRAPHY.weight_bold};
}}
QLabel[role="subtitle"],
QLabel[role="hint"],
QLabel[role="value"] {{
    color: {p.text_muted};
    font-size: {subtitle_size}px;
}}
QLabel[role="section"] {{
    color: {p.text_primary};
    font-size: {sizes["section"]}px;
    font-weight: {GLASS_TYPOGRAPHY.weight_semibold};
}}
QLabel[role="label"] {{
    color: {p.text_muted};
    font-size: {sizes["label"]}px;
}}
QLabel[role="caption"],
QLabel[role="microcopy"] {{
    color: {p.text_muted};
    font-size: {caption_size}px;
}}
QLabel[role="eyebrow"],
QLabel[role="field"] {{
    color: {p.accent};
    font-size: {eyebrow_size}px;
    font-weight: {GLASS_TYPOGRAPHY.weight_semibold};
    letter-spacing: 1px;
    text-transform: uppercase;
}}
QLabel[role="panel_title"] {{
    color: {p.text_primary};
    font-size: {panel_title_size}px;
    font-weight: {GLASS_TYPOGRAPHY.weight_semibold};
    letter-spacing: 0.4px;
    text-transform: uppercase;
}}
QLabel[role="panel_subtitle"] {{
    color: {p.text_muted};
    font-size: {panel_subtitle_size}px;
}}
QLabel[role="window_title"] {{
    color: {p.text_primary};
    font-size: {window_title_size}px;
    font-weight: {GLASS_TYPOGRAPHY.weight_semibold};
}}

QLineEdit,
QComboBox,
QTextEdit,
QPlainTextEdit,
QListWidget,
QTreeWidget,
QTableWidget {{
    background: {p.input_bg};
    border: {surface.border_px}px solid {p.input_border};
    border-radius: {r.input}px;
    color: {p.text_primary};
    padding: {control_density["input_y"]}px 10px;
    font-size: {sizes["body"]}px;
}}
QLineEdit:hover,
QLineEdit:focus,
QComboBox:hover,
QComboBox:focus,
QTextEdit:hover,
QTextEdit:focus,
QPlainTextEdit:hover,
QPlainTextEdit:focus {{
    border: {surface.border_px}px solid {p.input_border_hover};
}}

QPushButton {{
    background: rgba(255, 255, 255, 0.018);
    border: none;
    border-radius: {r.button}px;
    color: {p.text_primary};
    min-height: 22px;
    padding: {control_density["button_y"]}px 12px;
    font-size: {sizes["body"]}px;
    font-weight: {GLASS_TYPOGRAPHY.weight_semibold};
}}
QPushButton:hover {{
    border: {surface.border_px}px solid {p.shell_border_hover};
    background: {p.accent_soft};
}}
QPushButton:pressed {{
    border: {surface.border_px}px solid {p.shell_border};
    background: {p.button_bottom};
}}
QPushButton:focus {{
    border: {surface.border_px}px solid {p.shell_border_hover};
    background: {p.button_top};
}}
QPushButton:disabled {{
    color: {p.tab_text_muted};
    border: none;
    background: transparent;
}}
QPushButton[variant="primary"] {{
    background: {_gradient(p.button_top, p.button_bottom)};
    border: {surface.border_px}px solid {p.button_border};
}}
QPushButton[variant="secondary"] {{
    background: rgba(255, 255, 255, 0.014);
    border: none;
}}
QPushButton[variant="subtle"] {{
    background: rgba(255, 255, 255, 0.010);
    border: none;
    color: {p.text_muted};
}}
QPushButton[variant="subtle"]:hover {{
    color: {p.text_primary};
    border: {surface.border_px}px solid {p.shell_border_hover};
}}
QPushButton[variant="ghost"] {{
    background: rgba(255, 255, 255, 0.006);
    border: none;
}}
QPushButton[variant="ghost"]:hover {{
    border: {surface.border_px}px solid {p.shell_border};
    background: {p.accent_soft};
}}
QPushButton[variant="danger"] {{
    background: {_gradient(p.danger_top, p.danger_bottom)};
    border: {surface.border_px}px solid {p.danger_border};
}}
QPushButton[variant="warning"] {{
    background: {_gradient(p.warning_top, p.warning_bottom)};
    border: {surface.border_px}px solid {p.warning_border};
}}
QPushButton[variant="success"] {{
    background: {_gradient(p.success_top, p.success_bottom)};
    border: {surface.border_px}px solid {p.success_border};
}}

QTabWidget#GlassWorkspaceTabs::pane {{
    border: none;
    border-radius: {r.card}px;
    background: transparent;
    top: -1px;
    padding: 0px;
}}
QTabWidget#GlassWorkspaceTabs QTabBar::tab {{
    background: {p.tab_bg};
    color: {p.tab_text_muted};
    border: {surface.border_px}px {surface.tab_border_style} {p.tab_border};
    border-bottom-color: transparent;
    border-top-left-radius: {surface.tab_radius}px;
    border-top-right-radius: {surface.tab_radius}px;
    padding: {tab_density_values["tab_y"]}px {tab_density_values["tab_x"]}px;
    margin-right: 4px;
    font-size: {sizes["body"]}px;
}}
QTabWidget#GlassWorkspaceTabs QTabBar::tab:selected {{
    background: {p.tab_active_bg};
    color: {p.tab_text};
    border-color: {p.shell_border_hover};
}}
QTabWidget#GlassWorkspaceTabs QTabBar::tab:hover {{
    color: {p.tab_text};
    border-color: {p.shell_border};
}}
QTabWidget#GlassWorkspaceTabs QTabBar::tab:disabled {{
    background: {p.tab_hold_bg};
    color: {p.tab_text_muted};
}}
QTabWidget#GlassWorkspaceTabs QTabBar::close-button {{
    border-radius: {r.chip}px;
    margin-left: 6px;
    padding: 1px;
    background: rgba(255, 255, 255, 0.07);
}}
QTabWidget#GlassWorkspaceTabs QTabBar::close-button:hover {{
    background: rgba(255, 255, 255, 0.20);
}}
QTabWidget#GlassWorkspaceTabs[tabVariant="segmented"] QTabBar::tab {{
    border-radius: {r.chip}px;
    border: {surface.border_px}px solid {p.tab_border};
}}
QTabWidget#GlassWorkspaceTabs[tabVariant="pill"] QTabBar::tab {{
    border-radius: {r.chip}px;
    border: none;
}}
QTabWidget#GlassWorkspaceTabs[tabVariant="standard"] QTabBar::tab {{
    border-radius: {r.tab}px;
}}
QTabWidget#GlassWorkspaceTabs QTabBar::tab[tabState="pending"] {{
    background: {p.tab_pending_bg};
}}
QTabWidget#GlassWorkspaceTabs QTabBar::tab[tabState="warning"] {{
    background: {p.tab_warning_bg};
}}

QProgressBar {{
    border-radius: {r.progress}px;
    border: {surface.border_px}px solid {p.input_border};
    background: {p.progress_bg};
    text-align: center;
    color: {p.text_primary};
}}
QProgressBar::chunk {{
    border-radius: {r.progress - 1}px;
    background: {_gradient(p.progress_chunk_top, p.progress_chunk_bottom)};
}}

QToolButton[assetRole="icon_button"] {{
    background: transparent;
    border: {surface.border_px}px solid {p.input_border};
    border-radius: {r.button}px;
    padding: 4px;
}}
QToolButton[assetRole="icon_button"]:hover {{
    border-color: {p.input_border_hover};
    background: {p.accent_soft};
}}
QToolButton[assetRole="icon_button"]:disabled {{
    border-color: {p.input_border};
    background: transparent;
}}

QFrame[assetRole="segmented"],
QFrame[assetRole="filter_chip_bar"],
QFrame[assetRole="compact_toolbar"],
QFrame[assetRole="mini_legend"] {{
    background: transparent;
    border: none;
    border-radius: {r.card}px;
}}
QPushButton[assetRole="segment_button"],
QPushButton[assetRole="filter_chip"],
QPushButton[assetRole="toggle_pill"] {{
    border-radius: {r.chip}px;
    padding: 4px 10px;
}}
QPushButton[assetRole="segment_button"]:checked,
QPushButton[assetRole="filter_chip"]:checked,
QPushButton[assetRole="toggle_pill"]:checked {{
    background: {p.tab_active_bg};
    border: {surface.border_px}px solid {p.shell_border_hover};
}}
QPushButton[assetRole="segment_button"]:focus,
QPushButton[assetRole="filter_chip"]:focus,
QPushButton[assetRole="toggle_pill"]:focus {{
    border: {surface.border_px}px solid {p.shell_border_hover};
}}
QPushButton[assetRole="collapsible_header"] {{
    text-align: left;
    padding-left: 10px;
}}
QPushButton[assetRole="toolbar_button"] {{
    padding: 4px 10px;
}}

QFrame[assetRole="search_bar"] {{
    background: {p.input_bg};
    border: {surface.border_px}px solid {p.input_border};
    border-radius: {r.input}px;
}}
QFrame[assetRole="search_bar"] QLineEdit {{
    border: none;
    background: transparent;
}}
QFrame[assetRole="search_bar"] QLineEdit:focus {{
    border: {surface.border_px}px solid {p.input_border_hover};
}}

QLabel[assetRole="status_pill"] {{
    border-radius: {r.chip}px;
    border: {surface.border_px}px solid {p.tab_border};
    padding: 2px 8px;
    color: {p.text_primary};
    background: rgba(255, 255, 255, 0.05);
}}
QLabel[assetRole="status_pill"][statusKind="info"] {{
    background: {p.accent_soft};
    border-color: {p.shell_border_hover};
}}
QLabel[assetRole="status_pill"][statusKind="success"] {{
    background: {_gradient(p.success_top, p.success_bottom)};
    border-color: {p.success_border};
}}
QLabel[assetRole="status_pill"][statusKind="warning"] {{
    background: {_gradient(p.warning_top, p.warning_bottom)};
    border-color: {p.warning_border};
}}
QLabel[assetRole="status_pill"][statusKind="error"] {{
    background: {_gradient(p.danger_top, p.danger_bottom)};
    border-color: {p.danger_border};
}}
QLabel[assetRole="status_pill"][statusKind="pending"] {{
    background: {p.tab_pending_bg};
    border-color: {p.tab_border};
}}

QFrame[assetRole="stat_pill"],
QFrame[assetRole="control_card"],
QFrame[assetRole="collapsible_section"],
QFrame[assetRole="enhanced_slider"],
QFrame[assetRole="parameter_panel"],
QFrame[assetRole="hero_panel"] {{
    background: {_gradient(p.card_top, p.card_bottom)};
    border: {surface.border_px}px solid {p.card_border};
    border-radius: {r.card}px;
}}
QFrame[assetRole="hero_panel"] {{
    background: transparent;
    border: none;
    border-radius: {r.card}px;
}}
"""


__all__ = ["build_stylesheet"]
