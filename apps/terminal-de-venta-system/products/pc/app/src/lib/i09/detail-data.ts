export const detailSummary = [
  { title: 'Movimientos', value: '6,000', note: 'detalle operativo reciente' },
  { title: 'Recepciones', value: '540', note: 'último bloque consultable' },
  { title: 'Outbox', value: '2,000', note: 'eventos con trazabilidad visible' },
  { title: 'Acciones masivas', value: '3', note: 'solo propuestas con guardrails' },
];

export const movementPreview = [
  ['SKU-04893', 'Bebidas producto 4893', 'sale', '-3', 'venta', 'B-02', '2026-04-18 23:49'],
  ['SKU-04892', 'Snacks producto 4892', 'adjustment', '2', 'conteo', 'C-01', '2026-04-18 23:48'],
  ['SKU-04891', 'Abarrotes producto 4891', 'receipt', '8', 'recepción', 'A-03', '2026-04-18 23:47'],
];

export const receiptPreview = [
  ['PO-1699', 'Proveedor Norte', 'received', '12', '2 días', '2026-04-18 19:14'],
  ['PO-1698', 'Snacks MX', 'partial', '7', '1 día', '2026-04-18 18:51'],
  ['PO-1697', 'Limpieza Total', 'received', '16', '3 días', '2026-04-18 17:40'],
];

export const outboxPreview = [
  ['stock.adjusted', 'prod-01', 'pending', '18', '2026-04-18 19:00', ''],
  ['receipt.created', 'rr-02', 'sent', '12', '2026-04-18 18:54', '2026-04-18 19:06'],
  ['audit.closed', 'ac-03', 'error', '41', '2026-04-18 18:25', ''],
];

export const dateFilterGroups = [
  { title: 'Día', values: ['Hoy', 'Ayer', 'Últimos 7 días', 'Últimos 14 días'], note: 'ideal para colas calientes y movimientos recientes' },
  { title: 'Semana', values: ['Semana actual', 'Semana pasada', 'Últimas 4 semanas'], note: 'útil para auditoría y comportamiento del outbox' },
  { title: 'Mes', values: ['Mes actual', 'Mes pasado', 'Últimos 3 meses', 'Año actual'], note: 'sirve para compras, recepción y salud del catálogo' },
];

export const bulkActions = [
  { key: 'outbox-error', title: 'Reintentar outbox en error', candidates: 250, mode: 'preview + lote <= 50', note: 'solo eventos con error y topic permitido' },
  { key: 'stock-critico', title: 'Enviar a revisión stock crítico', candidates: 600, mode: 'preview + export CSV', note: 'genera cola de reabasto, no toca inventario directo' },
  { key: 'precios-viejos', title: 'Marcar precios envejecidos', candidates: 700, mode: 'preview + etiqueta de revisión', note: 'no cambia precio, solo señaliza y deja traza' },
];
