from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .intent import UIBaselineIntent

_ALLOWED = {
    "visual_role": {"workspace", "dashboard", "detail", "form", "dialog", "supporting"},
    "visual_variant": {"default", "data-heavy", "analysis", "focused", "compact"},
    "visual_emphasis": {"low", "medium", "high"},
    "visual_fx_level": {"off", "subtle", "standard", "rich"},
    "visual_level": {"performance", "standard", "premium", "showcase"},
    "data_state": {"ready", "loading", "empty", "error", "stale"},
    "base_preset": {"glass-default", "glass-quiet", "glass-contrast", "glass-ops"},
    "experience_mode": {"desktop", "touch", "embedded"},
    "data_density_bias": {"relaxed", "balanced", "dense"},
}

_ALIASES = {
    "visual_emphasis": {
        "balanced": "medium",
    },
    "visual_level": {
        "minimal": "performance",
        "rich": "premium",
    },
    "visual_fx_level": {
        "none": "off",
        "enhanced": "rich",
    },
    "visual_variant": {
        "standard": "default",
    },
}


def _coerce_dict(intent: UIBaselineIntent | Mapping[str, Any] | Any) -> dict[str, Any]:
    if isinstance(intent, Mapping):
        return dict(intent)
    if is_dataclass(intent):
        return asdict(intent)
    if isinstance(intent, UIBaselineIntent):
        return asdict(intent)

    result = {}
    for field_name in UIBaselineIntent.__dataclass_fields__:
        result[field_name] = getattr(intent, field_name, None)
    return result



def _normalize_value(field_name: str, value: Any, fallback: str) -> str:
    normalized = str(value or "").strip().lower()
    normalized = _ALIASES.get(field_name, {}).get(normalized, normalized)
    return normalized if normalized in _ALLOWED[field_name] else fallback



def normalize_intent(intent: UIBaselineIntent | Mapping[str, Any] | Any) -> UIBaselineIntent:
    """Devuelve una intención saneada con vocabulario canónico.

    Los alias heredados solo se aceptan aquí. A partir de este punto el
    paquete trabaja con valores canónicos del core.
    """

    data = _coerce_dict(intent)
    baseline = UIBaselineIntent()

    return UIBaselineIntent(
        visual_role=_normalize_value("visual_role", data.get("visual_role"), baseline.visual_role),
        visual_variant=_normalize_value("visual_variant", data.get("visual_variant"), baseline.visual_variant),
        visual_emphasis=_normalize_value("visual_emphasis", data.get("visual_emphasis"), baseline.visual_emphasis),
        visual_fx_level=_normalize_value("visual_fx_level", data.get("visual_fx_level"), baseline.visual_fx_level),
        visual_level=_normalize_value("visual_level", data.get("visual_level"), baseline.visual_level),
        data_state=_normalize_value("data_state", data.get("data_state"), baseline.data_state),
        reduced_motion=bool(data.get("reduced_motion", baseline.reduced_motion)),
        high_contrast_mode=bool(data.get("high_contrast_mode", baseline.high_contrast_mode)),
        base_preset=_normalize_value("base_preset", data.get("base_preset"), baseline.base_preset),
        experience_mode=_normalize_value("experience_mode", data.get("experience_mode"), baseline.experience_mode),
        data_density_bias=_normalize_value("data_density_bias", data.get("data_density_bias"), baseline.data_density_bias),
    )
