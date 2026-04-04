from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPlainTextEdit, QVBoxLayout, QWidget

from domain.models import SessionWorkspace
from ui.primitives import KeyValueDetailBlock, SectionCard


class RightPane(QWidget):
    def __init__(self) -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.detail_card = SectionCard("Detail", "Contexto del item seleccionado")
        self.detail_block = KeyValueDetailBlock()
        self.detail_text = QPlainTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_card.content_layout.addWidget(self.detail_block)
        self.detail_card.content_layout.addWidget(self.detail_text, 1)

        self.hint = QLabel("Selecciona un item de plan o diff para ver detalle.")
        self.hint.setProperty("role", "hint")
        self.detail_card.content_layout.addWidget(self.hint)
        outer.addWidget(self.detail_card)

    def show_session(self, session: SessionWorkspace | None) -> None:
        if session is None:
            self.detail_block.set_rows([])
            self.detail_text.setPlainText("")
            return

        self.detail_block.set_rows(
            [
                ("Session", session.title),
                ("State", session.state.value),
                ("Targets", str(session.scope.count)),
                ("Mode", session.mode),
                ("Stale", "yes" if session.stale else "no"),
            ]
        )
        self.detail_text.setPlainText("Selecciona un paso del plan para ver detalle extendido.")

    def show_payload(self, payload: dict) -> None:
        rows = [(str(key), str(value)) for key, value in payload.items() if key != "detail"]
        self.detail_block.set_rows(rows)
        self.detail_text.setPlainText(str(payload.get("detail") or ""))

    def focus_panel(self) -> None:
        self.detail_text.setFocus()
