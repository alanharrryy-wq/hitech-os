from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QStackedLayout, QVBoxLayout, QWidget

from ..controls.chips import create_chip
from ..controls.icons import icon_text
from ..effects.polish import enable_card_hover, repolish
from ..effects.shadow import apply_shadow
from ..widgets.primitives import make_separator


@dataclass(slots=True)
class ChartSlotSnapshot:
    title: str
    subtitle: str
    tone: str = "neutral"
    icon: str | None = "chart"
    badge_text: str = "Standby"
    bullet_points: tuple[str, ...] = ()
    footer: str = ""


class _ChartStateCard(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("chart_slot", "state_card")
        self.setObjectName("ChartSlotStateCard")
        apply_shadow(self, blur=16.0, y_offset=6.0, alpha=12)
        enable_card_hover(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        layout.addLayout(top_row)

        self._glyph_label = QLabel(self)
        self._glyph_label.setProperty("chart_slot_role", "glyph")
        self._glyph_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._glyph_label.setMinimumSize(42, 42)
        self._glyph_label.setMaximumSize(42, 42)
        top_row.addWidget(self._glyph_label, 0, Qt.AlignmentFlag.AlignTop)

        title_stack = QVBoxLayout()
        title_stack.setSpacing(3)
        top_row.addLayout(title_stack, 1)

        self._eyebrow_label = QLabel("AUX SLOT", self)
        self._eyebrow_label.setProperty("chart_slot_role", "eyebrow")
        title_stack.addWidget(self._eyebrow_label)

        self._title_label = QLabel(self)
        self._title_label.setProperty("chart_slot_role", "title")
        self._title_label.setWordWrap(True)
        title_stack.addWidget(self._title_label)

        self._subtitle_label = QLabel(self)
        self._subtitle_label.setProperty("chart_slot_role", "subtitle")
        self._subtitle_label.setWordWrap(True)
        title_stack.addWidget(self._subtitle_label)

        self._tone_chip = create_chip("Standby", tone="neutral", icon="status", parent=self)
        top_row.addWidget(self._tone_chip, 0, Qt.AlignmentFlag.AlignTop)

        layout.addWidget(make_separator())

        self._bullet_box = QVBoxLayout()
        self._bullet_box.setSpacing(6)
        layout.addLayout(self._bullet_box)

        self._footer_label = QLabel(self)
        self._footer_label.setProperty("chart_slot_role", "footer")
        self._footer_label.setWordWrap(True)
        layout.addWidget(self._footer_label)

        layout.addStretch(1)
        self.apply_snapshot(
            ChartSlotSnapshot(
                title="Chart surface ready",
                subtitle="The aux panel is live and waiting for a chart widget or diagnostics state.",
                tone="neutral",
                icon="chart",
                badge_text="Standby",
                bullet_points=(
                    "Use set_chart_widget(...) to attach a real chart surface.",
                    "Use show_missing_dependencies(...) to present a graceful fallback.",
                ),
                footer="The shell keeps this slot reusable for metrics, inspectors, timelines, or logs.",
            )
        )

    def _clear_bullets(self) -> None:
        while self._bullet_box.count():
            item = self._bullet_box.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def apply_snapshot(self, snapshot: ChartSlotSnapshot) -> None:
        self._glyph_label.setText(icon_text("", snapshot.icon))
        self._title_label.setText(snapshot.title)
        self._subtitle_label.setText(snapshot.subtitle)
        self._tone_chip.setText(icon_text(snapshot.badge_text, "status"))
        self._tone_chip.setProperty("tone", snapshot.tone)
        repolish(self._tone_chip)

        self._clear_bullets()
        for point in snapshot.bullet_points:
            label = QLabel(f"• {point}", self)
            label.setWordWrap(True)
            label.setProperty("chart_slot_role", "bullet")
            self._bullet_box.addWidget(label)

        footer = str(snapshot.footer or "").strip()
        self._footer_label.setVisible(bool(footer))
        self._footer_label.setText(footer)


class ChartSlotPanel(QFrame):
    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        empty_title: str = "Chart surface ready",
        empty_subtitle: str = "Attach a real chart widget here, or leave it as a graceful diagnostics panel.",
    ) -> None:
        super().__init__(parent)
        self.setProperty("chart_slot", "root")
        self.setObjectName("ChartSlotPanel")
        self._chart_widget: QWidget | None = None
        self._chart_visible = True
        self._visible_snapshot = ChartSlotSnapshot(
            title=empty_title,
            subtitle=empty_subtitle,
            tone="neutral",
            icon="chart",
            badge_text="Standby",
            bullet_points=(
                "The aux slot is provisioned for charts, KPI strips, logs, or custom inspectors.",
                "A real widget can be attached without rebuilding the shell layout.",
            ),
            footer="This slot stays reusable, so product UI can grow on top without reworking the shell.",
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._stack = QStackedLayout()
        self._stack.setContentsMargins(0, 0, 0, 0)
        root.addLayout(self._stack, 1)

        self._state_card = _ChartStateCard(self)
        self._stack.addWidget(self._state_card)

        self._content_surface = QFrame(self)
        self._content_surface.setProperty("chart_slot", "content_surface")
        self._content_surface.setObjectName("ChartSlotContentSurface")
        content_layout = QVBoxLayout(self._content_surface)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        self._content_layout = content_layout
        self._stack.addWidget(self._content_surface)

        self.show_placeholder(empty_subtitle, title=empty_title)

    @property
    def chart_widget(self) -> QWidget | None:
        return self._chart_widget

    def has_chart_widget(self) -> bool:
        return self._chart_widget is not None

    def is_chart_visible(self) -> bool:
        return self._chart_visible

    def _set_state(self, snapshot: ChartSlotSnapshot) -> None:
        self._visible_snapshot = snapshot
        self._state_card.apply_snapshot(snapshot)
        if self._chart_widget is None and self._chart_visible:
            self._stack.setCurrentWidget(self._state_card)

    def _show_hidden_state(self) -> None:
        hidden_snapshot = ChartSlotSnapshot(
            title="Charts hidden",
            subtitle="The chart surface is tucked away, but the layout stays warm and the shell remains stable.",
            tone="accent",
            icon="preview",
            badge_text="Hidden",
            bullet_points=(
                "Use the toolbar toggle to restore the chart area instantly.",
                "The current chart widget is preserved and will come back without rebuilding the shell."
                if self._chart_widget is not None
                else "No chart widget is loaded yet, so the slot remains in standby mode.",
            ),
            footer="Hiding charts keeps the aux column visually disciplined without tearing down state.",
        )
        self._state_card.apply_snapshot(hidden_snapshot)
        self._stack.setCurrentWidget(self._state_card)

    def _detach_chart_widget(self, *, delete: bool = False) -> QWidget | None:
        if self._chart_widget is None:
            return None
        widget = self._chart_widget
        self._content_layout.removeWidget(widget)
        widget.setParent(None)
        self._chart_widget = None
        if delete:
            widget.deleteLater()
        return widget

    def set_chart_widget(self, widget: QWidget) -> None:
        if widget is None:
            self.clear_chart_widget(delete=False)
            return
        if self._chart_widget is widget:
            if self._chart_visible:
                self._stack.setCurrentWidget(self._content_surface)
            return

        self._detach_chart_widget(delete=False)
        self._chart_widget = widget
        widget.setParent(self._content_surface)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._content_layout.addWidget(widget, 1)

        if self._chart_visible:
            self._stack.setCurrentWidget(self._content_surface)
        else:
            self._show_hidden_state()

    def clear_chart_widget(self, *, delete: bool = False) -> None:
        self._detach_chart_widget(delete=delete)
        if self._chart_visible:
            self._state_card.apply_snapshot(self._visible_snapshot)
            self._stack.setCurrentWidget(self._state_card)
        else:
            self._show_hidden_state()

    def show_status(
        self,
        title: str,
        subtitle: str,
        *,
        tone: str = "neutral",
        icon: str | None = "chart",
        badge_text: str = "Standby",
        bullet_points: Iterable[str] = (),
        footer: str = "",
    ) -> None:
        snapshot = ChartSlotSnapshot(
            title=title,
            subtitle=subtitle,
            tone=tone,
            icon=icon,
            badge_text=badge_text,
            bullet_points=tuple(str(item).strip() for item in bullet_points if str(item).strip()),
            footer=footer,
        )
        self._set_state(snapshot)

    def show_placeholder(
        self,
        message: str,
        *,
        title: str = "Chart surface ready",
        details: Iterable[str] = (),
        footer: str = "Attach a chart widget when product metrics are ready to render.",
    ) -> None:
        bullets = tuple(str(item).strip() for item in details if str(item).strip()) or (
            "Real chart widgets can be attached without rebuilding the surrounding shell.",
            "Use this state for demos, empty states, diagnostics, or progressive rollout messaging.",
        )
        self.show_status(
            title=title,
            subtitle=message,
            tone="neutral",
            icon="chart",
            badge_text="Standby",
            bullet_points=bullets,
            footer=footer,
        )

    def show_missing_dependencies(self, missing: Iterable[str]) -> None:
        normalized = tuple(sorted({str(item).strip() for item in missing if str(item).strip()}))
        bullets = tuple(f"Missing optional dependency: {name}" for name in normalized) or (
            "The chart engine reported unavailable optional dependencies.",
        )
        self.show_status(
            title="Charts unavailable",
            subtitle="The chart engine is present, but optional UI dependencies are missing.",
            tone="warn",
            icon="warning",
            badge_text="Unavailable",
            bullet_points=bullets + (
                "Install the optional chart extras and reopen the panel to unlock the full glass chart surface.",
            ),
            footer="The rest of the shell stays fully usable, so product work can continue while the chart stack is repaired.",
        )

    def set_chart_visible(self, visible: bool) -> None:
        self._chart_visible = bool(visible)
        if self._chart_visible:
            if self._chart_widget is not None:
                self._stack.setCurrentWidget(self._content_surface)
            else:
                self._state_card.apply_snapshot(self._visible_snapshot)
                self._stack.setCurrentWidget(self._state_card)
            return
        self._show_hidden_state()
