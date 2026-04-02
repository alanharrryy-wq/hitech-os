from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QWidget


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
        self._dragging = False
        self._drag_offset = QPoint(0, 0)

        self.setObjectName("WindowChrome")
        self.setProperty("card", "true")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        icon = QLabel("◽")
        icon.setProperty("role", "window_icon")
        layout.addWidget(icon, 0)

        label = QLabel(title)
        label.setProperty("role", "window_title")
        layout.addWidget(label, 1)

        if allow_minimize:
            layout.addWidget(self._create_button("−", self._minimize), 0)
        if allow_maximize:
            layout.addWidget(self._create_button("□", self._toggle_maximize), 0)
        layout.addWidget(self._create_button("×", self._close), 0)

    def _create_button(self, text: str, handler: Callable[[], None]) -> QToolButton:
        button = QToolButton(self)
        button.setText(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setAutoRaise(True)
        button.clicked.connect(handler)
        button.setFixedSize(26, 22)
        return button

    def _minimize(self) -> None:
        self._host.showMinimized()

    def _toggle_maximize(self) -> None:
        if self._host.isMaximized():
            self._host.showNormal()
        else:
            self._host.showMaximized()

    def _close(self) -> None:
        if self._on_close is not None:
            self._on_close()
            return
        self._host.close()

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton and not self._host.isMaximized():
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

