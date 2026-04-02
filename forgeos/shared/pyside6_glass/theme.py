from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping

from .contracts import (
    DEFAULT_THEME_ID,
    GLASS_DENSITY,
    GLASS_RADIUS,
    GLASS_TYPOGRAPHY,
    SUPPORTED_DENSITY,
    SUPPORTED_TAB_DENSITY,
    SUPPORTED_TAB_VARIANTS,
    SUPPORTED_TYPOGRAPHY_SCALE,
)


@dataclass(frozen=True, slots=True)
class GlassPalette:
    shell_top: str
    shell_bottom: str
    shell_border: str
    shell_border_hover: str
    chrome_top: str
    chrome_bottom: str
    chrome_border: str
    card_top: str
    card_bottom: str
    card_border: str
    text_primary: str
    text_muted: str
    text_inverse: str
    accent: str
    accent_soft: str
    button_top: str
    button_bottom: str
    button_border: str
    danger_top: str
    danger_bottom: str
    danger_border: str
    warning_top: str
    warning_bottom: str
    warning_border: str
    success_top: str
    success_bottom: str
    success_border: str
    input_bg: str
    input_border: str
    input_border_hover: str
    progress_bg: str
    progress_chunk_top: str
    progress_chunk_bottom: str
    tab_bg: str
    tab_active_bg: str
    tab_hold_bg: str
    tab_pending_bg: str
    tab_warning_bg: str
    tab_border: str
    tab_text: str
    tab_text_muted: str
    panel_form_border: str
    panel_data_border: str
    panel_metrics_border: str
    panel_detail_border: str
    panel_summary_border: str
    panel_aux_border: str

    def with_overrides(self, overrides: Mapping[str, str]) -> GlassPalette:
        payload = {key: value for key, value in overrides.items() if hasattr(self, key)}
        if not payload:
            return self
        return replace(self, **payload)


@dataclass(frozen=True, slots=True)
class GlassThemeManifest:
    theme_id: str
    palette: GlassPalette
    parent_theme_id: str | None = None
    description: str = ""


SILVER_FROST_CYAN = GlassPalette(
    shell_top="rgba(20, 33, 54, 0.92)",
    shell_bottom="rgba(10, 19, 37, 0.95)",
    shell_border="rgba(157, 214, 255, 0.28)",
    shell_border_hover="rgba(181, 233, 255, 0.42)",
    chrome_top="rgba(72, 88, 112, 0.34)",
    chrome_bottom="rgba(38, 48, 68, 0.30)",
    chrome_border="rgba(205, 235, 255, 0.20)",
    card_top="rgba(82, 102, 126, 0.36)",
    card_bottom="rgba(46, 57, 75, 0.34)",
    card_border="rgba(178, 224, 255, 0.22)",
    text_primary="#e7f2fb",
    text_muted="#b7cbdd",
    text_inverse="#081018",
    accent="#8cefff",
    accent_soft="rgba(140, 239, 255, 0.26)",
    button_top="rgba(132, 213, 250, 0.34)",
    button_bottom="rgba(102, 168, 212, 0.26)",
    button_border="rgba(168, 229, 255, 0.36)",
    danger_top="rgba(230, 165, 130, 0.18)",
    danger_bottom="rgba(174, 110, 82, 0.14)",
    danger_border="rgba(238, 177, 145, 0.28)",
    warning_top="rgba(236, 201, 133, 0.18)",
    warning_bottom="rgba(168, 130, 70, 0.13)",
    warning_border="rgba(240, 213, 157, 0.28)",
    success_top="rgba(133, 223, 173, 0.18)",
    success_bottom="rgba(86, 157, 117, 0.13)",
    success_border="rgba(157, 230, 187, 0.30)",
    input_bg="rgba(21, 35, 56, 0.72)",
    input_border="rgba(149, 204, 242, 0.24)",
    input_border_hover="rgba(165, 227, 255, 0.40)",
    progress_bg="rgba(19, 34, 52, 0.82)",
    progress_chunk_top="#8cefff",
    progress_chunk_bottom="#78d5f0",
    tab_bg="rgba(28, 43, 64, 0.70)",
    tab_active_bg="rgba(66, 103, 146, 0.55)",
    tab_hold_bg="rgba(39, 54, 73, 0.55)",
    tab_pending_bg="rgba(80, 98, 62, 0.56)",
    tab_warning_bg="rgba(114, 86, 44, 0.56)",
    tab_border="rgba(159, 211, 246, 0.34)",
    tab_text="#dcefff",
    tab_text_muted="#a8bed0",
    panel_form_border="rgba(150, 212, 255, 0.38)",
    panel_data_border="rgba(138, 227, 197, 0.32)",
    panel_metrics_border="rgba(255, 208, 140, 0.32)",
    panel_detail_border="rgba(204, 178, 255, 0.30)",
    panel_summary_border="rgba(140, 220, 255, 0.30)",
    panel_aux_border="rgba(154, 180, 204, 0.28)",
)

OBSIDIAN_ICE = GlassPalette(
    shell_top="rgba(21, 29, 44, 0.93)",
    shell_bottom="rgba(8, 13, 24, 0.95)",
    shell_border="rgba(136, 162, 193, 0.28)",
    shell_border_hover="rgba(171, 196, 224, 0.40)",
    chrome_top="rgba(57, 67, 87, 0.34)",
    chrome_bottom="rgba(29, 36, 52, 0.31)",
    chrome_border="rgba(176, 200, 228, 0.19)",
    card_top="rgba(63, 74, 95, 0.35)",
    card_bottom="rgba(36, 44, 61, 0.34)",
    card_border="rgba(137, 161, 188, 0.24)",
    text_primary="#e4ebf5",
    text_muted="#b2bfce",
    text_inverse="#0b121c",
    accent="#9abdf3",
    accent_soft="rgba(154, 189, 243, 0.24)",
    button_top="rgba(117, 153, 214, 0.30)",
    button_bottom="rgba(85, 119, 177, 0.24)",
    button_border="rgba(154, 188, 231, 0.34)",
    danger_top="rgba(203, 137, 129, 0.18)",
    danger_bottom="rgba(149, 90, 84, 0.14)",
    danger_border="rgba(221, 163, 156, 0.28)",
    warning_top="rgba(206, 176, 126, 0.18)",
    warning_bottom="rgba(145, 114, 68, 0.14)",
    warning_border="rgba(214, 189, 150, 0.26)",
    success_top="rgba(121, 186, 159, 0.17)",
    success_bottom="rgba(87, 128, 110, 0.14)",
    success_border="rgba(149, 206, 183, 0.27)",
    input_bg="rgba(18, 25, 39, 0.75)",
    input_border="rgba(126, 149, 177, 0.24)",
    input_border_hover="rgba(155, 181, 214, 0.40)",
    progress_bg="rgba(16, 24, 38, 0.84)",
    progress_chunk_top="#9abdf3",
    progress_chunk_bottom="#84a4d5",
    tab_bg="rgba(30, 40, 56, 0.66)",
    tab_active_bg="rgba(70, 94, 132, 0.52)",
    tab_hold_bg="rgba(39, 51, 69, 0.52)",
    tab_pending_bg="rgba(69, 84, 52, 0.55)",
    tab_warning_bg="rgba(88, 72, 49, 0.56)",
    tab_border="rgba(131, 154, 183, 0.33)",
    tab_text="#dbe7f7",
    tab_text_muted="#a6b4c7",
    panel_form_border="rgba(142, 173, 207, 0.35)",
    panel_data_border="rgba(119, 190, 168, 0.30)",
    panel_metrics_border="rgba(217, 181, 126, 0.30)",
    panel_detail_border="rgba(178, 155, 218, 0.28)",
    panel_summary_border="rgba(131, 176, 214, 0.28)",
    panel_aux_border="rgba(139, 157, 182, 0.26)",
)

THEME_REGISTRY: dict[str, GlassThemeManifest] = {
    "silver_frost_cyan": GlassThemeManifest(
        theme_id="silver_frost_cyan",
        palette=SILVER_FROST_CYAN,
        description="Default low-saturation silver/cyan glass.",
    ),
    "obsidian_ice": GlassThemeManifest(
        theme_id="obsidian_ice",
        palette=OBSIDIAN_ICE,
        description="Cool dark glass with obsidian undertones.",
    ),
}


def register_theme(
    theme_id: str,
    palette: GlassPalette,
    *,
    parent_theme_id: str | None = None,
    description: str = "",
    override: bool = False,
) -> None:
    normalized = str(theme_id or "").strip().lower()
    if not normalized:
        raise ValueError("theme_id is required")
    if not override and normalized in THEME_REGISTRY:
        raise ValueError(f"theme '{normalized}' already registered")
    if parent_theme_id:
        parent = str(parent_theme_id).strip().lower()
        if parent not in THEME_REGISTRY:
            raise ValueError(f"parent theme '{parent}' is not registered")
    THEME_REGISTRY[normalized] = GlassThemeManifest(
        theme_id=normalized,
        palette=palette,
        parent_theme_id=str(parent_theme_id).strip().lower() if parent_theme_id else None,
        description=description,
    )


def register_theme_overrides(
    theme_id: str,
    overrides: Mapping[str, str],
    *,
    base_theme_id: str = DEFAULT_THEME_ID,
    description: str = "",
    override: bool = False,
) -> None:
    base_palette = get_palette(base_theme_id)
    register_theme(
        theme_id,
        base_palette.with_overrides(overrides),
        parent_theme_id=base_theme_id,
        description=description,
        override=override,
    )


def list_theme_ids() -> tuple[str, ...]:
    return tuple(sorted(THEME_REGISTRY.keys()))


def get_theme_manifest(theme_id: str = DEFAULT_THEME_ID) -> GlassThemeManifest:
    normalized = (theme_id or DEFAULT_THEME_ID).strip().lower()
    return THEME_REGISTRY.get(normalized, THEME_REGISTRY[DEFAULT_THEME_ID])


def get_palette(theme_id: str = DEFAULT_THEME_ID) -> GlassPalette:
    return get_theme_manifest(theme_id).palette


def _coerce_typography_scale(scale: str) -> str:
    return _choice(scale, SUPPORTED_TYPOGRAPHY_SCALE, "md")


def _coerce_density(density: str) -> str:
    return _choice(density, SUPPORTED_DENSITY, "comfortable")


def _coerce_tab_density(value: str) -> str:
    return _choice(value, SUPPORTED_TAB_DENSITY, "comfortable")


def _coerce_tab_variant(value: str) -> str:
    return _choice(value, SUPPORTED_TAB_VARIANTS, "glass")


def _choice(value: str, allowed: tuple[str, ...], fallback: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in allowed:
        return normalized
    return fallback


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
    typography_scale: str = "md",
    tab_density: str | None = None,
    tab_variant: str = "glass",
    border_strength_scale: float = 1.0,
    surface_opacity_scale: float = 1.0,
) -> str:
    p = get_palette(theme_id)
    r = GLASS_RADIUS
    sizes = _sizes_for_scale(_coerce_typography_scale(typography_scale))
    control_density = _density_values(_coerce_density(density))
    tab_density_values = _density_values(_coerce_tab_density(tab_density or density))
    variant = _coerce_tab_variant(tab_variant)
    border_scale = max(0.5, min(2.0, float(border_strength_scale)))
    surface_scale = max(0.5, min(1.4, float(surface_opacity_scale)))

    tab_radius = r.input if variant != "pill" else r.chip
    tab_border_style = "solid" if variant in {"standard", "glass"} else "none"
    tab_active_border = p.tab_border if variant in {"standard", "glass"} else p.accent
    shell_border_px = max(1, int(round(1 * border_scale)))

    return f"""
QWidget#GlassStage,
QWidget#GlassContent {{
    background: transparent;
}}

QFrame#Shell {{
    background: {_gradient(p.shell_top, p.shell_bottom)};
    border: {shell_border_px}px solid {p.shell_border};
    border-radius: {r.shell}px;
}}
QFrame#Shell:hover {{
    border: {shell_border_px}px solid {p.shell_border_hover};
}}
QFrame#Shell[variant="progress"] {{
    border-radius: {r.shell_progress}px;
}}

QFrame#WindowChrome {{
    background: {_gradient(p.chrome_top, p.chrome_bottom)};
    border: {shell_border_px}px solid {p.chrome_border};
    border-radius: {r.window_chrome}px;
}}

QFrame[card="hero"] {{
    background: {_gradient(p.card_top, p.card_bottom)};
    border: {shell_border_px}px solid {p.card_border};
    border-radius: {r.hero_card}px;
}}

QFrame[card="true"],
QFrame[card="muted"],
QFrame[card="footer"] {{
    background: {_gradient(p.card_top, p.card_bottom)};
    border: {shell_border_px}px solid {p.card_border};
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
    font-size: {sizes["subtitle"]}px;
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
    font-size: {sizes["caption"]}px;
}}
QLabel[role="eyebrow"],
QLabel[role="field"],
QLabel[role="panel_title"] {{
    color: {p.accent};
    font-size: {sizes["caption"]}px;
    font-weight: {GLASS_TYPOGRAPHY.weight_semibold};
    letter-spacing: 1px;
    text-transform: uppercase;
}}
QLabel[role="panel_subtitle"] {{
    color: {p.text_muted};
    font-size: {sizes["caption"]}px;
}}
QLabel[role="window_title"] {{
    color: {p.text_primary};
    font-size: {sizes["body"]}px;
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
    border: {shell_border_px}px solid {p.input_border};
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
    border: {shell_border_px}px solid {p.input_border_hover};
}}

QPushButton {{
    background: {_gradient(p.button_top, p.button_bottom)};
    border: {shell_border_px}px solid {p.button_border};
    border-radius: {r.button}px;
    color: {p.text_primary};
    padding: {control_density["button_y"]}px 14px;
    font-size: {sizes["body"]}px;
    font-weight: {GLASS_TYPOGRAPHY.weight_semibold};
}}
QPushButton:hover {{
    border: {shell_border_px}px solid {p.accent};
}}
QPushButton:pressed {{
    background: {_gradient(p.button_bottom, p.button_top)};
}}
QPushButton:focus {{
    border: {shell_border_px}px solid {p.accent};
}}
QPushButton:disabled {{
    color: {p.tab_text_muted};
    border-color: {p.input_border};
    background: {_gradient(p.card_top, p.card_bottom)};
}}
QPushButton[variant="primary"] {{
    background: {_gradient(p.button_top, p.button_bottom)};
    border: {shell_border_px}px solid {p.accent};
}}
QPushButton[variant="secondary"] {{
    background: {_gradient(p.card_top, p.card_bottom)};
    border: {shell_border_px}px solid {p.button_border};
}}
QPushButton[variant="subtle"] {{
    background: rgba(0, 0, 0, 0.0);
    border: {shell_border_px}px solid {p.card_border};
    color: {p.text_muted};
}}
QPushButton[variant="subtle"]:hover {{
    color: {p.text_primary};
    border-color: {p.button_border};
}}
QPushButton[variant="ghost"] {{
    background: rgba(0, 0, 0, 0.0);
    border: {shell_border_px}px solid {p.input_border};
}}
QPushButton[variant="ghost"]:hover {{
    border-color: {p.accent};
}}
QPushButton[variant="danger"] {{
    background: {_gradient(p.danger_top, p.danger_bottom)};
    border: {shell_border_px}px solid {p.danger_border};
}}
QPushButton[variant="warning"] {{
    background: {_gradient(p.warning_top, p.warning_bottom)};
    border: {shell_border_px}px solid {p.warning_border};
}}
QPushButton[variant="success"] {{
    background: {_gradient(p.success_top, p.success_bottom)};
    border: {shell_border_px}px solid {p.success_border};
}}

QTabWidget#GlassWorkspaceTabs::pane {{
    border: {shell_border_px}px solid {p.tab_border};
    border-radius: {r.card}px;
    background: {_gradient(p.card_top, p.card_bottom)};
    top: -1px;
    padding: {control_density["panel_padding"]}px;
}}
QTabWidget#GlassWorkspaceTabs QTabBar::tab {{
    background: {p.tab_bg};
    color: {p.tab_text_muted};
    border: {shell_border_px}px {tab_border_style} {p.tab_border};
    border-bottom-color: transparent;
    border-top-left-radius: {tab_radius}px;
    border-top-right-radius: {tab_radius}px;
    padding: {tab_density_values["tab_y"]}px {tab_density_values["tab_x"]}px;
    margin-right: 6px;
    font-size: {sizes["body"]}px;
}}
QTabWidget#GlassWorkspaceTabs QTabBar::tab:selected {{
    background: {p.tab_active_bg};
    color: {p.tab_text};
    border-color: {tab_active_border};
}}
QTabWidget#GlassWorkspaceTabs QTabBar::tab:hover {{
    color: {p.tab_text};
}}
QTabWidget#GlassWorkspaceTabs QTabBar::tab:disabled {{
    background: {p.tab_hold_bg};
    color: {p.tab_text_muted};
}}
QTabWidget#GlassWorkspaceTabs[tabVariant="segmented"] QTabBar::tab {{
    border-radius: {r.chip}px;
    border: {shell_border_px}px solid {p.tab_border};
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
    border: {shell_border_px}px solid {p.input_border};
    background: {p.progress_bg};
    text-align: center;
    color: {p.text_primary};
}}
QProgressBar::chunk {{
    border-radius: {r.progress - 1}px;
    background: {_gradient(p.progress_chunk_top, p.progress_chunk_bottom)};
}}

QToolButton[assetRole="icon_button"] {{
    background: rgba(0, 0, 0, 0.0);
    border: {shell_border_px}px solid {p.input_border};
    border-radius: {r.button}px;
    padding: 4px;
}}
QToolButton[assetRole="icon_button"]:hover {{
    border-color: {p.accent};
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
    background: {_gradient(p.card_top, p.card_bottom)};
    border: {shell_border_px}px solid {p.card_border};
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
    border-color: {p.accent};
}}
QPushButton[assetRole="segment_button"]:focus,
QPushButton[assetRole="filter_chip"]:focus,
QPushButton[assetRole="toggle_pill"]:focus {{
    border-color: {p.accent};
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
    border: {shell_border_px}px solid {p.input_border};
    border-radius: {r.input}px;
}}
QFrame[assetRole="search_bar"] QLineEdit {{
    border: none;
    background: transparent;
}}

QLabel[assetRole="status_pill"] {{
    border-radius: {r.chip}px;
    border: {shell_border_px}px solid {p.input_border};
    padding: 2px 8px;
    color: {p.text_primary};
    background: {p.tab_bg};
}}
QLabel[assetRole="status_pill"][statusKind="info"] {{
    background: {p.tab_active_bg};
    border-color: {p.accent};
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
    border: {shell_border_px}px solid {p.card_border};
    border-radius: {r.card}px;
}}
"""
