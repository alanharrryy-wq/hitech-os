from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLayout, QVBoxLayout, QWidget

from .icons import get_icon
from .rendering import apply_surface_role
from ._template_helpers import _normalize_panel_role, _normalize_panel_state, _polish_widget
from ._template_specs import GlassPanelSpec

class GlassPanelFrame(QFrame):
    """Role-aware panel container with title/subtitle + content layout."""

    def __init__(self, spec: GlassPanelSpec, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._panel_id = str(spec.panel_id)
        self._panel_state = _normalize_panel_state(spec.state)
        self._panel_role = _normalize_panel_role(spec.role)
        self._deferred_factory = spec.deferred_factory
        self._deferred_loaded = False
        self._toolbar_enabled = bool(spec.toolbar_enabled)
        self._footer_enabled = bool(spec.footer_enabled)
        self.setAccessibleName(f"glass_panel_{self._panel_id}")
        self.setProperty("card", str(spec.card_kind or "true"))
        self.setProperty("panelRole", self._panel_role)
        self.setProperty("panelState", self._panel_state)
        apply_surface_role(
            self,
            role=f"panel_{self._panel_role}",
            variant="panel",
            emphasis="normal",
            fx_level="normal",
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(3)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(4)
        self._title_icon = QLabel("", self)
        self._title_icon.setFixedWidth(18)
        self._title_icon.setVisible(False)
        self._title_label = QLabel(spec.title, self)
        self._title_label.setProperty("role", "panel_title")
        self._title_label.setAccessibleName(f"glass_panel_title_{self._panel_id}")
        if spec.icon_name:
            icon = get_icon(spec.icon_name, pack=spec.icon_pack)
            if not icon.isNull():
                self._title_icon.setPixmap(icon.pixmap(16, 16))
                self._title_icon.setVisible(True)
        self._status_label = QLabel(str(spec.status or ""), self)
        self._status_label.setProperty("role", "caption")
        self._status_label.setVisible(bool(spec.status))
        header.addWidget(self._title_icon, 0, Qt.AlignTop)
        header.addWidget(self._title_label, 1)
        header.addWidget(self._status_label, 0, Qt.AlignRight)

        self._subtitle_label = QLabel(spec.subtitle, self)
        self._subtitle_label.setProperty("role", "panel_subtitle")
        self._subtitle_label.setAccessibleName(f"glass_panel_subtitle_{self._panel_id}")
        self._subtitle_label.setWordWrap(True)
        self._subtitle_label.setVisible(bool(spec.subtitle))

        self._toolbar_layout = QHBoxLayout()
        self._toolbar_layout.setContentsMargins(0, 0, 0, 0)
        self._toolbar_layout.setSpacing(4)
        self._toolbar_host = QWidget(self)
        self._toolbar_host.setLayout(self._toolbar_layout)
        self._toolbar_host.setVisible(self._toolbar_enabled)

        self._content_host = QFrame(self)
        self._content_host.setObjectName(f"glass_panel_content_{self._panel_id}")
        self._content_host.setProperty("card", "clear")
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(4)
        self._content_host.setLayout(self._content_layout)

        self._footer_layout = QHBoxLayout()
        self._footer_layout.setContentsMargins(0, 0, 0, 0)
        self._footer_layout.setSpacing(4)
        self._footer_host = QWidget(self)
        self._footer_host.setLayout(self._footer_layout)
        self._footer_host.setVisible(self._footer_enabled)

        outer.addLayout(header)
        outer.addWidget(self._subtitle_label)
        outer.addWidget(self._toolbar_host)
        outer.addWidget(self._content_host, 1)
        outer.addWidget(self._footer_host)

        if spec.min_size:
            self.setMinimumSize(max(0, int(spec.min_size[0])), max(0, int(spec.min_size[1])))
        if spec.max_size:
            self.setMaximumSize(max(0, int(spec.max_size[0])), max(0, int(spec.max_size[1])))
        if spec.preferred_size:
            self.resize(max(0, int(spec.preferred_size[0])), max(0, int(spec.preferred_size[1])))
        if self._panel_state == "deferred":
            self._render_deferred_placeholder()

    @property
    def panel_id(self) -> str:
        return self._panel_id

    @property
    def content_layout(self) -> QVBoxLayout:
        return self._content_layout

    @property
    def content_host(self) -> QWidget:
        return self._content_host

    def set_panel_title(self, title: str) -> None:
        self._title_label.setText(str(title))

    def set_panel_subtitle(self, subtitle: str) -> None:
        value = str(subtitle or "")
        self._subtitle_label.setText(value)
        self._subtitle_label.setVisible(bool(value))

    def set_panel_status(self, status: str) -> None:
        value = str(status or "")
        self._status_label.setText(value)
        self._status_label.setVisible(bool(value))

    def toolbar_layout(self) -> QHBoxLayout:
        return self._toolbar_layout

    def footer_layout(self) -> QHBoxLayout:
        return self._footer_layout

    def set_toolbar_visible(self, visible: bool) -> None:
        self._toolbar_enabled = bool(visible)
        self._toolbar_host.setVisible(self._toolbar_enabled)

    def set_footer_visible(self, visible: bool) -> None:
        self._footer_enabled = bool(visible)
        self._footer_host.setVisible(self._footer_enabled)

    def set_panel_role(self, role: str) -> None:
        self._panel_role = _normalize_panel_role(role)
        self.setProperty("panelRole", self._panel_role)
        apply_surface_role(
            self,
            role=f"panel_{self._panel_role}",
            variant=str(self.property("visualVariant") or "panel"),
            emphasis=str(self.property("visualEmphasis") or "normal"),
            fx_level=str(self.property("visualFxLevel") or "normal"),
        )
        _polish_widget(self)

    def set_panel_state(self, state: str) -> None:
        self._panel_state = _normalize_panel_state(state)
        self.setProperty("panelState", self._panel_state)
        _polish_widget(self)
        self._apply_state_behavior()

    def load_deferred_content(self) -> None:
        if self._deferred_loaded:
            return
        if self._deferred_factory is None:
            return
        widget = self._deferred_factory()
        if widget is None:
            return
        self.set_content_widget(widget)
        self._deferred_loaded = True

    def _render_deferred_placeholder(self) -> None:
        self.clear_content()
        placeholder = QLabel("Deferred panel. Content will be created on demand.", self)
        placeholder.setProperty("role", "panel_subtitle")
        placeholder.setWordWrap(True)
        self.add_content_widget(placeholder)

    def _apply_state_behavior(self) -> None:
        if self._panel_state == "hidden":
            self.setVisible(False)
            return
        if self._panel_state == "collapsed":
            self.setVisible(True)
            self._toolbar_host.setVisible(False)
            self._footer_host.setVisible(False)
            self._set_content_visible(False)
            return
        if self._panel_state == "deferred":
            self.setVisible(True)
            self._render_deferred_placeholder()
            return
        if self._panel_state == "disabled":
            self.setVisible(True)
            self.setEnabled(False)
            return
        self.setEnabled(True)
        self.setVisible(True)
        self._set_content_visible(True)
        self._toolbar_host.setVisible(self._toolbar_enabled)
        self._footer_host.setVisible(self._footer_enabled)
        if self._panel_state in {"visible", "background", "hold"}:
            self.load_deferred_content()

    def _set_content_visible(self, visible: bool) -> None:
        for idx in range(self._content_layout.count()):
            item = self._content_layout.itemAt(idx)
            widget = item.widget()
            if widget is not None:
                widget.setVisible(bool(visible))

    def clear_content(self) -> None:
        self._clear_layout(self._content_layout)

    def set_content_widget(self, widget: QWidget) -> None:
        self.clear_content()
        self.add_content_widget(widget, stretch=1)

    def add_content_widget(self, widget: QWidget, stretch: int = 0) -> None:
        if widget is None:
            raise ValueError("content widget is required")
        if widget is self or widget is self._content_host:
            raise ValueError("panel cannot mount itself as content")
        if widget.isAncestorOf(self._content_host):
            raise ValueError("cannot mount ancestor widget into descendant-owned panel layout")

        old_parent = widget.parentWidget()
        old_layout = old_parent.layout() if isinstance(old_parent, QWidget) else None
        if isinstance(old_layout, QLayout):
            old_layout.removeWidget(widget)
        widget.setParent(self._content_host)
        self._content_layout.addWidget(widget, max(0, int(stretch)))

    def _clear_layout(self, layout: QLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.setParent(None)
                continue
            if child_layout is not None:
                self._clear_layout(child_layout)

__all__ = ["GlassPanelFrame"]
