"""Hybrid UI Design System - Master Package

This package contains the complete design token system for the Hybrid UI
implementation across glassmorphism, neumorphism, luxury minimalism, and
kinetic physics effects.

PHASE: 1 (Design System Foundation)
DATE: 2026-03-19
STATUS: Core foundation (append-only, no modifications to existing code)

## Structure

- color_tokens: Master color definitions (luxury, glass, neumorphic, heatmap)
- typography_system: Font scales and typeface definitions
- spacing_system: Grid-based spacing (8px base)
- elevations: Elevation levels and shadow presets
- unified_palette: Single import for all tokens

## Usage

```python
from app.gui_qt.design_system import (
    HybridColorTokens,
    TypographyScale,
    LuxurySpacing,
    ElevationLevel,
)

# Access color tokens
tokens = HybridColorTokens()
bg_color = tokens.base_black

# Get typography scale
font = LuxuryTypeface.get_font(TypographyScale.HEADLINE)

# Use spacing
padding = LuxurySpacing.LG  # 24px
```

## Public API

All classes and enums are exported here for convenience.
"""

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
from .unified_palette import (
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

    # Master imports
    "MASTER_DESIGN_TOKENS",
    "MASTER_COLORS",
    "MASTER_TYPOGRAPHY",
    "MASTER_SPACING",
    "MASTER_ELEVATIONS",
]
