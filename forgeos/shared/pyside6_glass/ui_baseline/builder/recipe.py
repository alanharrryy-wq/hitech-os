from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from forgeos.shared.pyside6_glass.ui_baseline.defaults import normalize_intent



def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return slug or "generated_screen"



def derive_class_name(value: str) -> str:
    words = re.split(r"[^a-zA-Z0-9]+", value)
    words = [word for word in words if word]
    base = "".join(word.capitalize() for word in words) or "GeneratedScreen"
    return base if base.endswith("Screen") else f"{base}Screen"


@dataclass(slots=True)
class ScreenRecipe:
    screen_name: str
    class_name: str = ""
    output_dir: str = "."
    preset: str = "glass-default"
    visual_level: str = "standard"
    visual_role: str = "workspace"
    visual_variant: str = "default"
    visual_emphasis: str = "medium"
    visual_fx_level: str = "subtle"
    data_state: str = "ready"
    include_hero: bool = True
    include_main: bool = True
    include_side: bool = True
    include_footer: bool = True
    include_status: bool = True
    ingredients: list[str] = field(default_factory=list)

    def resolved_class_name(self) -> str:
        return self.class_name.strip() or derive_class_name(self.screen_name)

    def normalized_filename(self) -> str:
        base = _slugify(self.screen_name)
        return base if base.endswith("_screen") else f"{base}_screen"

    def output_path(self) -> Path:
        return Path(self.output_dir).expanduser().resolve() / f"{self.normalized_filename()}.py"

    def active_zones(self) -> list[str]:
        flags = {
            "hero": self.include_hero,
            "main": self.include_main,
            "side": self.include_side,
            "footer": self.include_footer,
            "status": self.include_status,
        }
        return [zone for zone, enabled in flags.items() if enabled]

    def normalized_visual_intent(self) -> dict[str, str]:
        intent = normalize_intent(
            {
                "visual_role": self.visual_role,
                "visual_variant": self.visual_variant,
                "visual_emphasis": self.visual_emphasis,
                "visual_fx_level": self.visual_fx_level,
                "visual_level": self.visual_level,
                "data_state": self.data_state,
                "base_preset": self.preset,
            }
        )
        return {
            "visual_role": intent.visual_role,
            "visual_variant": intent.visual_variant,
            "visual_emphasis": intent.visual_emphasis,
            "visual_fx_level": intent.visual_fx_level,
            "visual_level": intent.visual_level,
            "data_state": intent.data_state,
            "preset": intent.base_preset,
        }
