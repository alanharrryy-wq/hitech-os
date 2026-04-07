from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..common.types import ChipSpec
from ..controls.chips import create_chip
from ..controls.icons import icon_text
from ..effects.polish import enable_card_hover, repolish
from ..effects.shadow import apply_shadow
from ..widgets.primitives import make_separator


@dataclass(slots=True)
class HeroRefs:
    frame: QFrame
    eyebrow: QLabel
    title: QLabel
    subtitle: QLabel
    chip_stack: QVBoxLayout


def build_hero_panel(
    parent: QWidget,
    *,
    eyebrow: str,
    title: str,
    subtitle: str,
    title_icon: str | None = None,
    chips: list[ChipSpec] | None = None,
) -> HeroRefs:
    frame = QFrame(parent)
    frame.setProperty("card", "hero")
    apply_shadow(frame, blur=30.0, y_offset=10.0, alpha=24, color=QColor(7, 18, 28, 72))
    enable_card_hover(frame)

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(22, 20, 22, 20)
    layout.setSpacing(12)

    top_row = QHBoxLayout()
    top_row.setSpacing(12)
    layout.addLayout(top_row)

    title_stack = QVBoxLayout()
    title_stack.setSpacing(6)
    top_row.addLayout(title_stack, 1)

    eyebrow_label = QLabel(eyebrow, frame)
    eyebrow_label.setProperty("role", "eyebrow")
    title_stack.addWidget(eyebrow_label, 0, Qt.AlignLeft)

    title_label = QLabel(icon_text(title, title_icon), frame)
    title_label.setProperty("role", "title")
    title_stack.addWidget(title_label)

    subtitle_label = QLabel(subtitle, frame)
    subtitle_label.setProperty("role", "subtitle")
    subtitle_label.setWordWrap(True)
    title_stack.addWidget(subtitle_label)

    chip_stack = QVBoxLayout()
    chip_stack.setSpacing(8)
    top_row.addLayout(chip_stack, 0)

    for chip in chips or []:
        chip_widget = create_chip(chip.text, tone=chip.tone, icon=chip.icon, parent=frame)
        chip_stack.addWidget(chip_widget, 0, Qt.AlignRight)
    chip_stack.addStretch(1)

    line = make_separator()
    line.setProperty("tone", "glow")
    repolish(line)
    layout.addWidget(line)

    return HeroRefs(
        frame=frame,
        eyebrow=eyebrow_label,
        title=title_label,
        subtitle=subtitle_label,
        chip_stack=chip_stack,
    )

