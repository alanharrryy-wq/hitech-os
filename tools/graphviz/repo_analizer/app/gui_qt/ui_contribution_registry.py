from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

DockAreaLike = Qt.DockWidgetArea | str
DockWidgetFactory = Callable[[QWidget | None], QWidget]
ActionCallback = Callable[[], None]
ToolbarTarget = Literal['workspace', 'command']


@dataclass(frozen=True, slots=True)
class DockContribution:
    """Declarative plugin contribution for a dock widget."""

    contribution_id: str
    title: str
    widget_factory: DockWidgetFactory
    area: DockAreaLike = 'right'
    visible: bool = True
    closable: bool = False
    floatable: bool = False
    movable: bool = False
    allowed_areas: Qt.DockWidgetAreas | None = None


@dataclass(frozen=True, slots=True)
class ToolbarActionContribution:
    """Declarative plugin contribution for a toolbar action."""

    contribution_id: str
    text: str
    callback: ActionCallback
    target: ToolbarTarget = 'command'
    tooltip: str = ''
    shortcut: str = ''


@dataclass(frozen=True, slots=True)
class MenuActionContribution:
    """Declarative plugin contribution for a menu action."""

    contribution_id: str
    menu_path: str
    text: str
    callback: ActionCallback
    tooltip: str = ''
    shortcut: str = ''


class UIContributionRegistry:
    """Stores declarative UI contributions registered by plugins."""

    def __init__(self) -> None:
        self._dock_contributions: list[DockContribution] = []
        self._toolbar_contributions: list[ToolbarActionContribution] = []
        self._menu_contributions: list[MenuActionContribution] = []
        self._seen_ids: set[str] = set()

    def register_dock(self, contribution: DockContribution) -> None:
        self._remember(contribution.contribution_id)
        self._dock_contributions.append(contribution)

    def register_toolbar_action(self, contribution: ToolbarActionContribution) -> None:
        self._remember(contribution.contribution_id)
        self._toolbar_contributions.append(contribution)

    def register_menu_action(self, contribution: MenuActionContribution) -> None:
        self._remember(contribution.contribution_id)
        self._menu_contributions.append(contribution)

    def get_dock_contributions(self) -> tuple[DockContribution, ...]:
        return tuple(self._dock_contributions)

    def get_toolbar_contributions(self) -> tuple[ToolbarActionContribution, ...]:
        return tuple(self._toolbar_contributions)

    def get_menu_contributions(self) -> tuple[MenuActionContribution, ...]:
        return tuple(self._menu_contributions)

    def _remember(self, contribution_id: str) -> None:
        if not contribution_id:
            raise ValueError('Contribution id cannot be empty')
        if contribution_id in self._seen_ids:
            raise ValueError(f"Contribution '{contribution_id}' is already registered")
        self._seen_ids.add(contribution_id)
