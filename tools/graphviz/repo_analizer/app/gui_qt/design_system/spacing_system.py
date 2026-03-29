"""Spacing System for Hybrid UI

8px-based grid system for consistent spacing across all components.

PHASE: 1 (Design System Foundation)
NEW: 2026-03-19
SAFE: No modifications to existing code
"""

from __future__ import annotations


class LuxurySpacing:
    """8px-based spacing grid for consistent layout.

    All values are multiples of 8px for a clean, mathematical grid.
    Use these constants throughout the UI for padding, margins, gaps.

    Grid breakdown:
    - 4px  (XS)   - Micro gaps between inline elements
    - 8px  (SM)   - Small gaps, button padding
    - 16px (MD)   - Default spacing, standard margins
    - 24px (LG)   - Large gaps, section spacing
    - 32px (XL)   - Extra large, panel padding
    - 48px (XXL)  - Double spacing, heroic sections
    - 64px (XXXL) - Maximum spacing, dramatic separation

    Usage:
        ```python
        # In stylesheets
        stylesheet = f'''
            QWidget {{
                padding: {LuxurySpacing.MD}px;
                margin: {LuxurySpacing.LG}px;
            }}
        '''

        # In layouts
        layout = QVBoxLayout()
        layout.setSpacing(LuxurySpacing.SM)
        layout.setContentsMargins(
            LuxurySpacing.LG,  # left
            LuxurySpacing.MD,  # top
            LuxurySpacing.LG,  # right
            LuxurySpacing.MD,  # bottom
        )

        # Direct usage
        padding_value = LuxurySpacing.XL  # 32px
        ```
    """

    # Micro spacing
    XS = 4  # Micro gaps: minimal separation
    """4px - Minimal gap between tightly related elements."""

    # Small spacing
    SM = 8  # Small gaps: standard compact spacing
    """8px - Small gap for related elements, button padding."""

    # Default/medium spacing
    MD = 16  # Medium gaps: standard default spacing
    """16px - Standard spacing for most elements."""

    # Large spacing
    LG = 24  # Large gaps: section breaks
    """24px - Large gap for section separation."""

    # Extra large spacing
    XL = 32  # Extra large: padding in panels
    """32px - Extra large spacing for panel padding."""

    # Double spacing
    XXL = 48  # Double spacing: heroic sections
    """48px - Heroic spacing for major sections."""

    # Maximum spacing
    XXXL = 64  # Maximum: dramatic separation
    """64px - Maximum spacing for dramatic visual breaks."""

    @classmethod
    def padding(cls, size: str = "md") -> tuple[int, int, int, int]:
        """Return padding tuple (left, top, right, bottom) for common sizes.

        Args:
            size: "xs", "sm", "md", "lg", "xl", "xxl", "xxxl"

        Returns:
            Tuple of (left, top, right, bottom) in pixels

        Examples:
            ```python
            left, top, right, bottom = LuxurySpacing.padding("lg")
            widget.setContentsMargins(left, top, right, bottom)
            ```
        """
        size_map = {
            "xs": (cls.XS, cls.XS, cls.XS, cls.XS),
            "sm": (cls.SM, cls.SM, cls.SM, cls.SM),
            "md": (cls.MD, cls.MD, cls.MD, cls.MD),
            "lg": (cls.LG, cls.LG, cls.LG, cls.LG),
            "xl": (cls.XL, cls.XL, cls.XL, cls.XL),
            "xxl": (cls.XXL, cls.XXL, cls.XXL, cls.XXL),
            "xxxl": (cls.XXXL, cls.XXXL, cls.XXXL, cls.XXXL),
        }
        return size_map.get(size, size_map["md"])

    @classmethod
    def padding_horizontal(cls, size: str = "md") -> tuple[int, int, int, int]:
        """Return padding with emphasis on horizontal (left/right).

        Args:
            size: spacing size name

        Returns:
            Tuple of (left, top, right, bottom)

        Examples:
            ```python
            # Extra horizontal padding, normal vertical
            left, top, right, bottom = LuxurySpacing.padding_horizontal("lg")
            ```
        """
        size_val = getattr(cls, size.upper())
        return (size_val * 2, size_val, size_val * 2, size_val)

    @classmethod
    def padding_vertical(cls, size: str = "md") -> tuple[int, int, int, int]:
        """Return padding with emphasis on vertical (top/bottom).

        Args:
            size: spacing size name

        Returns:
            Tuple of (left, top, right, bottom)

        Examples:
            ```python
            # Normal horizontal, extra vertical padding
            left, top, right, bottom = LuxurySpacing.padding_vertical("xl")
            ```
        """
        size_val = getattr(cls, size.upper())
        return (size_val, size_val * 2, size_val, size_val * 2)

    @classmethod
    def responsive_padding(cls, role: str) -> str:
        """Return padding value as CSS string for a component role.

        Args:
            role: Component role name (card, panel, button, label, etc)

        Returns:
            CSS padding string

        Examples:
            ```python
            # For stylesheets
            padding_css = LuxurySpacing.responsive_padding("card")
            # Returns: "24px 32px"
            ```
        """
        padding_map = {
            "card": f"{cls.LG}px {cls.XL}px",      # 24px 32px
            "panel": f"{cls.XXL}px {cls.XXXL}px",  # 48px 64px
            "button": f"{cls.SM}px {cls.MD}px",    # 8px 16px
            "label": f"{cls.XS}px {cls.SM}px",     # 4px 8px
            "dialog": f"{cls.XL}px {cls.XXL}px",   # 32px 48px
            "header": f"{cls.LG}px {cls.XL}px",    # 24px 32px
            "footer": f"{cls.MD}px {cls.LG}px",    # 16px 24px
            "section": f"{cls.XXL}px 0px",         # 48px vertical
        }
        return padding_map.get(role, f"{cls.MD}px")

    @classmethod
    def gap(cls, size: str = "md") -> int:
        """Get layout gap/spacing value.

        Args:
            size: "xs", "sm", "md", "lg", "xl", "xxl", "xxxl"

        Returns:
            Gap value in pixels

        Examples:
            ```python
            layout.setSpacing(LuxurySpacing.gap("lg"))
            ```
        """
        return getattr(cls, size.upper(), cls.MD)
