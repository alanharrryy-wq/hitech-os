from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QSplitter, QVBoxLayout, QWidget

from ._template_tabs import GlassWorkspaceTabs

@dataclass(slots=True)
class GlassLayoutController:
    splitters: dict[str, QSplitter]
    default_sizes: dict[str, list[int]]

    def register_splitter(
        self,
        key: str,
        splitter: QSplitter,
        *,
        default_sizes: list[int] | tuple[int, ...] | None = None,
    ) -> None:
        normalized = str(key or "").strip().lower()
        if not normalized:
            raise ValueError("splitter key is required")
        self.splitters[normalized] = splitter
        if default_sizes is not None:
            self.default_sizes[normalized] = [max(0, int(size)) for size in default_sizes]
            splitter.setSizes(self.default_sizes[normalized])

    def set_sizes(self, key: str, sizes: list[int] | tuple[int, ...]) -> None:
        splitter = self.splitters.get(str(key or "").strip().lower())
        if splitter is None:
            return
        splitter.setSizes([max(0, int(size)) for size in sizes])

    def set_collapsed(self, key: str, index: int, collapsed: bool) -> None:
        splitter = self.splitters.get(str(key or "").strip().lower())
        if splitter is None:
            return
        sizes = splitter.sizes()
        if not sizes or not (0 <= index < len(sizes)):
            return
        if collapsed:
            sizes[index] = 0
            splitter.setSizes(sizes)
            return

        defaults = self.default_sizes.get(str(key or "").strip().lower(), [])
        if defaults and index < len(defaults):
            sizes[index] = max(0, defaults[index])
        else:
            sizes[index] = max(1, splitter.size().width() // max(1, len(sizes)))
        splitter.setSizes(sizes)

    def snapshot(self) -> dict[str, list[int]]:
        return {key: splitter.sizes() for key, splitter in self.splitters.items()}

    def restore(self, payload: dict[str, list[int] | tuple[int, ...]]) -> None:
        for key, sizes in payload.items():
            self.set_sizes(key, list(sizes))

    def reset_defaults(self) -> None:
        for key, sizes in self.default_sizes.items():
            self.set_sizes(key, list(sizes))


class GlassPanelSlotHost(QFrame):
    """Dedicated child host that owns nested slot insertion layout."""

    def __init__(self, panel_id: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName(f"glass_panel_slot_host_{str(panel_id or '').strip().lower() or 'slot'}")
        self.setProperty("card", "clear")
        self._host_layout = QVBoxLayout(self)
        self._host_layout.setContentsMargins(0, 0, 0, 0)
        self._host_layout.setSpacing(6)

    @property
    def host_layout(self) -> QVBoxLayout:
        return self._host_layout


@dataclass(slots=True)
class GlassTemplateSlots:
    hero_slot: QVBoxLayout
    main_slot: QVBoxLayout
    side_slot: QVBoxLayout
    footer_slot: QHBoxLayout
    status_slot: QVBoxLayout
    workspace_tabs: GlassWorkspaceTabs | None = None


@dataclass(slots=True)
class GlassTemplateCards:
    shell: QFrame
    hero: QFrame
    main: QFrame
    side: QFrame
    footer: QFrame
    status: QFrame
    body: QWidget


@dataclass(slots=True)
class GlassTemplateActions:
    cancel_button: QPushButton | None
    submit_button: QPushButton | None

__all__ = [
    "GlassLayoutController",
    "GlassPanelSlotHost",
    "GlassTemplateActions",
    "GlassTemplateCards",
    "GlassTemplateSlots",
]
