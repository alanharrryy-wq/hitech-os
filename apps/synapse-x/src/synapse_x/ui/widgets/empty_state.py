
from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from visuals.controls.chips import create_chip
from visuals.controls.icons import icon_text
from visuals.effects.polish import enable_card_hover, repolish
from visuals.effects.shadow import apply_shadow
from visuals.effects.polish import repolish
from visuals.widgets.primitives import make_separator


class EmptyStateCard(QFrame):
    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "Nothing loaded yet",
        subtitle: str = "This surface is waiting for live content.",
        icon: str | None = "preview",
        tone: str = "neutral",
        badge_text: str = "Standby",
    ) -> None:
        super().__init__(parent)
        self.setProperty("card", "muted")
        apply_shadow(self, blur=15.0, y_offset=5.0, alpha=10)
        enable_card_hover(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        top_row = QVBoxLayout()
        top_row.setSpacing(4)
        layout.addLayout(top_row)

        self.badge = create_chip(badge_text, tone=tone, icon="status", parent=self)
        top_row.addWidget(self.badge, 0, Qt.AlignmentFlag.AlignLeft)

        self.title_label = QLabel(icon_text(title, icon), self)
        self.title_label.setProperty("role", "section")
        self.title_label.setWordWrap(True)
        top_row.addWidget(self.title_label)

        self.subtitle_label = QLabel(subtitle, self)
        self.subtitle_label.setProperty("role", "hint")
        self.subtitle_label.setWordWrap(True)
        top_row.addWidget(self.subtitle_label)

        layout.addWidget(make_separator())

        self.points_box = QVBoxLayout()
        self.points_box.setSpacing(6)
        layout.addLayout(self.points_box)
        layout.addStretch(1)

    def _clear_points(self) -> None:
        while self.points_box.count():
            item = self.points_box.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def set_state(
        self,
        title: str,
        subtitle: str,
        *,
        icon: str | None = "preview",
        tone: str = "neutral",
        badge_text: str = "Standby",
        points: Iterable[str] = (),
    ) -> None:
        self.badge.setText(icon_text(badge_text, "status"))
        self.badge.setProperty("tone", tone)
        repolish(self.badge)
        self.title_label.setText(icon_text(title, icon))
        self.subtitle_label.setText(subtitle)
        self._clear_points()
        for point in points:
            label = QLabel(f"• {point}", self)
            label.setProperty("role", "hint")
            label.setWordWrap(True)
            self.points_box.addWidget(label)
