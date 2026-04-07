from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStackedLayout, QVBoxLayout, QWidget

from .backdrop import FrostedGlassBackdrop
from .contracts import DEFAULT_THEME_ID
from .frameless import FramelessResizeController
from .theme import build_stylesheet_exact_atlas


def build_glass_dialog_scene(
    host: QWidget,
    *,
    theme_id: str = DEFAULT_THEME_ID,
    typography_scale: str = "lg",
    variant: str = "selector",
    margins: tuple[int, int, int, int] = (6, 6, 6, 6),
    motion_enabled: bool = True,
    apply_stylesheet: bool = True,
    backdrop_factory: Optional[Callable[[QWidget], QWidget]] = None,
) -> tuple[QVBoxLayout, QWidget, QWidget]:
    """Builds the reusable glass stage/content stack used by host dialogs/windows."""

    host.setObjectName("GlassDialog")
    host.setAttribute(Qt.WA_StyledBackground, True)
    try:
        host.setAttribute(Qt.WA_TranslucentBackground, True)
    except Exception:
        pass

    if apply_stylesheet:
        host.setStyleSheet(build_stylesheet_exact_atlas(theme_id, typography_scale=typography_scale))

    if bool(host.windowFlags() & Qt.FramelessWindowHint) and not hasattr(host, "_resize_controller"):
        setattr(host, "_resize_controller", FramelessResizeController(host, margin=8))

    outer = QVBoxLayout(host)
    outer.setContentsMargins(*margins)
    outer.setSpacing(0)

    stage = QWidget(host)
    stage.setObjectName("GlassStage")
    stage.setAttribute(Qt.WA_StyledBackground, True)

    stack = QStackedLayout(stage)
    stack.setContentsMargins(0, 0, 0, 0)
    stack.setStackingMode(QStackedLayout.StackAll)

    if backdrop_factory is None:
        backdrop = FrostedGlassBackdrop(
            stage,
            theme_id=theme_id,
            variant=variant,
            motion_enabled=motion_enabled,
        )
    else:
        backdrop = backdrop_factory(stage)
        if backdrop is None:
            backdrop = FrostedGlassBackdrop(
                stage,
                theme_id=theme_id,
                variant=variant,
                motion_enabled=motion_enabled,
            )
    content = QWidget(stage)
    content.setObjectName("GlassContent")
    content.setAttribute(Qt.WA_StyledBackground, True)

    stack.addWidget(backdrop)
    stack.addWidget(content)
    stack.setCurrentWidget(content)
    outer.addWidget(stage)
    return outer, content, backdrop
