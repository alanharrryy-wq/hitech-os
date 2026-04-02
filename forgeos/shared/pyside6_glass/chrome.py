from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QToolButton, QWidget

from .icons import apply_icon


class WindowChromeBar(QFrame):
    """Reusable top chrome for frameless windows/dialogs."""

    def __init__(
        self,
        host: QWidget,
        *,
        title: str,
        on_close: Optional[Callable[[], None]] = None,
        allow_minimize: bool = True,
        allow_maximize: bool = True,
    ) -> None:
        super().__init__(host)
        self._host = host
        self._on_close = on_close
        self._allow_maximize = bool(allow_maximize)
        self._dragging = False
        self._drag_offset = QPoint(0, 0)

        self.setObjectName("WindowChrome")
        self.setFixedHeight(34)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.ArrowCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 6, 5)
        layout.setSpacing(6)

        icon = QLabel("")
        icon.setProperty("role", "window_icon")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedWidth(18)
        apply_icon(icon, "component", size="small", tooltip="Window")
        layout.addWidget(icon, 0)

        label = QLabel(title)
        label.setProperty("role", "window_title")
        layout.addWidget(label, 1)

        self._min_button = self._create_button(
            icon_name="minus",
            fallback_text="-",
            tooltip="Minimize",
            handler=self._minimize,
        )
        self._max_button = self._create_button(
            icon_name="square",
            fallback_text="[]",
            tooltip="Maximize / Restore",
            handler=self._toggle_maximize,
        )
        self._close_button = self._create_button(
            icon_name="x",
            fallback_text="x",
            tooltip="Close",
            handler=self._close,
        )

        if allow_minimize:
            layout.addWidget(
                self._min_button,
                0,
            )
        if self._allow_maximize:
            layout.addWidget(
                self._max_button,
                0,
            )
        layout.addWidget(self._close_button, 0)
        self._host.installEventFilter(self)
        self._sync_max_button()

    def _create_button(
        self,
        *,
        icon_name: str,
        fallback_text: str,
        tooltip: str,
        handler: Callable[[], None],
    ) -> QToolButton:
        button = QToolButton(self)
        button.setToolTip(tooltip)
        button.setText(str(fallback_text or ""))
        button.setProperty("chrome", True)
        button.setProperty("chrome_kind", icon_name if icon_name != "x" else "close")
        button.setFocusPolicy(Qt.NoFocus)
        button.setCursor(Qt.PointingHandCursor)
        button.setAutoRaise(False)
        button.clicked.connect(handler)
        button.setFixedSize(30, 22)
        apply_icon(button, icon_name, size="small", tooltip=tooltip)
        return button

    def _minimize(self) -> None:
        self._host.showMinimized()

    def _toggle_maximize(self) -> None:
        if not self._allow_maximize:
            return
        if self._host.isMaximized():
            self._host.showNormal()
        else:
            self._host.showMaximized()
        self._sync_max_button()

    def _close(self) -> None:
        if self._on_close is not None:
            self._on_close()
            return
        self._host.close()

    def _sync_max_button(self) -> None:
        if not self._allow_maximize:
            return
        self._max_button.setToolTip("Restore" if self._host.isMaximized() else "Maximize")

    def eventFilter(self, watched, event) -> bool:  # type: ignore[override]
        if watched is self._host and event.type() == QEvent.Type.WindowStateChange:
            self._sync_max_button()
        return False

    def _is_pointer_on_button(self, local_pos: QPoint) -> bool:
        child = self.childAt(local_pos)
        return isinstance(child, QToolButton)

    def mouseDoubleClickEvent(self, event) -> None:  # type: ignore[override]
        if (
            event.button() == Qt.LeftButton
            and self._allow_maximize
            and not self._is_pointer_on_button(event.position().toPoint())
        ):
            self._toggle_maximize()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if (
            event.button() == Qt.LeftButton
            and not self._is_pointer_on_button(event.position().toPoint())
            and not self._host.isMaximized()
        ):
            self._dragging = True
            self._drag_offset = event.globalPosition().toPoint() - self._host.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._dragging and bool(event.buttons() & Qt.LeftButton):
            self._host.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        self._dragging = False
        super().mouseReleaseEvent(event)
