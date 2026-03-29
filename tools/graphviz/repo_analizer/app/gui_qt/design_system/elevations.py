"""Elevation and Shadow System for Neumorphic UI

Defines elevation levels and their corresponding shadow properties.
Used for neumorphic depth and layering.

PHASE: 1 (Design System Foundation)
NEW: 2026-03-19
SAFE: No modifications to existing code
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class ElevationLevel(IntEnum):
    """Elevation level defines visual depth and z-order.

    Levels increase from inset (negative) to floating (maximum).
    Each level has specific shadow and visual properties.

    Usage:
        ```python
        from app.gui_qt.design_system import ElevationLevel

        # Use in neumorphic components
        ShadowPreset.apply(widget, ElevationLevel.RAISED)

        # Or directly
        if level == ElevationLevel.FLOATING:
            apply_floating_shadow(widget)
        ```
    """

    INSET = 0       # Pressed/sunken (negative depth)
    """Level 0: Inset - Pressed/sunken effect (negative z-depth)."""

    SURFACE = 1     # Default surface level
    """Level 1: Surface - Default surface elevation."""

    RAISED = 2      # Slightly raised
    """Level 2: Raised - Slightly elevated (2px shadow)."""

    FLOATING = 3    # Maximum elevation
    """Level 3: Floating - Maximum elevation, floating effect."""


@dataclass(frozen=True)
class ShadowConfig:
    """Configuration for a shadow at a specific elevation level."""

    color: str           # Shadow color (hex, can include alpha)
    blur: float          # Blur radius in pixels
    x_offset: float      # X offset in pixels
    y_offset: float      # Y offset in pixels
    spread: float = 0    # Spread radius (Qt uses blur mostly)


class ShadowPreset:
    """Factory and registry for elevation shadows.

    Shadow presets are calibrated for neumorphic depth perception.
    Use these instead of custom shadows for consistency.

    Usage:
        ```python
        # Apply preset to widget
        ShadowPreset.apply(my_widget, ElevationLevel.RAISED)

        # Get preset config
        shadow = ShadowPreset.get(ElevationLevel.FLOATING)

        # Use in stylesheet
        style = ShadowPreset.to_qss(ElevationLevel.RAISED)
        ```
    """

    # Shadow configurations per elevation level
    _PRESETS = {
        ElevationLevel.INSET: ShadowConfig(
            color="#00000073",  # Dark shadow for inset
            blur=2,
            x_offset=0,
            y_offset=-1,  # Negative = inset appearance
        ),
        ElevationLevel.SURFACE: ShadowConfig(
            color="#0000004d",  # Medium shadow
            blur=8,
            x_offset=0,
            y_offset=2,
        ),
        ElevationLevel.RAISED: ShadowConfig(
            color="#00000047",  # Lighter shadow
            blur=16,
            x_offset=0,
            y_offset=8,
        ),
        ElevationLevel.FLOATING: ShadowConfig(
            color="#0000005f",  # Full shadow
            blur=24,
            x_offset=0,
            y_offset=12,
        ),
    }

    @classmethod
    def get(cls, level: ElevationLevel) -> ShadowConfig:
        """Get shadow config for an elevation level.

        Args:
            level: ElevationLevel enum

        Returns:
            ShadowConfig with blur, offset, and color

        Examples:
            ```python
            shadow = ShadowPreset.get(ElevationLevel.RAISED)
            print(shadow.blur)  # 16
            ```
        """
        return cls._PRESETS.get(level, cls._PRESETS[ElevationLevel.SURFACE])

    @classmethod
    def apply(cls, widget, level: ElevationLevel) -> None:
        """Apply elevation shadow to a widget.

        Creates QGraphicsDropShadowEffect with preset values.

        Args:
            widget: QWidget to apply shadow to
            level: ElevationLevel enum

        Examples:
            ```python
            from PySide6.QtWidgets import QFrame
            panel = QFrame()
            ShadowPreset.apply(panel, ElevationLevel.FLOATING)
            ```
        """
        from PySide6.QtGui import QColor
        from PySide6.QtWidgets import QGraphicsDropShadowEffect

        shadow_config = cls.get(level)

        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(shadow_config.blur)
        effect.setOffset(shadow_config.x_offset, shadow_config.y_offset)
        effect.setColor(QColor(shadow_config.color))

        widget.setGraphicsEffect(effect)

    @classmethod
    def to_qss(cls, level: ElevationLevel) -> str:
        """Convert elevation to Qt stylesheet box-shadow.

        Args:
            level: ElevationLevel enum

        Returns:
            Qt stylesheet box-shadow declaration

        Note:
            Qt stylesheets use a different syntax than CSS.
            Format: box-shadow: x y blur spread color

        Examples:
            ```python
            qss = ShadowPreset.to_qss(ElevationLevel.RAISED)
            # Returns: "box-shadow: 0px 8px 16px #00000047;"
            ```
        """
        shadow = cls.get(level)
        return (
            f"box-shadow: "
            f"{shadow.x_offset:.0f}px "
            f"{shadow.y_offset:.0f}px "
            f"{shadow.blur:.0f}px "
            f"{shadow.color};"
        )

    @classmethod
    def get_all(cls) -> dict[int, ShadowConfig]:
        """Get all shadow presets as dictionary.

        Returns:
            Dictionary mapping ElevationLevel → ShadowConfig
        """
        return cls._PRESETS.copy()


# Convenience functions for common elevations
def apply_inset_shadow(widget) -> None:
    """Apply inset/pressed shadow."""
    ShadowPreset.apply(widget, ElevationLevel.INSET)


def apply_raised_shadow(widget) -> None:
    """Apply raised shadow."""
    ShadowPreset.apply(widget, ElevationLevel.RAISED)


def apply_floating_shadow(widget) -> None:
    """Apply floating shadow (maximum elevation)."""
    ShadowPreset.apply(widget, ElevationLevel.FLOATING)


def get_shadow_config(level: ElevationLevel) -> ShadowConfig:
    """Convenience: Get shadow config."""
    return ShadowPreset.get(level)
