from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .controls import create_button
from .icons import apply_icon


def _safe_id(value: str) -> str:
    normalized = str(value or "").strip().lower()
    if not normalized:
        return "item"
    return "".join(ch if ch.isalnum() or ch in {"_", "-", ":"} else "_" for ch in normalized)


class GlassIconButton(QToolButton):
    def __init__(
        self,
        *,
        icon_name: str,
        tooltip: str = "",
        on_click: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("assetRole", "icon_button")
        if tooltip:
            self.setToolTip(tooltip)
            self.setAccessibleName(tooltip)
        apply_icon(self, icon_name, size="small", tooltip=tooltip, accessible_name=tooltip)
        if on_click is not None:
            self.clicked.connect(on_click)


@dataclass(frozen=True, slots=True)
class StatusPillSpec:
    text: str
    kind: str = "neutral"  # neutral|info|success|warning|error|pending


class StatusPill(QLabel):
    def __init__(self, text: str, *, kind: str = "neutral", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setProperty("assetRole", "status_pill")
        self.setProperty("statusKind", _safe_id(kind))


class StatPill(QFrame):
    def __init__(self, label: str, value: str, *, trend: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("assetRole", "stat_pill")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        label_widget = QLabel(label, self)
        label_widget.setProperty("role", "caption")
        value_widget = QLabel(value, self)
        value_widget.setProperty("role", "label")
        value_widget.setProperty("strong", True)
        layout.addWidget(label_widget, 1)
        layout.addWidget(value_widget, 0)
        if trend:
            trend_widget = QLabel(trend, self)
            trend_widget.setProperty("role", "caption")
            layout.addWidget(trend_widget, 0)


class GlassSegmentedControl(QFrame):
    value_changed = Signal(str)

    def __init__(
        self,
        options: Iterable[tuple[str, str]],
        *,
        selected: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("assetRole", "segmented")
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[str, QPushButton] = {}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        first_value: str | None = None
        for raw_value, label in options:
            value = _safe_id(raw_value)
            if first_value is None:
                first_value = value
            button = create_button(label, "ghost", parent=self)
            button.setProperty("assetRole", "segment_button")
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.clicked.connect(lambda _checked, current=value: self.value_changed.emit(current))
            self._group.addButton(button)
            self._buttons[value] = button
            layout.addWidget(button)

        initial = _safe_id(selected) if selected else first_value
        if initial and initial in self._buttons:
            self._buttons[initial].setChecked(True)

    def value(self) -> str:
        for value, button in self._buttons.items():
            if button.isChecked():
                return value
        return ""

    def set_value(self, value: str) -> None:
        normalized = _safe_id(value)
        button = self._buttons.get(normalized)
        if button is None:
            return
        button.setChecked(True)
        self.value_changed.emit(normalized)


class TogglePill(QPushButton):
    toggled_value = Signal(bool)

    def __init__(
        self,
        text_on: str = "On",
        text_off: str = "Off",
        *,
        checked: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._text_on = str(text_on or "On")
        self._text_off = str(text_off or "Off")
        self.setCheckable(True)
        self.setProperty("assetRole", "toggle_pill")
        self.setCursor(Qt.PointingHandCursor)
        self.toggled.connect(self._on_toggled)
        self.setChecked(bool(checked))
        self._on_toggled(self.isChecked())

    def _on_toggled(self, checked: bool) -> None:
        self.setText(self._text_on if checked else self._text_off)
        self.setProperty("checked", bool(checked))
        self.style().unpolish(self)
        self.style().polish(self)
        self.toggled_value.emit(bool(checked))


class FilterChipBar(QFrame):
    selection_changed = Signal(tuple)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("assetRole", "filter_chip_bar")
        self._chips: dict[str, QPushButton] = {}
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)

    def clear(self) -> None:
        self._chips.clear()
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def add_chip(self, value: str, label: str | None = None, *, checked: bool = False) -> None:
        normalized = _safe_id(value)
        if normalized in self._chips:
            return
        chip = create_button(label or value, "ghost", parent=self)
        chip.setProperty("assetRole", "filter_chip")
        chip.setCheckable(True)
        chip.setChecked(bool(checked))
        chip.toggled.connect(lambda _state: self.selection_changed.emit(self.selected_values()))
        self._chips[normalized] = chip
        self._layout.addWidget(chip)

    def selected_values(self) -> tuple[str, ...]:
        output: list[str] = []
        for value, chip in self._chips.items():
            if chip.isChecked():
                output.append(value)
        return tuple(output)

    def set_single_selection(self, value: str) -> None:
        normalized = _safe_id(value)
        for key, chip in self._chips.items():
            chip.setChecked(key == normalized)
        self.selection_changed.emit(self.selected_values())


class SearchCommandBar(QFrame):
    search_changed = Signal(str)

    def __init__(
        self,
        *,
        placeholder: str = "Search",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("assetRole", "search_bar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)

        self.input = QLineEdit(self)
        self.input.setPlaceholderText(placeholder)
        self.input.setClearButtonEnabled(True)
        self.input.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.input, 1)

        self.clear_button = GlassIconButton(
            icon_name="x",
            tooltip="Clear search",
            on_click=lambda: self.input.clear(),
            parent=self,
        )
        layout.addWidget(self.clear_button, 0)

    def text(self) -> str:
        return self.input.text().strip()


class CompactToolbar(QFrame):
    def __init__(self, title: str = "", *, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("assetRole", "compact_toolbar")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 3, 4, 3)
        layout.setSpacing(4)

        self.title_label = QLabel(title, self)
        self.title_label.setProperty("role", "panel_title")
        self.title_label.setVisible(bool(title))
        layout.addWidget(self.title_label)

        self.actions_row = QHBoxLayout()
        self.actions_row.setContentsMargins(0, 0, 0, 0)
        self.actions_row.setSpacing(6)
        layout.addLayout(self.actions_row)
        layout.addStretch(1)

    def add_action(
        self,
        text: str,
        *,
        icon_name: str | None = None,
        variant: str = "secondary",
        on_click: Callable[[], None] | None = None,
    ) -> QPushButton:
        button = create_button(text, variant, on_click, parent=self, icon_name=icon_name, icon_size="small")
        button.setProperty("assetRole", "toolbar_button")
        self.actions_row.addWidget(button)
        return button

    def add_icon_action(
        self,
        *,
        icon_name: str,
        tooltip: str,
        on_click: Callable[[], None] | None = None,
    ) -> GlassIconButton:
        button = GlassIconButton(icon_name=icon_name, tooltip=tooltip, on_click=on_click, parent=self)
        self.actions_row.addWidget(button)
        return button


class ControlCard(QFrame):
    def __init__(
        self,
        title: str,
        *,
        subtitle: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("assetRole", "control_card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 5, 6, 5)
        layout.setSpacing(6)

        title_widget = QLabel(title, self)
        title_widget.setProperty("role", "panel_title")
        layout.addWidget(title_widget)
        if subtitle:
            subtitle_widget = QLabel(subtitle, self)
            subtitle_widget.setProperty("role", "panel_subtitle")
            subtitle_widget.setWordWrap(True)
            layout.addWidget(subtitle_widget)

        self.content = QVBoxLayout()
        self.content.setContentsMargins(0, 0, 0, 0)
        self.content.setSpacing(8)
        layout.addLayout(self.content, 1)


class CollapsibleSection(QFrame):
    toggled = Signal(bool)

    def __init__(
        self,
        title: str,
        *,
        subtitle: str = "",
        collapsed: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("assetRole", "collapsible_section")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 3, 4, 3)
        layout.setSpacing(6)

        self.header_button = create_button(title, "ghost", parent=self)
        self.header_button.setProperty("assetRole", "collapsible_header")
        self.header_button.setCheckable(True)
        self.header_button.setChecked(not collapsed)
        self.header_button.clicked.connect(self._toggle_from_button)
        layout.addWidget(self.header_button)

        if subtitle:
            subtitle_widget = QLabel(subtitle, self)
            subtitle_widget.setProperty("role", "panel_subtitle")
            subtitle_widget.setWordWrap(True)
            layout.addWidget(subtitle_widget)

        self.body_host = QWidget(self)
        self.body_layout = QVBoxLayout(self.body_host)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(6)
        layout.addWidget(self.body_host, 1)
        self.set_collapsed(collapsed)

    def _toggle_from_button(self, checked: bool) -> None:
        self.set_collapsed(not checked)

    def set_collapsed(self, collapsed: bool) -> None:
        self.body_host.setVisible(not collapsed)
        self.header_button.setChecked(not collapsed)
        self.toggled.emit(not collapsed)


class EnhancedSlider(QFrame):
    value_changed = Signal(int)

    def __init__(
        self,
        label: str,
        *,
        minimum: int = 0,
        maximum: int = 100,
        value: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("assetRole", "enhanced_slider")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 3, 4, 3)
        layout.setSpacing(4)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(4)
        self.label = QLabel(label, self)
        self.label.setProperty("role", "label")
        top.addWidget(self.label, 1)
        self.value_label = QLabel(str(int(value)), self)
        self.value_label.setProperty("role", "caption")
        top.addWidget(self.value_label, 0)
        layout.addLayout(top)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(int(minimum))
        self.slider.setMaximum(max(int(maximum), int(minimum)))
        self.slider.setValue(max(int(minimum), min(int(maximum), int(value))))
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider)

    def _on_value_changed(self, value: int) -> None:
        self.value_label.setText(str(int(value)))
        self.value_changed.emit(int(value))


class ParameterPanel(QFrame):
    def __init__(
        self,
        title: str = "Parameters",
        *,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("assetRole", "parameter_panel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 5, 6, 5)
        layout.setSpacing(8)

        title_widget = QLabel(title, self)
        title_widget.setProperty("role", "panel_title")
        layout.addWidget(title_widget)

        self.form_host = QWidget(self)
        self.form_layout = QFormLayout(self.form_host)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(6)
        layout.addWidget(self.form_host)
        layout.addStretch(1)

    def add_text_field(self, label: str, *, placeholder: str = "") -> QLineEdit:
        field = QLineEdit(self.form_host)
        field.setPlaceholderText(placeholder)
        self.form_layout.addRow(label, field)
        return field

    def add_slider(
        self,
        label: str,
        *,
        minimum: int = 0,
        maximum: int = 100,
        value: int = 0,
    ) -> EnhancedSlider:
        slider = EnhancedSlider(label, minimum=minimum, maximum=maximum, value=value, parent=self.form_host)
        self.form_layout.addRow("", slider)
        return slider

    def add_toggle(self, label: str, *, checked: bool = False) -> TogglePill:
        toggle = TogglePill("Enabled", "Disabled", checked=checked, parent=self.form_host)
        self.form_layout.addRow(label, toggle)
        return toggle


class MiniLegend(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("assetRole", "mini_legend")
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 4, 8, 4)
        self._layout.setSpacing(6)

    def add_status(self, text: str, kind: str = "neutral") -> StatusPill:
        pill = StatusPill(text, kind=kind, parent=self)
        self._layout.addWidget(pill)
        return pill


class HeroPanel(QFrame):
    def __init__(
        self,
        title: str,
        *,
        subtitle: str = "",
        eyebrow: str = "SHOWCASE",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("assetRole", "hero_panel")
        self.setProperty("card", "hero")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(3)

        if eyebrow:
            eyebrow_label = QLabel(eyebrow, self)
            eyebrow_label.setProperty("role", "eyebrow")
            layout.addWidget(eyebrow_label)
        title_label = QLabel(title, self)
        title_label.setProperty("role", "title")
        layout.addWidget(title_label)
        if subtitle:
            subtitle_label = QLabel(subtitle, self)
            subtitle_label.setProperty("role", "panel_subtitle")
            subtitle_label.setWordWrap(True)
            layout.addWidget(subtitle_label)
