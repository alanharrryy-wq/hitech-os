from __future__ import annotations

from dataclasses import dataclass

VISUAL_LEVELS = ("performance", "standard", "premium", "showcase")
VISUAL_FX_LEVELS = ("off", "subtle", "standard", "rich")
VISUAL_EMPHASIS_LEVELS = ("low", "medium", "high")


@dataclass(frozen=True, slots=True)
class UIBaselineIntent:
    """Contrato semántico mínimo para una pantalla gobernada.

    Este contrato no define apariencia final. Solo expresa intención para
    que el core pueda resolver la experiencia visual oficial.

    Vocabulario canónico:

    - visual_level: performance | standard | premium | showcase
    - visual_fx_level: off | subtle | standard | rich
    - visual_emphasis: low | medium | high
    """

    visual_role: str = "workspace"
    visual_variant: str = "default"
    visual_emphasis: str = "medium"
    visual_fx_level: str = "subtle"
    visual_level: str = "standard"
    data_state: str = "ready"
    reduced_motion: bool = False
    high_contrast_mode: bool = False
    base_preset: str = "glass-default"
    experience_mode: str = "desktop"
    data_density_bias: str = "balanced"
