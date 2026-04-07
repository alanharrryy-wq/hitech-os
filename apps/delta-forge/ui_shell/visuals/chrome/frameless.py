from __future__ import annotations

from typing import Any

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ..style.scale import resolve_scale

_EDGE_NONE = 0
_EDGE_LEFT = 1
_EDGE_TOP = 2
_EDGE_RIGHT = 4
_EDGE_BOTTOM = 8


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


class _ResizeGrip(QWidget):
    def __init__(self, host: QWidget, controller: "FramelessResizeController", *, edges: int, name: str) -> None:
        super().__init__(host)
        self._host = host
        self._controller = controller
        self._edges = edges
        self._name = name
        self._dragging = False
        self.setObjectName(f"ResizeGrip_{name}")
        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCursor(self._controller.cursor_for_edges(edges))
        self.setToolTip("Drag to resize")

    def paintEvent(self, event: Any) -> None:  # type: ignore[override]
        if "corner" not in self._name:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        line = QColor("#dff8ff")
        line.setAlpha(112)
        pen = QPen(line, 1.0)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        w = self.width()
        h = self.height()
        if "top_right" in self._name:
            painter.drawLine(w - 9, 4, w - 3, 10)
            painter.drawLine(w - 13, 4, w - 3, 14)
        elif "bottom_right" in self._name:
            painter.drawLine(w - 9, h - 4, w - 3, h - 10)
            painter.drawLine(w - 13, h - 4, w - 3, h - 14)
        elif "top_left" in self._name:
            painter.drawLine(9, 4, 3, 10)
            painter.drawLine(13, 4, 3, 14)
        else:
            painter.drawLine(9, h - 4, 3, h - 10)
            painter.drawLine(13, h - 4, 3, h - 14)

    def mousePressEvent(self, event: Any) -> None:  # type: ignore[override]
        if event.button() != Qt.LeftButton or self._host.isMaximized():
            super().mousePressEvent(event)
            return
        self._dragging = True
        self.grabMouse()
        self._controller.start_resize(self._edges, _global_point_from_event(event))
        event.accept()

    def mouseMoveEvent(self, event: Any) -> None:  # type: ignore[override]
        if self._dragging and bool(event.buttons() & Qt.LeftButton):
            self._controller.update_resize(_global_point_from_event(event))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: Any) -> None:  # type: ignore[override]
        if self._dragging and event.button() == Qt.LeftButton:
            self._dragging = False
            self.releaseMouse()
            self._controller.finish_resize()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def hideEvent(self, event: Any) -> None:  # type: ignore[override]
        if self._dragging:
            self._dragging = False
            self.releaseMouse()
            self._controller.finish_resize()
        super().hideEvent(event)


class FramelessResizeController(QObject):
    def __init__(
        self,
        host: QWidget,
        *,
        margin: int = 14,
        edge_hit: int = 12,
        corner_hit: int = 22,
    ) -> None:
        self._host = host
        super().__init__(host)
        self._margin = max(8, int(margin))
        self._edge_hit = max(8, int(edge_hit))
        self._corner_hit = max(16, int(corner_hit))
        self._active_edges = _EDGE_NONE
        self._resizing = False
        self._press_global = QPoint()
        self._start_geometry = QRect()

        self._grips: list[_ResizeGrip] = [
            _ResizeGrip(host, self, edges=_EDGE_TOP, name="top_edge"),
            _ResizeGrip(host, self, edges=_EDGE_BOTTOM, name="bottom_edge"),
            _ResizeGrip(host, self, edges=_EDGE_LEFT, name="left_edge"),
            _ResizeGrip(host, self, edges=_EDGE_RIGHT, name="right_edge"),
            _ResizeGrip(host, self, edges=_EDGE_TOP | _EDGE_LEFT, name="top_left_corner"),
            _ResizeGrip(host, self, edges=_EDGE_TOP | _EDGE_RIGHT, name="top_right_corner"),
            _ResizeGrip(host, self, edges=_EDGE_BOTTOM | _EDGE_LEFT, name="bottom_left_corner"),
            _ResizeGrip(host, self, edges=_EDGE_BOTTOM | _EDGE_RIGHT, name="bottom_right_corner"),
        ]

        self._host.installEventFilter(self)
        self._host.setMouseTracking(True)
        self._layout_grips()

    def apply_scale(self, scale_id: str) -> None:
        host = getattr(self, "_host", None)
        if host is None:
            return
        profile = resolve_scale(scale_id)
        self._margin = max(8, profile.px(14, 8))
        self._edge_hit = max(8, profile.px(12, 8))
        self._corner_hit = max(16, profile.px(22, 16))
        self._layout_grips()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        host = getattr(self, "_host", None)
        if host is None:
            return False
        if watched is not host:
            return False
        event_type = event.type()
        if event_type in {QEvent.Type.Resize, QEvent.Type.Show, QEvent.Type.WindowStateChange}:
            self._layout_grips()
            return False
        if event_type == QEvent.Type.MouseMove and not self._resizing:
            self._apply_resize_cursor(self._edge_mask_at(_local_point_from_event(event)))
            return False
        if event_type == QEvent.Type.Leave and not self._resizing:
            host.unsetCursor()
            return False
        if event_type == QEvent.Type.MouseButtonPress:
            return self._on_mouse_press(event)
        if event_type == QEvent.Type.MouseButtonRelease:
            return self._on_mouse_release(event)
        return False

    def _on_mouse_press(self, event: Any) -> bool:
        if self._host.isMaximized() or event.button() != Qt.LeftButton:
            return False
        edges = self._edge_mask_at(_local_point_from_event(event))
        if edges == _EDGE_NONE:
            return False
        self.start_resize(edges, _global_point_from_event(event))
        event.accept()
        return True

    def _on_mouse_release(self, event: Any) -> bool:
        if not self._resizing or event.button() != Qt.LeftButton:
            return False
        self.finish_resize()
        event.accept()
        return True

    def _layout_grips(self) -> None:
        host = getattr(self, "_host", None)
        if host is None:
            return
        if host.isMaximized():
            for grip in self._grips:
                grip.hide()
            return

        w = host.width()
        h = host.height()
        e = self._edge_hit
        c = self._corner_hit

        mapping = {
            "top_edge": QRect(c, 0, max(0, w - (2 * c)), e),
            "bottom_edge": QRect(c, max(0, h - e), max(0, w - (2 * c)), e),
            "left_edge": QRect(0, c, e, max(0, h - (2 * c))),
            "right_edge": QRect(max(0, w - e), c, e, max(0, h - (2 * c))),
            "top_left_corner": QRect(0, 0, c, c),
            "top_right_corner": QRect(max(0, w - c), 0, c, c),
            "bottom_left_corner": QRect(0, max(0, h - c), c, c),
            "bottom_right_corner": QRect(max(0, w - c), max(0, h - c), c, c),
        }

        for grip in self._grips:
            rect = mapping.get(grip._name)
            if rect is None:
                continue
            grip.setGeometry(rect)
            grip.show()
            grip.raise_()

    def _edge_mask_at(self, pos: QPoint) -> int:
        host = getattr(self, "_host", None)
        if host is None:
            return _EDGE_NONE
        if host.isMaximized():
            return _EDGE_NONE
        rect = host.rect()
        if rect.width() <= 0 or rect.height() <= 0:
            return _EDGE_NONE
        left = pos.x() <= self._margin
        right = pos.x() >= (rect.width() - self._margin)
        top = pos.y() <= self._margin
        bottom = pos.y() >= (rect.height() - self._margin)

        mask = _EDGE_NONE
        if left:
            mask |= _EDGE_LEFT
        if right:
            mask |= _EDGE_RIGHT
        if top:
            mask |= _EDGE_TOP
        if bottom:
            mask |= _EDGE_BOTTOM
        return mask

    def cursor_for_edges(self, edges: int) -> Qt.CursorShape:
        if edges in {_EDGE_TOP | _EDGE_LEFT, _EDGE_BOTTOM | _EDGE_RIGHT}:
            return Qt.SizeFDiagCursor
        if edges in {_EDGE_TOP | _EDGE_RIGHT, _EDGE_BOTTOM | _EDGE_LEFT}:
            return Qt.SizeBDiagCursor
        if edges in {_EDGE_LEFT, _EDGE_RIGHT}:
            return Qt.SizeHorCursor
        if edges in {_EDGE_TOP, _EDGE_BOTTOM}:
            return Qt.SizeVerCursor
        return Qt.ArrowCursor

    def _apply_resize_cursor(self, edges: int) -> None:
        host = getattr(self, "_host", None)
        if host is None:
            return
        cursor_shape = self.cursor_for_edges(edges)
        if cursor_shape == Qt.ArrowCursor:
            host.unsetCursor()
        else:
            host.setCursor(cursor_shape)

    def start_resize(self, edges: int, global_pos: QPoint) -> None:
        host = getattr(self, "_host", None)
        if host is None:
            return
        if host.isMaximized() or edges == _EDGE_NONE:
            return
        self._active_edges = edges
        self._resizing = True
        self._press_global = global_pos
        self._start_geometry = host.geometry()
        self._apply_resize_cursor(edges)

    def update_resize(self, global_pos: QPoint) -> None:
        self._resize_to(global_pos)

    def finish_resize(self) -> None:
        self._resizing = False
        self._active_edges = _EDGE_NONE
        host = getattr(self, "_host", None)
        if host is not None:
            host.unsetCursor()

    def _resize_to(self, global_pos: QPoint) -> None:
        if self._active_edges == _EDGE_NONE:
            return
        host = getattr(self, "_host", None)
        if host is None:
            return
        dx = global_pos.x() - self._press_global.x()
        dy = global_pos.y() - self._press_global.y()
        geom = QRect(self._start_geometry)

        min_width = max(380, int(host.minimumWidth() or 0))
        min_height = max(260, int(host.minimumHeight() or 0))

        if self._active_edges & _EDGE_LEFT:
            proposed_left = geom.left() + dx
            max_left = geom.right() - min_width + 1
            geom.setLeft(min(proposed_left, max_left))
        if self._active_edges & _EDGE_RIGHT:
            proposed_right = geom.right() + dx
            min_right = geom.left() + min_width - 1
            geom.setRight(max(proposed_right, min_right))
        if self._active_edges & _EDGE_TOP:
            proposed_top = geom.top() + dy
            max_top = geom.bottom() - min_height + 1
            geom.setTop(min(proposed_top, max_top))
        if self._active_edges & _EDGE_BOTTOM:
            proposed_bottom = geom.bottom() + dy
            min_bottom = geom.top() + min_height - 1
            geom.setBottom(max(proposed_bottom, min_bottom))

        host.setGeometry(geom)
