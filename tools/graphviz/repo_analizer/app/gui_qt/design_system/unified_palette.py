"""Unified Design Palette - Master Export

Single convenience module that bundles all design system tokens for easy import.

PHASE: 1 (Design System Foundation)
NEW: 2026-03-19
SAFE: No modifications to existing code
"""

from __future__ import annotations

# Import all token systems
from .color_tokens import (
    HybridColorTokens,
    HYBRID_DESIGN_TOKENS,
)
from .typography_system import (
    TypographyScale,
    TypographyScaleConfig,
    LuxuryTypeface,
)
from .spacing_system import (
    LuxurySpacing,
)
from .elevations import (
    ElevationLevel,
    ShadowConfig,
    ShadowPreset,
    apply_inset_shadow,
    apply_raised_shadow,
    apply_floating_shadow,
    get_shadow_config,
)


# ==== MASTER CONVENIENCE BUNDLES ====

class MASTER_DESIGN_TOKENS:
    """Master design token bundle - single import point for everything.

    Bundles all color, typography, spacing, and elevation tokens.

    Usage:
        ```python
        from app.gui_qt.design_system import MASTER_DESIGN_TOKENS

        # Colors
        bg = MASTER_DESIGN_TOKENS.COLORS.base_black
        text = MASTER_DESIGN_TOKENS.COLORS.text_primary
        accent = MASTER_DESIGN_TOKENS.COLORS.accent_gold

        # Typography
        font = MASTER_DESIGN_TOKENS.TYPOGRAPHY.get_font(
            TypographyScale.HEADLINE
        )

        # Spacing
        padding = MASTER_DESIGN_TOKENS.SPACING.LG

        # Elevations
        ShadowPreset.apply(widget, MASTER_DESIGN_TOKENS.ELEVATIONS.FLOATING)
        ```
    """

    COLORS = HYBRID_DESIGN_TOKENS
    TYPOGRAPHY = LuxuryTypeface
    SPACING = LuxurySpacing
    ELEVATIONS = ElevationLevel
    SHADOWS = ShadowPreset


class MASTER_COLORS:
    """Master color palette export."""

    PRIMARY = HybridColorTokens.accent_gold
    """Primary accent: warm gold."""

    SECONDARY = HybridColorTokens.accent_silver
    """Secondary accent: cool silver."""

    SURFACE = HybridColorTokens.surface_raised
    """Default surface color."""

    SURFACE_ELEVATED = HybridColorTokens.surface_floating
    """Elevated surface (floating)."""

    TEXT = HybridColorTokens.text_primary
    """Primary text color."""

    TEXT_SECONDARY = HybridColorTokens.text_secondary
    """Secondary text color."""

    BACKGROUND = HybridColorTokens.base_black
    """Background color."""

    SUCCESS = HybridColorTokens.success
    """Success state color."""

    WARNING = HybridColorTokens.warning
    """Warning state color."""

    DANGER = HybridColorTokens.danger
    """Danger state color."""


class MASTER_TYPOGRAPHY:
    """Master typography export."""

    DISPLAY = TypographyScale.DISPLAY
    """Heroic title - 48pt."""

    HEADLINE = TypographyScale.HEADLINE
    """Section heading - 32pt."""

    TITLE = TypographyScale.TITLE
    """Card title - 24pt."""

    BODY = TypographyScale.BODY
    """Body text - 14pt."""

    CAPTION = TypographyScale.CAPTION
    """Caption - 12pt."""

    LABEL = TypographyScale.LABEL
    """Label - 11pt."""

    MONO = TypographyScale.MONO
    """Monospace - 13pt."""


class MASTER_SPACING:
    """Master spacing export."""

    XS = LuxurySpacing.XS
    """Micro - 4px."""

    SM = LuxurySpacing.SM
    """Small - 8px."""

    MD = LuxurySpacing.MD
    """Medium - 16px."""

    LG = LuxurySpacing.LG
    """Large - 24px."""

    XL = LuxurySpacing.XL
    """Extra large - 32px."""

    XXL = LuxurySpacing.XXL
    """Double - 48px."""

    XXXL = LuxurySpacing.XXXL
    """Maximum - 64px."""


class MASTER_ELEVATIONS:
    """Master elevation export."""

    INSET = ElevationLevel.INSET
    """Inset/pressed - negative depth."""

    SURFACE = ElevationLevel.SURFACE
    """Surface level - default."""

    RAISED = ElevationLevel.RAISED
    """Raised - +2px shadow."""

    FLOATING = ElevationLevel.FLOATING
    """Floating - maximum elevation."""


# ==== BACKWARD COMPATIBILITY ====
# Re-export commonly used items at module level

__all__ = [
    # Token classes
    "HybridColorTokens",
    "HYBRID_DESIGN_TOKENS",
    "TypographyScale",
    "TypographyScaleConfig",
    "LuxuryTypeface",
    "LuxurySpacing",
    "ElevationLevel",
    "ShadowConfig",
    "ShadowPreset",

    # Convenience functions
    "apply_inset_shadow",
    "apply_raised_shadow",
    "apply_floating_shadow",
    "get_shadow_config",

    # Master bundles
    "MASTER_DESIGN_TOKENS",
    "MASTER_COLORS",
    "MASTER_TYPOGRAPHY",
    "MASTER_SPACING",
    "MASTER_ELEVATIONS",
]
