from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QStackedLayout, QVBoxLayout, QWidget

from ..backdrop.glass_backdrop import FrostedGlassBackdrop
from ..style.stylesheet import build_stylesheet


def build_glass_dialog_scene(
    host: QWidget,
    *,
    theme_id: str,
    variant: str = "selector",
    margins: tuple[int, int, int, int] = (10, 10, 10, 10),
    motion_enabled: bool = True,
    apply_stylesheet: bool = False,
    backdrop_factory: Callable[[QWidget], QWidget] | None = None,
) -> tuple[QVBoxLayout, QWidget, FrostedGlassBackdrop]:
    host.setAttribute(Qt.WA_StyledBackground, True)
    host.setAttribute(Qt.WA_TranslucentBackground, True)
    host.setAttribute(Qt.WA_NoSystemBackground, True)
    host.setAutoFillBackground(False)

    if apply_stylesheet:
        host.setStyleSheet(build_stylesheet(theme_id))

    outer = QVBoxLayout(host)
    outer.setContentsMargins(*margins)
    outer.setSpacing(0)

    stage = QFrame(host)
    stage.setObjectName("GlassStage")
    stage.setAttribute(Qt.WA_StyledBackground, True)
    stage.setAttribute(Qt.WA_TranslucentBackground, True)
    stage.setAutoFillBackground(False)
    outer.addWidget(stage, 1)

    stack = QStackedLayout(stage)
    stack.setStackingMode(QStackedLayout.StackAll)
    stack.setContentsMargins(0, 0, 0, 0)

    backdrop_widget = (
        backdrop_factory(stage)
        if callable(backdrop_factory)
        else FrostedGlassBackdrop(stage, theme_id=theme_id, variant=variant, motion_enabled=motion_enabled)
    )
    if not isinstance(backdrop_widget, FrostedGlassBackdrop):
        raise TypeError("backdrop_factory must return FrostedGlassBackdrop")

    backdrop_widget.setObjectName("GlassBackdrop")
    content = QWidget(stage)
    content.setObjectName("GlassContent")
    content.setAttribute(Qt.WA_StyledBackground, True)
    content.setAutoFillBackground(False)

    stack.addWidget(backdrop_widget)
    stack.addWidget(content)
    stack.setCurrentWidget(content)
    return outer, content, backdrop_widget
