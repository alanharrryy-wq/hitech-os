from __future__ import annotations

from dataclasses import dataclass

DEFAULT_THEME_ID = "silver_frost_cyan"
SUPPORTED_VARIANTS = ("selector", "progress")


@dataclass(frozen=True, slots=True)
class GlassRadiusContract:
    """Frozen visual radii copied from the current code-atlas visual DNA."""

    shell: int = 28
    shell_progress: int = 26
    window_chrome: int = 12
    hero_card: int = 22
    card: int = 18
    chip: int = 12
    input: int = 12
    button: int = 12
    progress: int = 10


GLASS_RADIUS = GlassRadiusContract()

