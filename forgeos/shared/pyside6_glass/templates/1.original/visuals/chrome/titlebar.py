from __future__ import annotations

from typing import Any, Callable, Optional

from PySide6.QtCore import QEvent, QObject, QPoint, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget

from ..common.constants import APP_TITLE
from ..common.helpers import clean_text
from ..controls.icons import resolve_icon
from ..style.scale import resolve_scale


def _global_point_from_event(event: Any) -> QPoint:
    try:
        return event.globalPosition().toPoint()
    except Exception:
        return QPoint()


def _local_point_from_event(event: Any) -> QPoint:
    try:
        return event.position().toPoint()
    except Exception:
        return QPoint()


class WindowChromeBar(QFrame):
    def __init__(
        self,
        host: QWidget,
        *,
        title: str,
        on_close: Optional[Callable[[], Any]] = None,
        allow_minimize: bool = True,
        allow_maximize: bool = True,
        title_icon: str | None = "workspace",
    ) -> None:
        self._host = host
        super().__init__(host)
        self._on_close = on_close
        self._allow_maximize = bool(allow_maximize)
        self._dragging = False
        self._drag_offset = QPoint()
        self._layout: QHBoxLayout | None = None

        self.setObjectName("WindowChrome")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.ArrowCursor)

        layout = QHBoxLayout(self)
        self._layout = layout
        layout.setContentsMargins(10, 5, 6, 5)
        layout.setSpacing(6)

        icon = QLabel(resolve_icon(title_icon) or "▣", self)
        icon.setProperty("role", "window_icon")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedWidth(18)
        layout.addWidget(icon, 0)

        self._title_label = QLabel(clean_text(title) or APP_TITLE, self)
        self._title_label.setProperty("role", "window_title")
        self._title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addWidget(self._title_label, 1)

        self._min_button = self._make_chrome_button("—", "min", "Minimize")
        self._max_button = self._make_chrome_button("□", "max", "Maximize / Restore")
        self._close_button = self._make_chrome_button("×", "close", "Close")

        if allow_minimize:
            layout.addWidget(self._min_button, 0)
        else:
            self._min_button.hide()

        if self._allow_maximize:
            layout.addWidget(self._max_button, 0)
        else:
            self._max_button.hide()

        layout.addWidget(self._close_button, 0)

        self._min_button.clicked.connect(self._host.showMinimized)
        self._max_button.clicked.connect(self._toggle_max_restore)
        self._close_button.clicked.connect(self._handle_close)

        self._host.installEventFilter(self)
        self._sync_max_button()
        self.apply_scale("100")

    def _make_chrome_button(self, text: str, kind: str, tooltip: str) -> QPushButton:
        button = QPushButton(text, self)
        button.setProperty("chrome", True)
        button.setProperty("chrome_kind", kind)
        button.setFocusPolicy(Qt.NoFocus)
        button.setToolTip(tooltip)
        button.setFixedSize(30, 22)
        return button

    def apply_scale(self, scale_id: str) -> None:
        profile = resolve_scale(scale_id)
        if self._layout is not None:
            self._layout.setContentsMargins(
                profile.px(10, 2),
                profile.px(5, 1),
                profile.px(6, 1),
                profile.px(5, 1),
            )
            self._layout.setSpacing(profile.px(6, 2))
        self.setFixedHeight(profile.px(34, 24))
        self._title_label.setFixedHeight(profile.px(20, 16))
        self._min_button.setFixedSize(profile.px(30, 22), profile.px(22, 18))
        self._max_button.setFixedSize(profile.px(30, 22), profile.px(22, 18))
        self._close_button.setFixedSize(profile.px(30, 22), profile.px(22, 18))

    def _handle_close(self) -> None:
        if callable(self._on_close):
            self._on_close()
            return
        self._host.close()

    def _toggle_max_restore(self) -> None:
        if not self._allow_maximize:
            return
        if self._host.isMaximized():
            self._host.showNormal()
        else:
            self._host.showMaximized()
        self._sync_max_button()

    def _sync_max_button(self) -> None:
        if not self._allow_maximize:
            return
        self._max_button.setText("❐" if self._host.isMaximized() else "□")
        self._max_button.setToolTip("Restore" if self._host.isMaximized() else "Maximize")

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        host = getattr(self, "_host", None)
        if host is None or watched is not host:
            return False
        if event.type() == QEvent.Type.WindowTitleChange:
            self._title_label.setText(clean_text(self._host.windowTitle()) or APP_TITLE)
        elif event.type() == QEvent.Type.WindowStateChange:
            self._sync_max_button()
        return False

    def _is_pointer_on_button(self, local_pos: QPoint) -> bool:
        child = self.childAt(local_pos)
        return isinstance(child, QPushButton)

    def mouseDoubleClickEvent(self, event: Any) -> None:  # type: ignore[override]
        if (
            event.button() == Qt.LeftButton
            and self._allow_maximize
            and not self._is_pointer_on_button(_local_point_from_event(event))
        ):
            self._toggle_max_restore()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: Any) -> None:  # type: ignore[override]
        if (
            event.button() == Qt.LeftButton
            and not self._is_pointer_on_button(_local_point_from_event(event))
            and not self._host.isMaximized()
        ):
            self._dragging = True
            self._drag_offset = _global_point_from_event(event) - self._host.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: Any) -> None:  # type: ignore[override]
        if self._dragging and bool(event.buttons() & Qt.LeftButton):
            if self._host.isMaximized():
                self._dragging = False
            else:
                self._host.move(_global_point_from_event(event) - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: Any) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            self._dragging = False
        super().mouseReleaseEvent(event)
