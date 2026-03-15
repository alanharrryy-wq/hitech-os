from __future__ import annotations

from PySide6.QtCore import Property, QEasingCurve, QEvent, QObject, QPointF, QRectF, QVariantAnimation
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QFrame, QPushButton, QWidget

from .skins import SkinTokens, rgba


class PanelCard(QFrame):
    def __init__(self, tokens: SkinTokens, accent: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self._accent = accent
        self.setObjectName("panelCard")
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(8, 8, 8, 8)

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        radius = 14.0

        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), radius, radius)

        painter.fillPath(path, QColor(self._tokens.panel))

        outer_pen = QPen(QColor(self._tokens.border), 1)
        painter.setPen(outer_pen)
        painter.drawPath(path)

        inner_rect = rect.adjusted(1, 1, -1, -1)
        inner_path = QPainterPath()
        inner_path.addRoundedRect(QRectF(inner_rect), radius - 1, radius - 1)
        painter.setPen(QPen(rgba(self._tokens.bevel_light, 120), 1))
        painter.drawPath(inner_path)

        shadow_rect = rect.adjusted(1, 2, -1, -1)
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(QRectF(shadow_rect), radius - 1, radius - 1)
        painter.setPen(QPen(rgba(self._tokens.bevel_shadow, 90), 1))
        painter.drawPath(shadow_path)

        if self._accent:
            accent_pen = QPen(QColor(self._tokens.accent), 1)
            painter.setPen(accent_pen)
            painter.drawLine(rect.left() + 12, rect.top() + 2, rect.right() - 12, rect.top() + 2)

        super().paintEvent(event)


class AccentButton(QPushButton):
    def __init__(self, text: str, tokens: SkinTokens, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self._tokens = tokens
        self._mix = 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(140)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._on_value_changed)
        self._refresh_style()

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self._refresh_style()

    def _on_value_changed(self, value) -> None:
        self._mix = float(value)
        self._refresh_style()

    def _refresh_style(self) -> None:
        hover = QColor(self._tokens.accent_hover)
        base = QColor(self._tokens.panel_alt)
        mix = QColor(
            round(base.red() + (hover.red() - base.red()) * self._mix),
            round(base.green() + (hover.green() - base.green()) * self._mix),
            round(base.blue() + (hover.blue() - base.blue()) * self._mix),
        )
        self.setStyleSheet(
            f"""
            QPushButton {{
                background: {mix.name()};
                color: {self._tokens.text};
                border: 1px solid {self._tokens.border};
                border-top: 1px solid {self._tokens.bevel_light};
                border-bottom: 1px solid {self._tokens.bevel_shadow};
                border-radius: 10px;
                padding: 8px 12px;
            }}
            QPushButton:hover {{
                border: 1px solid {self._tokens.accent};
            }}
            QPushButton:pressed {{
                background: {self._tokens.panel};
                border: 1px solid {self._tokens.accent_hover};
            }}
            """
        )

    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._anim.stop()
        self._anim.setStartValue(self._mix)
        self._anim.setEndValue(0.22)
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._anim.stop()
        self._anim.setStartValue(self._mix)
        self._anim.setEndValue(0.0)
        self._anim.start()
        super().leaveEvent(event)


class HoverRaiseFilter(QObject):
    def __init__(self, widget: QWidget, lift_px: float = 2.0) -> None:
        super().__init__(widget)
        self._widget = widget
        self._lift_px = lift_px
        self._base_pos = widget.pos()
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(130)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animation.valueChanged.connect(self._apply_lift)
        widget.installEventFilter(self)

    def _apply_lift(self, value) -> None:
        if self._widget.parentWidget() is None:
            return
        offset = float(value)
        self._widget.move(self._base_pos.x(), round(self._base_pos.y() - offset))

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self._widget:
            if event.type() == QEvent.Enter:
                self._base_pos = self._widget.pos()
                self._animation.stop()
                self._animation.setStartValue(0.0)
                self._animation.setEndValue(self._lift_px)
                self._animation.start()
            elif event.type() == QEvent.Leave:
                self._animation.stop()
                self._animation.setStartValue(self._widget.y() - self._base_pos.y())
                self._animation.setEndValue(0.0)
                self._animation.start()
        return False


def install_hover_raise(widget: QWidget, lift_px: float = 2.0) -> HoverRaiseFilter:
    filt = HoverRaiseFilter(widget, lift_px)
    widget._hover_raise_filter = filt  # type: ignore[attr-defined]
    return filt
