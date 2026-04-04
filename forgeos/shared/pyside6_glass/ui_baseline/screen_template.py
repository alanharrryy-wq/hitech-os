from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from .runtime import build_runtime_for_screen, intent_from_screen


class VisualScreenTemplate(QWidget):
    """Shell estructural para pantallas gobernadas.

    Organiza zonas y delega autoridad visual al runtime oficial del core.
    Si una zona está desactivada o sin contenido, se oculta de verdad.
    """

    visual_role = "workspace"
    visual_variant = "default"
    visual_emphasis = "medium"
    visual_fx_level = "subtle"
    visual_level = "standard"
    data_state = "ready"
    reduced_motion = False
    high_contrast_mode = False
    base_preset = "glass-default"
    experience_mode = "desktop"
    data_density_bias = "balanced"

    enable_hero = True
    enable_main = True
    enable_side = True
    enable_footer = True
    enable_status = True

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.ui_intent = intent_from_screen(self)
        self.runtime_bundle = build_runtime_for_screen(self)
        self.ui_intent = self.runtime_bundle.intent
        self.visual_runtime = self.runtime_bundle.visual_runtime

        self._zone_slots: dict[str, QFrame] = {}
        self._zone_layouts: dict[str, QVBoxLayout] = {}

        self._build_shell()
        self.mount_content()

        attach_to = getattr(self.visual_runtime, "attach_to", None)
        if callable(attach_to):
            attach_to(self)

    def _build_shell(self) -> None:
        self.setObjectName("visual-screen-template")
        root = QGridLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setHorizontalSpacing(16)
        root.setVerticalSpacing(12)

        self.hero_slot = self._make_zone("hero")
        self.main_slot = self._make_zone("main")
        self.side_slot = self._make_zone("side")
        self.footer_slot = self._make_zone("footer")
        self.status_slot = self._make_zone("status")

        self.main_slot.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.side_slot.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        root.addWidget(self.hero_slot, 0, 0, 1, 2)
        root.addWidget(self.main_slot, 1, 0, 1, 1)
        root.addWidget(self.side_slot, 1, 1, 1, 1)
        root.addWidget(self.footer_slot, 2, 0, 1, 2)
        root.addWidget(self.status_slot, 3, 0, 1, 2)

        root.setColumnStretch(0, 3)
        root.setColumnStretch(1, 1)
        root.setRowStretch(1, 1)

    def _make_zone(self, name: str) -> QFrame:
        frame = QFrame(self)
        frame.setObjectName(f"{name}-slot")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._zone_slots[name] = frame
        self._zone_layouts[name] = layout
        return frame

    def _clear_zone(self, zone_name: str) -> None:
        layout = self._zone_layouts[zone_name]
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def _zone_enabled(self, zone_name: str) -> bool:
        return bool(getattr(self, f"enable_{zone_name}", True))

    def _set_zone_widget(self, zone_name: str, widget: QWidget | None) -> None:
        slot = self._zone_slots[zone_name]
        self._clear_zone(zone_name)

        if not self._zone_enabled(zone_name) or widget is None:
            slot.hide()
            return

        slot.show()
        self._zone_layouts[zone_name].addWidget(widget)

    def mount_content(self) -> None:
        self._set_zone_widget("hero", self.build_hero() if self._zone_enabled("hero") else None)
        self._set_zone_widget("main", self.build_main() if self._zone_enabled("main") else None)
        self._set_zone_widget("side", self.build_side() if self._zone_enabled("side") else None)
        self._set_zone_widget("footer", self.build_footer() if self._zone_enabled("footer") else None)
        self._set_zone_widget("status", self.build_status() if self._zone_enabled("status") else None)

    def build_hero(self) -> QWidget | None:
        return None

    def build_main(self) -> QWidget | None:
        return None

    def build_side(self) -> QWidget | None:
        return None

    def build_footer(self) -> QWidget | None:
        return None

    def build_status(self) -> QWidget | None:
        return None

    def _state_widget(self, title: str, detail: str) -> QWidget:
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        title_label = QLabel(title, container)
        detail_label = QLabel(detail, container)
        detail_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(detail_label)
        return container

    def loading_state(self, detail: str = "Cargando información...") -> None:
        self.enable_status = True
        self._set_zone_widget("status", self._state_widget("Estado: loading", detail))

    def empty_state(self, detail: str = "No hay datos para mostrar todavía.") -> None:
        self.enable_status = True
        self._set_zone_widget("status", self._state_widget("Estado: empty", detail))

    def error_state(self, detail: str = "Ocurrió un error al preparar la vista.") -> None:
        self.enable_status = True
        self._set_zone_widget("status", self._state_widget("Estado: error", detail))
