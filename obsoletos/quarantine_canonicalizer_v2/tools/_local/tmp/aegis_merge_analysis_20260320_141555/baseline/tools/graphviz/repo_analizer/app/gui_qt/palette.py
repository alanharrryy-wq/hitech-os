"""Color utilities for theme-neutral styling.

This module provides safe color conversion and CSS generation functions
that decouple widget styling from direct token manipulation.

All functions return CSS-valid strings suitable for stylesheets.
"""

from __future__ import annotations

from PySide6.QtGui import QColor

from .skins import SkinTokens


def token_to_css(color_hex: str) -> str:
    """
    Convert a hex color token to a CSS-valid color string.
    
    Args:
        color_hex: Hex color string (e.g., "#ff9a3d")
    
    Returns:
        CSS color string ready for stylesheets
    """
    # Validate and normalize hex format
    if not color_hex.startswith('#'):
        color_hex = '#' + color_hex

    if len(color_hex) == 7:
        return color_hex

    # Support #RRGGBBAA tokens by converting to rgba()
    if len(color_hex) == 9:
        try:
            r = int(color_hex[1:3], 16)
            g = int(color_hex[3:5], 16)
            b = int(color_hex[5:7], 16)
            a = int(color_hex[7:9], 16) / 255.0
            return f"rgba({r}, {g}, {b}, {a:.2f})"
        except ValueError:
            return "#000000"

    return "#000000"  # Fallback to black


def token_with_alpha(color_hex: str, alpha_pct: int = 100) -> str:
    """
    Convert a hex color token to an rgba CSS string with alpha control.
    
    Args:
        color_hex: Hex color string (e.g., "#ff9a3d")
        alpha_pct: Alpha percentage (0-100)
    
    Returns:
        CSS rgba string (e.g., "rgba(255, 154, 61, 0.5)")
    """
    color_hex = token_to_css(color_hex)
    
    # Parse hex to RGB
    try:
        r = int(color_hex[1:3], 16)
        g = int(color_hex[3:5], 16)
        b = int(color_hex[5:7], 16)
    except ValueError:
        return "rgba(0, 0, 0, 0.5)"
    
    # Clamp alpha to 0-100
    alpha_pct = max(0, min(100, alpha_pct))
    alpha = alpha_pct / 100.0
    
    return f"rgba({r}, {g}, {b}, {alpha:.2f})"


def glow_css(color_hex: str, intensity_hex: str = "33") -> str:
    """
    Generate a CSS rgba glow/background color with safe alpha handling.
    
    This is used for soft backgrounds under badges, pills, status indicators.
    
    Args:
        color_hex: Hex color string (e.g., "#ff9a3d")
        intensity_hex: Hex alpha value (e.g., "33" ≈ 20% opacity)
    
    Returns:
        CSS rgba string with alpha baked in
    """
    color_hex = token_to_css(color_hex)
    
    # Parse hex to RGB
    try:
        r = int(color_hex[1:3], 16)
        g = int(color_hex[3:5], 16)
        b = int(color_hex[5:7], 16)
    except ValueError:
        r = g = b = 0
    
    # Parse intensity hex (alpha channel in 0-FF range)
    try:
        alpha_value = int(intensity_hex, 16)
        alpha = alpha_value / 255.0
    except ValueError:
        alpha = 0.2
    
    return f"rgba({r}, {g}, {b}, {alpha:.2f})"


def blend_colors(start_hex: str, end_hex: str, factor: float) -> str:
    """
    Blend two hex colors by a factor (0.0 = start, 1.0 = end).
    
    Used for hover and animated color transitions.
    
    Args:
        start_hex: Starting color
        end_hex: Ending color
        factor: Blend factor (0.0 to 1.0)
    
    Returns:
        Blended color as hex string
    """
    start_hex = token_to_css(start_hex)
    end_hex = token_to_css(end_hex)
    
    try:
        # Parse both colors
        sr, sg, sb = int(start_hex[1:3], 16), int(start_hex[3:5], 16), int(start_hex[5:7], 16)
        er, eg, eb = int(end_hex[1:3], 16), int(end_hex[3:5], 16), int(end_hex[5:7], 16)
        
        # Blend
        factor = max(0.0, min(1.0, factor))
        r = int(sr + (er - sr) * factor)
        g = int(sg + (eg - sg) * factor)
        b = int(sb + (eb - sb) * factor)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    except (ValueError, IndexError):
        return start_hex


def qcolor_to_css(qcolor: QColor) -> str:
    """
    Convert a QColor object to a CSS hex string.
    
    Args:
        qcolor: QColor instance
    
    Returns:
        CSS hex color string
    """
    return qcolor.name()  # Returns "#RRGGBB"


def severity_color_css(tokens: SkinTokens, severity: str) -> str:
    """
    Get the CSS color for a severity level.
    
    Args:
        tokens: SkinTokens instance
        severity: One of "accent", "success", "warning", "danger", "muted", "neutral"
    
    Returns:
        CSS color string
    """
    match severity.lower():
        case "accent":
            return token_to_css(tokens.accent)
        case "success":
            return token_to_css(tokens.success)
        case "warning":
            return token_to_css(tokens.warning)
        case "danger":
            return token_to_css(tokens.danger)
        case "muted":
            return token_to_css(tokens.text_muted)
        case _:
            return token_to_css(tokens.border)


def severity_glow_css(tokens: SkinTokens, severity: str) -> str:
    """
    Get the CSS glow background for a severity level.
    
    Args:
        tokens: SkinTokens instance
        severity: One of "accent", "success", "warning", "danger", "muted", "neutral"
    
    Returns:
        CSS rgba string
    """
    match severity.lower():
        case "accent":
            if isinstance(tokens.accent_glow, str) and len(tokens.accent_glow) == 9 and tokens.accent_glow.startswith('#'):
                return token_to_css(tokens.accent_glow)
            return glow_css(tokens.accent, "33")
        case "success":
            return glow_css(tokens.success, "33")
        case "warning":
            return glow_css(tokens.warning, "33")
        case "danger":
            return glow_css(tokens.danger, "33")
        case "muted":
            return token_with_alpha(tokens.border, 20)
        case _:
            return token_with_alpha(tokens.border, 15)
