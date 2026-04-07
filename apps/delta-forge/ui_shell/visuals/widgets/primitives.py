from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from ..controls.icons import icon_text


def make_separator() -> QFrame:
    line = QFrame()
    line.setObjectName("Line")
    return line


def make_panel_heading(text: str, *, icon: str | None = None) -> QLabel:
    label = QLabel(icon_text(text, icon))
    label.setProperty("role", "panel_title")
    return label


def make_placeholder(
    title: str,
    subtitle: str,
    *,
    icon: str | None = None,
    parent: QWidget | None = None,
) -> QFrame:
    frame = QFrame(parent)
    frame.setProperty("slot", "placeholder")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 14, 14, 14)
    layout.setSpacing(6)

    title_label = QLabel(icon_text(title, icon), frame)
    title_label.setProperty("role", "field")
    layout.addWidget(title_label, 0, Qt.AlignLeft)

    subtitle_label = QLabel(subtitle, frame)
    subtitle_label.setProperty("role", "hint")
    subtitle_label.setWordWrap(True)
    layout.addWidget(subtitle_label)
    layout.addStretch(1)
    return frame

