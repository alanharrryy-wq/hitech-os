from __future__ import annotations

from typing import Mapping

from PySide6.QtCore import QEasingCurve, Property, QPropertyAnimation, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QPushButton, QWidget


class CommandButton(QPushButton):
    """Delicate crystal button with soft liquid-glass reflections.

    This is the single canonical CommandButton implementation for DeltaForge.
    """

    _SIZE_PRESETS = {
        "sm": {"height": 34, "padding_x": 14, "radius": 13, "font_delta": -0.4, "icon": 14},
        "md": {"height": 40, "padding_x": 18, "radius": 15, "font_delta": 0.0, "icon": 16},
        "lg": {"height": 46, "padding_x": 22, "radius": 17, "font_delta": 0.55, "icon": 18},
    }
    _VARIANT_ALIASES = {
        "secondary": "command",
        "accent": "primary",
        "info": "primary",
    }

    def __init__(
        self,
        text: str = "",
        variant: str = "command",
        *,
        size: str = "md",
        icon: QIcon | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)
        self._idle_text = text
        self._size_name = "md"
        self._hover_progress = 0.0
        self._press_progress = 0.0

        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(False)
        self.setFlat(True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAutoDefault(False)
        self.setDefault(False)
        self.setProperty("ui_role", "command_button")
        self.setProperty("is_command_button", True)

        self.set_variant(variant)
        self.set_size(size)

        if icon is not None:
            self.setIcon(icon)

        font = QFont(self.font())
        font.setPointSizeF(max(font.pointSizeF(), 10.5) + self._size_config()["font_delta"])
        font.setWeight(QFont.Weight.DemiBold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.18)
        self.setFont(font)

        self._hover_anim = QPropertyAnimation(self, b"hoverProgress", self)
        self._hover_anim.setDuration(190)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._press_anim = QPropertyAnimation(self, b"pressProgress", self)
        self._press_anim.setDuration(120)
        self._press_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _normalize_variant(self, variant: str) -> str:
        raw = str(variant or "command").strip().lower()
        return self._VARIANT_ALIASES.get(raw, raw or "command")

    def set_variant(self, variant: str) -> None:
        self.setProperty("variant", self._normalize_variant(variant))
        self.update()

    def set_size(self, size: str) -> None:
        normalized = str(size or "md").strip().lower()
        if normalized not in self._SIZE_PRESETS:
            normalized = "md"
        self._size_name = normalized
        self.setProperty("command_size", normalized)
        cfg = self._size_config()
        self.setMinimumHeight(int(cfg["height"]))
        icon_size = int(cfg["icon"])
        self.setIconSize(QSize(icon_size, icon_size))
        self.updateGeometry()
        self.update()

    def set_busy(self, busy: bool, busy_text: str = "Working...") -> None:
        if busy:
            self._idle_text = self.text()
            self.setText(busy_text)
            self.setEnabled(False)
        else:
            self.setText(self._idle_text)
            self.setEnabled(True)

    def _size_config(self) -> dict[str, float]:
        return self._SIZE_PRESETS.get(self._size_name, self._SIZE_PRESETS["md"])

    def _animate(self, end_value: float, *, hover: bool) -> None:
        animation = self._hover_anim if hover else self._press_anim
        animation.stop()
        animation.setStartValue(self._hover_progress if hover else self._press_progress)
        animation.setEndValue(end_value)
        animation.start()

    def getHoverProgress(self) -> float:
        return self._hover_progress

    def setHoverProgress(self, value: float) -> None:
        self._hover_progress = float(value)
        self.update()

    hoverProgress = Property(float, getHoverProgress, setHoverProgress)

    def getPressProgress(self) -> float:
        return self._press_progress

    def setPressProgress(self, value: float) -> None:
        self._press_progress = float(value)
        self.update()

    pressProgress = Property(float, getPressProgress, setPressProgress)

    def sizeHint(self) -> QSize:  # type: ignore[override]
        cfg = self._size_config()
        metrics = self.fontMetrics()
        icon_width = self.iconSize().width() + 8 if not self.icon().isNull() else 0
        width = metrics.horizontalAdvance(self.text()) + int(cfg["padding_x"] * 2) + icon_width
        return QSize(max(width, 118), max(super().sizeHint().height(), int(cfg["height"])))

    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._animate(1.0, hover=True)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._animate(0.0, hover=True)
        if not self.isDown():
            self._animate(0.0, hover=False)
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self._animate(1.0, hover=False)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        super().mouseReleaseEvent(event)
        self._animate(0.16 if self.underMouse() else 0.0, hover=False)

    def focusInEvent(self, event) -> None:  # type: ignore[override]
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:  # type: ignore[override]
        self.update()
        super().focusOutEvent(event)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        del event
        palette = self._palette()
        cfg = self._size_config()
        hover = self._hover_progress
        press = self._press_progress
        enabled = self.isEnabled()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        outer = QRectF(self.rect()).adjusted(4.0, 4.0, -4.0, -4.0)
        if press > 0.0:
            outer.translate(0.0, 0.55 + press * 0.7)
        radius = float(cfg["radius"])

        self._paint_shadow(painter, outer, radius, palette, enabled, hover)
        self._paint_body(painter, outer, radius, palette, enabled, hover, press)
        self._paint_focus(painter, outer, radius, palette, enabled)
        self._draw_content(painter, outer, palette, enabled, press)

    def _paint_shadow(
        self,
        painter: QPainter,
        outer: QRectF,
        radius: float,
        palette: dict[str, QColor],
        enabled: bool,
        hover: float,
    ) -> None:
        if not enabled:
            return

        base_shadow = _with_alpha(palette["shadow"], 28)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(base_shadow)
        painter.drawRoundedRect(outer.adjusted(0.0, 5.5, 0.0, 6.5), radius + 0.5, radius + 0.5)

        for expand, alpha in ((10.0, 8), (6.0, 13), (2.0, 18 + int(hover * 8))):
            painter.setBrush(_with_alpha(palette["glow"], alpha))
            painter.drawRoundedRect(
                outer.adjusted(-expand, -expand * 0.45, expand, expand * 0.55),
                radius + expand,
                radius + expand,
            )

    def _paint_body(
        self,
        painter: QPainter,
        outer: QRectF,
        radius: float,
        palette: dict[str, QColor],
        enabled: bool,
        hover: float,
        press: float,
    ) -> None:
        fill_top = _mix(palette["fill_top"], palette["sheen"], 0.14 + hover * 0.06)
        fill_bottom = _mix(palette["fill_bottom"], palette["tint"], 0.10 + hover * 0.09)
        if press > 0.0:
            fill_top = _mix(fill_top, QColor("#ffffff"), 0.05)
            fill_bottom = _mix(fill_bottom, QColor("#000000"), 0.05)
        if not enabled:
            fill_top = _mix(fill_top, palette["disabled_fill"], 0.6)
            fill_bottom = _mix(fill_bottom, palette["disabled_fill"], 0.62)

        body_path = QPainterPath()
        body_path.addRoundedRect(outer, radius, radius)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_vertical_gradient(outer, fill_top, fill_bottom))
        painter.drawPath(body_path)

        glass_rect = outer.adjusted(1.0, 1.0, -1.0, -1.0)
        painter.setBrush(
            _vertical_gradient(
                glass_rect,
                _with_alpha(QColor("#ffffff"), 42 + int(hover * 10)),
                _with_alpha(QColor("#ffffff"), 8),
            )
        )
        painter.drawRoundedRect(glass_rect, radius - 1.1, radius - 1.1)

        frost_rect = outer.adjusted(0.8, outer.height() * 0.30, -0.8, -1.0)
        painter.setBrush(
            _vertical_gradient(
                frost_rect,
                _with_alpha(palette["frost"], 20 + int(hover * 10)),
                _with_alpha(palette["frost"], 4),
            )
        )
        painter.drawRoundedRect(frost_rect, radius - 1.2, radius - 1.2)

        highlight_rect = outer.adjusted(2.2, 1.8, -2.2, -outer.height() * 0.46)
        painter.setBrush(
            _vertical_gradient(
                highlight_rect,
                _with_alpha(QColor("#ffffff"), 64 + int(hover * 14)),
                _with_alpha(QColor("#ffffff"), 0),
            )
        )
        painter.drawRoundedRect(highlight_rect, max(radius - 3.0, 6.0), max(radius - 3.0, 6.0))

        pearl_sweep = QRectF(outer.left() + outer.width() * 0.32, outer.top() + 2.0, outer.width() * 0.48, outer.height() * 0.52)
        painter.setBrush(
            _diagonal_gradient(
                pearl_sweep,
                _with_alpha(QColor("#ffffff"), 10),
                _with_alpha(palette["pearl"], 34 + int(hover * 10)),
            )
        )
        painter.drawRoundedRect(pearl_sweep, radius - 3.5, radius - 3.5)

        inner_stroke_rect = outer.adjusted(1.0, 1.0, -1.0, -1.0)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(_with_alpha(QColor("#ffffff"), 58 if enabled else 24), 1.0))
        painter.drawRoundedRect(inner_stroke_rect, radius - 1.0, radius - 1.0)

        edge_gradient = _horizontal_gradient(
            outer,
            _with_alpha(palette["edge_start"], 116 if enabled else 45),
            _with_alpha(palette["edge_end"], 92 if enabled else 35),
        )
        painter.setPen(QPen(edge_gradient, 1.15))
        painter.drawRoundedRect(outer.adjusted(0.55, 0.55, -0.55, -0.55), radius - 0.65, radius - 0.65)

        base_line = QRectF(outer.left() + 2.0, outer.bottom() - 5.0, outer.width() - 4.0, 2.2)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(
            _horizontal_gradient(
                base_line,
                _with_alpha(palette["accent"], 12 + int(hover * 10)),
                _with_alpha(palette["accent_2"], 5 + int(hover * 6)),
            )
        )
        painter.drawRoundedRect(base_line, 1.2, 1.2)

    def _paint_focus(
        self,
        painter: QPainter,
        outer: QRectF,
        radius: float,
        palette: dict[str, QColor],
        enabled: bool,
    ) -> None:
        if not (enabled and self.hasFocus()):
            return
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(_with_alpha(palette["focus"], 88), 1.35))
        painter.drawRoundedRect(outer.adjusted(-3.0, -3.0, 3.0, 3.0), radius + 3.0, radius + 3.0)

    def _draw_content(
        self,
        painter: QPainter,
        outer: QRectF,
        palette: dict[str, QColor],
        enabled: bool,
        press: float,
    ) -> None:
        metrics = self.fontMetrics()
        icon = self.icon()
        icon_gap = 8 if not icon.isNull() else 0
        icon_size = self.iconSize()
        text_width = metrics.horizontalAdvance(self.text())
        icon_width = icon_size.width() if not icon.isNull() else 0
        total_width = icon_width + icon_gap + text_width

        start_x = outer.center().x() - total_width / 2.0
        baseline_y = outer.center().y() + metrics.ascent() / 2.0 - metrics.descent() / 2.0 + press * 0.35

        if not icon.isNull():
            pixmap = icon.pixmap(icon_size)
            icon_x = int(start_x)
            icon_y = int(outer.center().y() - pixmap.height() / 2.0 + press * 0.35)
            painter.setOpacity(0.94 if enabled else 0.45)
            painter.drawPixmap(icon_x, icon_y, pixmap)
            painter.setOpacity(1.0)
            start_x += icon_width + icon_gap

        text_color = palette["text"] if enabled else palette["muted"]
        glow_color = _with_alpha(QColor("#ffffff"), 40 if enabled else 12)
        painter.setFont(self.font())
        painter.setPen(glow_color)
        painter.drawText(int(start_x), int(baseline_y + 1.0), self.text())
        painter.setPen(text_color)
        painter.drawText(int(start_x), int(baseline_y), self.text())

    def _theme_colors(self) -> Mapping[str, str]:
        try:
            from ui.theme.theme_api import get_theme

            return get_theme().tokens.colors
        except Exception:
            return {
                "canvas": "#0b1118",
                "panel": "#151f2b",
                "panel_alt": "#1a2634",
                "surface": "#202f40",
                "hairline": "#2b3d52",
                "focus": "#4da6ff",
                "focus_soft": "#294f72",
                "text": "#e5edf6",
                "text_soft": "#b7c6d6",
                "text_muted": "#8ea1b7",
                "text_inverse": "#081119",
                "warning": "#f4b45a",
                "danger": "#ff6f75",
                "positive": "#36c57a",
            }

    def _palette(self) -> dict[str, QColor]:
        colors = self._theme_colors()
        variant = self._normalize_variant(str(self.property("variant") or "command"))

        canvas = QColor(colors.get("canvas", "#0b1118"))
        surface = QColor(colors.get("surface", "#202f40"))
        panel = QColor(colors.get("panel", "#151f2b"))
        panel_alt = QColor(colors.get("panel_alt", "#1a2634"))
        focus = QColor(colors.get("focus", "#4da6ff"))
        text = QColor(colors.get("text", "#e5edf6"))
        text_muted = QColor(colors.get("text_muted", "#8ea1b7"))
        success = QColor(colors.get("positive", colors.get("success", "#36c57a")))
        warning = QColor(colors.get("warning", "#f4b45a"))
        danger = QColor(colors.get("danger", "#ff6f75"))

        if variant == "primary":
            accent = _mix(focus, QColor("#9ed8ff"), 0.30)
            accent_2 = _mix(QColor("#e2d7ff"), focus, 0.22)
            tint = _mix(focus, QColor("#ffffff"), 0.90)
            text = QColor(colors.get("text_inverse", "#081119"))
        elif variant == "success":
            accent = _mix(success, QColor("#b6f2d1"), 0.36)
            accent_2 = _mix(QColor("#f4fffb"), success, 0.22)
            tint = _mix(success, QColor("#ffffff"), 0.90)
        elif variant == "warning":
            accent = _mix(warning, QColor("#ffe8be"), 0.34)
            accent_2 = _mix(QColor("#fff7ea"), warning, 0.20)
            tint = _mix(warning, QColor("#ffffff"), 0.89)
        elif variant == "danger":
            accent = _mix(danger, QColor("#ffd1d6"), 0.32)
            accent_2 = _mix(QColor("#fff0f2"), danger, 0.18)
            tint = _mix(danger, QColor("#ffffff"), 0.91)
        elif variant == "ghost":
            accent = _mix(focus, QColor("#d8ecff"), 0.24)
            accent_2 = _mix(QColor("#f5f9ff"), focus, 0.11)
            tint = _mix(surface, QColor("#ffffff"), 0.96)
            panel_alt = _with_alpha(panel_alt, 200)
            panel = _with_alpha(panel, 172)
        else:
            accent = _mix(focus, QColor("#cbe7ff"), 0.38)
            accent_2 = _mix(QColor("#f5f1ff"), focus, 0.16)
            tint = _mix(surface, QColor("#ffffff"), 0.92)

        fill_top = _mix(panel_alt, QColor("#ffffff"), 0.10)
        fill_bottom = _mix(panel, canvas, 0.18)
        shadow = _mix(canvas, QColor("#000000"), 0.32)
        pearl = _mix(QColor("#ffffff"), accent_2, 0.22)
        frost = _mix(QColor("#ffffff"), tint, 0.16)
        glow = _mix(accent, QColor("#ffffff"), 0.34)
        edge_start = _mix(QColor("#ffffff"), accent, 0.18)
        edge_end = _mix(QColor("#ffffff"), accent_2, 0.28)

        return {
            "fill_top": fill_top,
            "fill_bottom": fill_bottom,
            "sheen": QColor("#ffffff"),
            "tint": tint,
            "pearl": pearl,
            "frost": frost,
            "accent": accent,
            "accent_2": accent_2,
            "edge_start": edge_start,
            "edge_end": edge_end,
            "text": text,
            "muted": text_muted,
            "focus": focus,
            "glow": glow,
            "shadow": shadow,
            "disabled_fill": _mix(panel, canvas, 0.42),
        }


def _with_alpha(color: QColor, alpha: int) -> QColor:
    clone = QColor(color)
    clone.setAlpha(max(0, min(255, alpha)))
    return clone


def _mix(left: QColor, right: QColor, amount: float) -> QColor:
    t = max(0.0, min(1.0, amount))
    return QColor(
        int(left.red() + (right.red() - left.red()) * t),
        int(left.green() + (right.green() - left.green()) * t),
        int(left.blue() + (right.blue() - left.blue()) * t),
        int(left.alpha() + (right.alpha() - left.alpha()) * t),
    )


def _vertical_gradient(rect: QRectF, start: QColor, end: QColor) -> QLinearGradient:
    gradient = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
    gradient.setColorAt(0.0, start)
    gradient.setColorAt(1.0, end)
    return gradient


def _horizontal_gradient(rect: QRectF, start: QColor, end: QColor) -> QLinearGradient:
    gradient = QLinearGradient(rect.left(), rect.center().y(), rect.right(), rect.center().y())
    gradient.setColorAt(0.0, start)
    gradient.setColorAt(1.0, end)
    return gradient


def _diagonal_gradient(rect: QRectF, start: QColor, end: QColor) -> QLinearGradient:
    gradient = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.bottom())
    gradient.setColorAt(0.0, start)
    gradient.setColorAt(1.0, end)
    return gradient
