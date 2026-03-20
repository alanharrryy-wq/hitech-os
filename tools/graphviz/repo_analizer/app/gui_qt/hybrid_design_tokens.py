"""Hybrid Design Tokens - Convenience Re-Export Module

Single-file convenience import for all design system tokens.
Use this for simple imports without navigating the design_system/ package.

PHASE: 1 (Design System Foundation)
NEW: 2026-03-19
SAFE: No modifications to existing code

Usage:
    ```python
    # Option 1: Simple import (this module)
    from app.gui_qt.hybrid_design_tokens import (
        HybridColorTokens,
        TypographyScale,
        LuxurySpacing,
        MASTER_DESIGN_TOKENS,
    )

    # Option 2: Detailed import (from package)
    from app.gui_qt.design_system import (
        HybridColorTokens,
        TypographyScale,
        LuxurySpacing,
    )

    # Both are identical - use whichever feels more natural
    ```
"""

# Re-export everything from design_system package
from app.gui_qt.design_system import (
    # Color tokens
    HybridColorTokens,
    HYBRID_DESIGN_TOKENS,

    # Typography
    TypographyScale,
    TypographyScaleConfig,
    LuxuryTypeface,

    # Spacing
    LuxurySpacing,

    # Elevations
    ElevationLevel,
    ShadowConfig,
    ShadowPreset,
    apply_inset_shadow,
    apply_raised_shadow,
    apply_floating_shadow,
    get_shadow_config,

    # Master bundles
    MASTER_DESIGN_TOKENS,
    MASTER_COLORS,
    MASTER_TYPOGRAPHY,
    MASTER_SPACING,
    MASTER_ELEVATIONS,
)

__all__ = [
    # Colors
    "HybridColorTokens",
    "HYBRID_DESIGN_TOKENS",

    # Typography
    "TypographyScale",
    "TypographyScaleConfig",
    "LuxuryTypeface",

    # Spacing
    "LuxurySpacing",

    # Elevations
    "ElevationLevel",
    "ShadowConfig",
    "ShadowPreset",
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
