from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget


class WindowChromeBar(QFrame):
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
        self._drag_restore_pending = False

        self.setObjectName("WindowChrome")
        self.setFixedHeight(32)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.ArrowCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 6, 4)
        layout.setSpacing(4)

        icon = QLabel("▣", self)
        icon.setProperty("role", "window_icon")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedWidth(18)
        layout.addWidget(icon, 0)

        self._title_label = QLabel(str(title or ""), self)
        self._title_label.setProperty("role", "window_title")
        layout.addWidget(self._title_label, 1)

        self._min_button = self._create_button("—", "Minimize", self._minimize)
        self._max_button = self._create_button("□", "Maximize", self._toggle_maximize)
        self._close_button = self._create_button("×", "Close", self._close)
        self._close_button.setProperty("chrome_kind", "close")

        if allow_minimize:
            layout.addWidget(self._min_button, 0)
        if self._allow_maximize:
            layout.addWidget(self._max_button, 0)
        layout.addWidget(self._close_button, 0)

        self._host.installEventFilter(self)
        self._sync_host_title()
        self._sync_max_button()

    def _create_button(self, text: str, tooltip: str, handler: Callable[[], None]) -> QPushButton:
        button = QPushButton(text, self)
        button.setToolTip(tooltip)
        button.setProperty("chrome", True)
        button.setFocusPolicy(Qt.NoFocus)
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedSize(28, 20)
        button.clicked.connect(handler)
        return button

    def _sync_host_title(self) -> None:
        self._title_label.setText(self._host.windowTitle())

    def _sync_max_button(self) -> None:
        if not self._allow_maximize:
            return
        if self._host.isMaximized():
            self._max_button.setText("❐")
            self._max_button.setToolTip("Restore")
        else:
            self._max_button.setText("□")
            self._max_button.setToolTip("Maximize")

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

    def eventFilter(self, watched, event) -> bool:  # type: ignore[override]
        host = getattr(self, "_host", None)
        if host is None:
            return False
        if watched is host:
            if event.type() == QEvent.Type.WindowTitleChange:
                self._sync_host_title()
            elif event.type() == QEvent.Type.WindowStateChange:
                self._sync_max_button()
        return False

    def _is_pointer_on_button(self, local_pos: QPoint) -> bool:
        child = self.childAt(local_pos)
        return isinstance(child, QPushButton)

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
        if event.button() == Qt.LeftButton and not self._is_pointer_on_button(event.position().toPoint()):
            self._dragging = True
            if self._host.isMaximized():
                self._drag_offset = event.position().toPoint()
                self._drag_restore_pending = True
            else:
                self._drag_offset = event.globalPosition().toPoint() - self._host.frameGeometry().topLeft()
                self._drag_restore_pending = False
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._dragging and bool(event.buttons() & Qt.LeftButton):
            global_pos = event.globalPosition().toPoint()
            if self._drag_restore_pending and self._allow_maximize:
                ratio = max(0.0, min(1.0, event.position().x() / max(1.0, self.width())))
                self._host.showNormal()
                self._sync_max_button()
                rect = self._host.frameGeometry()
                self._drag_offset = QPoint(int(rect.width() * ratio), int(event.position().y()))
                self._drag_restore_pending = False
            self._host.move(global_pos - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        self._dragging = False
        self._drag_restore_pending = False
        super().mouseReleaseEvent(event)
