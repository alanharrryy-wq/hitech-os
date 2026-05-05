export type FilterPresetGroup = 'categoria' | 'ubicacion' | 'semaforo' | 'fecha' | 'estatusCompra';

export function serializeActiveFilters(filters: Record<string, string[]>) {
  return Object.entries(filters)
    .filter(([, values]) => values.length > 0)
    .map(([key, values]) => `${key}:${values.join('|')}`)
    .join(';');
}

export function describeEmptyState(activeFilterCount: number) {
  return activeFilterCount > 0
    ? 'No hubo coincidencias. Limpia un filtro o amplía el rango.'
    : 'Todavía no hay datos para mostrar aquí.';
}
