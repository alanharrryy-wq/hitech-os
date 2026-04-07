from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QLayout, QWidget

from ..common.helpers import clean_text

_BASE_MARGINS_PROP = "_base_margins"
_BASE_SPACING_PROP = "_base_spacing"


@dataclass(frozen=True, slots=True)
class ScaleProfile:
    scale_id: str
    label: str
    factor: float

    def px(self, value: int | float, minimum: int = 1) -> int:
        return max(int(minimum), int(round(float(value) * self.factor)))


_SCALE_PRESETS: tuple[ScaleProfile, ...] = (
    ScaleProfile("90", "90%", 0.90),
    ScaleProfile("100", "100%", 1.00),
    ScaleProfile("110", "110%", 1.10),
    ScaleProfile("125", "125%", 1.25),
    ScaleProfile("150", "150%", 1.50),
)

_SCALE_BY_ID: dict[str, ScaleProfile] = {preset.scale_id: preset for preset in _SCALE_PRESETS}
_SCALE_BY_LABEL: dict[str, ScaleProfile] = {preset.label.lower(): preset for preset in _SCALE_PRESETS}


def all_scales() -> tuple[ScaleProfile, ...]:
    return _SCALE_PRESETS


def normalize_scale(scale: Any) -> str:
    if isinstance(scale, (int, float)):
        numeric = int(round(float(scale)))
        if numeric in {90, 100, 110, 125, 150}:
            return str(numeric)
    cleaned = clean_text(scale).lower().replace("%", "")
    if cleaned in _SCALE_BY_ID:
        return cleaned
    label_match = _SCALE_BY_LABEL.get(f"{cleaned}%")
    if label_match is not None:
        return label_match.scale_id
    return "100"


def resolve_scale(scale: Any) -> ScaleProfile:
    scale_id = normalize_scale(scale)
    return _SCALE_BY_ID.get(scale_id, _SCALE_BY_ID["100"])


def _store_layout_base(layout: QLayout) -> None:
    if layout.property(_BASE_MARGINS_PROP) is None:
        margins = layout.contentsMargins()
        layout.setProperty(
            _BASE_MARGINS_PROP,
            (
                margins.left(),
                margins.top(),
                margins.right(),
                margins.bottom(),
            ),
        )
    if layout.property(_BASE_SPACING_PROP) is None:
        layout.setProperty(_BASE_SPACING_PROP, int(layout.spacing()))


def _scale_layout(layout: QLayout, profile: ScaleProfile) -> None:
    _store_layout_base(layout)
    base_margins = layout.property(_BASE_MARGINS_PROP)
    if isinstance(base_margins, (tuple, list)) and len(base_margins) == 4:
        layout.setContentsMargins(
            profile.px(base_margins[0], 0),
            profile.px(base_margins[1], 0),
            profile.px(base_margins[2], 0),
            profile.px(base_margins[3], 0),
        )

    base_spacing = layout.property(_BASE_SPACING_PROP)
    if isinstance(base_spacing, int) and base_spacing >= 0:
        layout.setSpacing(profile.px(base_spacing, 0))

    for index in range(layout.count()):
        item = layout.itemAt(index)
        child_layout = item.layout()
        if child_layout is not None:
            _scale_layout(child_layout, profile)
        child_widget = item.widget()
        if child_widget is not None and child_widget.layout() is not None:
            _scale_layout(child_widget.layout(), profile)


def apply_layout_scale(target: QWidget | QLayout | QObject | None, scale: Any) -> None:
    if target is None:
        return
    profile = resolve_scale(scale)

    if isinstance(target, QWidget):
        layout = target.layout()
        if layout is not None:
            _scale_layout(layout, profile)
        return
    if isinstance(target, QLayout):
        _scale_layout(target, profile)
        return
    if isinstance(target, QObject):
        for child in target.children():
            if isinstance(child, QWidget):
                apply_layout_scale(child, profile.scale_id)
            elif isinstance(child, QLayout):
                _scale_layout(child, profile)
