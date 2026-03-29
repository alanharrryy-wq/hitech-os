"""Color Token Definitions for Hybrid UI

Comprehensive color palette combining:
- Luxury Minimalism: Pure blacks, grays, and accents
- Glassmorphism: Translucent tokens with alpha values
- Neumorphism: Shadows, surfaces, and elevation
- Kinetic Physics: Dynamic accent colors
- 3D Heatmap: Categorical color scale

PHASE: 1 (Design System Foundation)
NEW: 2026-03-19
SAFE: No modifications to existing code
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HybridColorTokens:
    """Master color token palette for all UI components.

    This dataclass is immutable (frozen=True) to prevent accidental mutations.
    All colors are stored as hex strings for easy CSS/Qt integration.

    ## Luxury Foundation (Minimalism)
    Base colors for dark, elegant aesthetic using pure blacks and refined grays.

    ## Glassmorphic Effects
    Semi-transparent tokens for translucent, frosted glass effects.

    ## Neumorphic Surfaces
    Subtle surface colors with integrated shadow/light information.

    ## Kinetic Accents
    Dynamic accent colors (gold, copper, silver) for premium interactions.

    ## Heatmap Scale
    Categorical colors for data visualization (cool → hot).
    """

    # ==== LUXURY MINIMALISM: Pure blacks and refined grays ====
    base_black: str = "#000000"          # Pure black - absolute background
    base_dark: str = "#0a0a0a"           # Charcoal - subtle variation
    base_gray: str = "#1a1a1a"           # Dark gray - tertiary surface

    # ==== NEUMORPHIC SURFACES: Layered depth ====
    surface_inset: str = "#232d3a"       # Pressed/inset surface
    surface_raised: str = "#1a1a1a"      # Default raised surface
    surface_floating: str = "#252525"    # Maximum elevation floating
    surface_elevated: str = "#1d2531"    # Slightly elevated

    # ==== TEXT HIERARCHY ====
    text_primary: str = "#f5f5f5"        # Main text - off-white
    text_secondary: str = "#d0d0d0"      # Secondary text - light gray
    text_tertiary: str = "#5c6b7b"       # Tertiary text - stone gray
    text_muted: str = "#9aa8bc"          # Muted text - medium gray
    text_soft: str = "#7c8a9e"           # Soft text - neutral gray

    # ==== KINETIC ACCENTS: Premium colors ====
    accent_gold: str = "#d9a168"         # Primary gold - warm
    accent_gold_hover: str = "#e4b582"   # Gold on hover - brighter
    accent_gold_pressed: str = "#c8925a" # Gold on press - darker
    accent_gold_soft: str = "#36281a"    # Gold soft - background version
    accent_gold_glow: str = "#d9a1682c"  # Gold glow - with alpha

    accent_silver: str = "#c0c0c0"       # Silver - cool secondary
    accent_copper: str = "#b87333"       # Copper - warm tertiary
    accent_platinum: str = "#e5e4e2"     # Platinum - brightest accent

    # ==== GLASSMORPHIC: Translucent overlays ====
    glass_bg: str = "#1a212c"            # Glass background base
    glass_bg_light: str = "#232d3a"      # Glass background lighter
    glass_border: str = "#d9a1681f"      # Glass border with alpha
    glass_border_strong: str = "#d9a168" # Glass border opaque
    glass_overlay_soft: str = "#ffffff06" # White overlay - 4% opacity
    glass_overlay_medium: str = "#ffffff0a" # White overlay - 6% opacity
    glass_overlay_strong: str = "#ffffff14" # White overlay - 8% opacity

    # ==== SHADOWS: Neumorphic depth ====
    shadow_soft: str = "#0000004d"       # Soft shadow - 30% black
    shadow_medium: str = "#00000073"     # Medium shadow - 45% black
    shadow_hard: str = "#0000009f"       # Hard shadow - 62% black

    # ==== BORDERS & DIVIDERS ====
    border_soft: str = "#ffffff0a"       # Barely visible border
    border_subtle: str = "#263140"       # Subtle border
    border_medium: str = "#2d3848"       # Medium border
    border_strong: str = "#3f5067"       # Strong border
    divider: str = "#ffffff0a"           # Divider line

    # ==== SPECIAL EFFECTS ====
    bevel_light: str = "#ffffff12"       # Light bevel
    bevel_shadow: str = "#00000073"      # Shadow bevel
    selection: str = "#2f4058"           # Selection highlight
    focus_ring: str = "#d9a1686b"        # Focus ring glow

    # ==== INTERACTIVE STATES ====
    hover_overlay: str = "#ffffff06"     # Hover overlay
    focus_overlay: str = "#d9a1681f"     # Focus overlay
    active_overlay: str = "#d9a168"      # Active state
    disabled_overlay: str = "#66666666"  # Disabled overlay

    # ==== STATUS COLORS ====
    success: str = "#5fc794"             # Success green
    success_soft: str = "#2d4d40"        # Success soft background
    warning: str = "#d8b36d"             # Warning orange
    warning_soft: str = "#4d4428"        # Warning soft background
    danger: str = "#d58086"              # Danger red
    danger_soft: str = "#4d2d30"         # Danger soft background
    info: str = "#7fb8c1"                # Info cyan
    info_soft: str = "#2d4042"           # Info soft background

    # ==== HEATMAP SCALE (Cool → Hot) ====
    heatmap_cool: str = "#7fb8c1"        # Blue - cool/isolated (few deps)
    heatmap_warm: str = "#5fc794"        # Green - warm (some deps)
    heatmap_hot: str = "#d8b36d"         # Orange - hot (many deps)
    heatmap_vhot: str = "#d58086"        # Red - very hot (critical deps)

    # ==== CHROME & UI SURFACES ====
    toolbar_bg: str = "#111821"          # Toolbar background
    toolbar_hover: str = "#1a252f"       # Toolbar hover
    dock_title_bg: str = "#151f2b"       # Dock title bar
    menu_bg: str = "#151e28"             # Menu background
    menu_hover: str = "#1f2d3a"          # Menu hover state
    scrollbar: str = "#4f5d70"           # Scrollbar track
    scrollbar_hover: str = "#d9a168"     # Scrollbar on hover
    scrollbar_dark: str = "#3f4d60"      # Scrollbar dark variant
    splitter: str = "#2f3c4e"            # Splitter color

    # ==== CODE & MONOSPACE SURFACES ====
    code_bg: str = "#0b1118"             # Code editor background
    code_text: str = "#e8eef6"           # Code text foreground
    code_comment: str = "#6a737d"        # Code comments
    code_string: str = "#85e89d"         # Code strings
    code_keyword: str = "#f97583"        # Code keywords
    code_number: str = "#79b8ff"         # Code numbers
    code_line_bg: str = "#15202d"        # Code line highlight
    code_line_number: str = "#6a737d"    # Code line numbers

    # ==== DEPRECATED: Legacy compatibility ====
    # These are kept for backward compatibility with existing skins
    panel: str = "#1d2531"               # Panel surface
    panel_alt: str = "#232d3a"           # Panel alt
    panel_hover: str = "#2b3747"         # Panel hover
    panel_active: str = "#314258"        # Panel active


# ==== CONVENIENCE INSTANCE ====
HYBRID_DESIGN_TOKENS = HybridColorTokens()
"""Singleton instance of HybridColorTokens for direct access."""
