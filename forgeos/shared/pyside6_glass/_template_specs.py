from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from PySide6.QtWidgets import QWidget

@dataclass(slots=True, frozen=True)
class GlassWorkspaceTabSpec:
    tab_id: str
    title: str
    state: str = "visible"
    tooltip: str = ""
    icon_name: str | None = None
    icon_pack: str | None = None
    icon_namespace: str | None = None
    status: str = ""
    badge: str = ""
    favorite: bool = False
    pinned: bool = False
    family: str = ""
    lazy_factory: Callable[[], QWidget] | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class GlassPanelSpec:
    panel_id: str
    title: str
    role: str = "workspace"
    subtitle: str = ""
    state: str = "visible"
    card_kind: str = "true"
    status: str = ""
    icon_name: str | None = None
    icon_pack: str | None = None
    min_size: tuple[int, int] | None = None
    preferred_size: tuple[int, int] | None = None
    max_size: tuple[int, int] | None = None
    priority: int = 100
    group: str = ""
    collapsible: bool = True
    deferred_factory: Callable[[], QWidget] | None = None
    toolbar_enabled: bool = True
    footer_enabled: bool = False
    metadata: dict[str, str] = field(default_factory=dict)

__all__ = [
    "GlassPanelSpec",
    "GlassWorkspaceTabSpec",
]
