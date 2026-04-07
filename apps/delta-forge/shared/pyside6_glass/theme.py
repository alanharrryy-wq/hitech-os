from __future__ import annotations

from dataclasses import dataclass, replace
import re
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
    shell_top="rgba(13, 14, 18, 0.9)",
    shell_bottom="rgba(7, 8, 11, 0.93)",
    shell_border="rgba(245, 248, 252, 0.2)",
    shell_border_hover="rgba(245, 248, 252, 0.3)",
    chrome_top="rgba(255, 255, 255, 0.035)",
    chrome_bottom="rgba(255, 255, 255, 0.012)",
    chrome_border="rgba(245, 248, 252, 0.08)",
    card_top="rgba(255, 255, 255, 0.032)",
    card_bottom="rgba(255, 255, 255, 0.014)",
    card_border="rgba(245, 248, 252, 0.06)",
    text_primary="#e7edf4",
    text_muted="#b5bfcb",
    text_inverse="#081018",
    accent="#dfe5ee",
    accent_soft="rgba(245, 248, 252, 0.07)",
    button_top="rgba(255, 255, 255, 0.02)",
    button_bottom="rgba(255, 255, 255, 0.008)",
    button_border="rgba(245, 248, 252, 0.10)",
    danger_top="rgba(218, 170, 156, 0.17)",
    danger_bottom="rgba(145, 98, 86, 0.13)",
    danger_border="rgba(225, 182, 168, 0.26)",
    warning_top="rgba(219, 191, 145, 0.16)",
    warning_bottom="rgba(148, 120, 80, 0.12)",
    warning_border="rgba(226, 198, 157, 0.25)",
    success_top="rgba(151, 199, 176, 0.16)",
    success_bottom="rgba(96, 134, 116, 0.12)",
    success_border="rgba(171, 209, 189, 0.26)",
    input_bg="rgba(5, 6, 10, 0.56)",
    input_border="rgba(245, 248, 252, 0.13)",
    input_border_hover="rgba(245, 248, 252, 0.25)",
    progress_bg="rgba(5, 6, 10, 0.76)",
    progress_chunk_top="#d8dfe9",
    progress_chunk_bottom="#c2cbd8",
    tab_bg="rgba(255, 255, 255, 0.03)",
    tab_active_bg="rgba(255, 255, 255, 0.06)",
    tab_hold_bg="rgba(255, 255, 255, 0.04)",
    tab_pending_bg="rgba(181, 162, 124, 0.24)",
    tab_warning_bg="rgba(176, 137, 106, 0.24)",
    tab_border="rgba(245, 248, 252, 0.14)",
    tab_text="#e8edf4",
    tab_text_muted="#a7b0be",
    panel_form_border="rgba(140, 235, 255, 0.12)",
    panel_data_border="rgba(140, 235, 255, 0.15)",
    panel_metrics_border="rgba(140, 235, 255, 0.14)",
    panel_detail_border="rgba(140, 235, 255, 0.16)",
    panel_summary_border="rgba(140, 235, 255, 0.14)",
    panel_aux_border="rgba(140, 235, 255, 0.12)",
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
        description="Default low-saturation silver graphite glass.",
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


_RGBA_PATTERN = re.compile(
    r"^rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*([01](?:\.\d+)?)\s*\)$",
    re.IGNORECASE,
)


def _scale_rgba_alpha(color: str, scale: float) -> str:
    token = str(color or "").strip()
    match = _RGBA_PATTERN.match(token)
    if match is None:
        return token

    r_raw, g_raw, b_raw, alpha_raw = match.groups()
    r = max(0, min(255, int(r_raw)))
    g = max(0, min(255, int(g_raw)))
    b = max(0, min(255, int(b_raw)))
    alpha = max(0.0, min(1.0, float(alpha_raw) * float(scale)))
    alpha_text = f"{alpha:.3f}".rstrip("0").rstrip(".")
    return f"rgba({r}, {g}, {b}, {alpha_text})"


def _apply_surface_opacity_scale(palette: GlassPalette, scale: float) -> GlassPalette:
    if abs(float(scale) - 1.0) < 0.0001:
        return palette

    surface_keys = (
        "shell_top",
        "shell_bottom",
        "chrome_top",
        "chrome_bottom",
        "card_top",
        "card_bottom",
        "accent_soft",
        "button_top",
        "button_bottom",
        "danger_top",
        "danger_bottom",
        "warning_top",
        "warning_bottom",
        "success_top",
        "success_bottom",
        "input_bg",
        "progress_bg",
        "tab_bg",
        "tab_active_bg",
        "tab_hold_bg",
        "tab_pending_bg",
        "tab_warning_bg",
    )
    overrides = {
        key: _scale_rgba_alpha(getattr(palette, key), scale)
        for key in surface_keys
    }
    return palette.with_overrides(overrides)


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
    p = get_palette(theme_id)
    r = GLASS_RADIUS
    sizes = _sizes_for_scale(_coerce_typography_scale(typography_scale))
    control_density = _density_values(_coerce_density(density))
    tab_density_values = _density_values(_coerce_tab_density(tab_density or density))
    variant = _coerce_tab_variant(tab_variant)
    border_scale = max(0.5, min(2.0, float(border_strength_scale)))
    surface_scale = max(0.5, min(1.4, float(surface_opacity_scale)))
    p = _apply_surface_opacity_scale(p, surface_scale)
    subtitle_size = max(sizes["subtitle"] + 1, sizes["body"])
    caption_size = max(sizes["caption"] + 1, sizes["label"])
    eyebrow_size = max(caption_size, sizes["label"] + 1)
    panel_title_size = max(caption_size + 1, sizes["body"])
    panel_subtitle_size = max(caption_size, sizes["label"])
    window_title_size = max(sizes["body"] + 1, sizes["section"])

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
    border: {shell_border_px}px solid rgba(140, 235, 255, 0.14);
    border-radius: {r.shell}px;
}}
QFrame#Shell:hover {{
    border: {shell_border_px}px solid rgba(140, 235, 255, 0.24);
}}
QFrame#Shell[variant="progress"] {{
    border-radius: {r.shell_progress}px;
}}

QFrame#WindowChrome {{
    background: transparent;
    border: none;
    border-radius: {max(0, r.window_chrome - 2)}px;
}}

QFrame[card="hero"] {{
    background: rgba(0, 0, 0, 0.0);
    border: none;
    border-radius: {r.hero_card}px;
}}

QFrame[card="true"],
QFrame[card="muted"],
QFrame[card="footer"] {{
    background: {_gradient(p.card_top, p.card_bottom)};
    border: {shell_border_px}px solid rgba(140, 235, 255, 0.12);
    border-radius: {r.card}px;
}}
QFrame[card="clear"] {{
    background: transparent;
    border: none;
    border-radius: {r.card}px;
}}

QFrame[panelRole="main"],
QFrame[panelRole="workspace"] {{
    border-color: rgba(140, 235, 255, 0.12);
}}
QFrame[panelRole="form"] {{
    border-color: rgba(140, 235, 255, 0.14);
}}
QFrame[panelRole="data"],
QFrame[panelRole="dashboard"] {{
    border-color: rgba(140, 235, 255, 0.16);
}}
QFrame[panelRole="metrics"] {{
    border-color: rgba(140, 235, 255, 0.15);
}}
QFrame[panelRole="detail"],
QFrame[panelRole="inspector"] {{
    border-color: rgba(140, 235, 255, 0.16);
}}
QFrame[panelRole="summary"] {{
    border-color: rgba(140, 235, 255, 0.15);
}}
QFrame[panelRole="aux"],
QFrame[panelRole="auxiliary"],
QFrame[panelRole="tools"],
QFrame[panelRole="activity"] {{
    border-color: rgba(140, 235, 255, 0.12);
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
    border: {shell_border_px}px solid rgba(140, 235, 255, 0.16);
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
    border: {shell_border_px}px solid rgba(140, 235, 255, 0.58);
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
    border: 1px solid rgba(140, 235, 255, 0.48);
    background: rgba(140, 235, 255, 0.07);
}}
QPushButton:pressed {{
    border: 1px solid rgba(140, 235, 255, 0.86);
    background: rgba(140, 235, 255, 0.13);
}}
QPushButton:focus {{
    border: 1px solid rgba(140, 235, 255, 0.78);
    background: rgba(140, 235, 255, 0.11);
}}
QPushButton:disabled {{
    color: {p.tab_text_muted};
    border: none;
    background: transparent;
}}
QPushButton[variant="primary"] {{
    background: rgba(140, 235, 255, 0.07);
    border: none;
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
    border: 1px solid rgba(140, 235, 255, 0.44);
}}
QPushButton[variant="ghost"] {{
    background: rgba(255, 255, 255, 0.006);
    border: none;
}}
QPushButton[variant="ghost"]:hover {{
    border: 1px solid rgba(140, 235, 255, 0.42);
    background: rgba(140, 235, 255, 0.06);
}}
QPushButton[variant="danger"] {{
    background: {_gradient(p.danger_top, p.danger_bottom)};
    border: none;
}}
QPushButton[variant="warning"] {{
    background: {_gradient(p.warning_top, p.warning_bottom)};
    border: none;
}}
QPushButton[variant="success"] {{
    background: {_gradient(p.success_top, p.success_bottom)};
    border: none;
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
    border: {shell_border_px}px {tab_border_style} {p.tab_border};
    border-bottom-color: transparent;
    border-top-left-radius: {tab_radius}px;
    border-top-right-radius: {tab_radius}px;
    padding: {tab_density_values["tab_y"]}px {tab_density_values["tab_x"]}px;
    margin-right: 4px;
    font-size: {sizes["body"]}px;
}}
QTabWidget#GlassWorkspaceTabs QTabBar::tab:selected {{
    background: {p.tab_active_bg};
    color: {p.tab_text};
    border-color: rgba(140, 235, 255, 0.62);
}}
QTabWidget#GlassWorkspaceTabs QTabBar::tab:hover {{
    color: {p.tab_text};
    border-color: rgba(140, 235, 255, 0.42);
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
    border: {shell_border_px}px solid rgba(140, 235, 255, 0.18);
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
    border: {shell_border_px}px solid rgba(140, 235, 255, 0.16);
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
    border: {shell_border_px}px solid rgba(140, 235, 255, 0.16);
    border-radius: {r.button}px;
    padding: 4px;
}}
QToolButton[assetRole="icon_button"]:hover {{
    border-color: rgba(140, 235, 255, 0.56);
    background: rgba(140, 235, 255, 0.12);
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
    background: rgba(140, 235, 255, 0.12);
    border: 1px solid rgba(140, 235, 255, 0.62);
}}
QPushButton[assetRole="segment_button"]:focus,
QPushButton[assetRole="filter_chip"]:focus,
QPushButton[assetRole="toggle_pill"]:focus {{
    border: 1px solid rgba(140, 235, 255, 0.74);
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
    border: {shell_border_px}px solid rgba(140, 235, 255, 0.16);
    border-radius: {r.input}px;
}}
QFrame[assetRole="search_bar"] QLineEdit {{
    border: none;
    background: transparent;
}}
QFrame[assetRole="search_bar"] QLineEdit:focus {{
    border: 1px solid rgba(140, 235, 255, 0.70);
}}

QLabel[assetRole="status_pill"] {{
    border-radius: {r.chip}px;
    border: {shell_border_px}px solid rgba(140, 235, 255, 0.18);
    padding: 2px 8px;
    color: {p.text_primary};
    background: rgba(255, 255, 255, 0.05);
}}
QLabel[assetRole="status_pill"][statusKind="info"] {{
    background: rgba(140, 235, 255, 0.12);
    border-color: rgba(140, 235, 255, 0.58);
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
    border-color: rgba(140, 235, 255, 0.26);
}}

QFrame[assetRole="stat_pill"],
QFrame[assetRole="control_card"],
QFrame[assetRole="collapsible_section"],
QFrame[assetRole="enhanced_slider"],
QFrame[assetRole="parameter_panel"],
QFrame[assetRole="hero_panel"] {{
    background: {_gradient(p.card_top, p.card_bottom)};
    border: {shell_border_px}px solid rgba(140, 235, 255, 0.12);
    border-radius: {r.card}px;
}}
QFrame[assetRole="hero_panel"] {{
    background: transparent;
    border: none;
    border-radius: {r.card}px;
}}
"""


def build_stylesheet_exact_atlas(
    theme_id: str = DEFAULT_THEME_ID,
    *,
    density: str = "comfortable",
    typography_scale: str = "lg",
    tab_density: str | None = None,
    tab_variant: str = "glass",
    border_strength_scale: float = 1.0,
    surface_opacity_scale: float = 1.0,
) -> str:
    from .atlas_styles import build_app_stylesheet

    base = build_stylesheet(
        theme_id=theme_id,
        density=density,
        typography_scale=typography_scale,
        tab_density=tab_density,
        tab_variant=tab_variant,
        border_strength_scale=border_strength_scale,
        surface_opacity_scale=surface_opacity_scale,
    )
    overrides = build_app_stylesheet(theme_id)
    if not str(overrides or "").strip():
        return base
    return f"{base}\n{overrides}"
