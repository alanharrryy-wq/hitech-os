from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .models import WorkstationPreferences

DensityScale = Literal["tight", "normal", "relaxed"]
MotionPolicy = Literal["full", "reduced", "off"]
PerformancePolicy = Literal["balanced", "performance"]


@dataclass(frozen=True, slots=True)
class RuntimePolicy:
    """Computed runtime policy derived from persisted preferences."""

    density_scale: DensityScale
    motion_policy: MotionPolicy
    performance_policy: PerformancePolicy
    high_contrast: bool
    typography_scale: float
    spacing_scale: float
    min_readable_font_pt: int

    @classmethod
    def from_preferences(cls, prefs: WorkstationPreferences) -> "RuntimePolicy":
        density_scale: DensityScale = "normal"
        if prefs.density == "compact":
            density_scale = "tight"
        elif prefs.density == "spacious":
            density_scale = "relaxed"

        motion_policy: MotionPolicy = "full"
        if prefs.motion == "reduced":
            motion_policy = "reduced"
        elif prefs.motion == "off":
            motion_policy = "off"

        performance_policy: PerformancePolicy = "balanced"
        if prefs.performance == "performance":
            performance_policy = "performance"

        base_size = max(10, min(28, int(prefs.font_size)))
        typography_scale = round(base_size / 11.0, 2)

        spacing_scale = 1.0
        if prefs.density == "compact":
            spacing_scale = 0.9
        elif prefs.density == "spacious":
            spacing_scale = 1.15

        return cls(
            density_scale=density_scale,
            motion_policy=motion_policy,
            performance_policy=performance_policy,
            high_contrast=(prefs.contrast == "high"),
            typography_scale=typography_scale,
            spacing_scale=spacing_scale,
            min_readable_font_pt=max(10, int(round(10 * typography_scale))),
        )
