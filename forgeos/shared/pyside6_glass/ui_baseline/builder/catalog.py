from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IngredientSpec:
    id: str
    label: str
    suggested_zone: str
    description: str
    requires_data: bool
    stability: str


INGREDIENT_CATALOG: tuple[IngredientSpec, ...] = (
    IngredientSpec("hero_header", "Hero header", "hero", "Encabezado narrativo con contexto operativo.", False, "stable"),
    IngredientSpec("kpi_strip", "KPI strip", "hero", "Fila compacta de métricas resumidas.", True, "stable"),
    IngredientSpec("chart_panel", "Chart panel", "main", "Superficie para gráfica o tendencia.", True, "stable"),
    IngredientSpec("table_panel", "Table panel", "main", "Tabla primaria para datos tabulares.", True, "stable"),
    IngredientSpec("filter_bar", "Filter bar", "side", "Controles de filtrado y segmentación.", False, "stable"),
    IngredientSpec("search_bar", "Search bar", "side", "Búsqueda rápida contextual.", False, "stable"),
    IngredientSpec("actions_panel", "Actions panel", "footer", "Acciones primarias y secundarias.", False, "stable"),
    IngredientSpec("status_bar", "Status bar", "status", "Mensajes de estado, sincronización y salud.", False, "stable"),
    IngredientSpec("empty_state", "Empty state", "status", "Presentación de ausencia de datos.", False, "stable"),
    IngredientSpec("error_state", "Error state", "status", "Presentación de fallo recuperable.", False, "stable"),
    IngredientSpec("detail_form", "Detail form", "main", "Formulario de detalle o edición puntual.", True, "experimental"),
    IngredientSpec("tabs_section", "Tabs section", "main", "Sección tabulada para subáreas del screen.", False, "experimental"),
    IngredientSpec("activity_feed", "Activity feed", "side", "Flujo de actividad o eventos recientes.", True, "experimental"),
    IngredientSpec("inspector_panel", "Inspector panel", "side", "Inspector contextual para selección activa.", True, "stable"),
    IngredientSpec("summary_cards", "Summary cards", "hero", "Tarjetas de resumen de alto nivel.", True, "stable"),
    IngredientSpec("stale_data_banner", "Stale data banner", "status", "Advertencia de datos potencialmente desactualizados.", True, "stable"),
)


def list_ingredients() -> list[IngredientSpec]:
    return list(INGREDIENT_CATALOG)


def get_ingredient(ingredient_id: str) -> IngredientSpec | None:
    for item in INGREDIENT_CATALOG:
        if item.id == ingredient_id:
            return item
    return None


def ingredients_for_zone(zone: str) -> list[IngredientSpec]:
    return [item for item in INGREDIENT_CATALOG if item.suggested_zone == zone]
