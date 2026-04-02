from __future__ import annotations

from typing import Optional

from PySide6 import QtCore, QtWidgets


class SectionCard(QtWidgets.QFrame):
    def __init__(
        self,
        title: str = '',
        subtitle: str = '',
        body: Optional[QtWidgets.QWidget] = None,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName('SectionCard')
        self.setProperty('emphasis', 'default')

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(18, 16, 18, 16)
        self._layout.setSpacing(14)

        self._header = QtWidgets.QWidget(self)
        self._header_layout = QtWidgets.QVBoxLayout(self._header)
        self._header_layout.setContentsMargins(0, 0, 0, 0)
        self._header_layout.setSpacing(4)

        self._title_label = QtWidgets.QLabel(title, self._header)
        self._title_label.setObjectName('SectionTitle')
        self._title_label.setWordWrap(True)

        self._subtitle_label = QtWidgets.QLabel(subtitle, self._header)
        self._subtitle_label.setObjectName('SectionSubtitle')
        self._subtitle_label.setWordWrap(True)

        self._header_layout.addWidget(self._title_label)
        self._header_layout.addWidget(self._subtitle_label)

        self._body_container = QtWidgets.QWidget(self)
        self._body_layout = QtWidgets.QVBoxLayout(self._body_container)
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        self._body_layout.setSpacing(12)

        self._layout.addWidget(self._header)
        self._layout.addWidget(self._body_container)

        self.set_title(title)
        self.set_subtitle(subtitle)
        self.set_body(body)

    def set_title(self, text: str) -> None:
        self._title_label.setText(text)
        self._title_label.setVisible(bool(text))
        self._refresh_header_visibility()

    def set_subtitle(self, text: str) -> None:
        self._subtitle_label.setText(text)
        self._subtitle_label.setVisible(bool(text))
        self._refresh_header_visibility()

    def set_body(self, widget: Optional[QtWidgets.QWidget]) -> None:
        while self._body_layout.count():
            item = self._body_layout.takeAt(0)
            child = item.widget()
            if child is not None:
                child.setParent(None)
        if widget is not None:
            self._body_layout.addWidget(widget)
        self._body_container.setVisible(widget is not None)

    def set_emphasis(self, elevated: bool) -> None:
        self.setProperty('emphasis', 'elevated' if elevated else 'default')
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def add_widget(self, widget: QtWidgets.QWidget, stretch: int = 0, alignment: QtCore.Qt.AlignmentFlag = QtCore.Qt.Alignment()) -> None:
        self._body_layout.addWidget(widget, stretch, alignment)
        self._body_container.setVisible(True)

    def _refresh_header_visibility(self) -> None:
        self._header.setVisible(self._title_label.isVisible() or self._subtitle_label.isVisible())
