from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from .assets import CompactToolbar
from .controls import create_button
from .icons import apply_icon


class PanelHeader(QFrame):
    def __init__(
        self,
        title: str,
        *,
        subtitle: str = "",
        icon_name: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("card", "clear")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(6)

        self._icon = QLabel("", self)
        self._icon.setFixedWidth(18)
        if icon_name:
            apply_icon(self._icon, icon_name, size="small")
        layout.addWidget(self._icon, 0, Qt.AlignTop)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)
        self.title = QLabel(title, self)
        self.title.setProperty("role", "panel_title")
        self.subtitle = QLabel(subtitle, self)
        self.subtitle.setProperty("role", "panel_subtitle")
        self.subtitle.setVisible(bool(subtitle))
        text_col.addWidget(self.title)
        text_col.addWidget(self.subtitle)
        layout.addLayout(text_col, 1)

        self.actions = QHBoxLayout()
        self.actions.setContentsMargins(0, 0, 0, 0)
        self.actions.setSpacing(6)
        layout.addLayout(self.actions, 0)

    def add_action(
        self,
        text: str,
        *,
        variant: str = "secondary",
        icon_name: str | None = None,
        on_click: Callable[[], None] | None = None,
    ) -> QWidget:
        button = create_button(
            text,
            variant,
            on_click,
            parent=self,
            icon_name=icon_name,
            icon_size="small",
        )
        self.actions.addWidget(button)
        return button


class QuickActionsStrip(CompactToolbar):
    """Backward-compatible alias of CompactToolbar with hidden title.

    Existing code keeps using QuickActionsStrip while sharing the same
    implementation path as the newer toolbar asset.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("", parent=parent)
        self.title_label.setVisible(False)
        self.setProperty("card", "clear")

    def add_action(
        self,
        text: str,
        *,
        icon_name: str | None = None,
        variant: str = "secondary",
        on_click: Callable[[], None] | None = None,
    ) -> QWidget:
        return super().add_action(
            text,
            icon_name=icon_name,
            variant=variant,
            on_click=on_click,
        )


@dataclass(frozen=True, slots=True)
class MetricValue:
    label: str
    value: str
    trend: str = ""


class StatCard(QFrame):
    def __init__(self, metric: MetricValue, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("card", "clear")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        label = QLabel(metric.label, self)
        label.setProperty("role", "caption")
        value = QLabel(metric.value, self)
        value.setProperty("role", "title")
        trend = QLabel(metric.trend, self)
        trend.setProperty("role", "panel_subtitle")
        trend.setVisible(bool(metric.trend))

        layout.addWidget(label)
        layout.addWidget(value)
        layout.addWidget(trend)


class _StateCardBase(QFrame):
    def __init__(
        self,
        title: str,
        message: str,
        *,
        icon_name: str,
        meta: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("card", "clear")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)
        self.header = PanelHeader(title, subtitle=message, icon_name=icon_name, parent=self)
        layout.addWidget(self.header)
        self.meta_label = QLabel(meta, self)
        self.meta_label.setProperty("role", "caption")
        self.meta_label.setWordWrap(True)
        self.meta_label.setVisible(bool(meta))
        layout.addWidget(self.meta_label)
        self.actions = QHBoxLayout()
        self.actions.setContentsMargins(0, 0, 0, 0)
        self.actions.setSpacing(8)
        layout.addLayout(self.actions)

    def add_action(
        self,
        text: str,
        *,
        variant: str = "secondary",
        icon_name: str | None = None,
        on_click: Callable[[], None] | None = None,
    ) -> QWidget:
        button = create_button(text, variant, on_click, parent=self, icon_name=icon_name, icon_size="small")
        self.actions.addWidget(button)
        return button


class EmptyStateCard(_StateCardBase):
    def __init__(
        self,
        title: str,
        message: str,
        *,
        icon_name: str = "info",
        meta: str = "",
        action_label: str | None = None,
        action: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(title, message, icon_name=icon_name, meta=meta, parent=parent)
        if action_label and action is not None:
            self.add_action(action_label, variant="ghost", icon_name="refresh-cw", on_click=action)


class LoadingStateCard(_StateCardBase):
    def __init__(
        self,
        title: str = "Loading",
        *,
        message: str = "Preparing content...",
        meta: str = "",
        progress: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(title, message, icon_name="loader", meta=meta, parent=parent)
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setValue(max(0, min(100, int(progress))))
        self.layout().addWidget(self.progress)


class ErrorStateCard(_StateCardBase):
    def __init__(
        self,
        title: str = "Error",
        message: str = "Something went wrong.",
        *,
        details: str = "",
        retry: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(title, message, icon_name="alert-triangle", meta=details, parent=parent)
        if retry is not None:
            self.add_action("Retry", variant="warning", icon_name="refresh-cw", on_click=retry)


class FormSectionShell(QFrame):
    def __init__(self, title: str, *, subtitle: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("card", "clear")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(6)
        self.header = PanelHeader(title, subtitle=subtitle, icon_name="file-text", parent=self)
        layout.addWidget(self.header)
        self.content = QVBoxLayout()
        self.content.setContentsMargins(0, 0, 0, 0)
        self.content.setSpacing(8)
        layout.addLayout(self.content, 1)


class DashboardWidgetShell(QFrame):
    def __init__(self, title: str, *, subtitle: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("card", "clear")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(6)
        self.header = PanelHeader(title, subtitle=subtitle, icon_name="activity", parent=self)
        layout.addWidget(self.header)
        self.content = QVBoxLayout()
        self.content.setContentsMargins(0, 0, 0, 0)
        self.content.setSpacing(8)
        layout.addLayout(self.content, 1)
