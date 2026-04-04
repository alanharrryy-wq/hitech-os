from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RitualSourceSpec:
    """Describe una fuente ritual disponible en el dashboard."""

    id: str
    label: str
    accent: str
    hint: str


@dataclass(frozen=True, slots=True)
class RitualSourceState:
    """Estado serializable de una fuente individual."""

    id: str
    label: str
    accent: str
    hint: str
    active: bool = False


@dataclass(frozen=True, slots=True)
class RitualDashboardState:
    """Snapshot observable del ritual de activación."""

    sources: tuple[RitualSourceState, ...]
    required_source_ids: frozenset[str]
    unlocked: bool
    activation_count: int
    required_count: int
    basin_fill_ratio: float
    basin_label: str
    status_label: str
    unlocked_surface: str

    def is_source_active(self, source_id: str) -> bool:
        return any(source.id == source_id and source.active for source in self.sources)


DEFAULT_RITUAL_SOURCES: tuple[RitualSourceSpec, ...] = (
    RitualSourceSpec("clientes", "Clientes", "aqua", "Activa la lectura de clientes vivos."),
    RitualSourceSpec("pedidos", "Pedidos", "amber", "Abre el flujo de movimiento comercial."),
    RitualSourceSpec("cobranza", "Cobranza", "violet", "Trae liquidez y riesgo a la superficie."),
    RitualSourceSpec("reportes", "Reportes", "emerald", "Revela cortes y snapshots operativos."),
    RitualSourceSpec("analitica", "Analítica", "coral", "Enciende correlaciones y tendencias."),
)

DEFAULT_REQUIRED_SOURCE_IDS: frozenset[str] = frozenset({"clientes", "cobranza", "analitica"})
