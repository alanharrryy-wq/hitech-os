from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QEasingCurve, QObject, QVariantAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget


class DeckStateAnimator(QObject):
    """Optional widget-local motion helper for Aegis Deck.

    Shared infrastructure rules:
    - no geometry animation
    - no layout margin animation
    - no splitter or position mutation
    - correctness does not depend on animations being enabled
    """

    def __init__(self, parent: QObject | None = None, *, animation_enabled: bool = True) -> None:
        super().__init__(parent)
        self._animation_enabled = bool(animation_enabled)
        self._animations: dict[str, QVariantAnimation] = {}

    def set_animation_enabled(self, enabled: bool) -> None:
        self._animation_enabled = bool(enabled)
        if not self._animation_enabled:
            self.stop()

    def animation_enabled(self) -> bool:
        return self._animation_enabled

    def stop(self, key: str | None = None) -> None:
        if key is None:
            keys = list(self._animations.keys())
        else:
            keys = [str(key)]
        for item in keys:
            animation = self._animations.pop(item, None)
            if animation is None:
                continue
            if not _is_qobject_alive(animation):
                continue
            try:
                animation.stop()
            except Exception:
                pass
            try:
                animation.deleteLater()
            except Exception:
                pass

    def _track_lifecycle(self, key: str, target: QObject | None) -> None:
        """Stop an animation key as soon as the target QObject is destroyed."""
        if target is None:
            return
        if not _is_qobject_alive(target):
            self.stop(key)
            return
        try:
            target.destroyed.connect(lambda *_: self.stop(key))
        except Exception:
            pass

    def fade_widget(
        self,
        widget: QWidget | None,
        *,
        key: str | None = None,
        start: float | None = None,
        end: float = 1.0,
        duration_ms: int = 140,
        easing: QEasingCurve.Type = QEasingCurve.OutCubic,
    ) -> bool:
        if widget is None:
            return False
        effect = widget.graphicsEffect()
        if effect is not None and not isinstance(effect, QGraphicsOpacityEffect):
            widget.setWindowOpacity(1.0)
            return False
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
        target_key = key or f"fade:{id(widget)}"
        end_value = _clamp_scalar(end)
        if not self._animation_enabled or duration_ms <= 0:
            try:
                effect.setOpacity(end_value)
            except Exception:
                pass
            self.stop(target_key)
            return False
        current_value = effect.opacity()
        start_value = current_value if start is None else _clamp_scalar(start)
        try:
            effect.setOpacity(start_value)
        except Exception:
            self.stop(target_key)
            return False
        self._track_lifecycle(target_key, widget)
        self._track_lifecycle(target_key, effect)

        def _apply(value: float) -> None:
            if not _is_qobject_alive(effect):
                self.stop(target_key)
                return
            try:
                effect.setOpacity(_clamp_scalar(value))
            except Exception:
                self.stop(target_key)

        return self.animate_scalar(
            target_key,
            start=start_value,
            end=end_value,
            duration_ms=duration_ms,
            easing=easing,
            on_value=_apply,
        )

    def animate_scalar(
        self,
        key: str,
        *,
        start: float,
        end: float,
        duration_ms: int = 140,
        easing: QEasingCurve.Type = QEasingCurve.OutCubic,
        on_value: Callable[[float], None] | None = None,
        on_finished: Callable[[], None] | None = None,
    ) -> bool:
        safe_key = str(key or "scalar")
        end_value = float(end)
        if on_value is None:
            if on_finished is not None:
                on_finished()
            return False
        if not self._animation_enabled or duration_ms <= 0:
            try:
                on_value(end_value)
            except Exception:
                self.stop(safe_key)
                return False
            if on_finished is not None:
                on_finished()
            self.stop(safe_key)
            return False
        animation = QVariantAnimation(self)
        animation.setStartValue(float(start))
        animation.setEndValue(end_value)
        animation.setDuration(max(1, int(duration_ms)))
        animation.setEasingCurve(easing)

        def _emit_value(value: object) -> None:
            try:
                on_value(float(value))
            except Exception:
                self.stop(safe_key)

        animation.valueChanged.connect(_emit_value)
        if on_finished is not None:
            animation.finished.connect(on_finished)
        animation.finished.connect(lambda: self._animations.pop(safe_key, None))
        self.stop(safe_key)
        self._animations[safe_key] = animation
        animation.start()
        return True

    def pulse_scalar(
        self,
        key: str,
        *,
        base: float,
        peak: float,
        duration_ms: int = 420,
        on_value: Callable[[float], None] | None = None,
        on_finished: Callable[[], None] | None = None,
    ) -> bool:
        safe_key = str(key or "pulse")
        if on_value is None:
            if on_finished is not None:
                on_finished()
            return False
        peak_value = float(peak)
        base_value = float(base)
        if not self._animation_enabled or duration_ms <= 0:
            on_value(base_value)
            if on_finished is not None:
                on_finished()
            self.stop(safe_key)
            return False
        animation = QVariantAnimation(self)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setDuration(max(1, int(duration_ms)))
        animation.setEasingCurve(QEasingCurve.InOutCubic)

        def _apply(progress: object) -> None:
            phase = _clamp_scalar(progress)
            triangle = 1.0 - abs((phase * 2.0) - 1.0)
            value = base_value + ((peak_value - base_value) * triangle)
            try:
                on_value(value)
            except Exception:
                self.stop(safe_key)

        animation.valueChanged.connect(_apply)

        def _reset_to_base() -> None:
            try:
                on_value(base_value)
            except Exception:
                self.stop(safe_key)

        animation.finished.connect(_reset_to_base)
        if on_finished is not None:
            animation.finished.connect(on_finished)
        animation.finished.connect(lambda: self._animations.pop(safe_key, None))
        self.stop(safe_key)
        self._animations[safe_key] = animation
        animation.start()
        return True

    def pulse_widget(
        self,
        widget: QWidget | None,
        *,
        key: str | None = None,
        property_name: str = "pulseStrength",
        base: float = 0.0,
        peak: float = 1.0,
        duration_ms: int = 420,
        on_finished: Callable[[], None] | None = None,
    ) -> bool:
        if widget is None:
            return False
        target_key = key or f"pulse:{id(widget)}:{property_name}"
        self._track_lifecycle(target_key, widget)

        def _apply(value: float) -> None:
            if not _is_qobject_alive(widget):
                self.stop(target_key)
                return
            widget.setProperty(property_name, float(value))
            style = widget.style()
            if style is not None:
                style.unpolish(widget)
                style.polish(widget)
            widget.update()

        return self.pulse_scalar(
            target_key,
            base=base,
            peak=peak,
            duration_ms=duration_ms,
            on_value=_apply,
            on_finished=on_finished,
        )



def _clamp_scalar(value: object, minimum: float = 0.0, maximum: float = 1.0) -> float:
    try:
        numeric = float(value)
    except Exception:
        numeric = minimum
    return max(minimum, min(maximum, numeric))


def _is_qobject_alive(target: QObject | None) -> bool:
    if target is None:
        return False
    try:
        import shiboken6

        return bool(shiboken6.isValid(target))
    except Exception:
        try:
            target.objectName()
            return True
        except Exception:
            return False


__all__ = ["DeckStateAnimator"]
