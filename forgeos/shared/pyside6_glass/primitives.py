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
        self.setProperty("card", "muted")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

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


class QuickActionsStrip(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("card", "muted")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        self._layout = layout

    def add_action(
        self,
        text: str,
        *,
        icon_name: str | None = None,
        variant: str = "secondary",
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
        self._layout.addWidget(button)
        return button


@dataclass(frozen=True, slots=True)
class MetricValue:
    label: str
    value: str
    trend: str = ""


class StatCard(QFrame):
    def __init__(self, metric: MetricValue, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("card", "true")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
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


class EmptyStateCard(QFrame):
    def __init__(self, title: str, message: str, *, icon_name: str = "info", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("card", "muted")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)
        header = PanelHeader(title, subtitle=message, icon_name=icon_name, parent=self)
        layout.addWidget(header)


class LoadingStateCard(QFrame):
    def __init__(self, title: str = "Loading", *, progress: int = 0, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("card", "muted")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)
        layout.addWidget(PanelHeader(title, subtitle="Preparing content...", icon_name="loader", parent=self))
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setValue(max(0, min(100, int(progress))))
        layout.addWidget(self.progress)


class ErrorStateCard(QFrame):
    def __init__(
        self,
        title: str = "Error",
        message: str = "Something went wrong.",
        *,
        retry: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("card", "muted")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)
        layout.addWidget(PanelHeader(title, subtitle=message, icon_name="alert-triangle", parent=self))
        if retry is not None:
            layout.addWidget(create_button("Retry", "warning", retry, parent=self, icon_name="refresh-cw"))


class FormSectionShell(QFrame):
    def __init__(self, title: str, *, subtitle: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("card", "true")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        self.header = PanelHeader(title, subtitle=subtitle, icon_name="file-text", parent=self)
        layout.addWidget(self.header)
        self.content = QVBoxLayout()
        self.content.setContentsMargins(0, 0, 0, 0)
        self.content.setSpacing(8)
        layout.addLayout(self.content, 1)


class DashboardWidgetShell(QFrame):
    def __init__(self, title: str, *, subtitle: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("card", "true")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        self.header = PanelHeader(title, subtitle=subtitle, icon_name="activity", parent=self)
        layout.addWidget(self.header)
        self.content = QVBoxLayout()
        self.content.setContentsMargins(0, 0, 0, 0)
        self.content.setSpacing(8)
        layout.addLayout(self.content, 1)
