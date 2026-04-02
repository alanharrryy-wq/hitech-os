from __future__ import annotations

import math
import random
import time
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PySide6.QtWidgets import QWidget

from .contracts import GLASS_RADIUS


class FrostedGlassBackdrop(QWidget):
    """Lightweight animated backdrop aligned with code-atlas visual language."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        motion_enabled: bool = True,
    ) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(False)
        self._motion_enabled = motion_enabled
        self._epoch = time.monotonic()
        self._stars = [
            (random.random(), random.random(), 0.5 + random.random() * 1.2, random.random() * 2.0)
            for _ in range(90)
        ]
        self._timer = QTimer(self)
        self._timer.setInterval(24)
        self._timer.timeout.connect(self.update)
        if self._motion_enabled:
            self._timer.start()

    def set_motion_enabled(self, enabled: bool) -> None:
        self._motion_enabled = bool(enabled)
        if self._motion_enabled and not self._timer.isActive():
            self._timer.start()
        elif not self._motion_enabled and self._timer.isActive():
            self._timer.stop()
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        rect = self.rect()
        if rect.width() <= 1 or rect.height() <= 1:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)

        clip_path = QPainterPath()
        clip_path.addRoundedRect(rect.adjusted(1, 1, -1, -1), GLASS_RADIUS.shell, GLASS_RADIUS.shell)
        painter.save()
        painter.setClipPath(clip_path)

        phase = max(0.0, time.monotonic() - self._epoch)

        bg = QLinearGradient(0, 0, 0, rect.height())
        bg.setColorAt(0.0, QColor(15, 30, 52, 238))
        bg.setColorAt(1.0, QColor(8, 19, 35, 244))
        painter.fillRect(rect, bg)

        orb_specs = (
            (0.82, 0.18, 0.46, QColor(120, 218, 255, 58)),
            (0.22, 0.76, 0.34, QColor(140, 239, 255, 42)),
            (0.54, 0.62, 0.28, QColor(190, 228, 255, 30)),
        )
        for index, (x_factor, y_factor, r_factor, color) in enumerate(orb_specs, start=1):
            wobble_x = math.sin((phase * 0.08) + index) * 0.025
            wobble_y = math.cos((phase * 0.06) + index * 1.2) * 0.03
            cx = rect.width() * (x_factor + wobble_x)
            cy = rect.height() * (y_factor + wobble_y)
            radius = rect.width() * r_factor
            orb = QRadialGradient(cx, cy, radius)
            edge = QColor(color)
            edge.setAlpha(0)
            orb.setColorAt(0.0, color)
            orb.setColorAt(1.0, edge)
            painter.setBrush(orb)
            painter.drawEllipse(cx - radius, cy - radius, radius * 2.0, radius * 2.0)

        for x_seed, y_seed, size, speed in self._stars:
            x = rect.width() * ((x_seed + (phase * 0.0008 * speed)) % 1.0)
            y = rect.height() * y_seed
            twinkle = 0.55 + (0.45 * (0.5 + (0.5 * math.sin((phase * (0.8 + speed)) + (x_seed * 10.0)))))
            alpha = int(170 * twinkle)
            painter.setBrush(QColor(224, 246, 255, alpha))
            painter.drawEllipse(x, y, size, size)

        frame_path = QPainterPath()
        frame_path.addRoundedRect(rect.adjusted(1.5, 1.5, -1.5, -1.5), GLASS_RADIUS.shell, GLASS_RADIUS.shell)
        painter.fillPath(frame_path, QColor(206, 236, 255, 14))
        painter.setPen(QPen(QColor(168, 226, 255, 52), 1.1))
        painter.drawPath(frame_path)

        painter.restore()
        painter.end()

