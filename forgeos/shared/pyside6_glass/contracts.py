from __future__ import annotations

from dataclasses import dataclass

DEFAULT_THEME_ID = "silver_frost_cyan"
SUPPORTED_VARIANTS = ("selector", "progress")
SUPPORTED_DENSITY = ("compact", "cozy", "comfortable", "extended", "spacious")
SUPPORTED_EXPERIENCE_MODES = (
    "default",
    "focus",
    "dashboard",
    "editor",
    "inspector",
    "presentation",
    "analyst",
    "operator",
    "monitoring",
    "data_entry",
    "review",
)
SUPPORTED_TYPOGRAPHY_SCALE = ("sm", "md", "lg", "xl")
SUPPORTED_TAB_STATES = ("visible", "hold", "hidden", "disabled", "pending", "warning")
SUPPORTED_TAB_DENSITY = ("compact", "cozy", "comfortable", "extended")
SUPPORTED_TAB_VARIANTS = ("standard", "segmented", "pill", "glass")
SUPPORTED_TAB_ICON_MODES = ("text_only", "icon_only", "icon_text")
SUPPORTED_TAB_PLACEMENT = ("top", "bottom", "left", "right")
SUPPORTED_PANEL_STATES = (
    "visible",
    "hidden",
    "collapsed",
    "deferred",
    "disabled",
    "background",
    "hold",
)
PANEL_ROLES = (
    "main",
    "side",
    "inspector",
    "summary",
    "dashboard",
    "form",
    "related",
    "activity",
    "tools",
    "auxiliary",
    "workspace",
    "data",
    "metrics",
    "detail",
    "aux",
)
SUPPORTED_ANIMATION_LEVELS = ("off", "subtle", "standard", "rich")
SUPPORTED_VISUAL_LEVELS = ("performance", "standard", "premium", "showcase")


@dataclass(frozen=True, slots=True)
class GlassRadiusContract:
    """Frozen visual radii copied from the current glass language."""

    shell: int = 28
    shell_progress: int = 26
    window_chrome: int = 12
    hero_card: int = 22
    card: int = 18
    chip: int = 12
    input: int = 12
    button: int = 12
    progress: int = 10
    badge: int = 10
    tab: int = 12


@dataclass(frozen=True, slots=True)
class GlassSpacingContract:
    base: int = 10
    xsmall: int = 6
    small: int = 8
    medium: int = 12
    large: int = 16
    xlarge: int = 20
    xxlarge: int = 24
    xxxlarge: int = 30


@dataclass(frozen=True, slots=True)
class GlassTypographyContract:
    display_sm: int = 30
    display_md: int = 36
    display_lg: int = 42
    title_sm: int = 24
    title_md: int = 30
    title_lg: int = 36
    subtitle_sm: int = 11
    subtitle_md: int = 12
    subtitle_lg: int = 13
    section_sm: int = 12
    section_md: int = 13
    section_lg: int = 14
    body_sm: int = 10
    body_md: int = 11
    body_lg: int = 12
    body_strong_sm: int = 10
    body_strong_md: int = 11
    body_strong_lg: int = 12
    label_sm: int = 10
    label_md: int = 11
    label_lg: int = 12
    caption_sm: int = 9
    caption_md: int = 10
    caption_lg: int = 11
    microcopy_sm: int = 8
    microcopy_md: int = 9
    microcopy_lg: int = 10
    code_sm: int = 10
    code_md: int = 11
    code_lg: int = 12
    line_height_compact: float = 1.15
    line_height_regular: float = 1.28
    line_height_relaxed: float = 1.42
    weight_regular: int = 500
    weight_semibold: int = 650
    weight_bold: int = 760


@dataclass(frozen=True, slots=True)
class GlassDensityContract:
    input_y_compact: int = 6
    input_y_cozy: int = 7
    input_y_comfortable: int = 8
    input_y_extended: int = 9
    input_y_spacious: int = 10
    button_y_compact: int = 6
    button_y_cozy: int = 7
    button_y_comfortable: int = 8
    button_y_extended: int = 9
    button_y_spacious: int = 10
    panel_padding_compact: int = 12
    panel_padding_cozy: int = 13
    panel_padding_comfortable: int = 14
    panel_padding_extended: int = 15
    panel_padding_spacious: int = 16
    tab_padding_x_compact: int = 10
    tab_padding_x_cozy: int = 11
    tab_padding_x_comfortable: int = 12
    tab_padding_x_extended: int = 14
    tab_padding_y_compact: int = 5
    tab_padding_y_cozy: int = 6
    tab_padding_y_comfortable: int = 7
    tab_padding_y_extended: int = 8
    icon_compact: int = 14
    icon_cozy: int = 15
    icon_comfortable: int = 16
    icon_extended: int = 18
    icon_spacious: int = 20


GLASS_RADIUS = GlassRadiusContract()
GLASS_SPACING = GlassSpacingContract()
GLASS_TYPOGRAPHY = GlassTypographyContract()
GLASS_DENSITY = GlassDensityContract()
