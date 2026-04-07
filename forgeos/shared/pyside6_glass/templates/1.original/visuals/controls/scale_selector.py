from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidget

from ..effects.polish import repolish
from ..style.scale import all_scales, normalize_scale


class ScaleSelector(QFrame):
    def __init__(
        self,
        *,
        current_scale: str = "100",
        on_change: Callable[[str], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_change = on_change
        self._current_scale = normalize_scale(current_scale)
        self.setProperty("scale_selector", True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        self._buttons: dict[str, QPushButton] = {}
        for profile in all_scales():
            button = QPushButton(profile.label, self)
            button.setCheckable(True)
            button.setFocusPolicy(Qt.NoFocus)
            button.setProperty("scale_pill", True)
            button.setProperty("active", profile.scale_id == self._current_scale)
            button.clicked.connect(lambda checked=False, scale_id=profile.scale_id: self.set_scale(scale_id, emit=True))
            layout.addWidget(button, 0)
            self._buttons[profile.scale_id] = button

    @property
    def scale_id(self) -> str:
        return self._current_scale

    def set_scale(self, scale_id: str, *, emit: bool = False) -> None:
        # perf-safe-margin-patch: repolish only changed scale pills.
        resolved = normalize_scale(scale_id)
        if resolved == self._current_scale and not emit:
            return

        previous = self._current_scale
        self._current_scale = resolved
        changed_any = False

        for scale_key, button in self._buttons.items():
            active = scale_key == resolved
            if button.isChecked() != active:
                button.setChecked(active)
            if bool(button.property("active")) != active:
                button.setProperty("active", active)
                repolish(button)
                changed_any = True

        if previous != resolved or changed_any:
            repolish(self)

        if emit and callable(self._on_change):
            self._on_change(resolved)

