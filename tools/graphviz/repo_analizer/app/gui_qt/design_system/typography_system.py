"""Typography System for Hybrid UI

Comprehensive typography scale with:
- Multiple size tiers (DISPLAY, HEADLINE, BODY, etc)
- Font family management (Inter, IBM Plex)
- Letter spacing precision
- Weight definitions
- Font instance factory

PHASE: 1 (Design System Foundation)
NEW: 2026-03-19
SAFE: No modifications to existing code
"""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass

from PySide6.QtGui import QFont


@dataclass(frozen=True)
class TypographyScaleConfig:
    """Configuration for a single typography scale level."""

    size: int                    # Point size
    weight: int                  # Qt weight (0-900, usually 100-700)
    letter_spacing: float        # Em units (-0.5 to +1.0)
    line_height: str | None = None  # Optional line height (CSS style)
    family: str | None = None    # Optional override family


class TypographyScale(Enum):
    """Typography scale enum with all definition levels.

    Used to define semantic typography levels across the UI.
    Never instantiate - use as enums in LuxuryTypeface.get_font().

    Examples:
        ```python
        font = LuxuryTypeface.get_font(TypographyScale.HEADLINE)
        font = LuxuryTypeface.get_font(TypographyScale.BODY, italic=True)
        font = LuxuryTypeface.get_font(TypographyScale.LABEL)
        ```
    """

    DISPLAY = TypographyScaleConfig(
        size=48,
        weight=300,  # Light
        letter_spacing=-0.02,
        family="Inter",
    )
    """Heroic title - 48pt, light weight. Use for main page titles."""

    HEADLINE = TypographyScaleConfig(
        size=32,
        weight=400,  # Regular
        letter_spacing=-0.01,
        family="Inter",
    )
    """Section heading - 32pt, regular weight. Use for major sections."""

    TITLE = TypographyScaleConfig(
        size=24,
        weight=500,  # Medium
        letter_spacing=0,
        family="Inter",
    )
    """Card title - 24pt, medium weight. Use for card headings."""

    BODY = TypographyScaleConfig(
        size=14,
        weight=400,  # Regular
        letter_spacing=0,
        family="Inter",
    )
    """Main body text - 14pt, regular. Use for primary content."""

    BODY_SMALL = TypographyScaleConfig(
        size=13,
        weight=400,
        letter_spacing=0,
        family="Inter",
    )
    """Small body - 13pt. Use for secondary content."""

    CAPTION = TypographyScaleConfig(
        size=12,
        weight=400,  # Regular
        letter_spacing=0.01,
        family="Inter",
    )
    """Caption text - 12pt. Use for metadata, timestamps."""

    LABEL = TypographyScaleConfig(
        size=11,
        weight=500,  # Medium
        letter_spacing=0.05,
        family="Inter",
    )
    """Label - 11pt, medium, wide spacing. Use for UI labels, tags."""

    MONO = TypographyScaleConfig(
        size=13,
        weight=400,
        letter_spacing=0,
        family="IBM Plex Mono",
    )
    """Monospace code - 13pt. Use for code/technical content."""

    MONO_SMALL = TypographyScaleConfig(
        size=11,
        weight=400,
        letter_spacing=0,
        family="IBM Plex Mono",
    )
    """Small monospace - 11pt. Use for inline code, line numbers."""


class LuxuryTypeface:
    """Factory for creating QFont instances from typography scales.

    All fonts are created with proper hints and rendering for premium appearance.

    Usage:
        ```python
        # Get a standard font
        font = LuxuryTypeface.get_font(TypographyScale.BODY)

        # Get italic variant
        italic_font = LuxuryTypeface.get_font(TypographyScale.BODY, italic=True)

        # Get monospace
        mono = LuxuryTypeface.get_mono_font(TypographyScale.MONO)

        # Apply to widget
        label = QLabel("Text")
        label.setFont(font)
        ```
    """

    # Fallback families for better compatibility
    PRIMARY_FAMILIES = ["Inter", "Segoe UI", "Roboto", "System"]
    SECONDARY_FAMILIES = ["IBM Plex Sans", "Fira Sans", "Droid Sans"]
    MONOSPACE_FAMILIES = ["IBM Plex Mono", "Fira Code", "Courier New"]

    @classmethod
    def get_font(
        cls,
        scale: TypographyScale,
        italic: bool = False,
        strikeout: bool = False,
    ) -> QFont:
        """Create QFont from typography scale.

        Args:
            scale: TypographyScale enum value
            italic: Whether to make the font italic
            strikeout: Whether to add strikethrough

        Returns:
            Configured QFont instance ready to use

        Examples:
            ```python
            # Basic usage
            font = LuxuryTypeface.get_font(TypographyScale.HEADLINE)

            # With modifications
            font = LuxuryTypeface.get_font(
                TypographyScale.BODY,
                italic=True
            )
            ```
        """
        config = scale.value

        # Try to use the preferred family, fallback to alternates
        family = config.family or cls.PRIMARY_FAMILIES[0]

        font = QFont(family)

        # Set size (in points)
        font.setPointSize(config.size)

        # Set weight (map integer weight to QFont.Weight)
        # Weight values: 100=Thin, 300=Light, 400=Normal, 500=Medium, 700=Bold, 900=Black
        weight_value = config.weight
        if weight_value <= 300:
            font.setWeight(QFont.Weight.Light)
        elif weight_value <= 400:
            font.setWeight(QFont.Weight.Normal)
        elif weight_value <= 500:
            font.setWeight(QFont.Weight.Medium)
        elif weight_value <= 600:
            font.setWeight(QFont.Weight.SemiBold)
        elif weight_value <= 700:
            font.setWeight(QFont.Weight.Bold)
        else:
            font.setWeight(QFont.Weight.Black)

        # Set letter spacing (as percentage offset)
        # Qt PercentageSpacing: 100 = normal, 90 = -10%, 110 = +10%
        percentage_spacing = 100 + int(config.letter_spacing * 100)
        font.setLetterSpacing(QFont.PercentageSpacing, percentage_spacing)

        # Set style variants
        if italic:
            font.setItalic(True)

        if strikeout:
            font.setStrikeOut(True)

        # Hints for better rendering
        font.setStyleStrategy(QFont.PreferAntialias)

        return font

    @classmethod
    def get_mono_font(
        cls,
        scale: TypographyScale | None = None,
        italic: bool = False,
    ) -> QFont:
        """Create monospace QFont, optionally from a scale.

        Args:
            scale: Optional TypographyScale (will use size/weight)
                   If None, uses MONO scale
            italic: Whether to make italic

        Returns:
            Monospace QFont instance

        Examples:
            ```python
            # Use standard mono scale
            font = LuxuryTypeface.get_mono_font()

            # Use custom size from another scale
            font = LuxuryTypeface.get_mono_font(TypographyScale.CAPTION)
            ```
        """
        if scale is None:
            return cls.get_font(TypographyScale.MONO, italic=italic)

        # Get config from scale
        config = scale.value

        # Try monospace families
        family = cls.MONOSPACE_FAMILIES[0]

        font = QFont(family)
        font.setPointSize(config.size)

        # Map weight to QFont.Weight
        weight_value = config.weight
        if weight_value <= 300:
            font.setWeight(QFont.Weight.Light)
        elif weight_value <= 400:
            font.setWeight(QFont.Weight.Normal)
        elif weight_value <= 500:
            font.setWeight(QFont.Weight.Medium)
        elif weight_value <= 600:
            font.setWeight(QFont.Weight.SemiBold)
        elif weight_value <= 700:
            font.setWeight(QFont.Weight.Bold)
        else:
            font.setWeight(QFont.Weight.Black)

        if italic:
            font.setItalic(True)

        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFixedPitch(True)  # Ensure fixed-width

        return font

    @classmethod
    def get_display_font(cls) -> QFont:
        """Convenience: Get DISPLAY scale font."""
        return cls.get_font(TypographyScale.DISPLAY)

    @classmethod
    def get_headline_font(cls) -> QFont:
        """Convenience: Get HEADLINE scale font."""
        return cls.get_font(TypographyScale.HEADLINE)

    @classmethod
    def get_body_font(cls) -> QFont:
        """Convenience: Get BODY scale font."""
        return cls.get_font(TypographyScale.BODY)

    @classmethod
    def get_caption_font(cls) -> QFont:
        """Convenience: Get CAPTION scale font."""
        return cls.get_font(TypographyScale.CAPTION)

    @classmethod
    def get_label_font(cls) -> QFont:
        """Convenience: Get LABEL scale font."""
        return cls.get_font(TypographyScale.LABEL)

    @classmethod
    def get_mono_font_std(cls) -> QFont:
        """Convenience: Get MONO scale font."""
        return cls.get_mono_font(TypographyScale.MONO)
