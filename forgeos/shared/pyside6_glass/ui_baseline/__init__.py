"""Baseline gobernado para pantallas PySide6.

Esta capa adapta intención semántica al runtime visual oficial del core.
No tiene autoridad visual propia.
"""

from .intent import UIBaselineIntent
from .runtime import BaselineRuntimeBundle, build_runtime_for_screen, build_runtime_from_intent

__all__ = [
    "BaselineRuntimeBundle",
    "UIBaselineIntent",
    "VisualScreenTemplate",
    "build_runtime_for_screen",
    "build_runtime_from_intent",
]


def __getattr__(name: str):
    if name == "VisualScreenTemplate":
        from .screen_template import VisualScreenTemplate
        return VisualScreenTemplate
    raise AttributeError(name)
