from __future__ import annotations

from dataclasses import dataclass

from ..appearance import AppearanceProfile, AppearanceTokens, EffectsProfile, resolve_appearance_tokens


@dataclass(frozen=True, slots=True)
class ShadowMaterialSpec:
    blur: float
    x_offset: float
    y_offset: float
    alpha: int
    enabled: bool = True


def build_shadow_spec(
    tokens: AppearanceTokens,
    *,
    effects: EffectsProfile | None = None,
    emphasis: str = "normal",
) -> ShadowMaterialSpec:
    emphasis_key = str(emphasis or "normal").strip().lower()
    emphasis_scale = {
        "subtle": 0.82,
        "normal": 1.0,
        "high": 1.12,
        "critical": 1.24,
    }.get(emphasis_key, 1.0)
    fx_enabled = True if effects is None else bool(effects.shadow_enabled)
    enabled = bool(fx_enabled and tokens.elevation_scale > 0.0)
    return ShadowMaterialSpec(
        blur=max(0.0, float(tokens.shadow_blur) * emphasis_scale),
        x_offset=0.0,
        y_offset=max(0.0, float(tokens.shadow_offset_y) * min(1.2, max(0.75, emphasis_scale))),
        alpha=max(0, min(255, int(round(float(tokens.shadow_alpha) * min(1.2, emphasis_scale))))),
        enabled=enabled,
    )


def shadow_spec_from_profiles(
    profile: AppearanceProfile,
    effects: EffectsProfile | None = None,
    *,
    emphasis: str = "normal",
) -> ShadowMaterialSpec:
    resolved_effects = (effects or EffectsProfile.from_appearance(profile)).normalized()
    tokens = resolve_appearance_tokens(profile, resolved_effects)
    return build_shadow_spec(tokens, effects=resolved_effects, emphasis=emphasis)


__all__ = ["ShadowMaterialSpec", "build_shadow_spec", "shadow_spec_from_profiles"]
