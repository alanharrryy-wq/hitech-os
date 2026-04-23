export const stockColumns = ['SKU', 'Producto', 'Categoría', 'Ubicación', 'Disponible', 'Cobertura', 'Semáforo'] as const;
export const purchaseColumns = ['Folio', 'Proveedor', 'Estado', 'Creada', 'Esperada', 'Lead'] as const;
export const stateCards = [
  { key: 'loading', title: 'Cargando con contexto', note: 'Mantén filtros visibles mientras llegan datos.' },
  { key: 'empty', title: 'Sin resultados', note: 'Muestra CTA para limpiar filtros o crear registro.' },
  { key: 'error', title: 'Error accionable', note: 'Explica qué falló y cuál es el siguiente paso.' },
  { key: 'stale', title: 'Datos envejecidos', note: 'Marca snapshots viejos y sync rezagado.' },
  { key: 'offline', title: 'Sin sincronización', note: 'Haz visible el outbox pendiente y el último éxito.' },
];

export const filterPresets = {
  categoria: ['Bebidas', 'Snacks', 'Limpieza', 'Higiene', 'Abarrotes'],
  ubicacion: ['A-01', 'A-02', 'B-01', 'B-02', 'C-01'],
  semaforo: ['quiebre', 'critico', 'bajo'],
  fecha: ['hoy', '7_dias', '14_dias', '30_dias'],
  estatusCompra: ['ordered', 'partial', 'received'],
};

export const queueHighlights = [
  { title: 'Stock crítico', value: '3,000 filas máximas', note: 'prioriza disponible cero y cobertura baja' },
  { title: 'Compras', value: '700 órdenes', note: 'lead time y vencidas a la mano' },
  { title: 'Recepción', value: '540 recibos', note: 'incidencias primero' },
  { title: 'Outbox', value: '2,000 eventos', note: 'latencia visible y payload preview' },
  { title: 'Auditoría', value: '400 conteos', note: 'riesgo por varianza y estado' },
];
