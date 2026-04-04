from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from PySide6.QtWidgets import QWidget

from .contracts import PANEL_ROLES

VISUAL_VARIANTS: tuple[str, ...] = ('glass', 'panel', 'hero', 'chrome', 'canvas', 'flat')
VISUAL_EMPHASIS: tuple[str, ...] = ('subtle', 'normal', 'high', 'critical')
VISUAL_FX_LEVELS: tuple[str, ...] = ('off', 'soft', 'normal', 'rich')
_EMPHASIS_ALIASES = {
    'low': 'subtle',
}

_ROLE_ALIASES = {
    'shell': 'shell',
    'workspace': 'panel_workspace',
    'form': 'panel_form',
    'data': 'panel_data',
    'metrics': 'panel_metrics',
    'detail': 'panel_detail',
    'summary': 'panel_summary',
    'aux': 'panel_aux',
    'panel_workspace': 'panel_workspace',
    'panel_form': 'panel_form',
    'panel_data': 'panel_data',
    'panel_metrics': 'panel_metrics',
    'panel_detail': 'panel_detail',
    'panel_summary': 'panel_summary',
    'panel_aux': 'panel_aux',
    'hero': 'hero',
    'chrome': 'chrome',
    'status': 'status',
    'footer': 'footer',
}
for _role in PANEL_ROLES:
    _ROLE_ALIASES.setdefault(_role, f'panel_{_role}')


def _normalized(value: Any) -> str:
    return str(value or '').strip().lower()


def normalize_visual_role(value: Any, default: str = 'panel_workspace') -> str:
    return _ROLE_ALIASES.get(_normalized(value), default)


def normalize_visual_variant(value: Any, default: str = 'glass') -> str:
    token = _normalized(value)
    return token if token in VISUAL_VARIANTS else default


def normalize_visual_emphasis(value: Any, default: str = 'normal') -> str:
    token = _normalized(value)
    token = _EMPHASIS_ALIASES.get(token, token)
    return token if token in VISUAL_EMPHASIS else default


def normalize_visual_fx_level(value: Any, default: str = 'normal') -> str:
    token = _normalized(value)
    return token if token in VISUAL_FX_LEVELS else default


@dataclass(frozen=True, slots=True)
class VisualNodeSpec:
    role: str = 'panel_workspace'
    variant: str = 'glass'
    emphasis: str = 'normal'
    fx_level: str = 'normal'

    def normalized(self) -> 'VisualNodeSpec':
        return VisualNodeSpec(
            role=normalize_visual_role(self.role),
            variant=normalize_visual_variant(self.variant),
            emphasis=normalize_visual_emphasis(self.emphasis),
            fx_level=normalize_visual_fx_level(self.fx_level),
        )

    def to_dict(self) -> dict[str, str]:
        return asdict(self.normalized())


def set_visual_properties(
    widget: QWidget,
    *,
    role: Any | None = None,
    variant: Any | None = None,
    emphasis: Any | None = None,
    fx_level: Any | None = None,
) -> QWidget:
    if widget is None:
        return widget
    if role is not None:
        widget.setProperty('visualRole', normalize_visual_role(role))
    if variant is not None:
        widget.setProperty('visualVariant', normalize_visual_variant(variant))
    if emphasis is not None:
        widget.setProperty('visualEmphasis', normalize_visual_emphasis(emphasis))
    if fx_level is not None:
        widget.setProperty('visualFxLevel', normalize_visual_fx_level(fx_level))
    return widget


def visual_signature(widget: QWidget) -> dict[str, str]:
    return {
        'role': normalize_visual_role(widget.property('visualRole')),
        'variant': normalize_visual_variant(widget.property('visualVariant')),
        'emphasis': normalize_visual_emphasis(widget.property('visualEmphasis')),
        'fx_level': normalize_visual_fx_level(widget.property('visualFxLevel')),
    }


__all__ = [
    'VISUAL_EMPHASIS',
    'VISUAL_FX_LEVELS',
    'VISUAL_VARIANTS',
    'VisualNodeSpec',
    'normalize_visual_emphasis',
    'normalize_visual_fx_level',
    'normalize_visual_role',
    'normalize_visual_variant',
    'set_visual_properties',
    'visual_signature',
]
