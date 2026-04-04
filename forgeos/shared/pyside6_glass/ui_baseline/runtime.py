from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from importlib import import_module
from typing import Any, Callable

from .context_adapter import VisualIntelligenceContext, intent_to_visual_context
from .defaults import normalize_intent
from .intent import UIBaselineIntent


@dataclass(slots=True)
class BaselineRuntimeBundle:
    """Paquete de runtime construido desde intención semántica."""

    intent: UIBaselineIntent
    visual_context: VisualIntelligenceContext
    visual_runtime: Any
    runtime_factory_name: str
    is_fallback: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)


class NullVisualRuntime:
    """Fallback explícito y delgado.

    No define autoridad visual alternativa. Solo conserva contrato para que
    la screen pueda vivir mientras el core oficial no esté disponible.
    """

    def __init__(self, context: VisualIntelligenceContext, reason: str) -> None:
        self.context = context
        self.reason = reason
        self.is_fallback = True

    def attach_to(self, widget: Any) -> None:
        setattr(widget, "_ui_baseline_fallback_runtime", self)

    def describe(self) -> str:
        return f"Fallback activo: {self.reason}"



def _candidate_modules() -> tuple[str, ...]:
    return (
        "forgeos.shared.pyside6_glass.runtime",
        "forgeos.shared.pyside6_glass.runtime.factory",
        "forgeos.shared.pyside6_glass.runtime_factory",
        "forgeos.shared.pyside6_glass.visual_runtime",
        "forgeos.shared.pyside6_glass.core.runtime",
        "forgeos.shared.pyside6_glass.core.runtime.factory",
        "forgeos.shared.pyside6_glass.core.visual_runtime",
    )



def _resolve_runtime_factory() -> tuple[str | None, Callable[..., Any] | None]:
    container_names = (
        "runtime_factory",
        "visual_runtime_factory",
        "factory",
        "runtime",
        "visual_runtime",
    )

    for module_name in _candidate_modules():
        try:
            module = import_module(module_name)
        except Exception:
            continue

        direct = getattr(module, "create_visual_runtime", None)
        if callable(direct):
            return module_name, direct

        for container_name in container_names:
            container = getattr(module, container_name, None)
            factory = getattr(container, "create_visual_runtime", None)
            if callable(factory):
                return f"{module_name}.{container_name}", factory

    return None, None



def _context_to_kwargs(context: VisualIntelligenceContext) -> dict[str, Any]:
    if is_dataclass(context):
        return asdict(context)
    if hasattr(context, "__dict__"):
        return dict(vars(context))

    result: dict[str, Any] = {}
    for name in dir(context):
        if name.startswith("_"):
            continue
        try:
            value = getattr(context, name)
        except Exception:
            continue
        if callable(value):
            continue
        result[name] = value
    return result



def _invoke_factory(factory: Callable[..., Any], context: VisualIntelligenceContext) -> Any:
    payload = _context_to_kwargs(context)
    invocation_variants = (
        lambda: factory(context),
        lambda: factory(context=context),
        lambda: factory(visual_context=context),
        lambda: factory(visual_intelligence_context=context),
        lambda: factory(**payload),
    )
    last_error: Exception | None = None

    for invoke in invocation_variants:
        try:
            return invoke()
        except TypeError as exc:
            last_error = exc

    if last_error is not None:
        raise last_error
    raise RuntimeError("No se pudo invocar create_visual_runtime(...).")



def intent_from_screen(screen: Any) -> UIBaselineIntent:
    """Extrae intención desde una screen o clase compatible."""

    baseline = UIBaselineIntent()
    screen_type = type(screen)

    raw_intent = UIBaselineIntent(
        visual_role=getattr(screen, "visual_role", getattr(screen_type, "visual_role", baseline.visual_role)),
        visual_variant=getattr(screen, "visual_variant", getattr(screen_type, "visual_variant", baseline.visual_variant)),
        visual_emphasis=getattr(screen, "visual_emphasis", getattr(screen_type, "visual_emphasis", baseline.visual_emphasis)),
        visual_fx_level=getattr(screen, "visual_fx_level", getattr(screen_type, "visual_fx_level", baseline.visual_fx_level)),
        visual_level=getattr(screen, "visual_level", getattr(screen_type, "visual_level", baseline.visual_level)),
        data_state=getattr(screen, "data_state", getattr(screen_type, "data_state", baseline.data_state)),
        reduced_motion=getattr(screen, "reduced_motion", getattr(screen_type, "reduced_motion", baseline.reduced_motion)),
        high_contrast_mode=getattr(
            screen,
            "high_contrast_mode",
            getattr(screen_type, "high_contrast_mode", baseline.high_contrast_mode),
        ),
        base_preset=getattr(screen, "base_preset", getattr(screen_type, "base_preset", baseline.base_preset)),
        experience_mode=getattr(screen, "experience_mode", getattr(screen_type, "experience_mode", baseline.experience_mode)),
        data_density_bias=getattr(
            screen,
            "data_density_bias",
            getattr(screen_type, "data_density_bias", baseline.data_density_bias),
        ),
    )
    return normalize_intent(raw_intent)



def build_runtime_from_intent(intent: UIBaselineIntent) -> BaselineRuntimeBundle:
    """Normaliza intención, crea contexto visual e invoca el runtime oficial."""

    normalized = normalize_intent(intent)
    visual_context = intent_to_visual_context(normalized)
    module_name, factory = _resolve_runtime_factory()

    if factory is None:
        reason = "No se encontró create_visual_runtime(...) en los módulos conocidos."
        fallback = NullVisualRuntime(visual_context, reason)
        return BaselineRuntimeBundle(
            intent=normalized,
            visual_context=visual_context,
            visual_runtime=fallback,
            runtime_factory_name="fallback.null_runtime",
            is_fallback=True,
            notes=(
                reason,
                "El fallback no resuelve apariencia final y no compite con el core.",
            ),
        )

    try:
        visual_runtime = _invoke_factory(factory, visual_context)
        return BaselineRuntimeBundle(
            intent=normalized,
            visual_context=visual_context,
            visual_runtime=visual_runtime,
            runtime_factory_name=f"{module_name}.create_visual_runtime",
            is_fallback=False,
            notes=("Runtime oficial resuelto correctamente.",),
        )
    except Exception as exc:
        reason = f"Fallo al invocar el runtime oficial: {exc}"
        fallback = NullVisualRuntime(visual_context, reason)
        return BaselineRuntimeBundle(
            intent=normalized,
            visual_context=visual_context,
            visual_runtime=fallback,
            runtime_factory_name=f"{module_name}.create_visual_runtime",
            is_fallback=True,
            notes=(
                reason,
                "El fallback conserva el contrato y deja la autoridad visual al core.",
            ),
        )



def build_runtime_for_screen(screen: Any) -> BaselineRuntimeBundle:
    """Conveniencia para construir runtime directamente desde una screen."""

    return build_runtime_from_intent(intent_from_screen(screen))
