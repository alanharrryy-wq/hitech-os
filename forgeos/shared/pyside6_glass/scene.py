from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStackedLayout, QVBoxLayout, QWidget

from .backdrop import FrostedGlassBackdrop
from .contracts import DEFAULT_THEME_ID
from .theme import build_stylesheet


def build_glass_dialog_scene(
    host: QWidget,
    *,
    theme_id: str = DEFAULT_THEME_ID,
    margins: tuple[int, int, int, int] = (10, 10, 10, 10),
    motion_enabled: bool = True,
    apply_stylesheet: bool = True,
) -> tuple[QVBoxLayout, QWidget, FrostedGlassBackdrop]:
    """Builds the reusable glass stage/content stack used by host dialogs/windows."""

    host.setObjectName("GlassDialog")
    host.setAttribute(Qt.WA_StyledBackground, True)
    try:
        host.setAttribute(Qt.WA_TranslucentBackground, True)
    except Exception:
        pass

    if apply_stylesheet:
        host.setStyleSheet(build_stylesheet(theme_id))

    outer = QVBoxLayout(host)
    outer.setContentsMargins(*margins)
    outer.setSpacing(0)

    stage = QWidget(host)
    stage.setObjectName("GlassStage")
    stage.setAttribute(Qt.WA_StyledBackground, True)

    stack = QStackedLayout(stage)
    stack.setContentsMargins(0, 0, 0, 0)
    stack.setStackingMode(QStackedLayout.StackAll)

    backdrop = FrostedGlassBackdrop(stage, motion_enabled=motion_enabled)
    content = QWidget(stage)
    content.setObjectName("GlassContent")
    content.setAttribute(Qt.WA_StyledBackground, True)

    stack.addWidget(backdrop)
    stack.addWidget(content)
    stack.setCurrentWidget(content)
    outer.addWidget(stage)
    return outer, content, backdrop

