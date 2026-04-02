from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .chrome import WindowChromeBar
from .contracts import DEFAULT_THEME_ID
from .controls import create_button
from .scene import build_glass_dialog_scene


@dataclass(slots=True)
class GlassTemplateSlots:
    hero_slot: QVBoxLayout
    main_slot: QVBoxLayout
    side_slot: QVBoxLayout
    footer_slot: QHBoxLayout
    status_slot: QVBoxLayout


@dataclass(slots=True)
class GlassTemplateCards:
    shell: QFrame
    hero: QFrame
    main: QFrame
    side: QFrame
    footer: QFrame
    status: QFrame


@dataclass(slots=True)
class GlassTemplateActions:
    cancel_button: QPushButton | None
    submit_button: QPushButton | None


class GlassPanelTemplate(QWidget):
    """Clean reusable shell with card slots for fast tool construction."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        title: str = "Workspace",
        subtitle: str = "Compose your workflow with reusable glass cards.",
        eyebrow: str = "WORKSPACE",
        variant: str = "selector",
        theme_id: str = DEFAULT_THEME_ID,
        with_chrome: bool = True,
        show_side: bool = True,
        show_footer: bool = True,
        show_status: bool = True,
        include_default_actions: bool = True,
        cancel_text: str = "Cancelar",
        submit_text: str = "Continuar",
        cancel_variant: str = "danger",
        submit_variant: str = "primary",
        apply_stylesheet: bool = True,
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._subtitle = subtitle
        self._eyebrow = eyebrow
        self._variant = variant
        self._theme_id = theme_id
        self._show_side = show_side
        self._show_footer = show_footer
        self._show_status = show_status
        self._with_chrome = with_chrome
        self._include_default_actions = include_default_actions
        self._cancel_text = cancel_text
        self._submit_text = submit_text
        self._cancel_variant = cancel_variant
        self._submit_variant = submit_variant
        self._apply_stylesheet = apply_stylesheet

        self._title_label: QLabel | None = None
        self._subtitle_label: QLabel | None = None
        self._eyebrow_label: QLabel | None = None
        self._status_label: QLabel | None = None

        self.slots, self.cards, self.actions = self._build()

    def _card(self, card_kind: str) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame(self)
        card.setProperty("card", card_kind)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(10)
        return card, card_layout

    def _build(self) -> tuple[GlassTemplateSlots, GlassTemplateCards, GlassTemplateActions]:
        outer, content, self._glass_backdrop = build_glass_dialog_scene(
            self,
            theme_id=self._theme_id,
            variant=self._variant,
            apply_stylesheet=self._apply_stylesheet,
        )
        outer.setSpacing(0)

        scene_layout = QVBoxLayout(content)
        scene_layout.setContentsMargins(10, 10, 10, 10)
        scene_layout.setSpacing(0)

        shell = QFrame(self)
        shell.setObjectName("Shell")
        shell.setProperty("variant", self._variant)
        scene_layout.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(20, 20, 20, 20)
        shell_layout.setSpacing(14)

        if self._with_chrome:
            host = self.window() if isinstance(self.window(), QWidget) else self
            chrome = WindowChromeBar(host, title=self._title)
            shell_layout.addWidget(chrome)

        hero_card, hero_layout = self._card("hero")
        shell_layout.addWidget(hero_card)
        self._eyebrow_label = QLabel(self._eyebrow, hero_card)
        self._eyebrow_label.setProperty("role", "eyebrow")
        self._title_label = QLabel(self._title, hero_card)
        self._title_label.setProperty("role", "title")
        self._subtitle_label = QLabel(self._subtitle, hero_card)
        self._subtitle_label.setProperty("role", "subtitle")
        self._subtitle_label.setWordWrap(True)
        hero_layout.addWidget(self._eyebrow_label)
        hero_layout.addWidget(self._title_label)
        hero_layout.addWidget(self._subtitle_label)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 2)
        shell_layout.addLayout(grid, 1)

        main_card, main_layout = self._card("true")
        side_card, side_layout = self._card("muted")
        grid.addWidget(main_card, 0, 0)
        grid.addWidget(side_card, 0, 1)
        if not self._show_side:
            side_card.hide()

        footer = QFrame(self)
        footer.setProperty("card", "footer")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(14, 10, 14, 10)
        footer_layout.setSpacing(10)
        shell_layout.addWidget(footer)
        if not self._show_footer:
            footer.hide()

        status = QFrame(self)
        status.setProperty("card", "muted")
        status_layout = QVBoxLayout(status)
        status_layout.setContentsMargins(14, 10, 14, 10)
        status_layout.setSpacing(8)
        shell_layout.addWidget(status)
        if not self._show_status:
            status.hide()

        self._status_label = QLabel("", status)
        self._status_label.setProperty("role", "hint")
        self._status_label.setWordWrap(True)
        self._status_label.hide()
        status_layout.addWidget(self._status_label)

        cancel_button: QPushButton | None = None
        submit_button: QPushButton | None = None
        if self._show_footer:
            footer_layout.addStretch(1)
            if self._include_default_actions:
                cancel_button = create_button(
                    self._cancel_text,
                    self._cancel_variant,
                    parent=footer,
                )
                submit_button = create_button(
                    self._submit_text,
                    self._submit_variant,
                    parent=footer,
                )
                footer_layout.addWidget(cancel_button, 0, Qt.AlignRight)
                footer_layout.addWidget(submit_button, 0, Qt.AlignRight)

        slots = GlassTemplateSlots(
            hero_slot=hero_layout,
            main_slot=main_layout,
            side_slot=side_layout,
            footer_slot=footer_layout,
            status_slot=status_layout,
        )
        cards = GlassTemplateCards(
            shell=shell,
            hero=hero_card,
            main=main_card,
            side=side_card,
            footer=footer,
            status=status,
        )
        actions = GlassTemplateActions(
            cancel_button=cancel_button,
            submit_button=submit_button,
        )
        return slots, cards, actions

    def set_title(self, title: str) -> None:
        self._title = str(title)
        if self._title_label is not None:
            self._title_label.setText(self._title)

    def set_subtitle(self, subtitle: str) -> None:
        self._subtitle = str(subtitle)
        if self._subtitle_label is not None:
            self._subtitle_label.setText(self._subtitle)

    def set_eyebrow(self, eyebrow: str) -> None:
        self._eyebrow = str(eyebrow)
        if self._eyebrow_label is not None:
            self._eyebrow_label.setText(self._eyebrow)

    def set_status_text(self, text: str | None) -> None:
        if self._status_label is None:
            return
        value = (text or "").strip()
        if value:
            self._status_label.setText(value)
            self._status_label.show()
            self.cards.status.show()
            return
        self._status_label.hide()

    def set_side_visible(self, visible: bool) -> None:
        self.cards.side.setVisible(bool(visible))

    def set_footer_visible(self, visible: bool) -> None:
        self.cards.footer.setVisible(bool(visible))

    def set_status_visible(self, visible: bool) -> None:
        self.cards.status.setVisible(bool(visible))

    def set_submit_enabled(self, enabled: bool) -> None:
        if self.actions.submit_button is not None:
            self.actions.submit_button.setEnabled(bool(enabled))

    def bind_cancel(self, callback: Callable[[], None]) -> None:
        if self.actions.cancel_button is not None:
            self.actions.cancel_button.clicked.connect(callback)

    def bind_submit(self, callback: Callable[[], None]) -> None:
        if self.actions.submit_button is not None:
            self.actions.submit_button.clicked.connect(callback)

    def add_footer_action(
        self,
        text: str,
        variant: str = "secondary",
        *,
        align: str = "right",
        on_click: Callable[[], None] | None = None,
        minimum_width: int | None = None,
    ) -> QPushButton:
        button = create_button(
            text,
            variant,
            on_click=on_click,
            parent=self.cards.footer,
            minimum_width=minimum_width,
        )
        if align.strip().lower() == "left":
            self.slots.footer_slot.insertWidget(0, button, 0, Qt.AlignLeft)
        else:
            self.slots.footer_slot.addWidget(button, 0, Qt.AlignRight)
        return button

    def clear_slot(self, slot_name: str) -> None:
        normalized = slot_name.strip().lower()
        mapping = {
            "hero": self.slots.hero_slot,
            "main": self.slots.main_slot,
            "side": self.slots.side_slot,
            "footer": self.slots.footer_slot,
            "status": self.slots.status_slot,
        }
        layout = mapping.get(normalized)
        if layout is None:
            raise ValueError(f"Unknown slot '{slot_name}'")
        self._clear_layout(layout)

    def _clear_layout(self, layout: QVBoxLayout | QHBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.setParent(None)
                continue
            if child_layout is not None:
                self._clear_layout(child_layout)  # type: ignore[arg-type]
