from __future__ import annotations

from collections.abc import Iterable, Sequence

from PySide6.QtCore import QObject, Signal

from .ritual_dashboard_state import (
    DEFAULT_REQUIRED_SOURCE_IDS,
    DEFAULT_RITUAL_SOURCES,
    RitualDashboardState,
    RitualSourceSpec,
    RitualSourceState,
)


class RitualDashboardOrchestrator(QObject):
    """Orchestrator mínimo para el ritual de activación del dashboard.

    Vive en el core y expone estado serializable/observable para la screen.
    No resuelve apariencia final ni compite con AppearanceCoordinator.
    """

    state_changed = Signal(object)
    dashboard_unlocked = Signal(object)

    def __init__(
        self,
        source_specs: Sequence[RitualSourceSpec] | None = None,
        required_source_ids: Iterable[str] | None = None,
        unlock_surface: str = "customers_dashboard",
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._source_specs = tuple(source_specs or DEFAULT_RITUAL_SOURCES)
        self._required_source_ids = frozenset(required_source_ids or DEFAULT_REQUIRED_SOURCE_IDS)
        self._unlock_surface = unlock_surface
        self._active_source_ids: set[str] = set()
        self._state = self._build_state()

    @property
    def state(self) -> RitualDashboardState:
        return self._state

    def snapshot(self) -> RitualDashboardState:
        return self._state

    def source_specs(self) -> tuple[RitualSourceSpec, ...]:
        return self._source_specs

    def toggle_source(self, source_id: str, force: bool | None = None) -> RitualDashboardState:
        if source_id not in {spec.id for spec in self._source_specs}:
            raise KeyError(f"Fuente ritual desconocida: {source_id}")

        should_activate = force if force is not None else source_id not in self._active_source_ids
        if should_activate:
            self._active_source_ids.add(source_id)
        else:
            self._active_source_ids.discard(source_id)

        return self._commit_state()

    def set_source_active(self, source_id: str, active: bool) -> RitualDashboardState:
        return self.toggle_source(source_id, force=active)

    def reset(self) -> RitualDashboardState:
        self._active_source_ids.clear()
        return self._commit_state()

    def _commit_state(self) -> RitualDashboardState:
        previous = self._state
        self._state = self._build_state()
        self.state_changed.emit(self._state)
        if self._state.unlocked and not previous.unlocked:
            self.dashboard_unlocked.emit(self._state)
        return self._state

    def _build_state(self) -> RitualDashboardState:
        required_count = max(len(self._required_source_ids), 1)
        active_required = sum(1 for source_id in self._required_source_ids if source_id in self._active_source_ids)
        activation_count = len(self._active_source_ids)
        basin_fill_ratio = min(active_required / required_count, 1.0)
        unlocked = self._required_source_ids.issubset(self._active_source_ids)

        if unlocked:
            basin_label = "Cuenco lleno. El tablero ya respiró."
            status_label = "Ritual completo. La interfaz principal quedó liberada."
        elif activation_count == 0:
            basin_label = "Cuenco vacío. Activa las fuentes de arriba."
            status_label = "Selecciona las fuentes correctas para abrir la superficie útil."
        else:
            basin_label = f"Cuenco cargando: {active_required}/{required_count} fuentes requeridas."
            status_label = f"Ritual en curso. {activation_count} fuentes activas, {required_count - active_required} críticas pendientes."

        sources = tuple(
            RitualSourceState(
                id=spec.id,
                label=spec.label,
                accent=spec.accent,
                hint=spec.hint,
                active=spec.id in self._active_source_ids,
            )
            for spec in self._source_specs
        )
        return RitualDashboardState(
            sources=sources,
            required_source_ids=self._required_source_ids,
            unlocked=unlocked,
            activation_count=activation_count,
            required_count=required_count,
            basin_fill_ratio=basin_fill_ratio,
            basin_label=basin_label,
            status_label=status_label,
            unlocked_surface=self._unlock_surface,
        )
