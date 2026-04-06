from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..common.types import ActionSpec
from ..controls.buttons import create_button
from ..controls.scale_selector import ScaleSelector
from ..controls.inputs import create_combo
from ..effects.polish import enable_card_hover
from ..effects.shadow import apply_shadow


@dataclass(slots=True)
class ToolbarRefs:
    frame: QFrame
    row: QHBoxLayout
    buttons: dict[str, QWidget]
    scale_selector: ScaleSelector | None
    theme_combo: QComboBox | None
    perf_label: QLabel | None


def build_toolbar_panel(
    parent: QWidget,
    *,
    actions: list[ActionSpec],
    on_action: Callable[[str], None],
    scale_id: str = "100",
    on_scale_changed: Callable[[str], None] | None = None,
    theme_labels: tuple[str, ...] = (),
    selected_theme_label: str = "",
    on_theme_changed: Callable[[str], None] | None = None,
) -> ToolbarRefs:
    frame = QFrame(parent)
    frame.setProperty("card", "true")
    apply_shadow(frame, blur=16.0, y_offset=6.0, alpha=12)
    enable_card_hover(frame)

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(10)

    top_row = QHBoxLayout()
    top_row.setSpacing(10)
    layout.addLayout(top_row)

    heading = QLabel("Actions", frame)
    heading.setProperty("role", "section")
    top_row.addWidget(heading, 0, Qt.AlignLeft | Qt.AlignVCenter)
    top_row.addStretch(1)

    right_stack = QVBoxLayout()
    right_stack.setSpacing(6)
    top_row.addLayout(right_stack, 0)

    scale_selector: ScaleSelector | None = None
    if on_scale_changed is not None:
        scale_selector = ScaleSelector(
            current_scale=scale_id,
            on_change=on_scale_changed,
            parent=frame,
        )
        right_stack.addWidget(scale_selector, 0, Qt.AlignRight)

    theme_combo: QComboBox | None = None
    perf_label: QLabel | None = None
    if on_theme_changed is not None and theme_labels:
        theme_combo = create_combo(theme_labels, parent=frame)
        theme_combo.setProperty("toolbar_theme", True)
        if selected_theme_label:
            idx = theme_combo.findText(selected_theme_label)
            if idx >= 0:
                theme_combo.setCurrentIndex(idx)
        theme_combo.currentTextChanged.connect(on_theme_changed)
        right_stack.addWidget(theme_combo, 0, Qt.AlignRight)

    perf_label = QLabel("perf · idle", frame)
    perf_label.setProperty("role", "perf_ghost")
    perf_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    right_stack.addWidget(perf_label, 0, Qt.AlignRight)

    row = QHBoxLayout()
    row.setSpacing(10)
    layout.addLayout(row)

    buttons: dict[str, QWidget] = {}
    for spec in actions:
        button = create_button(
            spec.label,
            spec.variant,
            icon=spec.icon,
            tooltip=spec.tooltip,
            minimum_width=spec.minimum_width,
            enabled=spec.enabled,
            callback=lambda _=False, action_id=spec.action_id: on_action(action_id),
            parent=frame,
        )
        row.addWidget(button, 0)
        buttons[spec.action_id] = button

    row.addStretch(1)
    return ToolbarRefs(
        frame=frame,
        row=row,
        buttons=buttons,
        scale_selector=scale_selector,
        theme_combo=theme_combo,
        perf_label=perf_label,
    )
