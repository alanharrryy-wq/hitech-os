from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ActionSpec:
    action_id: str
    label: str
    variant: str = "secondary"
    icon: str | None = None
    tooltip: str = ""
    enabled: bool = True
    minimum_width: int = 0


@dataclass(frozen=True, slots=True)
class ChipSpec:
    text: str
    tone: str = "neutral"
    icon: str | None = None


@dataclass(slots=True)
class SelectorResult:
    accepted: bool
    workspace: str
    theme_id: str
    scale_id: str
    mode: str
    profile: str


@dataclass(slots=True)
class TemplateConsoleConfig:
    window_title: str = "Template Console"
    theme_id: str = "silver_frost_cyan"
    ui_scale: str = "100"
    hero_eyebrow: str = "Workspace"
    hero_title: str = "Template Console"
    hero_subtitle: str = (
        "Reusable visual shell with glass styling, configurable layout, and "
        "slot-based content injection."
    )
    hero_icon: str | None = "workspace"
    hero_chips: list[ChipSpec] = field(
        default_factory=lambda: [
            ChipSpec("Console", tone="accent", icon="console"),
            ChipSpec("PySide6 Glass", tone="neutral", icon="spark"),
        ]
    )
    toolbar_actions: list[ActionSpec] = field(
        default_factory=lambda: [
            ActionSpec("refresh", "Refresh", variant="secondary", icon="refresh"),
            ActionSpec("open_selector", "Workspace", variant="secondary", icon="workspace"),
            ActionSpec("open_progress", "Progress", variant="primary", icon="play"),
            ActionSpec("toggle_sidebar", "Sidebar", variant="secondary", icon="panel"),
        ]
    )
    panel_order: tuple[str, ...] = ("sidebar", "main", "aux")
    show_sidebar: bool = True
    show_aux: bool = True
    footer_hint: str = (
        "Slots are ready for console output, charts, tables, logs, or any custom widget."
    )
