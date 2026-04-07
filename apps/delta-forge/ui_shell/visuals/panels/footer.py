from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..controls.chips import create_chip
from ..effects.polish import enable_card_hover
from ..effects.shadow import apply_shadow


@dataclass(slots=True)
class FooterRefs:
    frame: QFrame
    hint_label: QLabel
    state_chip: QLabel


def build_footer(parent: QWidget, *, hint: str) -> FooterRefs:
    frame = QFrame(parent)
    frame.setProperty("card", "footer")
    apply_shadow(frame, blur=14.0, y_offset=5.0, alpha=10)
    enable_card_hover(frame)

    layout = QHBoxLayout(frame)
    layout.setContentsMargins(18, 14, 18, 14)
    layout.setSpacing(12)

    text_stack = QVBoxLayout()
    text_stack.setSpacing(4)
    layout.addLayout(text_stack, 1)

    label = QLabel("Status", frame)
    label.setProperty("role", "eyebrow")
    text_stack.addWidget(label, 0, Qt.AlignLeft)

    hint_label = QLabel(hint, frame)
    hint_label.setProperty("role", "hint")
    hint_label.setWordWrap(True)
    text_stack.addWidget(hint_label)

    state_chip = create_chip("Ready", tone="good", icon="check", parent=frame)
    layout.addWidget(state_chip, 0, Qt.AlignRight | Qt.AlignVCenter)
    return FooterRefs(frame=frame, hint_label=hint_label, state_chip=state_chip)

