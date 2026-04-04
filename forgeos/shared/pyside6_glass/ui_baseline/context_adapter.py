from __future__ import annotations

import inspect
from dataclasses import dataclass, fields, is_dataclass
from importlib import import_module
from typing import Any

from .intent import UIBaselineIntent

_CONTEXT_IMPORT_CANDIDATES = (
    ("forgeos.shared.pyside6_glass.visual_context", "VisualIntelligenceContext"),
    ("forgeos.shared.pyside6_glass.core.visual_context", "VisualIntelligenceContext"),
    ("forgeos.shared.pyside6_glass.runtime.visual_context", "VisualIntelligenceContext"),
    ("forgeos.shared.pyside6_glass.runtime.context", "VisualIntelligenceContext"),
    ("forgeos.shared.pyside6_glass.core.context", "VisualIntelligenceContext"),
    ("forgeos.shared.pyside6_glass.runtime", "VisualIntelligenceContext"),
    ("forgeos.shared.pyside6_glass.core.runtime", "VisualIntelligenceContext"),
)



def _load_core_context_class() -> type[Any] | None:
    for module_path, class_name in _CONTEXT_IMPORT_CANDIDATES:
        try:
            module = import_module(module_path)
        except Exception:
            continue

        candidate = getattr(module, class_name, None)
        if inspect.isclass(candidate):
            return candidate
    return None


CoreVisualIntelligenceContext = _load_core_context_class()


@dataclass(frozen=True, slots=True)
class _FallbackVisualIntelligenceContext:
    """Representación mínima del contexto esperado por el runtime oficial."""

    experience_mode: str
    requested_visual_level: str
    base_preset: str
    data_state: str
    reduced_motion: bool
    high_contrast_mode: bool
    data_density_bias: str
    visual_role: str
    visual_variant: str
    visual_emphasis: str
    visual_fx_level: str


VisualIntelligenceContext = CoreVisualIntelligenceContext or _FallbackVisualIntelligenceContext



def _context_payload(intent: UIBaselineIntent) -> dict[str, Any]:
    return {
        "experience_mode": intent.experience_mode,
        "requested_visual_level": intent.visual_level,
        "visual_level": intent.visual_level,
        "base_preset": intent.base_preset,
        "preset": intent.base_preset,
        "data_state": intent.data_state,
        "reduced_motion": intent.reduced_motion,
        "high_contrast_mode": intent.high_contrast_mode,
        "high_contrast": intent.high_contrast_mode,
        "data_density_bias": intent.data_density_bias,
        "visual_role": intent.visual_role,
        "role": intent.visual_role,
        "visual_variant": intent.visual_variant,
        "variant": intent.visual_variant,
        "visual_emphasis": intent.visual_emphasis,
        "emphasis": intent.visual_emphasis,
        "visual_fx_level": intent.visual_fx_level,
        "fx_level": intent.visual_fx_level,
    }



def _build_with_signature(context_type: type[Any], payload: dict[str, Any]) -> Any:
    signature = inspect.signature(context_type)
    parameters = signature.parameters

    if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in parameters.values()):
        return context_type(**payload)

    accepted = {}
    for name, parameter in parameters.items():
        if name == "self":
            continue
        if name in payload:
            accepted[name] = payload[name]
        elif parameter.default is inspect.Parameter.empty:
            raise TypeError(f"Falta parámetro requerido para {context_type.__name__}: {name}")

    return context_type(**accepted)



def _build_dataclass_like(context_type: type[Any], payload: dict[str, Any]) -> Any:
    accepted = {field.name: payload[field.name] for field in fields(context_type) if field.name in payload}
    return context_type(**accepted)



def _build_with_introspection(context_type: type[Any], payload: dict[str, Any]) -> Any:
    if is_dataclass(context_type):
        return _build_dataclass_like(context_type, payload)

    try:
        return _build_with_signature(context_type, payload)
    except (TypeError, ValueError):
        pass

    init = getattr(context_type, "__init__", None)
    if callable(init):
        try:
            signature = inspect.signature(init)
            parameters = signature.parameters
            accepted = {}
            for name, parameter in parameters.items():
                if name == "self":
                    continue
                if name in payload:
                    accepted[name] = payload[name]
                elif parameter.default is inspect.Parameter.empty:
                    raise TypeError(f"Falta parámetro requerido para {context_type.__name__}: {name}")
            return context_type(**accepted)
        except (TypeError, ValueError):
            pass

    return context_type(**payload)



def intent_to_visual_context(intent: UIBaselineIntent) -> VisualIntelligenceContext:
    """Traduce intención baseline a contexto visual compatible con el core.

    Intenta cargar la clase oficial desde varios paths probables y construirla
    con introspección para tolerar cambios menores de firma.
    """

    payload = _context_payload(intent)

    if CoreVisualIntelligenceContext is not None:
        try:
            return _build_with_introspection(CoreVisualIntelligenceContext, payload)
        except Exception:
            pass

    return _FallbackVisualIntelligenceContext(
        experience_mode=intent.experience_mode,
        requested_visual_level=intent.visual_level,
        base_preset=intent.base_preset,
        data_state=intent.data_state,
        reduced_motion=intent.reduced_motion,
        high_contrast_mode=intent.high_contrast_mode,
        data_density_bias=intent.data_density_bias,
        visual_role=intent.visual_role,
        visual_variant=intent.visual_variant,
        visual_emphasis=intent.visual_emphasis,
        visual_fx_level=intent.visual_fx_level,
    )
