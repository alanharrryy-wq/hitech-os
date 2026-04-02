from __future__ import annotations

import sys

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QDialog, QFrame, QVBoxLayout

from .compositions import GlassExampleCatalog
from ..chrome import WindowChromeBar
from ..scene import build_glass_dialog_scene
from ..theme import build_stylesheet


def _workbench_shell_overrides() -> str:
    return """
QDialog#GlassWorkbenchWindow {
    background: transparent;
}
QWidget#GlassStage,
QWidget#GlassContent {
    background: transparent;
}
QFrame#Shell {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(234, 242, 250, 0.08),
        stop:1 rgba(141, 159, 180, 0.04));
    border: 1px solid rgba(223, 235, 247, 0.22);
    border-radius: 28px;
}
QFrame#Shell:hover {
    border: 1px solid rgba(143, 188, 213, 0.40);
}
QFrame[card="hero"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(236, 244, 252, 0.10),
        stop:1 rgba(143, 188, 213, 0.06));
    border: 1px solid rgba(143, 188, 213, 0.40);
    border-radius: 22px;
}
QFrame[card="true"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(232, 241, 250, 0.09),
        stop:1 rgba(159, 173, 192, 0.05));
    border: 1px solid rgba(221, 233, 245, 0.18);
    border-radius: 18px;
}
QFrame[card="muted"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(226, 236, 246, 0.10),
        stop:1 rgba(146, 162, 182, 0.06));
    border: 1px solid rgba(221, 233, 245, 0.15);
    border-radius: 18px;
}
QFrame[card="footer"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(232, 241, 250, 0.10),
        stop:1 rgba(147, 162, 181, 0.06));
    border: 1px solid rgba(221, 233, 245, 0.15);
    border-radius: 18px;
}
QFrame#WindowChrome {
    min-height: 34px;
    max-height: 34px;
    border-radius: 10px;
    border: 1px solid rgba(219, 232, 245, 0.10);
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(237, 246, 255, 0.06),
        stop:1 rgba(149, 170, 195, 0.04));
}
QFrame#WindowChrome QLabel[role="window_title"] {
    font-size: 12px;
    font-weight: 740;
    color: #dce8f3;
    letter-spacing: 0.2px;
}
QFrame#WindowChrome QLabel[role="window_icon"] {
    color: #8cbcd5;
    font-size: 11px;
    font-weight: 700;
}
QFrame#WindowChrome QToolButton {
    min-width: 30px;
    max-width: 30px;
    min-height: 22px;
    max-height: 22px;
    border-radius: 8px;
    padding: 0px;
    color: #ebf4ff;
    background: rgba(12, 21, 32, 0.44);
    border: 1px solid rgba(238, 248, 255, 0.08);
}
QFrame#WindowChrome QToolButton:hover {
    background: rgba(143, 188, 213, 0.16);
    border: 1px solid rgba(143, 188, 213, 0.52);
}
QFrame#WindowChrome QToolButton:pressed {
    background: rgba(143, 188, 213, 0.28);
    border: 1px solid rgba(143, 188, 213, 0.82);
}
QFrame#WindowChrome QToolButton[chrome_kind="close"]:hover {
    background: rgba(143, 188, 213, 0.18);
    border: 1px solid rgba(143, 188, 213, 0.26);
}
QWidget#GlassWorkbenchResizeGrip {
    background: transparent;
}
"""


class _ResizeGrip(QFrame):
    def __init__(self, host: QDialog, *, edges: Qt.Edge, cursor: Qt.CursorShape) -> None:
        super().__init__(host)
        self._host = host
        self._edges = edges
        self._press_pos = QPoint(0, 0)
        self._press_geometry = QRect()
        self.setObjectName("GlassWorkbenchResizeGrip")
        self.setCursor(cursor)
        self.setMouseTracking(True)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton and not self._host.isMaximized():
            self._press_pos = event.globalPosition().toPoint()
            self._press_geometry = QRect(self._host.geometry())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if bool(event.buttons() & Qt.LeftButton) and not self._host.isMaximized():
            self._resize_from_delta(event.globalPosition().toPoint() - self._press_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def _resize_from_delta(self, delta: QPoint) -> None:
        rect = QRect(self._press_geometry)
        minimum = self._host.minimumSize()

        if bool(self._edges & Qt.LeftEdge):
            target = rect.left() + int(delta.x())
            max_left = rect.right() - minimum.width() + 1
            rect.setLeft(min(target, max_left))
        if bool(self._edges & Qt.RightEdge):
            target = rect.right() + int(delta.x())
            min_right = rect.left() + minimum.width() - 1
            rect.setRight(max(target, min_right))
        if bool(self._edges & Qt.TopEdge):
            target = rect.top() + int(delta.y())
            max_top = rect.bottom() - minimum.height() + 1
            rect.setTop(min(target, max_top))
        if bool(self._edges & Qt.BottomEdge):
            target = rect.bottom() + int(delta.y())
            min_bottom = rect.top() + minimum.height() - 1
            rect.setBottom(max(target, min_bottom))

        self._host.setGeometry(rect)


class GlassWorkbenchWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("GlassWorkbenchWindow")
        self.setWindowTitle("PySide6 Glass Workbench")
        self.setMinimumSize(1024, 640)
        self.resize(1260, 740)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._fit_applied = False

        base_styles = build_stylesheet(
            "silver_frost_cyan",
            density="compact",
            typography_scale="sm",
            border_strength_scale=0.84,
            surface_opacity_scale=0.62,
            tab_density="compact",
        )
        self.setStyleSheet(f"{base_styles}\n{_workbench_shell_overrides()}")

        outer, content_layer, _backdrop = build_glass_dialog_scene(
            self,
            theme_id="silver_frost_cyan",
            variant="selector",
            margins=(4, 4, 4, 4),
            motion_enabled=True,
            apply_stylesheet=False,
        )
        outer.setSpacing(0)
        self._backdrop = _backdrop

        scene_layout = QVBoxLayout(content_layer)
        scene_layout.setContentsMargins(12, 10, 12, 12)
        scene_layout.setSpacing(8)

        self.window_chrome = WindowChromeBar(
            self,
            title=self.windowTitle(),
            on_close=self.close,
            allow_minimize=True,
            allow_maximize=True,
        )
        scene_layout.addWidget(self.window_chrome)

        self.workbench = GlassExampleCatalog(content_layer)
        scene_layout.addWidget(self.workbench, 1)

        grip = 8
        self._resize_grips = [
            _ResizeGrip(self, edges=Qt.LeftEdge, cursor=Qt.SizeHorCursor),
            _ResizeGrip(self, edges=Qt.RightEdge, cursor=Qt.SizeHorCursor),
            _ResizeGrip(self, edges=Qt.TopEdge, cursor=Qt.SizeVerCursor),
            _ResizeGrip(self, edges=Qt.BottomEdge, cursor=Qt.SizeVerCursor),
            _ResizeGrip(self, edges=Qt.LeftEdge | Qt.TopEdge, cursor=Qt.SizeFDiagCursor),
            _ResizeGrip(self, edges=Qt.RightEdge | Qt.TopEdge, cursor=Qt.SizeBDiagCursor),
            _ResizeGrip(self, edges=Qt.LeftEdge | Qt.BottomEdge, cursor=Qt.SizeBDiagCursor),
            _ResizeGrip(self, edges=Qt.RightEdge | Qt.BottomEdge, cursor=Qt.SizeFDiagCursor),
        ]
        self._grip_size = grip
        self._layout_resize_grips()

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        if not self._fit_applied:
            self._fit_applied = True
            self._fit_to_screen()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._layout_resize_grips()

    def _fit_to_screen(self) -> None:
        screen = self.screen() or QGuiApplication.primaryScreen()
        if screen is None:
            return
        available = screen.availableGeometry()
        target_w = min(available.width() - 20, 1320)
        target_h = min(available.height() - 24, 760)
        target_w = max(self.minimumWidth(), target_w)
        target_h = max(self.minimumHeight(), target_h)
        self.resize(target_w, target_h)
        self.move(available.center() - self.rect().center())

    def _layout_resize_grips(self) -> None:
        if self.isMaximized():
            for grip in self._resize_grips:
                grip.hide()
            return

        for grip in self._resize_grips:
            grip.show()
            grip.raise_()

        grip = self._grip_size
        width = self.width()
        height = self.height()
        left, right, top, bottom, tl, tr, bl, br = self._resize_grips
        left.setGeometry(0, grip, grip, max(0, height - (grip * 2)))
        right.setGeometry(width - grip, grip, grip, max(0, height - (grip * 2)))
        top.setGeometry(grip, 0, max(0, width - (grip * 2)), grip)
        bottom.setGeometry(grip, height - grip, max(0, width - (grip * 2)), grip)
        tl.setGeometry(0, 0, grip, grip)
        tr.setGeometry(width - grip, 0, grip, grip)
        bl.setGeometry(0, height - grip, grip, grip)
        br.setGeometry(width - grip, height - grip, grip, grip)


def create_workbench_window(parent=None) -> GlassWorkbenchWindow:
    return GlassWorkbenchWindow(parent)


def run() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = create_workbench_window()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())
