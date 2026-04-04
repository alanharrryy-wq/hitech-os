from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping

from ..contracts import DEFAULT_THEME_ID


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
    shell_top="rgba(78, 80, 86, 0.90)",
    shell_bottom="rgba(54, 56, 61, 0.93)",
    shell_border="rgba(245, 248, 252, 0.22)",
    shell_border_hover="rgba(245, 248, 252, 0.34)",
    chrome_top="rgba(255, 255, 255, 0.11)",
    chrome_bottom="rgba(214, 220, 228, 0.06)",
    chrome_border="rgba(245, 248, 252, 0.12)",
    card_top="rgba(255, 255, 255, 0.10)",
    card_bottom="rgba(216, 221, 228, 0.05)",
    card_border="rgba(245, 248, 252, 0.10)",
    text_primary="#f1f4f8",
    text_muted="#c9d0d8",
    text_inverse="#1f2329",
    accent="#e2e6eb",
    accent_soft="rgba(245, 248, 252, 0.10)",
    button_top="rgba(255, 255, 255, 0.08)",
    button_bottom="rgba(208, 213, 220, 0.05)",
    button_border="rgba(245, 248, 252, 0.14)",
    danger_top="rgba(218, 170, 156, 0.17)",
    danger_bottom="rgba(145, 98, 86, 0.13)",
    danger_border="rgba(225, 182, 168, 0.26)",
    warning_top="rgba(219, 191, 145, 0.16)",
    warning_bottom="rgba(148, 120, 80, 0.12)",
    warning_border="rgba(226, 198, 157, 0.25)",
    success_top="rgba(151, 199, 176, 0.16)",
    success_bottom="rgba(96, 134, 116, 0.12)",
    success_border="rgba(171, 209, 189, 0.26)",
    input_bg="rgba(42, 44, 49, 0.58)",
    input_border="rgba(245, 248, 252, 0.16)",
    input_border_hover="rgba(245, 248, 252, 0.28)",
    progress_bg="rgba(44, 46, 51, 0.78)",
    progress_chunk_top="#eceff3",
    progress_chunk_bottom="#d9dfe7",
    tab_bg="rgba(255, 255, 255, 0.06)",
    tab_active_bg="rgba(255, 255, 255, 0.12)",
    tab_hold_bg="rgba(255, 255, 255, 0.08)",
    tab_pending_bg="rgba(181, 162, 124, 0.24)",
    tab_warning_bg="rgba(176, 137, 106, 0.24)",
    tab_border="rgba(245, 248, 252, 0.16)",
    tab_text="#f2f5f9",
    tab_text_muted="#bcc5cf",
    panel_form_border="rgba(245, 248, 252, 0.14)",
    panel_data_border="rgba(245, 248, 252, 0.16)",
    panel_metrics_border="rgba(245, 248, 252, 0.15)",
    panel_detail_border="rgba(245, 248, 252, 0.17)",
    panel_summary_border="rgba(245, 248, 252, 0.15)",
    panel_aux_border="rgba(245, 248, 252, 0.14)",
)

OBSIDIAN_ICE = GlassPalette(
    shell_top="rgba(67, 69, 75, 0.93)",
    shell_bottom="rgba(42, 44, 49, 0.95)",
    shell_border="rgba(209, 216, 226, 0.28)",
    shell_border_hover="rgba(229, 234, 240, 0.40)",
    chrome_top="rgba(112, 116, 124, 0.26)",
    chrome_bottom="rgba(74, 77, 84, 0.24)",
    chrome_border="rgba(220, 226, 234, 0.20)",
    card_top="rgba(103, 106, 114, 0.24)",
    card_bottom="rgba(70, 73, 80, 0.22)",
    card_border="rgba(213, 219, 228, 0.24)",
    text_primary="#eef2f6",
    text_muted="#c6ced7",
    text_inverse="#1c2025",
    accent="#dde2e8",
    accent_soft="rgba(221, 226, 232, 0.20)",
    button_top="rgba(159, 167, 178, 0.18)",
    button_bottom="rgba(118, 125, 136, 0.16)",
    button_border="rgba(221, 226, 232, 0.28)",
    danger_top="rgba(203, 137, 129, 0.18)",
    danger_bottom="rgba(149, 90, 84, 0.14)",
    danger_border="rgba(221, 163, 156, 0.28)",
    warning_top="rgba(206, 176, 126, 0.18)",
    warning_bottom="rgba(145, 114, 68, 0.14)",
    warning_border="rgba(214, 189, 150, 0.26)",
    success_top="rgba(121, 186, 159, 0.17)",
    success_bottom="rgba(87, 128, 110, 0.14)",
    success_border="rgba(149, 206, 183, 0.27)",
    input_bg="rgba(36, 39, 44, 0.74)",
    input_border="rgba(214, 220, 229, 0.24)",
    input_border_hover="rgba(236, 240, 245, 0.36)",
    progress_bg="rgba(34, 36, 41, 0.84)",
    progress_chunk_top="#dfe4ea",
    progress_chunk_bottom="#cfd6de",
    tab_bg="rgba(73, 76, 83, 0.62)",
    tab_active_bg="rgba(122, 127, 137, 0.42)",
    tab_hold_bg="rgba(82, 85, 92, 0.44)",
    tab_pending_bg="rgba(69, 84, 52, 0.55)",
    tab_warning_bg="rgba(88, 72, 49, 0.56)",
    tab_border="rgba(214, 220, 229, 0.30)",
    tab_text="#eef2f6",
    tab_text_muted="#c2cad3",
    panel_form_border="rgba(225, 230, 236, 0.28)",
    panel_data_border="rgba(220, 225, 232, 0.26)",
    panel_metrics_border="rgba(220, 225, 232, 0.27)",
    panel_detail_border="rgba(220, 225, 232, 0.27)",
    panel_summary_border="rgba(220, 225, 232, 0.27)",
    panel_aux_border="rgba(214, 220, 229, 0.24)",
)

ORCHESTRATOR_LAB = GlassPalette(
    shell_top="rgba(10, 14, 24, 0.98)",
    shell_bottom="rgba(3, 6, 14, 1.00)",
    shell_border="rgba(109, 208, 255, 0.26)",
    shell_border_hover="rgba(171, 231, 255, 0.42)",
    chrome_top="rgba(79, 142, 255, 0.22)",
    chrome_bottom="rgba(109, 76, 255, 0.12)",
    chrome_border="rgba(133, 198, 255, 0.22)",
    card_top="rgba(17, 24, 39, 0.94)",
    card_bottom="rgba(7, 11, 21, 0.97)",
    card_border="rgba(108, 182, 255, 0.24)",
    text_primary="#f4f9ff",
    text_muted="#9db2d1",
    text_inverse="#090d16",
    accent="#7de3ff",
    accent_soft="rgba(125, 227, 255, 0.18)",
    button_top="rgba(56, 130, 255, 0.24)",
    button_bottom="rgba(80, 77, 255, 0.18)",
    button_border="rgba(126, 201, 255, 0.30)",
    danger_top="rgba(234, 96, 124, 0.24)",
    danger_bottom="rgba(118, 36, 62, 0.20)",
    danger_border="rgba(255, 146, 170, 0.30)",
    warning_top="rgba(239, 186, 74, 0.24)",
    warning_bottom="rgba(140, 88, 20, 0.20)",
    warning_border="rgba(255, 214, 123, 0.30)",
    success_top="rgba(94, 224, 178, 0.24)",
    success_bottom="rgba(19, 113, 92, 0.20)",
    success_border="rgba(132, 245, 205, 0.30)",
    input_bg="rgba(5, 10, 20, 0.90)",
    input_border="rgba(122, 187, 255, 0.22)",
    input_border_hover="rgba(182, 226, 255, 0.36)",
    progress_bg="rgba(4, 8, 16, 0.94)",
    progress_chunk_top="#bdf3ff",
    progress_chunk_bottom="#6aa8ff",
    tab_bg="rgba(12, 18, 31, 0.90)",
    tab_active_bg="rgba(32, 55, 99, 0.96)",
    tab_hold_bg="rgba(17, 24, 36, 0.88)",
    tab_pending_bg="rgba(90, 76, 32, 0.82)",
    tab_warning_bg="rgba(117, 58, 39, 0.82)",
    tab_border="rgba(118, 181, 255, 0.26)",
    tab_text="#f5faff",
    tab_text_muted="#9fb5d8",
    panel_form_border="rgba(118, 191, 255, 0.24)",
    panel_data_border="rgba(102, 216, 255, 0.26)",
    panel_metrics_border="rgba(110, 241, 255, 0.26)",
    panel_detail_border="rgba(160, 173, 255, 0.24)",
    panel_summary_border="rgba(130, 196, 255, 0.26)",
    panel_aux_border="rgba(113, 160, 216, 0.22)",
)

_THEME_REGISTRY: dict[str, GlassThemeManifest] = {
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
    "orchestrator_lab": GlassThemeManifest(
        theme_id="orchestrator_lab",
        palette=ORCHESTRATOR_LAB,
        parent_theme_id="obsidian_ice",
        description="Experimental high-contrast lab palette for orchestrators, new UI and premium FX.",
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
    if not override and normalized in _THEME_REGISTRY:
        raise ValueError(f"theme '{normalized}' already registered")
    if parent_theme_id:
        parent = str(parent_theme_id).strip().lower()
        if parent not in _THEME_REGISTRY:
            raise ValueError(f"parent theme '{parent}' is not registered")
    _THEME_REGISTRY[normalized] = GlassThemeManifest(
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
    return tuple(sorted(_THEME_REGISTRY.keys()))


def get_theme_manifest(theme_id: str = DEFAULT_THEME_ID) -> GlassThemeManifest:
    normalized = (theme_id or DEFAULT_THEME_ID).strip().lower()
    return _THEME_REGISTRY.get(normalized, _THEME_REGISTRY[DEFAULT_THEME_ID])


def get_palette(theme_id: str = DEFAULT_THEME_ID) -> GlassPalette:
    return get_theme_manifest(theme_id).palette


__all__ = [
    "GlassPalette",
    "GlassThemeManifest",
    "get_palette",
    "get_theme_manifest",
    "list_theme_ids",
    "register_theme",
    "register_theme_overrides",
]
