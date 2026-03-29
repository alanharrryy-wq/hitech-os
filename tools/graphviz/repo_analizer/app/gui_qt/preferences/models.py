from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

DensityMode = Literal["compact", "comfortable", "spacious"]
ContrastMode = Literal["normal", "high"]
MotionMode = Literal["full", "reduced", "off"]
PerformanceMode = Literal["balanced", "performance"]
LayoutBehavior = Literal["single_active_tool", "legacy_docking"]


@dataclass(slots=True)
class WorkstationPreferences:
    """User-facing product preferences stored in QSettings."""

    skin_name: str
    font_family: str
    font_size: int
    density: DensityMode
    contrast: ContrastMode
    motion: MotionMode
    performance: PerformanceMode
    layout_behavior: LayoutBehavior
    include_dev_tools: bool
    enable_legacy_plugins: bool

    @classmethod
    def defaults(cls, *, skin_name: str) -> "WorkstationPreferences":
        return cls(
            skin_name=skin_name,
            font_family="System",
            font_size=11,
            density="comfortable",
            contrast="normal",
            motion="full",
            performance="balanced",
            layout_behavior="single_active_tool",
            include_dev_tools=False,
            enable_legacy_plugins=False,
        )

    def normalized(self) -> "WorkstationPreferences":
        """Return a normalized and safe preference payload."""
        density: DensityMode = "comfortable"
        if self.density in {"compact", "comfortable", "spacious"}:
            density = self.density

        contrast: ContrastMode = "normal"
        if self.contrast in {"normal", "high"}:
            contrast = self.contrast

        motion: MotionMode = "full"
        if self.motion in {"full", "reduced", "off"}:
            motion = self.motion

        performance: PerformanceMode = "balanced"
        if self.performance in {"balanced", "performance"}:
            performance = self.performance

        layout_behavior: LayoutBehavior = "single_active_tool"
        if self.layout_behavior in {"single_active_tool", "legacy_docking"}:
            layout_behavior = self.layout_behavior

        size = int(self.font_size or 11)
        size = max(10, min(28, size))

        skin_name = str(self.skin_name or "").strip() or "orange_ember"
        family = str(self.font_family or "").strip() or "System"

        return WorkstationPreferences(
            skin_name=skin_name,
            font_family=family,
            font_size=size,
            density=density,
            contrast=contrast,
            motion=motion,
            performance=performance,
            layout_behavior=layout_behavior,
            include_dev_tools=bool(self.include_dev_tools),
            enable_legacy_plugins=bool(self.enable_legacy_plugins),
        )
