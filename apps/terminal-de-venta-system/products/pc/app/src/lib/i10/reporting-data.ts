export const executiveCards = [
  { title: 'SKUs activos', value: '5,000', note: 'catálogo activo para panel ejecutivo' },
  { title: 'Quiebres', value: '667', note: 'disponible en cero dentro del snapshot' },
  { title: 'PO abiertas', value: '467', note: 'ordered + partial' },
  { title: 'Outbox con presión', value: '2,000', note: 'pending + failed visibles' },
];

export const exportCatalog = [
  { key: 'weekly-pack', title: 'Pack ejecutivo semanal', format: 'JSON', cadence: 'semanal', note: 'resumen para supervisión y dirección' },
  { key: 'monthly-pack', title: 'Pack ejecutivo mensual', format: 'JSON', cadence: 'mensual', note: 'corte consolidado por inventario y sync' },
  { key: 'category-margin', title: 'Margen por categoría', format: 'CSV + JSON', cadence: 'bajo demanda', note: 'sirve para mezcla comercial y compras' },
  { key: 'stock-exception', title: 'Excepciones de stock', format: 'CSV + JSON', cadence: 'diario', note: 'cola de revisión y reabasto' },
  { key: 'sync-sla', title: 'SLA de sincronización', format: 'CSV + JSON', cadence: 'diario', note: 'vigila latencia, pendientes y fallos' },
];

export const categoryHighlights = [
  ['Bebidas', '834 productos', '$7.42 margen prom.', '46.1%'],
  ['Snacks', '834 productos', '$7.48 margen prom.', '46.1%'],
  ['Limpieza', '833 productos', '$7.52 margen prom.', '46.1%'],
];

export const stockExceptionPreview = [
  ['SKU-00000', 'Bebidas producto 0', 'A-01', '0', '0.0 días', 'quiebre'],
  ['SKU-00015', 'Snacks producto 15', 'A-02', '2', '0.8 días', 'crítico'],
  ['SKU-00028', 'Abarrotes producto 28', 'B-01', '1', '1.1 días', 'crítico'],
];

export const syncSlaPreview = [
  ['product.updated', '1,000', '333', '333', '334', '5.99 min'],
  ['stock.adjusted', '1,000', '334', '333', '333', '5.98 min'],
  ['audit.closed', '1,000', '333', '334', '333', '5.99 min'],
];

export const reportContracts = [
  { contract: 'executive.inventory.health.v1', producer: 'PC / vistas-ejecutivas', consumer: 'dirección y supervisión', cadence: 'diario', format: 'JSON', notes: 'bloque base para tarjetas KPI' },
  { contract: 'executive.category.margin.v1', producer: 'PC / exportables', consumer: 'compras y dirección', cadence: 'bajo demanda', format: 'CSV, JSON', notes: 'exporta mezcla comercial por categoría' },
  { contract: 'operations.stock.exception.v1', producer: 'PC / exportables', consumer: 'inventario y reabasto', cadence: 'diario', format: 'CSV, JSON', notes: 'cola accionable, no cambia inventario directo' },
  { contract: 'sync.outbox.sla.v1', producer: 'PC / contratos-reporte', consumer: 'operaciones y soporte', cadence: 'diario', format: 'CSV, JSON', notes: 'salud del outbox y latencia de envíos' },
];
