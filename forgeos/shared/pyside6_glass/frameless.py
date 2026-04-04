from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, Qt
from PySide6.QtWidgets import QFrame, QWidget


_EDGE_NONE = 0
_EDGE_LEFT = 1
_EDGE_TOP = 2
_EDGE_RIGHT = 4
_EDGE_BOTTOM = 8


def _global_point_from_event(event: QEvent) -> QPoint:
    if hasattr(event, "globalPosition"):
        return event.globalPosition().toPoint()  # type: ignore[no-any-return]
    if hasattr(event, "globalPos"):
        return event.globalPos()  # type: ignore[no-any-return]
    return QPoint(0, 0)


def _local_point_from_event(event: QEvent) -> QPoint:
    if hasattr(event, "position"):
        return event.position().toPoint()  # type: ignore[no-any-return]
    if hasattr(event, "pos"):
        return event.pos()  # type: ignore[no-any-return]
    return QPoint(0, 0)


class _FramelessResizeCorner(QFrame):
    def __init__(
        self,
        host: QWidget,
        *,
        edges: int,
        cursor: Qt.CursorShape,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent or host)
        self._host = host
        self._edges = int(edges)
        self._press_pos = QPoint(0, 0)
        self._press_geometry = QRect()
        self.setCursor(cursor)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self.setProperty("framelessResizeGrip", True)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton and not self._host.isMaximized():
            self._press_pos = _global_point_from_event(event)
            self._press_geometry = QRect(self._host.geometry())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if bool(event.buttons() & Qt.LeftButton) and not self._host.isMaximized():
            self._resize_from_delta(_global_point_from_event(event) - self._press_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def _resize_from_delta(self, delta: QPoint) -> None:
        rect = QRect(self._press_geometry)
        minimum = self._host.minimumSize()

        if bool(self._edges & _EDGE_LEFT):
            target = rect.left() + int(delta.x())
            max_left = rect.right() - minimum.width() + 1
            rect.setLeft(min(target, max_left))
        if bool(self._edges & _EDGE_RIGHT):
            target = rect.right() + int(delta.x())
            min_right = rect.left() + minimum.width() - 1
            rect.setRight(max(target, min_right))
        if bool(self._edges & _EDGE_TOP):
            target = rect.top() + int(delta.y())
            max_top = rect.bottom() - minimum.height() + 1
            rect.setTop(min(target, max_top))
        if bool(self._edges & _EDGE_BOTTOM):
            target = rect.bottom() + int(delta.y())
            min_bottom = rect.top() + minimum.height() - 1
            rect.setBottom(max(target, min_bottom))
        self._host.setGeometry(rect)


class FramelessResizeController(QObject):
    def __init__(self, host: QWidget, *, margin: int = 8) -> None:
        super().__init__(host)
        self._host = host
        self._margin = max(2, int(margin))
        self._grips: list[_FramelessResizeCorner] = [
            _FramelessResizeCorner(host, edges=_EDGE_LEFT, cursor=Qt.SizeHorCursor),
            _FramelessResizeCorner(host, edges=_EDGE_RIGHT, cursor=Qt.SizeHorCursor),
            _FramelessResizeCorner(host, edges=_EDGE_TOP, cursor=Qt.SizeVerCursor),
            _FramelessResizeCorner(host, edges=_EDGE_BOTTOM, cursor=Qt.SizeVerCursor),
            _FramelessResizeCorner(host, edges=_EDGE_LEFT | _EDGE_TOP, cursor=Qt.SizeFDiagCursor),
            _FramelessResizeCorner(host, edges=_EDGE_RIGHT | _EDGE_TOP, cursor=Qt.SizeBDiagCursor),
            _FramelessResizeCorner(host, edges=_EDGE_LEFT | _EDGE_BOTTOM, cursor=Qt.SizeBDiagCursor),
            _FramelessResizeCorner(host, edges=_EDGE_RIGHT | _EDGE_BOTTOM, cursor=Qt.SizeFDiagCursor),
        ]
        self._host.installEventFilter(self)
        self._layout_grips()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        if watched is self._host and event.type() in {
            QEvent.Type.Resize,
            QEvent.Type.Show,
            QEvent.Type.WindowStateChange,
        }:
            self._layout_grips()
        return False

    def _layout_grips(self) -> None:
        if self._host.isMaximized():
            for grip in self._grips:
                grip.hide()
            return

        for grip in self._grips:
            grip.show()
            grip.raise_()

        grip = self._margin
        width = self._host.width()
        height = self._host.height()
        left, right, top, bottom, tl, tr, bl, br = self._grips
        left.setGeometry(0, grip, grip, max(0, height - (grip * 2)))
        right.setGeometry(width - grip, grip, grip, max(0, height - (grip * 2)))
        top.setGeometry(grip, 0, max(0, width - (grip * 2)), grip)
        bottom.setGeometry(grip, height - grip, max(0, width - (grip * 2)), grip)
        tl.setGeometry(0, 0, grip, grip)
        tr.setGeometry(width - grip, 0, grip, grip)
        bl.setGeometry(0, height - grip, grip, grip)
        br.setGeometry(width - grip, height - grip, grip, grip)


__all__ = [
    "FramelessResizeController",
]
