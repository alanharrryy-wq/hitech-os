from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget

from .chrome import WindowChromeBar
from .controls import create_button
from .scene import build_glass_dialog_scene


@dataclass(slots=True)
class GlassTemplateSlots:
    hero_slot: QVBoxLayout
    main_slot: QVBoxLayout
    side_slot: QVBoxLayout
    footer_slot: QHBoxLayout
    status_slot: QVBoxLayout


class GlassPanelTemplate(QWidget):
    """Clean reusable shell with card slots for fast tool construction."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        title: str = "Workspace",
        variant: str = "selector",
        with_chrome: bool = True,
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._variant = variant
        self.slots = self._build(with_chrome=with_chrome)

    def _card(self, card_kind: str) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame(self)
        card.setProperty("card", card_kind)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(10)
        return card, card_layout

    def _build(self, *, with_chrome: bool) -> GlassTemplateSlots:
        outer, content, _backdrop = build_glass_dialog_scene(self)
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

        if with_chrome:
            chrome = WindowChromeBar(self.window(), title=self._title)
            shell_layout.addWidget(chrome)

        hero_card, hero_layout = self._card("hero")
        shell_layout.addWidget(hero_card)

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

        footer = QFrame(self)
        footer.setProperty("card", "footer")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(14, 10, 14, 10)
        footer_layout.setSpacing(10)
        shell_layout.addWidget(footer)

        status = QFrame(self)
        status.setProperty("card", "muted")
        status_layout = QVBoxLayout(status)
        status_layout.setContentsMargins(14, 10, 14, 10)
        status_layout.setSpacing(8)
        shell_layout.addWidget(status)

        cancel = create_button("Cancelar", "danger", parent=footer)
        submit = create_button("Continuar", "primary", parent=footer)
        footer_layout.addStretch(1)
        footer_layout.addWidget(cancel, 0, Qt.AlignRight)
        footer_layout.addWidget(submit, 0, Qt.AlignRight)

        return GlassTemplateSlots(
            hero_slot=hero_layout,
            main_slot=main_layout,
            side_slot=side_layout,
            footer_slot=footer_layout,
            status_slot=status_layout,
        )

