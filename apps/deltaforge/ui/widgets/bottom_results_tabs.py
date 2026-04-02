from __future__ import annotations

import json

from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget

from forgeos.shared.pyside6_glass.template import GlassWorkspaceTabSpec, GlassWorkspaceTabs


class BottomResultsTabs(QWidget):
    TAB_ORDER = ('events', 'validation', 'plan', 'apply', 'rollback')

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.tabs = GlassWorkspaceTabs(
            self,
            tabs_closable=False,
            movable=False,
            document_mode=True,
        )
        self._views: dict[str, QTextEdit] = {}
        for name in self.TAB_ORDER:
            view = QTextEdit(self)
            view.setReadOnly(True)
            view.setProperty('readonly', 'true')
            self._views[name] = view
            self.tabs.add_workspace_tab(
                GlassWorkspaceTabSpec(
                    tab_id=name,
                    title=name.title(),
                    state='visible',
                    icon_name='file-text',
                ),
                view,
            )
        layout.addWidget(self.tabs)

    def set_payloads(self, payloads: dict | None) -> None:
        payloads = payloads or {}
        for name, view in self._views.items():
            payload = payloads.get(name, '')
            if isinstance(payload, str):
                view.setPlainText(payload)
            else:
                view.setPlainText(json.dumps(payload, indent=2, ensure_ascii=False))

    def set_tab_state(self, tab_id: str, state: str) -> None:
        self.tabs.set_tab_state(tab_id, state)
