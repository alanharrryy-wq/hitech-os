from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QEvent, QObject, QRectF, QVariantAnimation
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget

from .skins import SkinTokens, rgba


class PanelCard(QFrame):
    def __init__(self, tokens: SkinTokens, accent: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self._accent = accent
        self.setObjectName('panelCard')
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(8, 8, 8, 8)

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        self.update()

    def set_accent(self, accent: bool) -> None:
        self._accent = accent
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        radius = 16.0

        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), radius, radius)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(self._tokens.panel_alt if self._accent else self._tokens.panel))
        gradient.setColorAt(1.0, QColor(self._tokens.panel))
        painter.fillPath(path, gradient)

        painter.setPen(QPen(QColor(self._tokens.border), 1))
        painter.drawPath(path)

        inner_rect = rect.adjusted(1, 1, -1, -1)
        inner_path = QPainterPath()
        inner_path.addRoundedRect(QRectF(inner_rect), radius - 1, radius - 1)
        painter.setPen(QPen(rgba(self._tokens.bevel_light, 100), 1))
        painter.drawPath(inner_path)

        if self._accent:
            accent_pen = QPen(QColor(self._tokens.accent), 1)
            painter.setPen(accent_pen)
            painter.drawLine(rect.left() + 14, rect.top() + 2, rect.right() - 14, rect.top() + 2)

        super().paintEvent(event)


class AccentButton(QPushButton):
    def __init__(
        self,
        text: str,
        tokens: SkinTokens,
        parent: QWidget | None = None,
        *,
        strong: bool = False,
    ) -> None:
        super().__init__(text, parent)
        self._tokens = tokens
        self._strong = strong
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
        if self._strong:
            base = QColor(self._tokens.accent)
            hover = QColor(self._tokens.accent_hover)
            border = self._tokens.accent_hover
            text = '#101318'
        else:
            base = QColor(self._tokens.panel_alt)
            hover = QColor(self._tokens.accent_hover)
            border = self._tokens.border
            text = self._tokens.text

        mix = QColor(
            round(base.red() + (hover.red() - base.red()) * self._mix),
            round(base.green() + (hover.green() - base.green()) * self._mix),
            round(base.blue() + (hover.blue() - base.blue()) * self._mix),
        )
        self.setStyleSheet(
            f"""
            QPushButton {{
                background: {mix.name()};
                color: {text};
                border: 1px solid {border};
                border-top: 1px solid {self._tokens.bevel_light};
                border-bottom: 1px solid {self._tokens.bevel_shadow};
                border-radius: 10px;
                padding: 8px 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                border: 1px solid {self._tokens.accent};
            }}
            QPushButton:pressed {{
                background: {self._tokens.panel};
                color: {self._tokens.text};
                border: 1px solid {self._tokens.accent_hover};
            }}
            """
        )

    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._anim.stop()
        self._anim.setStartValue(self._mix)
        self._anim.setEndValue(0.28 if self._strong else 0.18)
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._anim.stop()
        self._anim.setStartValue(self._mix)
        self._anim.setEndValue(0.0)
        self._anim.start()
        super().leaveEvent(event)


class MetricTile(PanelCard):
    def __init__(self, tokens: SkinTokens, title: str, parent: QWidget | None = None) -> None:
        super().__init__(tokens, accent=False, parent=parent)
        self._tokens = tokens
        self._title = QLabel(title, self)
        self._title.setObjectName('metricTitleLabel')
        self._value = QLabel('0', self)
        self._value.setObjectName('accentValueLabel')
        self._caption = QLabel('', self)
        self._caption.setObjectName('metricCaptionLabel')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)
        layout.addWidget(self._title)
        layout.addWidget(self._value)
        layout.addWidget(self._caption)
        layout.addStretch(1)

    def set_skin(self, tokens: SkinTokens) -> None:
        self._tokens = tokens
        super().set_skin(tokens)

    def set_data(self, value: str, caption: str = '') -> None:
        self._value.setText(value)
        self._caption.setText(caption)


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
        try:
            offset = float(0.0 if value is None else value)
        except (TypeError, ValueError):
            offset = 0.0
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
                current_lift = max(0.0, float(self._base_pos.y() - self._widget.y()))
                self._animation.setStartValue(current_lift)
                self._animation.setEndValue(0.0)
                self._animation.start()
        return False


def install_hover_raise(widget: QWidget, lift_px: float = 2.0) -> HoverRaiseFilter:
    filt = HoverRaiseFilter(widget, lift_px)
    widget._hover_raise_filter = filt  # type: ignore[attr-defined]
    return filt
